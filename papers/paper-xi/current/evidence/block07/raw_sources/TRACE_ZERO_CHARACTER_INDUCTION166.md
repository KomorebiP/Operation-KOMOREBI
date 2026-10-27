# Full central-compatible characters on the explicit trace-zero tower

Parent checkpoint: Paper_XI_Base_Realization165. New arithmetic input:
`attachment166/tower/TRACE_ZERO_AS_TOWER166.md`, together with its
`RECURSIVE_TOWER166.md` defining-sequence proof. Input hashes are recorded
in `TRACE_ZERO_CHARACTER_PINS166.json`.

Evidence: ordinary proof using the explicitly constructed arithmetic
parameters and the named Bushnell–Kutzko character and transfer theorems.
No arithmetic-induction/descent constructor or inverse correspondence
is used. No Lean verification is claimed.

## 1. Statement

Let p be odd, F=F_p((t)), and

    0<h_1<...<h_d,       p not dividing any h_i,
    q_i=(p+1)h_i,        N=p^d.

Let beta_d be the actual trace-zero Artin–Schreier matrix constructor in
the named tower note. There exists an actual full simple character theta
for its maximal simple stratum such that

    theta restricted to U_F^1 is the trivial character.             (1)

Every step constructing theta is specified below: a finite abelian
character extension, the standard simple-character transfer, or the
explicit additive correction from the displayed defining sequence.
The field, order, and parameter are the actual tower ones, not an
unspecified arithmetic realization.

The actual canonical beta extension can then be completed to a maximal
extended type and supercuspidal pi with any prescribed smooth central
quasicharacter omega_F trivial on U_F^1. Its rank, Swan conductor,
torsion number and self-pair conductor remain those proved for the
same tower. The residue and noncompact extension choices must be free
or already compatible with omega_F.

For p=3, this gives full scalar-pushout attachment and same-candidate
sector recovery for any number d of the supplied cubic source planes,
with declared stabilizer C={1} and the one-vertex contract. All original
full source character values are retained in the attachment. A general
nontrivial stabilizer, transport diagram, or H5 conclusion is not part
of this statement.

## 2. The exact arithmetic inputs

For 1<=j<=d, put

    b_j=B(F,t;h_(d-j+1),...,h_d) in M_(p^j)(F),

where B is the trace-zero constructor. The tower proof gives:

1. K_j=F[b_j] is a totally ramified maximal field of degree p^j,
   normalizing the native complete period-p^j chain A_j.
2. In rank p^(j+1), gamma_j=b_j tensor I_p is a simple approximation
   to b_(j+1), at the critical level r_j=q_(d-j)>0 of b_(j+1).
   They are equivalent as strata at that level.
3. delta_j=b_(j+1)-gamma_j has grade -r_j and F-matrix trace zero.
4. At native rank p, b_1 is multiplication by alpha in the explicit
   Artin–Schreier field

       E=F(alpha),       alpha^p-alpha=t^(-q_d).

   Its actual field trace is zero, since p is odd.

For completeness, the tower's exact trace identity is

    tr_L Lift_E(C)=Tr_(E/L)(kappa^(-1) tr_E(C)),

where s=kappa*pr is its normalized trace corestriction and
Lift_E(C)=s(P0)^(-1) C P0. The recursive inner matrix has trace zero,
so this proves zero trace at every native rank. It is not merely the
automatic zero obtained by amplifying any matrix p times in
characteristic p. The literal compatibility of the truncations is
proved in Section6 of the tower note.

## 3. A finite character-extension fact

Let K/F be a finite totally ramified local extension. Suppose chi is a
smooth character of U_K^a, and chi is trivial on U_K^a intersect U_F^1.
Then chi extends to a smooth character of U_K^1 trivial on U_F^1.

Indeed, on U_K^a U_F^1 define chi_0(ku)=chi(k). Agreement on the
intersection makes this a character. Choose M>=a such that chi is
trivial on U_K^M. The character chi_0 descends to a subgroup of the
finite abelian group U_K^1/U_K^M. It extends to that whole group by
successively adjoining generators and selecting complex roots.
Pulling it back proves the assertion. This also describes an actual
finite procedure for making the extension choices.

This fact will be used only when the parameter field is maximal in
the current native matrix rank. Direct use in a nonmaximal centralizer
would require checking its determinant image and would not follow
from the scalar intersection alone.

## 4. Base character at native rank p

Let E=K_1, and let n_1=q_d be the native level of alpha. Since n_1 is
even, set a=n_1/2+1. On U_E^a the forced field-unit character is

    phi(v)=psi_F(Tr_(E/F)(alpha(v-1))).

