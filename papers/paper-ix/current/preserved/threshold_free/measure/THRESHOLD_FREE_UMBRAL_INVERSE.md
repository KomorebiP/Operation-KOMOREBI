# Threshold-free dyadic Kummer inverse theorem

All statements below are over the rational 2-adic integers R = Z_(2), or equivalently can be interpreted in Z_2. Let N = 2^s with s >= 1. Suppose a(0)=1 and

    Delta_1^k a(n) belongs to 2^k R, for all n,k >= 0.

Define the full degree sequence U_d by U_(Nn)=a(n) and U_d=0 if N does not divide d. Let V_d be the actual reciprocal Hurwitz coefficients:

    (sum_d U_d t^d/d!) (sum_d V_d t^d/d!) = 1.

Then V_d lies in R and vanishes off multiples of N. Writing b(n)=V_(Nn), one has

    Delta_1^k b(n) belongs to 2^k R, for all n,k >= 0.

In particular, no relation between k and n is imposed.

## Proof

Use R-linear umbral functionals L_U and L_V on R[X] defined by L_U(X^d)=U_d and L_V(X^d)=V_d. On two variables take their tensor product. The reciprocal identity says

    L_(U,V)((X+Y)^d) = 0 for d>0,
    L_(U,V)(1) = 1.

The source hypothesis implies

    L_U((X^N-1)^a X^d) belongs to 2^a R

for every a,d >= 0. If N does not divide d, every involved source degree has the same nonzero residue modulo N, and the expression vanishes. If d=Nn, the expression is exactly Delta_1^a a(n).

Because N is a power of two, all interior binomial coefficients binom(N,i) are even. Thus

    (X+Y)^N = (X^N-1) + (Y^N+1) + 2 R_N(X,Y),

where R_N is an integral polynomial with no pure monomials. For N=4 explicitly,

    R_4(X,Y)=2X^3Y+3X^2Y^2+2XY^3.

We prove

    L_V((Y^N+1)^k Y^ell) belongs to 2^k R

by induction on k and, for fixed k, induction on ell.

For k=0 this is integrality of the reciprocal coefficients, which follows by the ordinary binomial convolution recurrence, since U_0=1 and all U_d lie in R.

For k>0, the polynomial (X+Y)^(Nk+ell) has positive degree, so its joint umbral evaluation is zero. Expand it as

    [(X^N-1)+(Y^N+1)+2R_N(X,Y)]^k (X+Y)^ell.

After expanding R_N^c and (X+Y)^ell, each term is an integral coefficient times

    2^c (X^N-1)^a X^d (Y^N+1)^b Y^e,

with a+b+c=k. If b<k, the source factor is divisible by 2^a and the reciprocal factor is divisible by 2^b by the outer induction. Together with 2^c, the joint evaluation is divisible by 2^k.

If b=k, necessarily a=c=0. The terms then come only from (Y^N+1)^k(X+Y)^ell. The term with d=0, e=ell is exactly the desired expression, with coefficient U_0=1. Every other term has d>0 and e<ell, and is divisible by 2^k by the inner induction and source integrality.

All terms except the desired term have therefore been proved divisible by 2^k. Their sum plus the desired term is zero, proving the claim.

Finally,

    Y^N-1 = (Y^N+1)-2.

Expanding its kth power proves L_V((Y^N-1)^k Y^ell) divisible by 2^k: the i-th term has the proven reciprocal valuation at least i and a scalar factor of valuation k-i. Put ell=Nn to obtain Delta_1^k b(n).

## Arbitrary step, stronger precision

For positive H, put h=v_2(H). Then

    Delta_H^k b(n) belongs to 2^(k(h+1)) R

for all k,n >= 0. Indeed, if D=Delta_1 then

    Delta_H=(1+D)^H-1=sum_(i=1)^H binom(H,i)D^i.

The identity i binom(H,i)=H binom(H-1,i-1) gives

    v_2(binom(H,i)) >= h-v_2(i).

Since i-v_2(i)>=1 for every i>=1, each scalar 2^i binom(H,i) is divisible by 2^(h+1). In the kth power, a multi-index (i_1,...,i_k) contributes a scalar product of binomial coefficients and a difference of total order I=sum i_j. The threshold-free estimate contributes 2^I, so that entire term is divisible by 2^(k(h+1)). All sums here are finite. For H=0 and k>0 the difference is zero; for k=0 the integrality statement applies.

