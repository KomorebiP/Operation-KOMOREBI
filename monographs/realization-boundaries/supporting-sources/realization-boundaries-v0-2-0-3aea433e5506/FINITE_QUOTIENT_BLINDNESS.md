# Realization beyond finite quotients
## Dense rank-one groups with prescribed computational degree

*A mathematical continuation of the Realization Calculus boundary constructions*

## Main result

There is a family of countably infinite abelian groups \(G_A\), indexed by arbitrary subsets \(A\subseteq\mathbb N\), with the following properties.

1. Every \(G_A\) is residually finite and has no nonzero divisible subgroup.
2. Every group has the same torsion subgroup
   \[
   D=\bigoplus_{i\geq0}C_{p_i},
   \]
   and \(G_A/D\cong\mathbb Q\). The resulting extension does not split.
3. For every positive integer \(m\),
   \[
   G_A/mG_A\cong\prod_{p\mid m}C_p\cong C_{\operatorname{rad}(m)}.
   \]
   These identifications respect the quotient transition maps. Consequently every group has the same profinite completion
   \[
   \widehat{G_A}\cong P=\prod_{i\geq0}C_{p_i}.
   \]
4. The exact abstract isomorphism criterion is
   \[
   G_A\cong G_B\quad\Longleftrightarrow\quad A\mathbin\triangle B\text{ is finite}.
   \]
   Groups from distinct classes do not embed into one another, and neither is a quotient of the other.
5. For every oracle \(X\),
   \[
   G_A\text{ has an }X\text{-computable copy}\quad\Longleftrightarrow\quad A\leq_T X.
   \]
   Thus the isomorphism type has least presentation degree exactly \(\deg_T(A)\).
6. Inside this single profinite-completion class, continuum many groups escape any fixed countable, parameter-free, finite-description grammar with single-valued isomorphism semantics.

The conclusion is stronger than the observation that a finite grammar has only countably many descriptions. It separates the information needed to reconstruct an original group from the information retained by **all of its finite quotients**. Residual finiteness is retained throughout: this is not achieved by adjoining an invisible divisible direct summand.

### Verification and attribution

The statements in this note have ordinary mathematical proofs below. The executable companion implements the cocycle group law and exact root construction and checks finite instances. It is not a Lean formalization or an independent referee report. No historical priority is claimed for the family or theorem package.

The inherited prime-spectrum construction is explicitly classical: Montalbán's *Computable Structure Theory: Within the arithmetic*, Example III.39 and the following paragraph, contains both the direct-sum spectrum construction and complementary-set coding [R1]. The present continuation imposes the additional common-completion and residual-finiteness conditions and supplies its own proofs. Definitions of computable profinite presentations and cocycle extensions follow standard usage [R3].

## 1. Notation and the fixed ambient realization

List the primes as \(p_0=2,p_1=3,p_2=5,\ldots\). All groups are additive. Identify \(C_p\) with the additive group of \(\mathbb F_p\). Set

\[
D=\bigoplus_{i\geq0}\mathbb F_{p_i},\qquad
P=\prod_{i\geq0}\mathbb F_{p_i}.
\]

An element of \(D\) has finite support. No support restriction is imposed in \(P\). The latter has its product topology. Write \(e_p\) for the vector with coordinate one at \(p\) and zero elsewhere.

### Lemma 1.1. The ambient quotient is uniquely divisible

\(V=P/D\) is a rational vector space. Also \(\operatorname{Tor}(P)=D\), and \(P\) has no nonzero divisible subgroup.

**Proof.** An element of \(P\) has finite order precisely when it has finite support, since a nonzero coordinate of prime order \(p\) can be annihilated by an integer \(m\neq0\) only if \(p\mid m\).

Fix \(m\geq1\). Given \(x\in P\), put \(y_p=m^{-1}x_p\) in \(\mathbb F_p\) for \(p\nmid m\), and put \(y_p=0\) for \(p\mid m\). Then \(x-my\) has finite support. Hence multiplication by \(m\) is surjective on \(V\). If \(mx\in D\), then outside the finitely many prime divisors of \(m\), multiplication by \(m\) is invertible and \(x\) has finite support. Therefore \(x\in D\), proving injectivity. Unique division defines the rational vector-space structure.

