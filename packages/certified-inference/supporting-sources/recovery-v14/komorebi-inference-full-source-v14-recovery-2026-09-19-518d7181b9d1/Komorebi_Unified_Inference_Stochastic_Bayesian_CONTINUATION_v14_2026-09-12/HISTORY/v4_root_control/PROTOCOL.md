# Continuation protocol

1. Treat `AUDIT.json` and `CONTINUE_HERE.md` as the proof-state ledger.
2. Never reopen a `CLOSED_CHECKED` block unless a dependency/hash inconsistency is discovered.
3. For every new theorem block, separate algebraic identities from probability semantics.
4. Use the pinned Lean 4.34.0-rc2 / mathlib `aeb72f...` runtime.
5. Compile with `-DwarningAsError=true`.
6. Before `Checked` promotion: zero `sorry`; zero `admit`; zero custom axioms; representative `#print axioms`; SHA-256 manifest; explicit statement of what remains open.
7. A timeout, import/API mismatch, or resource failure is not a mathematical disproof. Record it separately.
8. Do not claim a canonical Bayesian posterior from Kalman algebra alone. Require a disintegration/normalized-Bayes semantic theorem.
9. Do not claim multiscale posterior semantics from the one-dimensional scalar bridge. Require finite-dimensional/Hilbert Gaussian conditioning first.
10. Do not claim literature novelty from formal verification alone.


## v3 active-layer addendum

Use `CHECKED_RELEASES/FD_Gaussian_Bayesian_Conditioning_v0.1.0_Checked/MODULE_ORDER.json` and `verify_blocks.py`. Each Lean process is
separate. The new completed boundary is finite-dimensional canonical Gaussian
conditioning with P positive semidefinite and R positive definite. The next open
boundary is its integration with the multiscale posterior perturbation layer.
Historical control documents under HISTORY describe their original checkpoints.
Only the root v3 CONTINUE_HERE.md specifies the current next task.


## v4 active-layer addendum (supersedes the v3 next-task paragraph)

The semantic multiscale posterior-moment bridge is now CLOSED_CHECKED. Its release
is `CHECKED_RELEASES/FD_Multiscale_Posterior_Semantic_Bridge_v0.1.0_Checked`. Follow that release's
module order and separate-process verifier. Every active theorem/lemma is audited,
not just representative ones. The next open block is shared-noise coupling and a
posterior-distribution metric bound. Preserve centering, norm geometry, distinct
canonical null-set measures, positivity, and non-identifiability boundaries.
Use the root v4 CONTINUE_HERE.md for the current next task; historical controls
remain snapshots rather than active instructions.
