# A bounded binder cannot hide from every faithful finite cut

**Status.** Ordinary proof of a compactness theorem and its application to a fixed matrix binder template. This does not prove the finite solvability required by the original Paper XI Theorem 16.2. In particular, it does not establish a general native-action or full-character realization from H1–H4.

## 1. Exact target

Let \(F\) be a nonarchimedean local field, \(\mathcal O\) its valuation ring, \(\pi\) a uniformizer, and \(k=\mathcal O/\pi\mathcal O\) its finite residue field. Fix a finite number of variables \(z=(z_1,\ldots,z_m)\in\mathcal O^m\).

A fixed lattice of matrix coefficients, including a lattice with negative valuation bounds, can be written in this form by choosing an \(\mathcal O\)-basis and rescaling each coefficient once. The rank, number of variables, and all valuation bounds remain fixed throughout the argument.

Let \(X\subseteq\mathcal O^m\) be a closed set. It can include a prescribed leading certificate, such as a list of nonzero graded-lane coefficients: requiring a residue to belong to \(k^\times\) is both open and closed, so it is an allowed closed condition. Let

\[
f_j:X\longrightarrow\mathcal O,\qquad j=1,2,\ldots,
\]

be continuous functions. Exact matrix equations are represented entry by entry, after clearing fixed denominators. A finite list is repeated or padded with zero equations.

For \(n\geq1\), define the *full level-\(n\) system*

\[
C_n=\{z\in X:f_j(z)\in\pi^n\mathcal O\text{ for every }1\leq j\leq n\}.
\]

The word “full” matters: constraints are imposed simultaneously on one tuple of variables. It is not enough to solve each equation separately, to check only numerical invariants of a representation, or to permit a new rank or unbounded coefficient valuations as \(n\) increases.

## 2. Compact binder theorem

**Theorem.** The following are equivalent:

1. There is \(z\in X\) with \(f_j(z)=0\) for every \(j\).
2. \(C_n\ne\varnothing\) for every \(n\geq1\).
3. Every finite subset of the exact equations is simultaneously soluble to every finite precision, within the same set \(X\).

**Proof.** The implications (1)⇒(3)⇒(2) are immediate. The set \(\mathcal O^m\) is compact: from any sequence one first extracts a subsequence constant modulo \(\pi\), then one constant modulo \(\pi^2\), and so on; the diagonal subsequence converges by completeness. The finite residue field supplies the finite choice at each extraction. Thus its closed subset \(X\) is compact.

Each \(C_n\) is closed because each \(f_j\) is continuous and \(\pi^n\mathcal O\) is closed. Also \(C_{n+1}\subseteq C_n\). If all \(C_n\) are nonempty, choose \(z_n\in C_n\). Compactness gives a convergent subsequence \(z_{n_\ell}\to z\in X\). For every fixed \(j,r\), all sufficiently large \(\ell\) have \(n_\ell\geq\max(j,r)\), whence \(f_j(z_{n_\ell})\in\pi^r\mathcal O\). Continuity and closedness give \(f_j(z)\in\pi^r\mathcal O\). Since this holds for every \(r\) and \(\bigcap_r\pi^r\mathcal O=\{0\}\), we have \(f_j(z)=0\). This proves (2)⇒(1). ∎

There is no assumption that the maps from level-\(n+1\) solutions onto level-\(n\) solutions are surjective. Some low-precision choices can be dead ends. Compactness selects a compatible limiting sequence from the entire family. An algorithm that insists on extending one arbitrary low-precision solution can fail even when the theorem applies.

The theorem also holds for any family of closed constraints with the finite intersection property. Countability is used here only to present an explicit sequential approximation procedure.

## 3. Finite obstruction certificates

Assume now that \(X\) is a union of residue classes modulo \(\pi^s\) for a fixed \(s\geq1\), and that the equations are integral polynomials, or ratios of integral polynomials whose denominators are units on \(X\). Their reductions modulo \(\pi^n\) depend only on the variables modulo \(\pi^n\). For rational functions this follows because the inverse of a unit modulo \(\pi^n\) is determined by that unit modulo \(\pi^n\).

