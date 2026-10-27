# Paper IX: proved results and remaining work

**Author: Komorebi P. — 8 September 2026.**

The stated Nishibuchi Conjecture 3.9 is resolved in the checked parameter range, which is its full stated range. The unchecked items below are further strengthenings and the broader native conjectures. They are not missing steps in that completed proof.

## Notation

Write
\[
U_{N,j}(n)=E_{Nn}^{(N,j)}=j!C_{N,j}(n),\qquad
\Delta_u f(n)=f(n+u)-f(n).
\]
For \(N=4\), abbreviate \(U_j=U_{4,j}\), with \(0\le j<4\). A packet shift \(u\) is a degree shift \(Nu\). Lower valuation bounds include zero; exact valuation claims explicitly exclude or prove nonzero differences.

## Completed in Lean

- [x] **Full stated Nishibuchi conjecture.** For every prime \(p\), positive \(m\) with \(m\mid p-1\) or \(m=2\), and \(j<mp\), the original coefficients are \(p\)-integral. With \(q=\operatorname{lcm}(2,p-1)\),
  \[
  E_{mpn+qp^r}^{(mp,j)}\equiv E_{mpn}^{(mp,j)}\pmod{p^r}
  \quad(r\ge1,\ n\ge r).
  \]
  On the divisor branch, the sufficient starting condition improves to \(r\le mn\).

- [x] **Amplification by the step valuation.** On the divisor branch, put \(h=(p-1)/m\). The checked bound is
  \[
  v_p\!\left(\Delta_{uh}^{k}U_{mp,j}(n)\right)
  \ge \min\{k(1+v_p(u)),mn\}\quad(u>0,\ k,n\ge0).
  \]
  For \(N=4\), the row cap is removed:
  \[
  v_2\!\left(\Delta_u^{k}U_j(n)\right)
  \ge k(1+v_2(u))+v_2(j!)
  \quad(u>0,\ k,n\ge0).
  \]
  The zero-step case is separately covered by the zero-safe formal statements; positive-order differences then vanish.

- [x] **Exact dyadic displacements and all positive packet periods.** With
  \((d_0,d_1,d_2,d_3)=(1,1,5,3)\),
  \[
  U_j(n+T)-U_j(n)\ne0,\qquad
  v_2\!\left(U_j(n+T)-U_j(n)\right)=v_2(T)+d_j
  \quad(n\ge0,\ T>0).
  \]
  The least positive packet period modulo \(2^r\) is
  \[
  P_j(r)=2^{\max(0,r-d_j)}\quad(r\ge0),
  \]
  and every positive period is exactly a positive multiple of \(P_j(r)\).
  This classifies packet periods, without asserting a least period among arbitrary off-support degree shifts.

- [x] **Optimal classical dyadic edge tower.** For the classical signed Euler coefficients \(E_{2n}\) of \(\operatorname{sech}z\), the existing depth-\(M\) approximation \(T_M(n)\) satisfies
  \[
  E_{2n}-T_M(n)\in2^{4M+3}\mathbb Z_2,
  \qquad v_2\!\left(E_{2M+2}-T_M(M+1)\right)=4M+3.
  \]
  Individual summand weights and row-sensitive tail lower bounds are also checked. This is the classical \(N=2\) family, separate from the four \(N=4\) packets.

- [x] **Finite affine obstruction.** Every finite integer-linear system at an actual solution modulo \(q^L\), for every \(q>0\) and \(L\ge0\), has a finite residual cokernel class. Its vanishing is equivalent to a next-level lift with the same lower residue.

- [x] **Shared-correction quotient — completed in the preceding block.** For modules over a commutative ring and linear maps \(J:U\to V\), \(K:U\to W\), define
  \[
  C=U/(\ker J+\ker K).
  \]
  There are well-defined surjective linear labels \(\alpha:\operatorname{im}J\to C\), \(\beta:\operatorname{im}K\to C\), and
  \[
  \operatorname{im}(J,K)\cong
  \operatorname{im}J\times_C\operatorname{im}K.
  \]
  Equivalently, \([u]=[v]\) exactly when some \(w\) satisfies \(Jw=Ju\) and \(Kw=Kv\). The paired universal factorization property is proved. Either finite target makes \(C\) finite, even when \(U\) is infinite.

