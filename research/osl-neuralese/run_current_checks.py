#!/usr/bin/env python3
"""Reproduce bounded OSL and finite-interface checks without training models.

The original source tree is never regenerated in place. All subprocesses run
in temporary working copies. No learned evaluation bank is opened by this file.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,platform,shutil,signal,subprocess,sys,tempfile,time
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent
CANONICAL='OSL_Core_0.5_Semantic_Independence_v0.1.0'

def h(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def execute(name:str,command:list[str],cwd:Path,out:Path,timeout:int,env:dict[str,str])->dict[str,Any]:
    log=out/(name+'.log');start=time.monotonic();timed_out=False
    with log.open('w',encoding='utf-8') as stream:
        process=subprocess.Popen(command,cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT,
                                 start_new_session=(os.name=='posix'))
        try:code=process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True
            if os.name=='posix':os.killpg(process.pid,signal.SIGKILL)
            else:
                if shutil.which('taskkill'):subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
                process.kill()
            process.wait();code=None
    return {'name':name,'returncode':code,'timeout':timed_out,'completed':code==0 and not timed_out,
            'seconds':round(time.monotonic()-start,3),'command':command,'log':log.name,'log_sha256':h(log)}

def run(out:Path,timeout:int)->dict[str,Any]:
    out=out.resolve()
    if out==ROOT or ROOT in out.parents:raise ValueError('Output must be outside the sealed release directory')
    out.mkdir(parents=True,exist_ok=False)
    records=[]
    with tempfile.TemporaryDirectory(prefix='osl-neuralese-check-') as temp:
        work=Path(temp);core=work/'OSL'/CANONICAL;bridge=work/'OSL'/'discovery_bridge'
        shutil.copytree(ROOT/'OSL/core05',core,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        shutil.copytree(ROOT/'OSL/discovery_bridge',bridge,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        # The finite demo has an explicit core05 import location; copy instead of a symlink for Windows portability.
        shutil.copytree(ROOT/'OSL/core05',work/'OSL/core05',ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        shutil.copytree(ROOT/'interface',work/'interface',ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=str(core/'reference')
        tasks=[
            ('core05_integrity',[sys.executable,'-B','reference/verify_core05_package.py'],core),
            ('core05_unit',[sys.executable,'-B','-m','pytest','-q','-p','no:cacheprovider','tests'],core),
            ('core05_corpus',[sys.executable,'-B','reference/generate_core05_evidence.py','--output',str(out/'corpus')],core),
            ('core05_bridge',[sys.executable,'-B','reference/generate_core05_evidence.py','--examples',str(core/'bridge_examples'),'--output',str(out/'bridge')],core),
            ('discovery_bridge',[sys.executable,'-B','verify_release.py','--osl-core',str(core/'reference')],bridge),
            ('finite_interface',[sys.executable,'-B','-m','unittest','discover','-s','tests','-v'],work/'interface'),
            ('actual_osl_demo',[sys.executable,'-B','run_demo.py','--output',str(out/'demo')],work/'interface'),
        ]
        for name,command,cwd in tasks:
            print('Checking '+name+' ...',flush=True)
            records.append(execute(name,command,cwd,out,timeout,env))
        comparison=[]
        for name in ['CORE05_CONFORMANCE_REPORT.json','CORE05_SEMANTIC_REPORT.json','CORE05_TRACE_BUNDLE.jsonl']:
            original=ROOT/'OSL/core05'/name;fresh=out/'corpus'/name
            comparison.append({'file':name,'original_sha256':h(original),
                'fresh_sha256':h(fresh) if fresh.is_file() else None,
                'byte_identical':fresh.is_file() and original.read_bytes()==fresh.read_bytes()})
    report={'schema':'komorebi.osl-neuralese.current-checks.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python':sys.version,'platform':platform.platform(),'checks':records,'corpus_comparison':comparison,
        'all_checks_pass':all(x['completed'] for x in records) and all(x['byte_identical'] for x in comparison),
        'scope':'OSL finite language, bounded Discovery Bridge, exact finite checkpoint and actual admission paths; no neural training or learned evaluation',
        'neural_scientific_replication':False,'unspent_banks_consumed':False}
    (out/'CURRENT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='New directory outside this release; must not already exist')
    parser.add_argument('--timeout',type=int,default=300,help='Per-command seconds (default300)')
    args=parser.parse_args()
    if args.timeout<=0:parser.error('--timeout must be positive')
    out=args.output or Path(tempfile.gettempdir())/('osl-neuralese-results-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
    try:result=run(out,args.timeout)
    except (OSError,ValueError) as exc:print('CHECK_RUN_FAILED: '+str(exc),file=sys.stderr);return 2
    print(json.dumps({'all_checks_pass':result['all_checks_pass'],'report':str(out.resolve()/'CURRENT_CHECKS.json')},indent=2))
    return 0 if result['all_checks_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
