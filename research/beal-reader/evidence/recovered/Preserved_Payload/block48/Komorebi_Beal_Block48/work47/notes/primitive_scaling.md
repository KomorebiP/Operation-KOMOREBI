# Exact primitive scaling and valuation strata

This is an elementary written equivalence, not a proof of Beal. It locates
the arithmetic information that a cancellation or coordinate change must
preserve. Put s=1-t for a rational number 0<t<1, and use the established
universal parametrization

    A0=t^12 s^28, B0=t^7 s^17, C0=t^5 s^12.

Then A0^3+B0^5=C0^7. Weighted scaling by a positive rational lambda gives

    A=lambda^35 A0, B=lambda^21 B0, C=lambda^15 C0.

## Proposition

A positive rational lambda producing primitive positive integers A,B,C
exists if and only if the following hold at every rational prime l:

- v_l(t)>0 implies 3 divides v_l(t).
- v_l(1-t)>0 implies 5 divides v_l(1-t).
- v_l(t)<0 implies 7 divides -v_l(t).

When such lambda exists it is unique. This is a recognition criterion for
one rational t, not a procedure guaranteed to find or exclude every t.

## Proof

Let m=v_l(t), n=v_l(s), and h=v_l(lambda). Since t+s=1, the valuation
pair has exactly one of four forms: m>0,n=0; m=0,n>0; m=n<0; m=n=0.
The output valuations are

    alpha=35h+12m+28n,
    beta =21h+ 7m+17n,
    gamma=15h+ 5m+12n.

Integrality requires all three to be nonnegative, and primitivity requires
their minimum to be zero. The minimum of 3alpha,5beta,7gamma is then zero.
In the first sector those three numbers are respectively
105h+36m,105h+35m,105h+35m. Hence h=-m/3 is forced, and the output valuations
are (m/3,0,0). In the second sector the three weighted valuations are
105h+84n,105h+85n,105h+84n. Hence h=-4n/5 and the output is (0,n/5,0).
In the third sector write m=n=-r with r>0. The weighted valuations are
105h-120r,105h-120r,105h-119r. Thus h=8r/7 and the output is (0,0,r/7).
In the fourth sector h=0 is forced.

Consequently an integral h exists precisely under the three displayed
divisibility conditions. Only finitely many primes occur in t or s, so
lambda=product_l l^h is a well-defined positive rational number. All output
valuations are nonnegative and their supports are disjoint. This proves
primitive integrality and pairwise coprimality. Uniqueness follows from the
forced valuations and positivity. QED.

## Interpretation for toolkit transfer

Residue projectors are exact coordinate selectors. A unit diagonal permits
inversion in the chosen local ring. Neither operation by itself makes these
three valuation congruences hold simultaneously for a rational t. The
defect consists of residues modulo 3,5,7 in the three different valuation
sectors. It is not measured by the number of lanes or by a formal-series
cancellation count.

Equivalently, if t=m/n is reduced with 0<m<n, then m must be a cube, n-m
a fifth power, and n a seventh power. The proposition is not a shortcut
around this original Diophantine condition.

The supporting finite audit checks the valuation linear systems against the
criterion in a declared range. The proof above, not that finite audit,
establishes the equivalence for every prime and every valuation size.
