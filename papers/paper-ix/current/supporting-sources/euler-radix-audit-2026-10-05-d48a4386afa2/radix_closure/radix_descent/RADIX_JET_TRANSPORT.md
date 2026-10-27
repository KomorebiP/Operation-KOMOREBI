# Exact radix transport of Euler tails and the surviving joint-jet obstruction

Base checkpoint: `Euler-shifted-obstruction-20261005`.
Base archive SHA256: `7125e5ed1ce7b0a3fb25473284ac92fa1a4c6db42862980f1b07cbfb50233dea`.
Scope: the actual Euler residual simplicity problem, including whether exact radix compression supplies a terminating joint-zero descent. No Lean run.

## 1. The analytic lift of the row weight theorem

Let A(s)=(9^(s+1)-1)/(8(s+1)(2s+1)), with its removable value at -1. The inherited source proof establishes A in Z_2<s>^x and A=1 modulo 2 coefficientwise. For m>=1 let

    f_m(s)=kappa_m binom(2s,2m) A(s-m),
    kappa_m=2^(4m-1) a_m,             a_m in Z_2^x.

For the actual Euler kernel a_m=-2(2m-1)B_(2m). The polynomial identity

    binom(2s,2m)=binom(s,m) product_(i=0)^(m-1)
                                (2s-2i-1)/(2m-2i-1)

shows that

    f_m(s)=2^(4m-1) binom(s,m) U_m(s),                     (1)

where U_m is an integral restricted analytic unit, reducing to 1 modulo 2. Thus the row valuation W_2,4(s,m)=4m+v_2 binom(s,m) is exact up to the common -1, at every dyadic s at which the summand is nonzero. The binomial valuation is not being substituted for a coefficientwise Gauss valuation.

More generally let C>=1 and

    f_m(s)=2^(Cm+d) binom(s,m) U_m(s),
    U_m in Z_2<s>^x, U_m=1 (mod 2),

for all m>=r>=1, and put B=2^C. The quotient

    f_(m+1)/f_m=2^C (s-m)/(m+1) U_(m+1)/U_m              (2)

extends analytically across the zeros of f_m. Whenever m+1 is not divisible by B, this quotient lies in 2 Z_2<s>. Consequently every full block has the exact identity

    sum_(h=0)^(B-1) f_(Bq+h)(s)=f_(Bq)(s) V_q(s),
    V_q in 1+2 Z_2<s>,                                  (3)

provided Bq>=r. The same conclusion holds for the initial partial block r,...,B ceil(r/B)-1. The initial partial block is absent when B divides r.

This is stronger than a value-only dominance statement: each grouped block differs from its first packet by an analytic unit. Its individual roots and multiplicities are preserved.

## 2. The exact variable rescaling retains the units

On the residue disc s=a+BY, 0<=a<B, write

    D_(a,q)(Y)=binom(a+BY,Bq)/binom(Y,q).

The apparent quotient is an integral polynomial unit. To see this, factor the numerator's falling factorial. The q factors with index i=a+Bj are B(Y-j). After cancellation of Y's falling factorial, every remaining factor is

    2^v (odd + 2^(C-v) Y),     v<C.

The scalar valuation cancels because

    v_2((Bq)!)-Cq-v_2(q!)=(B-C-1)q,

which is exactly the sum of the valuations of the remaining factors. Thus D_(a,q) belongs to 1+2 Z_2[Y]. No root has been canceled without recording its multiplicity: the canceled skeleton is precisely binom(Y,q).

Combining this with (3) gives

    sum_(h=0)^(B-1) f_(Bq+h)(a+BY)
      =2^(CBq+d) binom(Y,q) U_new,q(Y),                  (4)

where every U_new,q is an integral restricted analytic unit. The renormalized slope is C_new=C B. Starting at C=4, the first radix is16, the new slope is64, and the next cumulative scale is16*2^64=2^68. Iteration proves the historical radix tower with the full analytic unit data retained.

The series converge in the restricted Tate algebra: binom(s,m) has coefficient denominators dividing m!, so C>=2 gives coefficient valuation at least (C-1)m+d. The Euler tower always has C>=4.

