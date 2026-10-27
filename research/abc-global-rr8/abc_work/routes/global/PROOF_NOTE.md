# Pointwise exponent lifting and the exceptional birth-depth obstruction

Base: latest square-kernel checkpoint, archive SHA-256 `f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59`.

This route does not prove unrestricted ABC. It proves a pointwise restricted ABC theorem for common-power inputs, uniformly in their bases, and removes all ordinary moving output primes from that branch's unresolved obstruction. No historical originality or Lean-verification claim is made.

## 1. Target and family

Unrestricted ABC asks: for every epsilon > 0, does there exist K_epsilon such that every primitive positive triple a+b=c satisfies c <= K_epsilon rad(abc)^(1+epsilon)?

Here let A>B>=1 be coprime integers, n>=1, a=A^n, b=B^n, c=A^n+B^n, D=rad(AB), and R=D rad(c). This is a restricted family. Although every primitive triple has the representation n=1, estimates that require n to grow do not settle arbitrary triples.

For each odd prime p dividing c, put

    d_p = ord_p(A/B),
    e_p = v_p(A^d_p - B^d_p).

The quotient A/B is taken modulo p. It is invertible since gcd(A,B)=1. Call p exceptional for these bases when e_p>=2, and ordinary when e_p=1.

## 2. Exact pointwise identity

**Theorem 1.** For each odd p dividing c,

    v_p(c) = e_p + v_p(n).                                      (1)

Define

    W_n = product_(odd p|c) p^(e_p-1),
    G_n = product_(odd p|c) p^v_p(n).

Then G_n divides n. Let B_2(n)=2^(v_2(c)-1) if c is even, and B_2(n)=1 if c is odd. Then

    U(c) := c/rad(c) = B_2(n) W_n G_n,                          (2)
    c/R = B_2(n) W_n G_n / D.                                  (3)

If A,B are odd, B_2(n)=2^(v_2(A+B)-1) for odd n and B_2(n)=1 for even n. If they have opposite parity, B_2(n)=1. In every case B_2(n)<=A.

**Proof.** Since (A/B)^n=-1 modulo the odd prime p, the order d_p is even and n=(d_p/2)k with k odd. The factors A^(d_p/2)-B^(d_p/2) and A^(d_p/2)+B^(d_p/2) cannot both vanish modulo p; the second vanishes and the first does not. Therefore

    e_p = v_p(A^(d_p/2)+B^(d_p/2)).

For odd p and odd k, the elementary lifting identity is

    v_p(X^k+Y^k)=v_p(X+Y)+v_p(k)

when p divides X+Y and p does not divide XY. One proves it by factoring the sum when p does not divide k and using the binomial expansion for each multiplication of the exponent by p. Here p does not divide d_p because d_p divides p-1, so v_p(k)=v_p(n). This proves (1).

Subtract one from every positive output valuation to obtain (2), and use R=D rad(c) for (3). The factors in G_n use a subset of the prime-power factors of n, proving G_n|n. For odd A,B and odd n, the quotient (A^n+B^n)/(A+B) is odd, so v_2(c)=v_2(A+B). For even n, both A^n and B^n are 1 modulo 8 and v_2(c)=1. Finally, in the odd-n case B_2(n)<= (A+B)/2 < A, and otherwise B_2(n)=1<=A. QED.

**Consequence.** The entire powerful-part contribution of ordinary odd output primes divides n, irrespective of how large those primes are. Its logarithmic weight is at most log n. There is no cutoff, density limit, averaging hypothesis, or omitted moving ordinary tail in this statement.

## 3. An elementary uniform bound on small exceptional primes

For a real Y>=1 let

    J(Y)=sum_(odd prime p<=Y) (p-1).

The exceptional part W_(<=Y) of W_n satisfies

    log W_(<=Y) <= J(Y) log A.                                 (4)

Indeed, p^e_p divides the positive integer A^d_p-B^d_p < A^d_p. Thus

    (e_p-1)log p <= e_p log p < d_p log A <= (p-1)log A.

Summation proves (4). This bound is deliberately elementary; the stronger elementary Chebyshev estimate J(Y)=O(Y^2/log Y) is not needed below. The trivial bound

    J(Y) <= floor(Y)(floor(Y)-1)/2 <= Y^2/2                      (5)

is sufficient.

**Theorem 2 (explicit restricted ABC criterion).** Set gamma=epsilon/(1+epsilon). If every exceptional odd output prime is at most Y and

    1 + J(Y) + log_2(n) <= gamma n,                            (6)

then

    c <= R^(1+epsilon).                                        (7)

**Proof.** Equations (2), G_n<=n, B_2(n)<=A and (4) give

    log U(c) <= (1+J(Y))log A + log n
              <= gamma n log A <= gamma log c.

Since D>=1, log R=log c+log D-log U(c)>=(1-gamma)log c. Rearrangement gives (7). QED.

