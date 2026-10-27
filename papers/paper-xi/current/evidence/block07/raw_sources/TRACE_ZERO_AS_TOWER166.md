# A trace-zero Artin--Schreier version of the explicit parameter tower

Date: 2026-10-05. Ordinary proof, submitted for independent audit.

## Exact statement

Let p be odd, F=F_p((t)), and 0<h_1<...<h_d with p not dividing any h_i.
Put q_i=(p+1)h_i. The constructor below gives an actual matrix B_d over F
of size p^d with exactly the field, simplicity, approximation-level,
odd-prime quotient, and conductor conclusions of RECURSIVE_TOWER166.md.
In addition, its matrix trace is exactly zero. Every native shorter
constructor and every amplified arithmetic approximation also has
matrix trace zero. Therefore every difference between consecutive
arithmetic approximations has matrix trace zero.

The trace statement is an identity over the current coefficient field,
not merely a congruence, a field trace inferred from characteristic zero,
or a division by the matrix size. All coefficient fields have
characteristic p, so division by p^j would be invalid.

## 1. An explicit separable minimal extension with a traceless parameter

At an arbitrary recursive step let L have residue field F_p and
uniformizer t_L. Given q>0 prime to p, set

    E=L(alpha),  alpha^p-alpha=t_L^(-q).

The right side is not an Artin--Schreier coboundary in L: the negative
valuation of x^p-x, if x has negative valuation, is divisible by p.
Thus the polynomial is irreducible of degree p. The extension is
separable, and the valuation equation forces ramification index p and

    v_E(alpha)=-q.

It is therefore totally ramified and alpha is minimal over L. For odd p
its field trace is

    Tr_(E/L)(alpha)=sum_(c in F_p)(alpha+c)=0.

Choose the unique b in {1,...,p-1} with qb congruent to -1 modulo p, put
a=(qb+1)/p, and define

    z=t_L^a alpha^b.

Then v_E(z)=pa-qb=1, so z is a uniformizer and E=L(z). Its monic minimal
polynomial f(X)=X^p+a_(p-1)X^(p-1)+...+a_0 is Eisenstein. It is an explicit
polynomial: compute the product over the p conjugates

    f(X)=product_(c in F_p) (X-t_L^a(alpha+c)^b)

and reduce coefficients using alpha^p-alpha=t_L^(-q). The invariant
coefficients belong to L. This is a finite algebraic instruction, with
no choice of an unknown extension or matrix.

## 2. Normalized corestriction and an explicit filtered right inverse

Use the basis 1,z,...,z^(p-1) of E over L. If T_ij is its coefficient
matrix unit and pr is the trace corestriction, then

    pr(T_ij)=z^i z_j^*,
    z_j^*=sum_(k=j+1)^p a_k z^(k-j-1) / f'(z),  a_p=1.

Set

    kappa=-f'(z)/z^(p-1),  s=kappa pr.

The displayed dual-basis formula gives

    s(T_ij)=-z^(i-j) + terms of strictly larger E-valuation.

Indeed v_E(a_k)>=p for 1<=k<p, so the contribution indexed by a_k has
valuation at least k greater than the first contribution. Applying s
entrywise on E^m gives a B-bimodule corestriction from End_L(E^m) to
B=End_E(E^m). With the complete interleaved period-pm L-chain and
period-m E-chain, it preserves grades and satisfies s(P^r)=Q^r.

