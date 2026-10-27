#!/usr/bin/env python3
"""Replay one publication suite and four bounded finite suites.

No Lean/Lake invocation, arithmetic matrix constructor, or classical theorem audit.
All outputs are written outside the checkpoint; source bytes are not modified.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path

def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();root=Path(__file__).resolve().parents[1];out=args.output.resolve()
    if out.is_relative_to(root):raise SystemExit('Output must be outside the immutable checkpoint.')
    out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    jobs=[('block06_publication',root/'tools/test_readers.py',['--result',str(out/'publication.json')]),
          ('four_inherited_finite_suites',root/'predecessor/block05/tools/replay_block05.py',['--output',str(out/'finite')])]
    records=[]
    for label,source,argv in jobs:
        target=out/('publication.json' if label=='block06_publication' else 'finite/REPLAY_SUMMARY.json')
        target.unlink(missing_ok=True);start=time.monotonic()
        row={'gate':label,'source':source.relative_to(root).as_posix(),'source_sha256':digest(source)}
        print('RUN',label,flush=True)
        try:
            result=subprocess.run([sys.executable,str(source),*argv],cwd=out,env=env,capture_output=True,text=True,timeout=180)
            (out/f'{label}.stdout.log').write_text(result.stdout)
            (out/f'{label}.stderr.log').write_text(result.stderr)
            data=json.loads(target.read_text()) if target.is_file() else {}
            ok=result.returncode==0 and data.get('status')=='passed'
            if label=='block06_publication':ok=ok and data.get('methods')==15
            else:ok=ok and len(data.get('gates',[]))==4 and all(x['status']=='passed' for x in data.get('gates',[]))
            row.update(status='passed' if ok else 'failed',returncode=result.returncode,
                       result_sha256=digest(target) if target.exists() else None,
                       result=data)
        except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
            row.update(status='failed',error=str(exc))
        row['seconds']=round(time.monotonic()-start,3);records.append(row);print(row['status'],flush=True)
    report={'status':'passed' if all(x['status']=='passed' for x in records) else 'failed','checkpoint':'P11-PUB-B06',
            'suite_count':5,'publication_test_methods':15,'inherited_finite_method_counts':[28,23,15,12],
            'records':records,'scope':__doc__}
    (out/'REPLAY_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','suite_count','publication_test_methods','inherited_finite_method_counts']},indent=2))
    return int(report['status']!='passed')
if __name__=='__main__':raise SystemExit(main())
