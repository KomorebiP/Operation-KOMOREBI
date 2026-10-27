# v0.26 research boundary

## Closed as written

1. A square-zero ring kernel has a well-defined conjugation coefficient action induced by a representation.
2. Surjectivity of the coefficient homomorphism supplies normalized set-theoretic unit lifts. Existence of a representation lift is not assumed.
3. The actual normalized multiplication defect is a Mathlib two-cocycle.
4. Changing provisional lifts changes the defect by a two-coboundary. The absolute class is independent of that choice.
5. Vanishing of this actual H² class is necessary and sufficient for a lift of the original representation.
6. The criterion applies to invertible matrices over a surjective square-zero coefficient extension.
7. A fixed subgroup map has a stricter obstruction: the cancelling primitive must vanish on that subgroup. The explicit relative quotient gives a necessary and sufficient criterion.
8. A concrete nonzero absolute obstruction and a zero-absolute/nonzero-relative example are kernel checked.

## Crucial non-claims

- All groups in the new proofs are abstract groups. No topology, continuity of sections, continuous cochains, local Galois group, Selmer condition, or local Tate duality is constructed.
- The absolute coefficient object is the actual additive ring/matrix kernel, with its induced action over Z. It is not automatically identified with `ad(rho_bar) tensor I`, a scalar quotient, a cotangent H1 object, or a dual-Selmer space.
- The relative quotient is explicitly degree two of the kernel-of-restriction cochain complex. Its identification with a particular library relative-cohomology object or a continuous arithmetic relative complex is not proved.
- The fixed subgroup theorem preserves a specified lift exactly. A deformation functor fixing restriction only up to conjugacy needs its own gauge/relative comparison.
- This release proves a vanishing criterion, not general vanishing of H² or of the distinguished obstruction. Indeed the nonvanishing tests disprove those universal shortcuts.
- `representation_lifts_of_H2_subsingleton` is conditional on a subsingleton H². Its hypothesis is not discharged by naming it.
- A square-zero extension is one lifting step. Iteration through a thicker nilpotent ideal requires the relevant obstruction to vanish at every step, together with compatibility of the desired conditions.
- No auxiliary variables are introduced. No augmented-equation point is substituted for a point of the original problem.
- No automorphic carrier, arithmetic Taylor–Wiles theorem, Chebotarev instantiation, ramified attachment, or Strong Artin theorem follows from this release alone.

## The corrected next arrow

```text
actual continuous locally constrained representation problem
  -> continuous coefficient action and normalized defect
  -> continuous/relative degree-two class with the correct local conditions
  -> prove vanishing of that particular class in an explicit arithmetic setting
  -> a lift preserving those conditions
```

The local conditions may be stricter than ordinary fixed subgroup equality. Do not identify absolute vanishing with relative vanishing: the release proves a counterexample.

## Relationship to the audit

The audit rejected the shortcut `compatible = correctable`. This release replaces it by:

```text
compatible errors = two-cocycles
correctable errors = two-coboundaries
obstruction = their actual degree-two cohomology class
```

That repairs a missing algebraic construction. It does not discharge arithmetic obstruction vanishing. Historical novelty is not asserted: the obstruction mechanism is classical; the achievement here is an explicit Lean formalization and integration with the actual representation defects.
