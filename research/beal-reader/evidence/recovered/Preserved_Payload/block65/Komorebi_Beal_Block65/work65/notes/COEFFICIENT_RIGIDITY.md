# B65.1. Conductor-independent normalized coefficient rigidity

## Statement

Retain TARGET_CONTRACT.md and actual depth one. Suppose beta descends to
H1(Q,k(chi^-1)). Normalize the common classes by a5=1, so

    alpha=u[phi]+r[3]+[sqrt5],     u,r in k^*.

Then

    u^7=-u,      r in F7^*,

and the normalized descended beta class has an F7-valued representative.
Equivalently alpha=(v*w,r,1) with v,r in F7^*. There are36 such natural
coefficient directions, rather than2304. No finite conductor bound is used.

This is a theorem about cohomology coefficients in the normalized actual
trace-product system. It is NOT descent of the Tate lattice, the entire
representation, the Jacobian, or all natural coefficients to F7.

## 1. The three Kummer coordinates are independent

Let L=K(zeta7), Delta=Gal(L/K), so |Delta|=6 and chi(Delta)=F7^*.
The fields K and Q(zeta7) are linearly disjoint: the only quadratic subfield
of Q(zeta7) is imaginary, whereas K is real. Equivalently their intersection
has degree dividing2 and3 after taking the maximal real cyclotomic subfield.
Thus [L:K]=6 and Gal(L/Q) is the product of the base involution and Delta.

The classes [phi],[3],[sqrt5] are independent in K^*/K^{*7}.
Valuation at the prime above3 forces the exponent of3 to be0 modulo7.
Valuation at the prime above5 similarly forces the exponent ofsqrt5 to be0.
Phi is not a seventh power: a seventh root a in K would be an algebraic
integer and a unit. Under the positive embedding, 1<a=phi^(1/7)<phi.
Its norm is-1, so its integral trace is a-a^-1, strictly between0 and1.
This is impossible. If phi^j is seventh for1<=j<=6, Bezout with gcd(j,7)=1
would make phi seventh as well.

The restriction map K^*/K^{*7} -> L^*/L^{*7} is injective. Indeed, if x=y^7
in L, then x^6=Norm(y)^7, and Bezout between6 and7 makes x a seventh power
in K. Hence the three independent classes remain independent in L.
Kummer theory (Milne CFT VII Appendix A, Theorem A.3) gives a surjective
homomorphism

    kappa=(X,Y,Z):G_L -> F7^3.

Its coordinates use one fixed identification mu7=F7. No local root changes
are made between X,Y,Z and the trace-product normalization.

## 2. The opposite character values vary independently of all three coordinates

On G_L the coefficient action is trivial. The restriction B(g)=beta(g)
is therefore an additive homomorphism, canonical on its cohomology class.
Its image B0 is a nonzero F7-subspace of k. If the restriction were zero,
inflation-restriction and |Delta|=6 prime to7 would make beta zero globally.

Consider the joint image

    W=image(G_L -> F7^3 plus B0),   g |-> (kappa(g),B(g)).

It is an F7-linear subspace. For h in G_K with chi(h)=a, conjugation acts
on the first coordinates by a and on B by a^-1. Choose a=3, a^-1=5.
The eigenspace projection (T-5I)/(3-5) preserves W and extracts its first
three coordinates. The complementary projection extracts its B-coordinate.
Since both coordinate projections are surjective by definition,

    W=F7^3 plus B0.                                      (1)

This is an equality of the ACTUAL finite joint image. It is not an assumption
that independent abstract local classes may be assigned freely. Distinct
cyclotomic characters are essential to the proof.

## 3. Base conjugation and actual Frobenius realization

Choose a lift j of the nontrivial automorphism of K/Q with chi(j)=1. The
normalized Kummer classes satisfy

    [j(phi)]=-[phi],   [j(3)]=[3],   [j(sqrt5)]=[sqrt5],