## Application to all four N=4 addresses

Let

    A_j(t)=j! sum_(n>=0) t^(4n)/(4n+j)!,
    F_j(t)=A_j(t)^(-1),
    C_j(n)=(4n)! [t^(4n)] F_j(t).

The source Hurwitz coefficients are

    g_j(n)=binom(4n+j,j)^(-1),

with formulas

    g_0(n)=1,
    g_1(n)=1/(4n+1),
    g_2(n)=1/[(4n+1)(2n+1)],
    g_3(n)=3/[(4n+1)(2n+1)(4n+3)].

For h(n)=1/(An+B), with A even and B odd, the exact difference formula is

    Delta_1^k h(n)=(-A)^k k! / product_(q=0)^k [A(n+q)+B].

It lies in 2^k R. Products of such sequences retain this property by the discrete product rule

    Delta_1^k(fg)(n)=sum_(i=0)^k binom(k,i) Delta_1^i f(n) Delta_1^(k-i) g(n+i).

Consequently every g_j satisfies the required source property. The theorem therefore gives the unconditional result

    v_2(Delta_H^k C_j(n)) >= k(1+v_2(H)),

for H>0, every n,k>=0, and every j in {0,1,2,3}, with the zero-safe interpretation for vanishing differences.

The original unnormalized numbers satisfy E_(4n)^(4,j)=j! C_j(n), giving the additional v_2(j!) bit in all statements.

## Extension to every dyadic section size

The N=4 specialization is not a limit of the argument. For every N=2^s with s>=1 and every address 0<=j<N, put

    A_(N,j)(t)=j! sum_(n>=0) t^(Nn)/(Nn+j)!,
    C_(N,j)(n)=(Nn)! [t^(Nn)] A_(N,j)(t)^(-1).

Its source is

    g_(N,j)(n)=j!/product_(l=1)^j(Nn+l).

Strip the exact power of two from each l. If e_l=v_2(l), then e_l<s because 1<=l<N. Thus

    g_(N,j)(n)=product_(l=1)^j
       [(l/2^e_l)/((N/2^e_l)n+l/2^e_l)].

Every denominator is an affine expression with even slope and odd intercept. Its odd constant numerator does not alter the source higher-difference property. The exact linear-reciprocal formula and the discrete product rule prove source P2 at every such size and address. The same inverse theorem gives

    v_2(Delta_H^k C_(N,j)(n)) >= k(1+v_2(H))

for every dyadic N>=2, every allowed address, all n,k>=0 and H>0.

## Continuous interpolation

The coefficients a_k=Delta_1^k C_(N,j)(0) satisfy v_2(a_k)>=k. Hence

    C_(N,j)(x)=sum_(k>=0) a_k binom(x,k)

converges uniformly on Z_2, agrees with the original sequence on nonnegative integers, and defines its unique continuous interpolation. The first-difference bound implies

    v_2(C_(N,j)(x)-C_(N,j)(y)) >= 1+v_2(x-y)

for all distinct x,y in Z_2. This follows by continuity from the natural-index estimate; the zero-safe convention covers equal values.

The present estimate alone does not assert global analyticity. A bound v_2(a_k)>=k does not force v_2(a_k)-v_2(k!) to tend to infinity, since its guaranteed lower bound s_2(k) is only one along powers of two. Stronger coefficient estimates would be needed for that additional conclusion.

## Source of the proof idea and scope

The induction is an adaptation of the umbral reciprocal argument in Ira M. Gessel, *Applications of the classical umbral calculus*, Section 8, Theorems 8.1 and 8.3, https://arxiv.org/abs/math/0108121. The proof above supplies all details needed here: it changes the Frobenius exponent to the power of two N and uses a constant-character source together with its sign-reversed reciprocal character. It does not assert that the resulting Kummer class is closed under arbitrary Hurwitz products. Such closure is false: convolution of the constant N=4 sequence with itself has first packet values 1,2 and hence fails the required first difference parity.

This is a paper proof. No Lean compilation is claimed in this file. The original ordinary-Euler dyadic simplicity problem is distinct and is not closed by this threshold-free congruence result.
