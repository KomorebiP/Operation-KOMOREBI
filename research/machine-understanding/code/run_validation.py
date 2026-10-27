#!/usr/bin/env python3
"""Run bounded finite checks and record project-local computation evidence.

This is not independent attestation or proof-assistant verification. Each child
has a 30-second wall timeout. No separate memory or CPU affinity cap is imposed.
The v1 manifest is accompanied by input hashes and explicit execution records.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, platform, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='Machine_Understanding_v1.0.0'

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=Path('build/validation_rerun'))
    args=parser.parse_args(); out=(ROOT/args.out_dir).resolve()
    if not out.is_relative_to(ROOT): raise ValueError('Output directory must remain within this project.')
    out.mkdir(parents=True,exist_ok=True)
    inputs=sorted([ROOT/(BASE+'.tex'), ROOT/'CLAIMS.json',
                   *ROOT.glob('code/*.py'), *ROOT.glob('figures/*.pdf')])
    before={str(p.relative_to(ROOT)):digest(p) for p in inputs}
    start=datetime.datetime.now(datetime.timezone.utc).isoformat(); clock=time.monotonic()
    commands=[]; exit_status=0; outputs=[]
    for script,name in [('finite_checks.py','predecessor_checks'),('expanded_checks.py','expanded_checks'),
                        ('edition_checks.py','edition_checks'),('demo_expanded.py','expanded_demo'),
                        ('demo_first_edition.py','first_edition_demo'),('audit_source.py','source_audit')]:
        result=out/(name+'.json'); log=out/(name+'.log')
        argv=[sys.executable,'code/'+script,'--output',str(result.relative_to(ROOT))]
        t=time.monotonic()
        try:
            p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=30)
            log.write_text(p.stdout+p.stderr); status=p.returncode
        except subprocess.TimeoutExpired as e:
            status=124
            def txt(x): return x.decode(errors='replace') if isinstance(x,bytes) else (x or '')
            log.write_text(txt(e.stdout)+txt(e.stderr)+'\nWALL TIMEOUT: 30 seconds\n')
        commands.append({'argv':argv,'runtime_seconds':time.monotonic()-t,
                         'exit_status':status,'timeout_seconds':30})
        outputs.append(log)
        if result.exists(): outputs.append(result)
        if status: exit_status=status; break
    after={str(p.relative_to(ROOT)):digest(p) for p in inputs}
    if before!=after: exit_status=exit_status or 1
    results={}
    for name in ('predecessor_checks','expanded_checks','edition_checks'):
        p=out/(name+'.json')
        if p.exists():results[name]=json.loads(p.read_text())
    groups=sum(a['group_count'] for a in results.values())
    assertions=sum(a['assertions'] for a in results.values())
    if len(results)!=3 or any(a['status']!='passed' for a in results.values()):exit_status=exit_status or 1
    if groups!=38 or assertions!=252669:exit_status=exit_status or 1
    result_text=f"{'Passed' if exit_status==0 else 'Failed'}: {groups} groups, {assertions} finite assertions."
    manifest={'schema_version':1,'claim_id':'MU-1.0-FINITE-CONSTRUCTIONS',
       'repository':{'commit':'unavailable','dirty':True},
       'command':[sys.executable,'code/run_validation.py','--out-dir',str(out.relative_to(ROOT))],
       'environment':{'software':[f'Python {platform.python_version()}'],
                      'hardware':f'CPU-only, {platform.machine()}; {platform.platform()}'},
       'mathematics':{'assertion_tested':'Finite constructions for reusable state, transport, Bayesian correction, conditioning, recipient graphs, acquisition policy witnesses, fixed decoder covering, and compiled resource frontiers.',
         'coefficient_domain':'Integers, fractions.Fraction, and rational coefficients of logarithms of primes.',
         'conventions':'All probabilistic conditioning requires positive evidence. Exact deterministic acquisition tracks current states after physical transitions. Test horizons are declared finite contracts.',
         'inputs':list(before),
         'bounds':{'detailed_domains':'See per-group domain fields in predecessor_checks.json expanded_checks.json, and edition_checks.json.',
                   'original_register_states':125,'new_groups':10,'total_groups':groups,'total_assertions':assertions},
         'non_claims':['Not a general proof by enumeration.','Not empirical evidence about a neural model.','Not an independent or proof-kernel audit.','Not an efficient or unrestricted optimizer for joint noisy inquiry and explanation.']},
       'randomness':{'used':False,'generator':'none','seed':None},
       'run':{'started_at':start,'runtime_seconds':time.monotonic()-clock,'exit_status':exit_status},
       'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in outputs],
       'checks':[result_text,'Six separate commands (including demo and syntactic source audit) recorded.','Input hashes unchanged.' if before==after else 'Input hashes changed.'],
       'result':result_text,
       'residual_risks':['Legacy schema v1 has no external execution attestation or Git revision.','Resource control is a per-child wall timeout only.','The supplied manifest verifier is project-authored, not an authenticated distribution of the plugin validator.','Decoders and policy models are explicitly supplied, not learned.'],
       'input_artifacts':[{'path':name,'sha256':h,'sha256_after':after[name]} for name,h in before.items()],
       'executions':commands,'group_count':groups,'assertions':assertions}
    (out/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(result_text)
    if exit_status:raise SystemExit(exit_status)
if __name__=='__main__':main()
