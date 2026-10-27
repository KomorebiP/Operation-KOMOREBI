# Beal research, Block 56
## Actual Frobenius precision and the 97/293 high-support branch

Version 5.6.0. 19 September 2026.

The next bounded block is complete under the explicit inherited geometric
and representation hypotheses. Actual good-Frobenius calculations now prove

    491 does not divide C  =>  actual depth n=1,
    197 does not divide C  =>  n<=2 and eta_n=1.

Consequently the complete high-support branch H(C) subset {97,293} has only
depth one. This excludes a stated actual realization of the nontrivial ray
line that survived Block 55. It does not eliminate depth one, the complete
reducible branch of A^3+B^5=C^7, or Beal.

These are written proofs and exact computational certificates. No new Lean
compilation or independent mathematical review is claimed.

## 1. The actual Frobenius sees more precision

Let Q be the norm of a good place, h=v7(Q-1), n the actual global lattice
depth, and m=floor(n/2)+1. The actual character precision gives

    r=min(n,m+h),
    tr_E(Frob)=Q+1 mod 7^r,
    P_v(T)=(T-1)^2(T-Q)^2 mod 7^r,
    7^(2r) divides #J^nu(F_Q).

The proof applies the inherited global eta_n to the same actual Frobenius.
Writing eta=1+u, with u in7^m O, gives

    Q eta + eta^(-1) - (Q+1)
       = (Q-1)u + u^2/(1+u).

Since 2m>n, the precision is min(n,m+h). The rank-four polynomial and the
squared order divisibility follow by restriction of scalars and the norm.
At depth three and h>=1, the new order bound is 7^6, stronger than the earlier
general 7^4 bound. It is not an assertion that an abstract ray character is
the actual diagonal. See notes/FROBENIUS_PRECISION.md.

## 2. The exact curve excludes good 197 at depth three

The counted curve is the actual inherited Frey model

    Z^2=X^6+10BX^3+12AX+5B^2.

There are 5,516 admissible good equation pairs at 197. All are represented by
197 curve orbits, and all have rational trace zero. Write the rational
polynomial as T^4+bT^2+197^2. Since 197 is inert and the twist has sign -1,
the local polynomial is

    (T^2-bT+197^2)^2.

Modulo49, only b=2 and b=296 survive, comprising 56 pairs. Depth three
instead requires b=197^2+1=51 modulo 343. Neither value qualifies. Thus

    n>=3 => 197 divides C.

The 56 lower-precision survivors remain explicit. This does not eliminate
depth two at good 197.

## 3. Good491 excludes every higher depth

The split prime491 has 34,370 good equation pairs. After imposing the complete
residual polynomial modulo 7, only 490 pairs remain. Their rational traces
are in{-25,10,24}. The negative twist changes these to{25,-10,-24}.

For n>=2, the required rank-four trace is

    2*(491+1)=4 modulo 49.

None of the surviving trace values is congruent to4. Therefore

    n>=2 => 491 divides C.

This is a condition on the actual Frey reductions, not merely a test that
some possible Weil polynomial exists. The independent implementation
verifies the signs, base extension, coverage, and point counts.

| Prime | Good equation pairs | Full target mod 7 | Full target mod 49 | Full target mod 343 |
|---|---:|---:|---:|---:|
| 197 | 5,516 | 840 | 56 | 0 |
| 491 | 34,370 | 490 | 0 | 0 |

These are residue-pair counts, not numbers of global solutions.
See notes/FINITE_FROBENIUS_CERTIFICATE.md for the full reduction.

## 4. What happens to the surviving 97/293 line

Define H(C) as the complete set of variable rational prime divisors with
v7(q^f_q-1)>=2. Since491 itself has h=2,

    H(C) subset {97,293} => 491 does not divide C => n=1.

Arbitrary additional h<=1 divisors are allowed. Thus the nonzero diagonal
line from Block 55 cannot be the actual diagonal on that complete support
class. More generally, any nontrivial actual eta requires

    n>=3,             197*491 divides C.

