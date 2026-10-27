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
