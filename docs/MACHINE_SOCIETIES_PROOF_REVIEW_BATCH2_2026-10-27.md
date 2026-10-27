# Machine Societies: memory, composition, and governance review

**27 October 2026 · Komorebi P. · AI-assisted sequential self-review · Batch 2**

This pass checks eight additional statement/proof pairs in the final 1.0.0 manuscript at [commit 33537b585dd3](https://github.com/KomorebiP/Operation-KOMOREBI/commit/33537b585dd30e8d755ad987865ff3a55a810d65). **Seven pass as written in their declared contexts. The memory proposition needs an explicit positive finite-index qualification for its numerical bit bound.** The issue concerns the statement's domain; the intended finite counting argument is sound.

Together with the original 15-claim review and the [previous three-claim pass](MACHINE_SOCIETIES_PROOF_REVIEW_2026-10-27.md), the records now cover **26 distinct pairs out of 62: 25 recorded as proved as written, one qualified, and 36 unreviewed**. The original 15 verdicts are inherited from that review; this pass verifies their source binding and disjoint coverage without claiming to have re-audited all 15 proofs. These counts are review coverage, not a probability of correctness or whole-book certification.

The [new review record](../manifests/machine-societies-review-batch2-2026-10-27.json) contains exact statement/proof blocks and their hashes. The [cumulative coverage index](../manifests/machine-societies-review-index.json) lists every pair, its source line, block hash, verdict, and responsible review. The manuscript SHA-256 remains `600a8100804c4c91d7cf79a4985e9312eacc19195395aee01debb240cb0a6be0`; the publication and earlier reviews are unchanged.

## Findings by claim

### Behavior alone does not identify implementation — `prop:identifiability`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 433.

**Claim context.** The two realizations have the same law of the complete transcript available under each permitted evaluation experiment. The decision uses that transcript and a common randomization rule. The accuracy bound uses equal priors.

**Decisive argument.** A common decision kernel sends equal transcript laws to equal decision laws. If q is the probability of choosing the first realization, binary accuracy is (q + 1 - q)/2 = 1/2. Abstention cannot increase unconditional accuracy.

**Dependencies.** Equal transcript laws + common decision kernel → equal output laws → equal-prior accuracy bound. All leaves are explicit assumptions or the direct argument.

**Boundary and scope checks.** Identical deterministic transcripts, randomized decisions, and constant decisions. If tests are adaptive, their complete available transcript law must satisfy the premise; equality of isolated test marginals alone is insufficient. Unequal priors and extra implementation-dependent side information are outside the accuracy claim.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** For an application, enumerate the evaluator’s available observations and show equality for its complete experiment.

### Exact finite-memory lower bound — `prop:memory`

**Primary verdict: correct only after a stated restriction.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 456.

**Claim context.** Histories are equivalent when they require identical output sequences for every permitted continuation. N counts their equivalence classes. The quotient construction additionally assumes prefix closure and a transition congruence on the admissible history domain.

**Decisive argument.** Two inequivalent histories cannot receive the same exact deterministic summary: a distinguishing continuation would require different outputs from the same summary. Thus the summary has at least N states. For positive finite N, B fixed-length bits offer at most 2^B states, so B is at least ceil(log2 N). A transition congruence makes the next class independent of the representative.

**Dependencies.** Continuation distinguishability → no collision between inequivalent histories → state-count lower bound. Add 1 ≤ N < ∞ → ordinary numerical bit bound. Add transition congruence and the declared continuation closure → well-defined quotient updates.

**Boundary and scope checks.** N = 1 gives zero required bits; powers of two and their successors explain the ceiling. For an empty history family, N = 0 and the displayed ordinary logarithm is undefined. Infinite index admits no finite exact summary, rather than a finite numerical logarithm bound. The introduction’s finite-domain convention supports the intended finite reading, but the local history-family definition does not explicitly state positive finite index.

**Remaining gap.** Make the positive finite-index restriction explicit in the source statement before counting this as an unqualified pass. This is a domain-clarity finding, not a counterexample to the intended finite-state argument.

**Next discriminating check.** In a future source edition, specify a nonempty admissible history domain with 1 ≤ N < ∞ for the numerical bound, and state that allowed updates remain in the domain of the transition congruence. Keep the general no-collision statement separate.

### Compositional one-step closure — `prop:composition`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 532.

**Claim context.** Surjections X → Z → W and transition kernels use the same control family. The two per-state, per-control total-variation errors are uniformly bounded by epsilon_1 and epsilon_2 as defined immediately before the proposition.

**Decisive argument.** Insert the pushforward of the intermediate kernel. The triangle inequality bounds the second discrepancy by epsilon_2. For the first, summing signed masses within each fibre and applying the triangle inequality shows that deterministic pushforward cannot increase half the l1 distance. This yields epsilon_1 + epsilon_2; induction adds the errors across L levels.

**Dependencies.** Finite probability laws → grouped-sum triangle inequality → pushforward nonexpansiveness; combine with the two uniform bounds → two-level estimate → finite induction.

**Boundary and scope checks.** Identity and constant maps, zero errors, L = 1, and sums exceeding one. A bound greater than one is loose but valid. The separate finite-horizon corollary also needs prop:time, which is not newly audited here. Causal intervention compatibility is not implied.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** Audit prop:time and its control assumptions before extending this review to the adjacent finite-horizon corollary.

### Simulation by an unrestricted controller — `prop:flatten`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 560.

**Claim context.** The hierarchy is finite and effectively specified, its components are computable, and the controller stores component states, messages, and scheduling variables. It executes the same transitions in the same order, with the same input and random-tape consumption.

**Decisive argument.** Initialize matching records. One scheduled local transition reads identical records and random choices and therefore produces identical successor records and external outputs. Induction preserves equality along every finite execution prefix.

**Dependencies.** Effective representation and matching initialization → identical scheduled update → record equality invariant → identical external transcript.

**Boundary and scope checks.** A single component, an empty transcript, inactive components, and randomized components coupled by the same tape. The scheduler and random-consumption convention belong to the simulated specification. No time, memory, communication, or decentralized-access bound is asserted.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** Any claimed architectural advantage must specify the resource or information restrictions on the comparison controller.

### Symmetry lock for identical deterministic agents — `prop:symmetry`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 582.

**Claim context.** The deterministic joint transition is equivariant for permutations of agent labels. The initial joint state and every supplied input are invariant under that action.

**Decisive argument.** Writing the input explicitly, equivariance gives gF(X,u) = F(gX,gu). With gX = X and gu = u, the next state is fixed by every permutation. Induct from the invariant initial state.

**Dependencies.** Equivariance + invariant state and input → invariant successor → induction in time.

**Boundary and scope checks.** Zero updates, one agent, and invariant auxiliary state. Distinct addresses, unequal observations, or asymmetric scheduling can break the input/state hypothesis. The proposition concerns deterministic trajectories, not merely a symmetric distribution of random trajectories.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** For a concrete architecture, include scheduler state, addresses, and observations when checking invariance.

### Exact governance quotient — `thm:govquot`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 737.

**Claim context.** S is finite and nonempty; the action vocabulary is finite with fixed meanings; the state map is surjective. The preceding definition makes each partial transition defined exactly on its enabled action set.

**Decisive argument.** Factorization forces equal labels, enabled sets, and successor fibres. Conversely these conditions define representative-independent quotient labels, enabled sets, and successors. Surjectivity supplies each quotient value and forces uniqueness on the declared enabled domain. Equal enabled sets and preserved successor fibres then give equal legal action and label sequences by induction.

**Dependencies.** Fibre conditions ↔ well-defined quotient data; surjectivity → uniqueness; enabled-set equality + successor compatibility → finite-trace induction.

**Boundary and scope checks.** Deadlocked states, an empty action vocabulary, a singleton state space, and the empty action sequence. Quotient transitions use the same partial-map convention: they are defined exactly for quotient-enabled actions. Treating them as arbitrary extensions outside that domain would not be the stated governance structure.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** Verify the fibre conditions for a proposed concrete institutional summary; existence of a useful nontrivial quotient is not automatic.

### Coarsest finite governance summary — `prop:govrefine`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 768.

**Claim context.** Start with blocks sharing the same institutional labels and enabled sets, then refine by the blocks of every enabled successor. The finite state/action model and transition convention are those of thm:govquot.

**Decisive argument.** Each strict refinement increases the block count, which is at most |S|. At stabilization the quotient conditions hold. Any compatible partition refines the initial partition and, inductively, every refinement. It therefore refines the stable partition, which is itself compatible and has the least number of blocks.

**Dependencies.** Finite block count → termination bound; fixed point → thm:govquot (audited in this batch); induction over competing compatible partitions → coarseness → minimum size.

**Boundary and scope checks.** An initially discrete partition takes zero strict refinements; all-deadlock blocks need only distinguish labels. The bound counts strict refinements, not the final equality test or runtime. Equal enabled sets within a block make the successor comparisons well-typed.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** If actions or protected labels change, recompute the initial partition and refinement; minimality is relative to the fixed contract.

### Preservation of finite institutional conversations — `prop:languagetrace`

**Primary verdict: proved as written.** Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 804.

**Claim context.** Definition def:language supplies equivalent admission/rejection, commuting admitted transitions, and common event records on a transition-closed declared domain. Message translation depends on the evolving source state. Composition uses matching intermediate institutions and domains.

**Decisive argument.** Equivalent definedness gives the same first rejection point. For an admitted step, transition commutation preserves the state relation and event equality preserves the record. Induction handles every finite admitted prefix. For composition, compose state maps, substitute the two transition identities, and apply the two definedness equivalences and transitivity of event equality.

**Dependencies.** The three defining equalities/definedness conditions → one-step preservation → prefix induction. Well-typed composition of two such transports → the same three conditions for the composite.

**Boundary and scope checks.** Empty conversation, rejection of the first message, and rejection after a nonempty admitted prefix. No translation after an undefined source successor is needed. Composition is on the shared declared domain: if restricted domains are used, the first state translator must land in the second’s faithful domain, or the composite must be restricted accordingly. Surjectivity and preservation of unrelated target messages are not claimed.

**Remaining gap.** None for the implication in this declared context.

**Next discriminating check.** For an implementation, exhibit the compatible domains and access to the state needed to compute the context-dependent message translation.

## Maintained clarification for the memory result

Use the numerical statement only for a nonempty family of admissible histories with a positive finite number $N$ of continuation-equivalence classes. An exact deterministic summary has at least $N$ states. If it is encoded in $B$ fixed-length bits, then

$$2^B \geq N,\qquad B\geq\lceil\log_2 N\rceil,\qquad 1\leq N<\infty.$$

For quotient updates, the admissible history domain must remain closed under the updates to which the transition congruence applies, with the source's continuation-closure assumption retained. This makes every successor class well-defined and preserves the required continuation outputs. This maintained clarification supplies the safe reading; it has not silently rewritten the archived source or PDF. Integrating it into a revised source edition remains a finalization task.

The source's finite-domain convention is relevant context. This review does not assert that its intended finite-state theorem is false, nor that an infinite-state example contradicts its controlled finite-model assumptions. It makes the positive finite-index condition locally explicit so that the logarithm formula is not exported without its domain.

**Downstream impact.** The uses of `prop:memory` in the culture discussion (source line 1367) and in the fixed-bit storage discussion (line 1414) need the valid no-collision/counting conclusion: fewer than $N$ states cannot represent $N$ distinguishable classes, and $B$ bits represent at most $2^B$ classes. Those conclusions survive this qualification. This is a check of these direct uses, not a fresh audit of every claim in those sections. No new operational storage or deployment guarantee follows.

## Obligation matrix and open work

| Obligation | Seven passing claims | Memory claim |
|---|---|---|
| Objects, quantifiers, domains | Checked in the declared contexts above | Explicit positive finite index needed for bit formula |
| Written implication chain | Passed | Counting argument passes; numerical corollary qualified |
| Boundary and equality cases | Checked individually | Empty and infinite index separated from finite formula |
| Dependency cycles | None identified | None identified |
| Load-bearing external theorem or computation | None needed | None needed |
| Empirical effectiveness or real deployment | Out of scope | Out of scope |

The coverage validator checks the exact source and review hashes, rejects duplicate reviewed labels and stale proof blocks, and separates qualified verdicts from passes. It authenticates review bookkeeping; it does not prove the mathematics. The existing CI status check runs it, and regression tests exercise count inflation and stale evidence.

No new Lean execution, numerical mathematical experiment, literature-priority assessment, or independent peer review is claimed. The public work-in-progress and authorship statement still applies. The next bounded proof targets are stochastic quotient closure, finite-horizon error propagation, intervention compatibility, and kernel drift, beginning with their precise control and coupling assumptions. The 36 remaining pairs, the memory statement's source-edition clarification, and separate empirical qualifications remain open.
