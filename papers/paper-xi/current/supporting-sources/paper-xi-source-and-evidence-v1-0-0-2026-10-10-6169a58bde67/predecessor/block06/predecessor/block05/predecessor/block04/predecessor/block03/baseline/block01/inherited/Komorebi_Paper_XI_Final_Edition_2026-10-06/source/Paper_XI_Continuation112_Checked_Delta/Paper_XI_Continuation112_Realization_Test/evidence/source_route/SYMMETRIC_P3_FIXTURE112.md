# Symmetric p3 torsors: a whole dimension9 Weil parameter

This strengthens the frozen p5 fixture without changing it. The proposal came from `/root`; `/root/lattice_route/weil_realization112` and `/root/lattice_route` checked it directly. The fresh reader `/root/lattice_route/audit_morita`, who did not author this construction, independently verified the field/group/representation formulas and source applicability. This document proves only the actual Galois/Clifford fixture; any actual simple-character realization is a separate arithmetic result. It does not assert an H5 witness or a new Lean theorem.

## Fields and explicit equations

Let F=F3((t)) and K=F81((t)). Choose a nonzero constant a with a^9=-a, and put b=a^3. Such a exists in the nonzero trace-zero line of F81/F9. It has order16 and degree4 overF3. The coefficients a,b are F3-independent: b=lambda a would imply a^9=lambda^4 a=a, contrary to a^9=-a.

For m in {1,5}, put f=a t^-m,g=b t^-m and define

\[
x^3-x=f,\qquad y^3-y=g,\qquad
z^3-z=(fy-gx)/2.
\]

Every nonzero F3-combination of f,g has pole m, prime to3, whereas wp(s)=s^3-s with a pole has pole divisible by3. Thus the first two classes are independent and K(x,y)/K has degree9.

The field K(x,y,z) has degree27. If z were already in K(x,y), its commuting translations alpha:x→x+1 and beta:y→y+1 would satisfy

\[
\alpha(z)-z=-y/2+r,\qquad
\beta(z)-z=x/2+s,\qquad r,s\in\mathbf F_3.
\]

Then alpha beta(z)-beta alpha(z)=1, a contradiction. Its27 automorphisms are

\[
h(u,v,c):(x,y,z)\mapsto
(x+u,y+v,z+(vx-uy)/2+c),
\]

with u,v,c inF3 and symmetric Heisenberg law

