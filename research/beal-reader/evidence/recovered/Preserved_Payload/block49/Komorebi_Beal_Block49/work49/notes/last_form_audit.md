# Independent audit of the explicit CM realization of the last form

**Normalized claim.** Let `K=Q(sqrt(5))` and
`D: y^2=x^6+324x`. Its Jacobian has an actual CM action by
`E=Q(zeta_5)` and an RM system over `K`. That rank-two system is the
parallel-weight-two, trivial-nebentypus Hilbert system with canonical
label `2.2.5.1-2025.1-l`. Its exact conductor is `(45)`.
If a positive primitive solution of `A^3+B^5=C^7` has its rank-two
residual RM representation **directly and with the same normalization**
congruent to this form at seven, the new conclusions are `3|B`, `5∤C`
and `7|B`. Combined with the retained Block48 consequences, these give
`8778|B`, `gcd(C,210)=1`, `A,C` odd, and the stated paired residues
modulo eleven.

**Primary verdict: proved as written.** This verdict keeps the explicit
direct residual-comparison hypothesis and the retained exact modular-form
database inputs. No gap remains in the new local or representation
arguments after source-checking the CM-modularity bridge and the
a-number identity. The form is not excluded, and neither the signature
`(3,5,7)` nor Beal's conjecture is proved.

This is a fresh proof audit by a reviewer who did not write the main
note or its computation. The proof-audit and literature-check workflows
were applied; final proofreading was confined to this new audit. The
reviewer requested the missing a-number source citation, supplied it,
and re-read the resulting frozen main note. No frozen predecessor or
main proof was edited by the reviewer.

## Revision boundary

Checked on 2026-09-19. The author froze the main proof before this
review was finalized.

| Artifact | SHA-256 |
|---|---|
| `work49/notes/last_form.md` | `09027c91b714a1a38a5eff7a97af4fe6bdb5d41d0c29b0a72a767be66fbbe873` |
| `work49/notes/alt_cm_modularity_source.md` | `cac4fa51101b30b403201734c33af55a638fdbba10473a81e2047c7e695c70af` |
| `work49/computations/lastform_boundary.py` | `eec182896dfa8674c6593cd2969c03357b773b023a31f717b6194652ddb9bb00` |
| `work49/verification/lastform_run/result.json` | `af8d38af7586beaca7961e18144aa66a2ef4c74f6c7bae1843d1332ff1aac9ed` |
| `work48/source_records/candidate_lmfdb_2025_search.html` | `f46e35dee8173e93d828c82c013903f2562f6bfb55b6d4fd687bd03351d75c9a` |
| `work48/notes/bad7_torus_monodromy.md` | `8c970f3e4cf00b0fd437394b86984c6121d7ddb0bd293ffdbbcc5640c2930508` |
| `work48/notes/bad7_independent_review.md` | `1f7e4d5415dc002fb4fe3c93c6eb383d74c977f4aa6301389d309c0404c9d232` |
| `work47/notes/cartier_independent_audit.md` | `502fba199936fc28625b05cfe4ba83836fad50acad26c771414448ab010e0955` |

The script's result and manifest pin the fourteen individual Hecke pages
and the imported parser/point-count implementations. The complete
retained search page explicitly states coverage through level norm
4999 and returns fourteen forms, all at the relevant level. This review
checks application of that imported exact data; it does not claim to
recompute the Hilbert modular-form space from first principles.

## Dependency graph and obligation matrix

The proof has the following one-way dependencies:

1. The explicit order-five automorphism gives CM, polarized RM, and
   the two-dimensional compatible system over `K`.
2. The three local models give good reduction at two and exact tame
   conductors/types at three and five.
3. The checked CM character theorem and quadratic automorphic induction
   give an actual weight-two Hilbert form; the conductor and determinant
   put it in the complete level-`(45)` list.
4. An exact trace fingerprint at eleven selects `l` from that finite
   list. The other seven split-prime matches only corroborate this.
5. The actual local types imply `3|B` and `5∤C` under the direct residual
   comparison.
6. Residual simplicity upgrades the comparison to the actual full
   `F_7` modules `J[7]` and `J_D[7]`.
7. Finite-flat full faithfulness and special-fiber invariants imply
   `7∤C` and then `7|B`.

