# Theoretical extensions after the first edition

**Starting point: Grounded Abstraction v1.0.0.** These are research questions, not unfilled first-edition publication requirements.

## 1. State-changing noisy evidence

Replace a fixed-world likelihood model with an observation-and-transition kernel. Characterize when a compressed record supports filtering, intervention and later correction together. The first-edition static-cell theorem cannot be imported without accounting for transitions between cells and dependence created by action selection. A first tractable target is a finite hidden-state model with explicit aggregate transition/observation equalities and a small exact counterexample when one equality fails.

## 2. Economical and adaptive precision

The sufficient denominator grows with the horizon and uses a uniform likelihood floor. It is not optimal. Investigate certified variable precision, deferred rounding and query-dependent error allocations under one retained-record and working-memory contract. A new result should distinguish average error from guarantees after every attainable history. Nearly impossible evidence, support loss, and the cost of restoring discarded probability remain explicit obstacles.

## 3. Long-horizon stability with justified structure

A positive likelihood floor alone yields the conservative finite-horizon sensitivity bound, not uniform contraction of all filters. Seek additional mixing, observability or correction conditions that support time-uniform approximation. Keep this filtering question distinct from the visible-block small-gain condition. Demonstrate necessity boundaries rather than infer stability from small local residuals.

## 4. Restricted operation languages

The exact linear results quantify over all words. A finite protocol automaton can constrain the allowed sequences, changing the observable kernel and initialization problem. A next theorem could characterize the smallest protocol-relative common predictor and identify when an operation made legal by revision exposes an old hidden direction.

## 5. Model admission and prior allocation

Adding a world changes support and possibly the evidence-target partition. Old masses cannot determine how much probability a genuinely new world should receive. Study conservative admission contracts that separate transported prior mass, newly supplied evidence and unresolved allocation. No distribution should appear simply because a field has been added to a data structure.

## Method

Prioritize self-contained arguments, explicit counterexamples and finite illustrative calculations. Reuse the existing theory and avoid treating an implementation campaign as a prerequisite. An open extension does not make the first edition's proved conditional statements incomplete.
