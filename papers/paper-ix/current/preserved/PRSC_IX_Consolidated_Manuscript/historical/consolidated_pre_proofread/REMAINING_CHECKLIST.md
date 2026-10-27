# Paper IX: proved results and remaining work

**Current manuscript consolidation: complete. The local regularity proof retains its verified status.**

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

- [x] **Correction-digit torsors and exact polynomial lift counts — completed in the preceding count block.** For prime \(p\), depth \(L\ge1\), a lower root \(x\), and the actual induced Jacobian \(A_x=DF(x)\bmod p\), put \(\rho_x=\operatorname{rank}_{\mathbb F_p}A_x\). Every nonempty correction-digit fiber is an explicitly formalized torsor for \(\ker A_x\). It is in bijection with the actual next-level polynomial residue lifts, so
  \[
  \#\mathcal L_{x,L}=
  \begin{cases}p^{d-\rho_x},&o_x=0,\\0,&o_x\ne0,\end{cases}
  \qquad\#\mathcal O_x=p^{e-\rho_x}.
  \]
  The old integer-domain obstruction is identified with the finite-field cokernel by a class-preserving equivalence. The count is of distinct residue classes modulo \(p^{L+1}\), not integer correcting vectors.

- [x] **Compatible smooth polynomial towers and exact p-adic roots — completed in the preceding tower block.** For prime \(p\), \(L\ge1\), \(F(x)\equiv0\pmod{p^L}\), and a surjective actual reduced Jacobian \(A_x:\mathbb F_p^d\to\mathbb F_p^e\), there are a compatible integer tower \(z_n\) and \(a\in\mathbb Z_p^d\) with
  \[
  z_0=x,\quad F(z_n)\equiv0\pmod{p^{L+n}},\quad
  z_{n+1}\equiv z_n\pmod{p^{L+n}},\quad z_n\to a,
  \]
  \[
  F(a)=0,\qquad a-z_n\in p^{L+n}\mathbb Z_p^d.
  \]
  The reduced Jacobian is exactly constant along the tower. Every level has \(p^{d-e}\) next-level residue lifts, and the obstruction group is trivial. The integer tower theorem also covers positive composite moduli; the p-adic completion and rank counts use prime \(p\). Only the initial Jacobian is assumed surjective.

- [x] **Square polynomial root uniqueness — completed in the perturbation block.** If \(d=e\), \(L\ge1\), \(F(x)\equiv0\pmod{p^L}\), and the actual reduced Jacobian \(A_x\) is surjective, then
  \[
  \exists!\,a\in x+p^L\mathbb Z_p^d:\quad F(a)=0.
  \]
  Any two exact roots in this residue ball agree at every precision. This is uniqueness among arbitrary p-adic roots, extending the earlier uniqueness of the limit of a chosen tower.

- [x] **Actual coefficient perturbations — completed in the perturbation block.** For integer polynomial systems \(G=F+cH\), \(p^L\mid c\) preserves a lower root modulo \(p^L\), and \(p\mid c\) preserves the actual reduced Jacobian. Consequently smooth p-adic root existence at depth \(L\ge1\) persists. The identities are derived from the actual polynomial coefficients and partial derivatives.

- [x] **Nearby perturbed roots — completed in the perturbation block.** Let \(M\ge1\), \(p^M\mid c\), \(G=F+cH\), and suppose \(F(a)=0\), \(a\equiv x\pmod p\), and \(A_x\) is surjective. Then
  \[
  \exists b\in\mathbb Z_p^d:\quad G(b)=0,\qquad b-a\in p^M\mathbb Z_p^d.
  \]
  This existence statement permits rectangular systems.

- [x] **Unique square-root stability — completed in the perturbation block.** If \(d=e\), \(M\ge L\ge1\), \(p^M\mid c\), and \(a,b\in x+p^L\mathbb Z_p^d\) satisfy \(F(a)=0\), \((F+cH)(b)=0\), with \(A_x\) surjective, then
  \[
  b\equiv a\pmod{p^M}.
  \]
  Starting only with the lower root, Lean constructs the original root and its unique perturbed root in the base ball with this precision. The bound need not be an exact valuation, and no additional digit is promised.

