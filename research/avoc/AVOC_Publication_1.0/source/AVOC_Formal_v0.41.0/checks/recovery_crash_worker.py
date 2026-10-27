#!/usr/bin/env python3
"""Test-only process crash injection. Not installed as a deployment action."""
from pathlib import Path
import argparse,os,signal,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import run_recoverable_workflow as live

p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('run_dir',type=Path)
p.add_argument('point');p.add_argument('stage');a=p.parse_args()

class CrashRun(live.RecoverableRun):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if a.point in ('after_store_write','after_result_write'):
            def crash_transaction(point):
                op=self.db.operations()[-1]
                if point==a.point and op['action']['kind']==a.stage:
                    os.kill(os.getpid(),signal.SIGKILL)
            self.db.commit_hook=crash_transaction

    def hook(self,point,action):
        if point==a.point and action['kind']==a.stage:
            os.kill(os.getpid(),signal.SIGKILL)

a.run_dir.mkdir(parents=True,exist_ok=False)
with live.exclusive_run(a.run_dir):
    run=CrashRun.create(a.config,a.run_dir)
    try:result=run.run()
    finally:run.close()
print(json.dumps(result))
raise SystemExit(3)  # A configured crash that did not occur is a failed test.
