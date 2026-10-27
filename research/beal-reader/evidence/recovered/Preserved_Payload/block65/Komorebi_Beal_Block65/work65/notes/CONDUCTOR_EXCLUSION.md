# B65.4. Exact enlarged conductor exclusion

Let P2000 be ALL rational primes q between11 and2000 that are inert in
Q(sqrt5) and congruent to1 modulo7. Direct trial division gives25 primes:

    43,113,127,197,337,463,547,617,673,743,757,827,883,953,967,
    1093,1163,1303,1373,1583,1597,1667,1723,1877,1933.

Set

    T={673,1163,1723,1933},       W65=P2000\T.

Under the retained hypotheses, no depth-one beta has its COMPLETE ramification
contained in W65. Equivalently, beta must ramify outside W65. Extra prime
divisors of C unramified in beta remain unrestricted.

All these potential conductor primes are inert and1 modulo7. The inherited
cohomological descent therefore applies. B65.1 proves alpha=(v*w,r,1), with
v,r in F7^*, and that the normalized opposite inertia values are in F7.
The reduction is not an assumed numerical ansatz.

At conductor prime q, choose the least primitive residue generator g_q and
z_q=g_q^((q-1)/7). The actual chi^-1 row at an unramified test prime ell is

    R(ell,q)=-sum_(b=1)^6 b*log_gq(pi_ell(z_q^b)) mod7.

Every allowed column is included. Constant weights would give the wrong
character. The inherited rows at old test primes are rederived from their
integral generators, and the new379 generator is in PRIME379.md.

Natural local vanishing restricts the ratios. Six listed primes already
have no permissible nonzero r:757,827,1303,1583,1597,1877. They are present
in the full input and excluded by their actual natural rows, not silently
omitted. Among the remaining W65 columns the ratio groups are:

|r|Allowed ramification columns|
|---|---|
|1|883,953,1373,1667|
|2|127,883|
|3|883,1093|
|4|113,463,617,883,967|
|5|43,883|
|6|197,337,547,743,883|

Thus six of the21 named allowed primes were already unusable by the local
Kummer test. The meaningful enlargement includes743,967 and1093, and the new
uniform coefficient proof reduces the search without changing its quantifier.

## Justified initial rows and all good/bad alternatives

Use the inherited full beta-zero at71. At29 the nonzero unit coefficient and
same descended beta value at the two split places imply beta29=0, because the
good set is the singleton{2} and the two natural values differ by u. Bad29
cannot evade this. This argument does not assume29 is bad at depth one.

The finite tests are71,29,491,43 when unramified,211,239,281,379. At a test
place with good reduction the TWO products must belong to one actual quartic's
correction pair. At bad reduction both products are zero. When the natural
phi symbol is nonzero the inherited local theorem also requires beta zero
in the bad case. At a possible ramified43 conductor, the43 test is omitted.

Counts after the71 and29 rows, and then the later tests, are:

|r|After29|491|43|211|239|281|379|
|---|---:|---:|---:|---:|---:|---:|---:|
|1|288|92|50|12|6|0|0|
|2|0|0|0|0|0|0|0|
|3|0|0|0|0|0|0|0|
|4|2052|680|386|78|18|6|0|
|5|0|0|not used|0|0|0|0|
|6|2052|680|386|106|22|2|0|

There are4392 normalized coefficient/character pairs after the two initial
rows. The primary affine solver counts entire affine spaces exactly. The
independent Cramer-kernel solver enumerates732 nonzero F7 inertia vectors,
testing all six v-values with masks. Every stage and the complete survivor
lists agree. Eight tuples remain immediately before379; all fail it.

Every hypothetical actual representation with the stipulated conductor maps
into this finite necessary system. Its emptiness proves the exclusion. No
claim is made that an arbitrary conductor is bounded by2000.

## The larger system is not empty

Allow all25 primes of P2000 instead. The same computations, including the
new coefficient theorem and379 test, leave112 tuples:38 with r=4 and74 with
r=6. They are fully recorded and independently checked, not promoted to
representations or integer solutions.

Hence, WITH complete beta conductor inside P2000, actual ramification must
occur at some prime in T. Outside that stipulation, a ramified prime outside
P2000 can change all Frobenius values and is not excluded by this statement.
