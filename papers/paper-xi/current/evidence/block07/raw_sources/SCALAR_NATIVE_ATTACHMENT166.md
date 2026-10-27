# Scalar tame phases inside the same arithmetic candidate

Evidence: ordinary proof using rank-one reciprocity, the given central character,
and elementary finite group arguments. The result constructs actual central
matrix operators through a finite cover and proves their descent. It does not
construct a new arithmetic candidate or alter a canonical beta extension.

## 1. Exact statement

Let F be a nonarchimedean local field with residue field k of cardinality q
and residue characteristic p. Put Q=q-1 and n=p^r, allowing r=0. Let
rho:W_F -> GL_n(C) be a smooth Weil representation with finite inertia image.
Use the fixed reciprocity convention identifying its determinant with a
character omega:F× -> C×.

Let C be a finite group of order prime to p, and suppose its prescribed
operators on the **full source carrier** are

    Omega_src(c)=chi(c)I_n,

where chi is a character and each Omega_src(c) belongs to the actual matrix
image rho(I_F). A finite cyclic scalar tame image is the intended example.
This hypothesis refers to actual source operators, not freely chosen phases
on an unrelated multiplicity-space factor.

Let Pi be any already constructed irreducible smooth GL_n(F) representation
with central character omega. Suppose it has its supplied actual inducing
representation Lambda on N, with F× contained in N, and an attached finite
sector E=eLambda realizing the prescribed source Heisenberg packet. Assume
the prescribed C action on the source scalar extension is trivial, and that
the honest scalar phase on the packet is the same chi above.

**Theorem.** There is a finite group C_tilde surjecting onto C and a genuine
homomorphism

    g:C_tilde -> F× I_n contained in N

whose action on Lambda and on Pi descends to the prescribed honest C action
chi(c)I. Every finite sector is stable under this action. Any center-preserving
Heisenberg attachment and its intertwiner are C-equivariant. The retained
sector-induction recovery maps recover the same Lambda and Pi equivariantly.
All actual inducing data, including the fixed canonical beta extension,
remain unchanged.

The arithmetic action is supplied by actual central matrices, with an explicit
finite-cover descent. The theorem does not assert that C itself embeds as a
matrix subgroup. Such an embedding can fail even for a genuine scalar tame
source, as Section4 shows.

## 2. Construction and proof

Let D=k×, and let Teich:D -> O_F× be the canonical multiplicative lift.
For p=2 this is still the prime-to-p root-of-unity subgroup. When q=2, D is
trivial and the argument below forces chi trivial as well.

Local reciprocity identifies the determinant image of inertia with

    det rho(I_F)=omega(O_F×).

The unit group decomposes as

    O_F× = Teich(D) times U_F¹.

The smooth character image omega(U_F¹) is a finite p-group, while
omega(Teich(D)) has order prime to p. Therefore the prime-to-p elements of
omega(O_F×) are exactly omega(Teich(D)).

For every c in C, the actual-source hypothesis implies

    chi(c)^n=det(Omega_src(c)) in det rho(I_F).

This value has order prime to p, and hence lies in omega(Teich(D)). Since
n is a p-power and chi(C) has order prime to p, the map z -> z^n permutes
chi(C). Consequently

    chi(C) is contained in omega(Teich(D)).                 (1)

In particular every source phase has order dividing Q. This conclusion
does not require selecting a splitting of the tame quotient or choosing
Frobenius representatives.

Choose an integer k_0 with n k_0 congruent to1 modulo Q. When Q=1 take
k_0=1. Define

    delta(u)=omega(Teich(u))^(k_0),       u in D.

Because exponentiation by k_0 is an automorphism on every group of roots
of unity of order dividing Q, delta(D)=omega(Teich(D)). Define the finite
fiber product

    C_tilde={(c,u) in C times D : chi(c)=delta(u)}.          (2)

It is a subgroup, and projection pr:C_tilde -> C is surjective by (1).
Define the actual central matrix homomorphism

    g(c,u)=Teich(u^(k_0)) I_n.                             (3)

Its action on Lambda and Pi is the central-character scalar

    Lambda(g(c,u))=omega(Teich(u^(k_0)))I
                  =delta(u)I=chi(c)I.                     (4)

