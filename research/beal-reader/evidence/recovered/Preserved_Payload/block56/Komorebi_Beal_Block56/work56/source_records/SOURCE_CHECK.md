# Source authentication and translation

Checked 19 September 2026. This is a targeted dependency check, not a novelty
survey. The archive does not redistribute source PDFs or screenshots.

## James S. Milne, Abelian Varieties

Version 2.0, title page March 16, 2008. Author-hosted source:
https://www.jmilne.org/math/CourseNotes/AV.pdf

The title and version were checked. Actual page images were inspected:

- II.1.1, printed page 75, zero-based PDF page 80: Frobenius cardinality
  formula and absolute values of its eigenvalues.
- III.11.1, printed page 118, zero-based PDF page 123: the curve point count
  in terms of the eigenvalues of its Jacobian's Frobenius. The start of the
  section on printed page117 was also inspected.

Dictionary: the curve is the inherited complete smooth sextic model of genus
two. Counts N1,N2 determine the first two coefficients by Newton identities.
The abelian variety is the local unramified twist of its Jacobian over F_Q.
The four-dimensional action is the restriction of scalars of the given
rank-two RM action. That last Frey/RM identification is an inherited input,
not a new result proved by Milne's general point-count theorem.

The implementation independently verifies the two local twist signs from
3(5-sqrt5)/2, and the source-model identification of this radicand remains
pinned to Block52's input contract.

## James S. Milne, Class Field Theory

Version 4.03, 6 August 2020. Author-hosted source:
https://www.jmilne.org/math/CourseNotes/CFT.pdf

Theorem V.1.7, printed150 (PDF index158), and Theorems V.3.5-V.3.6 with
Remark V.3.8, printed158 (index166), were inspected as actual page images.
They supply the residue/ray/class sequence, reciprocity, and conductor
interpretation used to interpret the old 97/293 ray line. The local toric
matrix controls are direct algebra, not assertions from this source.

The new good-Frobenius exclusions themselves do not require a fresh
class-field-theory computation or identification of an abstract character
with the actual diagonal.

## Retrieval and limits

Direct opening and PDF rendering succeeded. Three text-find calls on the
AV PDF returned no match/internal-error results despite the section existing.
The known printed-page locators were then checked by direct screenshots.
No unverified search snippet supplied a theorem. No local PDF hash or full
PDF cache is claimed. No novelty classification is claimed.

All 13 project-specific inherited leaves are separately hashed in
INHERITED_INPUT_HASHES.json. Hash equality pins ancestry, not mathematical
validity. The upstream Frey geometry and global precision theorem remain
unformalized inherited hypotheses with their original review boundaries.
