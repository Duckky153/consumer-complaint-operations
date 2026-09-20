"""Build a typed local extract and verify every exported observation, including duplicates."""
from __future__ import annotations

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

from tableauhyperapi import (
    Connection, CreateMode, HyperProcess, SqlType, TableDefinition,
    TableName, Telemetry, escape_string_literal,
)
from .tableau import EXPORT_COLUMNS

ROOT = Path(__file__).resolve().parents[2]


def build_hyper(root: Path = ROOT) -> Path:
    source = root / 'data/processed/tableau-complaints.csv'
    target = root / 'data/processed/tableau-complaints.hyper'
    evidence = json.loads((root / 'evidence/tableau-data-verification.json').read_text())
    if not evidence['passed'] or hashlib.sha256(source.read_bytes()).hexdigest() != evidence['export_sha256']:
        raise ValueError('Rebuild and reconcile the CSV before creating Hyper')
    with source.open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != EXPORT_COLUMNS:
            raise ValueError('Unexpected export schema')
        csv_rows = list(reader)
    integers = {'complaint_count', 'not_timely', 'has_relief', 'january_top_cluster'}
    types = {n: SqlType.big_int() if n in integers else SqlType.date() if n == 'date_received' else SqlType.text()
             for n in EXPORT_COLUMNS}
    table = TableDefinition(TableName('Extract', 'Extract'),
                            [TableDefinition.Column(n, types[n]) for n in EXPORT_COLUMNS])
    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
                      parameters={'default_database_version': '2', 'log_config': ''}) as process:
        with Connection(process.endpoint, target, CreateMode.CREATE_AND_REPLACE) as conn:
            conn.catalog.create_schema('Extract')
            conn.catalog.create_table(table)
            inserted = conn.execute_command(
                f"COPY {table.table_name} FROM {escape_string_literal(str(source))} "
                "WITH (format csv, delimiter ',', header)")
            actual = Counter(tuple(str(v) for v in row) for row in conn.execute_list_query(f'SELECT * FROM {table.table_name}'))
            expected = Counter(tuple(row[n] for n in EXPORT_COLUMNS) for row in csv_rows)
            if actual != expected or inserted != evidence['rows']:
                raise ValueError('Hyper differs from CSV observations or multiplicities')
            conditions = [
                'TRUE', "issue='Managing an account'", "received_month='2025-06'",
                "company='CAPITAL ONE FINANCIAL CORPORATION' AND issue='Managing an account'",
                "sub_product='Checking account' AND issue='Managing an account'",
                "received_month<>'2025-01'", 'january_top_cluster=0',
            ]
            checks = []
            for cohort, where in zip(evidence['checks'], conditions, strict=True):
                values = conn.execute_list_query(f'SELECT COUNT(*), COALESCE(SUM(not_timely),0), COALESCE(SUM(has_relief),0) FROM {table.table_name} WHERE {where}')[0]
                if values != cohort['sql']:
                    raise ValueError(f'Hyper cohort mismatch: {cohort["scope"]}')
                checks.append({'scope': cohort['scope'], 'hyper': values, 'sql': cohort['sql'], 'passed': True})
    receipt = {'passed': True, 'rows': inserted, 'fields': EXPORT_COLUMNS,
               'all_rows_and_multiplicities_match': True, 'checks': checks,
               'source_sha256': evidence['source_sha256'], 'export_sha256': evidence['export_sha256'],
               'hyper_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'telemetry': 'DO_NOT_SEND_USAGE_DATA_TO_TABLEAU',
               'scope': 'Data engine verification; native workbook interactions are separate'}
    (root/'evidence/tableau-hyper-verification.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return target


if __name__ == '__main__':
    print(build_hyper())