**Corollary 2.1 (uniform growing-cutoff theorem).** Fix epsilon>0 and 0<delta<1/2. There is N_(epsilon,delta), independent of the coprime bases A>B>=1, such that if n>=N_(epsilon,delta) and every exceptional odd prime divisor of A^n+B^n is at most n^(1/2-delta), then c<=R^(1+epsilon).

Proof: by (5), the left side of (6), divided by n, is at most n^(-1)+(1/2)n^(-2delta)+log_2(n)/n, which tends to zero. All ordinary output primes are allowed to grow without restriction.

The absence of a uniform coefficient K in this large-n conclusion should not be misread: it requires n>=N and the stated exceptional-prime condition. When bases vary, this says nothing about the infinitely many remaining triples with small n.

## 4. Quantified escape beyond the square-root scale

Split W_n=W_(<=Y) W_(>Y). If c>R^(1+epsilon), (3) implies

    log W_n > gamma log c + log D - log B_2(n) - log G_n.

Consequently

    log W_(>Y) > gamma log c + log D
                  - (1+J(Y))log A - log n.                    (8)

If Y=n^(1/2-delta), the two subtracted terms are o(log c), uniformly in A,B. Thus for sufficiently large n, any such high-quality triple must satisfy

    log W_(> n^(1/2-delta)) > (gamma/2) log c + log D.           (9)

This is a pointwise necessary condition: a linear fraction of log c must come from genuinely exceptional birth depths at primes above the cutoff. Ordinary lifting, even at arbitrarily large primes, cannot supply it.

## 5. Prime exponents and a linear-scale primitive obstruction

The order condition also gives a stronger statement when n is an odd prime ell. Every odd output prime has d_p=2 or d_p=2ell. The first case consists exactly of the odd primes dividing A+B. Define

    W_prim = product_(odd p|c, d_p=2ell) p^(e_p-1).

Then the identity sharpens to

    U(A^ell+B^ell) = U(A+B) ell^[ell divides A+B] W_prim.        (10)

Every prime occurring in W_prim is at least 2ell+1 and is exceptional for the ratio A/B. To prove (10), note that for d_p=2 the birth depth e_p is v_p(A+B); the 2-adic contribution agrees with U(A+B) because ell is odd. The only possible odd prime in G_ell is ell itself. By Fermat's congruence, ell divides A^ell+B^ell exactly when ell divides A+B, so the factor from G_ell is the one displayed. All remaining output primes have order 2ell, which divides p-1 and hence forces p>=2ell+1.

This proves another uniform restricted ABC theorem: for any epsilon>0, all sufficiently large odd prime exponents ell and all coprime bases A>B>=1 for which W_prim=1 satisfy c<=R^(1+epsilon). Indeed, U(A+B)<2A gives U(c)<=2Aell, and

    log U(c)/log c <= 1/ell + log(2ell)/(ell log 2) -> 0

uniformly in the bases. No cutoff is imposed on inherited exceptional primes dividing A+B. If instead c>R^(1+epsilon), then necessarily

    log W_prim > gamma log c + log D - log U(A+B) - log ell.

Thus a large odd prime exponent pushes the entire unresolved linear-height mass into exceptional primes of order exactly 2ell, all above the linear cutoff 2ell.

For n=2^s with s>=1, all odd output primes have d_p=2n. Here G_n=B_2(n)=1, so U(c)=W_n exactly; every repeated output prime is exceptional and at least 2n+1. This is an exact reduction to repeated primitive factors, not a bound excluding those factors.

## 6. Why this does not solve ABC

Equation (2) controls inherited lifting exactly. It does not bound W_n at large exceptional primes. The estimate e_p log p < (p-1)log A becomes too weak when p grows at or above the square-root scale in n, and summing all such bounds is not sublinear in n log A. A prime with exceptional birth depth can contribute to a single c without violating a density estimate or a collision bound.

For general c=1+hq^n, h is not constrained to be 1 or a compatible power. Then the congruence q^n=-h^(-1) mod p need not put n in the half-order class, so (1) no longer follows. The full target therefore still needs both a large-exceptional-prime estimate and control of unrestricted multipliers or arbitrary input exponent vectors.

## 7. Countercheck against dropping W_n

Base 2 has p=1093 with ord_p(2)=364 and v_p(2^364-1)=2. At n=182,

    v_1093(2^182+1)=2,    v_1093(182)=0.

Thus the unjustified stronger statement U(2^n+1)|n is false. The exceptional factor W_n is essential. The accompanying verifier checks this example by exact modular arithmetic without factoring the entire 55-digit output.

## 8. Evidence and next continuation

These are elementary proofs, not results inferred from finite tests. `verify.py` checks the full identity on a stated finite family using integer factorization and modular order computations, checks an independent order algorithm on small primes, and verifies the base-2 exceptional example. The computation does not establish any universal distribution statement about exceptional primes.

Next mathematical obligation: obtain a uniform sublinear estimate for log W_n at large exceptional primes, or construct an arithmetic mechanism that transfers their birth depth to another radical budget. This route remains open; neither ordinary-channel control nor the small-exceptional theorem resolves that obligation.
