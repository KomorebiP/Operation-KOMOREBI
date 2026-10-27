"""Run the two bounded exact suites and record project-local execution evidence."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    val=ROOT/'validation';val.mkdir(exist_ok=True)
    paths=[ROOT/'Grounded_Abstraction_v0.5.0.tex']+sorted((ROOT/'code').glob('*.py'))+sorted((ROOT/'figures').glob('*.pdf'))
    names=[str(p.relative_to(ROOT)) for p in paths]
    before={name:sha(ROOT/name) for name in names}
    started=datetime.now(timezone.utc).isoformat();t=time.perf_counter();runs=[]
    for script in ('exact_checks.py','observable_checks.py','preservation_audit.py'):
        argv=[sys.executable,'code/'+script];r0=time.perf_counter()
        try:
            completed=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,timeout=20,check=False)
        except subprocess.TimeoutExpired as exc:
            (val/(script+'.timeout.txt')).write_text(str(exc)+'\n')
            raise RuntimeError('A bounded check timed out; no completed receipt was issued') from exc
        log='validation/'+script+'.log'
        (ROOT/log).write_text(completed.stdout+completed.stderr)
        runs.append({'argv':argv,'exit_status':completed.returncode,'runtime_seconds':time.perf_counter()-r0,'wall_limit_seconds':20,'log':log})
        if completed.returncode:raise RuntimeError('Check failed: '+script+'; see '+log)
    old=json.loads((val/'exact_checks.json').read_text());new=json.loads((val/'observable_checks.json').read_text())
    for r in (old,new):
        if r['status']!='PASS' or r['assertions']!=sum(g['assertions'] for g in r['groups']):
            raise RuntimeError('Inconsistent finite result inventory')
    aggregate={'status':'PASS','group_count':old['group_count']+new['group_count'],
               'assertions':old['assertions']+new['assertions'],
               'predecessor':{'groups':old['group_count'],'assertions':old['assertions']},
               'new':{'groups':new['group_count'],'assertions':new['assertions']},
               'non_claim':'Bounded exact checks, not training, empirical generality, or proofs by enumeration.'}
    (val/'aggregate_checks.json').write_text(json.dumps(aggregate,indent=2)+'\n')
    after={name:sha(ROOT/name) for name in names}
    if before!=after:raise RuntimeError('Pinned execution input changed during checks')
    outputs=['validation/exact_checks.json','validation/observable_checks.json','validation/aggregate_checks.json',
             'validation/preservation.json','data/illustrations.json','data/observable_illustrations.json']+[x['log'] for x in runs]
    groups=old['groups']+new['groups']
    record={'schema_version':1,'claim_id':'grounded-abstraction-exact-theory-illustrations-v0.5.0',
            'repository':{'commit':'unavailable','dirty':True},
            'command':[sys.executable,'code/run_checks.py'],
            'environment':{'software':[{'name':'Python','version':platform.python_version()}],
                           'hardware':platform.platform()+'; CPU only; no imposed memory or affinity cap'},
            'mathematics':{'assertion_tested':'Exact bounded checks of evidence, correction memory, calibration, fixed-model output agreement, common observable quotients, linear initialization and likelihood-profile migration.',
                           'coefficient_domain':'Integers, finite sets, exact fractions.Fraction and F2',
                           'conventions':'New matrix code is row-major. The retained first-draft helper uses columns. Words execute in chronological order. One candidate model is fixed per execution; switching is a separate control. No posterior is assigned to a zero-probability report.',
                           'inputs':names,'bounds':{g['name']:g['domain'] for g in groups},
                           'non_claims':['No universal proof by finite enumeration.','No learning-agent implementation or training.','No Lean or independent scientific replication.']},
            'randomness':{'used':False,'generator':'','seed':None},
            'run':{'started_at':started,'runtime_seconds':time.perf_counter()-t,'exit_status':0},
            'outputs':[{'path':name,'sha256':sha(ROOT/name)} for name in outputs],
            'checks':['Every subprocess completed within its declared twenty-second wall limit.',
                      'All pinned input hashes agree before and after execution.',
                      f"{aggregate['group_count']} exact groups and {aggregate['assertions']} assertions passed.",
                      'Ten predecessor statement/proof pairs and two reference programs preserved.'],
            'result':'Implementation and finite assertions verified within the recorded domains.',
            'residual_risks':['Proofs and checking programs are project-authored, not independent review.',
                              'Legacy-v1 manifest with extra input pins and project-local validation, not an authenticated external audit.',
                              'No repository commit, enforced memory cap, proof kernel or external execution attestation.'],
            'input_artifacts':[{'path':name,'sha256':before[name],'sha256_after':after[name]} for name in names],
            'subprocesses':runs}
    (val/'computation_manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print(f"PASS: {aggregate['group_count']} groups; {aggregate['assertions']} exact assertions. Local receipt recorded.")

if __name__=='__main__':main()
