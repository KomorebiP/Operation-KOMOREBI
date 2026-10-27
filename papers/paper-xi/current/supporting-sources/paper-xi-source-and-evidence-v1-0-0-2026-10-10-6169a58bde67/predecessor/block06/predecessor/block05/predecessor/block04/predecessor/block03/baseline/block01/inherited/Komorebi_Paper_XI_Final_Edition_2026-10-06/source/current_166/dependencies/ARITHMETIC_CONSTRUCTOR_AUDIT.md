# Source-defined arithmetic candidate by cyclic induction and tame descent

## Verdict

There is a valid published arithmetic-functor constructor for the original
rank-nine wild-irreducible source. Applied as specified below, it yields an
actual supercuspidal representation pi of GL_9(F) with

    Swan(pi)=24,
    a(pi)=33,
    no nontrivial unramified self-twist,
    a(pi x pi^vee)=232,
    omega_pi = det(rho) under the declared reciprocity convention.

The construction is cyclic automorphic induction after an unramified
degree-four splitting extension, followed by inverse algebraic tame lifting
with prescribed central character. Its invariant assertions are exact
published theorems, not inferred from bounded tests or from choosing an
inverse local-Langlands image.

This is a **substantial additional classical construction input**. It does
not follow from rank-one class field theory, finite Heisenberg uniqueness,
and Bushnell--Kutzko type existence alone. In particular, automorphic
induction, independence of its cyclic-tower presentation, and algebraic tame
descent must be acknowledged. It is not a new independent Komorebi proof of
that constructor.

The source-to-automorphic candidate was already contemplated in Block128.
The useful next implication is whether the displayed invariants force a
type profile permitting the original packet attachment. That implication
is a separate proof obligation; this audit does not assume it.

The original same-candidate H5 remains exactly the original conditional
premise. No new epsilon-factor assumption is introduced, and no complete
H5 verification is asserted for this candidate.

## 1. Precise primary-source dependencies

All primary sources below were read from their authorized project-local
text copies. The provenance table in SOURCE_PINS.json pins those actual
bytes.

| Source and locator | Exact input used |
| --- | --- |
| Bushnell--Henniart, *Local tame lifting for GL(n) II: wildly ramified supercuspidals*, Asterisque 254 (1999), Section 1.1, printed p.13 | Definition of A_wr: rank p^m supercuspidals with no nontrivial unramified self-twist, equivalently totally wildly ramified maximal parameter field of full degree. |
| Same, Theorem 1.3(i),(ii),(iii),(iv),(vi),(vii),(viii), printed pp.14--15 | Algebraic tame lifting on A_wr, naturality and transitivity, twisting and central-character rules, exact descent criterion, and descent fibre. This algebraic theorem works in positive characteristic. |
| Same, Theorem 1.7(ii), printed p.18 | Transformation of the self-pair conductor exponent under tame lift. For an unramified extension, the exponent is unchanged. |
| Same, Section 2.3, printed pp.23--26 | Constructor pi_m on wild-inertia-irreducible rank-p^m Weil representations: cyclic automorphic induction over a tame splitting field, followed by algebraic tame descent. The proof includes tower-independent cpi and descent. |
| Same, Theorem 2.3(iii),(iv),(v),(vii), printed p.23 | Compatibility with contragredience, determinant/central character, standard epsilon functions, and pair L-functions/conductor exponents. |
| Same, Introduction, printed pp.2--3 | Explicit limitation: the paper does not prove that its pi_m preserves complete pair epsilon functions; this must not be turned into an H5 certificate. |
| Bushnell--Henniart, *To an effective local Langlands Correspondence*, arXiv:1103.5316v2, printed p.8, Note on characteristic, and bibliography entries [3],[4],[30] | Explicit extension of their earlier characteristic-zero-restricted results to positive characteristic using Henniart--Lemaire. Entries [3],[4] identify the earlier 1996/1999 tame-lifting papers. Only this characteristic extension is used from this source here. |
| Henniart--Lemaire, *Changement de base et induction automorphe pour GL_n en caracteristique non nulle*, Mem. SMF 124 (2011), III.1.1--1.2, printed pp.137--138 | Cyclic local automorphic induction in characteristic p, with no restriction that the cyclic degree be prime to p. The arithmetic construction precedes its later LLC comparison. |
| Same, III.2.6 and remarks, printed pp.142--143 | Character-transfer definition, uniqueness, contragredience, and central-character formula for cyclic induction. |
| Same, III.3.3, III.3.6, III.3.7, III.3.8, printed pp.144--149 | Twisting, existence for essentially square-integrable input, pair conductor formula, uniqueness of the inducing Galois orbit, and the supercuspidality criterion. |