For \(n\geq s\), let

\[
S_n=\left\{\bar z\in X\bmod\pi^n:
 f_j(\bar z)=0\bmod\pi^n\ (1\leq j\leq n)\right\}.
\]

This is a finite set with at most \(|k|^{mn}\) candidates. Each residue tuple has an actual lift to \(X\); consequently \(S_n\ne\varnothing\) if and only if \(C_n\ne\varnothing\). The compact binder theorem gives

\[
\boxed{\text{No exact binder in this template}\quad\Longleftrightarrow\quad
S_N=\varnothing\text{ for some finite }N.}
\]

If coefficients, equations, and residue tests are effectively given, this is an implementable semidecision procedure for nonexistence:

1. Increase \(n\), starting at \(s\).
2. Enumerate \((\mathcal O/\pi^n)^m\), retaining the allowed leading residues.
3. Check the first \(n\) equations modulo \(\pi^n\) on each tuple.
4. When no tuple remains, retain the equation list, residue precision, and exhaustive verification as a finite obstruction witness.

A compact equivalent certificate is any verified derivation that makes this finite system inconsistent. Exhaustive enumeration is not required when elimination or a direct identity gives such a derivation.

This procedure eventually stops if the bounded template has no solution. It need not stop when a solution exists. The theorem supplies no universal bound on \(N\), and no algorithm for choosing an infinitely extendible low-precision tuple in advance. Finite searches that have not exhausted a full level give no nonexistence certificate.

For continuous functions more general than the displayed algebraic ones, compactness still proves the existence statement. A finite, effective test additionally requires an effective uniform modulus of continuity and an effective presentation of \(X\). The needed input precision can exceed \(n\).

## 4. Matrix binder specialization

Fix all of the following:

