#!/usr/bin/env python3
"""Isolated mutation probes of the added runtime-provenance release block."""
from __future__ import annotations
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[2]
TOOL=ROOT/'tools/release_check_v041.py'
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
tree=ast.parse(TOOL.read_text())
main=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='main')
hash_check=next(node for node in ast.walk(main) if isinstance(node,ast.FunctionDef) and node.name=='check_hashes')
def runtime_assignment(node):
    return isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='runtime' for target in node.targets)
branch=next(node for node in ast.walk(main) if isinstance(node,ast.If) and any(runtime_assignment(child) for child in node.body))
start=next(i for i,child in enumerate(branch.body) if runtime_assignment(child))
block=compile(ast.Module(body=branch.body[start:],type_ignores=[]),'<actual runtime provenance block>','exec')
cases=[]
with tempfile.TemporaryDirectory(prefix='gate_review_runtime_tmp_',dir=ROOT/'results/v0.41.0') as directory:
    root=Path(directory)
    closure=['tools/RecorderMain.lean','AVOC/A.lean','AVOC/B.lean']
    for name in closure:
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('fixture source '+name)
        obj=root/'.lake/build/lib/lean'/Path(name).with_suffix('.olean');obj.parent.mkdir(parents=True,exist_ok=True);obj.write_text('fixture object '+name)
    baseline=dict(local_source_sha256={name:sha(root/name) for name in closure},
      local_olean_sha256={'.lake/build/lib/lean/'+str(Path(name).with_suffix('.olean')):sha(root/'.lake/build/lib/lean'/Path(name).with_suffix('.olean')) for name in closure},
      local_module_count=3,lean_executable='/synthetic/runtime/lean',lean_sha256='pinned-executable')
    def run(name,runtime,expect_rejection):
        ns=dict(ROOT=root,Path=Path,sha=sha,errors=[],pins={'lean_executable_sha256':'pinned-executable'},
          oracle={'actual_lean':{'runtime_provenance':runtime}},
          deps={'tools/RecorderMain.lean':{'AVOC/A.lean'},'AVOC/A.lean':{'AVOC/B.lean'},'AVOC/B.lean':set()})
        exec(compile(ast.Module(body=[hash_check],type_ignores=[]),'<actual file hash helper>','exec'),ns)
        exec(block,ns)
        cases.append(dict(name=name,rejected=bool(ns['errors']),expected_rejection=expect_rejection,passed=bool(ns['errors'])==expect_rejection,errors=ns['errors']))
    run('valid_transitive_closure_control',deepcopy(baseline),False)
    run('missing_runtime',{},True)
    run('wrong_runtime_type',[],True)
    for name,key,value in [('wrong_count','local_module_count',2),('no_executable','lean_executable',''),('wrong_executable_hash','lean_sha256','old')]:
        candidate=deepcopy(baseline);candidate[key]=value;run(name,candidate,True)
    for label,field in [('source','local_source_sha256'),('object','local_olean_sha256')]:
        candidate=deepcopy(baseline);candidate[field].pop(next(iter(candidate[field])));run('omitted_'+label,candidate,True)
        candidate=deepcopy(baseline);candidate[field]['extra']='fake';run('extra_'+label,candidate,True)
        candidate=deepcopy(baseline);candidate[field][next(iter(candidate[field]))]='stale';run('stale_'+label,candidate,True)
        victim=root/next(iter(baseline[field]));saved=victim.read_bytes();victim.unlink()
        run('missing_'+label,deepcopy(baseline),True);victim.write_bytes(saved)
    candidate=deepcopy(baseline);candidate['local_source_sha256'].pop('AVOC/B.lean');candidate['local_olean_sha256'].pop('.lake/build/lib/lean/AVOC/B.olean');candidate['local_module_count']=2
    run('transitive_dependency_omitted',candidate,True)
report=dict(kind='isolated_runtime_provenance_release_probes',status='passed' if all(c['passed'] for c in cases) else 'failed',cases=len(cases),passed=sum(c['passed'] for c in cases),records=cases,
 source_sha256={'tools/release_check_v041.py':sha(TOOL)},
 limits=['Synthetic fixtures exercise the actual extracted release block; no production evidence is modified.',
         'This validates rejection of the listed mutations, not arbitrary evidence authenticity or universal gate correctness.'])
out=ROOT/'results/v0.41.0/gate_review_runtime_probes.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({key:report[key] for key in ('status','cases','passed')}))
raise SystemExit(0 if report['status']=='passed' else 1)
