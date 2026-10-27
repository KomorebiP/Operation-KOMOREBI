# Formalization ledger — v0.4.0, Lean block 1

This ledger distinguishes paper claims from exactly what has compiled. There is no speculative percentage-complete estimate.

| Obligation | Status | Evidence / remaining boundary |
|---|---|---|
| Pointwise sufficiency iff decoder on image | COMPILED | Foundations |
| Total decoder with explicit nonempty target | COMPILED | Foundations |
| Collision certificate defeats every decoder | COMPILED | Foundations |
| Helper access criterion for general functions | COMPILED | Foundations; no chromatic-number theorem yet |
| Arbitrary-code message alphabet lower bound | COMPILED | Injection of task representatives into messages |
| Linear factorization iff kernel inclusion | COMPILED | General division-ring vector spaces |
| Linear restricted helper feasibility | COMPILED | Kernel intersection condition |
| Joint-kernel impossibility witness | COMPILED | Witness equivalence and universal decoder rejection |
| Optimal linear repair into F(ker R) | COMPILED | Actual existence proof, not a certificate assumption |
| Nonlinear alphabet lower bound and q^d formula | COMPILED | Explicit finite-type hypotheses |
| d = rank[R;F] − rank R | COMPILED | Ranges of typed linear maps |
| Exact affine-fiber characterization | COMPILED | Task difference belongs to F(ker R) iff reachable in fiber |
| Row-space syntax / coordinate H with exactly d rows | NOT SEPARATELY PORTED | Optimal message space has proven dimension d; choose/expose a finite basis next |
| Python matrix-certificate importer and parser soundness | NOT PORTED | Linear certificate equality is typed; raw matrices are not yet imported |
| General leakage-block rank theorem and composition rank bound | NOT PORTED | Paper/Python status retained from v0.3 |
| Canonical operational quotient and induced actions | COMPILED | Actual quotient construction and well-definedness |
| Universal factorization of adequate representations | COMPILED | Includes arbitrary finite action words |
| Sound simulation for all words and all times | COMPILED | Induction, not bounded enumeration |
| Finite linear predictive closure algorithm, minimal row space, strict-step bound | NOT PORTED | Generic quotient minimality is proved; algorithm proof is distinct |
| Haar symbolic helper repair and closed dynamics | COMPILED | Every field with 2 ≠ 0 |
| Haar all-time coarse prediction | COMPILED | Every n and every source |
| Haar source incompleteness / first-detail insufficiency | COMPILED | Explicit counterexamples |
| Haar minimum one-field-symbol message | COMPILED | Achievability plus general nonlinear lower bound |
| Shannon entropy, optimal Bayes error, categorical projector identities | NOT PORTED | v0.2 proof/test evidence retained, not Lean claims |
| Full state-aware partial-repair success curve | NOT PORTED | v0.2 evidence retained |
| Native floating Haar implementation correctness and floating stability | NOT PORTED | Prior bounded adapter tests are not a Lean verification of the library |
| Quantum, semantic, multi-encoder, noisy physical generalizations | OUTSIDE THIS BLOCK | No universal unification claim |

## Verification gates

The strengthened `clean_run_02` and separate `archive_replay` are the release gates. `clean_run_01` is retained as historical evidence but its negative-control diagnostic was weaker. Each release-gating run builds six production modules and their aggregate root from no project object files, audits all 58 theorem declarations, and completes all five negative controls. Repeated builds do not increase the count of unique theorems.
