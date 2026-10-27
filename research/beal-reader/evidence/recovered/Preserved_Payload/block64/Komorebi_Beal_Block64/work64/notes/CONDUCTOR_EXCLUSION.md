# B64.3. A complete twelve-prime depth-one conductor is excluded

Set

    W64={43,113,127,197,337,463,547,617,883,953,1373,1667}.

The theorem assumes actual depth n=1 and EVERY beta-ramification prime above W64.
Extra primes can divide C without beta ramification. The conclusion is that
no such representation satisfies all the retained hypotheses.

All W64 primes are inert in K and1 mod7. The inherited split7, inertia-injectivity
and class-group inputs therefore give descent of beta AS A chi^-1 cohomology
class to Q. There is no claim of descent of the Tate lattice or of alpha.
Normalize alpha=(u,r,1), where u,r are nonzero in F49.

The natural conductor rows force these possible support groups:

| r | permitted rational ramification columns |
|---|---|
|1|883,953,1373,1667|
|2|127,883|
|3|883|
|4|113,463,617,883|
|5|43,883|
|6|197,337,547,883|

Each row outside883 has a nonzero3-symbol, and forces exactly the displayed
prime-field ratio. If r is outside F7, only883 could ramify, but the nonzero
71-row excludes that singleton. Thus the reduction to six ratios is proved,
not a coefficient-field descent assumption.

The forced-bad71 condition gives R71*s=0. The inherited good29 set is{2}, while
the two natural29 values differ by u!=0. A descended beta has the same value
there, so nonzero beta29 would make the two good products unequal. A bad29
cannot repair this. Hence R29*s=0. These are justified within the descended
conductor regime, not imposed on an arbitrary beta over K.

Every conductor column, including617 and953, is newly recomputed with the
correct chi^-1 weights. There is no unramified Frobenius test at43 in the
r=5 branch, because43 is permitted to ramify there.

## Exact finite necessary system

Use the old good/bad trace tests at491,43 when permitted,211,239 and then281.
For the exclusion theorem it is sufficient to retain the WEAKER independent
choices at the split places. Thus the new common-polynomial theorem is not
being used to conceal a failure of the basic281 argument.

Counts below are exact numbers of normalized coefficient/character tuples,
not solutions. The first column is after the two justified linear rows.

| r | after71 and29 | after491 | after43 | after211 | after239 | after281 |
|---|---:|---:|---:|---:|---:|---:|
|1|115200|5832|432|30|14|0|
|2|0|0|0|0|0|0|
|3|0|0|0|0|0|0|
|4|115200|5832|432|6|2|0|
|5|0|0|not used|0|0|0|
|6|115200|5832|2402|60|0|0|

There are345600 possibilities after the two linear rows. Each group has at
most two free F49 inertia parameters after these rows, multiplied by48 possible
nonzero u. The primary uses affine row elimination and exact affine-space
cardinalities. The separate implementation derives the two-row kernels by
Cramer's rule, enumerates their7200 nonzero vectors, and uses exact bitsets
for all48 nonzero coefficients per vector. It agrees on every stage count
and the COMPLETE lists of survivors, not merely the final zero.

The14 r=1 tuples after239 and the two old r=4 tuples are preserved before the
new281 test. Every one fails that test. An old success flag, or merely the
absence of numerical examples, is not used as a proof. PRIME281.md supplies
the complete reduction of the actual281 locus to its finite trace set.

Every hypothetical actual representation under the stipulated conductor maps
into this necessary finite system. Since that system is empty, it is excluded.
There is no theorem that arbitrary actual beta conductors lie in W64.
