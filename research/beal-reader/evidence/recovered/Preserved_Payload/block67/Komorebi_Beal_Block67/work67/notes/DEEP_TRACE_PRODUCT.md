# B67.1. Trace products at every depth on a deep cyclotomic slice

## Exact ring statement

Let O be the unramified quadratic integer ring over Z7, and let n>=1. Put
m=floor(n/2)+1 and h0=n+1-m=ceil(n/2). Suppose

    F=[[a,b],[7^n c,d]], det(F)=Q,
    d-1 in7^m O,             Q-1 in7^h0 O.

Then t=tr(F)-Q-1 lies in7^n O, and

    t/7^n = b*c modulo7.                                    (1)

This does NOT require the actual diagonal character to vanish modulo7^n.

Proof. Write D=d-1. Since a=Q+t-D, direct determinant expansion gives

    t(1+D)=7^n bc -(Q-1)D + D^2.                            (2)

The last two terms are in7^(n+1)O: h0+m=n+1 and2m>=n+1. Since1+D is a
unit congruent to1 modulo7, (2) first gives7^n|t and then(1). QED.

For the actual representation, B53.3 supplies d-1 in7^m O at EVERY Galois
value, in the single natural basis. At a good unramified Frobenius place with
Q=1 modulo7^h0, both residual coefficient characters are trivial. The fixed
cocycle conventions therefore give

    (tr_O(F)-Q-1)/7^n modulo7 = alpha(F)*beta(F).            (3)

At a variable bad place (3) is meaningful as a Frobenius CLASS value only
when the two classes are unramified there. The universal argument below uses
GOOD primes, so this ambiguity never occurs. No value of a ramified class
is assigned to an arbitrary Frobenius lift.

## One actual quartic still governs the paired products

At a rational split good prime ell=1 modulo7^h0, apply(3) at the two K-places.
The inherited twist identity delta'=phi^2 delta makes their rank-four
polynomials equal. Both actual rank-two traces are congruent toell+1 modulo
7^n by(1). Thus their normalized corrections lie in the one- or two-element
set of coefficient-conjugate roots coming from that SAME actual quartic.
The common-polynomial rule works with7^n in place of7. It does not assert
that the ordinary depth-one correction sets can be reused unchanged.

## Why arbitrary shallow Frobenius would be wrong

At n3,m2 take Q=8 and the exact integral matrix

    F=[[302,1],[15092,50]].

Its determinant is8, its lower-left entry is343*44, and d-1=49. However
tr(F)-Q-1=343, so the normalized trace correction is1 while bc=44=2 modulo7.
Here h=v7(Q-1)=1<2=h0. The discarded term in(2) is load-bearing. This is an
algebraic matrix control, not a Weil/Frey realization. It prevents extending
the old trace formula to ALL Frobenius at greater depth.

The written proof is universal. Exact finite tests at twelve depths audit
algebra and precision, not the inherited geometry or an infinite family.
