# Primary-source checks for v0.8.0

Checked 27 September 2026. Sources were opened directly as HTML on the official
Stacks Project site. No source copies or font files are bundled. The initial
broad web query returned irrelevant results and was discarded. Direct primary
pages supplied the exact dependencies below. This was not a historical-novelty
search and establishes no global novelty claim. Earlier reference entries are
preserved rather than being asserted freshly re-audited in their entirety.

## Derived tensor and perfect base change

- Stacks Project, Section 15.60, Tag 06XY, *Derived tensor product*:
  https://stacks.math.columbia.edu/tag/06XY
  Definition 15.60.13 and Lemma 15.60.15 give the exact derived construction and
  associativity. Bounded projective complexes are legitimate models. Used for
  C_(m,n), weighted cone transport, and the arithmetic fracture tensor step.
- Stacks Project, Section 15.76, Tag 0656, *Perfect complexes*:
  https://stacks.math.columbia.edu/tag/0656
  Definition 15.76.1 and Lemma 15.76.9: bounded finite projective models and
  preservation under derived base change. Conservativity is proved separately
  using minimal complexes, not imported from a generic base-change statement.

## Koszul structure

- Stacks Project, Section 15.29, Tag 0621, *The Koszul complex*:
  https://stacks.math.columbia.edu/tag/0621
  Definitions 15.29.1–2; Lemma 15.29.4 (invertible changes of row data),
  Lemmas 15.29.7–9 (cone constructions), Lemma 15.29.12 (tensor products).
  The source's homological grading is translated to degree -j in this cochain
  manuscript. C_R(a) has source in degree -1, target in degree 0. The finite
  Z/p^n cohomology is calculated in the new proof, not copied from the integral
  domain formula. In particular H^-1 need not vanish over a finite local ring.

## Inverse limits

- Stacks Project, Section 15.88, Tag 07KV, *Rlim of abelian groups*:
  https://stacks.math.columbia.edu/tag/07KV
  Lemma 15.88.1, especially (2), (3), and (5), supplies the product model,
  Mittag-Leffler acyclicity, and termwise computation for a complex of acyclic
  inverse systems. Lemma 15.88.9 also gives the product distinguished triangle.
  Application: specified based complexes whose termwise transition maps are
  surjective. This does not claim canonical lifting of arbitrary objects in an
  inverse system of homotopy categories. That distinction is explicitly noted
  in the source after Lemma 15.88.10 and preserved in K47.

## Localization and completion

- Stacks Project, Section 10.9, Tag 00CM, *Localization*:
  https://stacks.math.columbia.edu/tag/00CM
  Universal property, Proposition 10.9.12 (exactness on modules), and
  Lemma 10.9.14 (quotient compatibility). Used to interpret B_n[1/T] and the
  completed localized rings. The exact product-factor kernel and the fiber of
  the comparison are calculated in the manuscript.
- Stacks Project, Section 15.93, Tag 091N, *Derived Completion*:
  https://stacks.math.columbia.edu/tag/091N
  Lemma 15.93.12: when f in the defining ideal acts invertibly on a complex, its
  derived completion is zero. Used as a compatibility check on the Q_p example,
  not as a blanket effectivity theorem for arbitrary towers.

## Attribution and non-implications

CRT, arithmetic squares, integral lattice gluing, minimal complexes, derived
tensor, and nilpotent Koszul generation are classical mechanisms. The package
provides explicit proofs and interfaces for the stated Komorebi model. No claim
of a new historical theorem follows solely from this presentation. None of the
sources supplies automorphic occupancy, an arithmetic-to-automorphic functor,
or an equivalence of all the conceptual worlds in the earlier discussion.
