# Next work: prioritized, checkable milestones

Author: Komorebi P.

## A. Independently audit the latest universal margin argument

This is the first research priority, not merely a rerun of the integer arithmetic.

Audit resistor-only elimination with unbounded original resistor count, the retained vertex bound, all reactive endpoint placements, parallel branches, disconnected and irrelevant components, physical open/short limits, and the bounded-voltage/current formulation at positive real samples. Check that every allowed competitor is represented and that every zero-error boundary state gives a physical circuit after deletion/contraction. Check KCL elimination both ways, including all necessary bounds. Verify seven-sample rational identity at the actual degree bound.

Then inspect the exact JPT theorem and its coefficient/degree/compact-connected-component hypotheses. Recompute variables, equations/inequalities, coefficient heights, objective bounds, the choice of component carrying the minimum, and the exponent comparison. The original source locations are in `workspaces/effective_margin/docs/SOURCES.md`.

Acceptance: an explicit dependency-by-dependency audit with independent calculations and concrete rejection controls. Any gap must be retained and the theorem status corrected. An arithmetic PASS record alone is not acceptance.

## B. Obtain a useful or compactly certified base margin

A stronger certified Delta_H would immediately improve every transferred parameter. Preserve competitors of rational degrees three and four, not only the biquadratic exceptional loci in Hughes's classification. Preserve arbitrary resistor counts through a proved reduction. Never infer a distance bound from a finite optimizer sweep.

Potential paths: sound topology pruning, semialgebraic elimination, exact sign contradictions, positive-real constraints, rational SOS/ideal certificates, or interval covers over the compact model with a complete scope certificate. Retain singular and boundary states. Use the existing polynomial-refutation kernel in `workspaces/proof_carrying/` where its actual scope applies.

Acceptance: a certificate replayed without trusting the numerical search, together with an exact statement of graph coverage and the excluded budget. A scoped intermediate refutation remains a scoped result.

## C. Make known constructive families deterministic

The composition handoff identified a contained remaining task: specialize the uniform cubic family certificate to rational target points, without numerical rediscovery. Prove target binding and positivity, then combine with the explicit rational endcap inverse. This should recognize the already certified rational subfamily deterministically.

Acceptance: exact family-member certificates, rejection of out-of-box/corrupted inputs, inverse round trips, and an untouched frozen target set. Failure outside that family must remain UNKNOWN or a specifically scoped nonmembership result, never global infeasibility.

## D. Extend topology and singular-case discovery

The four-node cubic catalogs and current outer-module recursion are not universal. Investigate coupled quartic/quintic cores, multiple unknown coupled leaves, singular Jacobian strata, and genuine lower-dimensional realizations. Keep numerical generic-rank filters as heuristics unless an exact exclusion is supplied.

Acceptance: a newly covered explicitly defined family or an independently verified new witness with correctly scoped minimality, plus genuinely frozen validation distinct from inspected failures.

## E. Reconcile the unpublished reader

The historical extended reading still presents the original six-versus-seven interval. Integrate the later exact six-reactive closure and then the newer constructive/lower-bound chapters with clear evidence labels. Keep old work as history. Browser rendering, static validation and publication are separate tasks. Do not publish automatically.

## Research questions retained from brainstorming

Dissipation zeros and resistor-voltage jets may prune topologies, but cannot alone characterize all excess complexity because the written later argument preserves excess after adding a small positive resistor. Matrix block transfer must retain interface semantics and reactive costs. Tropical tree/forest coefficient limits may organize degenerations but are not currently a proved universal synthesis algorithm. Core classification and general lower-bound discovery remain open research directions, not implemented features.
