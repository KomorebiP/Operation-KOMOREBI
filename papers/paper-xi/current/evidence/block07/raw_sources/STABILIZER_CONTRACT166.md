# What the remaining stabilizer obligation actually says

Evidence: direct audit of the original statement, a new elementary reduction,
and an explicit actual-source/actual-type H1--H2 witness. Earlier artifacts are
read-only. No Lean closure, class-wide arithmetic realization, or H5 witness is
claimed.

**Primary audit verdict:** incomplete, with the smallest missing implication
being the identification of the declared finite action with the action intended
on a newly constructed common arithmetic candidate. The original text does not
define that identification by a common matrix normalizer.

## 1. Exact contract, and what is already an input

The controlling text is `closure_attempt162/inputs/original_reading.txt`:

* Proposition9.8, starting line4834: a finite group acting by automorphisms of
  the one-break Clifford datum acts symplectically on its intrinsic envelope.
* Definition11.1, lines4911--4923: a bridge supplies an equivariant isometry
  to an actual type quotient for a finite cyclic stabilizer C, with common
  central character and additional dyadic lift data.
* Proposition11.3 and Theorem11.5: once the two honest cyclic actions are
  chosen, their discrepancy is a character, killed by generator-phase equality.
* Theorem15.4 and Theorem16.2: breakwise comparisons and transports are supplied
  and tensored. They do not construct a common arithmetic host from separate
  actual type targets.

Thus H2 and H3 already settle the finite action comparison **on each supplied
break target**. They do not leave a second free stabilizer action to invent on
that same target. Their transport into a new common arithmetic type is another
assertion. Neither a map C into its matrix normalizer nor arbitrary transported
operators are identified with that assertion by the original text.

The cyclic group in Definition11.1 is not explicitly required there to have
order prime to p. The reduction below assumes that order condition; it applies
to the declared tame prime-to-p case, and cannot silently be applied to an
arbitrary finite-order Frobenius operator.

## 2. Full scalar-extension rigidity for a native tame action

Let an actual maximal simple type in GL_n(F) have a totally ramified parameter
field K/F of degree n=p^r and residue matrix rank one. Let

    W=J¹/H¹,  P=(C××J¹)/{(theta(h)^(-1),h):h in H¹},

and let eta be its irreducible Heisenberg representation. Let C be finite of
order prime to p. Suppose the C action on P fixes the scalar center and is
genuinely induced by character-preserving matrix normalizers of this type.
It is enough that it is an honest action whose action on W comes from those
normalizers. Then:

1. C acts trivially on W.
2. C acts trivially on the full scalar extension P.
3. Every honest C action Omega on eta implementing this action is
   Omega(c)=chi(c)I for one character chi of C.

**Proof.** The retained normalizer theorem in Block162 gives

    N=K×J¹,          N/(F×J¹) = Z/nZ.

The action on W factors through this cyclic p-group, so a homomorphic image
of the prime-to-p group C is trivial.

For any central extension P of the elementary abelian p-group W by C×,
the kernel of

    Aut_(C×)(P) -> Aut(W)

is naturally Hom(W,C×). Indeed, an automorphism phi fixing the quotient and
the center has phi(x)=a(x_bar)x. The scalar a is independent of the lift x
and multiplication shows that a is a character. Conversely every such
character defines an automorphism. Since W has exponent p, this kernel is a
finite elementary abelian p-group. The action of C lies in this kernel and
therefore is trivial. Finally an implementing operator commutes with the
irreducible P action, so is scalar by Schur. Honesty makes its scalar a
character. QED.

This strengthens the earlier W-level obstruction: passing to the full scalar
pushout cannot hide a nontrivial native prime-to-p action above an identity
quotient action.

## 3. Exact attachment criterion in this native setting

Suppose a marked source scalar extension P_src has a symplectic embedding
into W, and an actual finite sector of eta realizes that extension. Fix its
center-preserving attachment and a Heisenberg intertwiner T. If the host has
the native tame action of Section2, the attachment intertwines the full honest
C actions if and only if

    the source action on P_src is trivial, and
    chi_src = chi_host.

Necessity follows from equivariance and Section2. For sufficiency, trivial
extension actions make both honest carrier actions scalar by Schur, and equal
characters commute through every Heisenberg intertwiner. Any sector is stable
under the scalar host action.

