# Full characters with trivial wild center on the dyadic AS tower

Checkpoint: Paper_XI_Dyadic167. Parent: final Paper_XI_Attachment166.
Author scope: this file only; no Block166 file is modified.

Evidence: ordinary mathematical proof using the actual Artin–Schreier
matrix tower and the retained Bushnell–Kutzko character and transfer
theorems. No Lean verification is claimed. This note proves no dyadic
quotient-capacity, quadratic-phase, packet-attachment, or H5 result.

## 1. Exact theorem

Let F=F_2((t)), let psi_F be an additive character of conductor t O_F
(trivial there and nontrivial on O_F), and let

    0<h_1<...<h_d,       each h_i odd,
    q_i=3h_i,           N=2^d.

Use the dyadic Artin–Schreier recursion specified in Section2. It gives
the actual maximal simple parameter beta_d with its native arithmetic
defining sequence. There is an actual full simple character theta of
its maximal simple stratum such that

    theta restricted to U_F^1 is trivial.                         (1)

The construction retains the actual canonical beta extension and can
be completed with any prescribed central quasicharacter omega_F
trivial on U_F^1. Because k_F^times=F_2^times is trivial, such an omega_F
is unramified. Thus this covers every tamely ramified central
quasicharacter in this particular residue-field setting.

The corresponding compact induction is an actual irreducible
admissible supercuspidal of rank N, by the retained maximal-simple-type
theorem. No claim is made here about its Heisenberg quotient size or
about realization of a supplied dyadic finite packet.

The trace-zero argument from166 does not apply verbatim: at p=2 the
primitive Artin–Schreier parameter has trace one. The correct invariant
is **integral trace**, not necessarily zero trace. Since psi_F kills
t O_F, integral correction trace is sufficient on scalar principal
units. The recursion below preserves the stronger exact value one.

## 2. Actual dyadic recursion and exact native traces

At a recursive step let L be a characteristic-two local field with
residue field F_2, uniformizer t_L, and a positive odd q. Define

    E=L(alpha),       alpha^2-alpha=t_L^(-q).

The right side is not an Artin–Schreier coboundary: a negative
valuation of x^2-x is even, whereas -q is odd. The degree-two
polynomial is therefore irreducible and separable. Its valuation
equation gives total ramification and v_E(alpha)=-q. Put

    a=(q+1)/2,       z=t_L^a alpha.

Then z is an actual uniformizer and its Eisenstein polynomial is

    f(Z)=Z^2+t_L^a Z+t_L.                                      (2)

Its two conjugate alpha values are alpha and alpha+1, so

    Tr_(E/L)(alpha)=1.                                         (3)

Use the coefficient basis 1,z, the trace corestriction pr, and the
same normalized corestriction convention as166:

    kappa=-f'(z)/z = t_L^a/z = alpha^(-1),
    s=kappa pr.

Minus and plus agree in characteristic two. If P0 extracts the
constant coefficient on every E-coordinate, then

    u_0=s(P0)=t_L/z^2 is a unit,
    Lift_E(C)=u_0^(-1) C P0,
    s(Lift_E(C))=C.

The trace-dual calculation in166 gives, as an identity of L-matrix
traces for every matrix C over E,

    tr_L Lift_E(C)
       =Tr_(E/L)(kappa^(-1) tr_E(C))
       =Tr_(E/L)(alpha tr_E(C)).                               (4)

The lift preserves the complete-chain filtration valuation, by
expansion in 1,z. Thus it is the actual filtered right inverse used
in the field constructor, not an arbitrary inverse on vector spaces.

Define B(L,t_L;h_1,...,h_s) recursively. At s=1 use the L-matrix of
multiplication by alpha with q=q_1. At s>=2 use (2) with q=q_s,
m=2^(s-1), and

    C=B(E,z;h_1,...,h_(s-1)),
    B(L,t_L;h_1,...,h_s)=alpha I_m+Lift_E(C).                    (5)

The base trace is one by (3). If tr_E(C)=1, then (4) gives lift
trace one. Since m is even, the trace of alpha I_m as an L-matrix is
m Tr_(E/L)(alpha)=0. Consequently

    tr_L B(L,t_L;h_1,...,h_s)=1                                (6)

for every native recursion, by induction. There is no division by
the rank and no confusion between a native trace and its amplified
trace.

The actual field proof from166 applies with this degree-two
extension and normalized lift. At a nontrivial step its hypotheses
are n=2^(s-1)q_s, R=2^(s-2)q_(s-1), s(Lift(C))=C, and

    n>2R,
    -2R>-n-q_1.

The first strict inequality follows from h_s>h_(s-1). These are the
conditions used in BK Remark2.2.7. The displayed beta itself generates
the totally ramified degree-2^s field normalizing the complete chain,
and its final critical exponent is -q_1. This statement does not
identify the final field with its auxiliary derived field.

For the final length d write the native shorter matrices as

    b_j=B(F,t;h_(d-j+1),...,h_d),       1<=j<=d.

They are the compatible native truncations of (5), because the
outer extension, uniformizer, and lift depend on the same retained
largest h at each stage. In rank 2^(j+1), put

    gamma_j=b_j tensor I_2,
    delta_j=b_(j+1)-gamma_j.

