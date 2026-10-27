#!/usr/bin/env python3
"""Run actual Lean compiler/audit controls. A timeout never counts as a rejection."""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,time

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--kit',type=Path,required=True);a=ap.parse_args()
    r=Path(__file__).resolve().parents[1];src=r/'formal/controls';obj=r/'build/control_objects';src.mkdir(exist_ok=True)
    template=(r/'formal/audit/OwnedAudit.lean').read_text()
    cases=[
      ('GoodForeign','import Lean\nnamespace OutsideKomorebi\ndef data : Nat := 7\nprivate theorem internal_valid : (7 : Nat) = 7 := rfl\ntheorem exported_valid : (7 : Nat) = 7 := internal_valid\nend OutsideKomorebi\n',True,None),
      ('BadAxiom','import Lean\nnamespace OutsideKomorebi\naxiom untrusted : True\ntheorem consumer : True := untrusted\nend OutsideKomorebi\n',False,'OWNED AUDIT REJECTED'),
      ('BadOpaque','import Lean\nnamespace OutsideKomorebi\nopaque hidden : Nat := 7\nend OutsideKomorebi\n',False,'OWNED AUDIT REJECTED opaque'),
      ('BadUnsafe','import Lean\nnamespace OutsideKomorebi\nunsafe def code : Nat := 7\nend OutsideKomorebi\n',False,'OWNED AUDIT REJECTED unsafe'),
      ('BadPartial','import Lean\nnamespace OutsideKomorebi\npartial def forever (n : Nat) : Nat := forever (n+1)\nend OutsideKomorebi\n',False,'OWNED AUDIT REJECTED unreviewed partial')]
    records=[];started=time.monotonic()
    def run(module:str,expect:bool,reason:str|None=None):
      cmd=[sys.executable,str(r/'tools/run_lean.py'),module,'--kit',str(a.kit),'--source-root',str(src),'--objects',str(obj),'--tag','controls','--timeout','120']
      out=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
      # The runner prints one short receipt line before diagnostics.
      first=out.stdout.splitlines()[0];short=json.loads(first);p=Path(short['receipt']);d=json.loads(p.read_text());log=(p.parent/'compile.log').read_text()
      ok=(d['status']=='PASS') if expect else (d['status']=='FAIL' and d['exit_code']!=0 and reason in log)
      row={'module':module,'expected':'PASS' if expect else 'REJECTION','accepted':ok,'receipt':str(p.relative_to(r)),'actual_status':d['status'],'expected_diagnostic':reason,'source_sha256':d['source_sha256']}
      records.append(row);print(json.dumps(row),flush=True)
      return ok
    for name,text,good,reason in cases:
      (src/(name+'.lean')).write_text(text)
      if not run(name,True):continue
      aud=template.replace('import PaperIIIContinuation','import '+name)
      aud=re.sub(r'let ownedModules : Array Name := #\[.*?\]',f'let ownedModules : Array Name := #[`{name}]',aud,count=1)
      module='Audit'+name;(src/(module+'.lean')).write_text(aud)
      run(module,good,reason)
    for name,text,reason in [
      ('FalseArithmetic','import Lean\ntheorem falseArithmetic : (0 : Nat) = 1 := by decide\n','Tactic `decide` proved that the proposition'),
      ('AdmittedProof','import Lean\ntheorem admittedProof : (0 : Nat) = 1 := by sorry\n','declaration uses `sorry`')]:
      (src/(name+'.lean')).write_text(text);run(name,False,reason)
    result={'schema':'paper-iii.compiler-controls/1','status':'PASS' if len(records)==12 and all(x['accepted'] for x in records) else 'FAIL','controls':records,'auditor_template_sha256':sha(r/'formal/audit/OwnedAudit.lean'),'template_variation':'Only import and ownedModules binding differ; all policy checks are identical.','elapsed_seconds':time.monotonic()-started}
    (r/'verification/COMPILER_CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n')
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