- [x] **Local polynomial surjectivity and square inverse — parameter-chart block.** For prime \(p\), \(L\ge1\), integer polynomial \(F\), integer \(x\), and surjective \(DF(x)\bmod p\),
  \[
  F(x+p^L\mathbb Z_p^d)=F(x)+p^L\mathbb Z_p^e.
  \]
  Targets are arbitrary p-adic vectors. In the square case this evaluation map is a homeomorphism. For \(a,b\in x+p\mathbb Z_p^d\) and \(N\ge0\),
  \[
  F(a)\equiv F(b)\pmod{p^N}\iff a\equiv b\pmod{p^N}.
  \]
  No lower-root hypothesis is needed for these local-map statements.

- [x] **Continuous rectangular parameter charts — parameter-chart block.** For prime \(p\), let \(F\in\mathbb Z[X_1,\ldots,X_{e+q}]^e\), \(L\ge1\), \(F(x)\equiv0\pmod{p^L}\), and \(DF(x)\bmod p\) be surjective. A suitable coordinate permutation \(\sigma\), written \(\sigma z=(y,t)\), gives a homeomorphism
  \[
  h:T\xrightarrow{\ \sim\ }\{z\in x+p^L\mathbb Z_p^{e+q}:F(z)=0\},
  \qquad T=\operatorname{free}(\sigma x)+p^L\mathbb Z_p^q.
  \]
  Its inverse is actual selected-coordinate projection. It gives one root for every p-adic parameter and covers every root in the original ball. For \(N\ge0\),
  \[
  h(t)\equiv h(u)\pmod{p^N}\iff t\equiv u\pmod{p^N}.
  \]
  The theorem supplies a suitable minor; a prescribed coordinate choice can fail. Since \(x\) is an approximate root, the root over its free coordinates need not be \(x\).

