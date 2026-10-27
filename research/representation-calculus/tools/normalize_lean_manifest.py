"""Correct a run-record classification, without changing any proof, outcome or hash.

The auditor labels its JSON progress log a scientific result even though it was
not in declared_results. The validator correctly rejects that mismatch. This
postprocessor retains the raw manifest and labels that file as a log. It does
not add a newly declared mathematical result after execution.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    path=ROOT/'LEAN_MANIFEST.json';raw=path.read_bytes();m=json.loads(raw)
    rows=[x for x in m['outputs'] if x['path']=='evidence/LEAN_TASKS_PROGRESS.json']
    if len(rows)!=1:raise ValueError('Expected exactly one progress-log record')
    if rows[0]['kind']=='log':
        print('already normalized');return
    if rows[0]['kind']!='result':raise ValueError('Unexpected original classification')
    (ROOT/'evidence/LEAN_MANIFEST_RAW.json').write_bytes(raw)
    rows[0]['kind']='log'
    out=(json.dumps(m,indent=2)+'\n').encode();path.write_bytes(out)
    record={'operation':'classify the task-progress JSON as a log, not a scientific result',
      'timestamp_utc':datetime.now(timezone.utc).isoformat(),'raw_manifest_sha256':sha(raw),
      'normalized_manifest_sha256':sha(out),'normalizer_sha256':sha(Path(__file__).read_bytes()),
      'changed_field':'outputs[path=evidence/LEAN_TASKS_PROGRESS.json].kind',
      'old':'result','new':'log','all_proof_inputs_outcomes_and_output_hashes_unchanged':True}
    (ROOT/'evidence/LEAN_MANIFEST_NORMALIZATION.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
if __name__=='__main__':main()
