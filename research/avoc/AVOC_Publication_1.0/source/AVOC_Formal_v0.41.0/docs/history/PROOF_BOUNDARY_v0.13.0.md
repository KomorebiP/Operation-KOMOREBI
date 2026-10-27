# AVOC Formal v0.13.0 — proof boundary

## Mathematical model

A fixed partial order is the transitive dependency relation for a finite task set. `y < x` means task y must be completed before x. A completion ledger is a finite order ideal. Readiness and actual proof evidence are separate predicates.

## New proved statements

1. Inserting a fresh task preserves ideal closure exactly when all its strict prerequisites are already complete.
2. The ready frontier is disjoint from completed tasks and is an antichain.
3. A simultaneous batch is a subset of the frontier exactly when it is fresh, an antichain, and its union with the completed ideal is an ideal.
4. Any duplicate-free ordering of a ready batch is sequentially legal.
5. Sequential legality is equivalent to freshness, no duplicates, final dependency closure, and topological order. Complete legal schedules are precisely list presentations of linear extensions.
6. Every nonempty finite residual has a ready task. Every ideal admits a structural completion. Completion contains exactly the remaining number of tasks.
7. Distinct active workers assigned injectively to ready tasks are bounded by current frontier cardinality and global poset width.
8. Unit-time schedules respecting dependencies have at least as many rounds as any dependency chain. One task per worker per round implies N <= pT.
9. Actual local proof rules together with certified prerequisites justify admission and preserve certified truth. Readiness alone does not imply truth.
10. Diamond and chain examples and explicit premature-order / antichain-only counterexamples are kernel checked.

## Scope limitations

- A structural completion schedule does not show that tasks can actually be solved, that conjectures are true, or that a proof search will terminate successfully.
- Dependency edges and task meanings are declared inputs. Lean does not infer their scientific adequacy or correspondence to a real repository.
- Fixed AND-style prerequisite plans are used. Alternative proofs, disjunctive dependencies, circular proof systems, changing DAGs, and retractions are not modeled here.
- Width bounds distinct ready task assignments. They do NOT bound every useful agent, independent proof attempt, collaborative proof search, verifier, or falsifier.
- Time-slot bounds assume unit-duration tasks and at most one task per worker per slot. No stochastic-duration, optimal worker-allocation, or minimum-makespan theorem is claimed.
- The scheduling layer is not yet coupled to the Bayesian Bellman controller's action-selection objective, queue costs, or artifact investment.
- Certification uses actual `Prop` proof obligations and sound local proof rules. A metadata label is not a proof certificate. The type-level theorem does not authenticate external files or systems.
- The Python planner is a separate implementation, checked on the stated finite range; it is not a Lean-extracted or formally refined executable.

## Counting correction

The previous v0.12 report's 512 omitted 22 inline-attribute-prefixed theorem declarations. The complete inherited count is 534, and v0.13 adds 59 for 593. The new inventory lists each fully qualified name and source line. Counts include helper lemmas and concrete examples; they are not counts of mathematically independent discoveries.

## Verification scope

The detailed current run is recorded in `results/VERIFICATION_v0.13.0.md` and machine-readable files under `results/v0.13.0/`. A clean local-project rebuild uses the exact cached dependency revisions. Dependency-cache integrity and compiler/kernel correctness remain the usual trust boundary; no fresh rebuild of every mathlib source is claimed.
