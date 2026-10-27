# Final local and endomorphism source leaves

Checked 8 October 2026. This appendix supplements `LITERATURE_CHECK.md`; it does not change the manuscript's conditional bridge status.

## Split-Tate scalarity necessity

The exact manuscript locus is `paper/chapters/project_07.tex`, subsection *Two prime indices*. Its assertion is valid with the following explicit scope: `E/Q_q` has **split multiplicative reduction**, `q_E` is its Tate uniformization parameter with `v_q(q_E)>0`, `ell!=q`, and the **entire local Galois representation on `E[ell^n]`** is scalar. Scalarity of Frobenius alone is insufficient for the inertia conclusion.

The primary source is J.-P. Serre, *Abelian l-adic representations and elliptic curves*, the scanned **1989 Addison–Wesley edition**, originally published 1968, Chapter IV, Appendix A.1.2–A.1.3, printed IV-31–IV-34. The scan's title/copyright leaves were checked. The cached file was initially named with a guessed 1998 edition date; that acquisition identity was corrected to the verified 1989 edition before release. The source supplies:

- the exact Galois-module sequence `0 -> Z_ell(1) -> T_ell(E_qE) -> Z_ell -> 0` (A.1.2, printed IV-31);
- the identification of its extension class with the Kummer class of `q_E` (A.1.2 Proposition(a), IV-32);
- the unipotent matrix form over the completed maximal unramified extension and the off-diagonal image `ell^r Z_ell`, where `ell^r` is the largest power dividing `v(q_E)` (A.1.3 proof and exercise, IV-33–IV-34). The exercise statement was checked against the rendered page.

Here is the short deduction, rather than an assertion that the manuscript inequality is printed verbatim in Serre. Choose compatible roots of unity and roots of `q_E`. In the Tate basis the local action is

\[
\rho(\sigma)=
\begin{pmatrix}\chi_\ell(\sigma)&c_{q_E}(\sigma)\\0&1\end{pmatrix}.
\]

For `ell!=q`, roots of unity are unramified and arithmetic Frobenius acts on them by the `q`th power. Thus its two graded diagonal entries are `(q,1)`. On inertia the diagonal entries are both 1 and the off-diagonal image is the ideal `v_q(q_E) Z_ell` (equivalently `ell^(v_ell(v_q(q_E))) Z_ell`). One can also see the inertia ideal directly by writing `q_E=pi^m u`: over the maximal unramified extension the unit has all compatible prime-to-`q` roots, while the uniformizer Kummer character has image `Z_ell`; hence the image is `m Z_ell`.

Scalarity modulo `ell^n` forces the inertia off-diagonal to vanish and the Frobenius graded diagonal entries to agree. Consequently

\[
\ell^n\mid v_q(q_E),\qquad \ell^n\mid(q-1),\qquad
n\le\min\{v_\ell(q-1),v_\ell(v_q(q_E))\}.
\]

This is a necessary condition only. It does not prove sufficiency: an unramified off-diagonal Kummer component can impose further conditions. It also does not reproduce a conductor-prime power `q^(e-1)` as a coefficient-prime congruence factor or construct a global arithmetic transfer. For a general finite extension of `Q_q`, replace the integer `q` in the Frobenius condition by the residue-field cardinality and normalize the valuation accordingly.

## Number-field Galois endomorphisms

The checked primary author source is Gerd Faltings, *Finiteness Theorems for Abelian Varieties over Number Fields*, Chapter II, §1 Introduction, statement **(b)**, in the English chapter scan hosted on F. Pazuki's academic site. Its first chapter page was inspected visually because text extraction produced only page breaks. The introduction fixes a number field `K`, an abelian variety `A/K`, a prime `ell`, and the absolute Galois group `G_K`; statement (b) asserts

\[
\operatorname{End}_K(A)\otimes\mathbb Z_\ell
\;\xrightarrow{\sim}\;
\operatorname{End}_{G_K}(T_\ell(A)).
\]

Serre's **1989 Special Preface, printed p. ix**, independently states the Hom version for abelian varieties over a number field and explicitly attributes its proof, and rational Tate-module semisimplicity, to Faltings. That formula and attribution were checked visually. Faltings's original paper is *Endlichkeitssätze für abelsche Varietäten über Zahlkörpern*, Inventiones Mathematicae 73 (1983), 349–366; this is the number-field result, rather than Tate's finite-field isogeny theorem.

For an elliptic curve `E/K`, tensoring the integral statement with `Q_ell` yields

\[
\operatorname{End}_{G_K}(V_\ell(E))
=\operatorname{End}_K(E)\otimes\mathbb Q_\ell.
\]

The conclusion that this algebra consists only of scalar endomorphisms requires the explicit premise `End_K(E)=Z` (for example, the stronger hypothesis `End_(Kbar)(E)=Z`). The isomorphism alone does not impose that premise. In particular, no generic “Tate module must be scalar” statement follows, and the existence of Galois-equivariant projectors is constrained by the actual endomorphism algebra.

## Fresh formalization-status check

During this follow-up, the current primary README at `https://github.com/lana-agents/iut/blob/main/README.md` was inspected on 8 October 2026. It includes October 2026 interface changes and expressly says the repository does **not verify IUT**. It specifies `Corollary312Variant` as an unproved proposition, distinguishes it from Mochizuki's printed Corollary 3.12, and describes the implications to ABC as conditional. This repository statement is compatible with the cautious status in the main audit. It is not an independent compiler/source-faithfulness audit by this project. The July LANA report remains a dated interim report; the search record now also includes this newer repository boundary statement.

Primary-source originals and rendered pages remain private in `evidence/literature` and are excluded from the release ZIP. The source and theorem-leaf manifests record the new sources, hashes, and extraction limits.
