# Current status: v0.7.0

Base: supplied v0.6.0 source, PDF, and full ZIP; exact hashes in `audit/base_sha256.json`.

## Results of this continuation

| ID | Statement | Outcome and scope |
|---|---|---|
| K32 | Strict semantic event realization | Written proof for pure identity-preserving adjacent exchange, strict chain functors, and actual chain-natural transformations. |
| K33 | Interaction residual | Written finite-colimit proof: iterated cofiber equals the total cofiber of a coherent square; zero iff homotopy pushout. |
| K34 | Context-independent event increments | Written proof: elementary excision is equivalent to canonical constancy across the eligible contexts of each event. |
| K35 | Principal-ideal reconstruction | Written proof: reduced excisive diagrams on J(P) are equivalent to diagrams on finite P, by restriction and finite left Kan extension. |
| K36 | Universal excisive quotient | Written proof using stable Verdier localization, with constructor-invariant thick closure of specified square residuals. May be zero. |
| K37 | Tensor-cube formula | Written finite-colimit proof in stable categories with separately exact tensor. |
| K38 | Integral gcd interaction | Written unimodular exterior-power proof for positive integer labels. Splitting is not canonical. |
| K39 | Prime-overlap kernel | Written proof in Perf(Z); positive scalar labels give a proper torsion kernel and nonzero exact localization detector. |
| K40 | Finite-signature certificate | Written reduction for all finite event posets allowed by a fixed finite scalar label/independence signature, not arbitrary grammars. |
| K41 | Matrix collapse criterion | Written proof with verified Smith forms: free/free independent cones force collapse; otherwise explicit finite prime support. |

All new results are proofs in the manuscript and self-reviewed. They have not been checked in Lean or by an independent reviewer.

## Decisive boundaries retained

1. Strict commutativity does not imply homotopy pushout/excision.
2. Context-independent increments do not identify ordered filtrations or split dependent extensions.
3. K(6,10,15) vanishes, although its three pairwise interactions do not. Highest interaction is not a substitute for checking elementary squares.
4. Two zero scalar labels, or two matrix directions with free cone summands, can force the excisive quotient to be zero.
5. The total normalization residual C(product labels) differs from the total cofiber of the full tensor cube K(labels).
6. The excisive kernel uses designated defects. They are not assumed operationally killable before quotienting.

## Executed checks

Both scripts pass. The inherited run covers 2,047 words through length 10, 82,499 states, and 168,454 edges. New tests include all 1,554 positive integer vectors of arity 1–4 with entries 1–6, all 511 two-sort words through length 8 for scalar diagrams, 4,931 independent squares, and all 121 ordered pairs of an explicit 11-matrix family. Exact integer and finite-field checks only. Detailed counts and boundaries are in JSON.

## Remaining mathematical obligations

- Generalize K32 only after supplying the additional higher coherence data for a specified weak/reindexed grammar.
- Replace scalar identity coarsenings by an actual arithmetic restriction/truncation tower and compute the resulting interaction kernel.
- K15/K17: identify a genuine arithmetic globalization defect and prove a vanishing/existence equivalence. K35 does not supply that result.
- K18: formalize the discrete core and arithmetic certificates in Lean.
- Investigate a particular Dedekind or higher-dimensional coefficient ring rather than silently extend the integral Smith argument.
- Develop another nonadditive obstruction model beyond torsor sections.

A concrete next route is a ring tower with derived extension-of-scalars coarsenings and specified endofunctors. One must compute its natural exchange maps and determine whether they are exact already or leave nontrivial square residuals. That route is not executed in this release.
