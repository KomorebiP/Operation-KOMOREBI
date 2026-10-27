# Paper IX native conjectures: typed progress and boundaries

Author: Komorebi P.  
Independent continuation review: 2026-09-08.

## Verdict

**Incomplete, with the smallest missing implication identified.** The native Conjectures 13.2 and 13.3 on manuscript page 26 are not yet precise enough to admit an unqualified proof or disproof. Neither is promoted to proved here. There is nevertheless useful progress:

1. A complete elementary proof gives a finite obstruction and an exact lift count for every fixed finite system of integer polynomial equations.
2. For finitely presented commutative integer algebras, an intrinsic, presentation-independent obstruction is a specialization of a verified classical theorem.
3. The natural Hausdorff topological interpretation of the proposed spine reconstruction fails for global integer constant sequences. The same example identifies the necessary completion correction.
4. An accompanying standalone Lean module treats a stated affine-linear specialization. Its exact checked scope and execution records are separate from the general polynomial proof and the external cotangent-complex theorem.

These results do not assert mathematical novelty.

## 1. Manuscript claim cards

The authoritative inspected source was `paper/Projector_Resolved_Seed_Calculus_IX_Status_Corrected.pdf`, Definition 1.1 on page 4 and Section 13 on pages 25–26. The finite completion ledger explicitly keeps both native conjectures conjectural. The existing file named `ConjectureExamples.lean` concerns Nishibuchi examples, not these two native conjectures.

**13.2.** The manuscript quantifies over failed lifts from precision $p^L$ to $p^{L+1}$ in a finitely presented arithmetic seed system and requests a canonical finite obstruction packet, zero exactly when continuation is possible. Definition 1.1 permits a coefficient ring or module, a seed, allowed operators, relations, residue projectors, weights and a chosen topology. It does not specify a category of presentations, a lift functor, the allowed equivalences between presentations, the type of a packet, or whether “finite” means a finite set, finite dimension, or finite support. “Continuation” also needs to mean a single step unless a separate inverse-limit argument is supplied.

**13.3.** The manuscript requests a smallest common packet spine $C$ with

$$X\cong X^{\mathrm{wt}}_2\times_C\prod_{p>2}'X_p.$$

There is no definition of $X$, the distinguished subsets in the restricted product, the maps to $C$, the category of the fiber product, or an order/universal property expressing “smallest.” Compatibility and the proposed recurrence/spectral/Frobenius data are not specified as maps or descent conditions. In particular, neither the global object nor its completion is fixed.

## 2. A complete polynomial obstruction theorem

**Scope.** Fix a prime $p$, an integer $L\ge1$, finite natural numbers $d,r$, and polynomials $F_1,\ldots,F_r\in\mathbb Z[X_1,\ldots,X_d]$. Let $\bar x\in(\mathbb Z/p^L\mathbb Z)^d$ satisfy every equation $F_i(\bar x)=0$. Choose any integer representative $x\in\mathbb Z^d$. Set

$$e_i=F_i(x)/p^L\pmod p,\qquad J_{ij}=\frac{\partial F_i}{\partial X_j}(x)\pmod p.$$

The divisions are exact integer divisions. Regard $J$ as a linear map $\mathbb F_p^d\to\mathbb F_p^r$. Define

$$O_{F,\bar x}=\mathbb F_p^r/\operatorname{im}J,\qquad o_{F,\bar x}=[e].$$

**Theorem.** For this fixed polynomial presentation, the group and distinguished class are independent of the chosen integer representative. The class vanishes if and only if $\bar x$ lifts to a solution modulo $p^{L+1}$. The obstruction group has $p^{r-\operatorname{rank}J}$ elements. When lifts exist, their set is a torsor for $\ker J$ and contains exactly $p^{d-\operatorname{rank}J}$ elements.

**Proof.** For every integer correction vector $t$, expansion of each monomial gives

$$F(x+p^Lt)\equiv F(x)+p^LJ(x)t\pmod {p^{L+1}}.\tag{1}$$

Indeed, each term involving at least two correction factors is divisible by $p^{2L}$, and $2L\ge L+1$. Constant and linear correction terms give the two displayed summands. Adding the monomial expansions proves (1) for every polynomial, with no denominator or analytic convergence issue.

Every element reducing to $\bar x$ is uniquely expressible modulo $p^{L+1}$ as $x+p^Lt$ with $t\in\mathbb F_p^d$. By (1), it solves the equations exactly when

$$e+Jt=0\quad\text{in }\mathbb F_p^r.\tag{2}$$

Equation (2) is soluble exactly when $e\in\operatorname{im}J$: the sign makes no difference because the image is a subspace. This is equivalent to $[e]=0$.

