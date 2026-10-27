# From cyclotomic degree to a near-linear exceptional-prime cutoff

This is a consequence of the separate `ORDER_BUDGET.md`, whose source SHA-256 is `46679caa7dedefda2557b48f16e3de0f375b8e4e2b03651694a6001d8837f0ea`. It adds no hypothesis about the distribution of exceptional primes and no historical originality claim. The target remains unrestricted ABC, which is not proved here.

Use the same notation: A>B>=1 are coprime integers, n>=1, c=A^n+B^n, R=rad(A^n B^n c), gamma=epsilon/(1+epsilon), and

    d_p=ord_p(A/B),    e_p=v_p(A^d_p-B^d_p)

for each odd p|c. The exceptional birth primes have e_p>=2. Their distinct actual orders form E_n, with degree budget

    D_n=sum_(d in E_n) phi(d).

Let P_n be their largest prime, setting P_n=1 if there is none. Let

    K_n=number of divisors d|2n with d not dividing n.

The previously proved inputs are

    log U(c)<=log A+log n+D_n log(A+B),
    c>R^(1+epsilon) implies D_n>(gamma n-1-log_2(n))/2.          (1)

## 1. Counting the available order channels exactly

Write n=2^s m with m odd. The allowed divisors are exactly d=2^(s+1)t with t|m. Hence

    K_n=tau(m)=tau(2n)-tau(n)<=tau(2n).                        (2)

If every exceptional birth prime is at most Y>=1, then each occupied order d has a witness prime p<=Y, and

    phi(d)<=d<=p-1<=Y-1.

Since there are at most K_n occupied orders,

    D_n<=K_n(Y-1)<=tau(2n)(Y-1).                              (3)

No restriction on the number of primes in one order channel is needed: its degree is counted once. If there are no exceptional primes, D_n=0 and (3) still holds; taking Y=P_n=1 makes both sides zero.

Combining (3) with the degree criterion proves an exact sufficient condition:

    1+log_2(n)+2K_n(Y-1)<=gamma n
        implies c<=R^(1+epsilon).                              (4)

Put T_n=gamma n-1-log_2(n). If T_n>=0, a quality violation forces D_n>T_n/2>=0, so there is an odd exceptional birth prime. Taking Y=P_n and using (1) then gives the exact escape condition

    T_n>=0 and c>R^(1+epsilon)
        implies P_n>1+(gamma n-1-log_2(n))/(2K_n).               (5)

For sufficiently large n, this says that a high-quality common-power triple needs an exceptional birth prime at least on the scale n/K_n. When T_n<0, no existence of an odd exceptional prime is claimed: for example A=63,B=1,n=1 gives c=64,R=42 and c>R^1.1, with no odd output prime at all. Condition (5) is necessary, not an existence statement for high-quality triples.

## 2. Elementary divisor bound

For every eta>0 there is a constant C_eta such that

    tau(r)<=C_eta r^eta    for every integer r>=1.              (6)

Here is a direct proof. For every exponent a>=1, a+1<=2^a. If p>=2^(1/eta), this gives a+1<=p^(eta a). For each of the finitely many smaller primes p, put

    C_(p,eta)=sup_(a>=0) (a+1)/p^(eta a).

This constant is finite because the denominator grows geometrically while the numerator is linear. Multiplying the prime-power inequalities over r=product p^a yields (6), with C_eta the finite product of these small-prime constants. Thus the divisor count is subpolynomial uniformly in r; no analytic prime-counting theorem is used.

## 3. Uniform near-linear cutoff theorem

**Theorem.** Fix epsilon>0 and 0<delta<1. There is N_(epsilon,delta), independent of the coprime bases A>B>=1, such that if n>=N_(epsilon,delta) and every odd exceptional birth prime dividing A^n+B^n satisfies

    p<=n^(1-delta),

then

    c<=R^(1+epsilon).                                        (7)

**Proof.** Apply (6) with eta=delta/2. Equations (2)-(3) imply

    D_n<=C_delta n^(1-delta/2).

Therefore

    (1+log_2(n)+2D_n)/n
       <=(1+log_2(n))/n+2C_delta n^(-delta/2) -> 0.

For sufficiently large n this is at most gamma, so the audited degree-budget theorem gives (7). All constants depend only on epsilon and delta. QED.

This improves the earlier common-power cutoff n^(1/2-delta) to every fixed power below n. The restriction concerns exceptional birth primes only. Ordinary output primes may be arbitrarily large, and the degree theorem additionally permits very large exceptional primes in low-order channels. The theorem concerns the common-power family, not arbitrary primitive ABC triples with n=1.

## 4. Weighted escape into near-linear orders

A slightly stronger consequence identifies where the missing weight must sit. For Z>=1 define

    W_(order<=Z)=product_(odd exceptional p|c, d_p<=Z) p^(e_p-1),
    W_(order>Z)=W_n/W_(order<=Z).

Allocating the first packet to its occupied cyclotomic factors, exactly as in `ORDER_BUDGET.md`, gives

    log W_(order<=Z)<=K_n Z log(A+B).                          (8)

Set Z=n^(1-delta). By (6), the right side is O_delta(n^(1-delta/2)log A), which is o(log c) uniformly in A,B because log c>=n log A and log(A+B)<=2log A. The ordinary and 2-adic factors also obey

    log(B_2(n)G_n)<=log A+log n=o(log c)

uniformly in the bases. If c>R^(1+epsilon), the exact identity R=rad(AB)c/U(c) gives

    log W_n>gamma log c+log rad(AB)-log(B_2(n)G_n).

Subtracting (8) proves that, for all sufficiently large n depending only on epsilon,delta,

    log W_(order>n^(1-delta))
        >(gamma/2)log c+log rad(AB).                           (9)

Every prime in that last packet satisfies p>=d_p+1>n^(1-delta)+1. Thus high-quality triples require not merely one large exceptional prime, but a linear logarithmic birth-depth contribution in order channels beyond every fixed sublinear power of n.

## 5. What remains

An exceptional prime in the top conductor can have phi(d) comparable to n, and neither the degree bound nor the divisor estimate controls its birth depth. For prime n and powers of two, the largest-order channel already has this property. Equations (5) and (9) sharpen the location of a possible obstruction; they do not rule it out.

No new finite experiment is needed for these deductions: they follow from the audited degree allocation and the elementary divisor proof above. The outstanding input is still an arithmetic bound on high-degree, large-order exceptional birth contacts.
