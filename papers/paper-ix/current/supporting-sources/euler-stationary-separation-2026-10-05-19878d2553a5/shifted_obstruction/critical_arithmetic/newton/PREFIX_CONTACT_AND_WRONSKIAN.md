# Actual-prefix derivative inheritance and the contact Wronskian

Status: proved structural consequences and an explicit free-coefficient
countermodel. Actual Bernoulli/Euler critical nonvanishing remains open.

The input is the new exact theorem in
`../../root/EXACT_REGULARIZED_MOMENTS.md`: for

    u(s)=1+3*9^s,  b(s)=u(s) Ecal(s),

one has v2(b^(j)(s))=3j+2 for every j>=0 and s in Z_2. The bounded-measure
formula there also gives the coefficientwise bounds

    b^(j) in2^(3j+2) Z_2<s>.

The pointwise exact valuations are stronger than these Gauss bounds.

## 1. The actual cutoff automatically inherits all derivative valuations below r

For an ordinary r>=1 write

    S_r=sum_(m<r) 8^m beta_m P_m(s) A(s-m),
    F_r=Ecal-S_r,
    C_r=u S_r,   B_r=b-C_r=u F_r.

For every m>=1, v2(beta_m)=s2(m)-1>=0. Both P_m and A(s-m) are integral
restricted. Therefore the actual omitted tail satisfies, coefficientwise,

    F_r in2^(3r) Z_2<s>,
    B_r in2^(3r+2) Z_2<s>.                                (1)

Ordinary differentiation preserves a coefficientwise divisibility ideal in
Z_2<s>: it only multiplies coefficients by ordinary integers. Thus

    B_r^(j) in2^(3r+2) Z_2<s>  for every j>=0.             (2)

For 0<=j<r, the valuation3j+2 of b^(j)(s) is strictly below3r+2. Subtracting
(2) proves the uniform actual-prefix theorem

    v2(C_r^(j)(s))=3j+2,
    every s in Z_2 and every 0<=j<r.                      (3)

This is a consequence for the prescribed actual finite prefix, not a generic
deformation. In particular the two necessary derivative valuations at a
hypothetical double contact are automatically satisfied whenever r>=2.
Indeed all derivative-valuation conditions of order below r are automatic.
It is therefore impossible to obtain a contradiction merely by comparing
those valuations with the corresponding valuations of b.

No assertion is made about orders j>=r. The strict inequality used in the
proof stops exactly there. This result does not contradict the established
failure of an all-order bounded-measure estimate for the finite prefix.

## 2. Exact logarithmic-derivative identity

Since Ecal is a unit and u has valuation2, neither b nor u vanishes on Z_2.
Put H_r=C_r/b=S_r/Ecal. Then

    H_r=1-F_r/Ecal in1+2^(3r) Z_2<s>.

The exact Wronskian is

    W_r=b C_r'-b' C_r
       =b^2 H_r'
       =u^2 (Ecal S_r'-Ecal' S_r)
       =b' B_r-b B_r'.                                    (4)

In particular regularization cancels exactly from the logarithmic-derivative
difference:

    C_r'/C_r-b'/b = S_r'/S_r-Ecal'/Ecal                  (5)

where S_r is nonzero. The exact regularizing factor does not create an
additional forcing term in this Wronskian. From (1)-(2) and the Gauss bounds
on b,b' one obtains

    W_r in2^(3r+4) Z_2<s>.                                (6)

At a simultaneous contact C_r=b, C_r'=b', the equations become

    H_r=1, H_r'=0, W_r=0.

Differentiating (4) at such a contact gives

    W_r'=b(C_r''-b'')=-b B_r''.                           (7)

Equation (7) can certify a simple zero of the Wronskian if B_r'' is nonzero.
It does not exclude that zero. A second-order contact is fully consistent
with a nonzero Wronskian derivative. Thus a Rolle or Newton argument needs
an additional actual-prefix estimate, not merely b's nonzero derivatives.

For completeness the actual finite coefficients remain explicit. Let

    D=(s+1)(2s+1), lambda=9^(s+1), L=log9,
    Q_r=1+D sum_(1<=m<r) 8^m beta_m 9^-m P_(m-1)(s),
    R_r=1+D sum_(1<=m<r) 8^m beta_m P_(m-1)(s),
    N_r=lambda Q_r-R_r.