| Obligation | Status | Audit finding |
|---|---|---|
| Actual CM action and RM descent | Passed | The four nontrivial fifth-root eigenspaces give a rank-one quartic CM action; the real subalgebra is fixed over `K`. |
| Good reduction at two | Passed | Both affine and infinity charts are smooth in characteristic two. |
| Exact tame type at three | Passed | The degree-five tame model is smooth; inertia has all four nontrivial fifth roots, with no fixed vectors. |
| Residual absolute irreducibility of the RM factor at three | Passed | Arithmetic Frobenius has residue cardinality nine and exchanges the two inverse inertia eigenspaces. |
| Exact tame type at five | Passed | The degree-eight extension over `Q_5` is tame; the degree-four inertia over `K_5` has square `-I`. |
| Determinant and rank-two conductor `(45)` | Passed | The self-adjoint RM polarization gives cyclotomic determinant, and each rank-two factor has conductor exponent two at both bad primes. |
| Arithmetic modularity bridge | Passed | Exact Milne and Jacquet--Langlands passages were independently inspected; this is not inferred from point counts. |
| Complete-list fingerprint | Passed on imported exact data | Only `l` has trace polynomial `Z^2-9Z+19` at eleven; both base primes and coefficient conjugation are covered. |
| Restriction `3|B` | Passed using the retained potential-good theorem | The common geometric inertia action justifies changing Tate primes, and `S_3 × S_3` has no order-five element. |
| Restriction `5∤C` | Passed | The order-four target type cannot occur in a quadratic scalar times a unipotent residual group. |
| Actual full seven-torsion comparison | Passed | The underlying four-dimensional module is simple, so lattice independence of semisimplifications suffices here. |
| Finite-flat comparison at seven | Passed | Both finite-flat models exist; Raynaud applies with absolute ramification index `1<6`. |
| Cartier p-rank and a-number trichotomy | Passed | The actual matrix and the newly checked a-number formula distinguish all three good-reduction branches. |
| Exclusion of the named form or the Diophantine equation | Out of scope | The new necessary conditions give no global rigidity assertion. |

## Local models and exact types

The local changes of variables were re-expanded, including their
normalization and residue-field actions.

At two, completing the square recovers the original generic curve from
`y^2+x^3y=81x`. In characteristic two an affine singularity would require
simultaneously `x=0` and `x^2y=1`. The infinity chart
`v^2+v=81u^5` is smooth at both points over `u=0`. These charts give good
reduction, not merely a small discriminant valuation.

At three, `pi^5=3`, `x=pi^4 U`, `y=pi^12 V` gives
`V^2=U^6+4U` exactly, and its reduction is separable. The two points at
infinity are smooth as well. Over the maximal unramified base the
extension is tame cyclic of degree five. Its generator acts, up to
inverse convention, by `(U,V) -> (zeta_5 U,zeta_5^3 V)`.
Its characteristic polynomial on the full Tate realization is `Phi_5`.
Each RM factor pairs inverse roots, and Frobenius at the `K`-prime over
three conjugates inertia by the ninth power. It therefore interchanges
the two distinct eigenlines. The same argument survives reduction at
seven and proves absolute irreducibility over the local decomposition
group. The Swan conductor is zero, the full conductor exponent is four,
and each rank-two exponent is two.

At five, `-324=1-25*13`, so the logarithm on `1+5Z_5` supplies the
required fifth root `a`. With `lambda=zeta_5-1` and `pi^2=lambda`, the
displayed transformation produces integral coefficients because
`v_lambda(5)=4`. The reduction is `V^2=U^5-U`. Smoothness also holds
at infinity: in coordinates `t=1/U`, `W=V/U^3`, the reduction is
`W^2=t-t^5`, whose derivative with respect to `t` is a unit at zero.
Thus the loss of the degree-six leading term in the affine reduction
does not conceal an infinity singularity.

The total ramification degree is eight over `Q_5` and four over `K_5`.
After the maximal unramified base change it is tame Galois. A generator
over `K_5` has reduced action `(U,V) -> (-U,-iV)`, up to inversion;
its square is the hyperelliptic involution. The full inertia eigenvalues
are `i,-i`, each twice. All are nontrivial, so each rank-two factor has
conductor two. This gives `(3)^2(sqrt(5))^2=(45)`, whose norm is 2025.

Rosati sends the curve automorphism to its inverse. Its real subfield
is self-adjoint, so the polarized alternating pairing restricts
nondegenerately to each RM embedding and has cyclotomic multiplier.
This independently explains the asserted rank-two determinant.

## Exact modularity sources and their application

The following sources were independently opened and read as PDFs,
rather than accepted from an agent's conclusion:

