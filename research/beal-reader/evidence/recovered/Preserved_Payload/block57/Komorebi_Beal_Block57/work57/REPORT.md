# Beal research, Block 57
## Forced bad-prime Frobenius and highest-layer exclusion

Version 5.7.0. 19 September 2026.

**The remaining highest-layer pattern supported only at 97 and 293 is now
excluded, even when C contains additional high-congruence divisors such as
197 and 491.** This closes the specific realization gap left by Block 56.
It does not eliminate every larger support containing those primes.

The new input is a constraint from primes already known to be bad: the
actual local diagonal character must be trivial at the six places over
11, 19, and 31. Their Frobenius values add six global reciprocity equations.
No further auxiliary-prime good-reduction assumption is made.

All arithmetic results retain the explicit inherited geometric and
representation hypotheses. These are written, self-reviewed proofs with
exact computational certificates. No new Lean compilation or independent
mathematical review was performed. The full retained reducible branch of
A^3+B^5=C^7, the complete signature, and full Beal remain unresolved.

## 1. Bad reduction can provide the missing Frobenius constraint

Let eta be the actual diagonal correction modulo 7^n. At a variable bad
place, the inherited split toric representation has characters chi_7 and 1.
The same natural lattice has diagonal characters chi_7 eta and eta^(-1).
Their traces therefore give, for every local Galois element g,

    chi(g) eta(g) + eta(g)^(-1) = chi(g)+1 mod 7^n.

Multiplication by eta(g) gives

    (eta(g)-1)(chi(g)eta(g)-1)=0.

When chi(g) is not 1 modulo seven, the second factor is a unit. Hence
eta(g)=1. A separating local Frobenius, together with multiplicativity,
then determines eta on all remaining local elements. Consequently,

    q|C and Q_v != 1 mod7  =>  eta|G_v=1 mod7^n.

This is full local triviality, including Frobenius, not merely absence of
ramification. It uses the actual toric trace after the specified twist.
See notes/LOCAL_DECOMPOSITION.md for the complete argument.

A more general statement is also available. If h=v7(Q_v-1), the local
Frobenius image has order dividing 7^h. Inertia has order dividing
7^max(h-1,0). Thus the full local image has exponent dividing 7^h. For a
highest global layer of exponent 7^e, every bad place with h<e is locally
trivial on that layer. The h=0 places are useful without knowing e.

## 2. The old 97/293 line fails a two-by-two determinant

Nontrivial eta requires n>=3. The retained necessary divisibilities then
force 11, 19, and 31 into C. These primes split in K=Q(sqrt5), and their
norms are not 1 modulo seven. The preceding lemma therefore applies at both
places over each rational prime.

Put phi=(1+sqrt5)/2. Principal generators are

    3+phi, 4-phi;  4+phi, 5-phi;  5+2phi, 7-2phi.

Their norms are respectively 11, 11, 19, 19, 31, 31. Class-field reciprocity
turns their local triviality into six additional residue-logarithm rows for
the same global highest layer. Both conjugate generators are retained.

At the two inert places above 97 and 293, normalize ell(phi)=1. The exact
logarithms include

| Element | 97 | 293 |
|---|---:|---:|
| phi | 1 | 1 |
| 3+phi | 6 | 3 |
| 4+phi | 6 | 4 |
| 5+2phi | 2 | 1 |

The first two rows have determinant -3, which is 4 modulo seven. They have
no nonzero common kernel over F49. The old vector (6,1), although compatible
with the old unit row, evaluates to 4, 5, and 6 on the three displayed prime
generators. Each is incompatible with the actual local Frobenius condition.

**Additional primes dividing C do not repair this exact highest-layer
support.** Only additional nonzero highest-layer ramification coefficients
could do so; those would be a different support and must be included explicitly.
The argument does not assume that the highest layer exhausts the divisors of C.
See notes/AUGMENTED_RECIPROCITY.md.

## 3. Exactly two patterns survive in the declared ten-prime universe

Let

    U={97,197,293,491,587,883,1373,1471,1567,1667}.

This is a declared classification universe, not a bound on arbitrary C. The
augmented eleven-row matrix has 12 prime-ideal columns and rank 10. Testing
the compatible natural Kummer class over all 2,352 normalized F49 directions
leaves exactly two coefficient directions and two one-dimensional character
spaces.

If the actual nonzero highest layer ramifies only above U, it must be one of:

| Natural normalized class | Exact ramification of eta |
|---|---|
| (a_phi/a5, a3/a5, 1)=(0,3,1) | 97, both places over 491, 587, 1567 |
| (a_phi/a5, a3/a5, 1)=(0,1,1) | 97, 293, both places over 1471, 1567 |

In either case every displayed supporting place has h=2. Maximal inertia
therefore forces the entire character to have exponent seven. The compatible
line further shows that its image is cyclic of order seven. There are no
hidden lower inertia layers in these classified cases.

