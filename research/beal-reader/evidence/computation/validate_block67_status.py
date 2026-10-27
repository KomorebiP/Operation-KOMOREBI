#!/usr/bin/env python3
"""Correct a wrapper success-label mismatch without hiding its failed run.

The unchanged Block67 verifier reports PASS. The original generic wrapper
incorrectly required PASS_DECLARED_CHECKS. The wrapper exit1 remains recorded.
This separate bounded check interprets the actual successful subprocess and all
eight scientific comparisons, rather than rerunning or rewriting that evidence.
"""
import argparse, hashlib, json
from pathlib import Path

def require(value, message):
    if not value:raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);ns=p.parse_args()
    source=Path('evidence/computation/block67-run')
    report=json.loads((source/'report.json').read_text());invocation=json.loads((source/'extraction_and_invocation.json').read_text());manifest=json.loads((source/'manifest.json').read_text())
    plan=json.loads(Path('evidence/computation/plans/block67.json').read_text())
    require(report['status']=='PASS' and invocation['exit_status']==0,'Actual original verifier did not pass')
    require(manifest['run']['status']=='failed' and manifest['run']['exit_status']==1,'Original wrapper failure must remain visible')
    require('Verifier did not report PASS_DECLARED_CHECKS' in (source/'stderr.txt').read_text(),'Different failure cannot be interpreted as a label mismatch')
    expected={Path(k).name:v['original_byte_sha256'] for k,v in plan['expected_results'].items()}
    require(report['regenerated_output_sha256']==expected and len(expected)==8,'Regenerated scientific bytes differ from archived originals')
    require(len(report['negative_controls'])==9,'Archived corruption controls incomplete')
    require(all(x['sha256']==x['sha256_after'] for x in manifest['input_artifacts']),'Input changed in failed wrapper run')
    for record in manifest['outputs']:
        require(sha(Path(record['path']))==record['sha256'],'Recorded output hash changed')
    result={'status':'PASS_CORRECTED_INTERPRETATION','scientific_verifier_status':'PASS','scientific_verifier_exit_status':0,
            'original_wrapper_status':'failed','original_wrapper_exit_status':1,'wrapper_failure_reason':'Success label mismatch: PASS versus PASS_DECLARED_CHECKS',
            'complete_scientific_results_compared':8,'archived_rejection_controls':9,'scientific_algorithms_edited':False,
            'scientific_replay_repeated':False,'original_failure_record_rewritten':False,
            'nonclaims':['This is an interpretation check of an already observed exact replay, not a new arithmetic experiment or a Beal proof.']}
    ns.output.mkdir(parents=True,exist_ok=True);(ns.output/'status_review.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
