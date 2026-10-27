#!/usr/bin/env python3
"""Bounded locked dependency-aware rebuild; partial runs resume only current evidence."""
import argparse, json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path
from release_common_v040 import ROOT, RD, release_lock, build_graph, build_record_errors, write_json

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',type=int,default=45);parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--per-target-seconds',type=int,default=180);args=parser.parse_args()
    if min(args.seconds,args.workers,args.per_target_seconds)<=0: parser.error('bounds must be positive')
    with release_lock():
        order,deps=build_graph()
        if order!=json.loads((RD/'build_order.json').read_text()): raise RuntimeError('Build graph changed: run verify_v040.py --index')
        def ready(source):
            path=RD/f'clean_{Path(source).stem}.json'
            if not path.is_file():return False
            try:return not build_record_errors(source,json.loads(path.read_text()))
            except (KeyError,ValueError,OSError):return False
        if len({Path(source).stem for source in order})!=len(order): raise RuntimeError('Build log basename collision')
        done={source for source in order if ready(source)}
        while True:
            bad={source for source in done if not deps[source]<=done}
            if not bad:break
            done-=bad
        pending=set(order)-done;active={};failed=[];started=time.monotonic()
        def run(source):
            return subprocess.call([sys.executable,str(ROOT/'tools/lean_one_v040.py'),source,'--seconds',str(args.per_target_seconds),
                                    '--log',f'results/v0.40.0/clean_{Path(source).stem}.log'],stdout=subprocess.DEVNULL)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            while pending or active:
                if time.monotonic()-started<args.seconds:
                    for source in order:
                        if len(active)>=args.workers:break
                        if source in pending and deps[source]<=done:
                            pending.remove(source);active[pool.submit(run,source)]=source;print('START',source,flush=True)
                if not active:break
                finished,_=wait(active,return_when=FIRST_COMPLETED)
                for future in finished:
                    source=active.pop(future)
                    if future.result()==0 and ready(source):done.add(source);print('PASS',source,flush=True)
                    else:
                        failed.append(source);print('FAIL',source,(RD/f'clean_{Path(source).stem}.log').read_text(errors='replace')[-3000:],flush=True)
                if failed:break
        report=dict(status='failed' if failed else ('passed' if len(done)==len(order) else 'partial'),
                    complete=len(done)==len(order),total=len(order),passed=len(done),remaining=sorted(set(order)-done),failed=failed)
        write_json(RD/'build_progress.json',report)
        print('CURRENT',len(done),'/',len(order),'REMAINING',len(order)-len(done),'FAILED',failed,flush=True)
        return 1 if failed else 0
if __name__=='__main__':raise SystemExit(main())
