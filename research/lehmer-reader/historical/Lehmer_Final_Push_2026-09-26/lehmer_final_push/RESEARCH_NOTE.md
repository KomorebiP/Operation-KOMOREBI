# Final push on Lehmer: the remaining prime obstruction

Checkpoint **LEHMER-FINAL-BOUNDARY-03**, 26 September 2026.
Parent: **LEHMER-CONTENT-TRANSPORT-02**, pinned in [BASE.json](BASE.json).
This is the contemporaneous closeout of the requested final push.

**Lehmer's conjecture was not solved.** No prime with tau(p)=0 was found,
and no argument excluding all such primes was obtained. This phase proves
stronger boundaries for the packet and local arithmetic approaches, rather
than treating those boundaries as a proof of the conjecture.

## Target and inherited reduction

The target remains tau(n) != 0 for every positive integer n, where

\[
\sum_{n\ge1}\tau(n)q^n=q\prod_{m\ge1}(1-q^m)^{24}.
\]

The classical Hecke reduction makes it enough to exclude tau(p)=0 at every
prime p. The parent packet construction has

\[
\mathcal V_n=\{v\in\mathbb Z^5:v_i\equiv i\pmod5,
\ \sum_i v_i=0,\ \sum_i v_i^2=10n\},\qquad
W(v)=\frac{\prod_{i<j}(v_i-v_j)}{288}.
\]

Its primitive residual is

\[
R(n)=\sum_{\substack{v\in\mathcal V_n\\\gcd(v_0,\ldots,v_4)=1}}W(v)
=\sum_{d^2\mid n}\mu(d)\chi_5(d)d^{10}\tau(n/d^2).
\]

The inherited theorems R(s^2) != 0 for every s, and
R(n)=0 if and only if tau(n)=0, survived an independent derivation and source
audit. See [the audit](prior_audit/AUDIT.md). In particular R(p)=tau(p): the
primitive transform does not remove the prime obligation.

A solution would require a proof with all-prime quantifiers, or a verified
actual zero. A finite search, a full-rank correction space, a compatible
synthetic sequence, or a congruence obstruction to one method does not meet
that target.

## 1. All finite symmetric polynomial nulls conserve content

The new extension removes the former homogeneity restriction. If a finite
symmetric polynomial Q satisfies

\[
\sum_{v\in\mathcal V_n}W(v)Q(v)=0\qquad\text{for every }n\ge1,
\]

then every homogeneous component of Q is separately universally null, and
the same sum vanishes separately on each exact coordinate-gcd class.

The proof uses alternating harmonic decomposition of DQ_d. Its theta series
is quasimodular of weight 12+d. Different weights cannot cancel: their
transformation laws give homogeneous polynomials of different degrees in
the bottom row (c,d) of a modular matrix, and primitive integer pairs are
Zariski dense. Componentwise content conservation then follows from the
parent gcd-scaling argument. Odd-degree pieces vanish directly under J.

The complete proof, including the scalar harmonic theta normalization, is
[PC-ALL](null_span/POLYNOMIAL_CONTENT_THEOREM.md).

At n=121 the conserved masses are

| Exact content | Mass |
|---:|---:|
| 1 | -25439104668 |
| 11 | 25937424601 |

Their opposite signs rule out a common-sign certificate using **any finite
symmetric polynomial universal-null correction** at this composite index.
This does not obstruct a prime-specific sign construction: primes have only
one content class.

## 2. Every fixed congruence depth has actual prime survivors

For every integer M>=1, a positive-density set of primes satisfies

\[
p\equiv-1\pmod{5M},\qquad \tau(p)\equiv0\pmod M.
\]

At each such prime, simultaneously for every r>=1,

\[
\boxed{R(p^r)\equiv0\pmod M.}
\]

The first assertion is a classical-theorem consequence. In the actual joint
finite image of Deligne's representations and the cyclotomic character,
complex conjugation has trace zero and cyclotomic value -1. Chebotarev gives
a positive-density conjugacy class of prime Frobenius elements with those
values. This requires no independence between the representation images.
For the prime 2, trace zero is established before reduction, in characteristic
zero.

The project-specific translation is immediate from the primitive local factor:

\[
\sum_{r\ge0}R(p^r)X^r
=\frac{1-\chi_5(p)p^{10}X^2}{1-\tau(p)X+p^{11}X^2}
\equiv\frac{1-X^2}{1-X^2}=1\pmod M.
\]

Thus a fixed finite collection of tests seeking a nonzero residue among
these local blocks cannot cover every prime, even if all exponents are
available. This does not rule out adaptive moduli, and it does not produce
an integer zero. The quantifiers cannot be reversed.

