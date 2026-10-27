# A native four-dimensional carrier in the rank-four dyadic candidate

Date: 2026-10-05. Ordinary proof submitted for independent review.

## Result and boundary

For the actual rank-four Artin--Schreier candidate of Block167, one can
enlarge the compact group J1 to an actual compact subgroup P with

    J1 normal in P,  [P:J1]=2,
    E=Ind_(J1)^P(eta) irreducible of dimension 4.

The representation E occurs inside the restriction of the same actual
supercuspidal candidate pi. There is an explicit normal subgroup H0 of
P with [P:H0]=16 such that P/H0 is elementary abelian and the commutator
form supplied by the actual character on H0 is nondegenerate. Thus the
carrier has an actual four-dimensional binary symplectic quotient.
No abstract transfer of matrix operators is used to create this action.

The finite image of P has scalar center theta(H0), which can be larger
than {+1,-1}. It is literally an extraspecial group if this scalar center
has order two. That additional assertion is not assumed or proved here.
The construction supplies an actual finite Heisenberg central extension
with nondegenerate projective quotient F_2^4. Matching an independently
prescribed quadratic phase is also a separate assertion.

## 1. Actual arithmetic groups and notation

Let F=F_2((t)), and take the audited rank-four constructor with odd
0<h_1<h_2. Write

    q_i=3h_i,  n=2q_2,  a=n/2=q_2,
    r=q_1=2m+1,  m=(r-1)/2>=1.

We have a>r, so n>2r. Let A be the complete period-four hereditary
order, with radical P_A. Let gamma be the actual degree-two outer
minimal approximation, E=F[gamma], B=End_E(F^4)=M_2(E), B0=A cap B,
and Q=rad(B0). The actual final parameter is beta=gamma+delta, and

    s(delta)=c,

where c is the minimal degree-two Artin--Schreier parameter over E,
of B0-level r. The final field K=F[beta] is totally ramified of degree
four; no embedding E subset K is asserted.

Use U_A^j=1+P_A^j and U_B^j=1+Q^j. BK3.1.7--9 give the actual groups

    H=H1(beta)=U_K^1 U_B^(m+1) U_A^(a+1),
    J=J1(beta)=U_K^1 U_B^(m+1) U_A^a.

In particular J/H has dimension two over F_2. Let theta be the actual
full simple character constructed for beta, and let eta be its unique
Heisenberg representation on J, of dimension two. The argument below
works with this supplied actual theta; it does not replace its values.

Choose the outer minimal simple character theta_gamma from its defining
sequence. On H cap U_A^(m+1), the recursion says

    theta=theta_gamma psi_delta.

Moreover H is contained in H1(gamma)=U_B^1 U_A^(a+1). The character
theta_gamma is invariant under U_B^1: on U_B^1 it factors through the
E-determinant, and on U_A^(a+1) it is the gamma-additive character.

## 2. The actual final field has the needed graded line

For every integer j>=1 and k in K cap P_A^j, the minimal-approximation
commutator estimate gives

    k=b+e,  b in Q^j,  e in P_A^(j+n-r).              (1)

Indeed [gamma,k]=-[delta,k] belongs to P_A^(j-r), and the minimal
corestriction exact sequence for gamma solves its commutator with an
error of grade j+n-r. The remaining difference centralizes gamma and
therefore belongs to B. This is the usual minimal case of BK1.4.10.

Applying s to [beta,k]=0 and using (1) gives

    [c,b] in Q^(j+n-2r).

Hence the leading B-grade of b commutes with the leading grade of c.
Let R be the complete period-two E-chain shift, with R^2=z I, where z
is the chosen uniformizer of E. In the constructor's basis

    c congruent to R^(-r) modulo Q^(1-r).

Because r is odd, the centralizing subspace on every B-grade j is the
one-dimensional line spanned by R^j. On the other hand K is a totally
ramified maximal field normalizing the complete A-chain, so
(K cap P_A^j)/(K cap P_A^(j+1)) has dimension one over F_2. Estimate
(1) is injective on the leading grade, so its image is exactly that
centralizing line.

This proves the required graded assertion for the actual K, without
replacing it by the derived model E[c] or assuming nested fields.

## 3. Normality and index of the enlarged group

Set

    P=J U_B^m.

We first prove this is a group. The group U_B^m normalizes U_B^(m+1)
and every U_A^j. For k in U_K^1, (1) approximates k by an element of
U_B^1 with error in U_A^(n-r+1). Therefore

    [U_B^m,U_K^1]
       subset U_B^(m+1) U_A^(m+n-r+1)
       subset H,

where the last inclusion follows from a>r=2m+1. Thus U_B^m normalizes
both H and J, and P is an actual compact subgroup with J normal in P.

The quotient U_B^m/U_B^(m+1) has dimension two. By Section2 the image of
J cap U_B^m on this grade is exactly its centralizing line, of dimension
one. For the converse inclusion needed here, the B-approximation of a
K-element of grade m differs from it by grade m+n-r>a; that error lies
in U_A^a subset J. Thus the whole centralizing line really occurs in
the intersection, not only in an abstract associated graded space.
Consequently

    [P:J]=[U_B^m:J cap U_B^m]=2.                    (2)

For a concrete representative choose D=diag(1,0) in B and put

    x=R^m D,  u=1+x.

Its leading grade is outside the centralizing line, so u represents
the nontrivial coset of P/J. Since u^2=1+x^2 in characteristic two,
we have u^2 in U_B^(2m) subset U_B^(m+1) subset H.

## 4. The actual character has an orbit of length two

Define the character of H

    lambda(h)=theta(u h u^(-1))/theta(h).

For h in H the preceding normality argument gives [u,h] in
H cap U_A^(m+1). Since theta_gamma is invariant under u,

    lambda(h)=psi_delta([u,h]) in {+1,-1}.          (3)

