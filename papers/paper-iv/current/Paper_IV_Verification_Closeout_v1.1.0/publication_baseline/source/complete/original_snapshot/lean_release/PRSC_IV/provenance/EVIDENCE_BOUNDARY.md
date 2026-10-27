# Paper IV evidence boundary

This file records what each kind of evidence in the Paper IV development
release does and does not establish.

## Four evidence classes

| Code | Evidence | Meaning |
|---|---|---|
| `L` | Lean-backed declaration | A named theorem or construction compiles in the pinned Lean/Mathlib environment. |
| `P` | Article proof | The manuscript contains a mathematical proof, but the result is not necessarily in Lean. |
| `I` | Imported fact | The manuscript invokes a cited standard theorem with its hypotheses stated. |
| `C` | Finite computation | A symbolic or numerical test checks selected finite instances. It is regression evidence, not a universal proof. |

The register's `L(full)` code means the full scoped manuscript result is covered by the aggregate of its map rows. All 68 theorem-like records are full. Every proof is checked under the pinned environment; finite computations do not establish universal theorems.

Complex powers use a formal series, a normalized analytic germ, or a single fixed holomorphic logarithm on the stated zero-free domain. The diagonal determinant is the paper's actual trace-class specialization. Nearest-pole results retain positive integral reciprocal order and simple-nearest-zero hypotheses. Imported standard fact 11.1 remains imported; the checked growth-order proofs do not depend on it. Open claims of universal simplicity, positivity of every reduced zero, full displacement expansions and a zeta functional equation remain open.

## Audit of the inherited computational package

The following findings are retained from the earlier audit, not claimed as
new computations in checkpoint 0.14.0. The recovered pre-release package reported `1246/1246` strengthened checks,
`647/647` legacy checks, and `981/981` table rows. Independent reruns reproduced
those totals after installing undeclared dependencies. The checks are finite:

- 942 bounded exact-symbolic instances
- 275 finite numerical examples
- 15 text or build-hygiene checks
- 14 unconditional pass markers

Mutation testing changed a projector identity by a false factor of two and a
zero-counting constant by a false factor of seven; the strengthened suite still
reported `1246/1246`. The suite therefore cannot serve as theorem proof.

The old archive is retained only as provenance outside the canonical release.
Its SHA-256 is:

`ac3b97e1f9ae1086ed082a5cdf2e8c6486e0d1bf0c176bd275afaa03a1d2b9b5`

## Scope allocation in the twelve-paper series

- Paper III owns general nonlinear operation trees.
- Paper VI owns bounded-operator semigroup, resolvent, and Feshbach theory.
- Paper IX owns arithmetic congruences and p-adic/Amice--Mahler interpolation.
- Paper X owns abstract completion and occupancy questions.

Paper IV retains the scalar cyclic analytic family and its specialized diagonal
determinant model. It does not claim any of the four general theories above.
