# Cyclotomic root filters: exact pole preservation and the limit of resultant control

This continuation starts from RR2's pointwise common-power theorem in `abc_work/routes/global/PROOF_NOTE.md`, SHA-256 `f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc`. The base package SHA-256 supplied by the coordinator is `f5b5e7336d5cae31502106100997cf02733b1054f62e3df39827002cfe7e9469`.

The requested target remains unrestricted ABC. This note executes one specific proposed bridge: apply roots-of-unity filters and cyclotomic separation to eliminate exceptional output-prime depth. The calculation yields a precise obstruction to that bridge. It does not prove ABC or refute more arithmetic uses of roots of unity. No historical originality or Lean-compilation claim is made.

## 1. The exact filtered resolvent

Let n>=1, A>B>=1 be coprime integers, zeta a primitive n-th root of unity, and eta a root of unity with eta^n=-1. For 0<=k<n,

    sum_(j=0 to n-1) zeta^(-kj)/(A-eta zeta^j B)
       = n A^(n-1-k)(eta B)^k /(A^n+B^n).                       (1)

This is an identity in the cyclotomic field containing eta and zeta. The minus variant replaces eta by 1 and A^n+B^n by A^n-B^n.

**Proof.** Since B/A<1, expand each denominator into its convergent geometric series. The inner character sum sum_j zeta^((l-k)j) is n when l=k modulo n and zero otherwise. Thus the left side becomes

    (n/A)(eta B/A)^k sum_(t>=0)(eta B/A)^(nt)
       = n A^(n-1-k)(eta B)^k /(A^n+B^n).

Alternatively, multiply through by the product of all denominators to obtain a polynomial identity. This removes any analytic dependency. In particular the character filter really cancels all residue classes except k. QED.

## 2. The bridge discriminator: filtering retains primitive depth

Let p be an odd prime such that p does not divide nAB, and suppose p splits sufficiently to realize the roots in the p-adic integers. For example, it is enough that p=1 modulo 2n. Write e=v_p(A^n+B^n)>=1. Every numerator on the right side of (1) is a p-adic unit. Therefore

    v_p(filtered resolvent in (1)) = -e                         (2)

for every k=0,...,n-1. Root filtering preserves the entire denominator depth e at a primitive prime. It supplies no cancellation factor there.

Moreover, exactly one of the n denominators A-eta zeta^j B is divisible by p. Indeed, A/B is a root of X^n+1 modulo p and the n roots eta zeta^j are distinct; their pairwise differences are p-adic units because p does not divide n. The other n-1 denominators are units, so that one branch has valuation exactly e. This is the content of separability or unramified root separation in this calculation. It isolates the deep contact into one branch; it does not limit its depth.

The same conclusion holds at an unramified prime of the cyclotomic field even when the roots are not all rational p-adic numbers, provided p does not divide the relevant root discriminant. The split case above already suffices to test the proposed gain and to give counterexamples below.

**What was tested.** The proposed implication was: Fourier cancellation or a p-unit root discriminant makes a primitive p^2 contact disappear from the filtered expression. Equations (1)-(2) show that implication is false. This failure closes that particular cancellation mechanism, not all roots-of-unity methods.

## 3. Resultants separate branches but do not bound evaluated valuations

