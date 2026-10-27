# B67.4. Good/bad Frobenius at 1051 excludes the two frozen tuples

This theorem is at actual depth ONE. The all-depth theorem in the other notes
is not a license to reuse these numerical first-digit correction sets at n>1.
Assume the COMPLETE beta ramification is contained above P2000, the 25 inert
rational primes q=1 modulo7 between11 and2000. The preserved Block66 proof and
its exact full candidate list leave just

    alpha=(w,6,1) or(-w,6,1),
    (s337,s547,s673,s1933)=(4,6,2,3),

with all other inertia coordinates zero. The new verifier uses the BYTE-IDENTICAL
Block66 filter certificate and replays its selected predecessor chain. It does
not silently select two candidates from an unverified larger search.

## Complete good-reduction data

The curve is the inherited actual Frey family

    z^2=x^6+10 B x^3+12 A x+5 B^2.

For q=1051 every integer solution with good reduction supplies a pair(A,B) with
A^3+B^5 a NONZERO seventh power. All 157650 such pairs are generated directly.
Weighted curve isomorphisms are used only to reuse counts; equation eligibility
is tested member by member. Primary degree-one counts are made on1057 classes,
and degree-two counts on147 classes. A class whose first trace already violates
the necessary mod7 target needs no second count; its N2 is explicitly null.
There are3000 pairs satisfying the complete residual polynomial target.

The independent program uses a different quadratic-field basis, explicit
square-root tables, a different normalization and polynomial gcd checks on
ALL157650 pairs. Its1057 and147 class counts agree with the primary. This is
independent arithmetic implementation, not independent mathematical authorship.

At both split places the twist is positive. The complete actual good correction
PAIRS, with w^2=5 in the coefficient field, are

    {2}, {5}, {+w,-w}, {4+w,4-w}, {5+w,5-w},
    {+2w,-2w}, {1+2w,1-2w}, {4+2w,4-2w},
    {+3w,-3w}, {5+3w,5-3w}, {6+3w,6-3w}.

These are extracted from the full quartics, not guessed from their traces.
For N1,N2 put S=q+1-N1 and C2=(S^2-q^2-1+N2)/2, then use
P(T)=T^4-S T^3+C2 T^2-qS T+q^2. The primary factors the integral trace
discriminant; the independent program extracts the two correction roots from
trace and norm in a different coefficient basis. The classical curve trace
formula is recorded in SOURCE_CHECK.md.

## Compatible twisted Frobenius row

In Z[zeta7] the coefficient vector

    (-2,-1,2,1,0,-1)

has exact norm1051 and vanishes at the primitive seventh root801 modulo1051.
The primary norm is a multiplication determinant. The independent norm is the
product of conjugates in the inverse-cyclotomic basis. The natural phi roots
are73 and979; the compatible Kummer rows(phi,3,sqrt5) are

    (2,1,5), (5,1,5).

For EVERY one of the25 possible conductor primes, the correctly chi^-1-twisted
row is recomputed as -sum_b b log(pi1051(r_q^b)), in the frozen normalization.
In particular its entries at337,547,673,1933 are(5,6,0,6), so

    beta1051=5*4+6*6+0*2+6*3=4 modulo7.

With alpha=(+/-w,6,1), the two trace products are

    2+w and2-w.

Neither is zero and neither occurs in the displayed union, much less in one
common polynomial pair. Because1051 is split and not in P2000, beta is
unramified there regardless of whether1051 dividesC. If good, the actual
trace-product belongs to the good correction pair. If bad, the exact toric
trace gives product0. Both possibilities contradict the required values.
Thus NO actual depth-one beta has complete ramification inP2000. QED.

Additional primes may divideC without beta ramification. No theorem bounds
an arbitrary conductor by2000, and this is not an exclusion of ALL possible
ramification primes below2000: see CONDUCTOR_BOUNDARIES.md.

## Passing probes and evidence scope

Before1051, primary exploratory counts at701,911,1009 retained the two tuples.
Those exploratory scripts and summaries are preserved as historical text;
they are not additional independently accepted release count theorems. A
necessary-trace targeted1051 scan found zero before the full count. The released
proof uses the COMPLETE count and separate checker, not only that targeted scan.
