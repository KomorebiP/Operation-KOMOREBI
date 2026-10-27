# Nonhomogeneous polynomial corrections cannot escape content conservation

Claim PC-ALL, 26 September 2026. This is a new extension within the present
project, not a claim of historical novelty. It depends on the harmonic theta
modularity lemma established in the parent checkpoint and recalled below.
The proof is analytic/algebraic; no finite experiment is used to establish it.

## Theorem

Let Q be any finite symmetric polynomial over C in v_0,...,v_4, restricted to
the hyperplane sum_i v_i=0. Suppose that

    sum_{v in V_n} W(v) Q(v) = 0

for every positive integer n. Write Q=sum_d Q_d for its homogeneous
decomposition. Then every Q_d is separately universally null. Moreover,
every exact-content sector has zero weighted Q-sum, at every shell.

Thus allowing finite nonhomogeneous symmetric polynomial corrections adds
no escape from the parent content-conservation theorem. This statement does
not concern arbitrary nonpolynomial functions or nonsymmetric polynomials.

## 1. Harmonic decomposition and its theta weights

Let D=prod_{i<j}(v_i-v_j), and work in the four-dimensional Euclidean
hyperplane H: sum_i v_i=0. For a homogeneous symmetric Q_d of degree d,
P=D Q_d is alternating and homogeneous of degree M=10+d.

The usual homogeneous harmonic decomposition is

    P = sum_{j>=0} s2^j h_{M-2j},

with each h_l homogeneous harmonic of degree l. This decomposition can be
constructed recursively by the Laplacian; the relevant identity in
dimension four is

    Laplacian(s2^j h_l) = 4*j*(l+j+1)*s2^(j-1) h_l.

Its uniqueness and the commutation of the Laplacian with coordinate
permutations show that each h_l is alternating. An alternating polynomial
on H vanishes on every hyperplane v_i=v_j. The ten corresponding distinct
linear factors divide it, so D divides h_l. Therefore a nonzero h_l has
l>=10. In particular, j<=d/2. For even d all these harmonic degrees are even.

For such an even alternating harmonic polynomial, the parent theta lemma
says

    theta_h(tau) = sum_{v_i congruent i (mod 5), sum v_i=0}
                    h(v) exp(2*pi*i*tau*||v||^2/10)

is a scalar full-level cusp form of weight l+2. Scaling h by the constant
1/288, if desired, does not affect this conclusion.

Here is the lattice/coset normalization behind that lemma. Take L=sqrt(5) A4,
so L^*/L has order 5^5. Write a representative as

    x=(a_i+t/5)_i / sqrt(5),  0<=t<=4,  sum_i a_i=-t.

If two a_i agree modulo 5, their transposition fixes the discriminant coset,
and its alternating theta component is zero. If all five residues are
distinct, summing them shows t=0. The remaining 120 regular cosets form one
free S5-orbit. Thus the sign-isotypic subspace of the discriminant module is
one-dimensional. Its T-action is 1: sum a_i^2 is divisible by 5, and is even
because sum a_i=0. The Weil representation commutes with S5. On this line
the relation (ST)^3=S^2 therefore forces S=1. The rank is even, so the Weil
representation descends to SL2(Z); on the sign line its central action is
also 1. The standard harmonic theta transformation then gives scalar weight
l+2. The zero vector has h(0)=0, and full level has one cusp, so it is cuspidal.
The standard residue coset consists of v/sqrt(5) for v in the displayed sum,
with quadratic exponent ||v||^2/10. This recovers the stated normalization.

Put mathcal D=(1/(2*pi*i))*d/dtau=q*d/dq. The radial factors give the exact
identity

    theta_{s2^j h} = 10^j * mathcal D^j theta_h.

Differentiating the modular transformation law shows that mathcal D^j f,
when f has modular weight w, is quasimodular of weight w+2j and depth at most
j. Consequently

    F_d(tau) := sum_n [sum_{v in V_n} W(v)Q_d(v)] q^n

is quasimodular of weight (M-2j+2)+2j=12+d, independently of j, and depth at
most d/2. All its transformation powers below are thus nonnegative. Absolute
convergence on the upper half-plane follows from Gaussian decay against
polynomially weighted lattice sums and allows these differentiations.

For odd d, Q_d(Jv)=-Q_d(v), while W(Jv)=W(v). Every J-fixed packet has Q_d(v)=0.
It follows directly that F_d=0, and indeed that every exact-content Q_d-sum
is zero. No quasimodularity claim for an odd-degree nonzero theta is needed.

## 2. Different quasimodular weights cannot cancel here

The needed weight-separation fact has an elementary proof which avoids any
appeal to algebraic independence of E2,E4,E6.

Suppose finitely many full-level quasimodular functions F_k have distinct
nonnegative integer weights k, with transformation law

    F_k(gamma z) = sum_{r=0}^{p_k}
                      f_{k,r}(z) c^r (cz+d)^(k-r),
    f_{k,0}(z)=F_k(z),  p_k<=k,

for gamma=[[a,b],[c,d]] in SL2(Z). Constants in the usual quasimodular
normalization can be absorbed in f_{k,r}. Assume sum_k F_k=0 identically.
Fix z in the upper half-plane. The polynomial

    P_z(c,d)=sum_k sum_r f_{k,r}(z)c^r(cz+d)^(k-r)

vanishes for every relatively prime integer pair (c,d), since each such pair
is the bottom row of an SL2(Z) matrix. These pairs are Zariski dense: for each
positive prime c there are infinitely many d coprime to c, so the polynomial
in d vanishes identically; its coefficient polynomials in c then vanish at
infinitely many c. Thus P_z is identically zero.

The terms for each k have total polynomial degree k. Homogeneous components
of a zero polynomial vanish separately. Evaluating the degree-k component
at (c,d)=(0,1) gives F_k(z)=0. Since z was arbitrary, every F_k is identically
zero.

Apply this with k=12+d to the finitely many even components above. Universal
nullness of Q gives sum_d F_d=0; odd components were already zero. Therefore
F_d=0 separately for every even d as well. Equality of Fourier coefficients
is exactly universal nullness of each Q_d.

## 3. Content conservation now follows without a homogeneity restriction

For each homogeneous component Q_d define the primitive sum

    R_d(n)=sum_{v in V_n, gcd(v_0,...,v_4)=1} W(v)Q_d(v).

The parent scaling bijection gives

    Theta_{Q_d}(n)=sum_{g^2|n} chi_5(g)*g^(10+d)*R_d(n/g^2),

where terms with 5 dividing g vanish. Since Theta_{Q_d}=0, induction on n
gives R_d(n)=0 for every n: the g=1 term is R_d(n), and every other nonzero
term has a smaller argument. The exact-content-g sum is therefore
chi_5(g)*g^(10+d)*R_d(n/g^2)=0. Summing over the finitely many d proves the
claim for Q.

## Consequence and limit

At n=121, the parent exact computation gives opposite conserved masses

    content 1:  -25439104668,
    content 11:  25937424601.

No finite symmetric polynomial correction which is null on every shell can
turn all the packet weights at n=121 into one common sign. This is now true
without assuming homogeneous corrections or a prescribed finite span.

This obstruction is composite-specific: a prime shell has only content 1.
It does not prove, disprove, or further reduce the remaining assertion
tau(p)!=0. It closes a possible nonhomogeneous escape from the content
invariant, while leaving the prime arithmetic gap explicit.