Thus lambda has order dividing two, and its values are actual values
of the supplied simple character. It is J-invariant, since both theta
and its u-conjugate are J-invariant.

It is nontrivial. Take y=R^(m+1)D and h=1+y in U_B^(m+1). The leading
commutator in (3), after corestriction, has value

    psi_E(tr_(M_2(E)/E)(c[x,y]))=-1.

Here the commutator remainder has B-grade at least 3m+1, which becomes
positive after multiplication by c of grade -2m-1. On the leading
grades, writing X=R^m diag(A,B) and Y=R^(m+1)diag(C,D), one obtains

    tr(R^(-2m-1)[X,Y])=(A+B)(C+D) in F_2.

Both sums equal one for the chosen D=diag(1,0). The normalized psi_E
is nontrivial on the residue field and trivial on its maximal ideal.
For this AS normalization one can check the sign directly from
psi_E(1)=psi_F(Tr_(E/F)(alpha))=psi_F(1)=-1.

Hence theta^u differs from theta, eta^u differs from eta, and Clifford
theory applied to (2) gives

    E_carrier=Ind_J^P(eta) irreducible, dim(E_carrier)=4.       (4)

## 5. An actual nondegenerate symplectic quotient of dimension four

Put H0=ker(lambda) inside H, and theta0=theta restricted to H0. In the
two-coset induction model, h in H acts by

    diag(theta(h) I_2, theta^u(h) I_2).

Thus it acts scalarly precisely when h belongs to H0. We check that
H0 is the entire scalar preimage and that its quotient is symplectic.

First, lambda is invariant under u. Indeed u^2 belongs to J and theta
is J-invariant, so lambda^u=lambda^(-1)=lambda by (3). Consequently
H0 is normal in P, and theta0 is P-invariant.

Second, lambda is trivial on U_A^(a+1). There the correction formula is
valid, gamma commutes with u, and the delta contribution to a
commutator has grade at least a+1+m-r=a-m>0. Therefore it lies in the
kernel of the additive character.

Write J=H U_A^a. Since lambda is a character and J-invariant, it kills
[H,H] and [H,U_A^a]. It also kills [U_A^a,U_A^a], which lies in
U_A^(2a). Hence lambda([J,J])=1. It kills every square in J as well:
squares of H have lambda-value one, squares of U_A^a lie in U_A^(2a),
and the mixed commutator contributions have just been handled.

Finally lambda([u,H])=1 by u-invariance, and [u,U_A^a] belongs to
U_A^(a+m) subset U_A^(a+1), so lambda([u,J])=1. Also lambda(u^2)=1
because u commutes with u^2. It follows that

    [P,P] subset H0,  g^2 in H0 for every g in P,
    [P:H0]=[P:J][J:H][H:H0]=2*4*2=16.

Therefore P/H0 is an actual elementary abelian group of dimension four.
If an element of J acts scalarly on the carrier, its first eta-block
is scalar, so it belongs to H by the original nondegenerate Heisenberg
quotient J/H. It then belongs to H0. An element outside J exchanges the
two coset summands and cannot act scalarly. Thus H0 is precisely the
scalar preimage.

The pairing

    (gH0,kH0) |-> theta0([g,k])

is alternating and well defined. Since the projective quotient has
exponent two, its values lie in {+1,-1}. It is nondegenerate: an element
in its radical commutes with the entire irreducible carrier image and
therefore acts scalarly by Schur's lemma, forcing it into H0.

This is the actual four-dimensional binary Heisenberg quotient sought
for capacity. Its operators are supplied by elements of P.

## 6. The carrier occurs in the same supercuspidal candidate

Let pi=c-Ind_N^(GL_4(F))(Lambda) be the existing actual candidate, with
N=K^times J. The residue field is F_2, so the compact extended type
restricts to eta on J. Since P is contained in U_A^1,

    N cap P=J.

Indeed an element k j in P with k in K^times has k in U_A^1, hence
k in U_K^1 subset J. The identity double-coset term in the restriction
of compact induction to P is therefore

    Ind_J^P(eta)=E_carrier.

It is realized concretely by the functions supported on N P. Thus the
four-dimensional carrier occurs in the same pi, with its already fixed
full type character and noncompact extension scalar. No new arithmetic
candidate, beta extension, or inverse correspondence is used.

## 7. Exact limits: finite image versus literal extraspecial group

The actual finite image is P/ker(theta0), because H0 is the scalar
preimage. Its center is the scalar cyclic 2-group theta0(H0), and its
commutator subgroup has order two. Its quotient by its center is F_2^4.

If theta0(H0) has order two, this finite image is extraspecial of order
32. If its scalar center is larger, quotienting arbitrary central
elements need not preserve its commutator: in a cyclic 2-group the
order-two subgroup can lie inside the squares. Thus a literal
extraspecial quotient is not justified solely by the calculations above.

The stronger statement proved is the one with full actual character:
an actual compact subgroup, actual induced carrier, actual scalar
subgroup and nondegenerate actual commutator pairing. Passing to the
usual full scalar pushout retains all theta0-values. It does not prove
that an independently supplied quadratic refinement, stabilizer action,
or source phase agrees with this carrier. Those requirements must be
checked separately. No H5 or universal claim66 closure is asserted.

## Provenance

Uses the audited dyadic parameter/character construction, BK1.4.10,
BK3.1.7--9, and the defining-sequence character formula. The source
normalization and all field/chain data are the actual ones in
dyadic167/tower/DYADIC_AS_TOWER167.md. This note changes neither that
proof nor its recorded exact computation. Clifford induction and the
identity compact-induction double-coset term are used in their ordinary
finite-index forms, with hypotheses proved above.