The related support class H(C) subset {97,293,491} has n<=2 and eta=1.
At depth two, some actual beta-supporting prime has v7(v_q(C))=1. Neither
that multiplicity condition nor eta=1 eliminates beta.

The exact boundary matters: a highest character layer supported at 97/293
is NOT excluded when additional high primes, including 197 and 491, divide C.
Highest-layer support is not the complete divisor set. The newly forced
primes need not ramify in eta or beta.

Including the preserved older divisibilities, the necessary integer factors
are now

    n>=2 => 768912500245890 divides C,
    n>=3 => 151475762548440330 divides C.

These products impose no upper bound on C and are not contradictions.
See notes/ARITHMETIC_CONSEQUENCES.md.

## 5. The two simpler contradiction routes do not work

Exact local depth-three toric models at 97 and 293 satisfy the old reciprocal
line, have zero natural local class, and have trivial diagonal Frobenius.
Their inertia corrections give the required top-layer vector (6,1). They
are preserved as local controls, not claimed global Frey realizations.

Generic Weil polynomials also pass the new congruences. At491,
(T^2-2T+491)^2 has the required modulo 49 polynomial and order 490^2. At norm
197^2, (T^2-51T+197^2)^2 has the required modulo 343 polynomial. The exact
Frey locus excludes these possibilities, not the Weil bound alone.

These controls explain the new mechanism: an actual good reduction supplies
information missing from ramified-local matrices and abstract characters.
See notes/LOCAL_SURVIVOR_BOUNDARY.md.

## 6. Verification and provenance

The original Block 55 archive was restored cleanly and its verifier passed
with its selected nested predecessor replays before development. The exact
original bytes are retained in predecessor/.

The production finite certificate and an independent implementation agree
on all 39,886 directly generated good equation pairs. Each uses 692 degree-one
counts and 266 degree-two counts. Split491 rows failing the first trace
condition modulo 7 do not need N2. Those omitted values are explicitly null,
not fabricated full computations. The independent program performs 39,886
polynomial-gcd smoothness checks.

The primary uses a quadratic-nonresidue basis, norm characters, and weighted
orbits. The independent program uses theta^2+theta+1, explicit square-root
tables, B=1 normalization, Newton identities, and the twist radicand. It
imports no primary arithmetic code. Production replay needs only Python's
standard library, not NumPy or a compiler.

The algebra program checks 4,200 exact matrix instances, including 3,780 with
nonrational coefficients. The precision bound is tight in 3,600 cases ; 2,880
cases improve the old general m-bound. Two ramified-local controls and two
generic Weil-polynomial controls are included. These finite tests do not
replace the universal written proof.

The verifier regenerates all outputs in a clean scratch copy, compares the
complete JSONs, checks all payload hashes and 13 named inherited source leaves,
and tests rejection of an intentionally altered point count. The final
extracted-ZIP replay and archive audit are recorded externally, avoiding a
circular checksum claim.

The source pages for the curve/Jacobian trace, Frobenius order, and ray-class
interpretation were checked directly. Text-find failures were resolved by
rendering the known PDF pages. The exploratory NumPy source is preserved as
historical text. All earlier failures remain in the unmodified predecessors.

The first aggregate packaging replay was interrupted by an outer execution
timeout before writing its final report. Its incomplete log is retained. A
subsequent observed subprocess completed all declared checks, including the
altered-count rejection. The final archive has its own fresh replay record.

No new Lean compilation or independent mathematical review occurred.

## 7. Next obligation

The next actual realization problem must include 197 and 491 when eta is
nontrivial. A top layer may still be supported at 97/293 while those newly
forced primes divide C. The next useful input must constrain compatible
bad-prime matrices, other necessarily good Frobenius values, or the same
integral representation and endpoint lattices on that enlarged branch.

Depth one, depth two, unrestricted high support, actual coefficient descent,
independent proof audit, CM nonboundary points, higher Hilbert levels, the
complete signature, and full Beal remain separate unresolved obligations.
