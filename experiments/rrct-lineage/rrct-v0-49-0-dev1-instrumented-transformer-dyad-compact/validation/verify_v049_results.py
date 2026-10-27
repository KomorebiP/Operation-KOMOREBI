#!/usr/bin/env python3
"""Verify packaged RRCT v0.49 evidence without retraining."""
from __future__ import annotations
import hashlib,json
from pathlib import Path


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()


def main() -> int:
    root=Path(__file__).resolve().parents[1]
    result=root/'validation/v0.49.0_instrumented_transformer_dyad/results'
    receipt=json.loads((result/'HOLDOUT_EXECUTION_RECEIPT.json').read_text())
    summary=json.loads((result/'V0_49_FROZEN_SUMMARY.json').read_text())
    analysis=result/'instrumented_transformer_dyad_analysis.json'
    rows=result/'instrumented_transformer_dyad_rows.csv'
    checks={
      'scientific_status':receipt['scientific_status']=='V049_FROZEN_PILOT_ENDPOINTS_MET',
      'all_endpoints_met':summary['all_endpoints_met'] and receipt['all_endpoints_met'],
      'endpoint_count':summary['endpoint_count']==23 and summary['endpoint_pass_count']==23,
      'analysis_sha256':sha256(analysis)==receipt['analysis_sha256'],
      'summary_sha256':sha256(result/'V0_49_FROZEN_SUMMARY.json')==receipt['summary_sha256'],
      'rows_sha256':sha256(rows)==receipt['rows_sha256'],
    }
    for name,digest in receipt['weight_sha256'].items():
        path=result/'weights'/name
        checks[f'weight::{name}']=path.is_file() and sha256(path)==digest
    freeze=root/'validation/V0_49_PREOUTCOME_FREEZE.json'
    freeze_payload=json.loads(freeze.read_text())
    freeze_failed=[]
    for item in freeze_payload['files']:
        path=root/item['relative_path']
        if not path.is_file() or path.stat().st_size!=item['size_bytes'] or sha256(path)!=item['sha256']:
            freeze_failed.append(item['relative_path'])
    checks['source_freeze']=not freeze_failed
    payload={
      'schema':'rrct.v049.result_verification.v1',
      'status':'V049_RESULTS_VERIFIED' if all(checks.values()) else 'V049_RESULTS_VERIFICATION_FAILED',
      'checks':checks,
      'failed_checks':[k for k,v in checks.items() if not v],
      'freeze_failed_files':freeze_failed,
      'all_checks_pass':all(checks.values()),
    }
    print(json.dumps(payload,indent=2,sort_keys=True))
    return 0 if payload['all_checks_pass'] else 1

if __name__=='__main__':raise SystemExit(main())
