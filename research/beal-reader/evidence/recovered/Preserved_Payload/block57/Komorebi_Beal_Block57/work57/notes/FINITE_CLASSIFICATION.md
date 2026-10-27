# Exact augmented highest-layer classification

## Declared scope

Let

    U={97,197,293,491,587,883,1373,1471,1567,1667}.

There are12 prime ideals above U:491 and1471 split, and the other eight
primes are inert. All have h=2 except1373, which has h=3. This finite universe
is NOT a theorem about arbitrary C. The classification first assumes only
that the nonzero highest layer ramifies at places above U. Applications to
the entire high-divisor set H(C) are stated separately.

The complete eleven-row matrix and all exact residue logs are in
verification/augmented_certificate.json. Its rank is10, with a nonzero
integer10-by-10 minor and two explicit independent kernel vectors. The
independent implementation certifies the minor by subset determinant
expansion and derives the kernel again with Cramer's rule.

The primary checks all42 normalized F7 directions and all2352 normalized
F49 directions (a_phi/a5,a3/a5,1), a3/a5!=0. Only the two prime-field directions
below have a nonzero restricted kernel. Each such kernel is one-dimensional
over F49. Independent enumeration of all2401 F49 parameter pairs of the full
two-dimensional kernel finds exactly96 nonzero compatible vectors:48 in each
line. These are coefficient vectors, not counts of representations or solutions.

## B57.5. Exactly two necessary patterns remain

The column order is

    97,197,293,491:phi=74,491:phi=418,587,883,1373,
    1471:phi=478,1471:phi=994,1567,1667.

Up to a common nonzero scalar in F49, the two patterns are:

A. alpha=(0,3,1), inertia vector

    (3,0,0,5,2,5,0,0,0,0,1,0).

Its five nonzero prime-ideal components are97, both places over491,587,1567.

B. alpha=(0,1,1), inertia vector

    (5,0,2,0,0,0,0,0,2,5,1,0).

Its five nonzero components are97,293,both places over1471,1567.

No actual F49 coefficient direction outside these two survives the stated
system. This is a support-dependent coefficient determination, not the
missing unrestricted semilinear descent theorem.

All five supporting places in each pattern have h=2. Maximal inertia has
order7^e, while Block54 bounds its order by7^(h-1). Thus e=1. Consequently
lambda is eta itself in its final-digit identification, and there are no
additional lower nontrivial inertia layers. The full ramification support
of eta is exactly the displayed five-place support, under this classification.

Each vector's values are in one F7 line in F49. Since the ray group is generated
by its residue inertia factors and Cl(K)=1, the entire nontrivial character
image is cyclic of order7, not merely of exponent7.

Additional primes may still divide C without ramifying in eta. In particular,
197 and491 remain forced divisors by Block56 even for pattern B, whose eta is
unramified at both. They have not been deleted from the arithmetic problem.

## Rational cancellation, without a semilinear representation comparison

In either pattern, every inert supporting prime is -1 modulo7. Its rational
residue units have order dividing q-1, prime to7, so their logarithms vanish.
At the single split supporting rational prime, the two inertia coefficients
are opposite, and every rational element has the same residue in both fields.
Their contributions cancel. It follows that the character has value zero
on the residue vector of every rational unit prime to its conductor.

If q is an inert prime not in the displayed conductor, its ideal is(q).
Reciprocity therefore gives eta(Frob_(q))=1. Inertia there is already trivial,
so eta|G_(q)=1. This statement is about the classified abelian characters;
it does not assume a twist-compatible semilinear map of the Frey representation.
Both implementations check28 named rational-element evaluations, including1373.

## Exhaustive support-pattern audit

All1024 rational subsets of U were tested. The augmented criterion passes on
912 and leaves a first-layer survivor on112. Its minimal surviving rational
supports are exactly

    {97,491,587,1567},     {97,293,1471,1567}.

The old five-row criterion passed on124 and left900 survivors in the same
universe; those historical results are preserved. The increased exclusion
comes from six proved local-value rows, not repeating an unchanged test.
No percentage of Beal's conjecture follows from these counts.

Both remaining patterns satisfy every added row and the compatible Kummer
condition. They are retained as genuine nonzero abstract ray/Kummer systems.
Class-field reciprocity supplies the corresponding abelian characters, but
a same-lattice global Frey realization, the compatible beta, and a Diophantine
solution have not been constructed.
