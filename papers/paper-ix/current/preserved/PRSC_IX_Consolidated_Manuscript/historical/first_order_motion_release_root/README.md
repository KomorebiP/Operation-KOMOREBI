# Paper IX: weighted first-order root motion

**Komorebi P. — 8 September 2026.**

The first-order perturbation block is complete in Lean. Let \(p\) be prime,
\(R=\mathbb Z_p\), \(F,H\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(F(a)=0\).
Write \(J=DF(a)\). If
\[
J\in\operatorname{GL}_d(\mathbb Q_p),\qquad p^sJ^{-1}\in M_d(R),\qquad M>2s,
\]
then \(G=F+p^MH\) has exactly one root \(b\in a+p^{s+1}R^d\), and
\[
b-a\in p^{M-s}R^d,\qquad
\boxed{b-a=-p^MJ^{-1}H(a)+\varepsilon,\quad \varepsilon\in p^{2M-3s}R^d.}
\]
The proof constructs the root using the original Jacobian bound. It covers all
primes, arbitrary integral p-adic coefficients and centers, and finite square
dimension. Uniqueness holds throughout the stated ball. A checked dyadic
quadratic example realizes the error exponent exactly.

The five new mathematical modules contain 13 theorems and one definition.
The full theorem, proof, sharpness, and scope are in
`polynomial_motion/FIRST_ORDER_ROOT_MOTION.md`. The complete current checklist
is `REMAINING_CHECKLIST.md`.

## Verification and replay

The fresh gate rebuilds all 35 mathematical polynomial modules, checks expanded
theorem statements and boundary controls, and audits every project declaration's
axiom closure. Exact counts, hashes, and provenance are in `RELEASE_AUDIT.json`
and `polynomial_motion/verification/polynomial_motion_verification.json`.
The independent raw proof review and reconciliation are under
`polynomial_motion/audit/`. Actual development failures and corrections are retained.

With the separately supplied pinned Lean 4.34.0-rc2 kit, run:

    python3 replay_paper9_motion.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run

Compiled outputs and the separate runtime are excluded from this source archive.
Earlier non-polynomial proofs retain their recorded historical verification.

## Cumulative contents

All 1,248 files of the preceding weighted-lifting release are preserved by
uncompressed content hash. Replaced root documents are under
`historical/weighted_lifting_release_root/`. The exact coverage map is
`PACKAGE_COMPLETENESS.json`. The preceding ZIP has SHA-256
`dd99a705b933eff4fb8305afa6ebe4bcf8bc70812f0178ab76050c57d3e7efce`.
Earlier manuscript recovery limitations and historical source statuses remain recorded.

## Remaining work

The next clear block is the prescribed-parameter obstruction and its bridge to
actual polynomial lifts: \(Ju=-\bar r-Kv\), equivalently
\([\bar r+Kv]=0\) in \(\operatorname{coker}J\).
General rationally rank-deficient towers, higher obstructions, analytic
regularity, native presentation invariance and global/completed descent, further
exact dyadic valuations and period families, and manuscript consolidation remain.

The original stated Nishibuchi conjecture and earlier sharp dyadic results
retain their completed scopes. This release does not resolve every strengthening
or the full native program.
