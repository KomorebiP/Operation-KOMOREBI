# Beal research, Block55
## Maximal-order Kummer filtering and full diagonal triviality on stated support classes

Release v5.5.0. 19 September2026.

The next bounded block is complete. Under the explicitly inherited Frey
representation hypotheses, a new maximal-order theorem converts local Kummer
annihilation into a depth-independent test for vanishing of the ENTIRE actual
diagonal correction. It proves full triviality on an expanded high-support
class, without bounding the remaining low-congruence prime divisors.

The complete reducible branch of A^3+B^5=C^7 remains unresolved. These are
written conditional proofs with exact computational certificates, not new
Lean certificates or independent mathematical review.

## 1. The strongest ramification layer must annihilate the same alpha

Let the complete global image of the actual eta_n have exponent7^e, e>=1.
At every place whose inertia attains that order,

    ord(eta_n(I_v))=7^e  =>  alpha|G_v=0.

This works even when beta is unramified there. It extends the previous
annihilation theorem, which required beta ramification.

The proof sets L=n-e and uses global exponent control to obtain
F22=1 mod7^L in the SAME natural basis. Write the local toric factorization

    N=mu[[-xy,x^2],[-y^2,xy]],   F=I+(x,y)^T(p,r),
    t=w(mu)>=1.

Maximal inertia gives t+w(y)=L and x a unit. Since yr=F22-1,
w(r)>=t>=1, so F12=xr vanishes modulo7. Natural inertia already vanishes
there. This proves local vanishing of the natural Kummer class.

The highest nonzero character layer eta_n^(7^(e-1)) is therefore supported
on local zeros of one common alpha. It satisfies the same five global
reciprocity rows(phi,2,3,sqrt5,7). No independent local coefficients or
unproved conjugation map are introduced.

## 2. A general criterion at every depth

For the high-congruence places h_v=v7(Nv-1)>=2, let M be their five-row
logarithm matrix. Let L_v=(ell_v(phi),ell_v(3),ell_v(sqrt5)). For each
normalized candidate alpha=(u,r,1), r nonzero, retain only the columns with
L_v dot alpha=0.

If every such restricted matrix has independent columns, then

    eta_n=1 mod7^n.

This kills the full character, not merely its highest layer at one selected
depth: a hypothetical nontrivial character would always have a highest
nonzero layer contradicting the criterion.

Only42 F7 candidates need be tested, even though the natural coefficients
live in F49 and there are2352 normalized directions. Every F49 zero set is
contained in an admissible F7 zero set. This is a monotonicity argument,
NOT a proof that the actual Kummer coefficients lie in F7.

## 3. A stronger arithmetic branch exclusion

Define H(C) to consist of variable rational divisors q with
v7(q^f_q-1)>=2. If

    H(C) subseteq {197,491,883,1471,1667},

then the new exact criterion proves

    eta_n=1 mod7^n,           n<=2.

Arbitrary additional prime divisors with h<=1 are permitted, regardless of
size or multiplicity. This is not a finite bound on the full support of C.

The certificate uses seven prime-ideal columns. Eight small nonzero minors
cover all admissible Kummer zero sets. All42 prime-field tests and all2352
extension-field directions were checked, with an independent residue and
rank implementation.

At depth2, an actual beta-supporting prime must be in this set and satisfy
v7(v_q(C))=1: its multiplicity is divisible by7 but not49. If all high-prime
multiplicities are prime to7, only depth1 remains. Depth2 itself is not
eliminated without that extra hypothesis.

For H(C) subseteq{491,1471}, this also upgrades Block54's result to full
actual character triviality at every depth and allows arbitrary low-h
additional divisors. The numerical bound remains n<=2; that repeated bound
is not being counted as a new depth2 exclusion.

A mixed class H(C) subseteq{197,491,883,1373,1471} likewise has eta=1 and
n<=3. If n=3, beta must ramify at the inert1373 place, requiring
v7(v_1373(C))=2 and a3/a5=1. The unit coefficient is still undetermined.

## 4. Small necessary witnesses and a conditional descent statement

A nonzero actual eta requires a minimally dependent subset of at most five
prime-ideal logarithm columns inside its maximal-order inertia support.
If the normalized actual coefficients are not in F7, the bound is four.
This bounds a necessary relation witness, NOT the actual total prime support.

If the natural Kummer rows on actual maximal support have rank2 overF7,
their one-dimensional kernel forces the normalized actual coefficients into
F7. Rank0 or1 does not. This is a support-dependent algebraic deduction,
not the missing general semilinear comparison theorem.

## 5. The attempted universal exclusion fails a concrete test

The declared illustrative universe is
{97,197,293,491,587,883,1373,1471,1567,1667}.
All1024 rational subsets were tested. The criterion passes on124 and leaves
first-layer survivors on900. There are8 maximal passing sets and15 minimal
surviving rational support sets. These counts are properties of the finite
criterion, not counts of solutions or a completion percentage.

At the inert primes97 and293, both h=2, the five-row columns are both
(1,0,0,0,0). The nonzero character vector(6,1) satisfies reciprocity, while
alpha=(0,1,1) vanishes at both places and has a3*a5 nonzero. Thus the new
necessary system is genuinely nonempty. It does not produce a Frey Jacobian
or compatible full actual Frobenius data.

A separate explicit split-norm491 local model disproves the stronger claim
that EVERY eta-ramified place annihilates alpha. Only the maximal-order
layer has been proved to do so. The failing strengthening is retained.

## 6. Verification observed before final packaging

The original Block54 verifier passed with its nested predecessor replays.
The new exact programs completed successfully:

| Check | Declared coverage |
|---|---:|
| Nonrational local matrices |8000|
| Of these, maximal eta ramification with beta unramified |6080|
| Highest-layer principal-unit power tests |1440|
| Full normalized F49 Kummer directions |2352 in both implementations|
| Rational support subsets |1024 in both implementations|
| Prime-ideal candidate subsets of size at most5 |1585 in both implementations|
| Compatible column circuits |23|
| Small main-class determinant certificates |8|
| Independent named symbol checks |360|
| Independent integer determinant benchmarks |625|

The independent program uses sqrt5-basis fields, direct seventh-power
symbols and fraction-free integer minors. It imports no primary arithmetic
code. The primary uses the preserved phi-basis code, seven-primary logarithms
and modular row reduction. Their exact conclusions agree.

The release verifier regenerates all four output files in a fresh temporary
copy and compares complete JSON results. The final extracted-ZIP run and
archive integrity audit are recorded separately, outside the immutable
package. No claim relies on a preexisting cached success flag.

An initial streaming-container launch failed before execution. The successful
replacement run and all historical failures are retained. The broad source
search returned irrelevant results; the required Milne source was opened
and rendered directly. No new Lean compilation or independent mathematical
review occurred.

## 7. What remains

The new criterion is general, but it does not pass every support. The next
target is an actual representation relation that excludes a surviving
first-layer pattern, such as97/293, without arbitrarily removing other
possible high primes. Depth1, depth2, unrestricted higher-support branches,
actual Kummer coefficients and full Frobenius compatibility remain open.
The CM cover, three higher Hilbert levels, full signature and full Beal
remain separate obligations.
