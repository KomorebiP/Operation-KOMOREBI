# Literature and API boundary — v0.27

## Continuous-cochain definition

Primary source checked: The Stacks Project, Section 59.58, tag 0DVG, “Tate's continuous cohomology”.

URL: https://stacks.math.columbia.edu/tag/0DVG

The source defines continuous cohomology as the cohomology of continuous inhomogeneous cochains and gives the standard differential. In degrees 1 and 2 that is precisely the differential and cocycle equation used here. Our ContinuousH2 is explicitly Z2_cont / d(C1_cont), and continuity of d on the relevant cochains is proved.

No source citation is used to skip a Lean proof obligation. No global comparison between cohomology conventions is imported from comments on the page. There are multiple continuous-cohomology conventions; the chosen one is stated explicitly.

## Separate Mathlib API

Pinned Mathlib revision: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

Inspected source: Mathlib/RepresentationTheory/Homological/ContCohomology/Basic.lean.

Source SHA-256: 894d44893c995096ce5b1b83f3cbe9d3e35b56b86bf0c6944fceaac36ee13110

That API is based on continuous homogeneous cochains in TopRep. This release does not prove an equivalence of its separate continuousCohomology 2 functor with our explicit inhomogeneous quotient. The quotient instead reuses Mathlib's actual ordinary inhomogeneous cocycles and d_12 restricted to continuous maps, with all required continuity checked.

## Averaging and novelty

The degree-two and degree-one averaging arguments are supplied as direct Lean proofs. No H2-vanishing oracle or custom axiom is used. The mathematical mechanism is standard finite-group averaging; no historical novelty claim or full novelty survey is made.

The new formal synthesis connects this averaging directly to the actual square-zero representation defect, constructed continuous sections, strict subgroup correction, and same-image compact-source lifting. That is the release's precise formal contribution, not a claimed new automorphic theorem.
