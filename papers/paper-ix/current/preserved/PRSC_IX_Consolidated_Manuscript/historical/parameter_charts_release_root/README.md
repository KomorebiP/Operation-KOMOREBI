# Paper IX: continuous p-adic parameter charts

**Komorebi P. — 8 September 2026.**

**Fresh verification: PASS — 40 checks, 244 explicit declaration audits.**

## Main statement

Let \(p\) be prime, \(L\ge1\), \(e,q\ge0\), and
\[
F\in\mathbb Z[X_1,\ldots,X_{e+q}]^e,\qquad
x\in\mathbb Z^{e+q},\qquad F(x)\equiv0\pmod{p^L}.
\]
Assume the actual reduced Jacobian
\[
A_x=DF(x)\bmod p:\mathbb F_p^{e+q}\longrightarrow\mathbb F_p^e
\]
is surjective. All vector congruences are coordinatewise.

There is a coordinate permutation \(\sigma\), with
\((\sigma z)_i=z_{\sigma(i)}\). Write \(\sigma z=(y,t)\), using \(e\) solved
coordinates and \(q\) free coordinates. Define
\[
(y_0,t_0)=\sigma x,\qquad
B=x+p^L\mathbb Z_p^{e+q},\qquad
T=t_0+p^L\mathbb Z_p^q,\qquad
\mathcal R=\{z\in B:F(z)=0\}.
\]
There is a homeomorphism
\[
h:T\xrightarrow{\ \sim\ }\mathcal R,\qquad
h^{-1}(z)=\operatorname{free}(\sigma z).
\]
Equivalently, a continuous function \(\phi:T\to y_0+p^L\mathbb Z_p^e\)
gives the entire root locus through \(\sigma h(t)=(\phi(t),t)\).
Every parameter has exactly one corresponding root in \(B\). For every \(N\ge0\),
\[
\boxed{h(t)\equiv h(u)\pmod{p^N}\iff t\equiv u\pmod{p^N}.}
\]

The coordinate choice is a conclusion. A suitable minor and a preexisting
chart are not hypotheses. The theorem covers the original root locus after
undoing the coordinate reordering. Since \(x\) is an approximate root, it does
not assert \(\phi(t_0)=y_0\) unless \(F(x)=0\) exactly. The cases \(p=2\),
\(L=1\), \(e=0\), and \(q=0\) are included.

## Supporting theorems

For a rectangular integer polynomial system with a surjective reduced
Jacobian at \(x\), and \(L\ge1\),
\[
F(x+p^L\mathbb Z_p^d)=F(x)+p^L\mathbb Z_p^e.
\]
This covers arbitrary p-adic output targets. No lower-root hypothesis is needed.

When \(d=e\), the actual restricted polynomial map is a homeomorphism.
Moreover, for arbitrary \(a,b\in x+p\mathbb Z_p^d\) and every \(N\ge0\),
\[
F(a)\equiv F(b)\pmod{p^N}\iff a\equiv b\pmod{p^N}.
\]
Its inverse therefore preserves every congruence depth.


## Contents and replay

The complete theorem exposition and proof dependencies are in
polynomial_charts/POLYNOMIAL_PARAMETER_CHARTS.md. The active checklist is
REMAINING_CHECKLIST.md. Sources, contracts, current verification, independent
audit, and recovery provenance are in polynomial_charts/.

All 883 files of the recovered perturbation release are preserved by
uncompressed content hashes, including earlier papers and verification.
Replaced root documents are retained under historical/perturbation_release_root.
The original perturbation ZIP had SHA-256
61322b5b58a43def882cb77eff8dd00d8af44f803c99f97cce27c2e7f909f4e9.
Its prior-archive coverage record is preserved; those older archives were not
all independently downloaded and compared again during recovery.

Use the separately supplied pinned Lean kit:

    python3 replay_paper9_charts.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run

The observed new gate rebuilds the polynomial modules and their dependencies.
Earlier non-polynomial verification retains its recorded historical status.
The source archive excludes the separate runtime and reproducible compiled
outputs. Two older edge manuscripts remain partial recovered windows; the
Annals TeX remains identified as reconstructed text.

## Next work

Continuous rectangular charts are the present block. Weighted nonlinear
lifting for a Jacobian invertible over \(\mathbb Q_p\) but singular modulo
\(p\), followed by first-order root motion, is the next clear formalization.
General singular towers, native presentation invariance and global/completed
descent, exact higher differences, additional period families, general Mahler
valuations, arbitrary-row exact tails, and manuscript consolidation remain.

The original stated Nishibuchi conjecture and earlier sharp dyadic results
remain preserved. These further questions are not missing steps in that
completed conjecture proof. Analyticity is not claimed for the new chart.