Let P0 extract the constant coefficient on every E-coordinate. The
constant dual coefficient satisfies

    z_0^*=-a_0/(z f'(z)),
    u_0=s(P0)=kappa z_0^*=a_0/z^p in O_E^times.

For any C in M_m(E), define the actual L-linear matrix

    Lift_E(C)=u_0^(-1) C P0.

Then

    s(Lift_E(C))=C.

This lift preserves the exact filtration valuation. To see this, first
multiply C by the unit u_0^(-1), which does not change its valuation in
the E-chain. Expand each entry in the basis 1,z,...,z^(p-1). The only
nonzero columns of Lift are its constant-coefficient columns. The L-grade
of a coefficient c_i z^i E_uv is

    pm*v_L(c_i)+mi+u-v,

equal to its E-grade, and distinct i have valuations distinct modulo p.
Thus the minimum cannot cancel. This also proves the stated surjectivity
s(P^r)=Q^r without a compactness or lifting-existence assumption.

## 3. Exact trace identity

For y in E, extraction of its constant coefficient is

    coeff_0(y)=Tr_(E/L)(z_0^* y).

The ordinary L-matrix trace of the rank-one operator yP0 is coeff_0(y).
Consequently, for every C in M_m(E),

    tr_L(Lift_E(C))
       =Tr_(E/L)(z_0^* u_0^(-1) tr_E(C))
       =Tr_(E/L)(kappa^(-1) tr_E(C)).             (T)

Here tr_E(C) is the ordinary m-by-m matrix trace over E. In particular,
if tr_E(C)=0, then the lift has ordinary L-matrix trace zero exactly.

## 4. The recursive actual matrix

Define B(L,t_L;h_1,...,h_d) by induction. For d=1 use the multiplication
matrix of the alpha from Section1 with q=q_1. For d>=2 use Section1 with
q=q_d, put m=p^(d-1), recursively construct

    C=B(E,z;h_1,...,h_(d-1)),

and set

    B(L,t_L;h_1,...,h_d)=alpha I_m+Lift_E(C).       (ASR)

Everything in (ASR) is explicit in finite field operations and the
displayed degree-p polynomial extensions. It differs from the old
conjugacy-preserving two-summand construction. Preserving old lower
summand conjugacy classes is not claimed.

Inductively tr_E(C)=0. Equation (T) and the Artin--Schreier trace give

    tr_L(B)=m Tr_(E/L)(alpha)+tr_L(Lift_E(C))=0.

For the induction base the trace is Tr_(E/L)(alpha)=0. Thus this argument
proves tracelessness in the current base field for every native rank,
not merely tracelessness after an amplification whose size is divisible
by p.

## 5. Actual fields and profiles

Set gamma=alpha I_m and b=Lift_E(C). The minimal outer stratum has

    n=p^(d-1)q_d,  k_0(gamma)=-n.

The inner actual maximal field supplied by induction has

    R=p^(d-2)q_(d-1),  v(C)=-R,  k_0(C)=-q_1.

We have s(b)=C, v(b)=-R, and n>pR>2R because p is odd and the h_i
increase. Hence

    -2R > -n-q_1 = k_0(gamma)+k_0(C).

BK Remark2.2.7 applies to this pure derived maximal field. It gives the
field generated by the actual displayed gamma+b, with degree and
ramification p^d, residue degree one, normalization of the complete
chain, and k_0=-q_1. Its valuation remains -n. Thus [A,n,0,B] is simple.

This repeats the precise argument of RECURSIVE_TOWER166.md with a new
outer minimal extension and normalized right inverse. No step of that
argument required the old polynomial e^p+t e+t.

## 6. Native approximations, amplification, and traceless corrections

For the full rank p^d matrix put, for 1<=j<=d,

    B^[j]=B(F,t;h_(d-j+1),...,h_d) tensor I_(p^(d-j)).

These are literal truncations of (ASR). At the outer level the same
largest q_d selects the same Artin--Schreier extension and uniformizer
in all truncations. At the next level the same q_(d-1) does the same,
and so on. Thus no hidden change of bases or incompatible parameter
fields enters the truncations. Lift_E commutes with amplification by
an identity because P0 acts separately on each coordinate.

Every native shorter B has trace zero by Section4. Its amplification
therefore has trace zero. In particular

    tr_F(B^[j])=0,
    tr_F(B^[j+1]-B^[j])=0.                        (Z)

The same is true at native rank p^(j+1): the correction between
B(F,t;h_(d-j),...,h_d) and the identity-p amplification of
B(F,t;h_(d-j+1),...,h_d) has trace zero. This native assertion is the
one relevant when constructing characters before each transfer.

The field degrees and critical levels of B^[j] are exactly

    degree p^j,  n_j=p^(d-j)q_(d-j+1).

Valuation-preservation of every Lift gives

    v_A(B^[j+1]-B^[j])=-n_(j+1).

Thus the approximation and defining-sequence proof of the first note
applies unchanged. The odd-prime J/H dimensions, grade-index formula,
Swan conductor and self-pair conductor depend on these same levels and
centralizer degrees, so all their formulas carry over unchanged.

## 7. Precisely what the trace supplies

For any displayed correction delta and any scalar u in L^times for
which its additive correction character is defined,

    psi_delta(u I)=psi_L((u-1)tr_L(delta))=1.

This proves triviality of the actual additive correction on the scalar
subgroup of its domain. It does not, by itself, construct a simple
character with prescribed values on larger scalar groups. Compatible
extension, transfer, and intersection arguments for the full simple
character are separate obligations.

The note also does not identify the constructed candidates with any
Weil source, choose them by inverse LLC, realize arbitrary stabilizer
operators, or prove same-candidate H5. Its new output is an explicit
arithmetic defining sequence whose trace vanishes at every native and
amplified stage, suitable as input to that separate character argument.

## Primary dependency

Bushnell--Kutzko, The admissible dual of GL(N) via compact open subgroups,
Remark2.2.7 (printed p55), with the defining-sequence and ring recursion
already pinned in RECURSIVE_TOWER166.md. Retained source SHA256:
d69db0827256707a34cd2562af68b9de11fc889ab3f43535ec47b620d58ca9c8.
The trace-dual and Artin--Schreier calculations above are given in full.