* Milne, *Abelian Varieties with Complex Multiplication (for
  Pedestrians)*, [arXiv:math/9806172v1](https://arxiv.org/pdf/math/9806172),
  header dated 15 June 1998: Section 15.1, printed p.42, with its
  preceding definitions; Theorems 13.1--13.2, printed pp.30--31.
  Section 15.1 supplies compatible algebraic Hecke characters when the
  CM algebra is defined over the base. Here that base is `E`, and the
  exhibited automorphism defines the needed algebra there. The source
  is an explicit restatement of the CM theorem; this audit does not
  claim to have checked the original Shimura--Taniyama/Serre--Tate proof.
* Jacquet--Langlands, *Automorphic Forms on GL(2)*,
  [IAS author archive edition](https://publications.ias.edu/sites/default/files/automorphic-forms-on-gl2_rpl_9.pdf),
  Proposition 12.1, printed p.207, including the preceding local
  definition on pp.206--207; Lemma 5.12 and its weight calculation on
  pp.88--90. The local definition preserves determinant, local
  `L`-factors and epsilon factors. Consequently it supplies the required
  conductor compatibility as well as quadratic cuspidal induction.
  Angular exponent of absolute value one gives lowest positive weight
  two. Nonzero angular exponent also rules out norm factorization.

The index-two induction argument is valid: the nontrivial element of
`Gal(E/K)` exchanges the two CM character spaces above each real RM
embedding. The infinity exponents are a conjugate pair `0,1`. The
unitary half-norm normalization in the bridge note divides each
arithmetic Frobenius eigenvalue by the positive square root of its
residue cardinality. Cyclotomic determinant therefore becomes trivial
central character. This avoids mixing the source's reciprocity
convention with the note's arithmetic-Frobenius convention.

The stronger all-endomorphisms-defined hypothesis in the context of
Milne 13.1 is not silently substituted for the exact hypothesis of
15.1. The latter is sufficient and is the source actually needed for
the character realization here.

## Fingerprint and finite verification

The crucial point counts are `#D(F_11)=3` and `#D(F_121)=123`.
They give full polynomial
`T^4-9T^3+41T^2-99T+121`. Since both RM determinants at this good prime
are eleven, the two traces have sum nine and product nineteen. Thus
their minimal polynomial is `Z^2-9Z+19`.

The inspected exact fingerprints at either prime above eleven are:

| Form suffixes | Trace minimal polynomial |
|---|---|
| `a,f` | `Z+2` |
| `b` | `Z-4` |
| `c,d,e` | `Z` |
| `g,n` | `Z^2-18` |
| `h` | `Z^2+9Z+19` |
| `i,k` | `Z^2-8` |
| `j` | `Z^2+3Z-9` |
| `l` | `Z^2-9Z+19` |
| `m` | `Z^2-3Z-9` |

This use of one distinguishing prime is logically valid because the
preceding argument already puts the desired form in the finite complete
list. It is not a Sturm-bound substitute or a general identity test.

The reviewer ran

`python work49/computations/lastform_boundary.py --output /tmp/lastform_review_result.json`

with Python 3.12.14. It passed and reproduced the archived result
byte-for-byte. Its exact matches cover the eight displayed odd split
good primes `11,19,29,31,41,59,61,71`. The two point-count routines and
HTML parser were inspected: the monic degree-six model contributes two
points at infinity; the extension-field counts use respectively a norm
character and a square-set implementation. The result explicitly
contains two prime-above-eleven entries for each of the fourteen pages.
No missing-row or empty-fingerprint case occurs in this run.

## Inertia restrictions at three and five

The three-adic argument retains the full finite inertia group. If
`3|C`, potential multiplicativity gives only quadratic scalar and
seven-unipotent orders after reduction, excluding the target order five.
For `3∤C`, the fully covered potential-good result from
`work48/notes/reducibility_local_inertia.md` is used, including its
separately handled negative parameter-valuation case. The raw argument
and its stated source boundary were read; its earlier source audit is
retained rather than replaced by a new claim of re-proving Liu's theorem.

For potential good reduction, finite inertia on `V_7` has order prime to
seven: an element of order seven would require the degree-six
irreducible polynomial `Phi_7` over `Q_7` in dimension four. Its
order-five element can be viewed as an automorphism of the common good
special-fiber abelian variety. Faithfulness on prime-to-three Tate
modules transfers its order to `T_2`; the pro-two reduction kernel
cannot kill an element of odd order. This is a legitimate geometric
comparison of Tate primes.

When `3∤B`, the two distinct roots of
`X^2+Bbar X+2Bbar^2` define separate residue clusters of three roots.
Inertia fixes their residues and acts through `S_3 × S_3`. Its faithful
genus-two action on two-torsion cannot have order five. Hence `3|B`.

At five, the target has an actual inertia element of order four, whose
square is `-I`. In a potentially multiplicative residual system each
inertia element is `epsilon(I+N)` with `epsilon=±1` and `N^2=0`.
In characteristic seven its order divides fourteen, which excludes
four. Thus `5∤C`. The proof does not confuse equality of conductor
exponents with equality of inertial types.

## Actual seven-torsion, finite-flat uniqueness and special fibers

The lattice step passes for a specific reason, not because arbitrary
residual extensions are lattice independent. The target rank-two
residual factor is absolutely irreducible locally at three. Its trace
at eleven is outside `F_7`, since five is nonsquare modulo seven.
Thus it is not isomorphic to its coefficient-Frobenius conjugate.
Restriction of scalars to `F_7` is a simple four-dimensional module.
The stable-lattice theorem then identifies both actual full
seven-torsion semisimplifications with this simple module. A module
whose semisimplification is simple has length one and is itself simple.
This proves the actual full-module isomorphism needed at seven.

There is an independent check of target simplicity: full inertia at
three has polynomial `Phi_5`, which is irreducible over `F_7` because
`ord_5(7)=4`. Thus `J_D[7]` is already simple on this inertia subgroup.

Descent of the full isomorphism introduces no hidden finite-field
assumption. For the simple `F_7` modules in question, a nonzero
homomorphism after scalar extension implies a nonzero homomorphism
over `F_7`: the intertwiner equations are linear over `F_7` and their
solution space commutes with scalar extension. A nonzero map between
these simple modules is an isomorphism. Coefficient conjugation also
preserves their underlying `F_7` isomorphism class.

The inherited unit-Kummer construction at bad seven was checked in
the raw note, not just its audit summary. It uses period valuation
matrix `7c I_2`, replaces each period by its unit class modulo seventh
powers, and constructs a rank-`7^4` finite-flat group with kernel
`mu_7^2` and constant quotient `(Z/7)^2` after unramified splitting.
The carry-law and generic-fiber identification are consistent. This
model is not claimed to arise from good reduction of the bad-seven
Jacobian.

Raynaud, *Schémas en groupes de type (p,...,p)*, BSMF 102 (1974),
Theorem 3.3.3 and Corollary 3.3.6(1), printed p.268, were independently
rechecked in the [primary scan](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf).
The bound is `e<p-1` for finite commutative groups killed by a power of
`p`; strict henselianity is not required. Here `e=1<6`, including
after unramified base change. The full generic isomorphism therefore
extends to the finite-flat models.

For bad-seven Frey reduction, the geometric special fiber of that model
has `7^2` points; the multiplicative kernel has one geometric point in
each fiber over the constant quotient. For `D`, the Cartier matrix has
rank one and square zero, so its p-rank is zero and its seven-torsion
special fiber has one geometric point. The models cannot be isomorphic.
This excludes `7|C`.

For good-seven fibers the independently derived family matrix is
`M=[[0,A^2B],[A,0]]`, with `M^2=A^3B I_2`. The distinction between
p-rank and ordinary matrix rank is respected. To separate the two
p-rank-zero branches, the reviewer additionally checked Sarah Frei,
*The a-number of hyperelliptic curves*,
[arXiv:1703.03516v2](https://arxiv.org/pdf/1703.03516), header dated
26 June 2017, Section 2.4, printed p.3. That passage defines the
group-scheme invariant `dim Hom(alpha_p,Jac(C)[p])` and derives
`a=g-rank(Cartier)` using Verschiebung. It applies after geometric
residue-field extension. The exact-version URL failed to load, but the
inspected PDF itself has the v2 header; no result was inferred from the
failed request.

Accordingly the three branches have `(p-rank,a-number)` respectively
`(2,0)`, `(0,2)`, `(0,1)`. The boundary curve has `(0,1)`, leaving
only `A!=0,B=0` modulo seven. Thus `7|B` and `7∤AC`.

## Remaining boundary

No substantive gap remains in this note's stated implication. The
strongest safe result is an exact identification of the named form
with the explicit CM Jacobian system, and the resulting necessary
conditions under direct residual comparison. The next global obstacle
is to show that a nonzero `B` cannot realize that residual comparison.
Neither the finite fingerprint nor finitely many forced prime divisors
of `B` supplies such a rigidity theorem.

Proofreading of this audit covered the complete file. No unresolved
notation inconsistency or mathematical-token correction remains.
