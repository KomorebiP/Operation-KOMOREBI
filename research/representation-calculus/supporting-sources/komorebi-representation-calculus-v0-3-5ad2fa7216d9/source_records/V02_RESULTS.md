# Retained verification results — Representation Calculus v0.2

## Scope

This is the representation-calculus branch. It is not p-adic Block 16 and does not
claim a new replay of the entire historical p-adic corpus. Formal universal
semantics, symbolic matrix certificates, finite experiments, and ordinary program
correctness have separate evidence boundaries.

## Lean: final accepted cold run

**PASS.** 5 modules, 48 theorem declarations,
49 definitions, 1 abbreviation,
2 structures: 100 explicit named declarations.
All 9 expected-outcome tasks passed. Every module compiled with warnings as
errors. All accepted input hashes were unchanged. The positive control accepted;
deliberately false and placeholder controls were rejected.

Only `Classical.choice`, `Quot.sound`, `propext` occurred in the declaration audit.
No additional project axioms, `sorryAx`, or `Lean.ofReduceBool` were present.
The recorded runtime is 30.408144 seconds; this is a single execution
measurement, not a performance comparison or guarantee.

Toolchain: `Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)`.
These modules import Lean/Std only, not Mathlib. The saved offline runtime restore
was interrupted before a full cache extraction. The recovered core toolchain and
Std were successfully used for the smoke test and all retained builds. See
`evidence/ENVIRONMENT_VERIFIED.json` and `DEVELOPMENT_FAILURES.md`.

The generic semantics include quotient construction, all-word transport soundness,
universal sufficiency, invariant cuts, stable-horizon exactness, and finite local
checker soundness. The automatically generated finite instance proves exactness
for all words and admits an injection of its eight target states into any
competing all-word encoder's state space. The source has 256 possible states.

This does NOT formally verify the Python discoverer, Smith routine or exporter.
The universal matrix-certificate-to-Lean adapter and its numerical free-linear
minimum application remain written proofs plus certificates. The finite-table
export is not a substitute for that adapter.

## Exact Python discovery audit

**PASS.** 202 explicit complete finite linear profiles, seed
`2026092002`. The recorded audit runtime is 0.372514 seconds.
No floating arithmetic is used in load-bearing matrix/Smith calculations.

| Check | Count |
|---|---:|
| `independent_symbolic_certificate` | 202 |
| `sample_state_word_observation` | 3,504 |
| `exhaustive_same_partition` | 3,908 |
| `exhaustive_quotient_cardinality` | 62 |
| `witness_actual_word_distinguishes` | 643 |
| `fixture_invertible_scramble` | 19 |
| `hidden_two_coordinates` | 18 |
| `hidden_torsion_length` | 18 |
| `big_two_coordinates` | 1 |
| `big_thirty_digits` | 1 |
| `delay_seven_steps` | 1 |
| `precision_noncommutation` | 1 |
| `corrupt_certificates_rejected` | 11 |
| `invalid_inputs_rejected` | 4 |
| `resource_cap_unresolved` | 1 |

The independent checker imports neither the discoverer nor the Smith constructor.
Each certificate is checked against a separately supplied expected source, not only
against the source named inside the certificate. It verifies actual observation
word provenance, all local transport/output equations, Smith image witnesses and
explicit counterexamples to premature observation compression.

### Ranges and limitations

* 180 random full-matrix fixtures: primes 2,3,5; dimensions 1 through 6;
  precisions 1 through 5; zero and torsion observations included.
* 18 hidden-coordinate fixtures: dimensions 4 and 6, primes 2,3,5, precisions
  2,3,5. The hidden conjugating matrix is not supplied to the discoverer.
* One synthetic eight-coordinate system over Z/(2^16), hence 2^128 source states.
  Discovery accepts two independent tests, examines five candidates, and returns
  Smith valuations (0,2): two free coordinates, 2^30 distinct observable states.
  This instance is symbolically certified, not separately Lean-verified.
* One eight-coordinate delayed-observation system whose final distinguishing word
  needs seven operations, plus two explicit precision-change profiles.
* 62 small profiles are independently and exhaustively minimized as complete finite
  transition systems. Their total source-state count is 3,908. This exhaustive
  reference is separate from discovery, which never enumerates the state space.
* All 643 accepted-test growth witnesses are checked as actual distinguishing words.
* The 11 corrupted-certificate controls include changed source semantics with a
  stale hash and with a rebound hash but invalid equations. All are rejected.
* Four invalid inputs are rejected. A resource-cap exit is classified as unresolved,
  not as proof of mathematical impossibility.

These are synthetic mechanism tests, not a learned discovery benchmark, a held-out
structural evaluation, or evidence of advantage over existing tools. The two
coordinate counts and quotient cardinalities are distinct quantities. Minimum free
linear count assumes an R-linear initial encoding and the complete all-state
interface; it is not a lower bound for arbitrary algorithms.

## Predecessor reproduction

The frozen v0.1 ZIP is included unchanged under `history/`. Its documented audit
reproduced **22,758** check calls, and its deterministic `results/AUDIT.json`
matched the saved predecessor result byte-for-byte. Historical evidence and the
fresh replay are kept separate. See `evidence/PREDECESSOR_REPLAY.json`.

## Provenance

`LEAN_MANIFEST.json` and `COMPUTATION_MANIFEST.json` pin accepted inputs, logs,
outputs, commands and actual outcomes. `tools/validate_manifest.py` validates
these against the root. `FILE_MANIFEST.json` and `tools/verify_integrity.py`
provide distribution-byte integrity; hashes establish identity, not mathematical
truth. Rerunning an audit intentionally rewrites its current execution records.
Run distribution integrity BEFORE rerunning audits in an extracted copy.

Proof interpretation and code review are self-review, not independent researchers.
No historical-novelty claim is made.