The defining-sequence calculation of166 gives gamma_j as a simple
approximation at the critical level r_j=q_(d-j) of b_(j+1), and
delta_j has grade -r_j. Equation (6) gives the exact scalar identity

    tr_F(gamma_j)=0,
    tr_F(delta_j)=1.                                          (7)

Thus for every scalar u in U_F^1 on which its additive correction
is defined,

    psi_(delta_j)(u I)=psi_F((u-1)tr_F(delta_j))
                     =psi_F(u-1)=1.                           (8)

It is (8), not a false trace-zero assertion, that drives the full
character construction.

## 3. The odd-critical-level rounding

The critical levels r=q_i are odd. Write r=2s+1, and set

    m=floor(r/2)=s,        m+1=(r+1)/2.

The relevant BK statements use the floor, with no assumption that
r or the residue characteristic is odd or even:

- BK3.1.9(ii) identifies H^k(beta) and H^k(gamma) for
  k>=floor(r/2)+1.
- BK3.3.18 gives the correction bijection at
  floor(r/2)<=m<=r-1.
- BK3.2.5 extends the resulting character at floor(r/2) to a full
  character, its fibers being the indicated determinant characters.

At our exact endpoint m=s, the correction character is legitimate.
For x,y in the radical power P^(s+1),

    delta*x*y belongs to P^(2(s+1)-r)=P^1.

The level-one additive matrix character is trivial on P^1, so the
multiplicative cross term contributes one. Therefore psi_delta is
a character on U^(s+1), and hence on the recursive subgroup used
below. This checks the borderline odd-level rounding directly.
Replacing m by r/2 as if it were an integer would be incorrect.

The same check applies at the native minimal base level q, which
is odd: its forced additive character begins at
floor(q/2)+1=(q+1)/2, and 2*(q+1)/2-q=1.

## 4. Finite character extension at maximal rank

We reuse the elementary extension procedure with its compatibility
condition explicit. If K/F is a finite totally ramified field, and
chi is a smooth character of U_K^a trivial on U_K^a intersect U_F^1,
define a character on U_K^a U_F^1 by

    chi_0(ku)=chi(k).

It is well defined by the intersection condition. Choose M>=a with
chi|U_K^M=1. Then chi_0 is a character of a subgroup of the finite
abelian group U_K^1/U_K^M. Extend it by adjoining generators and
choosing the required complex roots, and pull it back. The resulting
chi_K extends chi and is trivial on U_F^1.

All freely chosen character extensions below take place at maximal
native rank, where the centralizer is K itself. We do not apply this
scalar-intersection argument directly inside a nonmaximal matrix
centralizer, which would require a separate determinant-image check.

## 5. Base full character with trace one

At native rank two, let E=F[alpha], with q=q_d and
a=floor(q/2)+1. The forced character on U_E^a is

    phi(v)=psi_F(Tr_(E/F)(alpha(v-1))).

For scalar u in U_E^a intersect U_F^1, equation (3) gives

    phi(u)=psi_F((u-1)Tr_(E/F)(alpha))=psi_F(u-1)=1.

Section4 constructs chi_E on U_E^1 extending phi and trivial on
U_F^1. Define theta_1 on H^1=U_E^1 U_(A_1)^a by chi_E on the first
factor and psi_alpha on the second. The restrictions agree on the
intersection. BK3.2.1 gives the actual full simple character, with
theta_1|U_F^1=1.

This uses the true trace value one and only the stated conductor
condition on psi_F. It does not require an artificial zero-trace
primitive parameter in a quadratic extension.

## 6. Native-rank induction via full beta-determinant transfer

Assume theta_j is a full simple character for native b_j in rank
2^j, with theta_j|U_F^1=1. Let K_j=F[b_j]. Since K_j is maximal,
the character chi_j=theta_j|U_(K_j)^1 is its full beta-determinant
character.

Transfer theta_j to the multiplicity-two realization
gamma_j=b_j tensor I_2 in rank 2^(j+1), using BK3.6.14. Denote the
full transferred character by Theta_j. BK3.6.13(ii) preserves the
entire beta-determinant character on U_(K_j)^1 at level m0=0.
Hence for every literal scalar u in U_F^1,

    Theta_j(u I)=chi_j(det_(K_j)(u I_2))
                =chi_j(u^2)=theta_j(u^2)=1.                    (9)

This statement includes nonminimal b_j. The determinant exponent
two is essential and has not been suppressed.

Now set beta=b_(j+1), gamma=gamma_j, delta=delta_j, r=r_j,
m=floor(r/2), and

    D=H^(m+1)(beta)=H^(m+1)(gamma).

The equality and endpoint m were verified in Section3. BK3.3.18
constructs the actual recursive simple character

    vartheta=(Theta_j restricted to D)*psi_delta.

For u in D intersect U_F^1, equations (8) and (9) prove

    vartheta(u)=1.                                             (10)

