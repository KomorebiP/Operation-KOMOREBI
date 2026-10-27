"""Test-only process kill hooks. Not exposed by the deployment configuration."""
import argparse,json,os,signal,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import run_retry_workflow as app

class CrashRun(app.RetryRun):
    def hook(self,name,action):
        if name==args.point and action['kind']==args.stage:
            os.kill(os.getpid(),signal.SIGKILL)

p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('config',type=Path);p.add_argument('run',type=Path)
p.add_argument('point');p.add_argument('stage');p.add_argument('--credit',type=int,default=5)
p.add_argument('--cap',type=int,default=8);p.add_argument('--key',default='retry-1');p.add_argument('--expected',type=int,default=1)
args=p.parse_args()
if args.mode=='start':args.run.mkdir()
with app.exclusive_run(args.run):
    r=CrashRun.create(args.config,args.run,attempt_budget=args.credit,max_attempts=args.cap) if args.mode=='start' else CrashRun(args.run)
    try:
        def ch(point):
            op=r.db.operations()[-1]
            if point==args.point and op['action']['kind']==args.stage:os.kill(os.getpid(),signal.SIGKILL)
        r.db.commit_hook=ch
        out=r.run() if args.mode=='start' else r.resolve('retry',args.key,args.expected,continue_run=False)
        print(json.dumps(out))
    finally:r.close()