Another representative has the form $x'=x+p^Ls$. Since $L\ge1$, its Jacobian is the same modulo $p$. Dividing (1) by $p^L$ shows that its residual digit is $e'=e+Js$, so it gives exactly the same quotient class. If $t_0$ solves (2), all its solutions are $t_0+\ker J$, and no others. The finite cardinalities follow from rank-nullity. This also covers no variables, no equations, zero Jacobian and singular solutions. $\square$

The proof is a universal mathematical argument. The accompanying Python checks are independently bounded evidence about an implementation, not a substitute for that argument. The standalone Lean specialization does not formalize multivariable polynomial expansion (1), unless its own checked source explicitly says so.

### Necessary boundaries and exact examples

- **A failed singular lift:** $p=3$, $L=1$, $F(X)=X^2-3$, $x=0$. Here $e=-1\ne0$ in $\mathbb F_3$ and $J=0$. There are no lifts of zero modulo 3 to a root modulo 9.
- **Representative independence is a quotient assertion:** for $F(X)=X^2-1$, $p=3$, $L=1$, representatives $1$ and $4$ have residual digits $0$ and $2$. Their common Jacobian is $2$, with full image, and both give zero obstruction. Their corrected representatives $1$ and $10$ are the same root modulo 9.
- **A successful step need not give indefinite continuation:** for $F(X)=X^2-5$, $p=2$, the root $1$ modulo 2 has zero obstruction and lifts to $1,3$ modulo 4. Both have nonzero obstruction at the next step. There is no root modulo 8 and no compatible infinite lift.
- **The raw Jacobian cokernel need not be presentation independent:** the presentations $F=(X)$ and $G=(X,0)$ define the same solution system. Their raw obstruction groups at zero are respectively zero and $\mathbb F_p$. Both actual distinguished obstructions are zero. Thus one cannot claim a canonical isomorphism of these two raw groups merely because the equations define the same seed.

## 3. An intrinsic finite obstruction under an algebraic restriction

Let $B$ be a finitely presented commutative $\mathbb Z$-algebra, $p$ prime and $L\ge1$. For a ring map $f:B\to\mathbb Z/p^L\mathbb Z$, use its reduction to make $\mathbb F_p$ a $B$-module. There is a canonical class

$$o(f)\in\operatorname{Ext}^1_B(\mathrm{NL}_{B/\mathbb Z},\mathbb F_p)$$

