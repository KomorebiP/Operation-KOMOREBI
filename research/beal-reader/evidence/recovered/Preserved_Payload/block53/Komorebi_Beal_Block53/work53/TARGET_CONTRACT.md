# Block 53 target and dependency contract

The sole authoritative predecessor is
Komorebi_Beal_Block52_Frobenius_Kummer_v5.2.0.zip,
SHA256 4b4d14f7c7c3b5474a8c209845cf2652497e6a266d657af00d0171bcc4367157.
It is preserved byte for byte. The startup replay passed before new files were
written. Earlier conjectural brainstorming is a proposal, not an authority.

## Objective and exact scope

Prove or refute the proposed implication good 13 ==> depth 1 by auditing the
fixed local places and global diagonal correction. Pursue structural
consequences that use the same actual representation. Success is not the
elimination of all reducible representations, the full signature, or Beal.

## Inherited arithmetic inputs

H1. A,B,C are positive pairwise-coprime integers, A^3+B^5=C^7, 3990|C.
J is the genus-two Jacobian of
Z^2=X^6+10BX^3+12AX+5B^2.

H2. K=Q(sqrt5), phi=(1+sqrt5)/2, E=Q_7(sqrt5), O=Z_7[phi], k=F49.
The 7-adic RM representation of the actual Jacobian, twisted by the character
nu of Q(zeta15)^+/K, is rank two over E. Its natural lattice is free over O,
and determinant is chi_7 in characteristic zero. The underlying rank-four
Q7 representation is restriction of scalars. Its natural residual orientation
has subcharacter chi_bar and quotient1.

H3. In the SINGLE natural-lattice Frobenius-at-three basis from Block51,
rho(g)=[[a(g),b(g)],[7^n c(g),d(g)]], a mod 7=chi_bar, d mod 7=1,
for a finite actual depth n>=1. This is not an arbitrary congruence modulus.
The actual opposite endpoint beta is nonzero and must ramify at an eligible
place above a divisor of C. The usual alpha/beta coupling is retained.

H4. In this same natural lattice, at every variable v above q|C with
q outside{2,3,5,7}, inertia is I+N_tau, N_tau^2=0 and N_tau in 7M_2(O).
The characteristic-zero natural monodromy content is
1+v_7(v_q(C))>=1. Integral changes of natural-lattice basis preserve this
entrywise divisibility. This input is audited in LOCAL_INPUT_AUDIT.md.

H5. At EACH place over 2,3,5,7 the actual twisted characteristic-zero RM
representation has toric subcharacter chi_7 and quotient1. This is stronger
than a residual splitting claim. At7 it comes from the analytic toric
uniformization at all 7-power levels, not a prime-to-seven theorem. The
comparison of inherited geometric files to this exact hypothesis is in
LOCAL_INPUT_AUDIT.md. At all other finite places not dividing C the twist and
representation are unramified. The finite ramification of nu is confined to3,5.

H6. At good 13, Block52 gives the ACTUAL scalar rho(Frob_(13))=-13I and
chi_7(Frob_(13))=169. This uses its complete finite certificate and semisimple
abelian Frobenius. A characteristic-polynomial congruence is not a substitute.

H7. For further support consequences retain the one global Kummer expansion
alpha=a_phi[phi]+a_3[3]+a_5[sqrt5], a_3*a_5!=0 in F49; the common-coordinate
local forms at 29,43,71; and the Block51 equality n=t+2s,0<=s<=h at actual
beta-ramified places, with alpha zero below the upper endpoint. Good13 gives
a_phi=0. Retain 71|C and n>=2 ==>29*43|C from Block52.

All H inputs are inherited source-dependent written mathematics. The new
finite checks do not certify them. Local-input auditing and a separate
adversarial self-review were performed, but no fresh independent mathematical
reviewer or Lean compilation was obtained. A new failure in an H input would
require propagating a correction to dependent arithmetic conclusions.

## Classical external leaves

C1. Hilbert class field theorem for finite abelian extensions unramified at all
places. Here the relevant field is K, not K(zeta7). Cl(K)=1 is also established
in the proof by the elementary norm-Euclidean argument; Minkowski is a second
check. Real places cannot ramify in the finite7-group image.
C2. At good reduction, order equals det_Q7(1-Frob); the Weil eigenvalue bounds
imply #J(F_Q)<=(1+sqrt(Q))^4. See source_records/SOURCE_CHECK.md.

## Verification contract

Arithmetic in the two scripts is exact integers and exact quadratic finite
rings. Generated families, complete finite rings, and coefficient enumerations
are distinguished in their JSON. Passing them is finite evidence for the
implementation and algebra, not an exhaustion of global representations.
A failure is separated into counterexample, code error, unavailable source,
or inconclusive timeout. No new auxiliary-prime point counts are performed.
