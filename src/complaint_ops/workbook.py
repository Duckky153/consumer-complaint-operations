"""Editable CCO workbook specification. Native acceptance is recorded separately.

The explicit Tableau XML layout reuses the locally verified hotel project's
parameter/reset pattern; it is not a substitute for opening the final package.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as E
import zipfile

from .tableau import EXPORT_COLUMNS

ROOT = Path(__file__).resolve().parents[2]
D = 'complaints'
NAME = 'Consumer Complaint Operations'
NAVY, TEAL = '#20364b', '#237d82'
MODES = ['Baseline', 'Exclude January', 'Exclude January top two clusters']
CONTROLS = {'Account type': ('sub_product', 'All account types'),
            'Issue': ('issue', 'All issues'), 'Company': ('company', 'All companies'),
            'Month': ('received_month', 'All months'), 'January sensitivity': (None, 'Baseline')}


def el(parent, tag, **attrs):
    return E.SubElement(parent, tag, {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def build(root: Path = ROOT) -> Path:
    out = root/'tableau'
    out.mkdir(exist_ok=True)
    receipt = json.loads((root/'evidence/tableau-hyper-verification.json').read_text())
    csv_path = root/'data/processed/tableau-complaints.csv'
    if hashlib.sha256(csv_path.read_bytes()).hexdigest() != receipt['export_sha256']:
        raise ValueError('CSV changed after Hyper verification')
    with csv_path.open() as stream:
        reader = csv.DictReader(stream)
        headers, rows = reader.fieldnames, list(reader)
    if headers != EXPORT_COLUMNS:
        raise ValueError('Unexpected export schema')
    receipt = json.loads((root/'evidence/tableau-hyper-verification.json').read_text())
    hyper = root/'data/processed/tableau-complaints.hyper'
    if not receipt['passed'] or hashlib.sha256(hyper.read_bytes()).hexdigest() != receipt['hyper_sha256']:
        raise ValueError('Build and verify Hyper first')
    w = E.Element('workbook', {'source-build':'2026.2.2', 'source-platform':'mac', 'version':'18.1',
                              'xmlns:user':'http://www.tableausoftware.com/xml/user'})
    manifest = el(w,'document-format-change-manifest')
    el(manifest,'ParameterAction'); el(manifest,'ParameterActionClearSelection')
    el(w,'preferences')
    ds = el(w,'datasources')
    params = el(ds,'datasource',hasconnection='false',inline='true',name='Parameters',version='18.1')
    param_meta = {}
    for name, (field, default) in CONTROLS.items():
        col = el(params,'column',caption=name,datatype='string',name=f'[{name}]',param_domain_type='list',
                 role='measure',type='nominal',value=f'"{default}"')
        el(col,'calculation',**{'class':'tableau','formula':f'"{default}"'})
        members = el(col,'members')
        for value in ([default]+sorted({r[field] for r in rows}) if field else MODES):
            el(members,'member',value='"'+value.replace('"','""')+'"')
        param_meta[name] = col
    data = el(ds,'datasource',caption='Published CFPB complaints · 2025 snapshot',inline='true',name=D,version='18.1')
    conn = el(data,'connection',**{'class':'federated'})
    named = el(el(conn,'named-connections'),'named-connection',name='hyper.complaints',caption='Complaint observations')
    el(named,'connection',**{'class':'hyper','dbname':'../data/processed/tableau-complaints.hyper',
       'authentication':'auth-none','author-locale':'en_US','default-settings':'yes','sslmode':'','username':'tableau_internal_user'})
    el(conn,'relation',connection='hyper.complaints',name='Extract',table='[Extract].[Extract]',type='table')
    meta = {}
    numbers = {'complaint_count','not_timely','has_relief','january_top_cluster'}
    for name in headers:
        typ = 'integer' if name in numbers else 'date' if name=='date_received' else 'string'
        meta[name] = el(data,'column',datatype=typ,name=f'[{name}]',caption=name.replace('_',' ').title(),
                        role='measure' if name in numbers else 'dimension',
                        type='quantitative' if name in numbers else 'nominal',
                        **({'default-format':'n#,##0'} if name in numbers else {}))
    meta['received_month'].set('caption', 'Month')
    meta['sub_issue'].set('caption', 'Sub-issue')
    filters = [f'([Parameters].[{p}] = "{default}" OR [{field}] = [Parameters].[{p}])'
               for p,(field,default) in CONTROLS.items() if field]
    filters.append('([Parameters].[January sensitivity] = "Baseline" OR '
                   '([Parameters].[January sensitivity] = "Exclude January" AND [received_month] <> "2025-01") OR '
                   '([Parameters].[January sensitivity] = "Exclude January top two clusters" AND [january_top_cluster] = 0))')
    formulas = {'Selected cohort': ('boolean','dimension',' AND '.join(filters))}
    for title,field in [('Selected complaints','complaint_count'),('Selected not timely','not_timely'),('Selected relief','has_relief')]:
        formulas[title] = ('integer','measure',f'ZN(SUM(IF [Selected cohort] THEN [{field}] ELSE 0 END))')
    formulas.update({
        'Not timely rate': ('real','measure','IF [Selected complaints] > 0 THEN [Selected not timely] / [Selected complaints] END'),
        'Relief mix': ('real','measure','IF [Selected complaints] > 0 THEN [Selected relief] / [Selected complaints] END'),
        'Cohort note': ('string','measure','IF [Selected complaints] = 0 THEN "No complaints match. Change a control or Reset view. Rates are undefined." ELSEIF [Selected complaints] < 30 THEN "Small base: fewer than 30 complaints. Review individual cases; interpret percentages cautiously." ELSE "Selected complaints are the denominator. Validate patterns against internal cases and transaction volumes." END'),
        'Small group': ('string','measure','IF SUM([complaint_count]) < 30 THEN " *" ELSE "" END'),
        'Reset label': ('string','dimension','"Reset view"'),
        'Clear reset selection': ('string','dimension','"Clear selection"'),
    })
    for p,(_,default) in CONTROLS.items():
        formulas['Reset '+p] = ('string','dimension',f'"{default}"')
    for name,(typ,role,formula) in formulas.items():
        attrs = {'default-format':'p0.00%'} if typ=='real' else {'default-format':'n#,##0'} if typ=='integer' else {}
        col = el(data,'column',datatype=typ,name=f'[{name}]',caption=name,role=role,
                 type='nominal' if typ in {'string','boolean'} else 'quantitative',**attrs)
        el(col,'calculation',**{'class':'tableau','formula':formula}); meta[name] = col

    def field(name):
        if meta[name].get('role')=='dimension': return f'[none:{name}:nk]'
        if name in formulas: return f'[usr:{name}:nk]' if meta[name].get('datatype')=='string' else f'[usr:{name}:qk]'
        return f'[sum:{name}:qk]'

    def ref(name): return f'[{D}].{field(name)}'

    def dependencies(parent,names):
        dep = el(parent,'datasource-dependencies',datasource=D)
        for n in dict.fromkeys(names):
            dep.append(copy.deepcopy(meta[n]))
            derivation = 'None' if meta[n].get('role')=='dimension' else 'User' if n in formulas else 'Sum'
            el(dep,'column-instance',column=f'[{n}]',derivation=derivation,name=field(n),pivot='key',
               type='nominal' if derivation=='None' or meta[n].get('datatype')=='string' else 'quantitative')
        pd = el(parent,'datasource-dependencies',datasource='Parameters')
        for column in param_meta.values(): pd.append(copy.deepcopy(column))

    works = el(w,'worksheets'); sheet_names = []
    def sheet(name,measure,dimension=None,text=False,filter_rows=False,detail=False,reset=False):
        sheet_names.append(name)
        s = el(works,'worksheet',name=name)
        title = el(el(s,'layout-options'),'title')
        el(el(title,'formatted-text'),'run',fontname='Arial',fontsize='14',fontcolor=NAVY,bold='true').text=name
        t=el(s,'table'); v=el(t,'view'); sources=el(v,'datasources')
        el(sources,'datasource',name=D,caption='Published CFPB complaints · 2025 snapshot')
        el(sources,'datasource',name='Parameters')
        names=[measure,'Selected cohort','Selected complaints','Selected not timely','Selected relief','Not timely rate','Relief mix','complaint_count','not_timely','has_relief']
        if dimension: names.append(dimension)
        if detail: names.append('Small group')
        if reset: names += ['Clear reset selection']+['Reset '+p for p in CONTROLS]
        dependencies(v,names)
        if filter_rows:
            f=el(v,'filter',**{'class':'categorical','column':ref('Selected cohort')})
            el(f,'groupfilter',function='member',level=field('Selected cohort'),member='true')
        el(v,'aggregation',value='true')
        style=el(t,'style')
        for element in ['worksheet','axis','header','pane']:
            rule=el(style,'style-rule',element=element)
            el(rule,'format',attr='font-family',value='Arial'); el(rule,'format',attr='font-size',value='12')
            el(rule,'format',attr='color',value=NAVY)
            if element == 'header' and dimension in {'issue', 'sub_issue'}:
                el(rule,'format',attr='width',field=ref(dimension),value='350' if dimension=='sub_issue' else '255')
                el(rule,'format',attr='wrap',field=ref(dimension),value='on')
        if dimension in {'issue', 'sub_issue'}:
            cell = el(style,'style-rule',element='cell')
            el(cell,'format',attr='height',field=ref(dimension),value='44')
        pane=el(el(t,'panes'),'pane');el(el(pane,'view'),'breakdown',value='auto')
        el(pane,'mark',**{'class':'Text' if text else 'Bar'})
        enc=el(pane,'encodings');el(enc,'text',column=ref(measure))
        if reset:
            for p in CONTROLS: el(enc,'lod',column=ref('Reset '+p))
            el(enc,'lod',column=ref('Clear reset selection'))
        if detail:
            el(enc,'text',column=ref('Not timely rate'));el(enc,'text',column=ref('Small group'))
        label=el(el(pane,'customized-label'),'formatted-text')
        font='28' if text and not dimension and measure not in {'Cohort note','Reset label'} else '12'
        label_text=f'<{ref(measure)}>'
        if detail: label_text+=f'  |  <{ref("Not timely rate")}> NT<{ref("Small group")}>'
        el(label,'run',fontname='Arial',fontsize=font,fontcolor=NAVY,bold='true' if font=='28' else 'false').text=label_text
        tooltip=el(el(pane,'customized-tooltip',show_buttons='false'),'formatted-text')
        el(tooltip,'run').text=(f'<{ref(dimension)}>\n' if dimension else '')+f'Complaints: <{ref("Selected complaints")}>\nNot timely: <{ref("Selected not timely")}> (<{ref("Not timely rate")}>)\nRelief responses: <{ref("Selected relief")}> (<{ref("Relief mix")}>)'
        tooltip_node = pane.find('customized-tooltip')
        pane.remove(tooltip_node)
        pane.insert(list(pane).index(pane.find('customized-label')), tooltip_node)
        ps=el(pane,'style');pr=el(ps,'style-rule',element='mark')
        el(pr,'format',attr='mark-color',value=TEAL);el(pr,'format',attr='mark-labels-show',value='true')
        el(el(ps,'style-rule',element='label'),'format',attr='font-size',value=font)
        el(t,'rows').text=ref(dimension) if dimension else ''
        el(t,'cols').text='' if text else ref(measure)

    sheet('Published complaints','Selected complaints',text=True)
    sheet('Not timely','Selected not timely',text=True)
    sheet('Not timely rate','Not timely rate',text=True)
    sheet('Relief responses','Selected relief',text=True)
    sheet('Relief mix','Relief mix',text=True)
    sheet('Monthly complaints','Selected complaints','received_month',filter_rows=True)
    sheet('Monthly not-timely exceptions','Selected not timely','received_month',filter_rows=True)
    sheet('Issues · count and not-timely rate','Selected complaints','issue',filter_rows=True,detail=True)
    sheet('Sub-issues · count and not-timely rate','Selected complaints','sub_issue',text=True,filter_rows=True,detail=True)
    sheet('Selection note','Cohort note',text=True)
    sheet('Reset view','Reset label',text=True,reset=True)

    dashboards=el(w,'dashboards'); dashboard_sheets={}
    for number,title,question in [('01','Overview','Which complaint patterns deserve a closer look?'),
                                  ('02','Investigation','What should we validate against internal cases?')]:
        name=number+' · '+title
        db=el(dashboards,'dashboard',name=name)
        el(db,'layout-options');st=el(db,'style')
        el(el(st,'style-rule',element='dashboard'),'format',attr='background-color',value='#f7f6f2')
        el(el(st,'style-rule',element='quick-filter'),'format',attr='font-size',value='12')
        el(db,'size',maxheight='850',minheight='850',maxwidth='1200',minwidth='1200')
        sources=el(db,'datasources');el(sources,'datasource',name=D);el(sources,'datasource',name='Parameters')
        dependencies(db,['Selected cohort'])
        zones=el(db,'zones');base=el(zones,'zone',h=100000,w=100000,x=0,y=0,id=0,type='layout-basic');zid=0
        placed=[]
        def zone(x,y,width,height,**attrs):
            nonlocal zid
            zid+=1
            if 'name' in attrs: placed.append(attrs['name'])
            return el(base,'zone',id=zid,x=round(x/1200*100000),y=round(y/850*100000),
                      w=round(width/1200*100000),h=round(height/850*100000),**attrs)
        def textzone(text,x,y,width,height,size=14,bold=False,color=NAVY):
            z=zone(x,y,width,height,type='text')
            el(el(z,'formatted-text'),'run',fontname='Arial',fontsize=size,bold=str(bold).lower(),fontcolor=color).text=text
        textzone('CONSUMER COMPLAINT OPERATIONS  /  '+title.upper(),24,15,925,24,12,True,TEAL)
        zone(1035,12,141,32,name='Reset view',show_title='false')
        textzone(question,24,47,1152,44,26,True)
        textzone('2025 checking and savings complaints. Use public patterns to choose an internal validation question.',24,99,1152,27)
        for p,x,width in [('Account type',24,230),('Issue',274,405),('Month',699,160),('January sensitivity',879,297)]:
            zone(x,137,width,64,type='paramctrl',param=f'[Parameters].[{p}]')
        zone(24,203,730,64,type='paramctrl',param='[Parameters].[Company]')
        textzone('Company narrows the view; volume does not rank performance.',774,216,402,45,12)
        for i,(sheet_name,label) in enumerate([('Published complaints','Published complaints'),('Not timely','Not timely'),('Not timely rate','Not timely rate'),('Relief responses','Relief responses'),('Relief mix','Relief mix')]):
            zone(24+i*232,280,222,94,name=sheet_name,show_title='true')
        zone(24,382,1152,42,name='Selection note',show_title='false')
        if number=='01':
            zone(24,442,559,268,name='Monthly complaints',show_title='true')
            zone(613,442,563,268,name='Monthly not-timely exceptions',show_title='true')
            textzone('Start with Managing an account, then compare the two January exclusions.\nJanuary’s original 18,367 complaints include 11,444 in two fixed company/issue clusters.',24,729,1152,49,14)
        else:
            zone(24,442,559,269,name='Issues · count and not-timely rate',show_title='true')
            zone(613,442,563,269,name='Sub-issues · count and not-timely rate',show_title='true')
            textzone('NT = not timely. * = fewer than 30 complaints. Scroll each list for all categories. Hover a mark for full details.\nNext: check current internal case outcomes and transaction volumes before proposing a process change.',24,725,1152,54,13)
        textzone('Public complaint volume is not a defect or harm rate. Relief is response mix, not proof of customer satisfaction.',24,788,1152,24,12)
        textzone('Source: CFPB · pinned snapshot extracted July 29, 2026 · all 84,194 observations retained in the data.',24,817,1152,20,11,color='#5b6770')
        dashboard_sheets[name]=placed

    actions=el(w,'actions')
    for dashboard_name in dashboard_sheets:
        for p in CONTROLS:
            a=el(actions,'edit-parameter-action',caption='Reset '+p,name='[Reset '+dashboard_name[:2]+' '+p+']')
            el(a,'activation',type='on-select');el(a,'source',dashboard=dashboard_name,type='sheet',worksheet='Reset view')
            el(a,'agg-type',type='attr');el(a,'clear-option',type='do-nothing',value='s:LROOT:')
            ps=el(a,'params');el(ps,'param',name='source-field',value=ref('Reset '+p));el(ps,'param',name='target-parameter',value=f'[Parameters].[{p}]')
        a=el(actions,'action',caption='Clear reset selection',name='[Clear '+dashboard_name[:2]+']')
        el(a,'activation',auto_clear='true',type='on-select');el(a,'source',dashboard=dashboard_name,type='sheet',worksheet='Reset view')
        expression='tsl:'+quote('Reset view',safe='')+'?'+quote(f'[{D}].[Reset label]',safe='')+'~s0=<[Clear reset selection]~na>'
        el(a,'link',caption='Clear selection',delimiter=',',escape='\\',expression=expression,include_null='true',multi_select='true',url_escape='true')
        cmd=el(a,'command',command='tsc:tsl-filter');el(cmd,'param',name='on-empty',value='all');el(cmd,'param',name='target',value='Reset view')
    sources=el(actions,'datasources');el(sources,'datasource',name=D)
    dep=el(actions,'datasource-dependencies',datasource=D)
    for n in ['Reset label','Clear reset selection']: dep.append(copy.deepcopy(meta[n]))
    actions[:]=sorted(actions,key=lambda n:{'action':0,'datasources':1,'datasource-dependencies':2,'edit-parameter-action':3}[n.tag])
    w.remove(actions);w.insert(list(w).index(works),actions)
    windows=el(w,'windows')
    for name in sheet_names:
        win=el(windows,'window',**{'class':'worksheet','name':name,'hidden':'true'});el(win,'cards')
        el(el(win,'viewpoint'),'zoom',type='fit-width' if name.startswith(('Issues', 'Sub-issues')) else 'entire-view')
    for name,placed in dashboard_sheets.items():
        win=el(windows,'window',**{'class':'dashboard','name':name,**({'maximized':'true'} if name.startswith('01') else {})})
        views=el(win,'viewpoints')
        for s in placed: el(el(views,'viewpoint',name=s),'zoom',type='fit-width' if s.startswith(('Issues', 'Sub-issues')) else 'entire-view')
        el(win,'active',id='-1')
    E.indent(w)
    twb=out/(NAME+'.twb');E.ElementTree(w).write(twb,encoding='utf-8',xml_declaration=True)
    packed=copy.deepcopy(w);packed.find('.//named-connection/connection').set('dbname','Data/tableau-complaints.hyper')
    package=out/(NAME+'.twbx')
    with zipfile.ZipFile(package,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(twb.name,E.tostring(packed,encoding='utf-8',xml_declaration=True))
        z.write(hyper,'Data/tableau-complaints.hyper')
    print(f'Built {len(sheet_names)} worksheets, two dashboards and five shared parameters: {package}')
    return package


if __name__=='__main__':
    build()
