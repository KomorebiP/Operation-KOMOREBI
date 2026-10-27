#!/usr/bin/env python3
"""Run bounded exact checks in temporary copies, preserving inherited sources.
No Lean compiler is invoked. Requires pytest, numpy, sympy, matplotlib.
"""
from pathlib import Path
import sys,subprocess,json,shutil,tempfile,time,argparse,os
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'verification/2026-10-10/replay');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);results=[]
    with tempfile.TemporaryDirectory(prefix='paperx-exact-') as tmp:
        tmp=Path(tmp)
        for name,source in [('visual',ROOT/'visual_appendix'),('original',ROOT/'inherited_baseline/original_companion'),('residue',ROOT/'inherited_baseline/original_releases/residue_counting')]:
            shutil.copytree(source,tmp/name)
        jobs=[
          ('preservation',[sys.executable,'formal_preservation/restore.py','--verify'],ROOT),
          ('source_integrity',[sys.executable,'verification/source_integrity.py'],ROOT),
          ('reader_regressions',[sys.executable,'verification/tests/test_reader_regressions.py'],ROOT),
          ('visual_exact',[sys.executable,'checks/verify_examples.py'],tmp/'visual'),
          ('original_pytest',[sys.executable,'-m','pytest','-q'],tmp/'original'),
          ('original_worked_models',[sys.executable,'run_all.py'],tmp/'original'),
          ('residue_saved_hashes',[sys.executable,'checks/replay_residues.py','--verify-only'],tmp/'residue')]
        for name,cmd,cwd in jobs:
            t=time.monotonic()
            try:
                p=subprocess.run(cmd,cwd=cwd,env={**os.environ,'MPLBACKEND':'Agg','PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=100)
                out=p.stdout.decode(errors='replace');code=p.returncode
            except (OSError,subprocess.TimeoutExpired) as e:out=repr(e);code=-1
            (args.output/(name+'.log')).write_text(out)
            row={'gate':name,'returncode':code,'status':'passed' if code==0 else 'failed','seconds':round(time.monotonic()-t,2),'command':cmd,'log':name+'.log'}
            results.append(row);print(json.dumps(row),flush=True);print(out[-450:],flush=True)
            (args.output/'RESULTS.json').write_text(json.dumps({'gates':results,'expected_gates':len(jobs),'complete':len(results)==len(jobs),'all_passed':len(results)==len(jobs) and all(x['returncode']==0 for x in results),'compiler_invoked':False,'plot_backend':'Agg'},indent=2))
        for source,target in [(tmp/'visual/checks/EXACT_CHECKS.json','visual_exact_results.json'),(tmp/'original/results/residual_seed_results.json','original_models.json')]:
            if source.exists():shutil.copy2(source,args.output/target)
    return 0 if all(x['returncode']==0 for x in results) else 1
if __name__=='__main__':sys.exit(main())
