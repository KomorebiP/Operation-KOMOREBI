# Block07 — one investigation under hard joint budgets

**Machine-Native Reasoning · Reviewed Core0.2 · Formal companion0.7.0 · Komorebi P.**

## 1. The source result and the dependency it closes

Core5.1 is the exact finite work/storage synthesis theorem on printed pages17–18. Core4.2, formalized in Block06, identifies when fixed recipients can use a common artifact from a given record. Block07 asks whether an allowed investigation can obtain a sufficiently informative record while satisfying one online resource vector and one complete-controller storage limit.

This is not Block03's expected-cost Bellman theorem. The online coordinates here are worst-case natural-number charges. A probability-weighted mean cannot replace any of them. The source book and its original statement remain unchanged.

## 2. The actual model and its information boundary

`HardInquiry.Model` contains finite experiment, report and artifact types, Boolean permission and terminal-acceptance tables, exact deterministic transitions and reports, a natural-number charge vector for each experiment, and a support-dependent worst-case terminal charge vector. The proof needs only a finite current state support; the ambient state type may be larger. This includes the source's finite nonempty state model.

The source's partial transition and report functions are represented by total functions with Boolean domains. Values outside an action's domain are never used by a valid tree. One finite report alphabet is used for all experiments. Experiment-specific finite alphabets can be represented by distinct tagged report values. A support must include all origin tags, recipient backgrounds, permissions and history-dependent variables required by the contract.

For a support V, experiment e and observed report o, the update is the literal finite image

    update V e o = {next e x : x in V and observe e x = o}.

`mem_update` proves exactly that membership characterization. `actual_next_mem` proves that an actual observed successor remains in that updated support. Neither theorem substitutes the pre-experiment state for the successor.

An experiment is allowed only when V is nonempty and every state in V permits it. A terminal artifact is acceptable only when V is nonempty and every state in V accepts the same artifact. No existentially permitted state or separately chosen per-state artifact suffices.

## 3. Literal trees, real children and complete storage

At horizon zero a `Tree` is one terminal artifact. At horizon h+1 it is either a terminal or an experiment together with a report-indexed finite optional child table at horizon h. A `none` entry means there is no stored child. The `Valid` predicate requires `none` exactly on impossible reports. Every possible report has a valid child on its actual updated support, and every such support is nonempty.

Thus a failed subproblem does not become a free zero-cost child. An invented child on an impossible report is also rejected under this literal representation. `validDecidable` is a finite recursive validity check; its correctness is its exact decision type, not a probabilistic test.

For a profile `(v,m)`, order means componentwise order on every online coordinate and on complete storage. A root combines children by

    online(r) = stepCost(e,r) + max_o childOnline(o,r)
    storage   = 1 + sum_o childStorage(o).

Absent children have zero contribution. Present terminals always have one stored record, even when their online charge is zero. `records` counts nodes independently of the terminal-cost fields. `profile_records` proves that the profile's storage coordinate is exactly this literal count. Child references, byte encodings, shared suffixes and peak runtime memory are different models and are not silently equated to this count.

## 4. Why Pareto pruning is complete

`HardPareto.frontier` retains p in a finite profile set S precisely when every q in S with q <= p also satisfies p <= q. In the product partial order, this is exactly the absence of a distinct dominating profile.

`exists_frontier_le` proves that each profile in a finite set has a retained profile below it. The argument uses finite minimal-element existence; it does not independently minimize resource coordinates. `budget_iff` consequently preserves every componentwise budget.

The inquiry backup begins with all acceptable terminal profiles. For each uniformly permitted experiment, it takes the finite product of the available child profiles for each possible report. Impossible reports supply only `none`; a possible report with an empty child frontier supplies no choice and eliminates that experiment from successful backups. Each actual child combination is passed to the root's maximum/sum constructor.

Two induction invariants do the work:

* `backup_witness`: if every input child profile has a valid tree witness, every backup profile has a complete valid tree witness. All children are chosen simultaneously, not after disclosure of the hidden case.
* `backup_dominates`: if the input family contains a profile below every valid child, then a backup profile lies below every valid parent. `nodeProfile_mono` proves that both the coordinatewise maxima and the complete storage sum are monotone.

`solve_correct` carries soundness and lower cofinality together through every finite horizon. `exact_frontier` then proves that the result is exactly the nondominated set of all valid tree profiles. `joint_budget_iff` gives the source equivalence between one affordable tree and one retained profile bounded by the same budget. `no_tree_iff_empty` is a complete negative result only inside the declared model and horizon.

