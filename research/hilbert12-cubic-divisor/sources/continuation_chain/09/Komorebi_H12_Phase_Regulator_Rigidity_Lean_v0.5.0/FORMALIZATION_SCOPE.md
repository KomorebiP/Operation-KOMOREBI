# Formalization scope: 154 compiled theorem constants

The inherited 140 theorem source files and proof bodies are unchanged. The new files contain fourteen theorems:

| File | Count | Kernel-checked scope |
|---|---:|---|
| H12PhaseRegulator | 7 | Complex-valued real interval integrals; actual derivative hypotheses and FTC; exponentiated endpoint and periodic cubic identities; explicit analytic comparison implications |
| H12ContractingRigidity | 3 | Invariance through every natural iterate, convergence under norm contraction, continuity at zero implies constant phase |
| H12CubicBranch | 4 | Complex cube roots have norm one; nontrivial roots have squared distance three from one; conditional comparison from cubic equality and an enclosure hypothesis |

These are not all algebraic placeholders. The first module uses Mathlib integration and differentiation, and the second uses topological limits. Both work with explicitly supplied functions and hypotheses.

Not Lean-formalized: the actual elliptic-gamma definition and its convergent logarithmic series, verification of the generic analytic hypotheses for gamma, the interval-arithmetic implementation, the sharp Green operator bound, the global meromorphic nondiscrete-period argument, elliptic uniformization in the finite-isogeny obstruction, and the arithmetic comparison exp(R3(G))=(U_alg/epsilon^2)^3.

The latter equality is not asserted as an axiom or silently inserted into an application. The branch lemma assumes the cubic equality AND the norm inequality. Interval files certify the inequality outside Lean, conditional on mpmath.iv's trusted arithmetic. No tiny residual is used as an equality proof.

All 154 are compiled with warnings as errors. The axiom audit permits only propext, Classical.choice and Quot.sound where required. There are no sorry/admit placeholders, custom axioms, unsafe declarations, or native_decide calls. A false integer equality is separately required to fail.
