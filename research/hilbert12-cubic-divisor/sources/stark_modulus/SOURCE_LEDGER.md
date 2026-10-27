# Source verification ledger

Checked 2026-10-02. This is a theorem/hypothesis check, not a systematic novelty search. Public mathematical sources only. No private document has been uploaded to an external service.

## BCG: arXiv:2311.04110v2, 30 November 2023

Bergeron, Charollois, García, *Elliptic units for complex cubic fields (On Eisenstein's Jugendtraum)*.

https://arxiv.org/html/2311.04110v2

Read the primary article's section 3.1, Theorem 3.2, section 3.3, and section 5.2. Theorem 3.2 is PROVED and gives the smoothed partial-zeta derivative as log of the squared gamma modulus. Section 5.2 specifies h_K=3, the fundamental unit, the norm-two ray generator, norm-five smoothing, and the original example at ray index five. These statements support PROOF.md (1.1), (7.1), and the comparison's normalization.

The complex gamma algebraicity/reciprocity assertion in section 2.3 is CONJECTURAL. It is not invoked. The Stark formulation in section 3.3 is the target whose three conditions are checked, not a theorem presumed true.

## Milne: Class Field Theory, version4.03, 6 August2020

https://www.jmilne.org/math/CourseNotes/CFT.pdf

Read the primary author notes, including page images of printed page249 (PDF page258), ExampleVIII.5.13, and printed pages261–262 (PDF pages270–271), VIII.10. The cubic reciprocity law is stated for relatively prime elements congruent to plus or minus one modulo3. Our J is -1mod3 and our ideal generators are normalized to 1mod3. This proves the conductor/character formula used in section3.

VIII.10 states invariance of Artin L-functions under induction. Applied to the explicit finite-group decomposition in section2, it gives (2.2). This does not assume Artin's holomorphy conjecture.

The analytic class number formula is used with h_K=3, w_K=2 and regulator R. The needed leading coefficient is written explicitly in the proof, as is zeta_Q(0)=-1/2.

## NIST DLMF

https://dlmf.nist.gov/23.10.E3
https://dlmf.nist.gov/23.6

Read the displayed sigma addition identity and sigma/theta relations. These supply the classical addition step (5.4). The quadratic corrections in the absolute Siegel function are accounted for, rather than discarded. The common multiplicative constant is fixed by the product over all six ray classes.

## Normalization and predecessor boundary

The shifted Epstein normalization is derived directly in AppendixA. It is not imported from a differently scaled Mellin transform.

The previous CM seven-torsion proof supplies the exact branch X=Omega^2/wp(1/J). The earlier unramified-cubic proof supplies E as the specified ray class field. The previous norm-five proof supplies W, its integrality, roots of unity, and the abelian radical. The load-bearing finite W identities are rechecked by two implementations here.

## Search boundary

The limited source search established that the external formulas above apply with the stated conventions. It did not classify whether this explicit Stark unit/logarithmic identification had appeared before. No priority claim is made. These results use classical monomial-character and CM mechanisms.
