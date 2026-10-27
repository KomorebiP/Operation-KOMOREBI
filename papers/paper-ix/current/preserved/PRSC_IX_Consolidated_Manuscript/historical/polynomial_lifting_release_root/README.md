# Paper IX: cumulative proofs, manuscripts and research archive

**Author: Komorebi P. — 8 September 2026.**

The next polynomial block is complete: actual multivariable Taylor divisibility, a finite one-step obstruction for every fixed integer-polynomial system, independence of integer representatives, and a finite compatibility criterion for shared polynomial lifts. The fresh Lean replay passed all 18 gates, including four expanded statement contracts and three rejected invalid proofs.

This cumulative archive includes the original completion, all subsequent sharp dyadic towers, exact packet periods, continuous isometries, affine and polynomial lifting work, available manuscripts, research checkpoints, reproducible scripts and audit history. It restores 38 previously omitted research/provenance files. Every file hash from all seven prior local output ZIPs is represented in this package, without nesting those seven releases. The original baseline archive is retained as provenance.

## Start here

| File or directory | Contents |
|---|---|
| `REMAINING_CHECKLIST.md` | Current proved/open status, full notation and next formalization task |
| `polynomial_lifting/POLYNOMIAL_LIFTING.md` | New theorem statements and proof explanation |
| `polynomial_lifting/INDEPENDENT_PROOF_AUDIT.md` | Independent review of hypotheses, scope, contracts and run evidence |
| `manuscript/` | All 25 historical PDF/TeX files exposed from the original baseline; main Paper IX PDF and supplements |
| `baseline/` | Original complete source ZIP and its provenance |
| `strengthening/` | Sharp towers, exact dyadic displacements and periods, and continuous dyadic isometries |
| `shared_correction/` | Common quotient and actual affine pair lifting |
| `polynomial_lifting/` | Actual polynomial Taylor, obstruction, representative and joint-lift formalization |
| `native/` | Earlier native-conjecture analysis, affine theorem and bounded polynomial experiments |
| `research/mahler_kernel/` | Recovered exact finite kernel experiments and results |
| `historical/` | Prior release metadata, development evidence and recovered source windows |
| `MANIFEST.json`, `PACKAGE_COMPLETENESS.json` | Distributed-file hashes and prior-release coverage |

Historical manuscript versions and notes keep their original contents. They have not been rewritten into a single new manuscript incorporating every continuation. The root checklist is the current status reference.

## New theorem

For a fixed system \(F\in\mathbb Z[X_1,\ldots,X_d]^e\), every integer \(q>0\), depth \(L\ge1\), and solution \(F(x)\equiv0\pmod{q^L}\), set
\[
R_q=\mathbb Z/q\mathbb Z,\qquad
r_x=F(x)/q^L,\qquad
J_x=\rho_q\circ DF(x):\mathbb Z^d\longrightarrow R_q^e.
\]
Then the finite obstruction
\[
\mathcal O_x=R_q^e/\operatorname{im}J_x,
\qquad o_x=[\rho_q(r_x)]
\]
satisfies
\[
\boxed{
 o_x=0\iff
 \exists y\equiv x\pmod{q^L}:F(y)\equiv0\pmod{q^{L+1}}.
}
\]
The proof computes \(DF\) from actual formal partial derivatives and establishes
\[
a^2\mid P(x+at)-P(x)-a\sum_i(\partial_iP)(x)t_i
\]
for every integer polynomial \(P\) and integer \(a\). The level hypothesis gives \(2L\ge L+1\). Moduli may be composite or equal to one.

Changing the representative to \(x+q^Ls\) preserves \(J_x\) and changes the residual digit by \(J_xs\), leaving its class unchanged. For a second system with reduced Jacobian \(K_x\), individually valid corrections \(u,v\) share a next lift exactly when
\[
[u]=[v]\quad\text{in}\quad
\mathcal C_x=\mathbb Z^d/(\ker J_x+\ker K_x).
\]
This finite quotient and the choice-independent labels are checked against actual nonlinear lifts.

