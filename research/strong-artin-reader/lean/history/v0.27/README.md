# Strong Artin Lean v0.27 — continuous obstruction and finite-quotient vanishing

Author: Komorebi P.

Evidence: all 11 new modules and all 10 unchanged direct dependencies freshly compiled with warnings as errors. All 72 explicitly named new constants were checked using `#print axioms`. The completed report is `RESULT.json`.

## What this release does

It fills the continuous-cochain gap left by v0.26 and proves obstruction vanishing in a stated order-invertible finite-image sector. It does not prove Strong Artin, a general arithmetic automorphy-lifting theorem, or vanishing for wild/local-Selmer constraints.

Let q:A -> B be a surjective ring map with square-zero kernel. Coefficient rings in the continuous obstruction construction carry their discrete topologies. The source G retains its given topological-group structure; it need not be discrete or finite.

1. Construct a normalized continuous provisional unit section of a continuous representation rho:G -> B^units. A representation lift is not assumed.
2. Prove continuity of the actual kernel action, normalized multiplication defect, change-of-section cochain, and correcting representation.
3. Define degree-two continuous inhomogeneous cohomology explicitly as continuous two-cocycles modulo continuous two-coboundaries, using the existing Mathlib group-cochain differential.
4. Prove continuous liftability of the ORIGINAL representation iff its constructed continuous obstruction class vanishes.
5. For a prescribed continuous lift on a clopen subgroup, construct a compatible continuous provisional section and prove the exact strict-relative lifting criterion.
6. Prove degree-two and degree-one finite-group averaging directly. If the group order is invertible on the actual coefficient kernel, the relevant cocycle has a primitive.
7. Apply averaging to a continuous finite quotient, including the actual residual image. If its order is a unit in the upper coefficient ring, a continuous lift exists through the same finite quotient, with exactly the original kernel.
8. Compactness plus discrete residual coefficients supplies finiteness of that image automatically.
9. Preserve a prescribed finite-subgroup lift under explicit group/subgroup order-invertibility hypotheses.

## Strongest positive theorem

For a compact topological source G, discrete B, a continuous representation rho:G -> B^units, and a surjective square-zero q:A -> B, suppose Nat.card(range rho) is a unit in A. Then there exists L:G -> A^units such that

```
Continuous L
q(L(g)) = rho(g) for every g
ker L = ker rho.
```

The theorem is `Komorebi.StrongArtin.SquareZeroH2.compact_source_lift_of_image_order_isUnit`.

This applies to matrix-unit rings via the supplied matrix specialization. It is an order-invertible lifting result, not a new Strong Artin theorem. In finite local coefficient rings of residue characteristic p, the familiar case is residual image of order prime to p. This does not cover the difficult p-divisible residual-image cases.

## Continuous obstruction criterion

```
Komorebi.StrongArtin.SquareZeroH2.
  continuous_lifts_iff_constructed_obstruction_zero
```

The coefficient object is the actual additive kernel of q with its induced conjugation action. No identification with an adjoint quotient, cotangent homology, or a Selmer space is assumed.

The normalized provisional section is obtained by choosing lifts on the DISCRETE residual unit group and composing with rho. Normalization is at the residual identity, not only at the identity of G. The latter pointwise modification can break continuity on a nondiscrete source.

## Prescribed subgroup

```
Komorebi.StrongArtin.SquareZeroH2.
  continuous_prescribed_subgroup_lifts_iff
```

For a clopen H <= G and a prescribed continuous tau:H -> A^units reducing to rho|H, the constructed continuous relative class vanishes iff a continuous global lift exists whose restriction is literally tau. Open subgroups of a topological group are also closed, so they are included.

This is not restriction up to conjugacy, and it does not automatically cover prescriptions on nonopen decomposition subgroups. Relative vanishing is not inferred from absolute vanishing.

## Continuous cohomology convention

`Datum.ContinuousH2` is an explicit continuous inhomogeneous degree-two cochain quotient. Continuity of the differential and the actual defect is proved. This is the cochain definition documented in Stacks tag 0DVG.

A Lean equivalence with the separately implemented homogeneous `continuousCohomology 2` functor or a derived Selmer complex is NOT supplied. No such comparison is hidden as a hypothesis in the continuous lifting criterion. The mathematical and API boundaries are recorded in `RESEARCH_BOUNDARY.md` and `LITERATURE_BOUNDARY.md`.

## Tests

- A genuinely compact, infinite, nondiscrete source, product_(n in N) C2, maps by first-coordinate sign to (Z/3)^units. The general theorem constructs a continuous lift to (Z/9)^units, and the continuous obstruction is proved zero. Compactness and nondiscreteness are themselves checked.
- EVERY C2 representation in GL2(Z/3) lifts to GL2(Z/9), by the general averaging theorem.
- The v0.26 C3 representation mod 9 with no lift mod 27 still has nonzero CONTINUOUS obstruction.
- The v0.26 C4 example still has zero absolute continuous obstruction and nonzero prescribed-subgroup continuous obstruction.

Finite enumerations use `decide`, not `native_decide`.

## Verification and ancestry

Exact base:

```
Strong_Artin_Lean_v0.26.0_Representation_H2_Obstruction_Checked.zip
6ab67721841940b82a621642dcb78a0e67e6012c1df20a9bb519ac01c8ee8bbd
```

The direct dependency sources are checked byte-for-byte against this archive. Historical/sibling branches are not silently merged.

Pinned environment:

```
Lean 4.34.0-rc2
Lean commit 6a10ac8c22beadecabdbb0919c2b50214762f91d
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
-DwarningAsError=true
```

Run from this directory:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For bounded synchronous batches:

```bash
python3 verify.py --kit /absolute/path/to/kit --max-modules 8
python3 verify.py --kit /absolute/path/to/kit --resume --max-modules 8
python3 verify.py --kit /absolute/path/to/kit --resume
```

`PARTIAL` is not `PASS`; every module and the axiom audit must finish. No network or package update is performed. The compiled Mathlib cache is reused, not rebuilt. This is a direct-closure replay, not a replay of all historical sources or an independent implementation of Lean's kernel.

## Counts

50 theorem declarations, 18 definitions, 4 abbreviations, 2 anonymous local topology instances, 965 new source lines. 72 explicitly named new constants are axiom-audited; constructor-generated constants and the two anonymous local instances are not counted as separate named audit entries. The named theorem audits transitively include the instances they use.

Final active sources contain no `sorry`, `admit`, custom `axiom`, custom `opaque`, `native_decide`, or `unsafe` declarations. Helper theorems and example statements are included in the counts. No cumulative historical theorem count is asserted.
