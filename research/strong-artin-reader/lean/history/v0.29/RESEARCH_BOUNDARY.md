# Research boundary — v0.29

## Closed at the stated scope
- Continuous degree-zero local gauge terms and their actual coboundaries.
- Explicit degree-two gauge quotient on the v0.28 continuous compatible pairs.
- Original continuous representation lifts with independent local kernel
  conjugacy iff its CONSTRUCTED class vanishes.
- No source discretization, local openness, or finite-order invertibility is
  imposed by that criterion.
- Continuous H1 quotients and induced global-to-local restriction.
- After an absolute primitive, local-conjugacy gluing is measured by a cokernel
  on H1 rather than strict Z1. The class is independent of that primitive.
- The H1 localization cokernel injects into the gauge degree-two quotient; its
  image is exactly the kernel of forgetting to absolute continuous H2.
- The strict-to-gauge map is surjective. Strict zero implies gauge zero.
- Kernel conjugating the prescribed local lifts preserves the class.
- A strict-nonzero/gauge-zero matrix example and an absolute-zero/gauge-nonzero
  character example are checked on the newly constructed classes.

## Non-claims and missing inputs
1. These are the explicit continuous INHOMOGENEOUS quotients. No equivalence with
   Mathlib's separate homogeneous/derived continuous-cohomology API or an arithmetic
   Selmer complex is claimed.
2. The criterion classifies vanishing but does not prove it for general data.
   The negative example rules out universal vanishing or localization surjectivity.
3. Local conditions are matching specified representations up to independent
   conjugators reducing to one. Crystalline, de Rham, inertial-type, polarization,
   and other arithmetic deformation conditions require their own comparison.
4. A zero-cochain is a single element per local group. No h-dependent conjugator
   is allowed, and the independent conjugators need not equal one global element.
5. The exact sequence has no terminal zero after absolute H2. The forgetful map
   need not be surjective.
6. Absolute H2 vanishing is still not sufficient for local-conjugacy matching.
7. This is one square-zero coefficient step, not a proved inverse-limit theorem.
8. Full quotient transport between arbitrary provisional-section Datum objects
   remains separate. Local gauge invariance here is an equality in a fixed object;
   the representation criterion gives intrinsic vanishing across section choices.
9. No new automorphic representation, determinant-bearing carrier, arithmetic
   Taylor-Wiles theorem, local Tate comparison, or Strong Artin case is supplied.
10. Standard deformation/cochain mechanisms are formalized. Historical novelty
    and universality of Komorebi Resolution Theory are not asserted.

## Corrected next consequential arrow

```
specified arithmetic local deformation condition
  -> identify its allowed local gauge/condition complex
  -> locate the distinguished obstruction in that actual complex
  -> prove vanishing or compute a definite obstruction
  -> compatible lift at the intended arithmetic coefficient level.
```

The H1 localization image is now an exact algebraic/cohomological target, rather
than an assumed surrogate. An arithmetic vanishing proof is still required.
