# Paper IX: weighted nonlinear lifting

**Komorebi P. — 8 September 2026.**

The next weighted lifting block is complete in Lean. Let \(p\) be prime,
\(R=\mathbb Z_p\), \(F\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(J=DF(a)\).
If
\[
J\in\operatorname{GL}_d(\mathbb Q_p),\qquad p^sJ^{-1}\in M_d(R),\qquad
F(a)\in p^rR^d,\qquad r>2s,
\]
then
\[
\boxed{\exists!\,b\in a+p^{s+1}R^d:\ F(b)=0,}
\qquad \boxed{b-a\in p^{r-s}R^d.}
\]
The actual Jacobian can be singular modulo \(p\). Uniqueness is on the full ball
of depth \(s+1\), and the inverse-denominator exponent \(s\) is retained.
The theorem covers arbitrary integral p-adic coefficients and centers, including
the dyadic case and dimension zero. Exact boundary controls show why the strict
threshold and displacement exponent cannot uniformly be improved.

The five new mathematical modules contain 37 theorems and seven definitions.
The proof constructs polynomial Taylor normalization, proves actual polynomial
contraction, retains constant-term precision, and translates the result back to
the original equations. The integral inverse certificate is proved equivalent
to the stated fraction-field hypothesis. Full statements, proof and scope are in
`polynomial_weighted/WEIGHTED_LIFTING.md`.

## Evidence and replay

The fresh verification rebuilds all 30 polynomial mathematical modules and checks
external theorem contracts, positive and negative controls, and all mathematical
declaration axiom closures. Exact counts and hashes are in `RELEASE_AUDIT.json`
and `polynomial_weighted/verification/polynomial_weighted_verification.json`.
Independent review is in `polynomial_weighted/audit/ROUTE_AUDIT.md`.
Development failures and their corrections are retained.

Use the separately supplied pinned Lean 4.34.0-rc2 kit:

    python3 replay_paper9_weighted.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run

The runtime and reproducible compiled files are excluded from this source ZIP.
Earlier non-polynomial results retain their recorded historical verification;
they are not all rebuilt by this polynomial gate.

## Cumulative contents

All 1,092 files of the previous parameter-chart release are preserved by exact
uncompressed content hashes. Replaced root documents are retained under
`historical/parameter_charts_release_root/`. The direct coverage map is
`PACKAGE_COMPLETENESS.json`. This includes the previous perturbation, chart,
dyadic sharpening, obstruction, lifting, native, and original completion work.
The previous archive has SHA-256
`063daf6cdaa889c0201735967e015c5f515fe41b57d4e8741ca1b2b977d83d6f`.
Older manuscript recovery limitations and historical statuses remain recorded.

## Remaining work

The next precise target is weighted perturbation and its first-order formula:
for \(F(a)=0\), \(G=F+p^MH\), \(M>2s\),
\[
b-a=-p^MDF(a)^{-1}H(a)+\varepsilon,
\qquad \varepsilon\in p^{2M-3s}R^d.
\]
That expansion remains a written proof awaiting Lean formalization. Prescribed
parameter obstructions, general rank-deficient towers, analyticity, native
presentation invariance and descent, additional exact dyadic valuations and
period families, and manuscript consolidation remain on `REMAINING_CHECKLIST.md`.

The original stated Nishibuchi conjecture and earlier sharp dyadic results remain
completed with their recorded scopes. This release does not assert that every
strengthening or the full native program is resolved.