- [x] **Actual joint affine lifting criterion — completed in the preceding block.** For two finite affine integer systems with the same unknown vector, individually valid corrections yield classes in a fixed finite \(C\). A shared next-level lift exists exactly when those classes agree. The proof derives residuals from the original lower-level congruences and proves independence of the individual correction choices. It includes composite \(q\), \(q=1\), and \(L=0\).


- [x] **Continuous dyadic isometric bijections — completed in the preceding isometry block.** For every \(j<4\), there is a unique isometric bijection \(G_j:\mathbb Z_2\to\mathbb Z_2\) satisfying
  \[
  G_j(n)=\frac{U_j(n)-j!}{2^{d_j}}\quad(n\in\mathbb N).
  \]
  It fixes zero and is unique among all continuous maps with those values. Every target has exactly one preimage. A generic checked theorem proves the same extension principle for every prime \(p\) whenever the natural samples preserve the induced p-adic distance.

- [x] **Original coefficient extensions and their exact images — completed in the preceding isometry block.** Define
  \[
  \widetilde U_j(x)=j!+2^{d_j}G_j(x).
  \]
  It agrees with \(U_j(n)\) on every natural packet index and satisfies
  \[
  |\widetilde U_j(x)-\widetilde U_j(y)|_2=2^{-d_j}|x-y|_2.
  \]
  Its exact image is \(j!+2^{d_j}\mathbb Z_2\), with a unique preimage for each point. The normalized maps are metric isometries; additivity is not asserted. An explicit checked control gives \(G_0(1)=-1\), \(G_0(2)=34\), hence failure of additivity.

- [x] **Actual polynomial Taylor formula — completed in the preceding polynomial block.** For every finite-variable integer polynomial and integer step \(a\),
  \[
  a^2\mid P(x+at)-P(x)-a\sum_i\partial_iP(x)t_i.
  \]
  At depth \(L\ge1\), the remainder vanishes modulo \(q^{L+1}\) when \(a=q^L\).

- [x] **Fixed-presentation finite polynomial obstruction — completed in the preceding polynomial block.** For every \(q>0\), \(L\ge1\), finite system \(F\), and lower root \(x\), put \(r_x=F(x)/q^L\) and \(J_x=\rho_q\circ DF(x)\). Then
  \[
  \mathcal O_x=(\mathbb Z/q\mathbb Z)^e/\operatorname{im}J_x,
  \qquad [\rho_q(r_x)]=0
  \iff \exists y\equiv x\pmod{q^L}:F(y)\equiv0\pmod{q^{L+1}}.
  \]
  The quotient is finite. The theorem derives the residual from the actual congruence and permits composite moduli and modulus one. No surjectivity premise is imposed on the Jacobian.

- [x] **Polynomial representative independence — completed in the preceding polynomial block.** Changing \(x\) by \(q^Ls\) leaves the reduced Jacobian unchanged and changes the residual digit by \(J_xs\). The same quotient therefore carries the same obstruction class. This is independence of integer representatives within a fixed presentation.

- [x] **Actual shared polynomial corrections — completed in the preceding polynomial block.** For two systems with the same variables, define \(\mathcal C_x=\mathbb Z^d/(\ker J_x+\ker K_x)\). Given separately valid corrections \(u,v\), a single next lift of both systems exists exactly when \([u]=[v]\) in this finite quotient. Each label is independent of the selected valid correction. An unconditional version includes individual solvability in the criterion.

- [x] **Correction-digit torsors and exact polynomial lift counts — completed in this block.** For prime \(p\), depth \(L\ge1\), a lower root \(x\), and the actual induced Jacobian \(A_x=DF(x)\bmod p\), put \(\rho_x=\operatorname{rank}_{\mathbb F_p}A_x\). Every nonempty correction-digit fiber is an explicitly formalized torsor for \(\ker A_x\). It is in bijection with the actual next-level polynomial residue lifts, so
  \[
  \#\mathcal L_{x,L}=
  \begin{cases}p^{d-\rho_x},&o_x=0,\\0,&o_x\ne0,\end{cases}
  \qquad\#\mathcal O_x=p^{e-\rho_x}.
  \]
  The old integer-domain obstruction is identified with the finite-field cokernel by a class-preserving equivalence. The count is of distinct residue classes modulo \(p^{L+1}\), not integer correcting vectors.

## Clear routes still awaiting formalization

