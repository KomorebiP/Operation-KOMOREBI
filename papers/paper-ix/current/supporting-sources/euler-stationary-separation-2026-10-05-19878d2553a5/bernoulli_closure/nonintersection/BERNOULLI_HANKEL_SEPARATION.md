# Actual Bernoulli separation below the undepletion scale

Date: 2026-10-05. Base checkpoint: Euler-radix-audit-20261005, archive SHA256 `d48a4386afa295176756f795b1a0abdd696df37a10ecba7a15b7f0ec7b69a7e6`.

## Target and outcome

The requested nonintersection target is `Phi_r(2^(2r−25)) != 0` for every admitted ordinary `r=(17659+2^18 T)2^640−161`. This document does **not** prove that target. It supplies a new exact quantitative theorem for the prescribed Bernoulli coefficients: a whole family of shifted moment determinants cannot vanish, including actual undepleted Bernoulli determinants of size approximately r/4. No artificial coefficient deformation is used in those theorems.

The proposed bridge was that the local stationary obstruction might be a Schur complement of these moment matrices. No such identity has yet been proved for the actual Newton/source weights. That precise bridge remains open; an unweighted Hankel determinant must not be substituted for the stationary scalar.

## 1. The actual depleted function is an exact scaled isometry

Use the Bernoulli convention B_1=−1/2 and define

    D(z)=sum_(h>=0) 2^h B_h binom(2z,h).

The inherited Gauss bound for the h=2n term is

    v_G(2^(2n) B_(2n) binom(2z,2n)) >= n+s₂(n)−1.

It tends to infinity, so D is restricted integral analytic. For n>=3 the bound is at least4. The terms h=0,1,2,4 sum exactly to

    1−12z/5+16z²/45+16z³/15−16z⁴/45.

Consequently

    D(z)=1+4z+16R(z),  R in Z₂<z>, R(0)=0.        (1.1)

For x,y in Z₂, integral restricted power series satisfy R(x)−R(y) in (x−y)Z₂. Hence

    v₂(D(x)−D(y))=2+v₂(x−y)                    (x!=y),
    v₂(D(x+q)/D(x)−1)=2+v₂(q)                  (q!=0). (1.2)

These are statements about the prescribed Bernoulli function, not arbitrary units.

There is also an exact two-by-two determinant law. Since the second forward difference of any integral power series satisfies

    R(x+2q)−2R(x+q)+R(x) in 2q²Z₂,

we have Δ_q²D(x) in32q²Z₂. The algebraic identity

    D(x+q)²−D(x)D(x+2q)
       =(D(x+q)−D(x))²−D(x)Δ_q²D(x)

has a first term of valuation4+2v₂(q) and a second of valuation at least5+2v₂(q). Therefore

    v₂(D(x+q)²−D(x)D(x+2q))=4+2v₂(q).          (1.3)

To justify the stated second-difference divisibility directly, it suffices to use monomials: for k>=2, the coefficient of q^k in the second difference is binom(n,k)(2^k−2), an even integer. Convergence passes this polynomial assertion to R.

## 2. Exact moment recurrence and its source

Let L be the rational moment functional on Q[U] defined by

    L(U^n)=D(n)=(2−4^n)B_(2n)=4^n B_(2n)(1/2),  n>=0.

The exponential generating function of these even moments is t/sinh(t).

The classical monic orthogonal recurrence for the Bernoulli functional with moments B_n has diagonal −1/2 and subdiagonal coefficient

    −n^4/[4(2n+1)(2n−1)].

This exact recurrence is authenticated in Karl Dilcher and Lin Jiu, *Hankel Determinants of shifted sequences of Bernoulli and Euler numbers*, arXiv:2105.01880v1 (5 May 2021), printed page 8, proof of Proposition 3.1, immediately following equation (3.11), using their recurrence (2.4). Their convention is `P_(n+1)=(y+s_n)P_n−t_n P_(n−1)` with `s_n=1/2` and the displayed negative t_n. The source attributes the recurrence to Touchard.

Primary PDF inspected: https://arxiv.org/pdf/2105.01880v1 . Checked 2026-10-05. The inspection verifies the recurrence and convention, not a theorem about our stationary scalar. An independent cross-check is the row `B_(2k)(1/2)` of Table 7.1 in arXiv:2007.09821v1, printed page 19; after multiplication of moments by 4^k it gives the same subdiagonal products below. The present shifted dyadic lattice proof is not asserted to be in those sources. These PDFs were inspected through the retrieval service; no local PDF hash is claimed.

Translate the underlying variable by X=2y+1. Its moments are `2^n B_n(1/2)`, its odd moments vanish, its diagonal is zero, and its recurrence coefficient is

    rho_n=−n^4/(4n²−1),  rho_0=0.

If Q_n(X) are its monic orthogonal polynomials, the zero diagonal implies that Q_(2n)(X)=P_n(X²). Applying the recurrence twice gives

    U P_n(U)=P_(n+1)(U)+b_n P_n(U)+a_n P_(n−1)(U),

    b_n=rho_(2n)+rho_(2n+1),
    a_n=rho_(2n) rho_(2n−1)
       =(2n)^4(2n−1)^4/[(4n−3)(4n−1)²(4n+1)]. (2.1)

The initial polynomials are P_0=1, P_1=U+1/3. The norms are

    h_n=L(P_n²)=product_(k=1)^n a_k.