See [arithmetic Theorem A](arithmetic/NOTE.md) for the complete proof and
checked Deligne and Chebotarev sources. The same note constructs a
trace-zero weakly admissible filtered Frobenius module with filtration jumps
0,11 and characteristic polynomial X^2+p^11. Local slope, integrality and
purity conditions permit zero trace; they do not provide a contradiction.

## 3. The retained arithmetic data admit a global zero model

The preceding theorem gives a stronger logical test of the approach. For
every finite coefficient bound B and fixed modulus M, one can choose q>B
and construct an integral multiplicative sequence f such that:

- f(n)=tau(n) for all n<=B and f(n)=tau(n) modulo 10M for every n;
- all weight-12 Hecke recurrences hold;
- the global bound |f(n)|<=d(n)n^(11/2), parity criterion and mod-5 congruence
  hold;
- its primitive transform is nonzero at every square;
- nevertheless f(q)=0.

Choose q with tau(q)=0 modulo 10M and q=-1 modulo 50M. Replace its prime
parameter by zero, keep all other prime parameters, and extend by the Hecke
recurrences. This is an actual countermodel to an implication from the
listed properties alone to nonvanishing. It is **not** a claimed
counterexample for the fixed modular form Delta.

No claim that f is nonmodular is needed or made: if tau(q) were already zero,
the construction could coincide with tau. The point is that modularity or
the packet realization has not been imposed in the weaker premises.
See [the full model proof](prior_audit/SYNTHETIC_MODEL.md).

## 4. Exact lifting shortcuts fail

We tested the potential shortcut v_ell(tau(p))=v_ell(p+1), at the auxiliary
primes ell=2,3,5 and primes p=-1 modulo ell. Each equality would give a
nonzero value on its claimed range. All three fail:

| ell | First failing prime p | v_ell(tau(p)) | v_ell(p+1) |
|---:|---:|---:|---:|
| 2 | 81919 | 20 | 14 |
| 3 | 8747 | 8 | 7 |
| 5 | 499 | 4 | 3 |

These are the first failures in an exhaustive search of primes through
150000, hence the smallest prime counterexamples to these stated equalities.
The 5-adic discrepancy also goes in the other direction at p=1249:
v_5(tau(1249))=3 whereas v_5(1250)=4. These are counterexamples to the
auxiliary equalities, never to Lehmer.

The four decisive integer values were independently recomputed from
(E4 E8-E6^2)/1728, using divisor-sum convolutions, rather than the triangular
recurrence used for the search. Both formulas agree exactly. The source and
normalization of that independent check are in [SOURCES.md](SOURCES.md);
the finite evidence is [result.json](computations/valuations001/result.json).

## 5. Unrestricted interpolation does not create universal nulls

On a shell with N J-orbits, the four even symmetric coordinates
s4, s3^2, s3*s5, s5^2, together with the fixed s2, identify exactly those
orbits. An explicit rational symmetric homogeneous polynomial of degree
10(N-1) can interpolate arbitrary orbit values.

This proves that no further coincidences of those coordinates explain the
remaining null-span problem. It does not prove universal nullness. The
natural interpolated zero-total transfers at n=7 and n=31 already fail the
null identity at shell 1. Top-degree harmonic projection cannot fix this
while preserving values: it annihilates s2*D, although that polynomial has
nonzero values on the shell.

Even if universal nulls span every content-preserving transfer, a common-sign
certificate at a prime exists if and only if tau(p) is nonzero. Fullness alone
does not supply the independent nonzero sign. The interpolation proof,
counterexamples and exact sign criterion are in
[the terminal boundary note](null_span/NOTE.md).

## Review and closeout

All three official computation records passed their input/output provenance
validators. The evidence distinguishes exact universal proofs from bounded
checks. The independent review of the new central proofs is in
[FINAL_BRANCH_AUDIT.md](prior_audit/FINAL_BRANCH_AUDIT.md). These are written mathematical
proofs and exact integer/rational computations, not Lean certificates.
No historical priority is claimed.

This final push is complete; the conjecture remains open in this program.
The scoped valuation identities and the interpolation-then-harmonicization
shortcut are refuted. Fixed-modulus nonzero-residue certificates are
insufficient by a universal theorem. Nonhomogeneous finite symmetric null
corrections give no escape from content conservation.

The all-degree null-span theorem remains unproved, but even proving it would
not close the prime gap. Adaptive congruences and genuinely global properties
of Delta remain possible; they are deferred here, not proved impossible.
A meaningful resumption must identify a specific additional consequence of
the actual modular or packet structure and show how it excludes a zero prime
parameter. The retained recurrence, congruences, bounds and square theorem
cannot do that by themselves, even in combination.
