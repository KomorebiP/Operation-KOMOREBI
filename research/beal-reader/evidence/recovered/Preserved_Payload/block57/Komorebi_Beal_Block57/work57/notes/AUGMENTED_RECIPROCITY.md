# Forced bad primes and the same global character

## B57.3. Six new rows

Assume the actual eta is nontrivial. The inherited precision makes eta trivial
at depths1 and2, so n>=3. The preserved necessary divisibilities imply

    11*19*31 divides C.

All three primes split in K, and their norms11,19,31 are not1 modulo7.
By B57.1 the ACTUAL eta is trivial on the full local groups at both primes
over each of them. This does not depend on their multiplicities in C.

Write phi=(1+sqrt5)/2. Six principal generators are

    pi11=3+phi,  bar(pi11)=4-phi,
    pi19=4+phi,  bar(pi19)=5-phi,
    pi31=5+2phi, bar(pi31)=7-2phi.

The norm formula N(a+b phi)=a^2+ab-b^2 gives11,11,19,19,31,31 respectively.
They therefore generate the six required prime ideals. Each is a unit at
all places of possible highest-layer ramification, since that ramification
has h>=2. Both conjugate generators must be included. For general support,
a rational prime row is not already present in the old five rows.

Let S_lambda be the COMPLETE ramification set of the nonzero highest layer
lambda=eta^(7^(e-1)). Its image is additive k=F49, after identifying the final
principal-unit digit. Choose one surjective residue logarithm ell_v mod7 at
each possible ramification place, using the SAME column normalization for the
Kummer rows. Its inertia coefficient vector c satisfies

    sum_v ell_v(a)c_v=0

for all eleven elements

    phi, 2, 3, sqrt5, 7,
    pi11, bar(pi11), pi19, bar(pi19), pi31, bar(pi31).    (R57)

Proof. The old five rows have their inherited ray-class interpretation.
The class-number-one ray sequence identifies a principal prime-ideal class
with the residue vector of its generator, up to the harmless common Artin
sign convention. Full local triviality annihilates that class. Apply this
six times to the actual eta, and hence to its highest layer. QED.

The source for the ray sequence and reciprocity is checked in SOURCE_CHECK.md.
The new ingredient is not a new class-field theorem: it is that the actual
bad-prime toric representation forces these extra local splitting conditions.

Maximal-order inertia still forces the same alpha to vanish. Thus, with
alpha=(u,r,1), r!=0, and L_v=(ell_v(phi),ell_v(3),ell_v(sqrt5)),

    c_v!=0 => L_v dot alpha=0.                         (K57)

The Block55 sufficient injectivity criterion applies with the eleven-row
matrix. Its 42-direction reduction remains valid without claiming general
coefficient descent. A nonzero restricted kernel remains only a necessary
system, not a Frey realization.

## B57.4. The remaining 97/293 highest layer is excluded

Suppose S_lambda is contained in the two inert places above97 and293.
The exact residue logs, normalized by ell(phi)=1, include

                  97   293
    phi            1     1
    pi11           6     3
    pi19           6     4
    pi31           2     1.

The first two rows have determinant -3=4 mod7. They are therefore invertible
over F49 as well as F7. Equations (R57) force c=0, contradicting the nonzero
highest layer. This conclusion does not need the unknown Kummer ratio.

The old line(6,1) satisfies the old unit row but evaluates to4,5,6 on pi11,
pi19,pi31. Each nonzero value is an incompatibility with the actual local
representation. Independent direct seventh-power symbols confirm the table.

Crucially this is a restriction on S_lambda, not a bound on the divisors of C.
Additional high primes in C, including197 and491, do not repair this exact
highest-layer support. Additional nonzero highest-layer inertia coefficients
COULD repair the equations, and may not be silently omitted. Lower layers
of eta, if any, vanish after passage to lambda and cannot alter its own ray
presentation. The class-number-one input rules out a separate unramified
highest character with all inertia coefficients zero.

The old abstract ray line and local97/293 matrices are not retracted. They
satisfy their original weaker conditions; they fail the added actual bad-prime
Frobenius constraints at other places.