It is trivial on U_E^a intersect U_F^1 because Tr_(E/F)(alpha)=0.
Section3 gives a full character chi_E of U_E^1 extending phi and
trivial on U_F^1. No additive-character normalization is needed for
this implication: the trace is exactly zero.

For the native minimal stratum, H^1=U_E^1 U_(A_1)^(a). Define theta_1
by chi_E on U_E^1 and by psi_alpha on U_(A_1)^a. They agree on the
intersection, so BK3.2.1 supplies the actual full simple character.
It satisfies theta_1|U_F^1=1.

## 5. Transfer the full field character before adding the next layer

Suppose theta_j has been constructed on the native rank-p^j stratum
of b_j, with theta_j|U_F^1=1. Its restriction to U_(K_j)^1 is the
full beta-determinant character chi_j, since its native centralizer
is K_j itself.

Use the standard simple-character transfer to the multiplicity-p
realization gamma_j=b_j tensor I_p in rank p^(j+1). Denote the
transferred full character by Theta_j. The exact primary result is
BK3.6.13(ii), with existence in Theorem3.6.14: transfer preserves the
full beta-determinant character on U_(K_j)^1. Consequently its
restriction to the centralizer order is chi_j composed with det_(K_j).

For every literal scalar u in U_F^1 this gives

    Theta_j(u I)=chi_j(u^p)=theta_j(u^p)=1.            (2)

The determinant exponent p is essential. We do not replace (2) by
an unsupported pullback along a scalar matrix embedding. This transfer
also deals with nonminimal b_j: beta-determinant preservation is the
general theorem, not just the minimal-character formula.

## 6. Add the actual correction and extend at maximal rank

Let r=r_j=q_(d-j), m=floor(r/2)=r/2, beta=b_(j+1), gamma=gamma_j,
and delta=beta-gamma. The actual defining sequence gives

    D=H^(m+1)(beta)=H^(m+1)(gamma).

By BK3.3.18, the character

    vartheta=Theta_j restricted to D times psi_delta

is an actual simple character at level m for beta. For every scalar
u in D intersect U_F^1, equation (2) and the exact trace identity give

    vartheta(u)=Theta_j(u)
                    psi_F((u-1)tr_F(delta))=1.        (3)

The new parameter field K=K_(j+1) is maximal and totally ramified,
and the native chain has K-period one. Thus

    U_K^1 intersect D=U_K^(m+1),
    U_F^1 intersect D=U_F^ceil((m+1)/p^(j+1)).

In particular (3) supplies the exact compatibility condition for
extending vartheta|U_K^(m+1) while imposing triviality on all U_F^1.
Apply Section3 to obtain such a character chi_K of U_K^1.

BK3.2.5, including its explicit extension formula, now constructs

    theta_(j+1)(kd)=chi_K(k) vartheta(d),
    k in U_K^1, d in D.

The proposition supplies normalization of vartheta by the field units,
well-definedness, and the full simple-character condition. This
theta_(j+1) has the claimed trivial wild center. Induction proves (1)
at the actual final rank p^d.

The proof deliberately performs every arbitrary character extension
at maximal native rank. Extending directly along amplified intermediate
centralizers M_(p^(d-j))(K_j) would introduce determinant-image
compatibility conditions. Merely knowing that their ambient matrix
trace is zero would not discharge those conditions. Transfer first,
followed by maximal-rank extension, removes that ambiguity rigorously.

## 7. Complete this same type with the prescribed tame center

Keep the actual canonical beta extension kappa of the resulting theta.
The final K/F is totally ramified of degree N, with residue rank one.
The compact type group satisfies

    J/J^1 = k_K^times = F_p^times.

On U_F^1 the beta extension acts by theta, hence trivially. For a
prescribed omega_F trivial on U_F^1, choose the residue character

    sigma=omega_F|F_p^times divided by omega_kappa|F_p^times.

Its inflation gives lambda=kappa tensor sigma with the right center
on O_F^times. Complete lambda to an actual extension Lambda_0 on
the inducing group K^times J using the retained maximal-type
completion theorem. If its center is omega_0, choose s in C^times
with

    s^N=omega_F(t)/omega_0(t).

Multiply Lambda_0 by the character of K^times J trivial on J and
taking a K-uniformizer to s. The quotient (K^times J)/J is Z, and t
has image N; this proves exact agreement of the resulting central
character with omega_F on all F^times. Canonical kappa is unchanged.