A characteristic-zero-only citation of BH1999 Section 2.3 would be
insufficient here. The later authors' explicit extension statement and
HL2011 are essential to the present F_3((t)) application.

Conversely, the main construction in *To an effective local Langlands
Correspondence* treats the totally wild correspondence as already known.
Its abstract must not be used as a fresh constructor for the current
totally wild rank-nine input. The relevant constructor here is the older
BH1999 arithmetic induction-and-descent construction, extended in
characteristic by the cited later work.

## 2. Exact source input and its inducing character

Take F=F_3((t)) and the retained rank-nine source rho=A_1 tensor A_2 from
Block127/161. Its wild restriction is irreducible, its Swan conductor is24,
and its Artin conductor is33. The retained adjoint calculation gives

    a(End rho)=232.

For the finite-normalized source displayed in Block128, write A=t^-1 and

    x^9+x=A,
    z^9+z=A^2,
    gamma_1^3-gamma_1=x^4,
    gamma_2^3-gamma_2=z^4.

The Frobenius-stable graph polarization gives

    y=z-x-x^3,
    y^9+y=A^2-A-A^3,
    M=F(y).

The field M/F is totally ramified of degree nine. Its normal closure is
split by K=F_81((t)); the extension M_K/K is elementary abelian of degree
nine. Its different exponent is24. The source character is explicitly
specified in the retained proof by

    C=y^4+A(y+y^3)-A^2,
    xi=nu_-1 tensor AS_positive-Weil(C),
    rho = Ind_{W_M}^{W_F} xi.

In an explicit uniformizer varpi of M, the complete AS class reduces to
varpi^-8, including its constant term, so the character has conductor9
over M. The full xi, including its unramified factor, is the constructor's
input. It is not replaced by the pole order8 or by a deep additive
linearization.

The scalar -1 belongs to the specific finite-normalized source in that
Block128 display. If the original immutable Weil input has another
unramified normalization, carry that exact factor through restriction,
induction and descent. No numerical Frobenius scalar should be inferred
from the break data alone. The general BH construction applies to the
actual given rho and does not require arbitrarily changing that scalar.

The assertion that M/F itself is a cyclic 3+3 tower is false: its normal
closure group is (C_3)^2 semidirect C_4, and the order-four action on the
two-dimensional F_3 quotient has no invariant line. There is no cubic
intermediate field over F.

## 3. The cyclic tower and its genuine automorphic induction

Over K choose a nonzero a satisfying a^9+a=0 and i in F_9 with i^2=-1.
Set

    B=A^2-A-A^3,
    r=(y^3-a^2 y)/(i a^3),
    s=y/a.

Then the retained exact equations are

    r^3-r=B/(i a),
    s^3-s=i r.

Thus K subset K_1=K(r) subset M_K=K(r,s) is a tower of cyclic degree-three
extensions. Both are totally ramified. Let xi_K be the restriction of the
complete source character xi to W_{M_K}, translated into a character of
M_K^times by rank-one local class field theory with the declared geometric
reciprocity convention.

Define actual automorphic representations by the HL2011 cyclic induction
operation:

    Sigma = AI_{M_K/K_1}(xi_K),
    Pi_K = AI_{K_1/K}(Sigma).

