"""Emit a kernel-checkable concrete all-word theorem for a bounded finite instance.
The exporter is not trusted: generated local laws are proved by Lean's `decide`.
The caller's source JSON must still represent the intended problem.
"""
from pathlib import Path
from itertools import product
from collections import deque
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from checks.check_certificate import check,canonical
from hashlib import sha256

def dot(a,x,m):return sum(v*w for v,w in zip(a,x))%m
def step(a,x,m):return tuple(dot(row,x,m) for row in a)
def render(x):
    if isinstance(x,list):return '['+', '.join(render(y) for y in x)+']'
    return str(x)

def export(spec,cert,path):
    check(spec,cert)
    m=spec['p']**spec['r'];n=m**spec['dimension'];k=len(spec['actions']);o=len(spec['observations'])
    if n>256:raise ValueError('finite Lean-table exporter cap: 256 source states; unresolved, not failure of mathematical representation')
    states=list(product(range(m),repeat=spec['dimension']));si={v:i for i,v in enumerate(states)}
    encoded=[step(cert['basis'],x,m) for x in states];targets=sorted(set(encoded));ti={v:i for i,v in enumerate(targets)};t=len(targets)
    if t>32:raise ValueError('pair-witness exporter cap: 32 target states')
    source_actions=[[si[step(a,x,m)] for x in states] for a in spec['actions']]
    source_out=[[dot(row,x,m) for x in states] for row in spec['observations']]
    target_actions=[[ti[step(a,x,m)] for x in targets] for a in cert['transitions']]
    target_out=[[dot(row,x,m) for x in targets] for row in cert['observation_decoder']]
    enc=[ti[y] for y in encoded];reps=[enc.index(i) for i in range(t)]
    words=[[[] for _ in range(t)] for _ in range(t)];obs=[[0]*t for _ in range(t)]
    for x in range(t):
      for y in range(t):
        if x==y:continue
        todo=deque([(x,y,[])]);seen={(x,y)}
        while todo:
            a,b,w=todo.popleft()
            js=[j for j in range(o) if target_out[j][a]!=target_out[j][b]]
            if js:words[x][y]=w;obs[x][y]=js[0];break
            for digit,T in enumerate(target_actions):
                v=(T[a],T[b])
                if v not in seen:seen.add(v);todo.append((v[0],v[1],w+[digit]))
        else:raise ValueError('not a minimal output quotient')
    s=f'''import ConcreteExamples

/- Generated from source SHA256 {sha256(canonical(spec)).hexdigest()}.
   Exact finite tables from the explicit linear profile; all source states are admissible.
   No native_decide, no assumed all-word equivalence. -/
namespace Komorebi.Representation.Generated
open Komorebi.Representation Komorebi.Representation.Fixtures
set_option maxRecDepth 20000
set_option maxHeartbeats 8000000

def sourceActions : List (List Nat) := {render(source_actions)}
def sourceOutputs : List (List Nat) := {render(source_out)}
def targetActions : List (List Nat) := {render(target_actions)}
def targetOutputs : List (List Nat) := {render(target_out)}
def encValues : List Nat := {render(enc)}
def repValues : List Nat := {render(reps)}
def witnessWords : List (List (List Nat)) := {render(words)}
def witnessObservations : List (List Nat) := {render(obs)}

def sourceSystem : System (Fin {n}) (Fin {k}) (Fin {o}) (Fin {m}) where
  step := fun a x => reduceFin {n} (by decide) ((sourceActions.getD a.val []).getD x.val 0)
  observe := fun j x => reduceFin {m} (by decide) ((sourceOutputs.getD j.val []).getD x.val 0)

def targetSystem : System (Fin {t}) (Fin {k}) (Fin {o}) (Fin {m}) where
  step := fun a x => reduceFin {t} (by decide) ((targetActions.getD a.val []).getD x.val 0)
  observe := fun j x => reduceFin {m} (by decide) ((targetOutputs.getD j.val []).getD x.val 0)

def encoder (x : Fin {n}) : Fin {t} := reduceFin {t} (by decide) (encValues.getD x.val 0)
def representative (x : Fin {t}) : Fin {n} := reduceFin {n} (by decide) (repValues.getD x.val 0)
def witnessWord (x y : Fin {t}) : List (Fin {k}) :=
  (((witnessWords.getD x.val []).getD y.val []).map (reduceFin {k} (by decide)))
def witnessObservation (x y : Fin {t}) : Fin {o} :=
  reduceFin {o} (by decide) ((witnessObservations.getD x.val []).getD y.val 0)

theorem local_check : checkLocal sourceSystem targetSystem encoder = true := by decide

def transport : Transport sourceSystem targetSystem :=
  checkedTransport sourceSystem targetSystem encoder local_check

theorem representative_check : ∀ y : Fin {t}, encoder (representative y) = y := by decide

theorem onto (y : Fin {t}) : ∃ x, encoder x = y := ⟨representative y,representative_check y⟩

theorem witness_check : ∀ x y : Fin {t}, x ≠ y →
    behavior targetSystem x (witnessWord x y) (witnessObservation x y) ≠
    behavior targetSystem y (witnessWord x y) (witnessObservation x y) := by decide

theorem separation (x y : Fin {t}) (h : x ≠ y) :
    ∃ w j, behavior targetSystem x w j ≠ behavior targetSystem y w j :=
  ⟨witnessWord x y,witnessObservation x y,witness_check x y h⟩

theorem all_words (x : Fin {n}) (w : List (Fin {k})) (j : Fin {o}) :
    behavior sourceSystem x w j = behavior targetSystem (encoder x) w j :=
  transport_behavior transport w j x

theorem exact_quotient (x y : Fin {n}) :
    ObsEq sourceSystem x y ↔ encoder x = encoder y :=
  separated_encoding_exact transport separation x y

theorem every_competitor_contains_target {{Z : Type}}
    (T : System Z (Fin {k}) (Fin {o}) (Fin {m})) (q : Fin {n} → Z)
    (hq : ∀ x w j, behavior sourceSystem x w j = behavior T (q x) w j) :
    ∃ f : Fin {t} → Z, ∀ x y, f x = f y → x = y :=
  ⟨semanticEmbedding transport onto q,
   minimal_word_encoding_injective transport onto separation q hq⟩

end Komorebi.Representation.Generated
'''
    path.write_text(s)
    return {'source_states':n,'target_states':t,'source_sha256':sha256(canonical(spec)).hexdigest(),
      'certificate_sha256':sha256(canonical(cert)).hexdigest(),'generated_file':path.name,
      'scope':'Exact all-state/all-word semantics for explicit complete finite tables. Cardinal state minimum via injection, not a general linear dimension formalization.'}

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('source');pa.add_argument('certificate');pa.add_argument('output');a=pa.parse_args()
    result=export(json.loads(Path(a.source).read_text()),json.loads(Path(a.certificate).read_text()),Path(a.output))
    print(json.dumps(result,indent=2))