\[
h(u,v,c)h(u',v',c')
=h(u+u',v+v',c+c'+(uv'-vu')/2).
\]

The commutator is central coordinate uv'-vu'. All degree3 subextensions arise from the coefficient span and are ramified; a nontrivial unramified3-group quotient would yield an unramified degree3 subextension. The extension is therefore totally ramified.

The two torsors for m1=1 and m2=5 are linearly disjoint. A nontrivial common3-group Galois quotient would yield a common degree3 AS class. Distinct leading pole orders1,5, both prime to3, prohibit a nonzero class common to those spans. Write their groups as H1,H2, each the order27 Heisenberg group.

## The central breaks really are4m/3

The normalized equation needed for Imai's published Example3.8(1), equations(3.53)–(3.56), follows by setting w=z+xy/2. Direct expansion gives

\[
\wp(xy)=fy+gx+fg,\qquad
\wp(w)=fy+fg/2.
\]

Its coefficients are a_I=f,b1=g,b2=fg/2. The perfect residue and total-ramification hypotheses hold; the positive pole orders m,m,2m are prime to3; the leading coefficients a,b are F3-independent; the source's nilpotency parameter n=2 satisfies n≤p-1. In the logarithmic differential convention,

\[
db_2-f\,dg=(g\,df-f\,dg)/2=0.
\]

The central-break formula consequently yields

\[
r_2=\max(-\infty,m/3+m,m+m/3)=4m/3.
\]

In particular it is false to reuse2m from the unsymmetrized p5 fixture. The corresponding factor slopes are {1,4/3} and {5,20/3}: each nontrivial linear irreducible has slope m, and each nonlinear irreducible has nontrivial scalar center and slope4m/3. The retrieved primary source and exact hypotheses are pinned in `IMAI_RETRIEVAL112.json`; no new article leaf is used here.

These factor slope sets are disjoint. As in the detailed p5 proof, every product irreducible is a tensor, and has slope equal to the maximum of the unequal factor slopes: between them the lower factor is trivial on the actual upper subgroup and the higher factor has no invariants. Intersecting kernels of all irreducibles trivial on that upper subgroup reconstructs the subgroup. This proves the actual product filtration, rather than assuming it from projections.

## Representation, balanced center, and ambient filtration

Fix a primitive cube root zeta and define on complex functions F3→C

\[
(\tau(u,v,c)h)(s)
=\zeta^{c+uv/2+vs}h(s+u).
\]

The symmetric group law gives an honest irreducible representation of dimension3. Modulation has three distinct eigenspaces and translation permutes them transitively. Both factors have the same central character chi(c)=zeta^c.

The tensor R0=tau1⊗tau2 is irreducible of dimension9. Its exact kernel is the anti-diagonal center

\[
D=\{(z(c),z(-c)):c\in\mathbf F_3\}.
\]

Let M=(L1L2)^D. Then G'=Gal(M/K)=(H1×H2)/D is the rank4 Heisenberg group of order3^5 and R0 is faithful on it. Upper quotient compatibility identifies the images of Z1×H2 and1×H2, so the ambient4/3 jump disappears. Away from endpoints,

| Ambient upper range | Group |
|---|---|
| 0<u<1 | G' |
| 1<u<5 | G1'≅H2 |
| 5<u<20/3 | common center G2'≅F3 |
| u>20/3 | 1 |

R0|G1' is tau2-isotypic with multiplicity3, and tau2|G2' is chi-isotypic with multiplicity3. Both constituent classes are stable: the outer H1 commutes with H2, and conjugation from H2 is inner. Both quotients are F3², their projective commutators are zeta^(uv'-vu'), and the terminal constituent has dimension1. Thus

\[
9=3\cdot3\cdot1.
\]

The full finite envelope is the literal orthogonal sum of those two source planes, with the common central character retained once.

Here1 and5 are the actual upper labels in the **original ambient extension** M/K and, after unramified descent, M/F. They are not claimed to be native upper labels of the two separate subgroup field extensions. Ambient lower breaks are1,37,172. Viewing G1' as Gal(M/M^{G1'}) requires the subgroup lower filtration and its own Herbrand function, giving native upper breaks37,52. This distinction is consistent with Definition9.1's one declared break and with breaking up one original filtered atom.

## Whole Weil parameter overF, with explicit Frobenius

Coefficient Frobenius on K/F sends (a,b) to (b,-a). It lifts to an order4 automorphism sigma by

\[
\sigma(x)=y,\quad\sigma(y)=-x,\quad\sigma(z)=z.
\]

It preserves the symmetric third equation exactly. It fixes the center and conjugates Heisenberg coordinates by (u,v,c)→(-v,u,c). Thus D is stable and Gal(M/F)=G'⋊C4.

Let

\[
(S h)(s)=3^{-1/2}\sum_{r\in\mathbf F_3}\zeta^{-sr}h(r).
\]

The inverse normalized Fourier transform satisfies S^4=1 and

\[
S\tau(u,v,c)S^{-1}=\tau(-v,u,c).
\]

Therefore S⊗S extends R0 to the finite semidirect product. Inflating it through W_F gives a whole smooth irreducible Weil rho with dimension9 and irreducible wild restriction on the same carrier. Irreducibility of that restriction already proves irreducibility of rho. Geometric Frobenius is represented by the inverse of the displayed arithmetic-Frobenius operator.

The positive upper filtration survives unramified descent. The scalar center remains active until20/3, so the sole ordinary slope of rho is20/3. Its Swan number is9·20/3=60. Its projective filtered-Clifford transitions are nevertheless1 and5. This is not an orbit of selected wild constituents padded to another ambient dimension.

Inertia maps to the3-group G'. Its actual tame-inertia image is trivial, so the declared tame stabilizer is C=1. The explicit C4 is an unramified Frobenius complement, not tame inertia. Its Fourier normalization is an actual source operator, not proof of an actual canonical type-side phase. No stronger non-induced primitivity assertion is made.

## Exact remaining arithmetic scope

Both packets pass the residue-cardinality test for k_F=F3, and their dimensions multiply to the actual ambient rank9. An actual local H2 bridge would still need the corresponding actual maximal simple character, quotient pairing, central-character compatibility, and required action. A claimed GL9 degree-spectrum obstruction to one assembled eta of dimension9 must be established from canonical BK H/J lattices; it is not a consequence of this finite source construction. Those type-side results are audited independently in the arithmetic route. This file supplies no H5, no type of LLC(rho), no altered twist family, and no Claim16.2 closure.
