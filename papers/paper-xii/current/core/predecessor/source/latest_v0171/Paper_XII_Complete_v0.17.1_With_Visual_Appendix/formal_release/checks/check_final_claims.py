#!/usr/bin/env python3
"""Check final-claim consumers against the exact objects in a successful cumulative report.
Run the cumulative verifier first for a fresh full build. No network access is used.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'propext','Classical.choice','Quot.sound'}
TARGETS=['PaperXIIFinalConsumer.exact_completed_kernel',
         'PaperXIIFinalConsumer.claim31','PaperXIIFinalConsumer.claim33']
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
def now() -> str:
    return datetime.now(timezone.utc).isoformat()
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('kit',type=Path)
    ap.add_argument('--timeout',type=int,default=180)
    args=ap.parse_args();kit=args.kit.resolve();ws=kit/'workspace';lean=kit/'toolchain/bin/lean'
    result={'status':'RUNNING','started_utc':now(),'scope':'three supplementary contract theorems; not new manuscript claims'}
    report=ROOT/'final_claims_check.json'
    def save():report.write_text(json.dumps(result,indent=2)+'\n')
    try:
        cumulative=json.loads((ROOT/'verification.json').read_text())
        if cumulative.get('status')!='PASS':raise RuntimeError('Cumulative report is not PASS')
        if sha(lean)!=cumulative['compiler_sha256']:raise RuntimeError('Compiler hash mismatch')
        commit=subprocess.check_output(['git','-C',str(ws/'.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
        if commit!=cumulative['mathlib_commit']:raise RuntimeError('Mathlib pin mismatch')
        for rel,digest in cumulative['source_hashes_after'].items():
            if sha(ROOT/'lean'/rel)!=digest:raise RuntimeError('Production source mismatch: '+rel)
        for mod in cumulative['modules']:
            if sha(ROOT/mod['olean_path'])!=mod['olean_sha256']:raise RuntimeError('Production object mismatch: '+mod['module'])
        source=ROOT/'checks/FinalClaimsConsumer.lean'
        body=re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
        body=re.sub(r'--[^\n]*','',body)
        if re.search(r'\b(?:axiom|sorry|admit|unsafe|native_decide)\b',body):raise RuntimeError('Prohibited consumer token')
        obj=ROOT/'checks/FinalClaimsConsumer.olean';log=ROOT/'logs/FinalClaimsConsumer.log'
        env=os.environ.copy();env['MALLOC_ARENA_MAX']='2'
        env['LEAN_PATH']=os.pathsep.join(map(str,[ROOT/'build',ws/'.lake/build/lib/lean',
          *sorted((ws/'.lake/packages').glob('*/.lake/build/lib/lean'))]))
        cmd=[str(lean),'-j1','-DwarningAsError=true','-o',str(obj),str(source)]
        result.update(compiler_sha256=sha(lean),mathlib_commit=commit,cumulative_report_sha256=sha(ROOT/'verification.json'),
          production_sources_verified=len(cumulative['source_hashes_after']),production_objects_verified=len(cumulative['modules']),
          source_sha256=sha(source),argv=cmd)
        save();started=time.monotonic();proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT,text=True,start_new_session=True)
        timed=False
        try:output,_=proc.communicate(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed=True;os.killpg(proc.pid,signal.SIGKILL);output,_=proc.communicate()
        log.write_text(output);result.update(exit_code=proc.returncode,timed_out=timed,
          seconds=round(time.monotonic()-started,3),log=str(log.relative_to(ROOT)),log_sha256=sha(log))
        print(output,end='')
        if proc.returncode!=0 or timed:raise RuntimeError('Contract compilation failed')
        axioms=[]
        for name in TARGETS:
            match=re.search(re.escape("'"+name+"'")+r' depends on axioms:\s*\[([^\]]*)\]',output)
            if not match:raise RuntimeError('Missing axiom report: '+name)
            names={x.strip() for x in match[1].split(',') if x.strip()}
            if not names<=ALLOWED:raise RuntimeError('Unexpected axiom: '+name)
            axioms.append({'name':name,'axioms':sorted(names)})
        result.update(status='PASS',finished_utc=now(),axioms=axioms,object_sha256=sha(obj),theorem_count=len(TARGETS))
        save();print('FINAL CLAIM CONTRACT CHECK: PASS');return 0
    except Exception as exc:
        result.update(status='FAIL',failed_utc=now(),error=str(exc));save();print('FAIL:',exc);return 1
if __name__=='__main__':sys.exit(main())
