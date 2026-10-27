# Paper IX: proved results and remaining work

**Komorebi P. — proofread edition, 8 September 2026**

The current {{PAGE_COUNT}}-page manuscript has been proofread, polished and checked against the available original paper and completed continuation blocks. Recoverable omissions in the first consolidation have been restored. This completes the editorial work within the manuscript's stated scope; it does not settle every extension in the broader research program.

Write
\[
U_{N,j}(n)=E_{Nn}^{(N,j)}=j!C_{N,j}(n),
\qquad \Delta_u f(n)=f(n+u)-f(n).
\]
For \(N=4\), put \(U_j=U_{4,j}\), \(0\le j<4\). A packet shift \(u\) is a degree shift \(Nu\). Valuation lower bounds include zero differences; exact valuation statements supply the necessary nonvanishing.

## Completed mathematical blocks

- [x] **Arithmetic framework.** Triangular inversion, denominator clearing, finite Newton–Mahler identities, packet and address operations, and the stated transport results have their matched formal sources. The explicit product \(D_{N,j}(n)=\prod_{r=1}^{n}\binom{Nr+j}{Nr}\) is restored in this edition.
- [x] **Full stated Nishibuchi conjecture.** For every prime \(p\), positive \(m\) with \(m\mid p-1\) or \(m=2\), and \(j<mp\), the original coefficients are \(p\)-integral. With \(q=\operatorname{lcm}(2,p-1)\),
  \[
  E_{mpn+qp^r}^{(mp,j)}\equiv E_{mpn}^{(mp,j)}\pmod{p^r}
  \qquad(r\ge1,\ n\ge r).
  \]
  On the divisor branch the sufficient starting condition improves to \(r\le mn\).
- [x] **Amplified differences.** On the divisor branch, with \(h=(p-1)/m\),
  \[
  v_p(\Delta_{uh}^{k}U_{mp,j}(n))\ge
  \min\{k(1+v_p(u)),mn\}\qquad(u>0).
  \]
  For \(N=4\), the row cap is removed:
  \[
  v_2(\Delta_u^k U_j(n))\ge k(1+v_2(u))+v_2(j!).
  \]
  The zero-step cases have separate zero-safe statements. The restored \((p,N,j)=(3,6,3)\) example proves that passing to \(C_{N,j}\) requires the factorial correction.
- [x] **Sharp dyadic displacements and periods.** For \((d_0,d_1,d_2,d_3)=(1,1,5,3)\),
  \[
  v_2(U_j(n+T)-U_j(n))=v_2(T)+d_j\qquad(n\ge0,\ T>0).
  \]
  The difference is nonzero. For \(r\ge0\), the least positive packet period modulo \(2^r\) is \(2^{\max(0,r-d_j)}\), and all positive packet periods are its positive multiples.
- [x] **Classical dyadic edge tower.** For the signed Euler coefficients of \(\operatorname{sech}z\), the depth-\(M\) tower has error in \(2^{4M+3}\mathbb Z_2\), with equality in valuation at row \(M+1\). Individual weights and row-sensitive lower bounds are checked. This is the classical \(N=2\) family.
- [x] **Dyadic interpolation.** Each normalized packet extends uniquely to an isometric bijection \(G_j:\mathbb Z_2\to\mathbb Z_2\), and \(\widetilde U_j=j!+2^{d_j}G_j\) has exact image \(j!+2^{d_j}\mathbb Z_2\). These maps need not be additive.
- [x] **Finite obstructions and shared corrections.** Affine and polynomial next-step lifts have finite obstruction classes derived from their lower-level equations. Within a fixed presentation, polynomial classes are independent of the chosen integer representative. The shared-correction quotient and its universal property give precise joint lifting criteria. The stated positive composite moduli and modulus-one cases are included; shared affine lifting also includes depth zero.
- [x] **Exact polynomial lift counts.** At a lower root with reduced Jacobian of rank \(\rho\), every nonempty correction fiber is a torsor for the kernel. For \(d\) variables and \(e\) equations its size is \(p^{d-\rho}\), while the obstruction group has size \(p^{e-\rho}\).
- [x] **Compatible towers and local charts.** The smooth results construct one compatible integer tower and its exact p-adic root, prove uniqueness for square systems in the stated ball, and give local surjectivity, square inverses and rectangular charts. Prescribed parameter paths and arbitrary p-adic endpoints have their corresponding existence and exact branching results.
- [x] **Weighted lifting and deformation.** The weighted theory covers arbitrary integral p-adic coefficients and centers when the solved Jacobian is invertible over \(\mathbb Q_p\). If \(p^sJ^{-1}\) is integral and \(M>2s\), coefficient and parameter perturbations have a unique nearby root in the stated ball. For \(G=F+p^MH\) and \(\tau=t_0+p^Mv\),
  \[
  y-y_0=-p^MJ^{-1}(H(y_0,t_0)+Kv)+\varepsilon,
  \qquad \varepsilon\in p^{2M-3s}\mathbb Z_p^e.
  \]
  Here \(J=D_YF(y_0,t_0)\), \(K=D_TF(y_0,t_0)\), and \(F(y_0,t_0)=0\). Checked examples attain the stated error depth.