For F(X)=X^n+B^n,

    gcd(F(A),F'(A)) = gcd(A^n+B^n,n)                            (3)

because gcd(A,A^n+B^n)=1. In particular, a prime p not dividing n can divide F(A) to arbitrarily high depth while the evaluated derivative F'(A)=nA^(n-1) remains a unit modulo p. A resultant or discriminant controls repeated roots modulo p; a repeated prime factor of the integer F(A) is a different condition.

The smallest useful negative control is

    n=2, B=1, A=7, p=5:
    Phi_4(7,1)=7^2+1=50,
    v_5(50)=2, but Phi_4'(7)=14 is a 5-adic unit.

The cyclotomic discriminant is -4, also a 5-adic unit. Thus neither the derivative nor the discriminant pays for the square factor 25. The k=0 filter is 2A/(A^2+1)=7/25, whose 5-adic valuation is -2, exactly as predicted.

For an odd prime exponent ell, the conductor separation already recorded in RR2 remains exact: gcd(A+B,Phi_(2ell)(A,B))=gcd(A+B,ell), and the latter cyclotomic value has ell-adic valuation exactly one when ell divides A+B. Every other prime divisor has order 2ell. This recovers RR2's inherited/primitive split. It gives no bound on the power of an unramified primitive prime in Phi_(2ell)(A,B).

## 4. Arbitrarily deep primitive contacts with unit discriminant

**Theorem.** Fix n>=1 and an odd prime p=1 modulo 2n. For every integer e>=1 there is a positive integer A>=2, coprime to p, such that

    v_p(A^n+1)=e,
    ord_p(A)=2n,
    p does not divide nA^(n-1),
    v_p(Phi_(2n)(A,1))=e.                                     (4)

**Proof.** Choose r modulo p with multiplicative order 2n. Then r^n=-1 modulo p and F'(r)=nr^(n-1) is nonzero modulo p. Inductively, if r_j is a root modulo p^j, the p candidates r_j+t p^j satisfy

    F(r_j+t p^j) = F(r_j)+t p^j F'(r_j) modulo p^(j+1).

Exactly one digit t modulo p lifts the root to depth j+1. At j=e choose a different digit. Then A=r_e+t p^e has valuation exactly e. Adding a multiple of p^(e+1) makes A>=2 if necessary without changing that valuation. Its residue modulo p is still r, so its order is still 2n.

To verify the final assertion, factor A^(2n)-1 into its integral cyclotomic factors. Since the residue order is 2n, p divides no factor Phi_d(A) with d a proper divisor of 2n. Also p does not divide A^n-1, because A^n=-1 modulo the odd prime p. Therefore the whole valuation e lies in Phi_(2n)(A,1). QED.

This theorem rules out any proposed universal cap on primitive depth that depends only on the conductor n, unit discriminant, or root separation. It is not a family of ABC counterexamples: the construction generally increases the base A at the same time as the depth. It therefore leaves possible arithmetic height bounds open.

## 5. A fixed-filter resultant dichotomy

The calculation extends beyond individual Fourier modes. Normalize the k-th expression in (1) by eta^(-k), and take a fixed integral linear combination with coefficients lambda_k. The result is

    n P(A,B)/(A^n+B^n),
    P(X,Y)=sum_(k=0 to n-1) lambda_k X^(n-1-k)Y^k.              (5)

Let H(T)=Phi_(2n)(T), and suppose P(T,1) is coprime to H(T). Its resultant

    R_P = Res(H(T),P(T,1))

is a fixed nonzero integer. If p is a primitive order-2n output prime and p does not divide n R_P, then p does not divide P(A,B). Therefore (5) still has valuation -v_p(A^n+B^n) at p.

**Proof.** The integer resultant admits a Bezout identity

    R_P=U(T)H(T)+V(T)P(T,1)

with integral polynomials U,V. Evaluate at T=A/B in the local ring at p. Since p does not divide B, all denominators are units. If both H(A/B) and P(A/B,1) vanished modulo p, the identity would force p|R_P, a contradiction. A primitive order-2n prime divides H(A,B) and no other cyclotomic factor of A^(2n)-B^(2n), so its valuation in A^n+B^n is exactly the valuation of that primitive component. QED.

More quantitatively, the amount of denominator depth canceled by P is at most v_p(R_P), since the same identity gives

    min(v_p(H(A,B)),v_p(P(A,B))) <= v_p(R_P).

Thus for fixed n and fixed coefficients, the filter can change primitive valuation only at a fixed finite resultant-prime set. This is not a finite-prime-set theorem for a family in which n or the coefficients vary. In a conductor-dependent family the resultant-prime set can itself move, and its height must be controlled rather than discarded.

For n=2^s, H(T)=T^n+1 is irreducible, while P has degree at most n-1. Hence every nonzero fixed P is coprime to H. Irreducibility here follows by the Eisenstein criterion at 2 after T is replaced by T+1: all intermediate binomial coefficients are even and the constant term is exactly 2. For n an odd prime ell, H is also irreducible, by the Eisenstein criterion at ell after the substitutions T->-T and T->T+1. In that case degree H=ell-1, so the only nonzero filters that cancel H identically are scalar multiples of H itself. They remove the primitive component from the observable completely; they do not bound its integer value or radical.

Two checks make the distinction concrete:

* For n=2 and P(T)=T+1, R_P=2. At A=7, p=5 the combined filter has value 2(7+1)/50=8/25 and retains depth two.
* For n=2 and P(T)=T-7, R_P=50. Its value at A=7 is zero. The contact was inserted into the adaptive resultant itself, which contains 5^2; this supplies no free radical bound.
* For n=ell prime, choosing P=Phi_(2ell) changes the filter to ell/(A+B), deleting every primitive contact. The untouched equality A^ell+B^ell=(A+B)Phi_(2ell)(A,B) still carries the entire unknown primitive factor.

There is an explicit budget for such a resultant. If d=degree H and L=sum_k |lambda_k|, the roots of H lie on the complex unit circle, so

    |R_P| = product_(H(z)=0) |P(z,1)| <= L^d.                   (6)

Consequently the product of primitive prime powers canceled by a coprime filter divides |R_P| and is at most L^d. This is an unconditional coefficient-height bound, not an ABC-strength estimate: d grows with the conductor.

An important countercheck is n=2^s with s>=1 and P(T)=T-2. The coefficient norm is only 3, but |R_P|=Phi_(2n)(2)=2^n+1. At the fixed base A=2,B=1 the observable is zero, and its moving resultant contains the whole unknown output. Thus small fixed coefficients alone do not keep the resultant-prime set fixed as n grows or produce a sublinear height budget.

This is a precise fixed-filter dichotomy with an explicit height ledger. It does not exclude filters accompanied by an additional arithmetic estimate that improves (6) for the contact packet actually used.

## 6. Exact gap left by the root calculation

In RR2, for c=A^n+B^n,

    U(c)=B_2(n) W_n G_n,    G_n divides n.

The filters above do more than relabel W_n: they explicitly test the mechanism that might have made its primitive valuation smaller. That mechanism preserves the valuation exactly, and Hensel lifting produces arbitrary local depth while preserving the primitive conductor.

To advance ABC with a root-of-unity construction, a further arithmetic input must compare the least global representatives A,B (or their heights) with the simultaneous root contacts. It would need to prove, in a stated family, a bound such as

    sum_(exceptional output p) (e_p-1)log p = o(n log A),

or transfer this weight into another radical budget. Separability, orthogonality, and resultants alone give no such comparison. For general h in 1+hq^n, an additional comparison is also needed to impose or replace the half-order relation.

## 7. Verification and continuation

`verify.py` performs exact modular polynomial checks of (1) after clearing denominators, identifies the unique deep branch, verifies the p-unit numerator of every Fourier mode, and constructs primitive contacts of prescribed depths. It includes the fixed-base exceptional example p=1093, n=182, A=2. These checks test the predicted obstruction, not an asymptotic distribution or ABC.

Route status: the proposed gain from standard resolvent filtering or unramified resultant separation is refuted. A root method using additional arithmetic heights remains open. The next useful continuation is a global simultaneous-contact height comparison, rather than another character-orthogonality identity.