All coefficients P_n are dyadically integral because b_n and a_n are integral. Directly from (2.1),

    b_n=1 (mod4),
    v₂(a_n)=4+4v₂(n),
    v₂(h_n)=4n+4v₂(n!).                         (2.2)

## 3. A unimodular orthogonal lattice

Set

    c_n=4^n(n!)²,
    e_n=P_n/c_n,
    d_n=L(e_n²)=h_n/c_n² in Z₂×.

The e_n are orthogonal with unit norms d_n. Let J be multiplication by U in this basis, with the column convention that J e_n is the expansion of U e_n. Then

    J e_n=4(n+1)² e_(n+1)+b_n e_n
                 +a_n/(4n²) e_(n−1).           (3.1)

The last term is omitted at n=0. Its coefficient is divisible by4, as is the upward coefficient. Thus J is an integral, uniformly bounded tridiagonal operator satisfying

    J=I (mod4).                                 (3.2)

Work in the c₀ completion of the span of the e_n, with the coefficient supremum norm. J is bounded there. The bilinear form with diagonal d_n is continuous: each sum of products of two c₀ coefficient sequences converges and has integral norm bound. For x in Z₂, the operator series

    J^x=sum_(k>=0) binom(x,k)(J−I)^k

converges in operator norm and J^x=I (mod4).

For ordinary x>=0, the weighted Gram matrix has entries

    L(U^x e_i e_j)=d_i (J^x)_(i,j).

Every finite principal weighted Gram matrix is therefore a diagonal unit matrix modulo4 and has unit determinant. By continuity in x, this remains true for every dyadic x, where weighted moments mean D(x+n). Equality for all dyadic x is justified by equality on dense nonnegative integers and continuity of both sides; no unproved Haar change of variables is used.

Changing from e_0,...,e_(m−1) to the monomials multiplies the Gram determinant by `product c_n²`, since each e_n has leading coefficient1/c_n. We obtain the uniform theorem

    v₂ det[D(x+i+j)]_(0<=i,j<m)
       =V_m:=2m(m−1)+4 sum_(k=0)^(m−1) v₂(k!),  x in Z₂. (3.3)

In particular every such determinant is nonzero. This holds for every size and every shift. The general step-q extension is owned by the separate Hankel bridge route and is not needed for the proof here.

## 4. Quantitative transfer to the actual Bernoulli coefficients

For ordinary r>=1, define the actual and depleted shifted functionals

    L_r^act(U^n)=2B_(2(r+n)),
    L_r^dep(U^n)=D(r+n).

The exact midpoint identity gives

    2B_(2(r+n))=D(r+n)/(1−2^(2(r+n)−1)).          (4.1)

For each n>=0, the difference in (4.1) has valuation exactly `2r+2n−1`. Therefore, for every dyadically integral polynomial P,

    v₂((L_r^act−L_r^dep)(P))>=2r−1.             (4.2)

Apply (4.2) to P_iP_j and divide by c_i c_j. In the normalized orthogonal basis, the Gram perturbation has entry valuation at least

    2r−1−v₂(c_i)−v₂(c_j).

For i,j<m this is strictly positive whenever

    2r−1>4(m−1)+4v₂((m−1)!).                    (4.3)

Under (4.3), the actual Gram matrix equals the depleted Gram matrix modulo2. Section3 proves the latter has unit determinant. Returning to the monomials proves

    v₂ det[2B_(2(r+i+j))]_(0<=i,j<m)=V_m         (4.4)

for every ordinary r satisfying (4.3). These are the actual prescribed rational Bernoulli coefficients. No coefficient has been replaced by a freely chosen unit.

Using `v₂(n!)=n−s₂(n)`, criterion(4.3) is

    2r−1>8(m−1)−4s₂(m−1).

For example it holds for every `m<=floor(r/4)+1`. The admissible terminal-161 indices are enormously inside this regime for any fixed matrix size such as161.

One can retain the whole nonunit correction instead of only its valuation. For every polynomial P,

    L_r^act(P(U))
       =sum_(h>=0)2^(h(2r−1)) L(U^r P(4^h U)). (4.5)

Equation(4.5) follows term by term from the convergent geometric series in (4.1). It is exact and displays why the leading depleted Gram form controls matrix sizes allowed by (4.3).

The restriction matters. At r=1 and m=2, the actual determinant has valuation1, while V_2=4. At r=2,m=2 it has valuation3. Criterion(4.3) first permits m=2 at r=3, and the exact law then gives valuation4 uniformly. Thus actual undepletion cannot be discarded at small indices.

## 5. What this resolves and what the stationary proof still needs

The originally proposed weak argument was that finite support of the ordinary index and Kummer congruences must force a departure before precision `2r−25`. No such conclusion follows just from knowing the bitlength of r. The new proved statement is more precise: the prescribed Bernoulli moment form has no singular principal block throughout the explicit size range (4.3).

A successful bridge to Phi would have to identify the critical scalar, or an exact determinant containing it as a factor, with a Gram/Schur expression whose basis lies in the integral orthogonal lattice and whose size/loss is bounded as in (4.3). The actual packet weights include rising factorial denominators, the source A(x−q), and the argument-dependent falling products P_q(x). Their derivative weights are harmonic sums rather than simple powers of the moment variable. Neither the moment Hankel law nor the finite packet index cutoff identifies that weighted matrix automatically.

Consequently the present output is a genuine actual-coefficient separation theorem, with an explicit ordinary-index bound. It is not a proof of stationary nonintersection, a proof of universal Euler simplicity, or a justification for replacing the actual weighted critical scalar by an unweighted Hankel minor.
