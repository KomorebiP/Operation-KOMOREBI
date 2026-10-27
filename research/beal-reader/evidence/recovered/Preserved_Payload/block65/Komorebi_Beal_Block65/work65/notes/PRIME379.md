# B65.2–B65.3. The actual prime379 closes the retained547/743 configurations

379 is prime, splits in K and is1 modulo7. Its phi residues are20 and360.
The actual twist delta=9-3phi is nonsquare at both. Every good integer triple
maps to a pair(a,b) with a^3+b^5 a NONZERO seventh power modulo379.

The complete locus has20466 pairs. Both implementations account for every
pair, including zeros in either separate coordinate when admissible. The
primary uses weighted curve orbits but filters every member for seventh-power
admissibility. The independent implementation uses a discrete-log canonical
curve and explicit square-root tables in another quadratic-field basis.
Every admissible pair is independently checked for smoothness.

There are381 degree-one counts and41 degree-two counts in each implementation.
Degree-two values are omitted only after a failed necessary degree-one trace
test. Such values are explicitly null. There is no claim of20466 direct
counts in degree two.

For the complete untwisted counts N1,N2, put S=380-N1 and
B2=(S^2-379^2-1+N2)/2. The rational quartic is
T^4-S*T^3+B2*T^2-379*S*T+379^2. The twist negates roots. The full residual
target is (T-1)^2(T-379)^2 modulo7. Exactly432 pairs survive, in eight
orbits of54 admissible pairs each:

|Representative|N1|N2|Twisted S|Twisted C2|Correction pair, w^2=5|
|---|---:|---:|---:|---:|---|
|(2,186)|370|143148|-10|-197|1 +/- 2w|
|(4,275)|314|142980|-66|1847|4|
|(6,21)|391|144975|11|727|6 +/- 3w|
|(6,133)|356|144380|-24|657|+/- w|
|(8,187)|363|143911|-17|279|4 +/- 2w|
|(8,352)|384|145150|4|762|2|
|(12,50)|335|144023|-45|1203|2 +/- 3w|
|(12,355)|405|144723|25|853|+/- 3w|

Here the twisted polynomial is T^4-S*T^3+C2*T^2-379*S*T+379^2.
For one such P the two rank2 traces have sum S and product C2-758.
Their corrections (tau-380)/7 give the displayed pairs. The primary extracts
them from D=S^2-4(C2-758)=5*v^2. The independent program enumerates all49
coefficient elements using the integer trace/norm of that correction.

Thus the complete good correction set is

    G379={2,4,+/-w,+/-3w,1+/-2w,4+/-2w,2+/-3w,6+/-3w}.

It contains no element whose scalar coefficient is3.

## The same global class fixes the other side of the identity

Use the integral cyclotomic prime generator

    pi379=-2-2*zeta-zeta^2+zeta^3-2*zeta^4-2*zeta^5.

Its exact norm is379, checked independently by multiplying all six conjugates.
Its unique primitive seventh-root zero modulo379 is195. That root fixes the
compatible Kummer normalization and gives rows

    (5,1,4), (2,1,4)     in coordinates(phi,3,sqrt5).

At conductor primes547,743 the chi^-1 weighted residue row is(2,5).
For the inherited inertia vector(5,1), the actual descended beta value is

    2*5+5*1=1 mod7.

For alpha=(+/-w,6,1) the two trace products are therefore3+/-2w. Both are
nonzero, and neither is in G379.

379 is outside the entire stipulated old conductor W64 union{743}. Thus beta
is unramified there. Good reduction requires membership in the actual good
set; bad reduction requires product zero by the exact toric trace. Both fail.
The retained547/743 tuples are excluded. No theorem that379 always divides C
is asserted. Other divisors of C, unramified in beta, are already allowed.

This exclusion can be proved directly from the frozen FULL-F49 two-survivor
list of Block64, without using the new coefficient-rigidity theorem. The
larger conductor result uses that theorem separately.
