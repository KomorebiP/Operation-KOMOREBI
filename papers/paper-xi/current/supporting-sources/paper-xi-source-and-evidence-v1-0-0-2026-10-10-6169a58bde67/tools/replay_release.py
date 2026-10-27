#!/usr/bin/env python3
"""Run the24-method release suite and all five immutable B06 suites.

All output is external. Finite checks and publication tests do not establish
universal arithmetic results or constitute a Lean/Lake compiler run.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    root=Path(__file__).resolve().parents[1];out=a.output.resolve()
    if out.is_relative_to(root):raise SystemExit('Output must be outside the release tree.')
    out.mkdir(parents=True,exist_ok=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');records=[]
    jobs=[('release_publication',root/'tools/test_release.py',['--result',str(out/'release_tests.json')],out/'release_tests.json'),
          ('immutable_block06',root/'predecessor/block06/tools/replay_block06.py',['--output',str(out/'predecessor')],out/'predecessor/REPLAY_SUMMARY.json')]
    for name,script,args,target in jobs:
        target.unlink(missing_ok=True);start=time.monotonic();record={'gate':name,'source':str(script.relative_to(root)),'source_sha256':sha(script)}
        print('RUN',name,flush=True)
        try:
            run=subprocess.run([sys.executable,str(script),*args],env=env,cwd=out,capture_output=True,text=True,timeout=200)
            (out/f'{name}.stdout.log').write_text(run.stdout);(out/f'{name}.stderr.log').write_text(run.stderr)
            report=json.loads(target.read_text()) if target.exists() else {};ok=run.returncode==0 and report.get('status')=='passed'
            ok=ok and (report.get('methods')==24 if name=='release_publication' else report.get('suite_count')==5)
            record.update(status='passed' if ok else 'failed',returncode=run.returncode,result=report,result_sha256=sha(target) if target.exists() else None)
        except (OSError,ValueError,subprocess.TimeoutExpired) as e:record.update(status='failed',error=str(e))
        record['seconds']=round(time.monotonic()-start,3);records.append(record);print(record['status'],flush=True)
    report={'status':'passed' if all(r['status']=='passed' for r in records) else 'failed','checkpoint':'P11-PUB-B07','suite_count':6,
            'new_release_methods':24,'preserved_publication_methods':15,'preserved_finite_methods':[28,23,15,12],'records':records,'scope':__doc__}
    (out/'REPLAY_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','suite_count','new_release_methods','preserved_publication_methods','preserved_finite_methods']},indent=2));return int(report['status']!='passed')
if __name__=='__main__':raise SystemExit(main())