Finally, a homomorphic image of a divisible group in \(C_p\) is zero: write an arbitrary element as \(p\) times another element. Every coordinate projection of a divisible subgroup of \(P\) is therefore zero. Such a subgroup is zero. \(\square\)

In particular, any subgroup of \(P\) is reduced, meaning that it has no nonzero divisible subgroup. This terminology is independent of finite generation or computability.

## 2. Encode a set by a paired prime selector

For \(A\subseteq\mathbb N\), let \(a_n=\mathbf 1_A(n)\), and select one prime from each consecutive pair:

\[
S_A=\{p_{2n+a_n}:n\geq0\}.
\]

Both \(S_A\) and its complement in the primes are infinite. Let \(u_A\in P\) have coordinate one on \(S_A\) and zero elsewhere. This is an idempotent of the coordinatewise ring \(P\), and also an ordinary element of its additive group.

Let \(q:P\to V=P/D\) be the quotient map. Define

\[
\boxed{G_A=q^{-1}\bigl(\mathbb Q q(u_A)\bigr).}
\]

Thus \(G_A\) is the full inverse image of a one-dimensional rational subspace of the fixed ambient quotient. The subspace is nonzero because \(u_A\) has infinite support.

This formula is a set-theoretic definition for every \(A\). It does not supply a finite effective description of the selector when \(A\) is arbitrary.

### 2.1 Concrete representatives of rational lifts

For a rational \(r=a/b\) in lowest terms with \(b>0\), define \(s_A(r)\in P\) by

\[
(s_A(a/b))_p=
\begin{cases}
a b^{-1}\pmod p,&p\in S_A\text{ and }p\nmid b,\\
0,&p\notin S_A\text{ or }p\mid b.
\end{cases}
\]

Here inversion takes place only when the denominator is a unit in \(\mathbb F_p\). In particular, \(s_A(0)=0\), \(s_A(1)=u_A\), and \(s_A(-r)=-s_A(r)\).

The difference \(b s_A(a/b)-a u_A\) is supported on the finitely many primes dividing \(b\). Therefore

\[
q(s_A(r))=r q(u_A).
\]

It follows that

\[
G_A=\{s_A(r)+d:r\in\mathbb Q,\ d\in D\}.
\]

### Lemma 2.1. Normal forms are unique

Every element of \(G_A\) has a unique expression \(s_A(r)+d\).

