#!/usr/bin/env python3
"""Time a fresh evidence collector; underlying proof/test commands have separate logs."""
from pathlib import Path
import argparse,datetime,hashlib,json,platform,subprocess,sys,time
root=Path(__file__).resolve().parents[1];rd=root/'results/v0.28.0'
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);args=p.parse_args()
cmd=[sys.executable,str(root/'tools/summarize_v028.py'),'--baseline',str(args.baseline.resolve())]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
r=subprocess.run(cmd,cwd=root,capture_output=True,text=True)
(rd/'final_collector.log').write_text(r.stdout+r.stderr)
runtime=time.monotonic()-t
if r.returncode:raise SystemExit(r.returncode)
outputs=[]
for name in ['verification_summary.json','source_counts.json','axiom_audit_summary.json','negative_summary.json','affine_tests/summary.json','final_collector.log']:
    f=rd/name;outputs.append(dict(path=str(f.relative_to(root)),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
m=dict(schema_version=1,claim_id='AVOC-v028-affine-proof-and-execution-audit',
 repository=dict(commit='archive:'+hashlib.sha256(args.baseline.read_bytes()).hexdigest(),dirty=True),
 command=' '.join(cmd),
 environment=dict(software=['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d',
  'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],hardware=platform.platform()+' '+platform.machine()),
 mathematics=dict(assertion_tested='Final-source local Lean compilation/axiom/negative evidence plus exact GF(5) implementation regression; not empirical LLM effectiveness',
 coefficient_domain='generic Ring in theorems; exact GF(5) in runtime regression',
 conventions='column vectors, g after f, explicit bias, dense ring-operation tariff',
 inputs=['baseline v0.27 source archive','five new Lean modules and affine entrypoint','seeded exact homogeneous-matrix regression'],
 bounds=dict(local_targets=156,theorem_reports=1499,negative_files=75,wire_requests=1137,input_vectors=7120,seed=20260913,max_runtime_dimension=8),
 non_claims=['No global affine-factorization minimum certificate instantiated','No physical speedup theorem','No full mathlib source rebuild','No universal Python/IO refinement']),
 randomness=dict(used=True,generator='Python random.Random for the separately recorded regression',seed=20260913),
 run=dict(started_at=started,runtime_seconds=runtime,exit_status=r.returncode),outputs=outputs,
 checks=['156 current source/import/output/log records','1499 exact-name axiom reports','75 non-setup negative rejections','135 byte-identical inherited modules','source-pinned executed GF(5) regression'],
 result='PASS: collector validated all required final records',
 residual_risks=['This manifest times the collector, not the whole earlier build and regression','Installed kernel/compiler/dependency cache and host are trusted','Inherited validator is a documented v1-only adaptation'])
(rd/'computation_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(r.stdout)
