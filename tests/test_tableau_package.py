"""Artifact tests complement (and never replace) recorded native Tableau tests."""
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile

import pytest

from complaint_ops.hyper import build_hyper
from complaint_ops.tableau import EXPORT_COLUMNS
from complaint_ops.workbook import build, CONTROLS


@pytest.fixture
def verified_extract(tmp_path):
    processed = tmp_path/'data/processed'
    processed.mkdir(parents=True)
    evidence = tmp_path/'evidence'
    evidence.mkdir()
    path = processed/'tableau-complaints.csv'
    # Two identical allowed-field rows are distinct observations and must survive.
    values = ['2025-06-01','2025-06','Checking account','Managing an account',
              'Unknown','CAPITAL ONE FINANCIAL CORPORATION',1,1,0,0]
    with path.open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(EXPORT_COLUMNS);writer.writerows([values,values])
    scopes=['all','Managing an account','June','CAPITAL ONE FINANCIAL CORPORATION / Managing an account',
            'Checking account / Managing an account','Exclude January','Exclude January top two clusters']
    (evidence/'tableau-data-verification.json').write_text(json.dumps({
        'passed':True,'rows':2,'source_sha256':'fixture',
        'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'checks':[{'scope':s,'sql':[2,2,0]} for s in scopes],
    }))
    build_hyper(tmp_path)
    return tmp_path


def test_hyper_preserves_observation_multiplicity_and_package_is_self_contained(verified_extract):
    root=verified_extract
    receipt=json.loads((root/'evidence/tableau-hyper-verification.json').read_text())
    assert receipt['rows']==2 and receipt['all_rows_and_multiplicities_match']
    package=build(root)
    with zipfile.ZipFile(package) as z:
        assert set(z.namelist())=={'Consumer Complaint Operations.twb','Data/tableau-complaints.hyper'}
        assert hashlib.sha256(z.read('Data/tableau-complaints.hyper')).hexdigest()==receipt['hyper_sha256']
        workbook=ET.fromstring(z.read('Consumer Complaint Operations.twb'))
    assert workbook.find('.//named-connection/connection').get('dbname')=='Data/tableau-complaints.hyper'
    source=workbook.find("datasources/datasource[@name='complaints']")
    physical=[c.get('name').strip('[]') for c in source.findall('column') if c.find('calculation') is None]
    assert physical==EXPORT_COLUMNS
    dashboards=workbook.findall('dashboards/dashboard')
    assert len(dashboards)==2
    for db in dashboards:
        assert {z.get('param') for z in db.findall(".//zone[@type='paramctrl']")}=={f'[Parameters].[{p}]' for p in CONTROLS}
        actions=[a for a in workbook.findall('actions/edit-parameter-action') if a.find('source').get('dashboard')==db.get('name')]
        assert {a.find("params/param[@name='target-parameter']").get('value') for a in actions}=={f'[Parameters].[{p}]' for p in CONTROLS}
    for pane in workbook.findall('.//pane'):
        tags=[c.tag for c in pane]
        assert tags.index('customized-tooltip') < tags.index('customized-label')


def test_workbook_rejects_csv_changed_after_hyper_verification(verified_extract):
    path=verified_extract/'data/processed/tableau-complaints.csv'
    path.write_text(path.read_text().replace('CAPITAL ONE','OTHER'))
    with pytest.raises(ValueError,match='CSV changed'):
        build(verified_extract)


def test_workbook_rejects_changed_hyper(verified_extract):
    path=verified_extract/'data/processed/tableau-complaints.hyper'
    with path.open('ab') as stream: stream.write(b'changed')
    with pytest.raises(ValueError,match='verify Hyper'):
        build(verified_extract)


def test_hyper_rejects_unverified_csv(verified_extract):
    path=verified_extract/'data/processed/tableau-complaints.csv'
    path.write_text(path.read_text()+'\n')
    with pytest.raises(ValueError,match='reconcile the CSV'):
        build_hyper(verified_extract)
