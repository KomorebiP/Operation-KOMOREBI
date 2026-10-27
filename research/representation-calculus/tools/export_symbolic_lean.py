"""Export matrix certificates to Lean without enumerating source or target states.

The parser and exporter are untrusted: the emitted finite matrix equations,
provenance trace, and generic bridge are checked by Lean's kernel.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from checks.check_certificate import check

def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def _matrix(rows: list, modulus: int) -> str:
    return f'fun i j => Fin.ofNat {modulus} ((({rows} : List (List Nat)).getD i.val []).getD j.val 0)'

def _vector(row: list, modulus: int) -> str:
    return f'fun i => Fin.ofNat {modulus} (({row} : List Nat).getD i.val 0)'

def _cases(proofs: list[str], depth: int = 0) -> str:
    if not proofs:
        return f'fun i{depth} => Fin.elim0 i{depth}'
    return f'fun i{depth} => Fin.cases ({proofs[0]}) ({_cases(proofs[1:], depth+1)}) i{depth}'

def emit(spec: dict, cert: dict, namespace: str, *, verify: bool = True) -> str:
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', namespace):
        raise ValueError('invalid Lean namespace')
    if verify:
        check(spec, cert)
    d, t, k, o, ell = spec['dimension'], cert['dimension'], len(spec['actions']), len(spec['observations']), len(cert['raw_tests'])
    m = spec['p'] ** spec['r']
    if d > 32 or ell > 256 or k > 16 or o > 32:
        raise ValueError('export resource cap: unresolved, not a nonexistence claim')
    # Expand word suffixes once. This accepts certificates whose witnesses are not
    # ordered by discovery and avoids exponential kernel recomputation of words.
    trace: list[tuple[int, tuple[int,...]]] = []
    lookup: dict[tuple[int,tuple[int,...]], int] = {}
    rows: list[list[int]] = []
    def visit(j: int, word: tuple[int,...]) -> int:
        key = (j, word)
        if key in lookup:
            return lookup[key]
        if word:
            q = visit(j, word[1:]); parent = rows[q]; a = spec['actions'][word[0]]
            row = [sum(parent[b]*a[b][col] for b in range(d)) % m for col in range(d)]
        else:
            row = spec['observations'][j][:]
        if len(trace) >= 512:
            raise ValueError('row trace cap: unresolved')
        ix=len(trace);lookup[key]=ix;trace.append(key);rows.append(row)
        return ix
    selected = [visit(tst['observation'], tuple(tst['word'])) for tst in cert['raw_tests']]
    source_hash=sha256(canonical(spec)).hexdigest(); cert_hash=sha256(canonical(cert)).hexdigest()
    out=[
        'import MatrixRowWitnesses', 'import MatrixSmith', '',
        '/- Automatically generated untrusted source. Every accepted identity is kernel checked.',
        f'   Canonical input JSON SHA256: {source_hash}',
        f'   Canonical certificate JSON SHA256: {cert_hash}',
        '   Source states are finite vectors, never an enumerated state table. -/',
        'set_option maxRecDepth 100000', 'set_option maxHeartbeats 8000000',
        f'namespace Komorebi.Representation.Symbolic.{namespace}',
        'open Komorebi.Representation', 'open Komorebi.Representation.Matrix',
        f'abbrev R := Fin {m}',
        f'def actions : Fin {k} → Mat R {d} {d} :=',
        f'  fun a i j => Fin.ofNat {m} (((({spec["actions"]} : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)',
        f'def observations : Mat R {o} {d} := {_matrix(spec["observations"],m)}',
        f'def source := linearSystem actions observations',
    ]
    for n,((j,word),row) in enumerate(zip(trace,rows)):
        out.append(f'def row{n} : Vec R {d} := {_vector(row,m)}')
        if word:
            q=lookup[(j,word[1:])];a=word[0]
            out += [f'theorem row{n}_local : ∀ i, row{n} i = rm row{q} (actions {a}) i := by decide',
              f'theorem row{n}_sound (x : Vec R {d}) : dot row{n} x = behavior source x {list(word)} {j} :=',
              f'  observed_row_prepend actions observations {a} {list(word[1:])} {j} row{q} row{n} row{q}_sound row{n}_local x']
        else:
            out += [f'theorem row{n}_local : ∀ i, row{n} i = observations {j} i := by decide',
              f'theorem row{n}_sound (x : Vec R {d}) : dot row{n} x = behavior source x [] {j} :=',
              f'  observed_row_base actions observations {j} row{n} row{n}_local x']
    tests='['+', '.join(f'({test["word"]}, {test["observation"]})' for test in cert['raw_tests'])+']'
    testfn=f'fun i => ({tests} : List (List (Fin {k}) × Fin {o})).getD i.val ([], 0)' if ell else 'fun i => Fin.elim0 i'
    selected_rows=[rows[ix] for ix in selected]
    out += [f'def data : CertificateData R {d} {t} {k} {o} {ell} where',
       '  actions := actions', '  observations := observations',
       f'  encoding := {_matrix(cert["basis"],m)}',
       f'  transitions := fun a i j => Fin.ofNat {m} (((({cert["transitions"]} : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)',
       f'  decoder := {_matrix(cert["observation_decoder"],m)}',
       f'  tests := {testfn}',
       f'  combinations := {_matrix(cert["basis_combinations"],m)}',
       f'def witnessedRows : Mat R {ell} {d} := {_matrix(selected_rows,m)}',
       'theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=',
       f'  {_cases([f"row{ix}_sound" for ix in selected])}',
       'theorem local_equations :',
       '    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧',
       '    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧',
       '    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide',
       'theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2',
       f'theorem all_states_all_words (x : Vec R {d}) (w : List (Fin {k})) (j : Fin {o}) :',
       '    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=',
       '  matrix_all_words data valid x w j',
       f'theorem exact_behavior (x y : Vec R {d}) :',
       '    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=',
       '  matrix_behavior_exact data valid x y',
       f'def smith : SmithData R {d} {t} where',
       '  width := by decide',
       f'  weights := {_vector([spec["p"]**s for s in cert["smith_valuations"]],m)}',
       f'  change := {_matrix(cert["V"],m)}', f'  inverse := {_matrix(cert["V_inverse"],m)}',
       'theorem smith_checked : checkSmith data.encoding smith = true := by decide',
       f'theorem exact_image (y : Vec R {t}) :',
       '    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=',
       '  checked_smith_image data.encoding smith smith_checked y',
       f'theorem every_competitor_contains_image {{Z : Type}} (U : System Z (Fin {k}) (Fin {o}) R)',
       f'    (encode : Vec R {d} → Z)',
       '    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :',
       '    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=',
       '  image_minimal_semantic_encoding data valid U encode h',
       f'def growthDeltas : Mat R {ell} {d} := {_matrix([e['delta'] for e in cert['strict_growth_witnesses']],m)}',
       'theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide',
       f'theorem growth_really_distinguishes (i : Fin {ell}) :',
       '    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧',
       '    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=',
       '  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i',
       f'end Komorebi.Representation.Symbolic.{namespace}', ''
    ]
    return '\n'.join(out)

def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);ap.add_argument('certificate',type=Path)
    ap.add_argument('output',type=Path);ap.add_argument('--namespace',required=True)
    args=ap.parse_args();src=json.loads(args.source.read_text());cert=json.loads(args.certificate.read_text())
    text=emit(src,cert,args.namespace);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(json.dumps({'status':'EXPORTED_NOT_YET_COMPILED','path':str(args.output),'bytes':len(text.encode()),'source_state_enumeration':False}))
if __name__=='__main__':main()
