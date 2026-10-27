#!/usr/bin/env python3
"""Parallel independent Lean replay and negative controls for B05.

This verifies model theorems and preserved KTG interfaces, not original IUT.
Run from the package root with actual Lean/ Lake executables via environment.
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'formalization'/'lean'
OUT=ROOT/'verification'/'b05'
OUT.mkdir(parents=True,exist_ok=True)
LEAN=os.environ.get('LEAN_BIN','lean')
LAKE=os.environ.get('LAKE_BIN','lake')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def run(argv, env=None, timeout=100):
    cp=subprocess.run(argv,cwd=PROJECT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
    return cp.returncode, cp.stdout

sources=sorted((PROJECT/'KTG').glob('*.lean'))+[PROJECT/'KTG.lean']
base=Path('/mnt/data/Komorebi_IUT_Hodge_Reduct_B04/formalization/lean')
# The ancestor root may not be present in a redistributed copy. In that case
# use the included predecessor hashes from the B04 final manifest.
manifest=ROOT/'MANIFEST_BLOCK04_PREDECESSOR.json'
if not manifest.is_file():
    raise SystemExit('FAIL: missing pinned B04 source-hash manifest')
baseline=json.loads(manifest.read_text())['sha256_by_basename']
missing=[name for name in baseline if not (PROJECT/'KTG'/name).is_file()]
changed=[name for name,digest in baseline.items()
         if (PROJECT/'KTG'/name).is_file() and sha(PROJECT/'KTG'/name)!=digest]

# Run a genuine independent warning-as-error Lean elaboration on each source.
env=os.environ.copy()
env['LEAN_PATH']=str(PROJECT/'.lake/build/lib/lean')
with TemporaryDirectory(prefix='b05-lean-independent-') as tmp:
    def compile_one(p):
        fname=p.name.replace('.lean','')
        output=Path(tmp)/f'{fname}.olean'
        return p, run([LEAN,'-j1','-DwarningAsError=true','-o',str(output),str(p)],env,timeout=100)
    checks={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(compile_one,p) for p in sources]):
            p,(code,out)=f.result()
            rel=str(p.relative_to(PROJECT))
            checks[rel]={'status':'PASS' if code==0 else 'FAIL', 'returncode':code}
            (OUT/(p.stem+'_independent.log')).write_text(out)

# Negative controls must produce elaboration errors.
negative={}
for p in sorted((ROOT/'experiments'/'negative_controls_b05').glob('*.lean')):
    code,out=run([LEAN,'-j1','-DwarningAsError=true',str(p)],env,timeout=100)
    negative[p.name]={'status':'PASS' if code!=0 and 'error' in out else 'FAIL','returncode':code}
    (OUT/(p.stem+'_rejected.log')).write_text(out)

# Audits of preserved typed IUT III interfaces and predecessor core.
spec=importlib.util.spec_from_file_location('legacy',ROOT/'verification'/'verify_block03.py')
legacy=importlib.util.module_from_spec(spec); spec.loader.exec_module(legacy)
contract=legacy.contract_audit()
sourcehash={str(p.relative_to(ROOT)):sha(p) for p in sources}
core=legacy.predecessor_core_audit(sourcehash)
forbidden={}
for p in sources:
    clean=legacy.strip_lean_comments(p.read_text())
    hits=re.findall(r'\b(?:sorry|admit|unsafe)\b|^\s*axiom\b',clean,re.M)
    if hits:forbidden[p.name]=hits

ok=all(d['status']=='PASS' for d in checks.values()) and all(d['status']=='PASS' for d in negative.values()) and not changed and not missing and not forbidden and contract['status']=='PASS' and core['status']=='PASS'
report={
    'status':'PASS' if ok else 'FAIL',
    'utc':datetime.now(timezone.utc).isoformat(),
    'lean_version':run([LEAN,'--version'])[1].strip(),
    'source_count':len(sources)-1,
    'source_and_entrypoint_count':len(sources),
    'new_modules':['ValuationHulls.lean','ValuationCost.lean','HodgeAnchors.lean','HodgeStructural.lean','IUT312DiscreteWitness.lean'],
    'independent_compilation':checks,
    'negative_controls':negative,
    'predecessor_modified_modules':changed,
    'predecessor_missing_modules':missing,
    'forbidden_tokens':forbidden,
    'block03_contract_audit':contract['status'],
    'predecessor_block02_audit':core['status'],
    'new_source_sha256':{p.name:sha(p) for p in sources if p.name in ('ValuationHulls.lean','ValuationCost.lean','HodgeAnchors.lean','HodgeStructural.lean','IUT312DiscreteWitness.lean')},
    'claims':{'theoretic_local_valuation_orbit':'PROVED_FOR_VALUATION_SHELL',
              'local_integral_saturation':'PROVED_FOR_VALUATION_SHELL',
              'local_lattice_min_cost':'PROVED_FOR_IDEAL_EXPONENT_MODEL',
              'F17_stronger_reconstruction_obstruction':'PROVED_FOR_MARKED_FINITE_FIELDS',
              'discrete_approximate_source_witness':'CONDITIONAL_NUMERIC_THEOREM',
              'actual_iut_prime_strips':'OPEN',
              'actual_iut_step_xi_e_witness':'OPEN',
              'abc':'NOT_PROVED'},
}
(OUT/'verification.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:report[k] for k in ('status','source_count','new_modules','negative_controls','predecessor_modified_modules','block03_contract_audit','predecessor_block02_audit')},indent=2))
raise SystemExit(0 if ok else 1)
