# Why an abstract higher Kummer lift alone does not finish depth two

At eta_2=1 the actual natural upper triangular reduction modulo49 defines a
Kummer-type extension class A_2 lifting alpha. Its ramification need not be
restricted to the three generators phi,3,sqrt5 used by the RESIDUAL class.
At a variable prime of content t=1, natural inertia is divisible by7 but not
necessarily49. Coefficients of the form7d[pi_v] are therefore allowed in
an abstract lift. Omitting these terms would silently import a false
higher-level ramification restriction.

## B59.8. An exact correction-space countertest

Take the twelve prime ideals above U and the following twelve base-field
units at those ideals:

    phi,3,sqrt5,pi11,bar_pi11,pi19,bar_pi19,
    pi31,bar_pi31,pi41,bar_pi41,pi59.

The pi generators are the exact ones retained in Blocks57–58. Their
supports, as well as3 andsqrt5, are outside U. All these variable rational
primes are already forced divisors in the depth>=2 branch. Neither2 nor7
is used in this test.

The twelve-by-twelve residue-log matrix, with these elements as rows,
has integer determinant

    -237892440 = 5 modulo7.

Therefore the TRANSPOSE evaluation map from correction coefficients to
local unramified Kummer errors at the twelve places is surjective overF7,
and after scalar extension overF49. Both arithmetic implementations verify
this rank certificate, and twelve explicit preimages of the coordinate
basis are retained.

Concretely, if a residual class vanishes at a selection T of these places,
a chosen modulo49 lift that is UNRAMIFIED at T has local errors in7
times the local residue Kummer module. For example, coefficient lifts
using only the three original unit generators have this property.
Ramified valuation errors at T are not corrected by this residue map. Adding7 times a linear combination of the displayed global
classes can cancel all those errors. Surjectivity for all twelve places
implies surjectivity on every smaller selection. Coefficient changes are
zero modulo7, so the residual alpha is unchanged. Principal local units
at q!=7 contribute no further 49-power obstruction.

This does NOT realize those freely chosen coefficients in the actual
natural Tate representation, preserve its full fixed-prime local Kummer
values, or supply beta. It proves only that a contradiction based on
these unrestricted correction variables and local vanishing equations
alone would be unsound. The actual natural A_2 has additional geometric
constraints. The nodal-period calculation supplies one such constraint,
and rules out local models that this abstract lift test would retain.

## Surviving controls

The exact local depth-two matrices

    N=49[[-1,1],[-1,1]], F=[[1,Q-1],[0,Q]]

have N^2=0, FN=QN, NF=N and beta ramification at n2 for each actual norm
Q=q^2 with q=97,197,14503. They make natural J[49]-type matrices trivial,
but are only toric matrix models. The off-diagonal geometric period is
not a49th power at97 or14503, excluding a Frey realization of those models.
The197 control passes this necessary period test and is NOT eliminated.

The historical abstract opposite Selmer space is also not the ordinary
ray-character space for eta: beta has coefficient twist chi^(-1). One
cannot apply the fifteen eta reciprocity rows to beta without constructing
and proving the appropriate comparison. No such comparison is claimed here.
