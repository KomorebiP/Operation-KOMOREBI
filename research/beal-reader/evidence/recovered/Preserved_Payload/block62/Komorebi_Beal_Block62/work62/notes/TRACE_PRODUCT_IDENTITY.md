# B62.1. Frobenius trace correction and the two actual endpoint classes

All arithmetic applications retain TARGET_CONTRACT.md. The coefficient ring is
O, the unramified quadratic extension of Z_7. Its residue field is k=F49.
The symbol w below is a COEFFICIENT-field element with w^2=5. It is not the
base-field radical in K=Q(sqrt5), nor a claimed comparison of Tate lattices.

## Exact determinant calculation

Suppose the actual depth is n=1, and let v be a prime outside 2,3,5,7 with
residue norm Q=1 mod7. Suppose beta is unramified at v. The natural class alpha
is also unramified there: this holds both at good reduction and at the variable
bad primes by the inherited natural-monodromy statement. On an arithmetic
Frobenius lift use the same fixed global natural basis:

    F = [[a,b],[7c,d]],   det F=Q,  a=Q mod7, d=1 mod7.

Write d=1+7D and tr(F)=Q+1+7T. Then a=Q+7(T-D), and

    bc = T+(Q-1)D+7TD-7D^2.                          (1)

Since Q=1 mod7,

    T mod7 = (b mod7)(c mod7).

The retained cocycles are alpha(g)=b(g) mod7 and beta(g)=c(g)/chi(g) mod7.
Here chi(F)=Q=1 mod7, so

    (tr_O(F)-Q-1)/7 mod7 = alpha(F) beta(F).          (2)

Equation (2) uses the ACTUAL coefficient-field trace, not half the rational
four-dimensional trace and not a guess of an independently chosen local
representation. The numerator is divisible by7 by the residual diagonal data.

The calculation works with 7 replaced by 7^n if eta_n is fully trivial modulo
7^n. The released depth-one application needs only the n=1 case.

## Values of classes and normalization

The coefficient characters chi and chi^-1 are trivial on the full local group
at these places. For an unramified class, its Frobenius value is independent
of the choice of Frobenius lift and of the cocycle representative: local
coboundaries vanish. All uses of (2) below are at primes outside the stipulated
complete beta conductor. No Frobenius value is assigned to a ramified beta.

A diagonal change of global basis rescales alpha by z and beta by z^-1.
Their product is unchanged. Thus a5 may be normalized to1 once globally without
losing the trace relation or fixing an artificial scale for beta. Its inertia
coordinates are still allowed to range over all of k. This is not coefficient
field descent.

## Good reduction and bad reduction give different tests

At a variable BAD place the exact toric trace is Q+1. Equation (2) gives
alpha(F) beta(F)=0. Moreover, if phi is not a seventh-power residue, the inherited
period obstruction and B61.1 force beta(F)=0. This stronger bad-place conclusion
uses eta_1=1, which is automatic in the retained residual orientation.

At a GOOD place, the right-hand side must instead equal the actual first trace
correction obtained from its Frobenius polynomial. It need NOT be zero. An
exact local matrix illustrating the distinction is

    F=[[-6,1],[-35,1]],  det F=29, tr F=-5.

It has residual diagonal(1,1), exact lower-left depth one, and product
alpha(F)beta(F)=2 mod7. Its trace satisfies the rank-two Weil bound. It is an
algebraic local control, not a claimed global Frey representation.

The hypothesis Q=1 mod7 cannot be deleted. For F=[[5/4,1],[7,8]], det F=3,
the trace correction is6 mod7 but bc=1 mod7. Equation (1), not an incorrectly
simplified formula, explains the difference.

## Extracting all possible corrections from the rational polynomial

For an actual good place write

    P(X)=(X^2-tau X+Q)(X^2-sigma(tau)X+Q)
        =X^4-SX^3+B X^2-QSX+Q^2.

The possible value of (tau-Q-1)/7 lies in k and its trace and norm are

    trace = (S-2(Q+1))/7 mod7,
    norm  = ((B-2Q)-(Q+1)S+(Q+1)^2)/49 mod7.          (3)

Both numerators have the stated divisibility for the retained scalar residual
trace. Equivalently D=S^2-4(B-2Q)=5v^2 and the possible roots are

    ((S-2(Q+1))/7 +/- (v/7) w)/2 mod7.

The primary uses the exact integer discriminant. The independent program
enumerates the49 elements of k by the two invariants in (3). Agreement does
not assume which coefficient conjugate occurs at a split base-field prime.
For the exclusion we even allow either conjugate to be chosen independently
at each test place and for each local residue. Empty intersection of this
larger necessary system is sufficient. No semilinear lattice comparison or
unstated matching of base and coefficient radicals is used.

## Evidence

There is a displayed universal proof, plus exhaustive checks of all117649
triples (D,b,c) in k^3 in O/49 at Q=29. This finite matrix check has one
implementation. The independent point-count/residue/sieve program is separate,
but is not a second matrix checker or an independent mathematical reviewer.
