# All-step Bernoulli Hankel nondegeneracy and the actual residual pairing

Base: Euler-radix-audit-20261005, archive SHA256
d48a4386afa295176756f795b1a0abdd696df37a10ecba7a15b7f0ec7b69a7e6.

The new theorem below concerns the prescribed depleted Bernoulli moments.
It proves that every principal Hankel matrix on every nonconstant dyadic
arithmetic progression is nonsingular. The final section gives the exact
map to the Euler residual. That map is a linear moment pairing, whereas
the Hankel theorem concerns Gram determinants and norms. No stationary
nonvanishing conclusion is asserted without the additional identification.

## 1. Statement and authenticated input

Let

    D(z)=sum_(h>=0) 2^h B_h binom(2z,h), z in Z_2.

For ordinary n>=0,

    D(n)=2^(2n)B_(2n)(1/2)
        =2(1-2^(2n-1))B_(2n),

where the second expression is also interpreted literally at n=0 and
gives1. For x,q in Z_2 with q!=0, and m>=1, define

    H_m(x,q)=det[D(x+(i+j)q)]_(0<=i,j<m).

Then

    v_2 H_m(x,q)
      =m(m-1)(2+v_2(q))+4 sum_(k=0)^(m-1) v_2(k!).       (1.1)

In particular every such determinant is nonzero. This is uniform in
the dyadic starting point and step, not only in ordinary indices.

The orthogonal-polynomial input is authenticated in
../nonintersection/BERNOULLI_HANKEL_SEPARATION.md. Its primary source is
arXiv:2105.01880v1, printed p.8, proof of Proposition3.1 following (3.11),
with the recurrence convention (2.4). After centering the Bernoulli
moment variable X=2u+1, the recurrence coefficient is

    rho_n=-n^4/(4n^2-1).

Writing U=X^2, the even contracted monic polynomials P_n(U) satisfy

    U P_n=P_(n+1)+b_n P_n+a_n P_(n-1),
    b_n=rho_(2n)+rho_(2n+1),
    a_n=rho_(2n)rho_(2n-1).

Here rho_0=0. The functional L(U^j)=D(j) makes these polynomials
orthogonal, with squared norms

    L(P_n^2)=((2n)!)^4 / product_(j=1)^(2n)(4j^2-1).

The required transformed recurrence and functional equality are proved
in the authenticated companion note. The argument below starts from
that exact actual-moment recurrence; no positivity assumption is used.

## 2. Two factorial lattices

Set c_n=4^n(n!)^2 and e_n=P_n/c_n. Then

    L(e_n e_k)=0 for n!=k,
    h_n=L(e_n^2) is a dyadic unit.

Multiplication by U in the e basis has matrix J, with

    coefficient of e_(n+1) in J e_n =4(n+1)^2,
    coefficient of e_n in J e_n=b_n,
    coefficient of e_(n-1) in J e_n=a_n/(4n^2).

All entries are integral, and J=I+4K with K integral. Indeed
b_n=1 mod4, and a_n/(4n^2) is divisible by4. The diagonal functional
with entries h_n extends continuously to the space c_0(e) of sequences
converging to0. Orthogonality, self-adjointness of J, and all displayed
matrix identities extend by continuity.

A second lattice is decisive. Set f_n=(n!)^2 e_n. In this basis K has
upward coefficient1. Its downward coefficient is a_n/16, which is
integral, and its diagonal remains integral. Thus K is bounded on
c_0(f) as well. The natural map c_0(f) -> c_0(e) is bounded and sends
f_n to (n!)^2 e_n.

## 3. Dyadic powers and the normalized step operator

Since J=I+4K, J^z=sum_l binom(z,l)4^l K^l converges in operator norm
for every z in Z_2, on either lattice. It has J^z=I mod4. For q!=0 put

    V_q=(J^q-I)/(4q)
       =K+sum_(l>=2) [4^(l-1)/l] binom(q-1,l-1) K^l.    (3.1)

For l>=2 the coefficient after K is even, since
2l-2-v_2(l)>=1. Its valuations tend to infinity. Hence V_q is bounded
on c_0(f) and

    V_q=K mod2.                                         (3.2)

This conclusion holds for every nonzero dyadic q, including nonunits.
Dividing by q has already been accounted for in (3.1).

The moment identity

    D(z)=<e_0,J^z e_0>

holds first at ordinary nonnegative integers and then on all Z_2 by
continuity. Consequently H_m(x,q) is the J^x-weighted Gram determinant
of e_0,J^q e_0,...,J^((m-1)q)e_0.

## 4. The unique odd coordinate in the exterior power

For i=0,...,m-1 set v_i=V_q^i f_0. By (3.2),

    v_i=K^i f_0 mod2.

