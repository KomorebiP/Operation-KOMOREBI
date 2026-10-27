# Core 7.4: conditional error budgets across an adaptive lineage

**Reviewed Core 0.2 · Formal companion Block 13 · Komorebi P.**

## The source contract

The source is `source/core_v0.2.tex`, lines 848–858, proposition 7.4, label `r:lineage`. It concerns the event of accepting a false claim at each actual attempt. The candidate may have been chosen using the preceding history. It does not concern the error of a candidate fixed before that history was seen.

Let μ be a probability measure on a measurable space Ω. For each natural index j, let Aⱼ be a measurable false-acceptance event and Hⱼ a sub-σ-algebra of the ambient measurable space representing information available before that attempt. The formal natural index zero denotes source attempt one. Let dⱼ be deterministic nonnegative real numbers. Assume the sequence is summable and its sum is at most D. The required validity premise is

\[
\mathbb E_\mu[1_{A_j}\mid H_j]\le d_j
\quad\mu\text{-almost surely, for every }j.
\]

Then

\[
\mu\left(\bigcup_{j\ge0}A_j\right)\le\sum_{j\ge0}d_j\le D.
\]

These are assumptions about the actual events and probability law. A stored number called confidence or a numerical budget schedule supplies none of the conditional validity evidence.

## Why conditional validity gives a marginal bound

The event indicator is measurable and bounded, hence integrable under a probability measure. Mathlib's conditional expectation preserves its integral when the conditioning measurable space is subordinate to the ambient space. Almost-sure domination by the constant dⱼ therefore gives

\[
\mu(A_j)=\int 1_{A_j}\,d\mu
=\int \mathbb E_\mu[1_{A_j}\mid H_j]\,d\mu
\le\int d_j\,d\mu=d_j.
\]

The last equality uses total mass one. There is no independence premise. The almost-sure qualifier allows conditional versions to differ on null sets without changing the conclusion.

The sub-σ-algebra hypothesis is explicit. Conditional expectation libraries provide total definitions outside their mathematical applicability conditions. An interface that dropped the hypothesis could accidentally reason about such a default value instead of the intended conditional probability.

## Why the conclusion covers countably many attempts

Finite subadditivity gives a bound for each finite collection of events. Countable subadditivity gives the full result, with the conversion between the nonnegative extended-real sum of measures and the summable real budget handled explicitly. This is equivalent to the manuscript's passage through increasing finite unions and continuity from below.

The formal theorem quantifies over all natural indices. No finite test horizon is substituted for that quantifier. A finite sequence of empty events followed by a certain error explains why inspecting a finite prefix cannot supply this result.

Summability is a material Lean hypothesis. A divergent real `tsum` has the library's default value zero. Nonnegativity alone cannot turn that value into a finite error budget. The constant-one schedule is the simplest warning: every individual event may be certain even though the nonsummable real `tsum` expression evaluates to zero. The source already requires a nonnegative series with finite total. The formal hypothesis makes that meaning explicit.

## Stopping and selection

For measurable gates Gⱼ, each retained error event Aⱼ ∩ Gⱼ is a subset of Aⱼ. Thus the union of retained errors is contained in the full error union. Measure monotonicity proves the same unconditional bound for the retained process. Choosing Gⱼ from a stopping rule is a special case. This argument needs no optional-stopping theorem. The code also proves the stronger containment bound for arbitrary gates, where the measure is an outer measure if a retained set is nonmeasurable. Separate measurability lemmas identify when the gated and stopped sets are ordinary probability events.

It also does not assert that conditioning on retention preserves the bound. A retained error event can have probability one half while, conditional on retention, its error probability is one. The denominator in that conditional statement is a different mathematical object.

A conventional history filtration may be increasing, and candidate selection should use available history in the application. Monotonicity of the family Hⱼ is not needed by the implication once each stated conditional bound holds for the actual attempt. This does not provide evidence that a real evaluator satisfies those bounds.

## Exact examples and their role

The finite examples use the inherited real-valued finite probability interface. They are exact specified laws, with no sampling or fitted confidence estimate. The measure-theoretic theorem supplies the countable result separately.

The sharp selection example has two equally likely worlds. Candidate c falsely accepts exactly in world c, so each fixed candidate has marginal error one half. History reveals the world, and the selector chooses that world's candidate. The actual selected false-acceptance event is the whole space and has probability one. The missing input is conditional validity after the selection.

Disjoint errors can attain the summed budget. Repeating the same error event gives complete dependence and a strict union bound. Zero-mass outcomes show that a null event need not be empty. A delayed certain event shows why a finite prefix does not settle the infinite lineage. Retention illustrates the difference between an unconditional stopped guarantee and a conditional error rate.

## Evidence and boundaries

The source book and all predecessor substantive Lean modules are preserved. Final compilation, API checks, transitive axiom auditing, same-kernel replay, rejection fixtures and reproducibility outcomes belong to `evidence/RELEASE_RESULTS_BLOCK13.md`, not to this mathematical explanation. Until completed current-source receipts exist, this guide is not a verification claim.

This block does not calibrate an evaluator, estimate a population error rate, establish physical-model truth, or convert deterministic proof/check counts into statistical observations. It does not provide a data-dependent budget theorem. Its schedule is deterministic and summable. Reusing pinned upstream proof objects is not an upstream source rebuild or an independent proof kernel.