- [x] **Weighted nonlinear lifting — preceding block.** For prime \(p\), let \(R=\mathbb Z_p\), \(F\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and \(J=DF(a)\). If
  \[
  J\in\operatorname{GL}_d(\mathbb Q_p),\qquad p^sJ^{-1}\in M_d(R),\qquad
  F(a)\in p^rR^d,\qquad r>2s,
  \]
  then
  \[
  \exists!\,b\in a+p^{s+1}R^d:\ F(b)=0,
  \qquad b-a\in p^{r-s}R^d.
  \]
  Uniqueness holds throughout the full stated ball. The same exponent \(s\) is retained. This includes arbitrary p-adic coefficients and centers, every prime, and finite square dimension. The integral certificate \(AJ=JA=p^sI\) is proved equivalent to the fraction-field inverse condition. The strict threshold and absence of a universally available extra precision digit have explicit Lean controls.

- [x] **Integral polynomial Taylor and contraction — preceding block.** Over any commutative ring, Taylor expansion at \(a+cu\) has one polynomial remainder \(c^2Q(u)\), with \(Q(0)=0\). Over \(\mathbb Z_p\), actual polynomial evaluation is 1-Lipschitz. The map \(u\mapsto c+pH(u)\) has a unique fixed point, which inherits every divisibility bound of \(c\) when \(H(0)=0\).

- [x] **Weighted perturbation and first-order root motion — preceding block.** For prime \(p\), let \(R=\mathbb Z_p\), \(F,H\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), \(F(a)=0\), and \(J=DF(a)\). Suppose \(J\in\operatorname{GL}_d(\mathbb Q_p)\), \(p^sJ^{-1}\in M_d(R)\), and \(M>2s\). Then \(G=F+p^MH\) has exactly one root \(b\) in \(a+p^{s+1}R^d\), with
  \[
  b-a\in p^{M-s}R^d,\qquad
  b-a=-p^MJ^{-1}H(a)+\varepsilon,\qquad
  \varepsilon\in p^{2M-3s}R^d.
  \]
  The Jacobian is the original one. Root construction, full-ball uniqueness, and the integral error vector are all supplied by the theorem. The dyadic quadratic control realizes error depth exactly \(2M-3s\), so an extra digit cannot uniformly be guaranteed. This includes arbitrary p-adic coefficients and centers, every prime, and finite square dimension.

- [x] **Prescribed-parameter polynomial obstruction and exact fibers — preceding block.** For \(q>0\), \(L\ge1\), \(m\) solved variables, \(k\) parameter variables, \(e\) equations, and an actual lower integer polynomial root \(x\), derive \(r=q^{-L}F(x)\). Let \(J\) and \(K\) be the actual reduced Jacobian blocks. For each prescribed parameter digit \(v\), define
  \[
  \mathcal C_x=(\mathbb Z/q\mathbb Z)^e/\operatorname{im}J,
  \qquad o_x(v)=[\bar r+Kv].
  \]
  The actual next-level residue lifts \(\mathcal L_v\) with that parameter digit satisfy
  \[
  \mathcal L_v\ne\varnothing\iff o_x(v)=0,
  \qquad \mathcal L_v\cong\{u:Ju=-\bar r-Kv\}.
  \]
  Every nonempty fiber is a checked torsor for \(\ker J\), including positive composite moduli. For prime \(p\), put \(\rho=\operatorname{rank}_{\mathbb F_p}J\). Then
  \[
  \#\mathcal L_v=\begin{cases}p^{m-\rho},&o_x(v)=0,\\0,&o_x(v)\ne0,\end{cases}
  \qquad \#\mathcal C_x=p^{e-\rho}.
  \]
  The same derived residual supports all parameter digits. These are counts of actual residue classes. No full-rank assumption is imposed. The criterion includes \(q=1\) and zero dimensions; the rank formulas require a prime field.

- [x] **Compatible towers with prescribed parameter paths — preceding block.** Let \(q>0\), \(L\ge1\), \(F\in\mathbb Z[Y_1,\ldots,Y_m,T_1,\ldots,T_k]^e\), and \(F(x)\equiv0\pmod{q^L}\). Suppose the actual solved block \(J_x=D_YF(x)\bmod q\) is surjective. For every integer path with
  \[
  t(0)=\operatorname{free}(x),\qquad t(n+1)-t(n)\in q^{L+n}\mathbb Z^k,
  \]
  Lean constructs a single integer tower satisfying
  \[
  z(0)=x,\quad\operatorname{free}(z(n))=t(n),\quad
  F(z(n))\in q^{L+n}\mathbb Z^e,\quad
  z(n+1)-z(n)\in q^{L+n}\mathbb Z^{m+k}.
  \]
  The parameter equality is exact in integers. The full actual reduced Jacobian stays fixed, and every earlier residue is retained. Only initial solved-block surjectivity is assumed. Integer towers include positive composite bases and \(q=1\).

- [x] **Arbitrary prescribed p-adic endpoints and exact branching — preceding block.** For prime \(p\) and every \(\tau\in\operatorname{free}(x)+p^L\mathbb Z_p^k\), Lean constructs the integer parameter path, polynomial tower, and endpoint \(b\), with
  \[
  z(n)\to b,\quad F(b)=0,\quad\operatorname{free}(b)=\tau,\quad
  b-z(n)\in p^{L+n}\mathbb Z_p^{m+k}\quad(n\ge0).
  \]
  At every stage and for every prescribed next parameter digit \(v\), there are exactly \(p^{m-e}\) actual next-level residue lifts. Surjectivity proves \(e\le m\). If \(m=e\), every parameter has exactly one root in the initial ball, independent of all path and tower choices. The checked \(F(Y_1,Y_2,T)=Y_1\) example rules out extending this uniqueness to rectangular solved blocks. All prime statements include \(p=2\).

- [x] **Simultaneous coefficient and parameter deformation — preceding block.** Let \(R=\mathbb Z_p\), \(F,H\in R[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\), \(a=(y_0,t_0)\), and \(F(a)=0\). Put \(J=D_YF(a)\), \(K=D_TF(a)\). If
  \[
  J\in\operatorname{GL}_e(\mathbb Q_p),\qquad p^sJ^{-1}\in M_e(R),\qquad M>2s,
  \]
  then for every \(v\in R^k\), setting \(\tau=t_0+p^Mv\) and \(G=F+p^MH\), there is exactly one \(y\in y_0+p^{s+1}R^e\) with \(G(y,\tau)=0\). It satisfies
  \[
  y-y_0\in p^{M-s}R^e,\qquad
  y-y_0=-p^MJ^{-1}\bigl(H(a)+Kv\bigr)+\varepsilon,
  \qquad\varepsilon\in p^{2M-3s}R^e.
  \]
  The proof constructs the actual augmented polynomial system, proves its two-sided inverse certificate with the same exponent \(s\), and imposes no hypothesis on the perturbed Jacobian. It covers all primes, arbitrary integral p-adic coefficients and centers, and zero finite dimensions. Actual dyadic controls detect an omitted or reversed parameter term. A parameter-only quadratic example attains error depth exactly \(2M-3s\), ruling out a uniform extra digit.

- [x] **Local analyticity and differentiability — current block, both parts complete.** Let \(p\) be any prime, \(e,k\ge0\), \(F\in\mathbb Q_p[Y_1,\ldots,Y_e,T_1,\ldots,T_k]^e\), and \(a=(y_0,t_0)\) satisfy \(F(a)=0\). Write \(J=D_YF(a)\), \(K=D_TF(a)\), and assume \(J\in\operatorname{GL}_e(\mathbb Q_p)\). There are open neighborhoods \(t_0\in U\subseteq\mathbb Q_p^k\), \(y_0\in V\subseteq\mathbb Q_p^e\), and a map \(\psi:\mathbb Q_p^k\to\mathbb Q_p^e\), analytic near every point of \(U\), such that
  \[
  \psi(t_0)=y_0,\quad\psi(U)\subseteq V,\quad
  F(y,t)=0\iff y=\psi(t)\quad(t\in U,\ y\in V),
  \qquad D\psi(t_0)=-J^{-1}K.
  \]
  The derivative is certified as a strict Fréchet derivative. Actual polynomial evaluation, actual evaluated formal partial derivatives, and the full augmented inverse are connected in the proof; analyticity and the derivative identity are conclusions. The core works over every complete nontrivially normed field. An explicit specialization includes arbitrary integral p-adic coefficients and centers by evaluating them in the ambient field. These local neighborhoods have no new explicit uniform radius; the earlier weighted radii remain separate checked results.

- [x] **Regularity of supplied continuous root selections — current block.** If \(g\) is continuous at \(t_0\), \(g(t_0)=y_0\), and \(F(g(t),t)=0\) for all sufficiently nearby \(t\), then \(g\) has the same germ as \(\psi\), is analytic at \(t_0\), and has strict derivative \(-J^{-1}K\). If \(g\) is a continuous exact root selection on an open set and \(D_YF(g(t),t)\) is invertible at every point, then it is analytic throughout that set and
  \[
  Dg(t)=-\bigl(D_YF(g(t),t)\bigr)^{-1}D_TF(g(t),t).
  \]
  This comparison is for ambient field-valued root selections. A separate formal comparison with each historical subtype-valued chart has not been added.

- [x] **Manuscript consolidation — current edition.** The main 45-page manuscript integrates the original arithmetic framework and the subsequent completed blocks, gives proof explanations, uses consistent notation and cross-references, and links 57 mapped statements to 178 actual source declarations. The original manuscripts, all mathematical sources, and every previous release file are retained. Consolidation changes exposition and reporting; it adds no Lean theorem and does not claim a new rebuild of every earlier proof. Historical material that lacks full recovery or matching formal coverage remains explicitly identified.

## Clear routes still awaiting formalization

| Status | Target | Exact work left |
|---|---|---|
| [ ] Recovery/formalization task | **Remaining historical edge identities and carry forms.** | Inventory the exact older odd-prime formulas and binary digit-sum form of the checked binomial weights. Recovered partial source windows and the available reconstructed Annals text are included with their provenance. |

The square weighted lifting and first-order motion theorems have arbitrary integral p-adic coefficients and centers. The prescribed-parameter finite-lifting theorem uses integer polynomial coefficients and integer lower-root representatives. The earlier rectangular chart interfaces retain integer coefficients and integer centers with arbitrary p-adic roots and parameters. The new ambient-field theorem proves local analyticity and differentiability for arbitrary p-adic coefficients with an invertible solved block. Generalizing every historical rectangular interface, or proving identity with each earlier subtype-valued chart, remains an interface task. First-order root motion and simultaneous coefficient/parameter response are now checked for square solved systems with arbitrary integral p-adic coefficients and centers.

## Research questions still open

- [ ] **General singular deformation towers.** The checked weighted criterion covers Jacobians invertible over the fraction field. Rationally rank-deficient Jacobians, higher obstructions, and general criteria ensuring compatible infinite branches remain open in this program.
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

## Status after consolidation

The manuscript is now consolidated around the proved results. Read `manuscript/consolidated/Paper_IX_Consolidated.pdf` and its editable TeX sources. The section on remaining questions makes the boundary between completed results and research extensions explicit.

General singular persistence, Native 13.2 and 13.3, sharper arithmetic classifications, historical formula recovery and explicit comparison with every older chart interface remain open. These do not prevent the consolidated proved-results manuscript from being complete within its stated scope.

## Evidence locations

- Current consolidated manuscript: `manuscript/consolidated/`; portable statement maps and audit: `consolidation/audit/STATEMENT_INDEX.json`, `STATEMENT_INDEX.csv`, `MANUSCRIPT_REVIEW.json`, and `PDF_VISUAL_REVIEW.json`.

- Current analytic regularity: `polynomial_regularity/ANALYTIC_REGULARITY.md`, `polynomial_regularity/formalization/`, `polynomial_regularity/verification/polynomial_regularity_verification.json`, and `polynomial_regularity/audit/ROUTE_AUDIT.md`.

- Previous joint deformation: `polynomial_joint_motion/JOINT_DEFORMATION.md`, `polynomial_joint_motion/formalization/`, `polynomial_joint_motion/verification/polynomial_joint_motion_verification.json`, and `polynomial_joint_motion/audit/ROUTE_AUDIT.md`.

- Previous prescribed-parameter towers: `polynomial_parameter_towers/PRESCRIBED_PARAMETER_TOWERS.md`, `polynomial_parameter_towers/formalization/`, `polynomial_parameter_towers/verification/polynomial_parameter_towers_verification.json`, and `polynomial_parameter_towers/audit/ROUTE_AUDIT.md`.

- Previous prescribed-parameter block: `polynomial_prescribed/PRESCRIBED_PARAMETER_LIFTING.md`, `polynomial_prescribed/formalization/`, `polynomial_prescribed/verification/polynomial_prescribed_verification.json`, and `polynomial_prescribed/audit/ROUTE_AUDIT.md`.

- Previous first-order block: `polynomial_motion/FIRST_ORDER_ROOT_MOTION.md`, `polynomial_motion/formalization/`, `polynomial_motion/verification/polynomial_motion_verification.json`, and `polynomial_motion/audit/ROUTE_AUDIT.md`.

- Previous weighted block: `polynomial_weighted/WEIGHTED_LIFTING.md`, `polynomial_weighted/formalization/`, `polynomial_weighted/verification/polynomial_weighted_verification.json`, and `polynomial_weighted/audit/ROUTE_AUDIT.md`.

- Previous chart block: polynomial_charts/POLYNOMIAL_PARAMETER_CHARTS.md, polynomial_charts/formalization/, polynomial_charts/verification/polynomial_charts_verification.json, and polynomial_charts/INDEPENDENT_PROOF_AUDIT.md. Recovery provenance is in polynomial_charts/RECOVERY_RECORD.md.

- Previous uniqueness/perturbation block: `polynomial_deformation/POLYNOMIAL_DEFORMATION.md`, `polynomial_deformation/formalization/`, `polynomial_deformation/verification/polynomial_deformation_verification.json`, and `polynomial_deformation/INDEPENDENT_PROOF_AUDIT.md`.
- Recovered perturbation route and written weighted proofs: `research/perturbation/Paper_IX_Perturbation_Deformation_Bridge.md`. Its pre-formalization status is historical; the current checked status is this checklist.
- Preceding tower/root block: `polynomial_towers/PADIC_TOWERS.md`, `polynomial_towers/formalization/`, `polynomial_towers/verification/polynomial_towers_verification.json`, and `polynomial_towers/INDEPENDENT_PROOF_AUDIT.md`.
- Previous torsor/count block: `polynomial_counts/POLYNOMIAL_LIFT_COUNTS.md`, `polynomial_counts/formalization/`, `polynomial_counts/verification/polynomial_counts_verification.json`, and `polynomial_counts/INDEPENDENT_PROOF_AUDIT.md`.
- Previous polynomial block: `polynomial_lifting/POLYNOMIAL_LIFTING.md`, `polynomial_lifting/formalization/`, `polynomial_lifting/verification/polynomial_verification.json`, and `polynomial_lifting/INDEPENDENT_PROOF_AUDIT.md`.
- Previous isometry block: `strengthening/formalization/`, the combined gate in `strengthening/verification/continuation_verification.json`, and `isometry/INDEPENDENT_PROOF_AUDIT.md`.
- Shared-correction block: `shared_correction/formalization/`, `shared_correction/verification/shared_verification.json`, and `shared_correction/INDEPENDENT_PROOF_AUDIT.md`.
- Exact periods and sharp towers: `strengthening/formalization/`, with the prior report in `review/EXACT_DYADIC_PERIODS_README.md`.
- Original completion: preserved `baseline/` source archive and source-statement review.
- Earlier affine and polynomial work: `native/Native_Conjectures_Progress.md` and `native/lean/`.

The historical notes retain their original dates and statuses. This checklist is the current status reference.