The vector K^i f_0 is supported on indices0,...,i, and its coefficient
at index i is1 because every upward step has coefficient1. Therefore
the wedge w=v_0 wedge ... wedge v_(m-1), in the completed c_0 exterior
space on f, has the following coordinates c_I:

    c_(0,...,m-1)=1 mod2,
    c_I=0 mod2 for every other increasing m-tuple I.     (4.1)

Let d_I=product_(i in I)(i!)^2 and I_0=(0,...,m-1). If I=(i_0<...<i_(m-1)),
then i_j>=j, so d_I/d_I0 is integral. In the e exterior basis,

    w/d_I0=sum_I c_I(d_I/d_I0) e_I
           =e_I0 mod2.                                (4.2)

This is a convergent vector: it is the image of the c_0 exterior vector
under a bounded diagonal map. Thus no unjustified infinite determinant
sum is being used. Alternatively, (4.2) can be proved after every finite
truncation and passed to the limit in the c_0 norm.

The induced weighted Gram operator is exterior^m(J^x), multiplied by
the diagonal exterior norms product_(i in I)h_i. It is integral and is
the unit diagonal operator modulo2 because J^x=I mod4. Equations
(4.1)-(4.2) therefore give

    <w,w>_x/d_I0^2 = product_(i=0)^(m-1) h_i mod2,

which is a unit. Hence the Gram determinant of v_0,...,v_(m-1) has
valuation

    2v_2(d_I0)=4 sum_(i=0)^(m-1)v_2(i!).                (4.3)

Finally J^(iq)=(I+4q V_q)^i. The change from the vectors V_q^i e_0 to
J^(iq)e_0 is triangular with diagonal entries (4q)^i. Its determinant
squares in a Gram determinant. Combining this factor with (4.3) proves
(1.1).

## 5. Exact source-to-residual bridge

Keep the actual coefficients beta_n and the source A from the base.
Define

    gamma_n=8^n beta_n/D(n),
    L_r(U^q)=D(r+q),
    W_r(y,U)=sum_(q>=0) gamma_(r+q) P_q(y) A(y-q) U^q.

Here P_q(y)=product_(i<q)(y-i)(2y-2i-1), the source-packet polynomial,
not the orthogonal polynomial from sections1-2. The two uses are
distinguished in this section by the explicit formula. The base
coefficient valuations give gamma_n in2^(3n) Z_2 for n>=1. Thus the
series and its y derivative converge in the restricted two-variable
algebra, and L_r acts continuously coefficientwise because D(r+q) is
a unit for every q.

The product law for the source packets gives the exact identity

    [Ecal(r+y)-S_r(r+y)]/P_r(r+y)=L_r[W_r(y,U)].          (5.1)

The quotient is the already analytically continued residual at the
forced skeleton. Away from that skeleton, a repeated residual zero is
exactly

    L_r[W_r(y,U)]=0,
    L_r[partial_y W_r(y,U)]=0.                          (5.2)

The normalization converting this quotient to the chosen G_r is a
nonzero scalar, so it does not change this simultaneous-zero criterion.

Equation (5.1) incorporates the actual coefficient data: D(r+q) restores
the precise beta_(r+q), not an arbitrary moment sequence. The theorem
(1.1) applies to its moment functional. It does not, by itself, make
either linear pairing in (5.2) a norm or a Schur complement.

For an ordinary y>=0 the kernel W_r(y,U) terminates at q=y and has
degree exactly y. Its highest coefficient is nonzero. Consequently,
when y is odd, this kernel is not a nonzero scalar times the square
of a polynomial in U. The simplest exact actual instance is

    W_1(1,U)=40/3+(64/7)U,
    L_1[W_1(1,U)]=-8/45.

The degree test rules out this literal square-kernel bridge. It does
not exclude a different weight, an analytic square, or another operator
identity, each of which would require its own source-to-target proof.

## 6. What the genuine Schur complement controls

For a linear polynomial w(U)=a+bU the exact Schur complement is

    L_r(w^2)-L_r(w)^2/D(r)
      =b^2 [D(r)D(r+2)-D(r+1)^2]/D(r).                 (6.1)

The Hankel theorem makes (6.1) nonzero whenever b!=0. But if L_r(w)=0,
the same identity says that the norm L_r(w^2) is nonzero. It does not
contradict the zero linear pairing. In particular the canonical
orthogonal vector U-D(r+1)/D(r) has zero mean and nonzero norm.

Likewise two linearly independent vectors in the orthogonal complement
of1 may have both linear pairings in (5.2) equal to0 while their Gram
matrix is nondegenerate. Nondegeneracy and even an anisotropic norm do
not prohibit orthogonality to1.

For the actual instance above, D(1)D(3)-D(2)^2=48/175, while the
Schur complement is -589824/8575. These exact values concern (6.1),
not the Euler stationary scalar. The missing implication is an identity
that converts the actual simultaneous contact into vanishing of a
specific nonzero Gram norm or principal Schur complement. No such
identity is established here.

