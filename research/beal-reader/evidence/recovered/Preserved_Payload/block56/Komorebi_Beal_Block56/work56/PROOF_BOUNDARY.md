# Proof boundary after Block 56

## New written results under the explicit inherited inputs

The actual good Frobenius has trace precision r=min(n,floor(n/2)+1+h).
Its rank-four polynomial meets the split target modulo 7^r, and its Jacobian
order is divisible by 7^(2r). Exact complete good-reduction certificates imply:

    491 not dividing C => n=1;
    197 not dividing C => n<=2 and eta_n=1;
    eta_n nontrivial => n>=3 and 197*491 divides C.

In particular H(C) subset {97,293} forces depth one, with arbitrary additional
h<=1 divisors permitted. H(C) subset {97,293,491} forces n<=2. These are actual
Frobenius restrictions, not vanishing claims about the abstract ray kernel.

## Explicitly not proved

Depth-one elimination; general depth-two elimination; beta=0; a universal
bound on high support; universal eta triviality; general coefficient descent;
a compatible next actual matrix diagonal; a global Frey realization of the
local controls; the full reducible branch; the CM or higher Hilbert-level
branches; full (3,5,7); full Beal; novelty.

The highest character layer might still be supported at 97/293 if additional
high primes, including 197 and 491, divide C. The new theorem does not turn
highest-layer support into the complete divisor set of C. It also does not
claim that either forced prime ramifies in beta or eta.

## Verification boundary

The finite assertions cover exactly 197 and 491 and the explicitly generated
algebraic controls. The complete inherited geometry has not been independently
reviewed or formalized here. Written universal reductions and finite checks
are separate evidence. No new Lean compilation occurred.

All prior proof boundaries, corrections, and failures remain in the untouched
predecessor archive. No earlier abstract construction is retrospectively
reclassified as false merely because a stated actual realization is excluded.
