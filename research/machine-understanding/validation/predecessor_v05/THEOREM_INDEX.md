# Statement index

**Machine_Understanding_v0.5.0 · 8 October 2026**

Seventeen statements with prose proofs: eight theorems and nine propositions. Nine predecessor statement/proof pairs are unchanged. Numbering follows the canonical PDF. These counts are not priority or independent-verification claims.

## Theorem 4.1: The minimal exact reusable state

Printed page 5 · `thm:quotient`

**Assumptions.** Finite deterministic states, total operations, all finite continuations and a fixed query family.

**Conclusion.** Minimal exact behavioral quotient and refinement by every exact reusable representation.

**Boundary.** Does not identify causal use, efficient construction, or a uniquely intelligible notation.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** partition refinement versus independent pair search, register quotient and diagnostic recovery.

## Proposition 4.2: Contract expansion and supplementary information

Printed page 6 · `prop:expansion`

**Assumptions.** Same complete state space; larger action/query family; exact old representation. Attainment additionally requires each expanded behavioral class to lie inside one old representation fibre.

**Conclusion.** Lower bound on supplementary code size; matching construction under the refinement hypothesis.

**Boundary.** A redundant old coordinate can require additional update information. An old-only function cannot restore a missing distinction.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** extension information obstruction, redundant old coordinates obstruct expanded dynamics, sharp supplementary code under the refinement hypothesis.

## Proposition 5.1: The identification limit of a transcript

Printed page 7 · `prop:identification`

**Assumptions.** Equal priors, finite complete permitted transcript laws, decision based only on those transcripts.

**Conclusion.** Optimal identification accuracy equals one half of one plus total variation.

**Boundary.** Does not identify an unrestricted hidden mechanism.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** transcript identification bound.

## Proposition 5.2: Uniform controlled stochastic reuse

Printed page 8 · `prop:lumpability`

**Assumptions.** Finite Markov kernels, a surjective state map, uniform projected rows per fibre, fibre-constant current queries, policies based on reduced histories.

**Conclusion.** Exact reduced process for matched initial projected laws and admissible policies.

**Boundary.** Not an empirical certificate for a neural or physical implementation.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** controlled stochastic quotient.

## Theorem 6.1: Exact transport of reusable operations

Printed page 9 · `thm:transport`

**Assumptions.** One-step operation squares and corresponding decoders commute for all declared source states.

**Conclusion.** Every finite matched continuation and sequential exact transports are preserved.

**Boundary.** Forward transport alone supplies neither injectivity nor target-operation coverage.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** exact coordinate transport, arbitrary finite recoding preserves behavior.

## Proposition 6.3: Finite-horizon transfer budget

Printed page 10 · `prop:error`

**Assumptions.** Uniform local transfer defect; target operations and decoder are Lipschitz; fixed matched operation sequence and bounded initial discrepancy.

**Conclusion.** Explicit finite-horizon state and output error bounds.

**Boundary.** Does not cover unmodeled adaptive policy changes or errors outside the stated domain.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** approximate transport and sharp accumulation.

## Proposition 7.2: The information an exact explanation must carry

Printed page 12 · `prop:explanation`

**Assumptions.** Fixed deterministic recipient, fixed background and fixed-length artifact; exact answers to the declared finite query family.

**Conclusion.** The artifact alphabet must distinguish all required answer profiles.

**Boundary.** An information bound does not construct an efficient interpreter or establish subjective comprehension.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** explanation and common-witness capacity.

## Theorem 8.1: A common explanatory artifact under sender and recipient constraints

Printed page 14 · `thm:audience`

**Assumptions.** Finite cases, one sender-access map, matched recipient background and demand maps, designable fixed decoders.

**Conclusion.** Exact common-message feasibility is loop-free graph colorability; the chromatic number is the least alphabet size.

**Boundary.** Does not establish causal use, decoder availability or efficient decoding. Background and side channels must be charged.

**Lineage.** Added in v0.5.0.

**Companion checks.** source-access explanation graphs against direct decodability, heterogeneous recipients and shared-message obstructions.

## Proposition 9.1: Finite correction under separating evidence

Printed page 16 · `prop:queries`

**Assumptions.** Finite realizable deterministic model family, exact evidence and an available separating experiment for each inequivalent pair.

**Conclusion.** Truth is retained and an observational class is isolated within at most |V0|-1 informative observations; b-ary depth lower bound.

**Boundary.** No guarantee of model invention, sensor truth, noisy inference or cheap experiment selection.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** finite informative correction.

## Theorem 10.1: Exact finite acquisition with state-changing observations

Printed page 18 · `thm:acquisition`

