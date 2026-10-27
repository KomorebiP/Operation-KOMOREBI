# Block 11 — mathematical route through selective reuse

**Source:** Machine-Native Reasoning, Reviewed Core 0.2, Theorem 7.1, printed page 26. The book and the forty-six predecessor substantive Lean modules are unchanged.

## 1. A finite closure, not a declared list of stale names

A graph assigns each claim `v` its finite parent set and finite direct artifact-input set. Artifact coordinates may have different types. An environment is a dependent function assigning one value to each coordinate. `Graph.view` is the literal restriction to the declared direct inputs.

The root set contains exactly vertices with at least one changed direct value. Write `S_0` for that set and set

    S_(k+1) = S_k union {v : some parent of v belongs to S_k}.

Each stage contains the previous one. Every strict growth adds a vertex, so a fixed point occurs within `card V - card S_0` strict rounds. The implemented closure uses `card V` rounds, not a supplied stopping witness. Once fixed, the sequence stays fixed. The proof identifies the computed result with the inductively defined finite forward paths from the changed roots.

Thus a nonstale vertex has equal direct restrictions and no stale parent. A separate theorem makes the closure the least forward-closed set containing the roots. This construction does not require acyclicity. It works on a cyclic graph too, but closure of changes does not make circular proof dependencies sound.

**Endpoints:** `Dependency.bounded_stabilization`, `closure_stable`, `closure_least`, `closure_iff_reach`, `Graph.nonstale_view`, `Graph.nonstale_parents`.

## 2. What semantic completeness actually says

`System` contains a claim predicate, an external-premise predicate, a typed local Boolean checker, and a universal soundness theorem. The checker receives only the local restriction and its own witness. Local soundness requires the applicable external premise and already established parent claims before deriving the child claim.

`System.Complete` is a different condition: equal direct restrictions, equivalent parent claims and equivalent external premises imply equivalent local claim meanings. It is a formal assumption for the general theorem and an actual proof for the example. It is not replaced by equal filenames, digests, cache identifiers or a diagram label.

`Established a v w` contains all three obligations: the actual local check passes on `a`, the applicable external premise holds, and the old claim is already established. The source's old-witness premise is consequently explicit. A separate topological induction derives establishment from local check results and external premises when all parents are grounded in an acyclic graph. Two circular implications cannot bootstrap it.

## 3. Selective reuse

A topological rank is a map to natural numbers that strictly increases from every parent to its child. It is an explicit acyclicity certificate. Strong induction on that rank transports claim meaning outside the stale closure. The direct restrictions agree there, and every parent lies outside the closure as well.

The original witness is copied without changing it. Its Boolean check agrees because its actual input restriction agrees. The old established claim transfers through the proved meaning equivalence. The new external premise is required, not manufactured by that equality.

**Endpoint:** `Dependency.System.selective_reuse`.

The argument remains a conditional mathematical statement. A graph or checker change is not silently included in a value-only revision of the same `System`. Its semantic correspondence would need to be established separately.

## 4. Partial restoration is an actual finite procedure

The replay table uses seven distinct constructors: pending, missing evidence, rejected witness, blocked by parents, blocked by external premise, reused witness and newly rechecked witness. Staleness is a separate set property, not one of those truth judgments.

Initially every unaffected vertex holds its exact old witness and every affected vertex is pending. At rank layer `k`, only affected vertices of that rank are reconsidered. The procedure checks parent availability, the supplied external flag, the presence of a new witness, and the result of its actual local checker in that order. Vertices at the same rank have no dependency edges between them under the rank certificate. The computation ends after one more than the largest rank.

`replay_sound` proves by induction that every exported witness has its revised interpretation at every intermediate layer, even if other vertices fail or lack evidence. A blocked or rejected table entry supplies no negation of its intended claim. When every affected vertex has a passing revised witness and an available external premise, topological induction proves readiness below each completed rank. `restoration` combines this readiness with soundness to obtain an actual established witness for every vertex.

This is not a proof that proof search can always find those new witnesses. Nor is an execution timeout a completed failure of proof existence. Rank iteration and finite input comparison are mathematical operations, not measurements of host time or storage.

**Endpoints:** `System.replay_sound`, `replay_unaffected`, `replay_complete`, `restoration`, `finish_sound`.

## 5. The outer admission boundary

Blindly copying an unaffected witness is unsafe if its external premise is unavailable. The admitted interface therefore checks both the supplied topological rank and the external flags of every unaffected vertex. If either fails, it returns `none` rather than a table claiming reuse. On affected vertices an unavailable flag produces a blocked-external outcome.

`admitted_reuse_and_restoration` ties any admitted output to the actual old established snapshot, semantic completeness and soundness of the external flags. The flags do not prove the external facts. A caller must supply the theorem connecting true flags to the declared premises. This separation is especially important for physical observations, delegated permissions and unverified service contracts.

## 6. The repair-language instance

The example has five claim vertices and three artifact inputs:

| Claim | Direct inputs | Parent claims |
|---|---|---|
| Arithmetic identity | None | None |
| Singleton counting scope | Repair-language selector | None |
| General controller lower bound | None | Counting scope |
| Actual controller validity | Repair selector and controller selector | None |
| Actual controller profile | Controller selector and expected-profile record | Controller validity |

The repair selector chooses the already formalized `BinaryExamples.eight` or `BinaryExamples.universalRepair`. Only the success predicate changes. The controller selector chooses the inherited balanced tree or one immediate repair. The lower-bound claim quantifies over every finite horizon, every support and every valid controller. The profile is the actual `HardInquiry.Model.profile` of the selected tree, not a Boolean merely named 'profile'.

The declared dependency registry is proved complete. The lower-bound claim is equivalent to the counting scope in this particular two-model family. Its failure under universal repair is proved by the actual one-step controller. The profile computation is proved independent of the changed acceptance relation, while its claim still requires the selected controller's validity.

Changing only the repair language has direct roots `{scope, validity}` and exact stale closure `{scope, lower bound, validity, profile}`. The arithmetic identity is unaffected. A first replay with missing profile evidence returns:

| Vertex | Actual outcome |
|---|---|
| Arithmetic identity | Reused |
| Counting scope | Rejected |
| General lower bound | Blocked by its rejected parent |
| Old balanced controller validity | Rechecked successfully |
| Its still-true profile | Missing evidence |

A second snapshot installs an immediate repair and changes the expected-profile record to `(1,1)`. Its validity and profile are both rechecked. The previous generic counting bound remains false. Retaining the old `(4,15)` profile record instead causes rejection, even though the newly installed controller is valid. No old speed or value comparison is silently restored.

**Endpoints:** `RevisionExamples.meanings_complete`, `old_established`, `addition_sound`, `replacement_sound`, `replacement_actual_controller`, `obsolete_profile_rejected`.

## 7. Mathematically distinct failure modes

The scalar omitted-input example keeps the recorded value `u` unchanged, changes an unrecorded `v`, and turns `u=v` from true to false. Local replay still passes. The source proves that the corresponding completeness assertion is false.

The cyclic example has two false claims and two sound implication rules, each conditional on the other. Every local Boolean check can pass, but neither old claim is established and no topological rank exists. The admission gate rejects every proposed rank.

Additional examples separate stale from false, missing evidence from false, rejection of a malformed witness from refutation, a true child from an available parent proof, and exact artifact equality from equality of an arbitrary fingerprint. The actual ordered compiler from Block10 supplies the example that a changed query order can change the literal returned tree.

These are universal or exact finite Lean statements. They are not statistical trials, learned dependency discovery, or an automatically verified host certificate manager.