The resulting pi=c-Ind Lambda is irreducible, admissible and
supercuspidal. All these choices are made before H5. If a residue
character or noncompact extension has been immutably supplied, it
must already satisfy this compatibility; an incompatible datum is
not silently replaced.

By the exact same parameter and defining-sequence calculations,

    rank(pi)=N=p^d,
    torsion(pi)=1,
    Swan(pi)=p^(d-1)(p+1)h_d,
    a(pi^vee x pi)=p^(2d)-1
                     + sum_i (p^(2i)-p^(2i-2))h_i.

No determinant twist changes the depth. These are the proved
arithmetic tower profile formulas, not a proof of H5.

## 8. Full packet attachment in arbitrary cubic length

For p=3, retain d original supplied full characters theta_i and
their actual character groups H_i^1 normal in J_i^1, with whole
symplectic quotients V_i that are the d labelled planes. Assume the
declared stabilizer is C={1} and the diagram is one vertex. The
source balanced scalar extension has quotient V_src of dimension
2d and Heisenberg carrier dimension 3^d, the original rank.

The actual final host has total quotient dimension N-1. Its leading
nondegenerate symplectic layer has dimension

    (p-1)p^(d-1)=2*3^(d-1) >= 2d.

This follows either from the explicit defining-sequence quotient
calculation or the independently proved leading-layer lemma. Choose
a labelled symplectic embedding of the supplied V_src in that layer.
Write W=V_src perpendicular-sum V_perp. Choose a maximal isotropic
subspace L in V_perp. Its associated eigenspace in the actual
Heisenberg carrier has dimension 3^d, and L-perp/L is V_src.

Form the actual reduced scalar extension using the full host
character and its extension to the inverse image of L. Form each
original full pushout

    P_i=(C^times x J_i^1)/
               {(theta_i(h)^(-1),h): h in H_i^1}.

The center-fixing symplectic-extension isomorphism, constructed by
matched Darboux lifts and complex roots, maps their balanced product
to that actual reduced scalar extension. In particular each original
h in H_i^1 maps to the scalar theta_i(h). Every prescribed shallow
and deep source character value is retained. Source character
attachment does not claim that the original field units are the same
literal scalar matrices in the new host.

Finite Stone–von Neumann supplies the full carrier intertwiner. The
retained sector induction and recovery idempotent then recover this
same Lambda and this same pi from the source-sized sector. The
canonical beta extension, residue factor, central character, and
noncompact scalar are those actually selected in Section7. No
source-independent alternate candidate is substituted in recovery.

For the retained independent tensor family with d>=2, each factor's
wild determinant has order dividing p, because the abelianization
of its extraspecial order-p^3 image is elementary abelian. The tensor
determinant raises each factor determinant to p^(d-1), so the full
source determinant is trivial on wild inertia. Thus the source's
prescribed central quasicharacter lies in the class covered by
Section7. At d=1, matching this central conclusion requires the
source determinant itself to be trivial on wild inertia; it is not
inferred merely by taking a tensor power of length one.

For p>3, the same arithmetic host and character theorem hold, and
the same attachment works for any actually supplied valid packet
whose whole quotient and markings meet the stated symplectic
contract. A proposed source plane is not automatically a whole
rank-p type quotient: that latter quotient has dimension p-1.
No admission of all such plane sources into original H2 is inferred.

## 9. Boundary and primary-source check

This provides the previously missing full-character and actual
wild-center construction for the explicit odd-prime arithmetic
tower in every prime-power rank. The proof uses no classical
automorphic-induction/descent candidate. It retains the supplied
finite characters through the declared scalar-pushout attachments.

It does not preserve old summand matrix conjugacy classes, produce
a prescribed nontrivial stabilizer action, preserve arbitrary
numerical depth labels, handle arbitrary transport graphs, settle
the dyadic case, or prove original same-candidate H5. It therefore
does not close unrestricted claim66.

The retained primary BK text, SHA256
`d69db0827256707a34cd2562af68b9de11fc889ab3f43535ec47b620d58ca9c8`,
was directly checked at:

- Definition3.2.1 and Proposition3.2.5, printed98–100: minimal
  character condition and explicit full-character extension.
- Corollary3.3.18, printed112–113: the actual additive correction
  takes the approximation character to the next simple character.
- Condition3.6.13(ii) and Theorem3.6.14, printed136–137: transfer
  preserves the full beta-determinant character, including at m0=0.

The actual field and defining-sequence assertions are the separately
proved and independently reviewed trace-zero tower inputs, with
BK2.2.7 and the retained simple-stratum theorems. No newly downloaded
source or new novelty claim is involved.
