#!/usr/bin/env python3
"""Deliberately false proofs must be rejected. A timeout does not count as rejection."""
from pathlib import Path
import argparse,datetime as dt,hashlib,json,os,signal,subprocess,time

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',type=Path,required=True)
    a=ap.parse_args();root=Path(__file__).resolve().parents[1];rt=a.runtime.resolve();ws=rt/'workspace'
    cases={
      'FalseEquality':'example : (1 : Nat) = 0 := by rfl\n',
      'Placeholder':'example : False := by sorry\n',
      'ForgedCertificate':'''import Komorebi.GeneratedExactRotated
open Komorebi.ExactPosterior
open Komorebi.ExactPosterior.GeneratedExactRotated
example : checkCandidate model outputs inputs candidate2 = true := by
  rw [candidate2_checked]
  decide +kernel
'''}
    results=[]
    for name,text in cases.items():
        file=ws/f'Negative{name}.lean';file.write_text(text)
        argv=['bash',str(rt/'run.sh'),'lake','env','lean','-j1','-DwarningAsError=true',file.name]
        log=root/'results'/f'negative_{name}.log';t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(argv,cwd=ws,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:rc=p.wait(timeout=40)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();rc=124
        results.append(dict(name=name,argv=argv,source=text,source_sha256=hashlib.sha256(text.encode()).hexdigest(),
          exit_status=rc,elapsed_seconds=round(time.monotonic()-t,4),
          expected_rejection=rc not in (0,124),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        print(name,rc,flush=True)
        file.unlink(missing_ok=True)
    (root/'results/negative_controls.json').write_text(json.dumps(results,indent=2)+'\n')
    if not all(x['expected_rejection'] for x in results):raise SystemExit(1)
if __name__=='__main__':main()
