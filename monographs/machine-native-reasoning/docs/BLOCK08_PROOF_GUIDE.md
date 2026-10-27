# Block 08 — binary diagnosis and certified optimality

**Machine-Native Reasoning · Reviewed Core 0.2 · Cumulative companion 0.8.0 · Komorebi P.**

## The one newly formalized source result

Core 5.3 states the general work and literal-storage lower bounds for immutable cases, binary observations, unit-cost queries and singleton unit-cost repairs. An actual successful controller attaining both bounds realizes the whole Pareto frontier at its requested horizon.

This block uses the **unchanged** `HardInquiry.Model`, `Tree`, `Valid`, `profile`, `execute`, `solve`, and `compute` contracts from Block 07. Leaf counts are derived from their actual transitions and terminal acceptance predicate. They are not postulated in a replacement abstract tree model.

## 1. Counting successful leaves from the model

`Scope M` records four premises:

1. Every experiment leaves each modeled state unchanged.
2. A fixed repair cannot succeed on two distinct states.
3. Every query costs one scalar online unit.
4. Every terminal costs one unit on every nonempty support.

The source assumes total query availability and a repair for every case. The lower-bound theorem is slightly stronger: it also permits partially allowed query catalogues and unused unsuccessful repair labels. Its conclusions concern a **valid successful tree**, which already enforces uniform permission and a successful repair on every reachable case. No successful tree is inferred from the scope alone.

For an immutable experiment the actual update is exactly its report filter:

\[
V_{e,o}=\{x\in V:o_e(x)=o\}.
\]

The false and true supports are disjoint and exhaust the current support. A successful terminal's support has exactly one state, by nonemptiness and singleton acceptance. Induction through the actual stored children gives

\[
|V|=L(T),
\]

where `leaves h t` counts terminal **occurrences**, not distinct printed labels. Missing report children have zero leaves. Validity excludes invented children and requires every possible branch.

**Endpoints:** `update_immutable`, `binary_card_split`, `terminal_card_one`, `cases_eq_leaves`.

## 2. Actual depth and redundant unary nodes

The tree type is indexed by an allowed horizon. `depth h t` instead counts the maximum number of queries actually stored on a path. Early terminal nodes do not fill the unused horizon.

For every binary tree,

\[
L(T)\le 2^{d(T)},\qquad d(T)\le h.
\]

Every valid tree is live: no query has zero possible children. Structural induction then proves the exact edge identity

\[
\operatorname{records}(T)+1=2L(T)+u(T),
\]

where `unary h t` counts internal nodes with exactly one stored child. Thus, for a successful singleton-repair tree,

\[
\operatorname{records}(T)=2|V|-1+u(T).
\]

Redundant queries are not silently deleted. They contribute exactly one additional record each. Minimum record count holds if and only if there are no unary nodes in this scope.

**Endpoints:** `leaves_le_pow_depth`, `depth_le_horizon`, `records_identity`, `records_exact`, `minimum_records_iff_no_unary`.

## 3. Online work includes repair and has an actual witnessing run

Unit query and terminal costs give

\[
W(T)=1+d(T).
\]

Lean uses `Nat.clog 2 n`, the natural-number ceiling logarithm. Its order characterization states that `Nat.clog 2 n <= d` exactly when `n <= 2^d`. No floating-point logarithm or rounding approximation is used.

Consequently,

\[
W(T)\ge 1+\lceil\log_2 |V|\rceil,
\qquad
\operatorname{records}(T)\ge 2|V|-1.
\]

The interpreter bridge proves existence of an actual initial state whose execution receipt attains the profile's worst-case scalar cost. The proof chooses a maximizing live child, recursively obtains its witnessing state, and takes a preimage through the actual update. An absent branch cannot win that maximum because some live child's cost is positive.

This deals directly with nonempty supports. It does not incorrectly require a unit terminal cost to equal the maximum over an empty set.

**Endpoints:** `work_eq_depth_succ`, `binary_lower_bounds`, `worst_execution_attained`, `actual_run_lower_bound`, `impossible_below_information_depth`.

## 4. Why both bounds close the existing frontier

Define

\[
p_n=(1+\lceil\log_2 n\rceil,2n-1).
\]

