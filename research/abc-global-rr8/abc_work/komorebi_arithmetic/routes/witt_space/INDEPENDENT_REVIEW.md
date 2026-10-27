# Independent proof audit: protected local arithmetic tower

**Normalized claim.** For every prime $p$, including 2, and every $N\geq1$, the explicitly declared finite diagrams have the extension fibers stated in Theorems 2–3; the protected carry quotient injects into the actual additive residual quotient; these data reduce naturally with precision; and the Teichmuller digit bijections transport the rings $\mathbf Z/p^N\mathbf Z$ to a compatible digit tower with inverse limit $\mathbf Z_p$. Lemma 1, equations (1)–(15), and the local nonsplitting conclusions are included in this claim.

**Primary verdict: proved as written**, for the final revision
`cf6854a9c966c3fcbbccb9bd2035c66a31642d532da3fbed15e3bf8f054188bb`.

This is a verdict on the local construction specified above. It is not an audit of IUT, a proof of global ABC, a construction of the general Witt functor, a novelty determination, or verification of earlier Lean receipts.

## 1. Claim card and dependency graph

The coefficient sequence is the exact sequence of additive groups

$

0\longrightarrow K_N=R_{N-1}\xrightarrow{i_N:z\mapsto pz}
R_N\xrightarrow{r_N}\mathbf F_p\longrightarrow0,

$

with $R_0=0$. The correction domain is precisely the additive group of functions $b:k\to K_N$ satisfying $b(0)=b(1)=0$. The variance is contravariant: for $f:v\to w$, the restriction has type $F_N(w)\to F_N(v)$, and its defect is in $F_N(v)$. All finite products include identities and every distinct composite arrow.

The proof has the following dependency structure:

1. The binomial congruence gives the finite sections $t_N$, their multiplicativity and precision compatibility.
2. The principal-unit argument gives uniqueness of the normalized multiplicative section.
3. The exact coefficient sequence and $t_N$ give the carries, cocycle identity, correction formula, and carry naturality.
4. Telescoping gives the functional $L_N$, hence nonvanishing for $N\geq2$.
5. The explicitly presented free category and protected seed identify additive extensions and give the injection of (7) into (9).
6. Adding carry coordinates and multiplication relations gives the unique protected Set-valued realization by item 2.
7. The declared reduction maps give natural transformations, maps on the protected quotients, and coherent obstruction classes.
8. Repeated application of the exact coefficient sequence gives the digit bijections. Their precision square gives the ring tower and inverse-limit isomorphism.
9. The direct component argument for injectivity of multiplication by $p$ on the inverse limit excludes an additive residue section there.

Items 1–9 are internally proved elementary implications. The framework source supplies definitions and their typing, not an unproved arithmetic input. The notation $\mathbf Z_p=\varprojlim_N R_N$ is the inverse-limit convention used in (13). No dependency cycle was found.

## 2. Obligation matrix

| Obligation | Status | Finding |
| --- | --- | --- |
| Formula (1), representative independence, fixed points and reductions | passed | The iterated binomial congruence has the required exponent and modulus, including $p=2$. |
| Lemma 1 | passed | Units and the $p-1$ argument are correctly justified; $p=2$ gives exponent one. |
| Coefficient group, division by $p$, cocycle and correction law | passed | Every division uses the inverse of the additive injection $i_N$, not inversion of $p$ in $R_N$. |
| Functional (8), protected and unit-unprotected nonsplitting | passed | The telescope is exact in $K_N$; reduction modulo $p$ handles the larger correction domain. |
| Finite free category, variance and parallel arrows | passed | There are no nonidentity paths longer than two; coincident labels do not identify arrows. |
| Protected partial section and Theorem 2 | passed | Only the two protected residue arrows are internal; the three roles impose exactly the stated equations. |
| Residual type and all-arrow product | passed | The final text explicitly uses $\prod_{f:v\to w}F_N(v)$. |
| Equivalence (10) and quotient injection | passed | Zero residue defects force divisibility; all composite and identity components are accounted for. |
| Carry-enlarged diagram and Theorem 3 | passed | Carries are uniquely forced; multiplication is treated in Set rather than by an additive quotient. |
| Multiplicative correction equation (11) | passed | The coefficient ring is $K_N$; coefficients reduce to $t_{N-1}$, with the prescribed zero-ring interpretation. |
| Naturality of realizations, $j_N$, and actual $Q_N$ | passed | Reduction commutes with restrictions, $D_N$, and $P_N$, so it descends to the quotient. |
| Digit bijections and precision square | passed | The tail induction proves bijectivity for the stated formula (12). |
| Transported ring operations and inverse limit | passed | The truncation maps are ring maps after transport; the componentwise inverse-limit maps are inverse. |
| Recursions (14)–(15) and limiting carry | passed | Tail domains, coefficient reductions, and the shifted $K_N$ inverse limit are correct. |
| $N=1$, $N=2$, $p=2$, zero tails | passed | The boundary cases agree with every stated local theorem. |
| Framework definition/notation translation | passed | Physical PDF pages 8–16 agree with the final view, partial-section, residual and quotient conventions. |
| Global ABC, IUT, predecessor compactness proof, earlier Lean, novelty | out of scope | None is used as evidence for the local theorem package. |

