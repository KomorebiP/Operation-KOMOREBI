# Contract for an enlarged arithmetic carrier at dyadic low rank

Evidence: a bounded contract audit and elementary conditional recovery lemmas.
This note does not prove that the proposed compact enlargement is a group,
that its induced representation is Heisenberg, or that the source markings
attach to it. Those are the arithmetic inputs to be verified by the separate
rank-two and rank-four constructions.

**Verdict:** an enlarged compact carrier is not, merely by being Heisenberg
or an equivalent type, a new instance of the original H2 quotient. It can
serve as a common assembly carrier for the already supplied H2 targets if
its actual occurrence, marked attachment, and same-candidate recovery are
proved and retained. The recovery mechanism differs from the finite sector
idempotent used when the packet lies inside the original inducing carrier.

## 1. What original H2 literally requires

Original Section10 fixes an actual maximal simple character theta, its actual
groups H_theta¹ subset J_theta¹ subset J_theta, and

    V_theta=J_theta¹/H_theta¹.

Its Heisenberg representation is the particular eta_theta containing theta.
Definition11.1 supplies an equivariant symplectic isometry from a source
envelope to that type-side quotient, together with the central character,
and at p=2 the compatible quadratic refinements and central-extension lift.
Standard Fact10.2 separately supplies the canonical beta extension of this
simple-character datum.

Consequently the following implications are invalid without more proof:

    Xi is a finite Heisenberg representation
       therefore Xi=eta_theta' for a maximal simple character theta';

    (P,Xi) is equivalent to a known arithmetic type
       therefore it has that type's J¹/H¹ or canonical beta extension.

An equivalence of generated representation categories does not identify the
particular finite group quotient in Definition11.1. If a fixed conductor and
torsion profile forces every maximal simple-character carrier in the candidate
to have dimension one or two, constructing a larger Xi in that candidate does
not refute the dimension theorem. Xi is another arithmetic carrier.

There is nevertheless an important distinction between **replacing an H2
target** and **assembling already supplied H2 targets**. The accepted sector
construction itself uses a finite sector that need not be a whole maximal
simple-character carrier. Its old actual break targets remain unchanged and
are attached to that sector. An enlarged P-carrier can play the analogous
assembly role, provided the complete dictionary and recovery below are proved.
Calling it merely an arbitrary vector space would understate that result;
calling it a new canonical maximal simple type would overstate it.

## 2. Precise conditional setup

Let G=GL_n(F), Z=F×I_n, and let the already constructed candidate be

    pi=c-Ind_N^G Lambda,

with its fixed actual extended type and fixed central character omega. Let
J be a compact open normal subgroup of N such that

    eta=Lambda|J is irreducible,       N/J is infinite cyclic.

In the proposed F2-residue, full-degree totally ramified setting, J is the
actual compact type group J¹=J, not a new group called J merely to fit this
notation. Let P be an actual compact open subgroup of G satisfying

    J subset P,          N intersect P=J.

Define the genuine finite-dimensional compact induction

    Xi=Ind_J^P eta.                                       (1)

Neither irreducibility nor Heisenberg structure of Xi is assumed to follow
from its dimension. They must be proved separately when needed.

If the known eta intertwining satisfies I_G(eta)=N, then Xi is irreducible:
the finite Mackey endomorphism formula gives

    End_P(Ind_J^P eta)=End_J(eta)=C,

because no nontrivial double coset in P lies in I_G(eta). Finite-dimensional
smooth representations of compact P factor through a finite group and are
semisimple, so scalar endomorphisms imply irreducibility. This criterion
requires its actual group and intertwining hypotheses; dimension alone is
not a substitute.

## 3. Xi occurs in the same pi, and can be an equivalent compact type

The subspace of the actual compact-induction model of pi consisting of
functions supported on NP is stable under P. Mackey restriction identifies
that subspace with

    Ind_(N intersect P)^P(Lambda|_(N intersect P))=Xi.     (2)

Thus Xi is an actual compact P-subrepresentation of the same pi, with no
change of arithmetic candidate or noncompact scalar.

Induction in stages also gives the exact G-isomorphism

    c-Ind_P^G Xi isomorphic to c-Ind_J^G eta.             (3)

If (J,eta) is already a type for a stated Bernstein block and Xi is
irreducible, then (P,Xi) detects the same irreducible representations:

    Hom_P(Xi,V) isomorphic to Hom_J(eta,V).

This is the precise equivalent-type statement that follows from (1). It
does not assert that Xi is the eta of another maximal simple character, or
attach a canonical beta extension to Xi. The known canonical extension in
Lambda remains the one originally supplied.

## 4. Exact recovery before fixing the center: a quotient

Choose u in N mapping to a generator of N/J, and retain the actual matrix
Lambda(u). Use the model

    X=c-Ind_J^G eta,
    f(jg)=eta(j)f(g),

with G acting by right translation. Define the invertible G-equivariant
shift operator

    (Tf)(g)=Lambda(u)^(-1)f(ug).                          (4)

Normality of J and the actual intertwining relation for Lambda(u) ensure
that Tf has the same J-covariance. Its normalization explicitly retains the
fixed noncompact extension; changing Lambda(u) changes the relation below.

Define

    (Qf)(g)=sum_(k in Z) Lambda(u)^(-k)f(u^k g).         (5)

