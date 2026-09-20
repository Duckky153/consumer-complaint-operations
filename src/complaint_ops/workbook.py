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
            el(members,'member',value='"'+value.replace('"','""')+'"',
               **({'alias':'Exclude top 2 groups'} if value==MODES[2] else {}))
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
        'Cohort note': ('string','measure','IF [Selected complaints] = 0 THEN "No complaints match. Change a control or Reset view. Rates are undefined." ELSEIF [Selected complaints] < 30 THEN "Small base: fewer than 30 complaints. Review individual cases; interpret percentages cautiously." ELSE "Rates use the selected complaints. Public counts do not measure company performance." END'),
        'Small group': ('string','measure','IF SUM([complaint_count]) < 30 THEN " *" ELSE "" END'),
        'Reset label': ('string','dimension','"Reset view"'),
        'Clear reset selection': ('string','dimension','"Clear selection"'),
    })
    for p,(source_field,default) in CONTROLS.items():
        if source_field:
            formulas['Current '+p] = ('string','measure',f'IF [Parameters].[{p}] = "{default}" THEN "" ELSEIF LEN([Parameters].[{p}]) > 24 THEN REGEXP_REPLACE(MAX([Parameters].[{p}]), "^(.{{1,24}}) +", "$1" + CHAR(10)) ELSE MAX([Parameters].[{p}]) END')
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
        el(el(title,'formatted-text'),'run',fontname='Arial',fontsize='17',fontcolor=NAVY,bold='true').text=name
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
            el(rule,'format',attr='font-family',value='Arial'); el(rule,'format',attr='font-size',value='14')
            el(rule,'format',attr='color',value=NAVY)
            if element == 'header' and dimension in {'issue', 'sub_issue'}:
                el(rule,'format',attr='width',field=ref(dimension),value='550')
                el(rule,'format',attr='wrap',field=ref(dimension),value='on')
        if dimension in {'issue', 'sub_issue'}:
            cell = el(style,'style-rule',element='cell')
            el(cell,'format',attr='height',field=ref(dimension),value='48')
        pane=el(el(t,'panes'),'pane');el(el(pane,'view'),'breakdown',value='auto')
        el(pane,'mark',**{'class':'Text' if text else 'Bar'})
        enc=el(pane,'encodings');el(enc,'text',column=ref(measure))
        if reset:
            for p in CONTROLS: el(enc,'lod',column=ref('Reset '+p))
            el(enc,'lod',column=ref('Clear reset selection'))
        if detail:
            el(enc,'text',column=ref('Not timely rate'));el(enc,'text',column=ref('Small group'))
        label=el(el(pane,'customized-label'),'formatted-text')
        font='32' if text and not dimension and measure not in {'Cohort note','Reset label'} and not measure.startswith('Current ') else '14'
        if measure in {'Not timely rate','Relief mix'}: font='20'
        label_text=f'<{ref(measure)}>'
        if detail: label_text+=f'    |    <{ref("Not timely rate")}> <{ref("Small group")}>'
        el(label,'run',fontname='Arial',fontsize=font,fontcolor=NAVY,bold='true' if font=='32' else 'false').text=label_text
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
    sheet('Issues · count and not-timely rate','Selected complaints','issue',text=True,filter_rows=True,detail=True)
    sheet('Sub-issues · count and not-timely rate','Selected complaints','sub_issue',text=True,filter_rows=True,detail=True)
    sheet('Selection note','Cohort note',text=True)
    sheet('Reset view','Reset label',text=True,reset=True)
    for p,(source_field,_) in CONTROLS.items():
        if source_field: sheet('Current '+p,'Current '+p,text=True)

    dashboards=el(w,'dashboards'); dashboard_sheets={}
    for number,title,question in [('01','Overview','Complaint patterns at a glance'),
                                  ('02','Investigation','Choose an issue to investigate')]:
        name=number+' · '+title
        db=el(dashboards,'dashboard',name=name)
        el(db,'layout-options');st=el(db,'style')
        el(el(st,'style-rule',element='dashboard'),'format',attr='background-color',value='#f7f6f2')
        for element in ['parameter-ctrl','parameter-ctrl-title']:
            rule=el(st,'style-rule',element=element)
            el(rule,'format',attr='font-size',value='14')
            el(rule,'format',attr='font-family',value='Arial')
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
        textzone('CONSUMER COMPLAINT OPERATIONS',24,18,1000,25,14,True,TEAL)
        textzone(question,340,58,836,43,26,True)
        textzone('2025 · Checking and savings accounts',340,105,836,26,16)
        # A stable left rail keeps controls out of the chart's reading path.
        rail=zone(16,56,300,716,type='text')
        el(el(rail,'formatted-text'),'run').text=''
        zs=el(rail,'zone-style');el(zs,'format',attr='background-color',value='#edf3f4')
        textzone('Filter the view',30,72,270,28,18,True)
        for i,p in enumerate(['Account type','Issue','Company','Month','January sensitivity']):
            y=116+i*95
            if p=='January sensitivity':
                zone(30,y,270,140,type='paramctrl',mode='list',param=f'[Parameters].[{p}]')
            else:
                textzone(p,30,y,270,23,14,True)
                zone(30,y+27,270,24,type='paramctrl',mode='compact',show_title='false',param=f'[Parameters].[{p}]')
                zone(30,y+52,270,42,name='Current '+p,show_title='false')
        z=zone(30,642,270,46,name='Reset view',show_title='false')
        zs=el(z,'zone-style');el(zs,'format',attr='border-color',value=TEAL)
        el(zs,'format',attr='border-width',value='1');el(zs,'format',attr='border-style',value='solid')
        textzone('Full January: 18,367 complaints\nTop 2 company/issue pairs: 11,444',30,700,270,60,13)
        # Three metric groups pair each count with its own rate.
        for x,label in [(340,'Complaints'),(624,'Not timely'),(908,'Responses with relief')]:
            textzone(label,x,137,268,28,17,True)
        zone(340,170,268,58,name='Published complaints',show_title='false')
        zone(624,170,268,58,name='Not timely',show_title='false')
        zone(908,170,268,58,name='Relief responses',show_title='false')
        for x,sheet_name in [(624,'Not timely rate'),(908,'Relief mix')]:
            zone(x,230,140,40,name=sheet_name,show_title='false')
            textzone('of complaints',x+148,237,120,28,13)
        textzone('Selected records',340,236,268,28,14)
        zone(340,277,836,50,name='Selection note',show_title='false')
        if number=='01':
            zone(340,335,400,395,name='Monthly complaints',show_title='true')
            zone(770,335,406,395,name='Monthly not-timely exceptions',show_title='true')
            textzone('Start with “Managing an account”. Compare both January exclusions.',340,738,836,45,15)
        else:
            textzone('Issues',340,337,380,28,17,True)
            textzone('Complaints  |  Not timely %',910,339,266,26,14,True)
            zone(340,372,836,154,name='Issues · count and not-timely rate',show_title='false')
            textzone('Sub-issues',340,541,380,28,17,True)
            textzone('Complaints  |  Not timely %',910,543,266,26,14,True)
            zone(340,576,836,173,name='Sub-issues · count and not-timely rate',show_title='false')
            textzone('Scroll for more rows. * Fewer than 30 complaints. Validate with internal cases.',340,751,836,30,14)
        textzone('Complaint volume is not a defect or harm rate. Relief describes response mix, not satisfaction.',24,790,1152,25,14)
        textzone('Source: CFPB · snapshot extracted July 29, 2026 · 84,194 records retained',24,822,1152,24,13,color='#465563')
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