## 3. Decisive derivations

### Finite category and protected extension fiber

The objects in the additive diagram are $2p+p^2$ distinct formal labels. There are $p+3p^2$ generating arrows and $3p^2$ nonidentity length-two paths. All $w_{x,y}$ are sinks. Thus the free category is finite; it has $3p+7p^2$ arrows including identities. In particular, roles 1–3 remain separate when their source labels coincide.

A coherent family has variable coordinates $u(x)$. Roles 1 and 2 force its $w_{x,y}$-coordinate to be $(u(x),u(y))$. Role 3 then imposes $u(x+y)=u(x)+u(y)$, and the residue and protected equations impose exactly $r_Nu=\mathrm{id}$, $u(0)=0$, $u(1)=1$. This also proves the converse, since maps on composites were defined by composition. At $N=1$, $r_1$ is the identity, so the extension is unique. For $N\geq2$, (8), or directly the additive order of a residue lift of 1, excludes it.

### Exact protected quotient injection, including composites

Write $M_N=\operatorname{Map}(k^2,K_N)$. In the final revision the residual product is

$

\mathrm{Rdef}_N=\prod_{f:v\to w}F_N(v).

$

The map $j_N:M_N\to\mathrm{Rdef}_N$ is additive. Its only potentially nonzero generating components are the role-3 values $i_NC(x,y)$.

Suppose $D_Nh=j_N(C)$ and $h\in\ker P_N$. At $l_x\to v_x$,

$

0=(D_Nh)_{l_x\to v_x}=r_N(h_{v_x})-h_{l_x}
=r_N(h_{v_x}).

$

Hence $h_{v_x}=i_Nb(x)$ uniquely, with $b(0)=b(1)=0$. The first two role equations force
$h_{w_{x,y}}=(i_Nb(x),i_Nb(y))$. The third gives
$i_NC(x,y)=i_N(db)(x,y)$, hence $C=db$.

Conversely, for such a $b$, take exactly these coordinates and zero $l_x$-coordinates. The residue and first two role defects vanish; the third is $i_Ndb$. Every composite $l\to v\to w$ defect vanishes because the restriction to $k$ kills every $i_Nb$. Equivalently,

$

(Dh)_{g\circ f}=f^*(Dh)_g+(Dh)_f

$

and the possible role-3 term is killed by residue. Identity defects also vanish. Therefore $Dh=j_N(db)$ in the full all-arrow product, not just on the generators.

It follows that

$

j_N^{-1}(D_N(\ker P_N))=d(B_N),

$

which is exactly the kernel statement needed for the induced injection $M_N/d(B_N)\hookrightarrow Q_N$. Since $D_Ne_N=j_N(C_N)$, its image is the actual protected obstruction class. No equality of the two entire quotients is asserted or needed. The signs in $C_u=C_N+db$ and the repair $e_N-h$ are consistent because $d(B_N)$ is a subgroup.

### Multiplication, naturality and correction domains