The new field K=F[beta] is maximal and totally ramified in native
rank 2^(j+1). Its chain has K-period one, so

    D intersect U_K^1=U_K^(m+1),
    D intersect U_F^1=U_F^ceil((m+1)/2^(j+1)).

Thus (10) is exactly the compatibility required by Section4.
Extend vartheta|U_K^(m+1) to chi_K on U_K^1 trivial on U_F^1.
BK3.2.5 constructs the full simple character by

    theta_(j+1)(kd)=chi_K(k)*vartheta(d),
    k in U_K^1, d in D.

That proposition supplies normalization and well-definedness; its
proof is a character-extension argument and imposes no exclusion
of residue characteristic two. The new theta_(j+1) is trivial on
U_F^1. Induction proves (1) in every native rank 2^d.

More generally the character argument needs only integral base
field trace and integral traces for the native corrections. The
dyadic tower establishes their exact value one, while the odd-prime
tower of166 establishes zero.

## 7. Canonical beta extension and prescribed tame center

Let K/F be the final totally ramified degree-N parameter field and
let eta be the Heisenberg representation for the constructed theta.
The compact type group is

    J=O_K^times J^1.

Here O_K^times=U_K^1 because the residue field is F_2. Since
U_K^1 is contained in J^1, we have

    J=J^1,       J/J^1=F_2^times={1}.                           (11)

Thus the actual canonical beta extension on J equals eta; there
is no residue-character choice and no change of that extension.
It acts trivially on the central U_F^1 by (1). Equation (11) does
not identify any externally prescribed dyadic quadratic phases.

Let omega_F be any smooth quasicharacter trivial on U_F^1. Since
O_F^times=U_F^1, it is determined by its value omega_F(t).
The actual maximal type extends to K^times J. Concretely,
(K^times J)/J is infinite cyclic, generated by a K-uniformizer.
An intertwiner for its conjugation action on eta gives an extension
Lambda_0. Denote its central character by omega_0.

Choose a complex scalar s with

    s^N=omega_F(t)/omega_0(t).

Multiply Lambda_0 by the character of K^times J trivial on J and
taking the K-uniformizer to s. Because t has valuation N in K,
this changes its scalar by s^N and gives the requested central
quasicharacter on all F^times. The value at every element of J,
including the canonical beta extension, is unchanged. This does
not assume that a chosen K-uniformizer raised to N equals t.

The retained maximal-simple-type theorem now gives the actual
irreducible admissible supercuspidal pi=c-Ind_(K^times J)^GL_N(F)
Lambda. The noncompact scalar is fixed before any H5 comparison.
An incompatible immutably prescribed extension is not overwritten;
as in166, its value must be free or already compatible.

## 8. What this closes and what it does not

This closes the full-character and actual tame-central-character
construction for the explicit dyadic arithmetic tower. The
failure of trace zero at p=2 is repaired by the correct integral
trace invariant. Both the odd-level floor and the multiplicity-two
determinant transfer are accounted for explicitly.

This note does not compute J^1/H^1 or prove that it contains a
particular dyadic source packet. It does not establish a quadratic
refinement, canonical phase matching, nontrivial stabilizer action,
general transport graph, source admission, or H5. In particular,
an actual supercuspidal host with the required central character
is not asserted to be a completed realization of the original
dyadic packet without those separate proofs.

## 9. Exact source checks and input pins

The following final166 files were read and reused without editing:

- `attachment166/central/TRACE_ZERO_CHARACTER_INDUCTION166.md`
  SHA256 `99cb6e80c419e0bf7325e2b2b3fbaba1391903448a3b6a0c4cd9f3944ed406a1`.
- `attachment166/tower/TRACE_ZERO_AS_TOWER166.md`
  SHA256 `49a18fb733f0209b3e38118f5132839a060961edd0bdc0211e1f7b441a4e5653`.
- `attachment166/tower/RECURSIVE_TOWER166.md`
  SHA256 `6f39a077df18eb03f9fab2b6e426529dbe14cf4f7e1cfce95ddb0fcd187d7b33`.
- `attachment166/audit/TOWER_CENTRAL_REVIEW166.md`
  SHA256 `4bc71dd050ddb321a253105c8a4ee7a86185af255532d5605caa7a9de383e26b`.

Primary retained source: Bushnell–Kutzko, *The admissible dual of
GL(N) via compact open subgroups*, text SHA256
`d69db0827256707a34cd2562af68b9de11fc889ab3f43535ec47b620d58ca9c8`.
The current dyadic check reread definitions3.1.7–8 and
Proposition3.1.9(ii) (printed90–91), Definition3.2.1 and
Proposition3.2.5 (printed98–100), and Corollary3.3.18
(printed112–113). Their level thresholds are floor(r/2)+1 or
floor(r/2), as used above, and their statements do not exclude p=2.
The transfer's preservation of the full beta-determinant character
is BK3.6.13(ii), with existence Theorem3.6.14 (printed136–137),
already directly checked in166 and reread for this application.

The character-extension and correction proofs use neither division
by two nor an odd-order averaging argument. The exact dyadic trace
calculation and the borderline correction-character check are
given in Sections2–3. No new publication lookup, external
arithmetic-induction/descent constructor, or inverse LLC is used.
