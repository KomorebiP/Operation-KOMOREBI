#!/usr/bin/env python3
"""Bounded fail-closed negative proof suite; rejects setup/parser/resource failures."""
import argparse,json,re,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from release_common_v041 import ROOT,RD,sha,write_json,import_hashes,release_lock
NEG=RD/'negative_all'
SETUP=re.compile(r'object file .*does not exist|unknown module|failed to locate application|No such file or directory|failed to synthesize|unknown constant|unknown identifier|unknown tactic|unexpected token|invalid field notation|Expected type must not contain free variables|maximum recursion depth|maximum number of heartbeats|stack overflow|segmentation fault|uncaught exception|\bPANIC\b|internal exception|internal error|expected token|unexpected end of input|invalid syntax|parser error|invalid declaration|out of memory|illegal instruction',re.I)
def valid(source):
    jp=NEG/f'{source.stem}.json';lp=NEG/f'{source.stem}.log'
    if not jp.is_file() or not lp.is_file():return False
    try:
        record=json.loads(jp.read_text());text=lp.read_text(errors='replace');relative=source.relative_to(ROOT).as_posix()
        if record.get('source_sha256')!=sha(source) or record.get('returncode')!=1:return False
        if record.get('timed_out') or not record.get('source_unchanged') or not record.get('imports_unchanged'):return False
        if not record.get('warning_as_error') or record.get('log_sha256')!=sha(lp):return False
        if record.get('import_outputs')!=import_hashes(relative) or any(value is None for value in record.get('import_outputs',{}).values()):return False
        if SETUP.search(text):return False
        return bool(re.search(r'unsolved goals|Tactic `(?:decide|rfl|contradiction|assumption)`|omega could not prove|`simp` made no progress',text) or
          (source.name=='FalseAffineDimension.lean' and 'Application type mismatch' in text and 'Signature F 2 3' in text and 'Signature F 3 3' in text) or
          (source.name=='FalseStagedDeployBeforeReady.lean' and 'Type mismatch' in text and 'Action.deployWarm ∉' in text and 'Action.deployWarm ∈' in text) or
          (source.name=='FalseUnlimitedFreeRetry.lean' and 'Application type mismatch' in text and 'Except.error' in text and 'Except.ok initial' in text))
    except (KeyError,ValueError,OSError):return False

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=int,default=45)
    parser.add_argument('--workers',type=int,default=2);parser.add_argument('--per-file-seconds',type=int,default=90);args=parser.parse_args()
    if min(args.seconds,args.workers,args.per_file_seconds)<=0:parser.error('bounds must be positive')
    with release_lock('negative'):
        NEG.mkdir(parents=True,exist_ok=True);files=sorted((ROOT/'tests/negative').rglob('*.lean'))
        if not files or len({source.stem for source in files})!=len(files):raise RuntimeError('Empty suite or negative log basename collision')
        done={source for source in files if valid(source)};pending=[source for source in files if source not in done];active={};failed=[];started=time.monotonic()
        def run(source):
            log=NEG/f'{source.stem}.log'
            return subprocess.call([sys.executable,str(ROOT/'tools/lean_one_v041.py'),str(source.relative_to(ROOT)),'--no-output',
                                    '--seconds',str(args.per_file_seconds),'--log',str(log.relative_to(ROOT))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            while pending or active:
                while pending and len(active)<args.workers and time.monotonic()-started<args.seconds:
                    source=pending.pop(0);active[pool.submit(run,source)]=source;print('START',source.name,flush=True)
                if not active:break
                finished,_=wait(active,return_when=FIRST_COMPLETED)
                for future in finished:
                    source=active.pop(future);future.result()
                    if valid(source):done.add(source);print('PASS',source.name,flush=True)
                    else:failed.append(source);print('BAD',source.name,flush=True)
                if failed:break
        records=[]
        for source in files:
            jp=NEG/f'{source.stem}.json';record=json.loads(jp.read_text()) if jp.exists() else {'returncode':None,'timed_out':False}
            record.update(source=source.relative_to(ROOT).as_posix(),expected_rejection=valid(source),diagnostic_classifier='v041-fail-closed-proof-rejection-v1');records.append(record)
        count=sum(r['expected_rejection'] for r in records)
        summary=dict(total=len(files),substantive_rejections=count,complete=count==len(files),records=records)
        write_json(NEG/'summary.json',summary)
        print('CURRENT',count,'/',len(files),'REMAINING',len(files)-count,'FAILED',[source.name for source in failed],flush=True)
        return 1 if failed else 0
if __name__=='__main__':raise SystemExit(main())
