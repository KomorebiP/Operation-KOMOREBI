# Actual Bernoulli quadratic forms: sharp degree-three anisotropy

Base: Euler-radix-audit-20261005, archive SHA256
d48a4386afa295176756f795b1a0abdd696df37a10ecba7a15b7f0ec7b69a7e6.
This is an auxiliary actual-coefficient theorem. It does not identify the
stationary Euler scalar with a quadratic form.

Let D(z)=sum_h 2^h B_h binom(2z,h). For x in Z_2 define the linear
functional L_x(U^n)=D(x+n) on Q_2[U]. At ordinary nonnegative integers n,
D(n)=(2-4^n)B_(2n), with D(0)=1. The accompanying Hankel proof constructs
its normalized orthogonal lattice from the authenticated centered Bernoulli
recurrence. We use that construction explicitly below.

## 1. A uniform congruence stronger than determinant nonvanishing

Write P_n for the monic orthogonal polynomials for L_0 and put

    c_n=4^n(n!)^2, e_n=P_n/c_n, u_n=L_0(e_n^2).

The even contraction of the centered Bernoulli recurrence gives

    U P_n=P_(n+1)+b_n P_n+a_n P_(n-1),
    a_n=(2n)^4(2n-1)^4/[(4n-3)(4n-1)^2(4n+1)],
    b_n=-(2n)^4/(16n^2-1)-(2n+1)^4/[4(2n+1)^2-1].

The n=0 lower term is omitted. Thus u_0=1 and

    u_n/u_(n-1)=a_n/(16n^4)=5 (mod8),
    u_n=5^n (mod8).

Also b_n=5 mod8 for every n. Multiplication by U in the e basis has
upper coefficient c_(n+1)/c_n=4(n+1)^2 and lower coefficient
a_n c_(n-1)/c_n in4 Z_2. Its bounded matrix J therefore satisfies
J=I+4K, with K integral and every diagonal entry1 modulo2.

On the c_0 completion in this basis the series

    J^x=sum_(h>=0) binom(x,h)4^h K^h

converges in operator norm for x in Z_2. Terms h>=2 are zero modulo8.
Hence the Gram matrix M_x(i,j)=L_x(e_i e_j) satisfies

    M_x(i,i)=(1+4x)5^i (mod8),
    M_x(i,j)=0 (mod4) for i!=j.                       (1)

For ordinary x>=0 this follows from multiplication by U^x and
orthogonality. The analytic extension in x agrees with L_x on every
polynomial by equality at dense ordinary indices. Formula (1) is uniform
over all dyadic shifts. It does not invoke positivity over the reals.

## 2. Anisotropy through degree three

For every nonzero p in Q_2[U] of degree at most3,

    L_x(p^2) != 0,        for every x in Z_2.          (2)

To prove this, multiply p by a nonzero dyadic scalar so that
p=sum_(i=0)^3 v_i e_i has integral coordinates, at least one odd.
Equation (1) makes every cross term zero modulo8. Modulo4 its norm is
sum_i v_i^2, because both 1+4x and 5^i are1 modulo4. If one, two, or
three coordinates are odd, that sum is nonzero modulo4. If all four
are odd, every square is1 modulo8 and the norm is

    (1+4x)(1+5+1+5)=4 (mod8).

Thus the norm cannot vanish. In particular after primitive normalization
its valuation is at most2.

## 3. The degree threshold is sharp

For each x in Z_2 there is a nonzero polynomial p of degree4 with
L_x(p^2)=0. This is compatible with every finite Hankel determinant
being nonzero: an invertible bilinear form may be isotropic.

Use the first five basis vectors and let w=e_0+e_2+e_3+2e_4. Put

    A=L_x(e_1^2), b=L_x(e_1 w), C=L_x(w^2).

By (1), A=5(1+4x) mod8, b belongs to4 Z_2, and
C=3(1+4x) mod8. Consequently

    d=(b/A)^2-C/A=1 (mod8).

Every dyadic unit congruent1 modulo8 has a square root in Z_2. Choose
such a root t and set y=-b/A+t. Then

    L_x((y e_1+w)^2)=A y^2+2by+C=0.

Its e_4 coefficient is2, so the polynomial has degree4 and is nonzero.
The square-root assertion can be proved by elementary bit lifting of an
odd square; it does not rely on finite numerical evidence.

## 4. Transfer to prescribed, undepleted Bernoulli coefficients

For an ordinary r>=1 define L_actual,r(U^n)=2B_(2(r+n)). Since

    2B_(2(r+n))=D(r+n)/(1-2^(2(r+n)-1)),

each moment differs from its depleted counterpart by valuation at least
2r-1. The polynomials P_n are dyadically integral, by their recurrence.
Thus in the normalized basis with 0<=i,j<m the Gram difference has
valuation at least

    2r-1-4(m-1)-4v_2((m-1)!).                         (3)

For degree at most3, m=4 and the loss in (3) is16. If r>=10, the
difference is divisible by8, so (1)-(2) hold unchanged for L_actual,r.
For degree4, m=5 and the loss is28. If r>=16, the difference is again
divisible by8, so the explicit isotropic construction in section3 also
holds for L_actual,r.

Therefore the prescribed ordinary Bernoulli moment form is anisotropic
on degree<=3 for every r>=10, and already isotropic on degree<=4 for
every r>=16. Both statements concern the actual coefficients.

## 5. Exact relation to the Euler goal

No identity currently expresses Phi_r, or the pair (G_r,G_r'), as the
norm of a nonzero polynomial of degree<=3 for these forms. The Newton
weights in the actual residual depend on the argument and its logarithmic
derivatives. Hankel invertibility by itself does not give that identity.

The new theorem states exactly what a low-degree norm representation
would buy. The degree4 construction also prevents replacing the missing
representation with an unrestricted assertion that all nonzero polynomial
norms are nonzero. No conclusion about an actual Euler double zero follows.

## Source and evidence

The external input is the classical Bernoulli orthogonal recurrence,
recorded in Dilcher-Jiu, arXiv:2105.01880v1 (5 May2021), Eq.(2.4) and
the proof of Proposition3.1, printedp8. The actual source and its
normalization are authenticated in the companion source record and
Hankel audit. The new mod8 argument is self-contained from that recurrence.

The checker independently builds the rational polynomials and actual
moments, verifies Gram congruences and all primitive residue patterns,
and checks a finite square-root lift. The universal claims rest on the
proof above, not on the tested shifts or residues.