For nonzero $x\in k$, multiplicativity and $u(1)=1$ make $u(x)$ a unit with $u(x)^{p-1}=1$. The quotient by $t_N(x)$ lies in $1+pR_N$. If it is 1 modulo $p^r$, its $(p-1)$-st power modulo $p^{r+1}$ forces it to be 1 at the next precision. This proves Lemma 1 without an odd-prime assumption.

In the carry diagram, the residue equation makes $u(x)+u(y)-u(x+y)$ belong to the image of $i_N$, so the carry role has precisely one possible value. In the multiplication diagram the third role imposes $u(xy)=u(x)u(y)$. Lemma 1 then gives the complete unique realization.

Expanding $(t_N(x)+pb(x))(t_N(y)+pb(y))$ and applying the inverse of $i_N$ yields (11) in $R_{N-1}$. Both cross coefficients are reductions of $t_N$, hence $t_{N-1}$; the quadratic term is $p\,b(x)b(y)$ in that same ring. This verifies the nonlinear multiplication condition separately from the additive correction quotient.

For reductions, the only additional carry square is

$

\rho_N\,i_{N+1}=i_N\,(K_{N+1}\to K_N).

$

Multiplication squares use reduction as a ring homomorphism. Consequently the declared fiber maps are natural. In the additive diagrams the same maps commute with $D$ and protected restriction $P$, sending $D_{N+1}(\ker P_{N+1})$ into $D_N(\ker P_N)$. They therefore define $Q_{N+1}\to Q_N$; the displayed $i_N$ square gives compatibility with $j_N$. This checks the actual quotient tower, not only the cochain quotient.

### Digit induction and inverse limit

For $x\in R_N$, let $d_0=r_N(x)$ and

$

X'=i_N^{-1}(x-t_N(d_0))\in R_{N-1}.

$

The induction determines the remaining digits uniquely. If
$X'=\sum_{j=0}^{N-2}p^j t_{N-1}(d_{j+1})$, multiplication through $i_N$, together with the precision compatibility of $t_N$, gives exactly formula (12) in $R_N$. This checks that the induction in the note inverts the stated $\Psi_N$, rather than an alternative digit map.

Reducing $\Psi_{N+1}$ deletes its last term and reduces each other Teichmuller coefficient. Thus the ring operations transported through $\Psi_N$ make truncation a ring homomorphism. Passing to coherent families gives mutually inverse maps coordinate by coordinate. The digit operations are transported operations; the proof does not claim coordinatewise addition in $k^N$.

In (14) the bracket is in $R_{N-1}$. In (15), reducing the cross coefficients to that ring gives $t_{N-1}$, while the $p^2X'Y'$ term becomes $p[pX'Y']$. The inverse limit of the $K_N=R_{N-1}$ tower is canonically the same shifted inverse limit $\mathbf Z_p$; the limits of (3) and (8) therefore give $pC=t(x)+t(y)-t(x+y)$ and $\sum_jC(1,j)=1$.

Finally, if $pz=0$ in $\varprojlim R_N$, then $z_{N+1}$ is divisible by $p^N$, and so $z_N=0$. This proves the claimed injectivity and excludes an additive residue section.

## 4. Boundary cases and smallest explicit example

At $N=1$, $K_1=R_0=0$, $i_1$ is the injection from the zero additive group, $C_1=0$, and (7) is the trivial group. In (8), “1 in $K_1$” is zero. Both enlarged and additive protected realizations are unique, and $\Psi_1$ is the identity. Equations (11), (14), and (15) use exactly the specified zero tail $t_0$; no undefined negative precision or inversion of $p$ occurs.

For $p=2,N=2$, $t_2(0)=0,t_2(1)=1$ in $\mathbf Z/4$, and

$

C_2(0,0)=C_2(0,1)=C_2(1,0)=0,\qquad C_2(1,1)=1

$

in $\mathbf F_2$. The protected correction group $B_2$ is zero. Hence the role-3 defect at $w_{1,1}$ is 2, and the additive obstruction is nonzero. The carry realization retains exactly that value. Also
$\Psi_2(d_0,d_1)=d_0+2d_1\pmod4$, so adding the digit vector $(1,0)$ to itself produces $(0,1)$, as (14) requires. These are direct hand checks, not a finite-range substitute for the universal proof.