If (1,u) belongs to ker pr, (4) is the identity. Hence the represented action
factors uniquely through C. It is exactly the prescribed source action.
Although selecting a particular matrix representative for c may require a
choice of u, the represented operator is independent of that choice. Changing
k_0 by a multiple of Q leaves (3) unchanged.

All matrices (3) are central. Their conjugation on actual groups, characters,
and scalar pushouts is therefore the identity, and their Lambda operators are
scalar. Thus they preserve every e and every sector E. The source extension
action is also the identity by hypothesis, so any attachment of those scalar
extensions is equivariant. Both honest carrier actions are chi(c)I, so every
Heisenberg intertwiner intertwines C without a new phase choice.

For the recovery step, put P={a in N:Lambda(a)eLambda(a)^(-1)=e}. Then F×
is contained in P. The retained maps

    Phi:Ind_P^N E -> Lambda,
    j:Lambda -> Ind_P^N E

are N-equivariant. They therefore commute with all actual matrices (3), and
ker pr also acts trivially on Ind_P^N E: its matrices are central elements of
P acting trivially on E, hence trivially on every induced translate. Thus the
equality descends through pr to C. The recovering idempotent, and then
compact induction to GL_n(F), preserve this equivariance. They recover the
same fixed Lambda and Pi. QED.

## 3. What this closes and what it does not

For a source packet whose marked tensor carrier is the entire rank-n source,
this proves the stabilizer step whenever its genuine tame operators are
scalar and an actual host with the correct central character and full-character
attachment is already present. There is no remaining scalar-phase equation to
solve in that situation: the determinant and central character supply it.

If only the source symplectic C action is known to be trivial, the preceding
`STABILIZER_CONTRACT166.md` proves triviality of its full scalar-extension
action for prime-to-p C. Schur then gives a scalar packet character. To apply
the present theorem one must still identify that character with the action of
actual inertia on the full source. That identification holds when the supplied
honest packet carrier is the whole source carrier. It is not automatic for a
proper multiplicity-space factor, whose omitted factor can contribute to the
determinant.

For several factors the total packet character is the product of the supplied
factor characters. The theorem matches that product on the whole attached
packet. It does not represent independent factor actions by distinct central
matrices unless those additional marked actions are separately specified and
verified.

The result uses the fixed full inducing representation Lambda. If
Lambda|J=kappa_can tensor sigma, then kappa_can and sigma are both unchanged.
Equation(4) concerns Lambda, and does not assert that kappa_can alone has the
same scalar character. A contract prescribing an action specifically on the
canonical beta extension requires that distinction to remain explicit.

No nontrivial source symplectic action is realized here. No new base candidate,
new H5 comparison, dyadic quadratic refinement, or general rank theorem is
claimed. Existing quadratic refinements are preserved because the actual
central conjugation action is the identity.

## 4. Why a direct map C into residue units is too strong

Take q=5, n=5^r, and let omega on k×=F5× be the quadratic character. Let
C=C2 and let chi be its nontrivial character. Such scalar tame behavior is
obtained by twisting a tame-trivial rank-5^r source by the quadratic tame
character, whenever such a source is supplied; the retained odd-prime
two-factor family supplies rank25 examples.

A group homomorphism a:C2 -> F5× must send its generator to1 or -1. Both
have quadratic character1. Consequently

    omega(a(c)) = chi(c)^n

is impossible at the nontrivial c, since n is odd. The proposed direct
section is not forced by genuine scalar tame source data. Reciprocity supplies
a quotient of residue units; that quotient need not split.

The construction above still works. Here k_0=1 modulo4, C_tilde is the
cyclic group of order4, and its central matrices act by the quadratic
character. The kernel of C_tilde -> C2 acts trivially on the fixed candidate,
so the actual operator action descends correctly. This example explains why
finite-cover descent is necessary rather than a cosmetic reformulation.

## Dependencies and review status

External input: rank-one local class field theory, with the same fixed
normalization used for omega=det rho; the existing actual candidate's central
character identity; the retained sector recovery theorem. The finite-cover
construction and its descent are proved above and use no local Langlands
candidate selection. No computation is needed. This version has undergone
author self-review; a parent audit is requested. No Lean run is claimed.
