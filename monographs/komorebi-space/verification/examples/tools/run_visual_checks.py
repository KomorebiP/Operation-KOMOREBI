#!/usr/bin/env python3
"""Rebuild both visual investigations and record their bounded checks."""
from pathlib import Path
import datetime,hashlib,json,platform,subprocess,sys,time
import numpy,matplotlib

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    dest=ROOT/'build/visual_checks';dest.mkdir(parents=True,exist_ok=True)
    scripts=[ROOT/'tools/visual_companion'/n for n in ['foundations.py','analysis.py','style.py']]
    before={str(p.relative_to(ROOT)):sha(p) for p in scripts}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();clock=time.monotonic();runs=[]
    for name in ['foundations','analysis']:
        argv=[sys.executable,'tools/visual_companion/'+name+'.py']
        t=time.monotonic()
        with (dest/(name+'.log')).open('wb') as f:
            run=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=60)
        runs.append({'argv':argv,'exit_status':run.returncode,'runtime_seconds':time.monotonic()-t,'timeout_seconds':60})
        if run.returncode:raise SystemExit(f'{name} failed; see {dest/(name+".log")}')
    after={str(p.relative_to(ROOT)):sha(p) for p in scripts}
    assert before==after,'Figure sources changed during the recorded run.'
    records=[json.loads((ROOT/'build'/f'{name}_checks.json').read_text()) for name in ['foundations','analysis']]
    checks=[x for r in records for x in r['checks']]
    assert all(x['passed'] for x in checks)
    outputs=[ROOT/'build'/f'{n}_checks.json' for n in ['foundations','analysis']]
    outputs+=list((ROOT/'source/figures/visual_companion').glob('*.pdf'))
    outputs+=list(dest.glob('*.log'))
    manifest={
      'schema_version':1,'claim_id':'visual-companion-worked-examples',
      'repository':{'commit':'archive:b0b52eff0daf2c573aee7f1e8604f29b89fbf54ee9f34a2debede6b63360067c','dirty':True},
      'command':'python3 tools/run_visual_checks.py','exact_subprocess_runs':runs,
      'environment':{'software':[f'Python {platform.python_version()}',f'NumPy {numpy.__version__}',f'Matplotlib {matplotlib.__version__}'],'hardware':platform.machine()},
      'mathematics':{
        'assertion_tested':'The sixteen explicitly specified visual examples and their displayed values satisfy the recorded algebraic identities and finite numerical checks.',
        'coefficient_domain':'Integers, F2, exact rational arithmetic where marked, and IEEE 754 binary64 for plotted geometry and numerical formulas.',
        'conventions':'Scene formulas and domains are authoritative; matrix products act right to left; sequence coordinates start at the index explicitly printed; Euclidean norms unless a scene declares another metric.',
        'inputs':[{'path':p,'sha256':h} for p,h in before.items()],
        'bounds':{'foundation_scenes':8,'analytic_scenes':8,'binary_phase_triples':64,'scalar_binary_phase_changes':16,'diagonal_energy_prefix_maximum':4096,'scope':'Deterministic finite grids and worked values specified in the two plotting scripts; no stochastic sampling.'},
        'non_claims':['Finite graphics and numerical checks do not prove the general monograph theorems.','Infinite tail, series, and convergence statements use the stated algebra and existing mathematical arguments.','These illustrative variations are not claimed as new Lean instances.']},
      'randomness':{'used':False,'generator':'none','seed':None},
      'run':{'started_at':started,'runtime_seconds':time.monotonic()-clock,'exit_status':0},
      'input_hashes_after':after,'inputs_unchanged':True,
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(outputs)],
      'checks':checks,'result':'Finite algebraic and numerical assertions passed in the recorded ranges; rendering and proof-scope review are separate.',
      'residual_risks':['Numerical geometry uses binary64 and the tolerances recorded by each check.','Schema version 1 records finite bounds and actual commands but does not provide the version 2 resource-limit attestations.']}
    target=dest/'computation_manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{len(checks)} recorded checks passed; sources unchanged; manifest: {target}')

if __name__=='__main__':main()