**Assumptions.** Finite deterministic experiments with costs, current-state transitions and uniform admissibility; finite horizon.

**Conclusion.** Exact minimax acquisition recurrence, attained finite costs, and explicit finite-horizon infeasibility.

**Boundary.** The target is current-state knowledge unless origins are retained. State law discovery and efficient large-state planning are not supplied.

**Lineage.** Added in v0.5.0.

**Companion checks.** acquisition Bellman values versus full policy enumeration, current-state knowledge versus preserved origin information, instrument acquisition includes its physical update.

## Theorem 11.1: Correction transport and evidence reflection

Printed page 20 · `thm:correction`

**Assumptions.** Commuting model/evidence square; all candidate subsets, including those contradicted by an attainable observation.

**Conclusion.** Filter-then-translate is contained in translate-then-filter; equality uniformly iff evidence translation is injective on attainable outcomes.

**Boundary.** Restricting away inconsistent candidate sets changes the necessity question; no model discovery is supplied.

**Lineage.** Statement and proof preserved verbatim from v0.1.0.

**Companion checks.** correction and evidence transport, explicit lost correction and contradiction.

## Theorem 12.1: Exact Bayesian correction through a reporting channel

Printed page 22 · `thm:bayes`

**Assumptions.** Finite models and likelihoods, one model-independent reporting channel, positive-probability conditioning only.

**Conclusion.** All-prior posterior equality is equivalent to conditional reconstruction in the actual joint experiment and to equality under one full-support prior.

**Boundary.** Does not authenticate likelihoods, create missing models, or preserve a different model-identity mapping.

**Lineage.** Added in v0.5.0.

**Companion checks.** all-prior Bayesian sufficiency and stochastic reporting, noise, ancillary flags and repeated-readout instrument.

## Proposition 12.2: Expected posterior loss is conditional information

Printed page 23 · `prop:posterior-information`

**Assumptions.** One finite joint experiment and a fixed prior.

**Conclusion.** Expected fine/coarse posterior KL divergence equals conditional mutual information.

**Boundary.** This is a prior-averaged quantity, not a worst-case or rare-event posterior guarantee.

**Lineage.** Added in v0.5.0.

**Companion checks.** posterior information loss identity without floating logarithms.

## Proposition 13.1: A conditional stability bound with an evidence denominator

Printed page 25 · `prop:conditioning`

**Assumptions.** Two finite joint laws with total-variation error at most delta and an event positive under both.

**Conclusion.** Conditional total variation is at most min(1,delta/max(P(E),Q(E))); the bound is sharp for general joint laws.

**Boundary.** Rare events can amplify approximation. An event impossible in one model requires separate treatment.

**Lineage.** Added in v0.5.0.

**Companion checks.** conditional stability and rare-evidence counterexample.

## Proposition 13.3: A joint posterior and recipient decision certificate

Printed page 25 · `prop:decision`

**Assumptions.** A bounded total-variation posterior chain, finite common action set, common bounded losses and exact optimization by the recipient.

**Conclusion.** A regret bound and a sufficient strict-gap certificate for preserving the true optimum.

**Boundary.** Not a guarantee for unbounded losses, exact logical obligations, mismatched values or approximate optimization not separately budgeted.

**Lineage.** Added in v0.5.0.

**Companion checks.** bounded-loss recipient decision certificate.

## Theorem 14.1: Sequential preservation of noisy correction under adaptive experiments

Printed page 27 · `thm:adaptive-bayes`

**Assumptions.** Static finite model, fresh conditional likelihood draws, per-experiment factorization, report-history action selection and bounded public stopping.

**Conclusion.** Exact posterior preservation through adaptive inquiry at all positive histories.

**Boundary.** Copied evidence, hidden selection, changing latent states or undisclosed stopping require a different model.

**Lineage.** Added in v0.5.0.

**Companion checks.** sequential noisy correction under a declared adaptive policy, noise, ancillary flags and repeated-readout instrument.

## Theorem 16.1: A finite joint certificate for acquisition and explanation

Printed page 30 · `thm:joint-acquisition`

**Assumptions.** Finite deterministic experiment catalogue and depth, explicit costs and sender transcript, fixed rules for recipient backgrounds and demands.

**Conclusion.** One feasible acquisition and shared-message system exists exactly when an attainable tree meets its budget and graph-coloring bound.

**Boundary.** Finite characterization, not efficient synthesis. The reference code checks constituent constructions and explicit joint examples, not an unrestricted noisy joint optimizer.

**Lineage.** Added in v0.5.0.

**Companion checks.** joint acquisition and explanation without source reconstruction, source-access explanation graphs against direct decodability.
