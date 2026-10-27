# Block10 — mathematical route through the proofs

**Machine-Native Reasoning · Reviewed Core0.2 · Formal companion0.10.0**

## 1. Numerical completion is a necessary capacity test

Let m count distinct cases, C the leaf capacity of each child, and a,b the partial report counts. Assume a+b<=m and m<=2C. A completion chooses nonnegative u,v with u+v=m-a-b and a+u<=C, b+v<=C. Such a completion exists exactly when max(a,b)<=C.

The constructive sufficiency proof chooses u=min(m-a-b,C-a) and v=m-a-b-u. The total headroom ensures v<=C-b. Necessity follows because adding nonnegative counts cannot repair an excessive branch.

`PrefixScan.completion_iff` proves the natural-number formulation. `integer_completion_iff` retains all source integer hypotheses, including C>=1 and 2<=m. The proposition concerns possible assignments of unread reports, not existence of useful later queries in the installed language. The checked example m=9,C=4,a=b=0 shows why the total headroom premise matters.

## 2. A literal streaming scan

`partition` reads the supplied Boolean report function and preserves original order within both output sublists. `full` completes this partition and tests both final counts. `stream` tests the current prefix before reading another row, increments exactly one count, and stops at its first violation. On success it returns the same complete ordered sublists, without re-reading the report table to reconstruct them.

`stream_branches` proves exact equality of optional partition results. `stream_reads_le` bounds the number of actual report-function calls by the list length. `stream_checks` proves the exact test count reads+1 for one scan, including its initial/final prefix tests. `successful_reads` proves that accepted candidates were fully read. A successful candidate does not obtain unknown suffix data for free.

Only report-table reads and capacity tests are metered in these definitions. Building and allocating lists, incrementing integers, computing a maximum and interpreting the surrounding program have their own implementation costs. One capacity test is a declared event, not one processor instruction.

## 3. Exact preservation through recursive search

`OrderedCompiler.search` returns `Run (Tree E Bool C h)`, using the exact inherited tree datatype. It first checks the ordered repair list. If no common terminal succeeds and positive horizon remains, it scans the ordered experiment list. An experiment must be permitted on every remaining case. Its false child is searched before its true child. A failed live child causes backtracking. An impossible child uses `some none` in the child constructor, distinct from the outer failure `none`.

`Run.bind` and `Run.first` charge unsuccessful attempted branches before a later success. The relation `Run.Refines` means equal optional answer and nonincreasing report reads. Its composition lemmas yield `streaming_preserves_search` by induction on the actual horizon. Consequently `same_returned_tree` identifies literal trees, not just equal values or equally good answers. `no_more_report_reads` covers all recursive calls and failed roots in that same ordered computation. The separate predicate count need not decrease.

`same_fallback` applies an identical fallback only after an identical completed failure. It is not a timeout-to-failure conversion. These are total structural recursions in the formal model. If host execution is interrupted before producing that result, no completed negative conclusion is supplied.

Result equivalence itself does not need singleton or immutability: both scans agree even for a misapplied capacity rule. Correctness and completeness of their interpretation require the next step.

## 4. Capacity is derived from the actual controller semantics

`valid_capacity` uses Block08's actual leaf count and tree depth to show |V|<=2^h for every valid h-depth tree in `BinaryDiagnosis.Scope`. Immutability makes each scanned branch's finite support equal the original model's actual post-experiment update. With nonduplicated rows, the list lengths are those support cardinalities.

`valid_root_capacity` applies the bound to both actual children of a valid root. `prefix_exclusion` proves that an overfull observed sub-support rules out EVERY valid child completion under that root. No assumption that the desired tree exists is inserted. `rejected_root_impossible` connects this result to an actual rejected streaming scan.

Soundness follows by induction on the emitted tree. Completeness follows by induction on any valid witness in the inherited semantics. A valid terminal appears in the complete repair catalogue. A valid root appears in the complete experiment catalogue, passes its capacity test and has valid children, so recursive completeness finds a result. The chosen result may precede the witness in query order. `streaming_sound_complete` then characterizes completed failure as absence of any valid tree at that horizon.

The model's `Scope` includes unit costs because it is the exact scope inherited from Block08. The capacity exclusion uses its immutable-case and singleton-repair content. State-changing experiments and repairs covering multiple cases need another lower-bound contract. Source preservation is not a license to apply the old scope to a new model.

## 5. Admission and the existing Pareto solver

`guard` checks the actual scope, no duplicate rows, and complete query and repair lists. `checkedSearch` has an outer option: outer `none` rejects the optimization's admission conditions. `some r` means the scope passed and the formal finite search completed. Only then does inner `r.answer=none` establish horizon-relative infeasibility.

`admitted_search_sound_complete` proves that distinction. `admitted_failure_iff_empty_frontier` connects that completed failure to an empty result from the UNCHANGED `HardInquiry.Model.compute`. No new tree model is substituted. The ordered DFS returns its first valid controller, not generally the full Pareto frontier or a minimum-work controller. The old Pareto and optimality results retain their separate roles.

The guard examines finite supports through the inherited scope checker. Its cost is not in the report-read comparison and need not be small. A cached scope receipt would need its own dependency binding. This block does not claim such caching is free.

## 6. Connection to the acquired expression

Block09's eight-expression learner returned the original `.maxGtC` syntax after three counterexamples. Here `acquired_rule_meaning` proves its evaluation equals the capacity rejection predicate for all natural prefixes. `acquired_rule_excludes_actual_root` supplies a separate controller-semantic certificate for its use at child capacity2^h. That proof is not inferred from the developmental examples.

The alternative `.capped` expression agrees with the three development contexts but rejects (a,b,C)=(0,5,8), even though the unread rows can be completed within capacity. The learner's finite agreement and this universal scope theorem therefore remain different evidence.

## 7. One exact eight-case computation

The query list contains all eight equality tests followed by the three coordinate-bit tests. Repairs and rows use a fixed lexicographic order. Both compilers use precisely these same lists. The actual program yields184 versus153 report reads,45 versus198 capacity tests, and the same literal valid controller with work4 and15 records.

These are new formal reference counts, not the historical source paper's larger implementation counts. In the two-coordinate price model with read price w and predicate price1, the isolated saving is31w-153. Equal prices lose122 units. For natural-number prices, w=5 is the first beneficial read price and saves2 units. Preparation and unmetered execution work remain additional requirements.

## 8. Boundary cases

The kernel-checked controls distinguish equality from strict overflow, missing total headroom, finite fitting from global correctness, insufficient query languages, duplicate rows, destructive reset, shared repairs, incomplete catalogues, changed query order and omitted permissions. The unchanged silent model survives a nominal capacity test but remains unsolvable. A reset model has a valid small controller although the stale cardinality-pruned compiler would return failure. The admission guard rejects that scope rather than reclassifying its failure as model impossibility.

## 9. Scope of checking

All general statements are Lean proof terms under explicit premises. Finite instance computations use ordinary kernel-checked `decide`, not `native_decide`. No reference executable is promoted to a theorem by the volume of assertions. Current full-gate results, declaration counts and object comparisons belong to the terminated current-source receipts. Same-kernel replay is not independent peer review or an independently implemented verifier.
