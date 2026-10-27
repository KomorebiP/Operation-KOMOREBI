# A positive cyclotomic degree budget for the exceptional birth part

This is a separate extension of the frozen filtered-resolvent note. Its input is RR2's exact identity for coprime integers A>B>=1, n>=1:

    c=A^n+B^n,    R=rad(A^n B^n c),
    U(c)=c/rad(c)=B_2(n) W_n G_n,
    B_2(n)<=A,    G_n divides n.

For every odd prime p|c, write d_p=ord_p(A/B) and e_p=v_p(A^d_p-B^d_p). Then v_p(c)=e_p+v_p(n), and

    W_n=product_(odd p|c) p^(e_p-1).

Only primes with e_p>=2 contribute to W_n; call these exceptional birth primes. Define the set of their distinct multiplicative orders

    E_n={d_p : odd p|c and e_p>=2},
    D_n=sum_(d in E_n) phi(d).

E_n is a set, so a conductor is counted once even if many exceptional primes have that order. D_n is a cyclotomic degree budget. No historical originality or Lean-compilation claim is made.

## 1. Exact allocation to cyclotomic factors

**Theorem 1.** Every d in E_n divides 2n and does not divide n. Moreover,

    W_n divides product_(d in E_n) Phi_d(A,B),                  (1)
    log W_n <= D_n log(A+B).                                   (2)

Here Phi_d(A,B)=B^phi(d) Phi_d(A/B) is the integral homogeneous cyclotomic polynomial.

**Proof.** For p|c, A/B has n-th power -1 in the odd-prime field, so its order d_p divides 2n and does not divide n. Also d_p divides p-1, hence p does not divide d_p.

Factor

    A^d_p-B^d_p = product_(k|d_p) Phi_k(A,B).

If p divided a factor Phi_k(A,B) with k a proper divisor of d_p, it would divide A^k-B^k, contrary to the definition of the order. Therefore

    v_p(Phi_d_p(A,B)) = e_p.                                  (3)

All primes assigned to the same d are distinct, so the product of p^(e_p-1) over those primes divides Phi_d(A,B). Multiplication over the distinct d proves (1).

For (2), factor Phi_d(A,B) over the primitive d-th roots zeta. Each factor A-zeta B has complex absolute value at most A+B. There are phi(d) factors, so

    |Phi_d(A,B)| <= (A+B)^phi(d).

The value is positive for A>B>0: d=2 gives A+B, and nonreal roots pair into positive conjugate products. The case d=1 does not occur. Taking logarithms in (1) proves (2). QED.

**Imprimitive-prime audit.** A prime may also divide cyclotomic factors with conductor d_p p^j, where it is an imprimitive prime. None of those extra appearances is used in (3): the allocation is exclusively to its actual order d_p, which is prime to p. Possible additional factors in the product on the right of (1) only enlarge that product. The inherited lifting v_p(n) has already been placed in G_n and is not counted again as birth depth. The prime 2 is entirely in B_2(n). Thus there is neither an omitted branch nor a multiplicity assumption in (1).

The polynomial identity

    X^n+Y^n = product_(d|2n, d does not divide n) Phi_d(X,Y)

also shows

    0<=D_n<=n.                                                (4)

## 2. Uniform restricted ABC theorem

Fix epsilon>0 and gamma=epsilon/(1+epsilon). Combining the degree budget with the exact lifting identity gives

    log U(c) <= log A + log n + D_n log(A+B).                   (5)

Since A>=2 and A+B<=A^2,

    log U(c) <= (1+2D_n)log A + log n.                         (6)

**Theorem 2.** If

    1 + log_2(n) + 2D_n <= gamma n,                            (7)

then

    c <= R^(1+epsilon).                                       (8)

**Proof.** Condition (7) and log n<=log_2(n)log A imply log U(c)<=gamma n log A<=gamma log c. Because rad(A^n B^n)>=1,

    log R=log c+log rad(AB)-log U(c)>=(1-gamma)log c.

This is (8). QED.

The sharper base-dependent sufficient criterion replaces 2D_n in (7) by D_n log(A+B)/log A and log_2(n) by log n/log A.

**Corollary 2.1.** Fix epsilon>0 and 0<delta<1. There is N_(epsilon,delta), independent of A and B, such that every admissible triple with n>=N_(epsilon,delta) and

    D_n <= n^(1-delta)

satisfies c<=R^(1+epsilon). Indeed, the left side of (7), divided by n, is at most n^(-1)+log_2(n)/n+2n^(-delta), which tends to zero.

**Corollary 2.2 (degree escape).** If c>R^(1+epsilon), then necessarily

    D_n > (gamma n-1-log_2(n))/2.                              (9)

For sufficiently large n, high quality therefore requires exceptional birth primes to occupy a positive linear fraction of the available cyclotomic degree. Their number or size alone is not the controlling statistic in this theorem.

## 3. What this adds

The preceding prime-size theorem bounded exceptional primes by n^(1/2-delta). The present theorem permits arbitrarily large exceptional primes, as long as the sum of the degrees of their distinct order channels is sublinear in n. All primes sharing one order use that channel's degree once.

For example, if n=3^s, all possible conductors are 2*3^j with 0<=j<=s. The total degree through level J is

    sum_(j=0 to J) phi(2*3^j)=3^J.

If exceptional birth primes occupy only these levels with J<=(1-delta)s, then D_n<=n^(1-delta), regardless of how large those primes are. This gives (8) for sufficiently large s.

For an odd prime exponent ell, the possible conductors are 2 and 2ell. If there is any primitive exceptional prime, its channel already costs ell-1 in degree. Thus this theorem agrees with the earlier prime-exponent obstruction and does not solve its hard branch. For n a power of two, the only possible conductor is 2n and any exceptional prime costs the full degree n; the criterion then requires W_n=1. This boundary case is explicit, not silently excluded.

The new condition is a genuine additional structural regime. It is not a universal numerical improvement on every earlier prime-size bound; one may retain the smaller of the old primewise estimate and (2).

## 4. Remaining gap

Nothing proved here prevents exceptional birth primes from occupying a conductor of degree comparable to n. One such prime in the largest-order channel can already make D_n linear. The theorem does not bound its valuation or its radical contribution. It therefore proves a positive restricted ABC statement and a necessary order-degree escape condition, not unrestricted ABC.

The next obligation is to control high-degree exceptional channels, or show that their birth depth must be paid by another radical budget. Root factorization has reduced the needed statistical object from individual prime size to occupied cyclotomic degree, but has not supplied that last arithmetic estimate.

## 5. Verification

`verify_order_budget.py` independently computes homogeneous cyclotomic values by exact division of A^d-B^d, assigns each odd exceptional prime exclusively to its actual order, checks the multiplicity identity (3), the divisibility (1), the degree bound (4), and the exact integer version of the size estimate. The finite assertion and its domain are recorded in `order_budget_verification.json`. These checks supplement the proof and do not establish a universal distribution law.
