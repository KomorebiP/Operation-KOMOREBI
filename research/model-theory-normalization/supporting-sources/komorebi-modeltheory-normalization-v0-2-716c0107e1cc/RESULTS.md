# Retained results — M2 / v0.2

## Lean

PASS: 11 modules; 18 expected-outcome tasks;
181 named declarations axiom-audited. Five new modules
contain 35 new theorem declarations. Cold-run duration:
24.032023 seconds. Accepted source hashes are unchanged.
Positive control accepts. All five negative controls reject. Only propext,
Classical.choice and Quot.sound occur. Exact argv and diagnostic logs are retained.

## Finite reference audit

PASS: **77,461 check calls**, deterministic seed 2026092102.
All 64 two-state systems with two labelled actions and one binary observation
are included, followed by 36 deterministic-seeded systems of sizes 1..6.
For each system and free-variable count 0,1,2, 24 source formulas are sampled
at recursion depth <=4. Another 32 operation-prefix formulas per system are
sampled at depth <=5. Value sort 0,1,2. All state assignments of the specified
arity are evaluated; quantifiers exhaust the finite tagged universe. Formula
sampling itself is not exhaustive. Finite-code formulas are checked against an
independent pair-search procedure on every pair of tagged objects.

| Check | Count |
|---|---:|
| binder mutation rejected | 1 |
| code formula qf | 100 |
| empty state sort guarded | 1 |
| empty state sort unguarded | 1 |
| existential retained not QE | 1 |
| full state equality failure | 1 |
| guarded definition all tags | 3,226 |
| invalid source rejected | 4 |
| invalid target or signature rejected | 5 |
| local code certificate | 100 |
| nested binders correct | 1 |
| nonsurjective reflection fails | 1 |
| path compiler qf | 3,200 |
| path compiler truth | 8,128 |
| standard quotient transport | 27,744 |
| standard satisfaction translation | 27,744 |
| state value tags disjoint | 1 |
| syntactic quantifier rank | 7,200 |
| unguarded spurious value witness | 1 |
| word reversal rejected | 1 |

The target reference interpreter uses only primitive first-order syntax and an
appended bound environment. The source reference remains unchanged and prepends
new state binders. These are implementation checks, not the universal proof.
Target quantifier-rank equality is tested here; the new universal formal complexity
endpoint is preservation of Mathlib IsQF when source quantifierRank is zero.

## Predecessor

The original v0.1 ZIP is frozen. Its byte-integrity check passed (82 payload files),
and its 78,011 finite checks reproduced. All six inherited proof sources are
unchanged and included in the new cold build. The earlier representation-calculus
and p-adic suites are not newly rerun.

## Interpretation

The universal compiler and fragment-preservation claims are exact Lean statements.
The mathematical interpretation audit is self-review. Python is not executable-
verified or extracted from Lean. Cached upstream Mathlib proofs are reused at the
recorded pin, not rebuilt from zero.