whose vanishing is equivalent to a lift $B\to\mathbb Z/p^{L+1}\mathbb Z$. This follows from the ring-map lifting theorem in [Stacks Project, Lemma 91.2.1, tag 08S5](https://stacks.math.columbia.edu/tag/08S5). Specialize the source extension to $0\to0\to B\to B$ and the target extension to the kernel $p^L/p^{L+1}\cong\mathbb F_p$. The base maps are identities of $\mathbb Z$. The kernel is square zero because $L\ge1$.

The comparison in [Stacks Project, Lemma 10.134.2, tag 00S1](https://stacks.math.columbia.edu/tag/00S1) identifies the complex from a polynomial presentation with the canonical naive cotangent complex up to homotopy. Thus this construction is intrinsic, up to the stated canonical comparison.

The group is finite. Choose a finite presentation $P=\mathbb Z[X_1,\ldots,X_d]\twoheadrightarrow B$ with finitely generated kernel $I$. The presentation description in [Stacks Project, Remark 91.2.4, tag 0GPU](https://stacks.math.columbia.edu/tag/0GPU) identifies the group as

$$\operatorname{coker}\left(\operatorname{Hom}_B(\Omega_{P/\mathbb Z}\otimes_P B,\mathbb F_p)\longrightarrow\operatorname{Hom}_B(I/I^2,\mathbb F_p)\right).$$

If $I$ has $r$ chosen generators, evaluation on their classes injects the latter Hom module into $\mathbb F_p^r$. Hence its quotient is finite. The relation module $I/I^2$ retains dependencies between equations, including redundant zero equations, which the raw target $\mathbb F_p^r$ does not.

**Status:** externally proved after the exact stated specialization, with the finiteness argument above. This theorem is not independently formalized in the accompanying Lean file. Extending it to all operator/recurrence/module systems admitted by manuscript Definition 1.1 requires a specified encoding and a proof that its notion of lift is preserved. That is the missing implication for applying it to native Conjecture 13.2 without restriction.

**Source record.** The Stacks Project authors, live primary text inspected 2026-09-08, tags 08S5, 0GPU and 00S1. Full theorem/proof text was inspected, not only search snippets. No immutable source revision was pinned or downloaded. The use is a classical specialization, not a novelty search or a claim of a new obstruction theory. No broader paper or source cache was changed.

## 4. A topological obstruction to the proposed spine formula

Consider the recurrence $a_{n+1}=a_n$ with integer initial value. Its global parameter space is $X=\mathbb Z$. Its local parameter spaces are $X_p=\mathbb Z_p$, and every local realization has the same prime-independent recurrence. Give the local factors their usual $p$-adic topologies and the product its product topology. For these integral local factors, the restricted product relative to all $\mathbb Z_p$ is the ordinary product. Write

$$A=\mathbb Z_2,\qquad B=\prod_{p>2}\mathbb Z_p,\qquad D=\{(n,(n)_{p>2}):n\in\mathbb Z\}\subset A\times B.$$

**Theorem.** There are no Hausdorff space $C$ and continuous maps $f:A\to C$, $g:B\to C$ for which the equality locus

$$\{(a,b):f(a)=g(b)\}$$

is exactly $D$. Thus the canonical local realizations of global integer constant sequences cannot satisfy the manuscript's fiber-product formula in this Hausdorff topological interpretation.

**Proof.** The equality locus is closed: it is the inverse image of the diagonal of $C\times C$ under the continuous map $f\times g$, and a Hausdorff space has closed diagonal.

The set $D$ is dense in $A\times B$. A nonempty basic open set prescribes congruences at only finitely many primes and finite precision at each. The moduli are pairwise coprime. The finite Chinese remainder theorem supplies an integer meeting all those congruences, so every such open set meets $D$.

However, $D$ is not the whole product. The element with 2-adic coordinate zero and every odd-adic coordinate one is not diagonal. If an integer had zero 2-adic coordinate, it would be divisible by every power of two, forcing it to be zero. Its 3-adic coordinate would then be zero, not one. Consequently $D$ is a proper dense subset and is not closed. It cannot be the equality locus above. $\square$

This is not asserted to refute the original, underspecified sentence under every possible reading. It refutes the explicit and natural interpretation just stated. The assumptions of continuity, Hausdorffness and identification through the canonical local maps are essential to this claim.

### A precise reconstruction that does hold

For a finite set $S$ of primes, positive precisions $L_p$, and a fixed integer polynomial system $F$, put

$$N=\prod_{p\in S}p^{L_p},\qquad\operatorname{Sol}_F(R)=\{x\in R^d:F(x)=0\}.$$

Then coefficientwise CRT gives a canonical bijection

$$\operatorname{Sol}_F(\mathbb Z/N\mathbb Z)\cong\prod_{p\in S}\operatorname{Sol}_F(\mathbb Z/p^{L_p}\mathbb Z).$$

The reason is exact: the CRT ring isomorphism preserves polynomial evaluation, and zero in a finite product is equivalent to zero in every component. For $F$ empty, passing to all compatible finite congruences identifies the profinite completion $\widehat{\mathbb Z}$ with $\prod_p\mathbb Z_p$. The same finite reconstruction is compatible with coefficient projections and integer recurrence matrices because these operations commute with reduction and CRT.

Here the polynomial equations or recurrence matrices are fixed common data. The theorem reconstructs finite or profinite objects. It does not identify a “smallest” spine, impose additional spectral descent, or recover global $\mathbb Z$ from arbitrary tuples of local points. A completed version of 13.3 must say exactly which object is completed and specify its universal property.

### A finite compatibility criterion with a precise universal property

Fix finite sets $A,B$ of local packets and an explicitly given relation $R\subseteq A\times B$. Say that $R$ is rectangular when

$$R(a,b),\ R(a',b),\ R(a',b')\quad\Longrightarrow\quad R(a,b')$$

for all $a,a'\in A$ and $b,b'\in B$.

**Theorem.** The relation $R$ can be represented exactly as

$$R(a,b)\quad\Longleftrightarrow\quad f(a)=g(b)$$

for maps from $A$ and $B$ to a common set if and only if $R$ is rectangular. In that case a canonical finite choice of common set is the connected-component set $C_R$ of the bipartite graph with vertex set $A\sqcup B$ and edges given by $R$.

The component maps $f_R:A\to C_R$ and $g_R:B\to C_R$ have the following universal property. For every set $Y$ and maps $h:A\to Y$, $k:B\to Y$ satisfying $h(a)=k(b)$ whenever $R(a,b)$, there is a unique map $u:C_R\to Y$ with $u\circ f_R=h$ and $u\circ g_R=k$.

**Proof.** Any equality representation is rectangular, since the three assumed equalities imply $f(a)=g(b)=f(a')=g(b')$.

Conversely, suppose $R$ is rectangular. An edge always gives equal component labels. If $a\in A$ and $b\in B$ have equal component labels, there is a finite path between them. Its length is odd. A path of length one is already an $R$-edge. A longer path begins with three edges $a-b_1-a_1-b_2$. Rectangularity gives the edge $a-b_2$. Replacing these three edges by that edge shortens the path by two. Induction therefore yields $R(a,b)$. This proves the exact equality representation. Finiteness follows because the component set is a quotient of the finite set $A\sqcup B$.

For the universal property, combine $h$ and $k$ into a function on $A\sqcup B$. It is constant across every edge by hypothesis, hence along every finite path. It therefore descends to a well-defined function on components. The two required factorization identities hold by construction. They determine the value on every component, proving uniqueness. $\square$

For example, the three pairs $(a_0,b_0),(a_1,b_0),(a_1,b_1)$ without $(a_0,b_1)$ fail rectangularity. Every equality-label representation agreeing on those three pairs also admits the fourth pair, so it cannot represent that relation exactly.

This is a precise finite gluing obligation: future arithmetic applications must define $A$, $B$ and $R$ and prove rectangularity. The universal property holds for the component quotient even when rectangularity fails, but then the equality locus strictly enlarges $R$. The theorem establishes neither a minimum number of labels nor a smallest spine in the manuscript's unspecified category. It carries no automatic topology, spectral information or Frobenius compatibility. **Evidence: prose proof in this note, not a Lean formalization.**

## 5. Dependency and obligation audit

| Result or obligation | Evidence | Status |
|---|---|---|
| Native notions of finite presentation, packet, lift and canonicality | Definition 1.1 and page 26 | Incomplete |
| Finite polynomial correction identity | Monomial expansion and $2L\ge L+1$ | Proved in the stated scope |
| Obstruction class independent of integer lift | Residual changes by $Js$ | Proved in the stated scope |
| Vanishing iff one-step polynomial lift | Explicit correction equation | Proved in the stated scope |
| Finite obstruction and exact lift count | Finite-field linear algebra | Proved in the stated scope |
| Intrinsic finite-algebra obstruction | Verified Stacks theorem plus finite-generator argument | Externally proved in the stated scope |
| Every manuscript seed system has the required algebraic encoding | No such encoding supplied | Not addressed |
| Raw Jacobian group unchanged by redundant equations | $(X)$ versus $(X,0)$ | Failed |
| Native fiber-product maps, category and minimum | No such definitions supplied | Incomplete |
| Global integer reconstruction over a Hausdorff spine | Dense proper diagonal versus closed equality locus | Refuted in the stated interpretation |
| Finite/profinite reconstruction | CRT and compatible reduction | Proved in the stated scope |
| Finite equality-label gluing iff rectangularity | Bipartite paths and universal component quotient | Proved in prose in the stated scope |
| Multivariable polynomial theorem checked in Lean | Separate affine module only | Not claimed |

## 6. Exact computation and proofread record

The Lean specialization is `lean/FiniteAffineObstruction.lean`. It proves an actual lift criterion for every finite integer-linear map $A:\mathbb Z^d\to\mathbb Z^e$, right-hand side $b$, lower solution $x$, positive modulus $p$ and $L\ge0$. It constructs the residual from the stated divisibility of $Ax-b$, constructs a finite quotient, and proves that zero obstruction is equivalent to existence of a next-level solution congruent to $x$ modulo $p^L$. The arithmetic residual transport and cancellation are proved from linearity and nonzeroness. There is no assumed Taylor or lift-existence bridge. The result even permits composite positive moduli and $p=1$, since no field argument is used in this affine proof.

`lean/verify_native.py --kit PATH --output NEWDIR` copies the source, compiles with one Lean thread and warnings as errors, and writes a fresh audit. The authoritative run is `lean/replay_02/native_affine_audit.json`: aggregate PASS. It checks all 13 declarations in the main module and all 4 control theorems. Every transitive axiom is among `propext`, `Classical.choice`, and `Quot.sound`. Both false strengthening attempts are rejected by Lean with the expected mathematical type mismatches. The controls also prove a nonzero obstruction and a genuine system that is solved modulo 2 but has no solution modulo 4. An earlier development verifier run failed only because its rejection-message matcher was case-sensitive; the successful run fixes this parser issue.

Run `python3 native_work/check_polynomial_obstructions.py` from the parent workspace. The exhaustive part covers all 625 integer coefficient vectors in $\{-2,-1,0,1,2\}^4$, primes $2,3,5$, precisions $L=1,2,3$, and every residue representative modulo $p^L$. It scans 130,000 residues and checks 6,502 solution points, including 3,004 singular points. The direct evaluation and correction criterion agree on all 5,118 liftable and 1,384 obstructed points. Six explicit benchmarks test failure, representative changes and a later obstruction following an initially successful step. The manifest records exact scope, script/output hashes and environment. Its schema validator passed.

Self-review covered this entire newly written note. Routine notation, hypotheses, zero-dimensional cases, signs and completion distinctions were checked. No prior manuscript text was edited. The remaining unresolved issues are the native definitions and the missing encoding/descent implications recorded above.
