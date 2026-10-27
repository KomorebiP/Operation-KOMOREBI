#!/usr/bin/env python3
"""Run a fresh bounded test suite with current-source and output provenance."""
from pathlib import Path
import argparse,hashlib,json,os,platform,subprocess,sys,time
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.25.0'
p=argparse.ArgumentParser();p.add_argument('mode',choices=['differential','live']);args=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((ROOT/'synthesis_source_pins.json').read_text())
paths=set(pins['sources'])|{'checks/test_synthesis.py','tools/record_synthesis_tests.py','synthesis_source_pins.json'}
paths|={str(f.relative_to(ROOT)) for f in (ROOT/'examples/synthesis').glob('*.json')}
before={rel:sha(ROOT/rel) for rel in sorted(paths)}
cmd=[sys.executable,'checks/test_synthesis.py']+(['--live'] if args.mode=='live' else [])
started=datetime.now(timezone.utc).isoformat();t=time.monotonic()
log=RD/('recorded_'+args.mode+'.log')
with log.open('w') as f:
 r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=120)
after={rel:sha(ROOT/rel) for rel in sorted(paths)}
outputs={str(log.relative_to(ROOT)):sha(log)}
for name in (['live_summary.json','demo_pair.json','demo_guard.json','demo_unprofitable.json'] if args.mode=='live' else ['differential_summary.json']):
 f=RD/name
 if f.exists():outputs[str(f.relative_to(ROOT))]=sha(f)
if args.mode=='differential':
 for pattern in ['differential_*_requests.json','differential_*_stdout.jsonl','checker_*','invalid_wire_*']:
  for f in RD.glob(pattern):
   if f.is_file():outputs[str(f.relative_to(ROOT))]=sha(f)
record={'command':cmd,'started_at':started,'runtime_seconds':time.monotonic()-t,'returncode':r.returncode,
 'sources_before':before,'sources_after':after,'sources_unchanged':before==after,'outputs':outputs,
 'python':sys.version,'platform':platform.platform(), 'passed':r.returncode==0 and before==after}
(RD/(args.mode+'_provenance.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ['sources_before','sources_after','outputs']},indent=2))
if not record['passed']:print(log.read_text()[-3000:]);raise SystemExit(1)