Every valid controller profile is componentwise above `lowerProfile n`. If one actual valid candidate has profile exactly `lowerProfile n`, that profile is attainable and dominates every other attainable one. The unchanged Block 07 `exact_frontier` theorem then gives

\[
M.\operatorname{solve}(h,V)=\{p_{|V|}\}.
\]

The result transfers through `compute_eq_solve` to the existing computable recurrence. It is not an equality to a newly defined solver.

Horizon promotion inserts no actual query and changes no cost. The certificate therefore proves the same frontier at every horizon `h+n`.

**Endpoints:** `checked_candidate_closes_frontier`, `checked_candidate_closes_compute`, `closed_frontier_all_larger_horizons`.

## 5. Two executable checks with different jobs

`checkCandidate` verifies the actual tree's `Valid` predicate and equality of its complete profile to `lowerProfile`. Its soundness alone is conditional on `Scope M`.

`checkScope` separately checks the finite model's semantic and charge premises. Its terminal-cost check ranges over **all finite state supports**. This may be exponentially expensive. It is not called free, nor is it an efficient general scope inference algorithm.

`admissionCheck` combines both checks. Its soundness theorem has no supplied scope witness: a returned `true` establishes the scope, the actual candidate validity, and equality to the unavoidable profile. It follows that the whole computed frontier is the certified singleton and that a common budget is feasible exactly when it bounds that profile.

Neither checker calls `compute` or enumerates all controllers. Nonetheless, this block makes no measured wall-clock speedup claim. The model, candidate construction, scope checking, validity checking, arithmetic and storage have costs not counted by the online query/repair units.

A false check means **this candidate is not certified by this gate**, not that the problem has no solution. The gate is sound, not complete for every optimal controller in every query language.

**Endpoints:** `checkScope_iff`, `checkCandidate_iff`, `admitted_scope_and_candidate`, `admitted_frontier`, `admitted_all_horizons`, `admitted_budget`.

## 6. Source example: eight immutable cases

One common model supplies both three coordinate-bit queries and eight equality queries. The balanced tree uses three observations and a final repair, with eight leaves and fifteen records. Its entire finite `admissionCheck` evaluates to `true` by ordinary kernel-checked `decide`.

The general theorem proves the frontier `(4,15)` at **every horizon 3+n**. No enumeration of all larger-horizon controllers is performed. Two binary observations are proved insufficient.

The equality-first controller is valid in the same model, but costs eight online units with the same fifteen records. It attains the record lower bound, not the work lower bound, and its candidate check rejects. The existence of this valid rejected candidate proves that rejection is not infeasibility.

A fabricated tree with the balanced shape and wrong leaf labels has the same `(4,15)` profile but is rejected on validity. Numeric costs alone do not prove the target.

## 7. Boundaries and small exact controls

A three-case tree has optimal depth two and work three but includes a redundant unary query on a shorter branch. It stores six records instead of five. It therefore attains the work bound without attaining the storage bound.

A destructive reset of eight states to one permits a two-unit, two-record controller while retaining singleton repair meanings for the **new state**. The old immutable-origin counting argument no longer applies. A universal repair instead changes the success predicate and succeeds with one online unit and one record. Their actual finite scope checks reject the changed models.

Free terminal work removes the final online unit without changing the number of leaves. A four-valued direct report distinguishes four cases in one query and has `(2,5)` after repair, outside the binary alphabet.

A constant-report model satisfies the counting scope but has no successful tree at **any finite horizon**. That is proved by induction, not by checking a fixed set of depths. Numerical lower bounds never create a missing observation.

The one-case boundary is `(1,1)`, not zero work. An empty support has no valid controller under the unchanged nonempty-support contract.

## 8. Assurance boundary

The statement inventory is one new source result, Core 5.3, plus supporting lemmas and instances. The certificate does not learn the model or a candidate, prove physical fidelity, verify arbitrary host software, or optimize code bytes. It concerns one-coordinate natural costs and literal report trees. It does not supply the source's later finite-learning or teacher-trace theorems. Those remain separate obligations.

Actual compiler, kernel replay, axiom audit, negative controls and fresh-source comparison are recorded in this release's terminated evidence files. A successful finite example is not substituted for the general proof.
