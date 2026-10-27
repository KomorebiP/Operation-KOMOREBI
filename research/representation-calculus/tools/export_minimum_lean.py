"""Emit an untrusted symbolic certificate AND its sharp prime-power linear-encoding theorem.
The generated source is not accepted until Lean compiles it against the pinned libraries.
"""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from export_symbolic_lean import emit

def emit_minimum(spec,certificate,namespace):
    text=emit(spec,certificate,namespace)  # invokes unchanged independent checker
    lines=text.splitlines(keepends=True)
    last=max(i for i,l in enumerate(lines) if l.startswith('import '))
    out=['module\n']
    for i,l in enumerate(lines):
        out.append('public '+l if l.startswith('import ') else l)
        if i==last:
            out.append('public import MatrixPrimeMinimality\n\n@[expose] public section\n')
    p,r,d=spec['p'],spec['r'],spec['dimension'];k=len(spec['actions']);o=len(spec['observations']);t=certificate['dimension']
    ns='Komorebi.Representation.Symbolic.'+namespace
    out.append(f'''\nset_option backward.isDefEq.respectTransparency false
open Fin.CommRing
namespace {ns}
open Komorebi.Representation Komorebi.Representation.Matrix

theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide

theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin {k}) (Fin {o}) R)
      (e : (Fin {d} → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      {t} ≤ budget :=
  fin_certificate_minimum_iff (m:={p**r}) (p:={p}) (r:={r}) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end {ns}
''')
    return ''.join(out)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('source',type=Path);ap.add_argument('certificate',type=Path)
    ap.add_argument('--namespace',required=True);ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args();s=json.loads(a.source.read_text());c=json.loads(a.certificate.read_text())
    text=emit_minimum(s,c,a.namespace)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    print(json.dumps({'status':'LEAN_SOURCE_WRITTEN_NOT_YET_COMPILED','output':str(a.output),'coordinates':c['dimension']}))
if __name__=='__main__':main()