The sum is finite on each argument and has the required compact support
modulo N. It is N-covariant and therefore lies in pi. It is surjective and
satisfies Q(Tf)=Q(f). Decomposing support into N/J-orbits reduces its kernel
to the elementary augmentation kernel on finitely supported sequences on Z.
That kernel consists exactly of consecutive differences. Hence

    X/(T-1)X isomorphic to pi.                           (6)

Through (3), this is a recovery of pi from the enlarged compact carrier plus
the original noncompact relation. It does not select the correct relation
from the finite Heisenberg packet alone.

In general this quotient cannot be replaced by a G-equivariant split
inclusion before central normalization. A nonzero vector of X has finite
support modulo compact J. The valuation of its determinant support is a
finite subset of Z. A scalar uniformizer z=tI_n shifts these valuations
by n; consequently X has no nonzero eigenvector for z. Every vector of
pi is such an eigenvector, with eigenvalue omega(t). Therefore no nonzero
G-map pi -> X exists. In particular (6) does not split.

This is why the Block159 sector summand projector cannot simply be quoted:
there the finite sector was inside Lambda and its stabilizer contained the
noncompact center. Here Xi is larger than Lambda and lies in pi|P, with P
compact. These are different induction problems.

## 5. After retaining the center: a finite Hecke idempotent

There is also an exact summand version once the already fixed central
character is imposed. Put J_Z=ZJ and P_Z=ZP. Assume, as in the proposed
totally ramified full-degree setting, that

    N/J_Z is finite cyclic of order ell

(here ell=n). Let Lambda_0=Lambda|J_Z. Because Xi occurs in the same pi,
its action on Z intersect P agrees with omega. It therefore extends to
P_Z by letting Z act through omega; call this Xi_omega. Induction in stages
gives

    Y=c-Ind_(P_Z)^G Xi_omega
      isomorphic to c-Ind_(J_Z)^G Lambda_0.              (7)

Using the same normalized shift (4), now on Y, one has T^ell=1. Indeed
u^ell belongs to J_Z and the J_Z covariance cancels Lambda(u)^ell.
The finite operator

    e_Lambda=(1/ell) sum_(j=0)^(ell-1) T^j               (8)

is a G-equivariant idempotent whose image is exactly the fixed pi. To see
this directly, N-covariant functions embed in J_Z-covariant functions
because N/J_Z is finite. On that embedded pi the finite version of (5)
equals ell times the identity. Its average is precisely (8), and its
image consists exactly of the N-covariant functions.

Equivalently, Ind_(J_Z)^N Lambda_0 is Lambda tensored with the regular
representation of N/J_Z. Formula(8) selects the Lambda summand. It uses
the already fixed Lambda(u), including its root choice, so it preserves
the same candidate. Other root choices select the other extensions in
this finite induction. They are not interchangeable input data.

This is a finite Hecke/induction projector after central-character
normalization. It is not the original finite image-algebra projector
onto a sector of eta. A final artifact must retain (7), (8), and the
normalization Lambda(u), rather than describing recovery merely as
“the carrier is an equivalent type.”

## 6. The exact remaining admissibility checks

For either proposed low-rank enlargement, the new proof must supply all of
the following concrete inputs:

1. **Actual compact group:** prove that the proposed P is a subgroup,
   is compact open, contains the actual J, and satisfies P intersect N=J.
   Compute [P:J] and the resulting Xi dimension.
2. **Actual carrier:** verify eta=Lambda|J, its actual intertwining if the
   irreducibility criterion is used, and the Mackey realization (2).
3. **Actual finite Heisenberg structure:** exhibit the scalar preimage in
   P and the resulting elementary abelian projective quotient. Compute its
   represented commutator and prove nondegeneracy. An irreducible carrier
   of dimension two or four need not automatically have this structure.
4. **Original attachments:** attach the unchanged supplied actual H2 break
   targets, retaining their full source character values and dyadic finite
   extension/lift/square markings. The precise transported-versus-native
   distinction remains the one proved in DYADIC_MARKINGS167.md.
5. **Recovery data:** retain the actual Lambda, central character and
   noncompact generator normalization, and prove the isomorphisms and
   quotient/idempotent above for those exact groups.

When these are supplied, the result is stronger than occurrence of an
unrelated finite vector space: it is a marked arithmetic carrier in the
same candidate, equivalent through explicit induction and recovering that
candidate exactly. For C={1} and one vertex, it can repair the failed
low-rank **assembly-carrier** realization under the retained scalar-pushout
contract. The original H2 targets remain their original simple-character
quotients; they are not renamed Xi.

If the intended target instead requires the source packet itself to equal
J_theta'¹/H_theta'¹ for a maximal simple character in this same candidate,
the enlargement does not solve it. The retained low-rank dimension obstruction
still applies. A separate theorem identifying Xi with such an eta would be
needed, and under the fixed obstructed profile it cannot be inferred from
type equivalence.

No H5 condition is added or discharged. If H5 is subsequently supplied, it
must concern this fixed recovered candidate. Nontrivial stabilizer actions,
canonical native quadratic comparison, and arbitrary transport graphs remain
outside this bounded argument.

## Evidence and self-review

Read directly: original Section10 and Definition11.1 in the raw manuscript;
the Block159 NONINVARIANT_SECTOR_RECONSTRUCTION159.md; current PROOF167.md
and TARGET167.md; the retained dyadic marking theorem. The Mackey, induction,
shift-quotient, and central-normalized projector arguments above are proved
conditionally for the displayed groups, rather than assumed for the proposed
congruence formula. No actual low-rank P computation or new Lean execution
is claimed in this contract note.