## 7. The literal square bridge fails uniformly on the actual target chart

There is a sharper obstruction than the odd-degree example in section5.
Assume the actual admitted terminal161 chart from the base:

    r=(17659+2^18 T)2^640-161, T an ordinary nonnegative integer,
    mu_r=-154,
    x=10202+2^15 Z, Z in Z_2.

Let gamma_(r,q) be the actual normalized coefficients in
G_r(x)=sum_q gamma_(r,q)P_q(x)A(x-q), and put

    Psi_(r,x)(U)=sum_q gamma_(r,q)P_q(x)A(x-q)/D(r+q) U^q,
    Xi_(r,x)(U)=D(r)2^(-154) Psi_(r,x)(U).

Thus L_r(Psi)=G_r(x). Every congruence in this section is coefficientwise
in U or V for each fixed x on the chart, uniformly over Z. No stronger
joint Gauss congruence in Z is needed or asserted.

Write Xi=sum a_q U^q. The exact coefficients at q=0,1 are

    a_0=A(x),
    a_1=16 P_1(x)A(x-1)/[(2r-1)(r+1)]
             * (1-epsilon)/(1-4epsilon),
    epsilon=2^(2r-1).

Every coefficient with q>=2 is divisible by16. Here is the uniform
tail justification. For 1<=q<=160 the actual normalized gamma satisfies

    v_2 gamma_(r,q)=5q-164+v_2((321-2q)!).

This follows by evaluating the factorial ratio on r=-161 mod2^640;
none of its factors vanishes or reaches that congruence precision.
Also P_q(x) belongs to q! Z_2 pointwise for x in Z_2. Consequently the
valuation of a_q is at least

    4q+3-s_2(321-2q)-s_2(q).

At q=2,3,4 these bounds are respectively4,7,13. For q>=5 the elementary
bounds s_2(321-2q)<=8 and s_2(q)<=q-1 give at least3q-4>=11.
For q>=161 the true-terminal assumption makes every gamma_(r,q)
integral, while v_2(P_q(x))>=v_2(q!)>=v_2(161!)=158.
After the normalization2^(-154), this again leaves at least4.
The latter bound also tends to infinity, proving convergence in U.

The low coefficients have the more precise values

    a_0=5 mod16,        a_1=15 mod16.                    (7.1)

To check them, the chart may be reduced to r=-161 and x=10202 at this
precision. A is integral restricted analytic, and the denominators in
a_1 lose only the fixed valuation5 of r+1. The undepletion factor is1
at much higher precision. The identity P_1(x)A(x-1)=(9^x-1)/8 gives

    a_1=(9^10202-1)/25840 mod16,

whose denominator has valuation4 and odd part1615. Exact modular powers
give (7.1). The dependence on x changes only beyond the displayed precision.

It follows that

    Xi(U)=1+U mod2,
    Xi(1+8V)/4=1+2V mod4.                              (7.2)

The first congruence rules out Xi being a nonzero scalar times a square
in Q_2<U>. The second proves the stronger statement on the natural
odd-square domain U=1+8V: Xi(1+8V) is not a nonzero scalar times the
square of a Q_2-valued analytic function on that disc. In fact its values
at V=0 and V=1 have ratio3 modulo4. A ratio of two nonzero Q_2 squares
is a square, and a dyadic unit square is1 modulo8. This is a contradiction.
The same argument even excludes a scalar-square assignment at just
these two actual odd-square arguments U=1 and U=9.

This result only closes the literal constant-times-square kernel route.
It does not rule out a different weight, a sum of several squares, an
additional operator, or an identity derived after imposing stationarity.
The companion ../root/BERNOULLI_QUADRATIC_FORM.md proves that norm
nonvanishing holds through polynomial degree3 and fails already in
degree4. Therefore an unrestricted higher-degree norm representation
would not by itself establish the Euler claim either. A successful
bridge must specify the exact controlled form that its arithmetic
nondegeneracy theorem actually covers.

## 8. Evidence and limitations

The accompanying checker uses exact rational Bernoulli arithmetic and
independent determinant elimination. It checks the proposed valuation
formula for m=1,...,6, x=0,...,9, q=1,...,5, and checks the actual row
bridge for small ordinary cutoffs and arguments. It additionally checks
the explicit finite tail inequalities and the low coefficient residues
at nine prescribed ordinary target-chart representatives. The dyadic-universal
quantifiers in (1.1) follow from the completed-lattice proof, not from
this bounded computation. No Lean compilation is used.

The current source run is certified_run_final. The earlier certified_run
is retained as a superseded development record from before section7 and
its checks were added; it is not current-source evidence.
