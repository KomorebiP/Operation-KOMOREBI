# Development roadmap

## 1. Expand the relational grammar

Add typed graph matching, containment transfer, alignment, contact, role
matching, and object correspondence. The executor should remain exact and
bounded.

## 2. Add conditional construction

Support branches over counts, colors, holes, symmetry classes, and relation
graphs. Add bounded iteration for paths, repeated motifs, recursive frames,
and progressive fills.

## 3. Improve residual proposals

Replace broad lookup refinement with interpretable residual operators whenever
a repeated residual pattern can be described as translation, drawing,
periodicity, object substitution, or relation transfer. Retain local lookup
programs only as calibrated low-prior experts.

## 4. Learn proposal routing

Use public training data to predict a small operator-family portfolio before
program execution. Routing should reduce search cost without replacing exact
demonstration verification.

## 5. Counterfactual ambiguity tests

Perturb demonstrations by legal color permutations, translations, reflections,
and object duplication. Prefer programs whose behavior remains coherent under
transformations that preserve the inferred rule.

## 6. Hierarchical program composition

Allow a posterior over short program trees with typed intermediate states.
Cache every intermediate grid and archive its residual signature so repeated
subprograms are executed once.

## 7. Next freeze

Record source hashes, calibration hashes, parameter-holdout results, runtime
distribution, and the complete change ledger before producing another external
benchmark result.
