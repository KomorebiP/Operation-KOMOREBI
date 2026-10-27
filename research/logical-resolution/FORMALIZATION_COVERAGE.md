# Formalization coverage — Logical Resolution v0.2

PASS: 13 local library modules, 112 theorem declarations,
74 definitions, 2 abbreviations,
3 structures and 5 inductive syntaxes.
All **196 explicit named declarations** were axiom-audited.
The five new modules add 39 theorems, 20 definitions, one abbreviation, one
structure, and three inductive syntaxes. No claim of 39 historically new results.

All 23 expected-outcome tasks passed. Every library file was compiled
with warnings-as-errors. Only Classical.choice, Quot.sound and propext occur.
No additional project axiom, sorryAx, or Lean.ofReduceBool appears. Two positive
controls pass; six false/placeholder controls reject. Accepted source hashes were
unchanged. The eight inherited library files match their frozen original bytes.

Lean: Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. This is a cold LOCAL build using the pinned upstream
compiled cache, not a rebuild of Mathlib or the entire embedded history.

| New module | Checked content |
|---|---|
| RelationalSyntax | Exact old-language inclusion; binary state relations; surjective quantified transport; relation descent iff fiber invariance; actual behavioral quotient preservation |
| RelationalBackForth | Atomic relation-sensitive agreement, both witness directions, reflexivity/symmetry, finite-rank and all-rank soundness |
| StandardTranslation | Actual FirstOrder.Language/model, source-to-Mathlib syntax, arbitrary free/bound assignment correctness, old-language bridge, quantifier rank and IsQF correctness, standard transport |
| StandardContracts | Fully composed actual quotient and finite-rank back-and-forth theorems for standard Realize |
| QuantifierWitness | Three actual vertices and one edge; all parameter-free standard QF formulas agree on single-vertex assignments; a rank-one formula distinguishes; no QF replacement in the same model; old quotient cannot retain the relation |

## Boundaries

The translation is a one-sorted relationalization on the state carrier, with
primitive predicates interpreting observations in a fixed external value type.
It is not a native many-sorted backend. The translated fragment excludes state
equality even though the target syntax supports it. Generic preservation therefore
does not assert full first-order elementarity. The three-vertex QF theorem is
explicitly stronger within that particular parameter-free model and does include
standard equality atoms.

Back-and-forth is a sufficient preservation condition, not a proved completeness
or strategy-discovery theorem. Atomic tests allow arbitrary finite operation words.
The Python executable and interpretation of prose are not kernel-verified. No
compactness, saturation, QE algorithm, imaginaries theorem, performance advantage,
independent referee result, or novelty verdict is claimed.