## Earlier completed results retained

- The full stated Nishibuchi Conjecture 3.9, including the exceptional dyadic branch, and the improved divisor-branch starting threshold.
- Step-valuation amplification and the uncapped all-row \(N=4\) difference bounds.
- The optimal classical \(N=2\) dyadic edge tower with uniform exponent \(4M+3\).
- For \(U_j(n)=E_{4n}^{(4,j)}\), \(j<4\), exact displacements
  \[
  v_2(U_j(n+T)-U_j(n))=v_2(T)+d_j,
  \quad (d_0,d_1,d_2,d_3)=(1,1,5,3),\quad T>0,
  \]
  and least positive packet periods \(2^{\max(0,r-d_j)}\) modulo \(2^r\).
- Unique continuous isometric bijections \(G_j:\mathbb Z_2\to\mathbb Z_2\) with
  \[
  G_j(n)=\frac{U_j(n)-j!}{2^{d_j}},
  \]
  and original coefficient extensions with exact images \(j!+2^{d_j}\mathbb Z_2\). The parameter is packet index \(n\), corresponding to coefficient degree \(4n\).
- Finite affine obstructions and the common-quotient universal property with actual joint affine lifting.

The normalized dyadic maps are metric isometries; the checked example \(G_0(1)=-1\), \(G_0(2)=34\) shows they need not be additive.

## Validation and reproduction

The new polynomial replay freshly compiled all nine listed modules, including four prior affine/common-quotient dependencies. It checked four explicit statement contracts, audited 91 named declarations and rejected three invalid proofs: **18 gates passed in 66.708 seconds**. The five new polynomial modules contain 44 declarations (35 theorems, eight definitions and one abbreviation); four further declarations are statement contracts. Counts include support lemmas and boundary controls.

Only `propext`, `Classical.choice` and `Quot.sound` are permitted; warnings are errors. The runtime is Lean `4.34.0-rc2` with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The pinned Mathlib cache is reused. All project modules needed by the new polynomial gate are freshly built.

Prior completed blocks retain their passing evidence. The preceding isometry continuation passed 38 gates with 22 modules and 246 declaration audits, including **three statement contracts and eleven negative controls**. The older isometry root audit transposed this breakdown to one and thirteen; its historical bytes are preserved, while this release uses the authoritative gate entries. Its total gate count and source proofs are unaffected. The full baseline and dyadic continuation were not rerun during this polynomial block.

Run only the new block:

```sh
python3 replay_paper9.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_run
```

Run all preserved active proof blocks, then the polynomial block:

```sh
python3 replay_paper9.py --all --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --output /absolute/path/to/new_full_run
```

These commands use the separately supplied portable kit and do not download dependencies. The full wrapper is provided for reproduction; the observed new run is the polynomial gate described above. Original source and verification records include source hashes and the exact commands used. Compilation outputs are reproducible and are excluded from this source archive.

## What remains

The next clear formalization is the correction-digit torsor and prime-field lift counts. Transition maps and hypotheses for compatible infinite lifting also need to be specified and proved. Unrestricted native Conjectures 13.2/13.3 remain open in the stated program: this block establishes fixed-presentation, one-step results.

Research questions still include exact higher-order difference valuations, least periods in other parameter families, general Mahler-kernel valuations and exact classical-tail valuations at arbitrary rows. None is a missing step in the completed stated Nishibuchi conjecture.

## Archive scope

This is the complete cumulative collection of known local Paper IX work covered by the inventory, plus the new verified block. The two older edge manuscripts recovered only as partial source windows remain partial; the reconstructed Annals source is identified as such. The external Nishibuchi paper is recorded by URL, version and checksum. The separately distributed Lean runtime, compiled caches, unrelated search results and repeated cumulative ZIPs are excluded. `PACKAGE_COVERAGE_RECOMMENDATIONS.md` records these decisions.