This is a genuine support-dependent determination of the natural coefficients:
a_phi=0 and a3/a5 is 3 or 1. It is not an assumed general descent to F7.
Additional primes, including the forced 197 and 491, may still divide C while
remaining unramified in eta.

The finite support audit covers all 1,024 rational subsets of U. The augmented
criterion excludes nontrivial eta on 912 patterns and leaves first-layer
survivors on 112. Its only minimal surviving rational supports are

    {97,491,587,1567},     {97,293,1471,1567}.

These are support-pattern counts, not solution counts or a completion fraction.
The two surviving abstract ray/Kummer systems are retained explicitly.
See notes/FINITE_CLASSIFICATION.md.

## 4. A depth-three ceiling on the complete high-divisor class

Define H(C) to be the complete set of variable prime divisors with
v7(q^f_q-1)>=2. Arbitrary additional h<=1 divisors are permitted.

The new classification yields

    H(C) subset U without 1567 => eta=1 mod7^n and n<=3.

Removing 1373 as well gives

    H(C) subset {97,197,293,491,587,883,1471,1667}
                               => eta=1 mod7^n and n<=2.

At depth two, a beta-supporting prime still needs v7(v_q(C))=1. That is a
condition on its multiplicity in C, not a contradiction.

There is a further conclusion even when 1567 remains:

    H(C) subset U => n<=3.

If eta is trivial, a beta-supporting place must satisfy h>=n, and U has
maximum h=3. If eta is nontrivial, its classified exponent is seven, so the
same-lattice slope bound gives n<=h+1<=4. At depth four, beta could ramify
only at the inert place over 1373.

The classified characters, however, cancel on every rational unit. Their
inert supporting primes are -1 modulo seven, and their split-pair inertia
coefficients are opposite. Since (1373) is a principal inert prime outside
the character conductor, reciprocity forces its actual Frobenius value to be
trivial. Thus eta is fully locally trivial there, forcing h>=n. The inequality
3>=4 is impossible. This excludes the potential depth-four case without
assuming good reduction at 1373 or an unproved semilinear representation map.

Under COMPLETE H(C) subset U, a nontrivial eta therefore has n=3 and one of
the two displayed patterns. All five eta-supporting places then also ramify
in beta, with monodromy content t=1, so their multiplicities in C are prime
to seven. In the ratio-one pattern, the inert 1373 place is the only possible
extra beta ramification; it would require v7(v_1373(C))=2. In the ratio-three
pattern there is no extra beta ramification within this support class.

The complete high-divisor hypothesis is essential for these depth bounds.
A highest-layer-only restriction permits other primes to support beta.
See notes/ARITHMETIC_CONSEQUENCES.md.

## 5. Verification and failed strengthenings

Block 56 was restored cleanly and its verifier passed, including its selected
nested predecessor replays. The original ZIP is preserved byte for byte.
The new finite computations completed successfully:

| Check | Exact coverage |
|---|---:|
| Independently constructed residue fields | 12 |
| Direct seventh-power symbol comparisons | 132 |
| Normalized natural F49 coefficient directions | 2,352 |
| Complete F49 parameter pairs of the rank-two kernel | 2,401 |
| Rational support subsets | 1,024 |
| Rational-unit cancellation checks | 28 |
| Frobenius trace-congruence tests | 29,412 |
| Full principal-residue separated-root tests modulo 343 | 84,035 |
| Exact same-basis nonrational toric matrices | 486 |

The primary implementation uses phi-basis residue fields, seven-primary
logs, modular row reduction and Bareiss determinants. The independent program
uses sqrt5-basis fields, direct seventh-power symbols, subset determinant
expansion and Cramer's rule. It imports no primary arithmetic code. The
rank-ten minor is the exact integer -191706, nonzero modulo seven.

A stronger universal-zero claim fails: the two augmented patterns really
remain nonzero. The claim that every bad prime forces local triviality also
fails. The retained exact n=3, Q=29 model has trivial diagonal inertia but
nontrivial Frobenius of order seven. The h=0 condition cannot be discarded.

The initial streaming-container launch failed before execution. The observed
replacement replay completed. A document-generation escape-sequence warning
was corrected; it did not interrupt generation or affect mathematical code.
All historical failures remain in the unmodified predecessor.

The release verifier checks immutable payloads, 13 named inherited source
leaves, the copied primary arithmetic module, freshly regenerated full JSON
results, and rejection of an intentionally altered residue logarithm. The
final extracted-ZIP replay and integrity audit are recorded externally. They
are not included in their own checksum set.

No new Lean compilation or independent mathematical review was performed.
Independent finite implementations do not certify the inherited geometry.

## 6. Remaining obligation

The old 97/293 highest-layer branch is closed. The next specified targets are
the two five-place patterns above, or a uniform representation constraint
that reaches arbitrary highest-layer support. Their compatible actual endpoint
lattices, higher representation relations and global beta remain unresolved.

Depth one, general depth two, unrestricted prime support, the CM nonboundary
points, the higher Hilbert levels, the full signature, and full Beal remain
separate obligations.