- [x] **Local analytic regularity.** An invertible solved Jacobian gives a local analytic graph \(y=\psi(t)\), with strict derivative \(D\psi(t_0)=-J^{-1}K\). The core holds over every complete nontrivially normed field. Continuous root selections have the same germ and inherit the regularity; the integral p-adic specialization is stated in the ambient field. No new explicit uniform radius is asserted by this qualitative theorem.

## Material restored or clarified in this edition

- [x] Restore the explicit denominator product, Lucas standard-window reduction, residue independence and common period, the signed zigzag coefficient identity, and the exact normalization-loss counterexample, with matched preserved Lean sources.
- [x] Restore the Bernoulli boundary
  \[
  C_{2,1}(n)=(2-2^{2n})B_{2n},\qquad B_1=-\tfrac12,
  \]
  with its classical generating-series proof. A dedicated Lean bridge was not matched; this is not reported as new formal verification.
- [x] Acknowledge the earlier commutative-algebra obstruction argument, finite polynomial CRT reconstruction and finite compatibility analysis, with their historical prose or external-source evidence kept distinct from Lean certification.
- [x] Clarify notation and coefficient domains, improve transitions, and retain the proof hypotheses and limitations.
- [x] Bind current source maps and independent reviews to the final TeX, build the PDF and inspect every page.
- [x] Preserve all {{PRIOR_FILE_COUNT}} files from the previous consolidated archive, including superseded manuscript and review versions.

## Research questions still open

- [ ] **General singular persistence.** Treat Jacobians that remain rank-deficient over the fraction field, including higher obstructions and criteria for compatible infinite branches under deformation. A successful next-step lift alone does not ensure continuation at all later levels.
- [ ] **Exact higher differences.** Determine \(v_2(\Delta_u^kU_j(n))\) for \(k\ge2\), including cancellation and zero cases.
- [ ] **Least periods beyond \(N=4\).** Prove exact displacement and minimal-period results for additional primes and packet parameters; sufficient periods alone do not establish minimality.
- [ ] **General affine Mahler-kernel valuations.** Determine exact valuations for
  \[
  \Theta_{M,s}(r,k)=[z^r](1+z)^s((1+z)^M-1)^k
  \]
  beyond the special families already derived, accounting for cancellation.
- [ ] **Exact classical tail values at arbitrary rows.** Strengthen the sharp uniform exponent and known summand weights to a general exact valuation of the full tail.
- [ ] **Native 13.2 in full generality.** Specify the seed category and allowed presentation changes, construct an intrinsic finite obstruction, and prove that the encoding preserves the intended lifts. The commutative-algebra progress does not yet cover the unrestricted seed program.
- [ ] **Native 13.3 in full generality.** Specify the local objects, restricted product, compatibility maps, category and universal property; distinguish global reconstruction from completion. Then prove the required passage through levels and any global descent condition.

## Recovery and interface tasks

- [ ] Recover and match the remaining historical odd-prime edge formulas, binary carry forms and full derivations. Partial source windows and the reconstructed Annals text are preserved with their provenance.
- [ ] Extend or compare every historical rectangular chart interface with the current ambient-field analytic theorem. The earlier integer-coefficient interfaces retain their original hypotheses.
- [ ] Recover original historical TeX, figure-generation sources and the complete experiment package if they become available. Their absence remains a historical limitation, not a missing step in the proved Nishibuchi result.

The current manuscript and [statement index](consolidation/audit/STATEMENT_INDEX.json) are the entry points for the proved results. The [completeness review](consolidation/editorial/COMPLETENESS_REVIEW.json) records the checked coverage and its limits. Earlier detailed checklists remain in the historical archive.