because j(phi)=-phi^-1, j(sqrt5)=-sqrt5 and -1 is itself a seventh power.
As j fixes mu7, for g in G_L:

    kappa(j g j^-1)=(-X(g),Y(g),Z(g)).

The assumed cohomology descent of beta, and chi(j)=chi(g)=1, give

    B(j g j^-1)=B(g).                                    (2)

The kernels of these homomorphisms define a finite extension E/L, Galois
over Q: their joint kernel is stable under Delta and j by the displayed
transformation rules. The image Gal(E/L) is W.

For ANY (x,y,z,b) in W, Chebotarev for the finite Galois extension E/Q
provides rational primes ell with that Frobenius conjugacy class. Because
this element projects trivially to Gal(L/Q), such primes split completely
in L. A suitable prime above ell realizes the chosen element itself.
Discard the finitely many bad primes of the actual Jacobian and all ramified
primes of E. Infinitely many remain. Thus the trace-product identity and
common-polynomial rule apply to the paired K-primes for every prescribed
joint vector in (1).

This is an existence statement at necessarily GOOD primes after excluding
a finite set. It is not an effective bound for the next auxiliary prime,
nor a count of primes already tested.

The two actual products at these places are

    p_plus  = b(u*x+r*y+z),
    p_minus = b(-u*x+r*y+z).                              (3)

They belong to the correction set of ONE actual rational quartic.
The finite-curve identity delta'=phi^2 delta proves that common-polynomial
statement without a semilinear map of Tate lattices. The correction set is
one element or a pair of coefficient-conjugate elements of k.

If x,b are nonzero, (3) are distinct because u!=0. They must therefore be
conjugate under z |-> z^7. Since2 is invertible, this means

    b(r*y+z) in F7,       (b*u*x)^7=-b*u*x.               (4)

We use no identification of the BASE radical sqrt5 with the COEFFICIENT
root w. The latter appears only after deriving its trace-zero line.

## 4. Two independent probes determine the coefficients

By (1), for every b in B0\{0} both choices (x,y,z)=(1,0,1) and (1,1,0)
occur at good split Frobenius elements.

The first choice in (4) gives b in F7^* and bu trace-zero. Hence B0=F7
and u^7=-u. The second choice gives br in F7, so r in F7^*.
The trace-zero subspace of k is F7*w because w^2=5 and w^7=-w.
Therefore u=v*w with v in F7^*, proving the claimed36 normalized directions.

To descend coefficients of the class itself, quotient the coefficient module
k(chi^-1) by F7(chi^-1). Its restriction to G_L is zero by B0=F7.
Inflation-restriction for G_Q/G_L, of order12 prime to7, makes that quotient
cohomology class zero. The long exact sequence for the coefficient modules
then puts the normalized descended class in the image of

    H1(Q,F7(chi^-1)) -> H1(Q,k(chi^-1)).

Thus an F7-valued representative exists. Values on G_L, and tame inertia
coordinates in the declared prime normalizations, are genuinely F7-valued.
Values of an arbitrary cocycle representative outside G_L need not already
be F7-valued before adjusting by a coboundary. QED.

## Limits and controls

The proof requires actual n1 trace products, u!=0, and cohomology descent of
beta. There is no assertion for a beta without that descent, nor for arbitrary
n>=2. The Kummer independence and distinct Delta characters supply the joint
values; a single observed local pair does not.

For example u=1, beta=w and (X,Y,Z)=(1,0,0) give the conjugate pair w,-w,
although u is not trace-zero and beta is not F7-valued. This valid local
algebra example fails the independent (1,0,1) probe. It prevents inferring
global coefficient rigidity from a lone finite prime.

The finite algebra scripts independently verify all110592 nonzero(u,r,b)
triples. The first probe leaves1728, and the two probes leave216, exactly
u in wF7^*, r,b in F7^*. All74088 further coordinate triples on these survivors
and16807 eigenprojection vectors pass. These checks do not prove Chebotarev
or Kummer theory. The universal argument is the written proof above.