This is a mathematical representation constructor characterized by the
source's character-transfer identities. It is not an evaluated finite
matrix algorithm, and is not defined by taking an inverse LLC image.

The inputs lie in the appropriate unitary/essentially discrete classes.
The finite-normalized source character is unitary. An unramified
quasicharacter normalization can be removed and then restored by the
twisting rule when needed.

Supercuspidality can be checked without selecting an LLC image. Weil
induction of xi_K to W_K is irreducible, so the inner inducing character
has a full Gal(M_K/K_1)-orbit. HL III.3.8 then makes Sigma supercuspidal.
If a nontrivial element of Gal(K_1/K) fixed Sigma, lift it to Gal(M_K/K).
Naturality and III.3.7 would make its conjugate of xi_K equivalent to a
Gal(M_K/K_1)-conjugate, contradicting irreducibility of the original
Weil induction. Hence Sigma has a full outer Galois orbit, and Pi_K is
supercuspidal by the same III.3.8 criterion.

The same two applications of III.3.3 and III.3.7 show that an unramified
self-twist of Pi_K would give an unramified self-twist of the irreducible
source Ind_{W_{M_K}}^{W_K}xi_K. The latter has irreducible wild restriction,
so Schur's lemma makes that twist trivial. Thus Pi_K belongs to A_wr^2(K).

## 4. Descent to F and the exact additional theorem needed

To descend, Pi_K must be invariant under Gal(K/F). This cannot be inferred
merely because the degree-nine Weil source is defined over F. Frobenius
permutes the three-degree intermediate fields K_1; it need not preserve
the particular cyclic tower chosen above.

The legitimate input is the independence and naturality of the classical
cyclic-tower construction cpi used and proved in BH1999 Section2.3,
printed pp.24--25, extended to positive characteristic as recorded above.
It identifies the arithmetic outputs obtained from different tower
presentations of the same induced source. With that theorem, Pi_K is
Gal(K/F)-invariant. This dependency must not be hidden behind the word
'naturality' alone.

Let omega_F=det(rho) under local reciprocity. The central-character
formula gives

    omega_{Pi_K}=omega_F composed with N_{K/F}.

Theorem1.3(viii) now supplies at least one arithmetic tame descent pi_0
in A_wr^2(F), with I_{K/F}(pi_0)=Pi_K. Its descent fibre, by1.3(vii), is

    {pi_0 tensor(alpha composed with det): alpha trivial on N_{K/F}(K^times)}.

Since K/F is unramified of degree four, the characters alpha in this
fibre are the unramified characters of order dividing four. The two
central characters omega_F and omega_{pi_0} have ratio r satisfying
r composed with N_{K/F}=1, so r lies in this same order-four character
group. There is a unique alpha with alpha^9=r because 9 is coprime to4;
indeed exponent9 acts as exponent1 on that group. Twisting pi_0 by
alpha composed with det produces exactly one descent with central
character omega_F.

Call this representation pi_BH(rho). Its construction has fixed the actual
central character, not just a value on units. It is an independently
defined arithmetic candidate before any invocation of the original H5.

## 5. The three numerical invariants required by the profile argument

The precise shortest verification uses Theorem2.3 of BH1999, whose map
is the induction-and-descent constructor just described.

1. **Torsion one.** The theorem's codomain is A_wr^2(F). By the defining
   Proposition1.1, pi has no nontrivial unramified self-twist, and its
   maximal simple-type parameter field is totally ramified of degree9.

2. **Swan24.** Theorem2.3(v) identifies the standard epsilon functions of
   pi and rho for the same additive character. Comparing their conductor
   exponents, the dimensions and additive-character normalization terms
   are identical, so a(pi)=a(rho)=33. Thus Swan(pi)=33-9=24.