The inherited exact finite resummation gives S_r=N_r/(8D). Hence

    W_r = u^2/(8D^2) *
      { Ecal [D(lambda(Q_r'+LQ_r)-R_r')-D'N_r]
        -D Ecal' N_r }.                                   (8)

This holds where D!=0 and extends at the removable points by the original
analytic definition (4). On the surviving deep chart D is nonzero: s is
10041 mod32768, so v2(s+1)=1 and 2s+1 is odd. Formula (8) retains the actual
finite prefix and its derivative. It does not separate its two terms at a
hypothetical contact; substituting N_r=8D Ecal and its derivative makes the
right side vanish identically, as it must.

## 3. The two source packets have an invertible value-derivative matrix

Set

    J(y)=P_1(y) A(y-1)=(9^y-1)/8.

The exact source congruences give

    A=1 (mod2) coefficientwise, A'=0 (mod2),
    J'=1 (mod2) coefficientwise.

The last assertion follows from J'=(log9/8)9^y and log9/8 odd.
Consequently, for every a in Z_2,

    det [[A(a), J(a)], [A'(a), J'(a)]]
       =A(a)J'(a)-A'(a)J(a)=1 (mod2).                    (9)

This is a uniform unit determinant for the actual source functions. Given
any two target jets v,w in2^M Z_2, the unique solution of

    d0 A(a)+d1 J(a)=v,
    d0 A'(a)+d1 J'(a)=w                                  (10)

has d0,d1 in2^M Z_2.

For r>=2, apply (10) with v=F_r(a), w=F_r'(a), M=3r. Modifying only the
coefficients of A and J in S_r by d0,d1 produces a finite prefix of the same
cutoff length with exact value and derivative contact at a. Its regularized
prefix retains all valuations in (3). These coefficients are dyadic numbers,
not asserted rational or Bernoulli. This first construction need not preserve
the forced lower Euler interpolation values; the next one does preserve them.

## 4. Stronger model: preserve the actual prefix and the forced skeleton

The product law P_(r+q)(s)=P_r(s)P_q(s-r) gives the exact factorization

    F_r(s)=P_r(s) Hbar_r(s-r),
    Hbar_r(y)=sum_(q>=0) 8^(r+q) beta_(r+q)
                            P_q(y) A(y-q).

The last series is coefficientwise in2^(3r) Z_2<y>, as is its derivative.
Choose any a in Z_2. Apply (10) to

    v=Hbar_r(a), w=Hbar_r'(a), M=3r.

Define a finite prefix with cutoff length r+2 by appending two free packets
to the unchanged actual prefix of length r:

    S_tilde(s)=S_r(s)
       +d0 P_r(s) A(s-r)
       +d1 P_(r+1)(s) A(s-r-1).                           (11)

Then exactly

    Ecal(s)-S_tilde(s)=P_r(s) Q(s-r),
    Q(y)=Hbar_r(y)-d0 A(y)-d1 J(y),
    Q(a)=Q'(a)=0.                                        (12)

Thus the quotient residual has a repeated zero at a. If P_r(r+a)!=0, the
unfactored residual has at least a double zero at s=r+a. All original
coefficients with m<r are unchanged. Every forced zero supplied by P_r is
preserved. The appended coefficients d0,d1 lie in2^(3r) Z_2; the construction
does not assert their equality to8^r beta_r and8^(r+1) beta_(r+1).

The coefficientwise bound in (1) still holds for the new residual because
both appended terms are in2^(3r) Z_2<s>. Its regularized prefix therefore
still satisfies (3) for every j<r. The comparison is with the bound of the
original cutoff r, not an unproved order-r+2 bound for the free cutoff.

This construction is not an Euler counterexample. It proves that the full
regularized derivative laws, finite source-packet form, fixed lower actual
prefix, and forced skeleton together do not exclude double contact when the
next two dyadic coefficients are free. Arithmetic constraints on those actual
Bernoulli coefficients are essential.

## 5. Precise outcome

The new positive theorem is the actual-prefix derivative inheritance (3).
The exact Wronskian (4), finite formula (8), and unit two-jet matrix (9) are
uniform identities. The free two-packet construction (11)-(12) is an explicit
countermodel to deriving noncontact from those analytic/jet properties alone.

The remaining actual-index problem is to prove that the prescribed next and
subsequent Bernoulli coefficients cannot realize the simultaneous contact.
No strict estimate for that actual Wronskian under contact was obtained.
No parameter digits were extended, and no new Lean compilation was performed.

The existing exact source and tail estimates prove the general statements.
The accompanying checker verifies the Wronskian algebra by independent finite
polynomial coefficient identities and verifies the source jet determinant at
bounded precision. These finite checks do not supply the universal quantifiers.
