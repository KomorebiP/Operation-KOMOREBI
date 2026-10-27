"""Replay eight calculation suites and sixteen example/generator programs, with checkpointed batching.

Ordinary use: python run_reference_checks.py --verify-hashes
Bounded runners may add --batch-start 0 --batch-count 3 --session review,
then continue at successive script indices with the same session. Only a report
containing every expected successful script is marked as a complete PASS.
"""
from __future__ import annotations
import argparse,hashlib,json,platform,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCRIPTS=[
 'checks/exact_foundation_checks.py','checks/learning_stability_checks.py',
 'checks/controlled_stochastic_checks.py','checks/certified_domain_checks.py',
 'checks/curved_continuous_checks.py','checks/discovery_evidence_checks.py',
 'examples/output_only_example.py','examples/observable_probability_example.py',
 'examples/certified_probability_example.py','examples/replay_probability_certificate.py',
 'examples/continuous_moment_example.py','examples/replay_continuous_certificate.py',
 'examples/discover_quadratic_example.py','examples/replay_quadratic_certificate.py',
 'examples/robust_noisy_example.py','examples/robust_comparison_example.py',
 'examples/replay_robust_certificate.py','checks/robust_curved_checks.py',
 'examples/dependent_signal_generator.py','examples/dependent_data_certificate.py',
 'examples/replay_dependent_data_certificate.py','examples/reduced_repair_example.py',
 'examples/replay_reduced_repair.py','checks/data_supported_checks.py']

def run_script(script):
    start=time.perf_counter()
    try:
        r=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,text=True,capture_output=True,timeout=180)
        return {'script':script,'source_sha256':hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),
                'seconds':round(time.perf_counter()-start,6),'returncode':r.returncode,
                'stdout':r.stdout,'stderr':r.stderr,'passed':r.returncode==0}
    except subprocess.TimeoutExpired as e:
        return {'script':script,'seconds':round(time.perf_counter()-start,6),'returncode':None,
                'stdout':str(e.stdout or ''),'stderr':str(e.stderr or ''),'passed':False,'error':'180-second subprocess timeout'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify-hashes',action='store_true');p.add_argument('--batch-start',type=int,default=0)
    p.add_argument('--batch-count',type=int,default=len(SCRIPTS));p.add_argument('--session',default='default')
    a=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,48}',a.session) or a.batch_start<0 or a.batch_start>=len(SCRIPTS) or a.batch_count<1:
        p.error('Invalid session or batch range.')
    folder=ROOT/'verification/replay_checkpoints';folder.mkdir(exist_ok=True)
    path=folder/(a.session+'.json')
    if a.batch_start==0:
        report={'version':'0.8.0','session':a.session,'python':platform.python_version(),'platform':platform.platform(),
                'runs':[],'hash_check':None,'passed':False,'complete':False,'proof_kernel_run':False,'production_runtime_modified':False}
    else:
        if not path.exists():p.error('Continuation requires a checkpoint for this session.')
        report=json.loads(path.read_text())
        if len(report['runs'])!=a.batch_start or not all(x['passed'] for x in report['runs']):p.error('Batch must continue exactly after successful stored runs.')
    if a.verify_hashes:
        if a.batch_start!=0:p.error('Verify hashes before the first mutating batch only.')
        report['hash_check']=run_script('checks/verify_bundle.py')
        print(report['hash_check']['stdout'],end='',flush=True)
        if not report['hash_check']['passed']:raise SystemExit('Hash check failed.')
    def save():
        report['complete']=len(report['runs'])==len(SCRIPTS)
        report['passed']=report['complete'] and all(x['passed'] for x in report['runs'])
        txt=json.dumps(report,indent=2)+'\n';path.write_text(txt);(ROOT/'verification/reference_replay.json').write_text(txt)
    save()
    for script in SCRIPTS[a.batch_start:min(len(SCRIPTS),a.batch_start+a.batch_count)]:
        r=run_script(script);report['runs'].append(r);save()
        print(('PASS' if r['passed'] else 'FAIL')+': '+script,flush=True)
        if not r['passed']:
            print(r['stdout']);print(r['stderr'],file=sys.stderr);raise SystemExit(1)
    print(f"Completed {len(report['runs'])}/{len(SCRIPTS)} scripts; complete replay PASS = {report['passed']}.",flush=True)
if __name__=='__main__':main()
