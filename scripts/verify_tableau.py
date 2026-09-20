"""Independent source SQLite / packaged Hyper acceptance, without native-UI claims."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import pandas as pd
from tableauhyperapi import Connection, HyperProcess, Telemetry, TableName
from complaint_ops.tableau import PINNED_SHA256, EXPORT_COLUMNS

ROOT=Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    raw=root/'data/raw/complaints_2025_checking_savings.csv'
    if hashlib.sha256(raw.read_bytes()).hexdigest()!=PINNED_SHA256:
        raise ValueError('Source no longer matches the pinned snapshot')
    source=pd.read_csv(raw)
    package=root/'tableau/Consumer Complaint Operations.twbx'
    expected=json.loads((root/'evidence/tableau-hyper-verification.json').read_text())
    with zipfile.ZipFile(package) as z:
        if set(z.namelist())!={'Consumer Complaint Operations.twb','Data/tableau-complaints.hyper'}:
            raise ValueError('Unexpected package member')
        workbook=ET.fromstring(z.read('Consumer Complaint Operations.twb'))
        if workbook.find('.//named-connection/connection').get('dbname')!='Data/tableau-complaints.hyper':
            raise ValueError('Package does not use relative packaged data')
        data=z.read('Data/tableau-complaints.hyper')
    if hashlib.sha256(data).hexdigest()!=expected['hyper_sha256']:
        raise ValueError('Packaged Hyper is not the verified extract')
    cases=[
        ('Baseline','1=1','TRUE'),
        ('Managing an account',"issue='Managing an account'", "issue='Managing an account'"),
        ('June',"substr(date_received,1,7)='2025-06'","received_month='2025-06'"),
        ('Company / issue',"company='CAPITAL ONE FINANCIAL CORPORATION' AND issue='Managing an account'",None),
        ('Checking / Managing',"sub_product='Checking account' AND issue='Managing an account'",None),
        ('Exclude January',"substr(date_received,1,7)<>'2025-01'","received_month<>'2025-01'"),
        ('Exclude fixed clusters',"NOT (substr(date_received,1,7)='2025-01' AND (company,issue) IN (SELECT company,issue FROM raw WHERE substr(date_received,1,7)='2025-01' GROUP BY company,issue ORDER BY count(*) DESC,company,issue LIMIT 2))",'january_top_cluster=0'),
        ('Small base',"company='TRUEBILL, INC'",None),
        ('Empty',"company='NAVY FEDERAL CREDIT UNION' AND sub_product='CD (Certificate of Deposit)' AND issue='Closing an account' AND substr(date_received,1,7)='2025-01'", "company='NAVY FEDERAL CREDIT UNION' AND sub_product='CD (Certificate of Deposit)' AND issue='Closing an account' AND received_month='2025-01'"),
        ('Unknown sub-issue','sub_issue IS NULL',"sub_issue='Unknown'"),
        ('29 observations',"company='JPMORGAN CHASE & CO.' AND sub_product='Checking account' AND issue='Problem caused by your funds being low' AND substr(date_received,1,7)='2025-02'", "company='JPMORGAN CHASE & CO.' AND sub_product='Checking account' AND issue='Problem caused by your funds being low' AND received_month='2025-02'"),
    ]
    checks=[]
    with tempfile.TemporaryDirectory(prefix='cco-package-check-') as scratch, sqlite3.connect(':memory:') as sql:
        source.to_sql('raw',sql,index=False)
        path=Path(scratch)/'packaged.hyper';path.write_bytes(data)
        with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,parameters={'log_config':''}) as process:
            with Connection(process.endpoint,path) as conn:
                columns=[str(c.name).strip('"') for c in conn.catalog.get_table_definition(TableName('Extract','Extract')).columns]
                if columns!=EXPORT_COLUMNS: raise ValueError('Packaged field allowlist changed')
                for label,raw_where,hyper_where in cases:
                    reference=list(sql.execute(f"SELECT COUNT(*), COALESCE(SUM(timely='No'),0), COALESCE(SUM(company_response IN ('Closed with monetary relief','Closed with non-monetary relief')),0) FROM raw WHERE {raw_where}").fetchone())
                    actual=conn.execute_list_query(f'SELECT COUNT(*), COALESCE(SUM(not_timely),0), COALESCE(SUM(has_relief),0) FROM "Extract"."Extract" WHERE {hyper_where or raw_where}')[0]
                    if reference!=actual: raise ValueError(f'Packaged cohort mismatch: {label}')
                    checks.append({'scope':label,'source_sql':reference,'packaged_hyper':actual,'passed':True})
                # Counter comparison preserves multiplicity without publishing complaint IDs.
                rows=conn.execute_list_query('SELECT * FROM "Extract"."Extract"')
                csv_rows=pd.read_csv(root/'data/processed/tableau-complaints.csv',dtype=str).itertuples(index=False,name=None)
                if Counter(tuple(map(str,row)) for row in rows)!=Counter(csv_rows):
                    raise ValueError('Packaged observations differ from the CSV')
    receipt={'passed':True,'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),
             'source_sha256':PINNED_SHA256,'hyper_sha256':expected['hyper_sha256'],
             'all_packaged_rows_and_multiplicities_match':True,'checks':checks,
             'scope':'Automated packaged-data verification; see native-tableau-readability-verification.json for current GUI evidence'}
    (root/'evidence/tableau-package-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'Packaged Hyper: {len(checks)} source-SQL cohorts and all row multiplicities passed')


if __name__=='__main__': verify()