3. **Self-pair conductor232.** Theorem2.3(iii) gives
   pi_BH(rho^vee)=pi_BH(rho)^vee. Apply2.3(vii) to rho and rho^vee.
   It identifies the pair conductor exponents. The additive-character
   dimension terms again cancel on both sides, giving

       a(pi x pi^vee)=a(rho tensor rho^vee)=232.

These are consequences of published theorem conclusions, not new
unverified H5 assumptions. They apply to the same pi constructed above.

There is also a narrower direct route to the self-pair identity over K.
Iterate HL2011 III.3.6(b) through the two totally ramified cyclic stages.
Together with the ordinary Artin induction/Mackey identities and rank-one
local class field theory, this gives

    a(Pi_K x Pi_K^vee)
      = sum_{g in Gal(M_K/K)} a_{M_K}(xi_K/xi_K^g)
        + 9 d(M_K/K)
      = a(End(rho|_{W_K}))
      = 232.

BH Theorem1.7(ii), with e(K/F)=1, then retains that conductor under
unramified tame descent. This direct reduction illustrates which part
comes from pair-conductor induction rather than full correspondence.

A tempting shortcut for the standard conductor is to compare with the
iterated induction of the trivial character and divide a resulting
rank-nine pair conductor by nine. The printed III.3.6(b) applies to two
essentially discrete inputs of the same rank, whereas that shortcut has
a principal-series input. No unsupported extension of that theorem is
used here. The audited standard-conductor source is2.3(v).

## 6. What this gives, and what it does not give, for simple types

Bushnell--Kutzko classification supplies a maximal simple type in the
constructed supercuspidal pi. The torsion-one assertion makes its maximal
parameter field totally ramified of degree nine. The two conductor
equalities are available to constrain its approximation degrees and
critical levels.

This audit does not derive the proposed profile (degrees9->3->1,
levels4 and24); that is the coordinator's separate arithmetic-profile
argument. Nor does the arithmetic induction theorem itself print a
matrix beta, the full shallow values of its simple character, or an
explicit compact type of Pi_K or pi.

The direct alternative 'inducing character xi on M^times -> its derivative
as a simple-type parameter' is not a cited constructor. Block128 computed
the exact field-character linearization

    xi(1+u)=psi_M(beta_red u),  u in p_M^5,
    beta_red=(t d/dt)(varpi^-8),  v_M(beta_red)=-24.

That is only a linearization statement on the field units. It does not
prove that the required full simple character is the one specified by
beta_red, or that its compact induction realizes xi's Weil induction.
The recovered historical note reports critical exponent8 rather than the
desired4 for its tested derivative candidates, but explicitly says the
original matrix run files were lost. This report does not upgrade that
historical computation into fresh verified evidence.

Likewise, Tsushima2024 primarily supplies the explicit Galois source and
its ramification. The immediate simple-supercuspidal identification in the
related Imai--Tsushima work is the minimal m=1 situation. Our factor
parameters are m=4 and8, and the rank-nine tensor is another step again.
No direct source-to-rank-nine-type constructor follows from that m=1
identification alone.

## 7. H5 and the exact new-versus-inherited boundary

BH1999 explicitly distinguishes its arithmetic map from a completed full
pair-factor comparison. Theorem2.3(v) concerns standard epsilon functions;
part(vii) concerns pair L-functions and conductor exponents. These are not
an assertion that all pair epsilon functions agree on the original
characterizing twist family.

Therefore:

* the classical arithmetic-functor candidate exists and has the displayed
  invariants;
* the original packet/character attachment to a type in this candidate
  remains to be supplied by a separate argument;
* H5, when used, must refer to precisely this already constructed
  candidate with its retained full scalar normalization;
* importing the induction-and-descent constructor is a major external
  existence theorem, and cannot be reported as a new derivation from the
  finite packet hypotheses alone;
* the substantive prospective addition to Block128 is the profile-forcing
  and same-candidate attachment step, not rediscovery of candidate existence.

No new computation or Lean build was run for this source audit.
