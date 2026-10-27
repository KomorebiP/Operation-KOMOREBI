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


## v5 active-layer addendum (supersedes older next-task paragraphs)

The shared-noise posterior-distribution bound, inexact-gain residual certificate,
noise-floor stopping implication, and compatible two-model factor bound are now
CLOSED_CHECKED. Use CHECKED_RELEASES/FD_Posterior_Coupling_v0.1.0_Checked and the
root v5 CONTINUE_HERE.md. Audit all active theorem/lemma axioms and final-source /
direct-dependency hashes. Keep the all-plan transport definition, chosen-coupling
nonoptimality, numerical boundary, factor convention, noise floor and explicit-versus-
canonical posterior scope visible. Next: correct self-adjoint packet-energy refinement,
then certified numerical majorants and admissible adaptation. Historical root controls
are immutable and are not the current next-task instructions.


## v6 active-layer addendum (supersedes older next-task paragraphs)

The self-adjoint packet-energy layer and its actual-posterior coupling/stopping
interfaces are CLOSED_CHECKED. Use root v6 controls and the active FD_Packet_Energy
release. Preserve the distinction between self-adjoint energy geometry and the old
algebraic projector family. Complete fixed-residual re-accounting is not adaptive
progress. Next: certified numerical enclosures and validity-preserving acceptance.
Keep every failed or interrupted attempt separate from final successful receipts.


## v7 active-layer addendum (supersedes all older next-task paragraphs)

The exact-rational residual-energy/noise-floor checker, real posterior bound and
fixed-model finite acceptance policy are CLOSED_CHECKED. Use root v7 controls
and FD_Exact_Posterior_Certificates_v0.1.0_Checked. Preserve the exact-input and
factor-witness scope. A Python output is provisional until the concrete Lean
proof instance compiles. Concrete checks use decide +kernel, never native
proof shortcuts. Audit every active theorem and final source/dependency hashes.
Non-increasing certificate scores are not monotonic true error or convergence.
Next: solver-specific contraction and iteration-to-tolerance, then broader input
uncertainty or model/packet-changing policies as separately proved extensions.
