"""Emit source/evidence DATA and one kernel-reduced replay check, not hand-built
per-branch proof terms. The exported source is untrusted until Lean accepts it.
"""
from pathlib import Path
import sys,json,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from new_checks.check_trace import check_trace
from new_checks.export_queue_lean import vector,tests

def export(source, trace, name):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',name):raise ValueError('Lean namespace')
    check_trace(source,trace)
    p,r,d=source['p'],source['r'],source['dimension']
    k,o=len(source['actions']),len(source['observations'])
    es=[]
    for e in trace['events']:
        if e['decision']=='skip':
            es.append('.combination ['+', '.join(map(str,e['coefficients']))+']')
        else:es.append('.separation ('+vector(e['delta'])+')')
    return '\n'.join([
      'module','public import CertifiedOracle','', '@[expose] public section',
      'namespace Komorebi.Discovery.CheckedData.'+name,
      'open Komorebi.Discovery Komorebi.Discovery.Certified',
      'open Komorebi.Representation Komorebi.Representation.Matrix',
      'open Komorebi.ModelTheory Komorebi.ModelTheory.Standard',
      'set_option maxRecDepth 100000','set_option maxHeartbeats 12000000',
      f'abbrev R := ZMod {p**r}',
      f'def A : Fin {k} → Mat R {d} {d} := '+vector(source['actions']),
      f'def O : Mat R {o} {d} := '+vector(source['observations']),
      f'def evidence : List (Evidence R {d}) := [\n  '+',\n  '.join(es)+']',
      f'def result : List (Test {k} {o}) := '+tests(trace['result']),
      'theorem checked_data : replaySource A O evidence = some result := by decide +kernel',
      'theorem reference_result :',
      f'    finitePrimeDiscover {p} {r} {d} (fun a => rowRight (A a)) O = some result :=',
      f'  replaySource_reference {p} {r} {d} (by decide +kernel) A O evidence result checked_data',
      f'theorem all_words (x y : Fin {d} → R) :',
      '    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=',
      '  replaySource_all_words A O evidence result checked_data x y',
      f'theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin {d} → R) R) :',
      '    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔',
      '      e ∈ taggedBehaviorSet (linearSystem A O) :=',
      '  replaySource_standard_formula A O evidence result checked_data e',
      'end Komorebi.Discovery.CheckedData.'+name,''])

if __name__=='__main__':
    s,t,n,out=sys.argv[1:]
    Path(out).write_text(export(json.loads(Path(s).read_text()),json.loads(Path(t).read_text()),n))