| Status | Target | Exact work left |
|---|---|---|
| [ ] Beyond the completed one-step theorem | **Compatibility through a specified polynomial tower.** | Define level objects and transition maps. Use the checked stability of the reduced Jacobians, then prove transport of the actual residual labels and the conditions needed for a compatible infinite lift. A one-step lift does not ensure continuation. |
| [ ] Recovery/formalization task | **Remaining historical edge identities and carry forms.** | Inventory the exact older odd-prime formulas and binary digit-sum form of the checked binomial weights. Recovered partial source windows and the available reconstructed Annals text are included with their provenance. |

The continuous isometry, polynomial Taylor bridge, fixed-presentation obstruction, one-step shared-polynomial application, correction torsor and exact prime-field counts are now formalized. Infinite compatibility and presentation invariance remain separate tasks.

## Research questions still open

- [ ] **Exact higher-order valuations.** Determine \(v_2(\Delta_u^kU_j(n))\) for \(k\ge2\), including zero cases. Existing all-order bounds and exact first displacements do not rule out cancellation between higher differences. Start with \(k=2\) in one address.
- [ ] **Least periods beyond \(N=4\).** Obtain exact displacements and least-period classifications for selected additional primes and parameters. The general sufficient-period theorem alone does not establish minimality.
- [ ] **General affine Mahler-kernel valuations.** For
  \[
  \Theta_{M,s}(r,k)=[z^r](1+z)^s\bigl((1+z)^M-1\bigr)^k,
  \]
  find exact valuation rules beyond the special families already derived. Cancellation prevents a general rule based only on the minimum term valuation. The new affine lifting quotient does not solve this distinct kernel problem.
- [ ] **Exact classical tail valuations at arbitrary rows.** The uniform exponent \(4M+3\) is optimal and the individual weights are known. The valuation of their sum can increase through cancellation; the general exact row formula remains open.

## Original native conjectures: definitions and proof obligations

- [ ] **Native 13.2 in full generality.** Specify the seed category, allowed changes of presentation, lift functor, obstruction object and meaning of finite/canonical. Prove that the seed-to-algebra or seed-to-linear construction preserves the actual lifts. The fixed-presentation affine and polynomial results do not establish invariance under arbitrary changes of presentation; adding a redundant zero equation can change a raw cokernel.
- [ ] **Native 13.3 in full generality.** Specify \(X\), its local objects, restricted-product conditions, maps to \(C\), the category, and the desired universal property. Decide whether the target is global or completed. Apply the new linear theorem only after proving that the actual compatibility relation is represented by shared corrections, then establish the required passage through levels and any global descent condition.

The new quotient has a precise universal property in the category of modules. It does not yet identify the unrestricted native objects with that model. In particular, the joint image retains corrections only modulo \(\ker J\cap\ker K\); it is not a reconstruction of the original correction module without accounting for that kernel. The previously documented obstruction to recovering global integers from a continuous Hausdorff equality locus also remains relevant.

## Suggested next block

Formalize **lifting through all levels under a surjective reduced Jacobian**. Along a fixed residue class the reduced Jacobian remains constant. Surjectivity then makes every residual digit correctable. Specify the actual level objects and transition maps, prove compatible recursive lifting, and use completeness to construct the p-adic polynomial root. A general one-step lift without this hypothesis can still stop at a later level.

## Evidence locations

- Latest torsor/count block: `polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md`, `polynomial_counts/formalization/`, `polynomial_counts/verification/polynomial_counts_verification.json`, and `polynomial_counts/INDEPENDENT_PROOF_AUDIT.md`.
- Previous polynomial block: `polynomial_lifting/POLYNOMIAL_LIFTING.md`, `polynomial_lifting/formalization/`, `polynomial_lifting/verification/polynomial_verification.json`, and `polynomial_lifting/INDEPENDENT_PROOF_AUDIT.md`.
- Previous isometry block: `strengthening/formalization/`, the combined gate in `strengthening/verification/continuation_verification.json`, and `isometry/INDEPENDENT_PROOF_AUDIT.md`.
- Shared-correction block: `shared_correction/formalization/`, `shared_correction/verification/shared_verification.json`, and `shared_correction/INDEPENDENT_PROOF_AUDIT.md`.
- Exact periods and sharp towers: `strengthening/formalization/`, with the prior report in `review/EXACT_DYADIC_PERIODS_README.md`.
- Original completion: preserved `baseline/` source archive and source-statement review.
- Earlier affine and polynomial work: `native/Native_Conjectures_Progress.md` and `native/lean/`.

The historical notes retain their original dates and statuses. This checklist is the current status reference.