## 5. Source and command checks

The exact framework source read independently was *Realization_Calculus_Volume_I_Komorebi_Space.pdf*, current native file
`file_00000000750881f6814ea548be018387`,
Library identity `libfile_bd054a01919c8191b1bb6d1a9a4965d6`,
physical pages 8–16 (printed pages 1–9), 162 pages total, 1,341,516 bytes. The returned metadata has no version id; its created and modified timestamps are both `2026-10-24T18:52:08.948030Z`.

Definition 1.1 and Definition 1.2 give the contravariant view system and coherent section; section 1.2 gives the naturality square; section 2.1 gives the full protected domain; sections 3.1–3.2 give the all-arrow source-fiber residual and quotient; Theorem 4.1 has the same correction principle. The translation to the final note is exact. Only these definitions and elementary quotient reasoning are needed; no arithmetic theorem is imported from this source.

The exact extracted page text has SHA-256
`6fbb744ac152d73d0b2c2b80691b21bbad455914ea2c499bec434457d86ff7d0`,
using UTF-8 and the returned content array joined by LF with no final LF. Its size is 27,920 bytes. The canonical structured API response has SHA-256
`11bd9c0cdbe5082b5a8962faf0819b9826b458cc25e25118d8f7cba38b52f949`.
The full PDF bytes were not materialized or hashed; these are extraction hashes, not a claimed full-PDF hash.

Checks used raw `cat` reads, focused `sed` reads of author revisions, `rg -n` for theorem/type locations, `sha256sum` for raw proof revisions, and Python SHA-256 for the exact source extraction. Applicable ancestor `AGENTS.md` files were checked; none were present. No Lean build, formal certification, exhaustive finite experiment, or load-bearing computation was run or required. No route status, other review, route INPUTS, or predecessor research note was read.

## 6. Remaining gap, safe conclusion and provenance

There is no remaining mathematical gap in the normalized local claim at the final pinned revision. Its strongest safe conclusion is the explicit protected finite arithmetic realization and its $\mathbf Z_p$ digit tower, with a persistent nonzero additive carry obstruction at every precision $N\geq2$. A general perfect-residue Witt functor and a uniform global height estimate require further work outside this proof. No further finite enumeration is needed to establish the proved local statements.

This was an isolated subagent audit, initially given the raw proof and no preferred verdict. The reviewer derived the critical objects from the definitions and independently read the necessary framework pages. No route status or prior review was consulted. The author supplied the exact framework locator and notified the reviewer of revisions. During the review, the author explicitly raised the residual-type wording and the residue-arrow wording. The reviewer checked them and agreed to the uniquely forced clarifications; the residue-arrow derivation had already been reconstructed independently. Accordingly this is an independent mathematical reconstruction with disclosed author interaction, not a blind audit of an unchanged submission or a claim of model-independent verification.

Revision history relevant to this review:

- Initial raw proof read: `9951b38e3bbeb06cb8c67a827454e1c527c849809e65e0d5578c3e875c606293`.
- Author added the explicit naturality paragraph for the actual $Q_N$ tower: `629350b705b2ca4d7fbb5f207b0ad21748a044dc160afef99298676324daa983`.
- The earlier phrase “target fibers over all arrows of the finite category” could literally mean $F_N(w)$, which would not type the displayed differential. The author replaced it by the forced type $\prod_{f:v\to w}F_N(v)$: `93fd08030ee10d134d97ba10f3fd3b1b249093aa64ef30d126e3ad95205c6995`.
- The bare assertion that a protected correction has residue-zero variable coordinates needed the witness equation $Dh=j(C)$. For the smallest example, at $p=3,N=1$ a correction supported at the unprotected vertex $v_2$, with value 1, belongs to $\ker P$ but has nonzero residue. The author made the already assumed zero residue-arrow component explicit. Final complete proof reread and pinned: `cf6854a9c966c3fcbbccb9bd2035c66a31642d532da3fbed15e3bf8f054188bb`.

The reviewer did not edit the author's proof. The final primary verdict applies to the final hash, with both wording clarifications present. It does not silently certify the ambiguous wording of the earlier revisions.
