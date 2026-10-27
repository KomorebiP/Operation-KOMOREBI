# Beal research, Block 58
## Good/bad Frobenius closure and discriminant rigidity

Version5.8.0. 19 September2026.

Both five-place highest-layer patterns retained in Block57 are now excluded,
even when C has arbitrary additional prime divisors. The stronger statement is:

    A nonzero actual highest character layer must ramify outside
    U={97,197,293,491,587,883,1373,1471,1567,1667}.

A separate discriminant argument proves

    n>=3 =>2549 divides C.

Consequently, when U contains the COMPLETE high-congruence divisor set H(C),
only depths one and two remain:

    H(C) subset U =>n<=2, eta=1 mod7^n.

These conclusions retain the explicit upstream Frey-geometry and representation
hypotheses. This completes the next bounded block, not the entire reducible
branch of A^3+B^5=C^7, the full signature, or Beal. The evidence is written proofs
with exact computational certificates. No new Lean compilation or independent
mathematical reviewer is claimed.

## 1. Good reductions at41 and59 fail at the required precision

The actual inherited curve is

    Z^2=X^6+10 B X^3+12 A X+5 B^2.

The complete finite certificate is:

| Prime | Admissible good pairs | Full target mod7 | Full target mod49 | Twisted traces on the mod7 locus |
|---|---:|---:|---:|---|
|41|1640|120|0|0,7,14|
|59|3422|116|0|-6,1|

At n>=2, the same actual rank-two Frobenius congruence forces the rank-four
polynomial to be (T-1)^2(T-q)^2 modulo49. Its traces must therefore be35 modulo49
at41 and22 modulo49 at59. None of the residual-locus traces qualifies. Thus

    n>=2 =>41*59 divides C.

The 120 and116 mod7 survivors are preserved. No depth-one exclusion follows.
The independent implementation directly counted both degrees at EVERY one of
the5062 good parameter pairs, without a curve-orbit reduction. It also checked
smoothness at every pair and computed the two twist signs from the actual
stipulated radicand at both roots of5.

## 2. The resulting bad primes eliminate the old character kernel

Once41 and59 divide C, they are bad places. Their norms are not1 modulo7,
so the inherited exact toric trace forces the actual eta to be trivial on
their full local groups, including Frobenius. This is not a claim that
unramifiedness alone implies local triviality.

The prime-ideal generators

    6+phi,7-phi,7+2phi,9-2phi

have norms41,41,59,59. Their actual local triviality supplies four new
reciprocity rows. On the old rank-two character kernel, spanned by the
vectors A and B retained in Block57, just two of those rows act as

    [[3,4],[0,4]].

The determinant is12=5 modulo7, so every vector in that old kernel is killed.
The complete new fifteen-row/twelve-column matrix has rank12, certified by
an integer minor27374988=4 modulo7 and an independent determinant implementation.

This eliminates more than the two Kummer-compatible lines: it eliminates the
ENTIRE highest-layer character kernel above U, without testing or assuming
any Kummer coefficient ratio. Arbitrary additional primes may divide C, but
a nontrivial highest layer now needs nonzero inertia at some prime outside U.

The old two characters remain valid abstract objects satisfying their earlier
splitting conditions. They fail the newly proved local values at41 and59.
No earlier arithmetic output is retrospectively changed.

## 3. A new discriminant test uses the actual rank-two precision

Write the actual good Frobenius polynomial as

    P(T)=(T^2-tau T+Q)(T^2-sigma(tau) T+Q)
        =T^4-S T^3+C2 T^2-Q S T+Q^2,

and suppose tau=Q+1 modulo7^r. The integer

    D=S^2-4(C2-2Q)=(tau-sigma(tau))^2

then satisfies

    7^(2r) divides D,       0<=D<=16Q.

The divisibility comes from the scalar trace congruence and its coefficient-field
conjugate. The real bound comes from the actual Weil root pairs: each quadratic
trace is real and has magnitude at most2sqrt(Q). This does not assume a missing
semilinear comparison of Frey lattices or a global coefficient-descent theorem.

