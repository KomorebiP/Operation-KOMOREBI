"""Export checked matrix certificates as original-language observation formulas.

No state enumeration is used. Python and JSON parsing are not formally verified;
the exported Lean file must compile before any Lean result is claimed.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Any
from checks.check_certificate import check
from standard_logic import guarded_code, observed_term, conj, translate
from tools.export_symbolic_lean import emit as emit_matrix

SCHEMA = 'komorebi-matrix-logical-code-v0.3'

def canonical(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def digest(x: Any) -> str:
    return sha256(canonical(x)).hexdigest()

def compile_artifact(spec: dict, cert: dict) -> dict:
    check(spec, cert)
    tests = [(tuple(t['word']), t['observation']) for t in cert['raw_tests']]
    return {
        'schema': SCHEMA,
        'source_sha256': digest(spec),
        'certificate_sha256': digest(cert),
        'profile': {'modulus': spec['p'] ** spec['r'], 'initial_interface': 'all_states',
                    'word_order': 'left_to_right', 'quantifier_domain': 'encoded_image',
                    'language': 'state_guard + original_actions + original_observations + named_values'},
        'tests': cert['raw_tests'],
        'terms': [observed_term((0, w), j, (('free', 0),)) for w, j in tests],
        'formula': guarded_code(tests),
        'test_count': len(tests),
        'term_horizon': max((len(w) for w, _ in tests), default=0),
        'quantifier_rank': 0,
        'coordinate_count': cert['dimension'],
        'non_claims': ['No minimal-formula or minimal-test-list theorem.',
                       'Not unrestricted first-order elementarity or quantifier elimination.',
                       'Export is untrusted until Lean compilation.'],
    }

def _value(spec: dict, state: list[int], word: list[int], obs: int, target: dict | None = None) -> int:
    m = spec['p'] ** spec['r']
    actions = spec['actions'] if target is None else target['transitions']
    observations = spec['observations'] if target is None else target['observation_decoder']
    v = list(state)
    for a in word:
        v = [sum(c*x for c,x in zip(row,v)) % m for row in actions[a]]
    return sum(c*x for c,x in zip(observations[obs],v)) % m

def class_formula(spec: dict, cert: dict, encoded: list[int]) -> tuple:
    """A class query; exactness/nonemptiness requires that encoded lies in image(P)."""
    check(spec, cert)
    m = spec['p'] ** spec['r']
    if not isinstance(encoded, list) or len(encoded) != cert['dimension'] or any(type(x) is not int or not 0 <= x < m for x in encoded):
        raise ValueError('invalid encoded vector')
    if any(v % (spec['p'] ** s) for v,s in zip(encoded, cert['smith_valuations'])):
        raise ValueError('encoded vector is outside the certified image')
    formula = ('true',)
    for test in reversed(cert['raw_tests']):
        w, j = test['word'], test['observation']
        atom = ('test', (0, tuple(w)), j, _value(spec, encoded, w, j, cert))
        formula = ('and', atom, formula)
    return conj(('state', ('free', 0)), translate(formula, 1))

def emit_lean(spec: dict, cert: dict, namespace: str) -> str:
    # The old exporter validates the expected source and all matrix/Smith witnesses.
    base = emit_matrix(spec, cert, namespace)
    end = f'end Komorebi.Representation.Symbolic.{namespace}\n'
    if not base.endswith(end):
        raise RuntimeError('unexpected inherited exporter format')
    base = base[:-len(end)]
    base = base.replace('import MatrixRowWitnesses\nimport MatrixSmith\n',
        'module\npublic import MatrixRowWitnesses\npublic import MatrixSmith\npublic import MatrixLogicalWitnesses\n\n@[expose] public section\n',1)
    k,o,d = len(spec['actions']),len(spec['observations']),spec['dimension']
    tests = '[' + ', '.join(f'({test["word"]}, {test["observation"]})' for test in cert['raw_tests']) + ']'
    addon = f'''
open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin {k}) (Fin {o})) := {tests}
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin {k}) (Fin {o}) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R {d}) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R {d}, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R {d}) R)).Definable
      (observationLanguage (Fin {k}) (Fin {o}) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {{n : Nat}}
    (f : ObsFO (Fin {k}) (Fin {o}) R n) (env : Fin n → Vec R {d}) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R {d}) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R {d}) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin {len(cert['raw_tests'])}) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i
'''
    return base + addon + '\n' + end
