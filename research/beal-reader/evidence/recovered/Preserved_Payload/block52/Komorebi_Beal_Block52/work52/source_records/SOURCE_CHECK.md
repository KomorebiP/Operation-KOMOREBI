# Source check and dependency boundary

Checked19 September2026. This is a targeted source check, not a literature-
wide novelty review. No novelty claim is made for the matrix lemma, the
finite-field results, or their arithmetic combination.

## New classical source used directly

J. S. Milne, *Abelian Varieties*, Course Notes, Version2.0, March2008.
Author-hosted source:
https://www.jmilne.org/math/CourseNotes/AV.pdf

1. ChapterII, Theorem1.1, printed page75, PDF page81 (zero-index80):
   #A(F_(q^m)) is the product of1-alpha_i^m, and every complex absolute
   value of a Frobenius root alpha_i is sqrt(q).
2. ChapterII, Lemma1.3 and Remark1.4, printed pages77--78, PDF pages83--84
   (zero-index82--83): Q[pi] is a product of fields, hence reduced.
3. The introduction to ChapterII, printed page75, describes Frobenius as
   acting on points by q-th power. This agrees with the arithmetic Frobenius
   convention on the covariant Tate module used in the project.

Authentication: fetched from the author's mathematical website. The theorem
and remark were read in parsed text and their PDF pages were visually
inspected. No licensed/private source was uploaded. A source-copy hash is
not claimed here: this release records the authenticated URL and exact
locators rather than bundling a fresh copy of the full notes.

Translation: A in the source becomes the locally unramified quadratic twist
of the Frey Jacobian, dimension2. For the norm argument its four-dimensional
Q7 Tate action is restriction of scalars of the two-dimensional E-action.
At13 the source's reducedness turns (pi^2-13)^2=0 into pi^2=13; it is not
inferred from a repeated characteristic root without that input.

Status: exact statements authenticated; notation/conventions checked; the
new application is proved in the Block52 notes. The whole historical proof
of Weil's theorem is not independently reverified by this computation.

## Relevant primary comparison, not an additional unproved bridge

Amit Ophir and Ariel Weiss, *On Ribet's Lemma for GL2 modulo prime powers*,
arXiv:2111.01559v3,1 February2024:
https://arxiv.org/html/2111.01559v3

Theorem1.2 relates the stable-lattice geometry and character factorization;
Theorem1.3 supplies the opposite orientation. The project already used these
in Blocks49--51. Block52 takes the exact canonical segment from H3 and proves
its determinant consequence directly; it does not redefine n by a chosen
trace-testing modulus.

## Inherited mathematical source leaves, not newly authenticated proofs

The Frey model, RM integral representation, nu identification and local
geometry are inherited from work47--work51 inside the original archive.
The current calculations independently check the four needed nu values
using its defining quadratic radicand. They do not reprove the complete
Frey construction, all local models, level lowering, or Faltings's theorem.

The Kummer support and nonzero a_3,a_5 are exactly work50/notes/
extension_geometry.md §5, incorporating its cited natural dyadic thickness
and finite-flat inputs. The support existence and higher-cup identity remain
those of work49/notes/extension_route.md, work50/notes/extension_geometry.md,
and work51/notes/LOCAL_DEPTH_THEOREM.md. All original primary-source records
and original review limits are retained byte for byte in the predecessor.

The local units comparison used in this block is elementary: away from7,
Hensel's lemma makes seventh powering invertible on principal units, and
finite-field multiplicative groups are cyclic. The exact symbol identities
are both written down and computed. No source supplies uncomputed global
coefficient ratios.