- a finite-dimensional matrix algebra \(A\), a lattice chain and its radical filtration \(\mathfrak P^a\), and a closed, lattice-bounded coefficient template \(L\subseteq A\);
- the original parameters \(\gamma',b_0\), a fixed continuous linear corestriction \(s\), and the ambient rank;
- a fixed integer \(q>0\) and a derived complete chain of rank \(r\geq2\), with \(\gcd(q,r)=1\);
- the prescribed native and character data, once expressed as actual conditions on the same finite tuple of variables.

Put

\[
Q(x)=-s(xb_0x),\qquad
\beta(x)=\gamma'+[x,b_0]-xb_0x.
\]

The conditions \(x^2=0\) and \(Q(x)=Q_\mathrm{target}\) are polynomial matrix equations. The condition that every grade-\(-q\) lane coefficient of \(Q(x)\) is nonzero depends only on finitely many residue coefficients. It is therefore a closed and open restriction on the compact parameter lattice. Fixed membership conditions such as \(x\in\mathfrak P^a\) are closed; they can instead be built into the coordinate lattice.

It follows that **if all simultaneous congruence systems for this fixed template and these actual native/character equations are soluble, then there is an exact square-zero binder carrying the same leading primitive cycle.** No leading coefficient can disappear at the limit, since it was required to stay nonzero at a fixed finite precision.

Under all of the hypotheses of the retained binder proposition—initial minimal simple stratum, normalization and filtration identities for corestriction, \(b<n\), \(q=b-2a>0\), and the primitive leading cycle—the resulting \(\beta(x)\) then has the arithmetic field and critical-exponent conclusions of that proposition. Compactness does not prove those hypotheses. It preserves the supplied finite leading certificate so that the previously established proposition applies to the limiting binder.

In particular, merely asking that \(F[\beta]\) be a field, or that a determinant be nonzero, would not be an adequate replacement for that certificate: these requirements need not survive an unrestricted limit. A fixed determinant valuation prevents the determinant from becoming zero. A fixed primitive leading cycle, under the retained proposition's other hypotheses, ensures the required arithmetic field conclusion; a determinant valuation alone does not.

## 5. Native actions and full characters

There are three separate questions: whether the original data admit a faithful equation encoding; whether the encoded conditions are closed; and whether every finite simultaneous system has a solution. Compactness answers only the passage from the third assertion to exact solvability, once the first two have been established.

### Native matrices

For a finite native group, fixed matrix action identities, multiplication identities for its proposed lifts, and intertwining equations are polynomial after introducing entries for the lifts. Inverses can be represented by auxiliary matrices \(g,h\) with \(gh=hg=I\), provided both sets of entries have fixed bounds. Alternatively, restricting \(g\) to a fixed compact subgroup, such as \(1+\mathfrak P^a\) for \(a\geq1\), makes inversion continuous on a compact set.

Thus actual finite native equations can be included. It is not enough to verify only that the action descends to a prescribed symplectic quotient. That quotient condition omits any additional scalar, marking, or full-character identity unless it has been explicitly encoded.

For identities on a compact metrizable source group \(H\), suppose the two evaluations \((x,h)\mapsto A_x(h)\) and \((x,h)\mapsto B_x(h)\) are jointly continuous in the parameter \(x\) and the source element \(h\), with values in a Hausdorff target. Equality can then be checked on a countable dense subset of \(H\): continuity in \(h\) extends the equality to all of \(H\), while continuity in \(x\) makes each test a closed condition on the parameter space. A finite generating list suffices only when such a list, or an appropriate finite quotient, has actually been supplied; it is not assumed for arbitrary local pro-finite groups.

### A uniform finite test for continuously parameterized characters

**Lemma.** Let \(X\) be compact, let \(H\) be a profinite group, and let
\[
\Phi:X\times H\longrightarrow\mathbb C^\times
\]
be jointly continuous, with \(\Phi_x(h)=\Phi(x,h)\) a group homomorphism for every \(x\). There is one open normal subgroup \(U\triangleleft H\) on which every \(\Phi_x\) is trivial. Consequently all the characters factor through the same finite quotient \(H/U\).

**Proof.** The image of each \(\Phi_x\) is a compact subgroup of \(\mathbb C^\times\), so it lies in the unit circle. Choose an open arc \(V\) around \(1\) in that circle which contains no nontrivial subgroup; for example take \(\operatorname{Re}(z)>0\). Joint continuity at each \((x,1)\) gives a neighborhood \(A_x\) of \(x\) and an open subgroup \(U_x\) of \(H\) such that \(\Phi(A_x\times U_x)\subseteq V\). Finitely many \(A_x\) cover \(X\). Choose an open normal subgroup \(U\) contained in the intersection of the corresponding finitely many \(U_x\). For every parameter \(y\), the subgroup \(\Phi_y(U)\) lies in \(V\), hence is trivial. ∎

The assertion about the arc follows elementarily: if \(z\ne1\) is on the unit circle and its angle has absolute value in \((0,\pi]\), some positive power has angle in \([\pi/2,3\pi/2]\) modulo \(2\pi\), so that power has nonpositive real part.

Apply the lemma to the ratio

\[
\Phi_x(h)=\Theta_x(\iota_x(h))\,\theta(h)^{-1}
\]

when \(H\) is the fixed compact source group, \(\theta\) is its supplied full character, \(\iota_x\) is an actual homomorphism into the proposed host, and the displayed evaluation is jointly continuous. Then requiring the **entire** character identity

\[
\Theta_x\circ\iota_x=\theta\quad\text{on }H
\]

is equivalent to finitely many equalities on representatives of \(H/U\). Its solution set is closed. Indeed the possible values belong to the finite group of roots of unity of order dividing the exponent of \(H/U\); each equality is consequently also an open condition. If desired, its failure indicator is a continuous \(\{0,1\}\)-valued function and hence can be included among the functions in the compact binder theorem. An effective finite-cut algorithm still needs effective access to these evaluations and their uniform precision bound. This is a full-character test, not just a test on the central quotient.

Crucially, neither the actual maps \(\iota_x\) nor the jointly continuous character family \(\Theta_x\) has been constructed by this lemma. Those are input obligations. If the domains vary with \(x\), fixed identifications or an equivalent continuous presentation must first be supplied. If the relevant group is noncompact, the assertion above covers its compact part only; values on any extra generators, including scalar valuation directions, must also be fixed or separately imposed.

## 6. A finite witness already visible in the cubic corner

For the corner in `EXPLICIT_BINDER_SECTION.tex`, all sixteen coefficients lie in a fixed copy of \(\mathbb F_3[[t]]^{16}\). The target parameters are

\[
(u,v,w,p,q),\qquad u,v,w\in\mathbb F_3^\times,
\quad p,q\in\mathbb F_3.
\]

Its exact coordinate identities imply, already on residues,

\[
u=\bar c\bar d,\qquad v=\bar a\bar b,
\qquad w=\bar b\bar c,
\]
\[
p=\bar c(\bar a-\bar P),\qquad
q=\bar b(\bar d-\bar P).
\]

For the target \((1,1,1,1,2)\), the first three equations force
\(\bar a=\bar c=\bar d=\bar b\ne0\), because every nonzero element of \(\mathbb F_3\) has square one. The last two equations then force \(p=q\), contradicting \(1\ne2\).

This is a finite obstruction certificate for the **entire** fixed corner, even when its entries are arbitrary infinite power series. It uses only the indicated finitely many coefficients of the output. Additional deeper coefficients cannot repair this residue contradiction. Its force is limited to that corner: the target has not been shown to be forced by an admitted original input, and a larger template need not satisfy its invariant.

Conversely, the target \((1,1,1,2,2)\) has an explicit polynomial solution in the retained six-entry template. Its earlier failure in a smaller finite coefficient search was a support/degree restriction, not an obstruction requiring a new infinite global object.

## 7. Why the bounds and closed conditions matter

Each omitted hypothesis has a concrete failure mode.

**Unbounded coefficients.** On \(F\), the first \(n\) conditions in the list
\[
v(x)\leq-j\qquad(j=1,2,\ldots)
\]
have the solution \(x=\pi^{-n}\). There is no element satisfying all of them. These solutions escape every fixed compact coefficient lattice.

**A nonzero condition without a leading certificate.** On \(\mathcal O\setminus\{0\}\), every congruence \(x\equiv0\bmod\pi^n\) has a solution, for example \(\pi^n\). The exact equation \(x=0\) has none in this set. The omitted point is precisely the limit; this domain is not closed.

**Separate finite tests.** The equations \(x=0\) and \(x=1\) are each soluble, but their joint reduction modulo \(\pi\) is not. Finite breakwise constructions do not supply simultaneous congruence solutions unless their common variables and identifications have been matched.

**Incomplete tests.** Every finite test of a list of quotient invariants can pass while a full-character or native lift condition fails, because that condition was never tested. The theorem applies to a faithful encoding of the full claim, not to a chosen set of necessary invariants.

## 8. Consequence for the original gap

Within one fixed rank and bounded matrix template, preserving an explicit leading arithmetic certificate, an exact global binder cannot fail while every faithful simultaneous finite cut succeeds. The sharp remaining question is therefore:

\[
\boxed{\begin{gathered}
\text{Do H1–H4 imply nonemptiness of every full finite system}\\
\text{for a faithfully encoded, uniformly bounded realization template?}
\end{gathered}}
\]

This note does not establish that implication. In particular, it supplies no uniform template containing a solution for every original admitted input, no native/full-character encoding for those inputs, and no proof that the resulting finite systems are nonempty. It does show that, after those obligations are fixed, lack of reduction-map surjectivity is not itself an additional obstruction and nonexistence has a finite witness inside the template.

No H5 assertion, universal arithmetic realization, or change to the 65/66 status follows from this result alone.