There are two distinct operations which must not be conflated. The original scalar residual coefficients have valuation

    lambda_r(q)=3q+s_2(r+q)-s_2(r).

The slope4 radix theorem applies to the full binomial row term (1). It incorporates the falling-factorial contribution which is absent from lambda. Applying the slope4 theorem to lambda alone would use the wrong object.

## 3. The exact joint-zero equations after a cut

Let Q=ceil(r/B). When B does not divide r, let P(s) be the grouped initial partial block. Then, on every a+B Z_2,

    T_r(a+BY)=P(a+BY)
       +sum_(q>=Q) 2^(CBq+d) binom(Y,q) U_new,q(Y).      (5)

If B divides r the first term is zero and Q=r/B. Differentiation with respect to Y is exact. A double zero of T_r gives

    P(a+BY)+T_new(Y)=0,
    B P'(a+BY)+T_new'(Y)=0.                             (6)

Equations (6) do not assert T_new=T_new'=0. The partial block is an inhomogeneous forcing term; it is not removed by the decrease r -> ceil(r/B). Moreover the new units U_new,q are the actual grouped units, not the prescribed Bernoulli units for a smaller Euler index. Radix proves (4)-(6), but does not prove this missing identification or an invariant excluding their simultaneous vanishing.

This is the analytic form of the earlier carry obstruction, not an omission of remote carries. Every carry and odd unit is retained in (4)-(6). A proposed well-founded descent must either carry the forcing and the unit sequence as part of its state, or prove a new Bernoulli-specific elimination of them.

## 4. A unit-preserving double-contact construction

The following establishes a sharp limit of conclusions based only on the complete radix valuation data and the actual source A. It is not an Euler counterexample.

Take the ordinary actual index

    r=17659*2^640-161,

whose true terminal is161 and mu=-154. Write the actual normalized residual as

    G(x)=sum_(q>=0) gamma_q P_q(x) A(x-q).

The inherited complete local coefficient certificate on x=10202+2^15 Z gives

    2^-178 G(10202+2^15 Z)
          =213+88 Z+81 Z^2 (mod 256).