**Proof.** If \(r\neq0\), then \(s_A(r)\) has a nonzero coordinate at every selected prime outside the finite set dividing its numerator or denominator. It has infinite support, so it does not belong to \(D\). Subtracting two proposed expressions and passing to \(V\) gives \((r-r')q(u_A)=0\). Since \(q(u_A)\neq0\) in a rational vector space, \(r=r'\), and then \(d=d'\). \(\square\)

Consequently \(G_A\) is countable, even if \(A\) is noncomputable. The normal-form set \(\mathbb Q\times D\) can be named effectively. What may fail to be computable is its **group operation**.

## 3. An exact finite cocycle gives the group law

Define

\[
c_A(r,t)=s_A(r)+s_A(t)-s_A(r+t).
\]

### Lemma 3.1. The cocycle is finitely supported

\[
\operatorname{supp}c_A(r,t)
\subseteq\{p:p\mid\operatorname{den}(r)\operatorname{den}(t)\}.
\]

**Proof.** At any other prime all denominators are invertible. On a selected coordinate, rational reduction respects addition. On an unselected coordinate, all three terms vanish. The denominator of \(r+t\) has no prime factor absent from the two original denominators. \(\square\)

In normal forms the operation is

\[
\boxed{(r,d)+(t,e)=(r+t,d+e+c_A(r,t)).}
\]

The identity is \((0,0)\), and the inverse is \((-r,-d)\). The latter assertion uses the particular normalization \(c_A(r,-r)=0\).

The cocycle is symmetric and satisfies

\[
c_A(r,t)+c_A(r+t,v)=c_A(t,v)+c_A(r,t+v),
\]

by cancellation of the four section terms on each side. Thus the operation is associative and commutative. Equivalently, the map \((r,d)\mapsto s_A(r)+d\) identifies the law with the addition of the actual subgroup \(G_A\leq P\).

### 3.1 One operation can expose a selector bit

For any prime \(p\),

\[
\boxed{c_A(1/p,(p-1)/p)=-\mathbf 1_{S_A}(p)e_p.}
\]

Away from \(p\), rational addition gives zero defect. At \(p\), both fractional section values are zero and the section value of one is \(\mathbf 1_{S_A}(p)\).

This is a concrete warning against dropping the cocycle. The ordinary direct product law on \(\mathbb Q\times D\) describes a different group.

### 3.2 A small worked example

Take \(A=\varnothing\), so the selected primes begin \(2,5,11,17,\ldots\). Then

\[
(1/2,0)+(1/2,0)=(1,e_2),
\]

not \((1,0)\). There is no element whose double is \(u_A=(1,0)\). By contrast,

\[
3(1/3,0)=(1,0),
\]

because the prime 3 is unselected. The executable example reproduces both identities using exact rational and modular arithmetic.

## 4. Structural properties and the nonsplitting obstruction

### Theorem 4.1. Fixed torsion, rational quotient, and residual finiteness

For every \(A\):

\[
\operatorname{Tor}(G_A)=D,\qquad G_A/D\cong\mathbb Q.
\]

The group is reduced, residually finite, and dense in \(P\). The exact sequence

\[
0\longrightarrow D\longrightarrow G_A\longrightarrow\mathbb Q\longrightarrow0
\]

does not split.

**Proof.** The torsion claim follows either from \(\operatorname{Tor}(P)=D\) or from the rational part of the unique normal form. The map \(s_A(r)+d\mapsto r\) is a surjective group homomorphism with kernel \(D\).

Every nonzero element has a nonzero prime coordinate, so a homomorphism to a finite \(C_p\) detects it. This proves residual finiteness. Density follows from \(D\subseteq G_A\) and the density of finite-support vectors in the product. Reducedness follows from Lemma 1.1.

A splitting would embed the nonzero divisible group \(\mathbb Q\) into the reduced group \(G_A\). This is impossible. More explicitly, every homomorphism \(\mathbb Q\to P\) has zero composite with every finite coordinate and is therefore zero. \(\square\)

The quotient has torsion-free rank one. Individual finitely generated subgroups are either finite cyclic or isomorphic to \(\mathbb Z\oplus C_m\) for some squarefree \(m\), including \(m=1\). To see the latter, the torsion part of such a subgroup is a finite subgroup of \(D\), hence cyclic. Its nonzero image in \(\mathbb Q\) is finitely generated and cyclic. Lifting a generator splits this *finitely generated* extension. This does not split the extension by all of \(\mathbb Q\).

## 5. Exact root tests determine every finite quotient

### Theorem 5.1. Integer divisibility is a coordinate condition

For \(g\in G_A\) and \(m\geq1\),

\[
\boxed{g\in mG_A\quad\Longleftrightarrow\quad g_p=0\text{ for every prime }p\mid m.}
\]

**Proof.** Necessity is immediate because multiplication by \(m\) is zero on every \(C_p\) with \(p\mid m\).

For sufficiency, write \(g=s_A(r)+d\) and put \(t=r/m\). The element

\[
h=g-ms_A(t)
\]

belongs to \(D\): it has zero image in \(V\). More explicitly, its support lies among the support of \(d\) and the primes dividing the denominators of \(r\) and \(t\). At a prime dividing \(m\), the hypothesis gives \(h_p=g_p=0\).

Set

\[
e_p=\begin{cases}m^{-1}h_p,&p\nmid m,\\0,&p\mid m.\end{cases}
\]

The vector \(e\) has finite support and satisfies \(me=h\). Hence

\[
m(s_A(t)+e)=g.
\]

This is both a proof and an explicit root construction relative to the selector. \(\square\)

### Theorem 5.2. All finite quotients are independent of the selector

The map

\[
\pi_m:G_A\longrightarrow\prod_{p\mid m}C_p,\qquad
\pi_m(g)=(g_p)_{p\mid m}
\]

is surjective and has kernel \(mG_A\). Therefore

\[
G_A/mG_A\cong\prod_{p\mid m}C_p\cong C_{\operatorname{rad}(m)}.
\]

**Proof.** Surjectivity already holds on \(D\), using a vector supported on the specified finite prime set. The kernel is exactly Theorem 5.1. The final identification is the Chinese remainder theorem. For \(m=1\), both groups are trivial.

If \(m\mid n\), the transition \(G_A/nG_A\to G_A/mG_A\) becomes the coordinate projection from the primes dividing \(n\) to those dividing \(m\). Thus the entire compatible quotient system is the same for every \(A\).

Every finite quotient of an abelian group has finite exponent \(m\), so its kernel contains \(mG_A\). These quotients are consequently cofinal among all finite quotients. Their inverse limit is \(P\). \(\square\)

### 5.1 A stronger natural formulation

For every finite group \(F\), restriction induces a natural bijection

\[
\operatorname{Hom}(G_A,F)\longrightarrow\operatorname{Hom}(D,F).
\]

For injectivity, put \(m=|F|\). Every element \(g\in G_A\) is congruent modulo \(mG_A\) to an element \(d\in D\), and every map to \(F\) kills \(mG_A\). Consequently two maps agreeing on \(D\) agree on every \(g\). This argument does not subtract maps into a possibly nonabelian target.

For surjectivity, a map from \(D\) to \(F\) kills every prime component not dividing \(|F|\) and factors through a finite coordinate product. The same finite-coordinate formula defines its unique extension to \(G_A\).

This fixes not just the list of finite quotient isomorphism types, but their maps and compatibility. In particular,

\[
\boxed{\widehat{G_A}=P\text{ under the canonical coordinate identification, for all }A.}
\]

The product \(P\) is topologically generated by \((1,1,\ldots)\) and has a computable inverse system independent of \(A\). This does **not** make \(G_A\) computable.

## 6. The missing information is an intrinsic divisibility pattern

For \(g\in G\), write \(p\mid_G g\) when there is \(y\in G\) with \(py=g\). This is a group-theoretic property, not a choice of coordinates.

For the distinguished element \(u_A=s_A(1)\), Theorem 5.1 gives

\[
p\mid_{G_A}u_A\quad\Longleftrightarrow\quad p\notin S_A.
\]

Consequently,

\[
\begin{aligned}
p_{2n}\mid_{G_A}u_A&\Longleftrightarrow n\in A,\\
p_{2n+1}\mid_{G_A}u_A&\Longleftrightarrow n\notin A.
\end{aligned}
\]

Exactly one of the two root equations is solvable.

### Lemma 6.1. Every nontorsion element has the same tail signature

If \(g=s_A(r)+d\) with \(r\neq0\), then for all but finitely many primes,

\[
p\mid_{G_A}g\quad\Longleftrightarrow\quad p\notin S_A.
\]

**Proof.** Exclude primes dividing the nonzero numerator or denominator of \(r\), and the finite support of \(d\). At any remaining prime, \(g_p\) is nonzero exactly when \(p\in S_A\). Apply Theorem 5.1. \(\square\)

Thus the class of \(S_A\) modulo finite symmetric difference can be recovered from the divisibility signature of **any** nontorsion element. It is an intrinsic invariant of the unmarked group.

### Theorem 6.2. Exact isomorphism classification

\[
\boxed{G_A\cong G_B\quad\Longleftrightarrow\quad A=^*B,}
\]

where \(A=^*B\) means finite symmetric difference.

**Proof.** Suppose \(f:G_A\to G_B\) is an isomorphism. The image of \(u_A\) has infinite order, so it is \(s_B(r)+d\) with \(r\neq0\). Isomorphisms preserve the solvability of every root equation. The exact signature of \(u_A\) and the tail signature of its image therefore imply \(S_A=^*S_B\). Because one prime is selected from each pair, this is equivalent to \(A=^*B\).

Conversely, if \(A=^*B\), then \(s_A(r)-s_B(r)\) has finite support for every rational \(r\). Hence the two subsets \(G_A\) and \(G_B\) of \(P\) are actually equal. Their normal-form coordinate systems differ by

\[
(r,d)\longmapsto(r,d+s_A(r)-s_B(r)).
\]

This supplies the isomorphism. \(\square\)

**Important correction to a tempting overstatement.** The unmarked invariant is \(A\) modulo finite changes, not the literal subset. The marked groups satisfy the sharper statement

\[
(G_A,u_A)\cong(G_B,u_B)\quad\Longleftrightarrow\quad A=B.
\]

The root signature of the distinguished element proves necessity. No uniform recovery of the literal original \(A\) from an unmarked group is asserted.

### Theorem 6.3. A homomorphism obstruction

If \(A\not=^*B\), every homomorphism \(f:G_A\to G_B\) has image in \(D\). In particular, neither group embeds in the other and neither is a quotient of the other.

**Proof.** A homomorphism preserves torsion and induces a map \(\mathbb Q\to\mathbb Q\), necessarily multiplication by a rational \(r\). If \(r=0\), the image is in \(D\).

Suppose \(r\neq0\). The image of \(u_A\) has the tail signature of \(S_B\). Whenever \(p\notin S_A\), a \(p\)-root of \(u_A\) maps to a \(p\)-root of its image. Lemma 6.1 implies \(S_B\setminus S_A\) is finite. Since the two sets select exactly one prime from each pair, this forces \(A=^*B\), a contradiction.

An injective map cannot send an infinite-order element to a torsion element. A surjection to \(G_B\) cannot have torsion image. \(\square\)

## 7. The exact computational requirement

A copy is a group on a computably named countable domain with decidable equality and group operations computable relative to an oracle \(X\). Equivalently, one can use a copy on \(\mathbb N\) with atomic diagram computable in \(X\). Here \(A\leq_T X\) means that membership in \(A\) is computable using \(X\).

### Theorem 7.1. Exact presentation-degree criterion

\[
\boxed{G_A\text{ has an }X\text{-computable copy}\quad\Longleftrightarrow\quad A\leq_T X.}
\]

**Sufficiency.** Suppose \(A\leq_T X\). Use the normal-form domain \(\mathbb Q\times D\). Reduced rationals and normalized finite-support prime vectors have decidable canonical codes, with a computable bijection to \(\mathbb N\). Equality and inverse are computable without additional information. To add two elements, evaluate \(c_A(r,t)\). Its support is confined to the finitely many prime divisors of the two denominators, and each coordinate requires only the corresponding selector bit. Thus addition is computable in \(X\).

The identity in Section 3.1 also shows that the operation in this particular normal-form copy computes the selector. The canonical copy has degree exactly \(\deg_T(A)\), not merely a degree bounded above by it.

**Necessity.** Let \(H\) be an \(X\)-computable copy of \(G_A\). Choose a name \(h\) for one nontorsion element. By Lemma 6.1, there is a finite bound \(N\) such that for every \(n\geq N\), exactly one of

\[
p_{2n}y=h,\qquad p_{2n+1}z=h
\]

has a solution, and the first has a solution exactly when \(n\in A\).

For such an \(n\), dovetail the two searches through the named elements of \(H\). Each individual equation check is decidable in \(X\). Exactly one search succeeds, so this decides the bit. Hard-code the finitely many initial bits, the name of \(h\), and \(N\) into the Turing procedure. This proves \(A\leq_T X\).

These are finite constants. They need not be recoverable uniformly from an arbitrary unmarked copy, and no such claim is used. With the distinguished element \(u_A\) named, the same decoding works uniformly without the finite exception set. \(\square\)

### Consequences

The least degree of a presentation of \(G_A\) is exactly \(\deg_T(A)\). In particular, \(G_A\) has a computable copy exactly when \(A\) is decidable. Every Turing degree occurs among groups with the *same fixed computable profinite completion*.

For example, the empty set gives a computable group. The diagonal halting set \(K\) gives a group with no computable copy and least presentation degree \(\mathbf 0'\). Higher iterates of the jump give successively stronger examples. These complexity claims refer to effective presentation, not to finite mathematical definability: the group defined using \(K\) still has a finite mathematical definition.

The notion of least degree of an isomorphism type is standard in computable structure theory [R1, R2]. We do not silently identify “a copy computable in \(X\)” with “a copy whose atomic diagram has degree exactly \(X\).” The theorem supplies the former equivalence and establishes the least degree. Nothing more is needed here.

## 8. Exact failure of reconstruction from all finite quotients

Let \(\mathcal F(G)\) denote the unmarked pro-object of finite quotient groups and transition maps. The source group itself and the evaluations of named source elements are not included as additional data. Theorem 5.2 gives

\[
\mathcal F(G_A)\cong\mathcal F(D)\quad\text{for every }A.
\]

### Theorem 8.1. No reconstruction depending only on this observation system

There is no isomorphism-invariant assignment \(R\) such that

\[
R(\mathcal F(G_A))\cong G_A
\]

for all \(A\).

**Proof.** Take \(A=\varnothing\) and \(B=\mathbb N\). Their finite-quotient systems are identical, but their groups are not isomorphic by Theorem 6.2. A single input observation system cannot be assigned both isomorphism types. \(\square\)

This is not merely the failure of a computable algorithm. It is an information loss in the observation system itself, so an unrestricted set-theoretic decoder depending only on that system also fails.

### 8.1 Why residual finiteness does not contradict this

For each fixed \(A\), the coordinate maps jointly separate the elements of \(G_A\). They induce an injective map

\[
G_A\hookrightarrow\varprojlim_N\prod_{i<N}C_{p_i}=P.
\]

What is not determined by the inverse system is **which dense subgroup is the admissible original image**. The completion specifies all compatible coordinate tuples. The original realization admits only the tuples in \(G_A\).

Thus elementwise separation and reconstruction of the object are different requirements. No existing theorem identifying a complete inverse-limit realization with \(P\) is contradicted: these \(G_A\) are proper, noncomplete dense subgroups.

### 8.2 The observation contract matters

The finite quotients contain no distinguished coherent image of \(u_A\). Adding that marked point to the inverse system retains its prime-coordinate pattern and therefore adds the missing selector information.

Root-solvability formulas in the original group are also additional information. They are not determined by the unmarked finite quotient system. Consequently, the theorem must not be paraphrased as “all finite mathematical observations are identical.” It concerns the full **unmarked finite-quotient system**.

### 8.3 Grammar implications

A finite formal expression containing an idempotent \(u_A\) as an unrestricted primitive can conceal all of \(A\). Naming the idempotent does not make its parameter information finite. An effective realization contract must account for the selector's description and evaluation, not only the number of symbols surrounding it.

The distinction is therefore between three mathematical tasks: construct the compatible ambient completion, select the intended dense realization, and make that selection effective. In this family the first task is fixed and computable, while the third has precisely the degree of \(A\).

## 9. Finite seeds still do not suffice

### Proposition 9.1. The endomorphism-seed rank is countably infinite

For every \(A\), a finite set of seeds cannot generate \(G_A\), even allowing every abstract group endomorphism. The same is true for topological generation in its subspace topology from \(P\).

**Proof.** By Theorem 5.1, \(\ker\pi_p=pG_A\). Every endomorphism preserves \(pG_A\), so a zero \(p\)-coordinate stays zero under every endomorphism. Equivalently, the composite with \(\pi_p\) factors through \(G_A/pG_A\cong C_p\), and is multiplication by a scalar on that coordinate.

Every element of \(G_A\) has only finitely many nonzero coordinates outside \(S_A\). A finite family therefore misses infinitely many unselected prime coordinates. All finite sums of its endomorphism orbits continue to vanish there. Each omitted coordinate projection is a non-generation certificate. Its kernel is closed, so taking the subspace-topology closure does not fix the failure.

Countably many seeds suffice because \(G_A\) is countable. Hence the rank is exactly \(\aleph_0\). \(\square\)

The completion has one topological generator, but every original group here has infinite finite-seed requirements. Neither of these seed ranks detects the varying Turing degree. The arithmetic and computational invariants measure different aspects of realization.

## 10. Escape any fixed finite-description grammar inside the same completion

Fix a grammar with countably many parameter-free finite descriptions. A valid description has one group isomorphism type as its semantics. Enumerate the descriptions as \(d_0,d_1,\ldots\), and write \(R_j\) for their outputs, assigning an arbitrary dummy output to invalid descriptions.

If \(R_j\cong G_B\) for some \(B\), choose one such \(B_j\). Otherwise put \(B_j=\varnothing\). This is a set-theoretic choice, not an asserted effective operation. Let \(\langle j,k\rangle\) be a fixed pairing bijection \(\mathbb N^2\to\mathbb N\).

For any \(C\subseteq\mathbb N\), define \(A_C\) by

\[
\begin{aligned}
\mathbf 1_{A_C}(2\langle j,k\rangle)
 &=1-\mathbf 1_{B_j}(2\langle j,k\rangle),\\
\mathbf 1_{A_C}(2\langle j,k\rangle+1)
 &=\mathbf 1_C(j).
\end{aligned}
\]

### Theorem 10.1. Continuum many escaping realizations

Every \(G_{A_C}\) lies outside the grammar, and distinct \(C\) give nonisomorphic, nonembeddable groups. All of them have profinite completion \(P\).

**Proof.** For a fixed \(j\), the first rule makes \(A_C\) disagree with \(B_j\) at infinitely many coordinates. Therefore \(A_C\not=^*B_j\), so \(G_{A_C}\not\cong R_j\) whenever \(R_j\) belongs to the family. When \(R_j\) does not belong to the family, nonisomorphism holds by definition.

If \(C\neq C'\), choose \(j\) where they differ. The second rule makes \(A_C\) and \(A_{C'}\) disagree on the infinite odd block indexed by \(j\). Apply Theorems 6.2 and 6.3. The common completion follows from Theorem 5.2. \(\square\)

Repeated diagonalization is essential. Disagreeing at only one bit against each output would not work, because finite changes do not change these unmarked isomorphism types.

The theorem proves grammar-relative finite nonrealizability. It does not prove that a named group is beyond every possible finite semantic definition. Nor does it give an algorithm evaluating an arbitrary grammar's semantic table. Enlarging the grammar or supplying an oracle changes the contract.

## 11. What has been established, and what has not

The ordinary proofs establish a common-completion family, its exact classification, a homomorphism obstruction, an exact oracle requirement, a nonsplitting theorem, and a repeated diagonal escape theorem. The group law is an explicit finite cocycle, so the construction is not only a cardinality argument.

The earlier direct-sum spectrum argument has known literature antecedents [R1]. A search of selected primary sources was used to anchor the terminology and identify that overlap. Historical novelty of this stronger combined family has not been established. No claim that the construction supersedes the classical theory of rank-one mixed abelian groups is made.

The finite arithmetic tests do not prove infinite noncomputability, global nonisomorphism, or the classification theorem. They check exact formulas, the cocycle law on a stated finite domain, roots and obstructions, quotient representatives, and the coordinate transport required by finite selector changes. The proofs above carry the universal claims.

Lean is not installed in the current runtime. No new Lean source has been represented as verified, and no Lean compilation is claimed.

## 12. References and source correspondence

**[R1]** Antonio Montalbán. *Computable Structure Theory: Within the arithmetic*. Draft of Part 1, compiled June 25, 2019. Definition III.36, Definition III.37, Example III.39, and the complementary-set coding paragraph on printed pages 49–50. The source explicitly contains the prime direct-sum enumeration-degree construction used in the inherited note. It does not serve as a citation for the new common-completion theorem proved here.

**[R2]** Wesley Calvert, Valentina Harizanov, and Alexandra Shlapentokh. “Turing degrees of isomorphism types of algebraic objects.” *Journal of the London Mathematical Society* 75 (2007), 273–286. DOI: 10.1112/jlms/jdl012. Preprint arXiv:math/0507128. Background for degrees of isomorphism types and arbitrary degrees in algebraic structures, not a substitute for the proof in Section 7.

**[R3]** Martino Lupini, Alexander Melnikov, and André Nies. *Computable topological abelian groups*. arXiv:2105.12897v2 (2021). Definition 3.3 gives computable profinite presentations. Section 3.2 recalls the symmetric cocycle construction of abelian extensions. These are background definitions. Profinite completion in this note is not Pontryagin duality, and the two operations are not being identified.

**Inherited source.** `inherited/REALIZATION_BOUNDARY_NOTE.md` contains the previous squarefree direct-sum boundary note. It is preserved unchanged. The input archive's hash and the fresh exact-check reports are in `verification/`.
