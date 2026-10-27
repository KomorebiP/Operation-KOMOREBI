# Common-denominator reconstruction: executed height discriminator

Status: exact bounded reconstruction and global finite-precision lower-height
certificates. The actual stationary nonvanishing theorem remains unproved.
This continues the degree-two construction in
`QUADRATIC_COMPRESSION_AND_HEIGHT.md`, without changing that reviewed note.

## 1. The reconstruction lattice and invariant

At one of the frozen actual controls, let W=Z^2+2 beta Z+alpha be known
modulo2^P. Put M=2^P, and use coordinates (A,B,C) for the polynomial
A Z^2+2 B Z+C. Exact projective agreement requires

    B=beta A (mod2^(P-1)),  C=alpha A (mod2^P),  A odd.       (1)

The first congruence is equivalent to agreement of the full linear
coefficient modulo2^P. The lattice of the first two congruences has row basis

    (1,beta,alpha),  (0,2^(P-1),0),  (0,0,2^P),

and determinant2^(2P-1). For every odd-A vector its scaling-invariant rational
reduced discriminant is

    t=(B^2-A C)/A^2 = delta (mod2^P).                       (2)

Dividing (A,B,C) by its common gcd is legitimate: the gcd is odd and hence
invertible modulo2^P. This removes artificial projective scaling. One must
also reduce the rational number t itself. The additional odd cancellation

    g=gcd(B^2-A C,A^2),  n=(B^2-A C)/g,  d=A^2/g

can shrink its numerator even when (A,B,C) is primitive. Since d is odd,

    0<|n|<2^P                                               (3)

is a sufficient nonvanishing certificate. It is stronger than only testing
0<|B^2-A C|<2^P. The exact invariant is t, not the size of an arbitrarily
scaled polynomial discriminant.

## 2. What was actually executed

The checker uses exact Fraction Gram-Schmidt and exact LLL with delta=3/4.
It verifies determinant preservation, all size-reduction inequalities, and
all Lovasz inequalities. It then forms every integer combination of the
three reduced basis vectors with coefficients in[-8,8], retains odd A,
divides by the full common gcd, and removes duplicates. This is a declared
bounded search, not a claim that it finds the globally shortest vector or
smallest discriminant. Every candidate's congruences and discriminant
congruence(2) are checked directly using integers.

The only inputs are the14 quadratic records already produced from the fixed
actual controls T=0 and T=718787533, at P=16,24,32,48,64,80,93. No new
multiplier digits or candidate values are computed.

Projective reconstruction substantially reduces the coefficient heights.
At P=93, each control has a primitive odd-denominator model with62-bit
coefficients, compared with93-bit least-residue monic coefficients. Among
the declared candidates, the smallest absolute integer discriminants have
116bits for T=0 and119bits for T=718787533. After reducing the rational
numerator in(2), these improve to114bits and112bits, respectively. They
still exceed the93-bit approximation precision. No zero-discriminant
model occurs in this bounded search.

The reduced-numerator test does succeed at two lower frozen precisions:

| T | P | (A,B,C) | Reduced rational discriminant t |
|---|---:|---|---|
| 0 | 16 | (5805,3708,2209) | 34297/1248075 |
| 0 | 32 | (4789197,-4929540,5227073) | -3878929729/121356655581 |

The numerator is nonzero and smaller than2^P in absolute value in each case.
Both numerators are odd, so these are valid independent arithmetic
certificates of the already known valuation0. They are not new instances
of the universal theorem. The other12 precision/control pairs do not pass
(3) in the declared search. In particular, the unresolved P=16 and24 data
at T=718787533 cannot pass(3): delta is zero modulo2^P there, and an odd
denominator would force every nonzero reduced numerator to have absolute
value at least2^P.

## 3. A global lower-height certificate at each frozen precision

There is also a conclusion independent of the bounded enumeration. Let B_0
be any integer row basis of the reconstruction lattice and C_0 its cofactor
matrix. For v=B_0^T z with integer z, the exact identity

    C_0 B_0^T=det(B_0) I

implies, with H=max_j |v_j|,

    |z_i| <= H * (sum_j |(C_0)_(i,j)|)/|det(B_0)|.

Every nonzero v has some nonzero integer z_i. Therefore every nonzero
lattice vector, with or without the odd-A restriction, satisfies

    H >= ceil(|det(B_0)| / max_i sum_j |(C_0)_(i,j)|).       (4)

The checker verifies the cofactor identity and records this exact integer
lower bound L for each reduced basis. For all14 frozen lattices,

    2 L^2 >= 2^P.

Thus no projective representative at these precisions can satisfy the
sufficient coefficient-height test2H^2<2^P. This is a global impossibility
certificate for that particular sufficient test at the specified inputs,
not merely a failure to find a short model. At P=93 the lower bounds are
2370903276496295044 for T=0 and1944707394794158329 for T=718787533.

The conclusion does not prohibit exceptional cancellation in B^2-A C or in
its reduced rational numerator. The two successful examples in Section2
show why those distinctions matter. Nor does a finite list of lower bounds
prove any asymptotic exponent for other precisions or ordinary indices.

## 4. Arithmetic consequence and exact remaining input

Common-denominator reconstruction and gcd removal improve the raw height
materially, and can occasionally give a strict numerator certificate. They
do not supply a scaling invariant that forces the coefficient-height
exponent below1/2. At the frozen precisions the corresponding strict
coefficient-height criterion is impossible by(4), while the reduced-numerator
criterion succeeds only in the two already easy valuation0 records.

A uniform closure would need a new actual-coefficient constraint giving
nonzero reduced numerators with |n|<2^P at an explicitly bounded precision,
or an equivalent quantitative inequality with a depth-independent constant.
The LLL construction and determinant of this congruence lattice give no
such bound. In particular, they cannot turn a vanishing residue into a
nonzero rational numerator of size below its modulus. Centering beta at zero
and copying the local Bezout scalar would be the old certificate, not this
new projective construction.

Reproducibility: `check_projective_reconstruction.py`,
`projective_contract.json`, and
`projective_run/{manifest.json,results.json}`. The new script imports only
the previously recorded quadratic result file. The run pins both files.
Exact integer and Fraction arithmetic is used throughout; no floating-point
LLL, numerical height estimate, random choice, or Lean compilation is used.