If7^(2r)>16Q, the discriminant must be zero. The two traces coincide in a rational
algebraic integer a, forcing

    P(T)=(T^2-aT+Q)^2,
    |a|<=2sqrt(Q),        a=Q+1 modulo7^r.

At the split prime2549, h=2, and every n>=3 supplies r>=3. But

    117649=7^6>16*2549=40784,
    floor(2sqrt(2549))=100,
    2549+1=149 modulo343.

There is no such integer trace in[-100,100]. Good2549 is impossible, so
n>=3 forces2549 into C. No point counts at2549 were needed.

## 4. The full ten-prime high-support class now has depth at most two

Define H(C) as the set of variable rational divisors q with
v7(q^f_q-1)>=2. If COMPLETE H(C) subset U, then2549 cannot divide C, because
2549 itself has h=2 and lies outside U. The preceding theorem gives n<=2.
The inherited half-precision then makes eta completely trivial.

Arbitrarily many additional h<=1 divisors are permitted. In particular, this
is not a theorem only about integers whose prime factors all belong to U.
The former n3 case with trivial eta and beta supported at1373 is also excluded
under this complete high-divisor assumption. It would require2549 outside U.

Depth two remains genuinely open. At some actual beta-supporting prime,

    t=2, s=0, h>=2, v7(v_q(C))=1, alpha locally trivial.

The prime multiplicity in C is divisible by7 but not49. That condition is not
a contradiction. If all high-prime multiplicities are prime to7, only depth one
remains, but no theorem imposing that extra condition is claimed.

## 5. A tempting stronger shortcut fails

A quartic Frobenius congruence is weaker than a scalar rank-two congruence.
At Q=2549 the polynomial

    T^4+45T^3+2603T^2+114705T+6497401

has Weil root magnitudes, factors over the same quadratic coefficient field,
and is congruent to (T-1)^2(T-Q)^2 modulo343. Its rank-two trace can be
-47+49phi, however, which has only49-adic scalar congruence, not343.
Its discriminant12005 is not divisible by117649.

This control prevents substituting the weaker quartic statement into the
new proof. It is a generic Weil polynomial, not an asserted Frey reduction.
The independent checker verifies it and the exact2549 bound.

## 6. Verification and provenance

The original Block57 verifier passed with its selected nested predecessor chain.
The new production certificates and independent implementation agree on:

| Verification | Coverage |
|---|---:|
|Admissible good parameter pairs|5062|
|Primary degree-one / degree-two counts|104 /104|
|Independent direct degree-one / degree-two counts|5062 /5062|
|Independent smoothness gcd checks|5062|
|Independent residue fields / direct seventh-power symbols|12 /180|
|Trace/discriminant algebra instances|2940|
|Complete small separated principal-unit root tests|4902|
|Generic quartic-only Weil controls|18|

The independent checker imports no primary arithmetic. Source hashes preserve
the old geometry and precision inputs without claiming to independently prove
them. The final archive replay regenerates every new result, checks full JSONs,
and requires rejection of deliberately altered point-count and residue-row data.
Final integrity and fresh-extracted replay records are external to the immutable
archive to avoid self-referential checksum claims.

A source-inspection glob failed before the exact file was opened. Broad source
searches returned irrelevant pages, which were discarded; the required primary
PDF theorem pages were opened and rendered directly. Exploratory results at
other primes were not promoted to release theorems. All incidents, counterexamples,
and earlier historical failures are retained. No new Lean compilation or
independent mathematical review took place.

## 7. Next obligation

The former two high-layer patterns are no longer the target. Depth one and
general depth two remain. On the complete ten-prime high-divisor class, the
next meaningful objective is a constraint on the actual nonzero beta at depth2,
not another argument claiming eta=1 is enough.

For unrestricted higher support, a nontrivial highest layer must ramify outside U,
while n>=3 separately forces2549 into C. The ramifying outside-U place is NOT
proved to be2549. The CM cover, higher Hilbert levels, full signature, and full
Beal remain separate obligations.
