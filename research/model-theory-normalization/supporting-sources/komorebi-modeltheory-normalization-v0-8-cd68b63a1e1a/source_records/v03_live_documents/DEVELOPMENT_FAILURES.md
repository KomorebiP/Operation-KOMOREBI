# Development failures and recovery — M3

Failures below are not counted as mathematical successes. Final accepted evidence
is in results/LEAN_AUDIT_ALL.json, results/LOGICAL_DISCOVERY_AUDIT.json and the
version-two manifests.

## Environment

1. An initial compression inspection tried to import the unavailable zstandard
   Python module. The actual concatenated runtime archive was then identified by
   its magic bytes as XZ, not Zstandard. The installed xz command and lzma reader
   were used instead. This was an environment/format assumption error.
2. The first full five-part XZ runtime extraction exceeded the enclosing
   120-second command limit. The potentially incomplete most recent output was
   removed and a skip-existing extraction replay completed with exit code zero.
   Its completion record, removal list, script and log are retained under
   evidence/runtime_restore. The final environment check verifies the actual
   Lean binary hash, pinned version, Mathlib revision and selected upstream source
   hashes. No extraction timeout is counted as a proof check.

## Lean drafts

Three development module invocations failed before correction:

* MatrixObservationCode_01: unused automatically included semiring parameters,
  an insufficiently unfolded sourceSystem in simplification, and a brittle
  rewrite of the transport equation. Fixed by separating structural list lemmas
  from algebraic variables and using the existing exact behavioral bridge.
* MatrixObservationCode_02: the local code certificate is a proposition, so
  warnings-as-errors rejected declaring it with `def`. It is now a theorem
  constructing the two required fields.
* MatrixLogicalBridge_01: a deprecated set-membership simplification lemma caused
  a strict warning. Replaced with the supported lemma.

Exact diagnostics, source snapshots and per-attempt JSON records are retained in
evidence/development. Final accepted modules all compile with warnings as errors.
No `sorry`, axiom, native_decide or assumed correctness flag was used as a repair.

## Python fixture

The first independent finite-model audit omitted the required explicit `size`
argument when constructing its source/image FiniteSystem values. The constructor
raised TypeError before that audit finished. The fixture now supplies the actual
source and image sizes; the clean rerun passed all 66,428 checks. The first
traceback is retained as evidence/development/python_first.log. This was a fixture
bug, not a mathematical counterexample.

## Accepted run

The final 222-module cold Lean run and full 202-case Python audit completed with
all required outcomes. Both evidence manifests validate without a metadata repair.
The deliberately false, placeholder and invalid-certificate controls are expected
rejections, not unrecorded failures of the accepted proof.
