"""Export a checked FIFO trace to literal Lean branch proofs; no state enumeration.
This exporter is not verified: the emitted proof is checked by Lean and the audit
recompares literal inputs with the separately supplied source.
"""
from __future__ import annotations
from collections import deque
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from new_checks.check_trace import check_trace


def vector(v):
    return '!['+', '.join(vector(x) if isinstance(x,list) else str(x) for x in v)+']' if v else 'Fin.elim0'
def test(t): return '('+'['+','.join(map(str,t['word']))+'], '+str(t['observation'])+')'
def tests(ts):return '['+', '.join(map(test,ts))+']'


def export(source:dict,trace:dict,namespace:str) -> str:
    check_trace(source,trace)
    p,r,d=source['p'],source['r'],source['dimension'];k=len(source['actions']);o=len(source['observations'])
    n=len(trace['events']);rows=[];pending=deque({'word':[],'observation':j} for j in range(o));lines=[
       'module','public import DiscoveryTrace','', '@[expose] public section',
       f'namespace Komorebi.Discovery.{namespace}',
       'open Komorebi.Discovery Komorebi.Representation Komorebi.Representation.Matrix',
       'open Komorebi.ModelTheory Komorebi.ModelTheory.Standard',
       'open scoped BigOperators','set_option maxRecDepth 100000','set_option maxHeartbeats 4000000',
       f'abbrev R := ZMod {p**r}',f'def A : Fin {k} → Mat R {d} {d} := '+vector(source['actions']),
       f'def O : Mat R {o} {d} := '+vector(source['observations']),
       f'def AA : Fin {k} → (Fin {d} → R) →ₗ[R] (Fin {d} → R) := fun a => rowRight (A a)',
       f'def result : List (Test {k} {o}) := '+tests(trace['result'])]
    for i,ev in enumerate(trace['events']):
        t=pending.popleft();assert t==ev['test']
        lines += [f'def accepted{i} : List (Test {k} {o}) := '+tests(rows),
                  f'def pending{i} : List (Test {k} {o}) := '+tests([t]+list(pending)),
                  f'def test{i} : Test {k} {o} := '+test(t)]
        if ev['decision']=='skip':
            c=vector(ev['coefficients'])
            lines += [f'theorem branch{i} : testValue AA O test{i} ∈ testSpan AA O accepted{i} := by',
                f'  apply span_member_from_coefficients AA O accepted{i} (testValue AA O test{i}) ({c})',
                '  decide +kernel']
        else:
            lines += [f'def delta{i} : Fin {d} → R := '+vector(ev['delta']),
                f'theorem branch{i} : testValue AA O test{i} ∉ testSpan AA O accepted{i} := by',
                f'  apply span_nonmember_from_indexed_functional AA O accepted{i}',
                f'    (testValue AA O test{i}) (rowEvaluate delta{i})',
                '  · decide +kernel','  · decide +kernel']
            rows.append(t)
            for a in range(k):pending.append({'word':[a]+t['word'],'observation':t['observation']})
    assert not pending
    lines += [f'theorem trace{n} : QueueTrace AA O result [] result := QueueTrace.done result']
    for i in reversed(range(n)):
        lines += [f'theorem trace{i} : QueueTrace AA O accepted{i} pending{i} result := by',
                  f'  exact QueueTrace.{trace["events"][i]["decision"]} branch{i} trace{i+1}']
    lines += [f'theorem complete_trace : QueueTrace AA O [] (roots {k} {o}) result := trace0',
      'theorem exact_observable_span : testSpan AA O result = observableSpan AA O :=',
      '  queueTrace_exact AA O complete_trace',
      f'theorem reference_algorithm_result : finitePrimeDiscover {p} {r} {d} AA O = some result :=',
      f'  prime_trace_matches_reference {p} {r} {d} (by decide +kernel) AA O result complete_trace',
      f'theorem exact_all_words (x y : Fin {d} → R) :',
      '    CodeEqual (linearSystem A O) result x y ↔ ObsEq (linearSystem A O) x y :=',
      '  certified_code_exact _ _ (queueTrace_code A O result complete_trace) x y',
      f'theorem standard_definition (e : Fin 2 → TaggedCarrier (Fin {d} → R) R) :',
      '    taggedRealize (linearSystem A O) (guardedCodeFormula result) e ↔',
      '      e ∈ taggedBehaviorSet (linearSystem A O) :=',
      '  queueTrace_standard_definition A O result complete_trace e',
      f'end Komorebi.Discovery.{namespace}','']
    return '\n'.join(lines)

if __name__=='__main__':
    s,t,ns,out=sys.argv[1:]
    Path(out).write_text(export(json.loads(Path(s).read_text()),json.loads(Path(t).read_text()),ns))