The independently defined computable `compute` recurrence is proved equal to the mathematical `solve` in `compute_eq_solve`. Finite examples evaluate this concrete recurrence using ordinary kernel-checked `decide`. No `native_decide`, external oracle or generated pass label proves the result.

## 5. What those profiles say about an execution

`execute` runs a given tree in the specified environment. The controller's root is fixed by the tree and its later choices use only the returned report. The environment simulator uses the actual state to produce a report and apply the transition; that state is not another input to an action-selection function.

Terminal work is supplied as a per-case function `charge`. If each such charge is bounded by the declared terminal profile, `execution_sound` proves that every possible starting state reaches an accepted final artifact, stays within every online coordinate, and produces at most the declared number of experiment reports.

A stronger premise, `ExactCharges`, says that each terminal-profile coordinate is the exact maximum of the per-case charge over the support. `worst_coordinate_attained` then proves that every online profile coordinate is attained by an actual execution from some initial state. The proof first restricts the root maximum to live reports; each child maximizer has a preimage in the parent support. This addresses both destructive transitions and zero-cost branches.

Different coordinates can attain their maxima on different initial states. That is exactly what a componentwise hard budget means. The theory does not claim one trace simultaneously consumes all coordinatewise maxima.

## 6. The four-case tradeoff, at every finite horizon

The source instance has four immutable cases, four unit-cost equality tests, a four-unit direct reveal, and zero-cost terminal answers that identify the actual case.

The executable three-step recurrence returns exactly

    (online 4, records 5) and (online 3, records 7).

`direct` and `equality` are explicit stored trees. Their validity, costs, record counts and terminal outputs are checked. The equality tree makes 1,2,3,3 reports on the four respective cases, while storing all seven nodes. The direct reveal stores five nodes and visits only two on any execution.

The stronger all-horizon conclusion is not inferred from testing several depths. `fourTable` gives a finite profile invariant for every subset of the four states. `fourTable_closed` checks its exact backup fixed-point equation. The generic `closed_family_dominates` theorem propagates this lower bound through every finite tree. `promote` enlarges the permitted horizon without inserting work, and `pad_horizon` preserves validity and profile.

Combining the invariant with attained three-step witnesses proves `four_frontier_all`: the same two-point frontier holds at every horizon 3+n. `four_no_mixed_budget` rules out `(3,5)` at every finite horizon, including horizons below three. This is a finite certificate plus a universal induction argument, not bounded numerical extrapolation.

## 7. Connection to the unchanged fixed recipients

`AudienceBridge.attach` specializes terminal acceptance to the exact `RecipientExecution.Audience.Accepts` predicate from Block06. Outputs, permission, work limits, peak-space limits, timeout and malformed outcomes stay inside that same predicate. `terminal_common` and `recipient_inquiry` instantiate Core5.1 without designing a new decoder.

The concrete XOR example preserves the earlier eight-world sensor and its two installed recipients. Recipient A knows the sensor convention, recipient B the target bit. An initially uninformed sender makes one exact display observation and broadcasts that bit. The same message allows both fixed XOR procedures to recover their respective demanded bit.

Three online coordinates are declared separately: observation calls, combined recipient arithmetic work, and transmitted bits. Their profile is `(1,2,1)` with three complete stored records. Each recipient's one-unit work and peak-space limits remain checked by the inherited acceptance predicate. The two arithmetic units assume both recipients execute once; this is a declared accounting convention, not elapsed time or an inference about parallel hardware.

Before the observation the finite frontier is empty. After one observation the complete frontier is the stated singleton. `sensor_recipient_execution` uses the general execution theorem and the proved equality with the installed audience acceptance. `sensor_two_records_insufficient` rules out storing only the visited root and leaf as the complete controller.

## 8. Boundary cases and what remains

Other proofs reject missing possible branches, extra impossible branches, nonuniform permission, an unsolved live child counted as free, omitted terminal work, and use of a reset to infer an erased origin. A two-coordinate example proves that separate maxima need not belong to one trace.

Core5.3's general binary leaf-count lower bound and optimality closure remain unformalized. The specialized four-case invariant is not counted as formalizing that general result. No large-scale learning, probabilistic workload result, physical model verification or arbitrary host-program extraction is claimed.
