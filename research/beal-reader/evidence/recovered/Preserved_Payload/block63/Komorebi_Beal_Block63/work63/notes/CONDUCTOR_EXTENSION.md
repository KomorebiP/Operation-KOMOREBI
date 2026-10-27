# B63.5. An enlarged depth-one opposite conductor is excluded

Let

    W={43,113,127,197,337,463,547,883,1373,1667}.

Suppose n=1 and EVERY beta-ramification prime lies above W. Arbitrary additional
primes may divide C without beta ramification. All W primes are inert in K and
1 modulo7, so the inherited inertia-injectivity/split7 argument descends beta
AS A chi^-1 COHOMOLOGY CLASS to Q. This is not descent of alpha or of Tate lattices.

Normalize alpha=(u,r,1), with u in k^*, r in k^*, using B63.3. The natural
Kummer rows at these conductor places have phi coordinate0. Their required
ratios are:

    r=1: 1373,1667; r=2:127; r=4:113,463; r=5:43;
    r=6:197,337,547; and883 imposes no ratio.

If r is outside F7^*, only883 could ramify; the nonzero71 row kills that case.
Thus six prime-field ratios suffice by this deduction, not by an assumed
coefficient-field descent. For each ratio883 remains a permitted column.

## Correctly twisted new columns

For each q choose the least positive primitive root g_q, and r_q=g_q^((q-1)/7).
Index the six cyclotomic conductor primes by zeta -> r_q^b, b=1,...,6. The
chi^-1 weights are b, not1 or b^-1. If pi_ell is the inherited norm-ell
integral generator, its row is

    R_ell,q = -sum_(b=1)^6 b*log_(g_q)(pi_ell(r_q^b)) mod7.

Natural conductor rows are(0,2 log_g(3),log_g(5)); their common scalar does not
affect their zero condition. Changing a conductor base prime rescales an
entire column and its free inertia coordinate inversely. Test-prime natural
rows and the root conventions used for the inherited trace sets are unchanged.
No coefficient-field radical is substituted for base-field sqrt5.

The complete columns, generator roots, direct residue values and logarithms
are in verification/conductor.json. The independent program computes symbols
by seventh powering, evaluates the cyclotomic polynomials using zeta^-1, and
checks all six integral generator norms by multiplying conjugates.

## Exact necessary tests and complete finite reduction

At71, beta is zero by the justified forced-bad theorem. At29, the two natural
values differ by u !=0, while the only possible good correction is2. If the
common descended beta29 were nonzero, the two good products could not both
be2. A bad29 also requires beta29=0, because phi is not seventh. Therefore

    R71*s=0 and R29*s=0.

This early reduction uses descent and u!=0; it is not a uniform statement
about every arbitrary-conductor beta over K.

At491,43,211,239 use the inherited ACTUAL good trace sets or bad product0.
Skip43 whenever its conductor column is present: there is no unramified
Frobenius value at an allowed ramified43. The other tests lie outside W.
At split places allow independent coefficient-conjugate choices, a larger
necessary system than the actual one. At inert43 include its factor2.

The primary affine solver and independent Cramer-kernel enumeration agree:

| r | permitted columns | after71 &29, u!=0 | after491 | after43 (when used) | after211 | after239 |
|---|---|---:|---:|---:|---:|---:|
|1|883,1373,1667|2304|72|6|0|0|
|2|127,883|0|0|0|0|0|
|3|883|0|0|0|0|0|
|4|113,463,883|2304|72|2|0|0|
|5|43,883|0|0|not used|0|0|
|6|197,337,547,883|115200|5832|2402|60|0|

There are119808 coefficient/vector candidates after the two initial rows.
The independent program enumerates2496 nonzero kernel vectors times48 nonzero
u values and obtains zero survivors. Thus n1 requires actual beta ramification
outside W. This result includes337,463,547, which were outside the old Splus.
Their new columns are included, rather than reusing the four-prime system.

## Why the new83 theorem is load-bearing

Without u!=0 the exact same W system has THREE survivors, all with alpha=(0,6,1).
In the column order197,337,547,883 they have inertia vectors

    (1,0,5,6), (14,30,25,39), (35,23,32,18),

where coefficient values a+b*w use a+7b and w^2=5 in k. The second and third
are conjugate. Both implementations preserve these tuples. They are genuine
necessary-system survivors, not actual Frey representations. B63.3, not an
unchanged rerun of the earlier sieve, excludes them.

## Larger-conductor negative control

Adding617 defeats this bounded exclusion. All current tests permit

    alpha=(3w,4,1) or(-3w,4,1),
    (s113,s463,s617,s883)=(6,0,5,3),
    beta values at(71,29,491,43,211,239)=(0,0,3,4,0,3).

Each actual nonzero support is113,617,883. These are the two exact survivors
in W union{617}, with u!=0. They are not constructed global Frey models, and
the test does not enforce every fixed-prime or actual residue correlation.
They show why another column cannot be silently omitted or dismissed.
