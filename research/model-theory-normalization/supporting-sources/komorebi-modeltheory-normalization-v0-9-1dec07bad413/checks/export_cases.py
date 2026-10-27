from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from costed_echelon import discover_costed

def vec(x):
 return '!['+', '.join(vec(t) if isinstance(t,list) else str(t) for t in x)+']'

def main():
 records=json.loads((ROOT/'source_records/EXPORTED_DATA.json').read_text())
 outcomes=[];batches={}
 for r in records:
  src=json.loads((ROOT/r['source']).read_text());answer,stats=discover_costed(src)
  assert answer==r['result']
  idx=r['index'];n=idx//12;prefix=f'c{idx:03}_'
  if n not in batches:
   batches[n]=f'''module
public import CostedBounds
@[expose] public section
namespace Komorebi.CostedRegression.Batch{n:02}
open Komorebi.Costed Komorebi.Discovery
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
'''
  p,pr,d=src['p'],src['r'],src['dimension'];k=len(src['actions']);o=len(src['observations'])
  result='['+', '.join('(['+', '.join(map(str,t['word']))+'], '+str(t['observation'])+')' for t in answer)+']'
  batches[n]+=f'''abbrev {prefix}R := ZMod ({p}^{pr})
def {prefix}A : Fin {k} → Mat {prefix}R {d} {d} := {vec(src['actions'])}
def {prefix}O : Mat {prefix}R {o} {d} := {vec(src['observations'])}
def {prefix}result : List (Test {k} {o}) := {result}
theorem {prefix}computed : discoverEval {p} {pr} {d} {prefix}A {prefix}O =
    (some {prefix}result, {stats['units']}) := by decide +kernel
theorem {prefix}all_words : FiniteCodeCertificate (linearSystem {prefix}A {prefix}O) {prefix}result :=
  discoverEval_code {p} {pr} {d} {prefix}A {prefix}O {prefix}result
    (congrArg Prod.fst {prefix}computed)
'''
  outcomes.append({'index':idx,'source':r['source'],'result':answer,**stats})
 for n,s in batches.items():
  (ROOT/f'formalization/CostedComputed{n:02}.lean').write_text(s+f'end Komorebi.CostedRegression.Batch{n:02}\n')
 (ROOT/'source_records/COSTED_CASES.json').write_text(json.dumps(outcomes,indent=2)+'\n')
 print('exported',len(outcomes),'cases across',len(batches),'modules')
if __name__=='__main__':main()