In particular at x0=10202,

    v_2(G(x0))=178,  v_2(G'(x0))=166,  v_2(G''(x0))=149. (7)

Also v_2(gamma_0)=154 and v_2(gamma_1)=153, from the exact carry formula. Set J(x)=P_1(x)A(x-1). Since A=1 (mod2), A'=0 (mod2), P_1=x(2x-1), and P_1'=4x-1, the matrix

    M(x0)=[[A(x0), J(x0)], [A'(x0), J'(x0)]]

has determinant1 modulo2. Therefore there are unique dyadic corrections d0,d1 in2^166 Z_2 satisfying

    M(x0) [d0,d1]^t = -[G(x0),G'(x0)]^t.

The modified series

    G_tilde=G+d0 A+d1 J

has an exact double zero at x0. Indeed its value and derivative vanish, while the correction to its second derivative belongs to2^166 Z_2 and G''(x0) has valuation149. Its second derivative therefore remains nonzero. Both changed coefficients retain their exact valuations because166>154,153. All other coefficients are unchanged.

To express this at the kernel level, use the fixed original normalization constant and set

    beta_tilde_(r+q)=beta_(r+q)
           +2^mu beta_r d_q/8^q,   q=0,1,

where d_q=d0,d1, and leave every other beta_m unchanged. The relative corrections satisfy

    v_2((beta_tilde_r-beta_r)/beta_r)>=12,
    v_2((beta_tilde_(r+1)-beta_(r+1))/beta_(r+1))>=13.

Hence v_2(beta_tilde_m)=s_2(m)-1 for every m>=1. Equivalently every kappa_tilde_m has the original exact valuation4m-1. The modified residual formed with its own beta_tilde_r normalization is a nonzero constant multiple of G_tilde, so it has the same double zero.

This construction preserves:

* the entire actual finite prefix m<r;
* every individual coefficient valuation, at every depth;
* every row weight, carry comparison, intrablock ordering, and iterated radix identity above;
* the actual source A and the forced falling-factorial skeleton;
* all original kernel coefficients except the two at r and r+1.

The modified two coefficients are dyadic numbers, not asserted rational or Bernoulli. Thus the theorem shows exactly why radix alone cannot close the actual Euler theorem: its full valuation hypotheses hold for a neighboring family with a repeated residual zero. An exclusion must use an additional identity or arithmetic restriction distinguishing the prescribed Bernoulli units from this deformation.

The construction does not show that a proof using radix together with such Bernoulli-specific information is impossible. It identifies the missing input rather than declaring the entire radix route exhausted.

## 5. Sharpening: one coefficient already suffices

There is a stronger deformation using only beta_r. Keep the same actual r and chart, and put

    L(Z)=A(10202+2^15 Z),
    K_u(Z)=K(Z)+u L(Z),       u in Z_2.

The actual coefficient certificate and source integrality give, coefficientwise,

    K_Z/2=Z (mod2),     K_ZZ/2=1 (mod2),
    L=1 (mod2),         L_Z/2 in2^15 Z_2<Z>.

Here A'=0 mod2 explains the last bound. Thus the equation

    K_Z(c(u))/2+u L_Z(c(u))/2=0

has a unique solution c(u) in Z_2<u>, with c(u)=0 mod2. This can be constructed directly by contraction: write the left side as Z+2R(Z,u), and iterate Z -> -2R(Z,u) in the complete integral Tate algebra. The critical value

    Psi(u)=K(c(u))+u L(c(u))

belongs to Z_2<u> and satisfies

    Psi(u)=1+u (mod2), coefficientwise.

Consequently Psi is a dyadic isometry and has one unique zero u_star in Z_2, necessarily odd. At this parameter the zero at c(u_star) is exactly double, since K_u,ZZ/2 remains1 modulo2. This statement follows from an explicit contraction and Hensel's lemma, not from a zero residue at finite precision.

In kernel coordinates this changes exactly one coefficient:

    beta_tilde_r=(1+2^24 u_star) beta_r,
    beta_tilde_m=beta_m,       m != r.                    (8)

Indeed the corresponding fixed-normalization correction to G is2^178 u_star A. The actual normalization using beta_tilde_r multiplies this residual by the unit(1+2^24 u_star)^-1 and preserves the double root.

Thus the complete original prefix and every other kernel coefficient can remain fixed. The modified coefficient differs from its true Bernoulli value only in relative dyadic precision24 and above. All exact coefficient valuations and all radix statements in Sections1-3 still hold.

The number u_star is dyadic and is not asserted rational or an admissible Euler deformation. In particular (8) does not preserve the exact generating function (z/sinh z)^2 or the full regularized Euler moment identity. Those additional Bernoulli-specific identities remain possible sources of the missing exclusion. This is a sharper obstruction to valuation-only closure, not a counterexample to the actual theorem.

## 6. Scope and next executable implication

Positive result: the complete radix tower lifts to exact analytic block-unit transformations and explicit two-jet equations. Negative result: all of its valuation data, even at every radix level, are compatible with exact double contact in a one-coefficient deformation of the target's actual kernel.

The first unresolved implication is now precise: show that the transformed Bernoulli unit sequence and initial forcing in (5) cannot solve (6) simultaneously, or find a Bernoulli-specific finite state invariant preserved by (4) that forbids this. Merely carrying the units as unnamed analytic functions does not supply that invariant.

The companion exact checker verifies the finite polynomial quotient identity on representative first-radix discs, the historical weight relation, and the source two-jet matrix modulo a declared power of two. The universal assertions above are established by the symbolic argument; bounded checks do not establish universal Euler simplicity.

## Self-review and execution record

Checked the half-index binomial identity, both occurrences of the common -1 in the kernel valuation, the partial-block endpoint, the distinction between pointwise and coefficientwise valuations, the derivative scale2^15, and the modified-kernel renormalization. The local second-derivative valuation149 follows from the same inherited coefficient2=81 mod256. No substantive proof token was changed during this review. The first runner attempt rejected an incomplete input declaration before executing; the corrected contract and completed manifest are in certified_run/. No mathematical failure was hidden by that setup correction.
