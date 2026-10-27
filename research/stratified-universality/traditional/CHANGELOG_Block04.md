# Block 04 change ledger

## Version

- Previous: 1.3.0 Block 03
- Current: 1.4.0 Block 04
- Date: 29 August 2026

## Main expansion

Block 04 widens the verified digital and functional-Mahler overlap beyond pure periodicity. The semantic domain is the category of unit formal series over a prime field whose canonical mask `F(z)/F(z^p)` is rational. The new section constructs normalized mask, minimal Cartier-module, and minimal digit-automaton charts, types the ambient compiler as a directional constructor, proves all overlap laws, and establishes effective descent and invariant completeness on that domain.

## New theorem-level results

- Frobenius-radical characterization
  - `R_F(z) = F(z)^(1-p)`
  - rational canonical mask iff `F^(p-1)` is rational
  - every selected series is algebraic of degree at most `p-1`
- exact rational-collapse criterion through divisor valuations modulo `p-1`
- characteristic-two collapse of every rational mask
- existence of odd-characteristic rational-mask series that are automatic but non-C-finite
- fixed-denominator Cartier realization with explicit degree bound
- injectivity of the numerator-to-series intertwining map
- finite canonical Cartier module and reachable-observable minimality
- exact reachable numerator core
  - reachable numerator states equal the `p`-kernel
  - the reachable span equals the canonical Cartier module
  - no nontrivial behavioral quotient remains after reachability restriction
- exact state-complexity hierarchy
- equivalence of reduced mask, minimal Cartier-module, minimal DFAO, and semantic series groupoids
- contractibility of normalized fibers
- triple-overlap coherence and effective descent for objects and morphisms
- coherent descent and completeness of the rational-mask invariant package
- strict negative control showing that the rational-mask atlas is a proper subatlas of the automatic stratum

## Corrections to Block 03 language

The generic compiler-reduction language has been sharpened. For the normalized fixed-denominator Cartier compiler, injectivity shows that reachable states are already behaviorally distinct. The ambient-to-minimal bridge therefore removes unreachable states only. It does not require an additional output-equivalence quotient.

## New exact validation

The Block 04 verifier enumerates all reduced normalized masks in the declared ranges:

- `p = 2`, `deg A, deg B <= 3`
- `p = 3`, `deg A, deg B <= 2`
- `p = 5`, `deg A, deg B <= 1`

It records:

- 125 reduced masks
- 51 collapse masks
- 74 noncollapse masks
- 11,391 exact checks
- zero failures

## New figures

- `rational_mask_digital_atlas`
- `cartier_state_hierarchy`
- `rational_collapse_obstruction`
- `rational_mask_nonperiodic_examples`

The earlier `cartier_compiler_reduction` figure was corrected to show reachability restriction rather than a required behavioral quotient.

## Claim boundary

The new equivalence is restricted to the rational-mask essential image. It does not classify automatic sequences with nonrational canonical masks, unrestricted `p`-regular systems, Newton-Mahler interpolation, or the full heterogeneous registry.