If the source C action on its symplectic quotient is trivial, its action on
the full scalar extension is already trivial by the Hom-kernel argument.
For several break factors, the source character is the product of their
characters. Thus the criterion is a single scalar-character equality, rather
than a further system of symplectic placement equations.

This applies to the original C={1} fixture immediately. For nontrivial C, H3
equates source and **supplied break-target** phases. It does not equate their
product with a separately built common host's phase without a dictionary.
We do not change a fixed canonical beta extension to enforce this equality.

## 4. H2 and matching carrier dimensions do not force trivial C

Here is an actual H1--H2 witness under the literal original allowance of
separate type targets. It is not a claimed H5-admitted input, and does not
assert equal ambient matrix ranks for source and break target.

Take F=Fp((t)), p odd. The retained primary source by Tsushima, Definition3.1,
Lemmas2.6,2.8,3.9,3.12,3.14 and Corollary3.15, with R(X)=X^p and m=1,
constructs a genuine rank-p Weil representation irreducible on wild inertia.
Its wild image is extraspecial of order p³. The source envelope is a
symplectic plane, and its actual tame image C=mu_(p+1) acts by multiplication
on the roots of X^(p²)+X. This action is nontrivial and has order p+1.
The source's finite Heisenberg carrier has dimension p.

For the actual type target, take the unramified quadratic extension E/F and
the maximal order A=End_OF(OE). Let beta=t^(-2)a, where a is a unit generating
the residue extension. This is a minimal simple stratum of even level two.
The standard minimal simple-character formulas give

    J¹=U_A¹,  H¹=U_E¹ U_A²,
    W_theta=End_Fp(Fp²)/Fp²,     dim_Fp W_theta=2,
    dim eta_theta=p.

These are actual groups of a simple character, not an abstract replacement.
The type residue units act by conjugation. Write sigma(x)=x^p and decompose

    End_Fp(Fp²)=Fp² direct-sum Fp² sigma.

On the quotient represented by b sigma, conjugation by u in Fp²× is

    b -> u^(1-p)b.

Its image is the norm-one torus, of order p+1. Consequently the actual
projective residue action of Fp²×/Fp× on the two-dimensional quotient is
nontrivial. It has the same symplectic C-module as the source: identify the
cyclic groups using the displayed ratio map. The two invariant alternating
forms differ by a nonzero Fp scalar, and multiplication by lambda in Fp²×
rescales an alternating form by Norm(lambda). Surjectivity of the norm gives
an equivariant symplectic isometry.

This supplies the actual source, actual type quotient, matching degree-p
Heisenberg carriers, and nontrivial equivariant H2 action. For p=3, C has
order4 and the action is an irreducible rotation of the F3 plane.

The target here is in GL_2(F), while the source has rank p. This is permitted
by the literal breakwise definitions, which contain no relation between the
individual type targets' ambient ranks. Block161 already recorded that exact
omission. If a stricter intended contract requires every break target in a
specified GL_(p^r)(F), this example does not settle that stricter question.
We have not supplied H5 for a common candidate or certified fixed canonical
beta-extension phases for this example. It refutes only the proposed inference
that actual H2 plus equality of finite carrier dimensions forces C trivial.

## 5. Result for the next construction attempt

There are three distinct cases:

| Given contract | Exact remaining issue |
| --- | --- |
| Original C={1} fixture | No stabilizer issue remains. |
| Native prime-to-p C action in a degree-p^r totally ramified host | Source extension action must be trivial; then compare one scalar character. |
| Nontrivial source symplectic C action under the original finite contract | A common-host arithmetic action dictionary is needed. Requiring an inner normalizer makes this impossible for the preceding host; transporting external operators alone was already done in161. |

Thus “solve arbitrary nontrivial stabilizer attachment by adjusting the current
totally ramified binder” is not a viable native-inner target. That is a precise
failure of that stronger construction route, not a refutation of16.2.

## Evidence and self-review

Dependencies: original Sections9--11,15--16; Block162's source-backed normalizer
theorem; Block165's base realization contract and same-candidate attachment;
the retained published Tsushima text; the retained minimal-stratum group
formulas. The new Hom-kernel lemma and attachment criterion are ordinary
elementary proofs. The witness uses the displayed arithmetic constructor
inputs, not a numerical experiment. No independent review of this new note is
claimed in this file, and no new Lean compilation was attempted.

Self-review explicitly checked: the prime-to-p qualification, honest action
versus projective implementers, center-fixed scalar extension automorphisms,
separate target rank versus original rank, and the absence of an H5 witness.
