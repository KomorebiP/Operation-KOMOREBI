# Independent mathematical and interface review — AVOC v0.41.0

**Primary verdict: proved as written.** The frozen recorder, source-generative
refinement, indexed executor, and `recorder_issued_failure_le` statements follow
from their explicit hypotheses. No mathematical blocker remains in these
statements. Applying the statistical conclusion to real provider outcomes remains
conditional on the stated source coupling, sampling law, identity interpretation,
and protected complete records. The raw input parser cannot establish those
hypotheses.

This review reconstructed the main implication from the raw definitions and proof
terms before relying on release summaries. It separately ran the pinned Lean
compiler on twelve focal theorem axiom reports, an independent dictionary-based
lifecycle reference, and raw text probes of both actual endpoints. It shares the
project's Lean/compiler/kernel trust boundary and is not an alternative-kernel
check. The exact reviewed artifacts and source revisions are recorded in
`independent_review.json`.

## Normalized claim

Identities form an arbitrary type with decidable equality. Each identity has a
finite Boolean source, and commands form a finite list. The raw lifecycle recorder
has a separate pending registry and an immutable terminal log in one global
operation-ID space. A successful run from the empty state has unique pending IDs,
unique terminal IDs, no ID in both, and no unfinished terminal entry. Its completed
records persist exactly once. Duplicate terminal delivery is idempotent; changed
outcome or identity conflicts; a late matching intent does not reopen completion.

The source-generative command language supplies only `begin`, `report`, and
`fault`, with an ID and identity. A fresh report constructs its terminal outcome
from the next source Boolean. A repeated report returns the previously recorded
binary outcome before inspecting source exhaustion. Faults and repeated deliveries
consume no source position. Every accepted generated run projects to a successful
raw command run and to a reveal trace whose per-identity samples are exactly the
terminal log samples. Consequently those samples are prefixes of the source.

The final statistical theorem works on a finite rational probability space. Each
identity's latent source satisfies the supplied primitive `ConditionalLaw` at a
stationary rational parameter in [0,1]. A finite schedule fixes checkpoint
identities, sample sizes no larger than their source, positive grid sizes, and
nonnegative error allocations. Cross-identity independence is not assumed.
Selectors may depend on the entire outcome, but must select the prescribed warm
and cold parameter strata. Deterministic realization memberships are supplied.

The planner reads counts from the actual generated terminal log only after the
entire command run succeeds and every identity has no pending operation. Both
selected checkpoints must be available. The conclusion is

    P(a plan is issued and lacks the specified frozen-episode certificate)
        <= sum of the fixed schedule's error allocations.

Invalid, pending, and insufficient-sample outcomes remain in the original
probability space. The theorem assumes none of them away. It gives no conditional
coverage among successful runs, no completion-rate bound, and no empirical
performance guarantee. Large error allocations may make the bound uninformative.

## Reconstructed dependency graph

1. `ObservationRecorder.step` branches on global terminal and pending ID use.
   Reachable-state induction proves `WellFormed`. Terminal completion removes its
   pending ID and appends a fresh immutable record; exact replay changes nothing.
   Prefix preservation plus unique IDs proves retention exactly once.
2. `finish_record` identifies every accepted terminal transition with the older
   `CalibrationLog.record` operation on the separate terminal-only log. It does
   not identify the entire old unfinished-event protocol with the new recorder.
3. `RecorderReveal.step` checks prior success/rejection before reading the next
   source bit. `commit` updates the reveal state only if the raw transition
   accepts. The `Tracks` induction proves full raw execution, full reveal
   execution, and per-identity sample equality. The helper's next-bit premise is
   discharged inside the transition proof; it is not an input to `run_refines`.
4. Reveal conservation gives `run_samples_eq_take`. The stronger result relating
   actual source-generative terminal samples to the source does not require the
   caller to supply a count correspondence or effective reveal trace.
5. `RecorderCodec.replayFrom_toOption` proves the indexed executor's successful
   result equals the raw recorder's result for every finite command list. JSON
   parsing and Python registry export are separately tested interfaces.
6. `gatedCounts` maps rejected runs and any global pending registry to `none`.
   On acceptance, `availableCount_value` plus the prefix theorem identifies each
   available first-n count with the fixed latent prefix. The final theorem
   constructs that prefix using `truncateSample`, discharging `hprefix`.
7. The inherited primitive conditional law derives the prefix's binomial law.
   Existing finite-schedule simultaneous calibration and the deterministic
   frozen-episode bridge give `recorder_episode_coverage`. Taking the event
   complement gives `recorder_issued_failure_le` over the unchanged probability
   law. No conditioning division is introduced.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Global uniqueness, pending/terminal disjointness | Passed | Reachable `WellFormed` induction |
| Immutable completion, replay, changed-ID conflicts | Passed | Raw transition lemmas and retention theorem |
| Late begin does not reopen | Passed | Terminal branch, explicit replay theorem |
| Both success and rejection consume one fresh source bit | Passed | Fresh report construction and sample equality |
| Faults and binary replay consume no fresh bit | Passed | Step cases and exhaustion/replay kernel example |
| Fresh report after exhaustion fails closed | Passed | Empty-source branch and kernel example |
| Whole generated run refines raw and reveal runs | Passed | `run_refines`, reconstructed induction |
| Invalid suffix or unrelated pending blocks issue | Passed | `gatedCounts`, no-count/no-plan theorems |
| Final count-law and prefix premises are discharged | Passed | Truncation and primitive-law composition |
| Unconditional finite-schedule error bound | Passed | Final theorem and complement argument |
| Completion-conditioned error bound | Out of scope | No such conclusion; inherited counterexamples apply |
| Actual-provider coupling and authentication | Conditional | Explicit supplied assumptions |
| Universal Python/JSON/storage refinement | Not addressed | Indexed typed Lean executor proved; interfaces tested |
| Multi-episode adaptation and physical cost accounting | Out of scope | Frozen-episode contract retained |

## Decisive interface checks and scope correction

The new lifecycle protocol must remain distinguished from the older immutable
unfinished-event log. In the old implementation, storing an unfinished event and
then changing it to a terminal outcome under the same ID is a conflict. The new
recorder stores pending intents separately and sends only terminal entries to the
old calibration format. `inherited_unfinished_terminal_conflict` formally records
that incompatibility. The checked Python export is a syntactic adapter to that
terminal-only format, not an authenticated history migration or sampling proof.

A raw external `finish` supplies an outcome. The source-generative `report`
constructs an outcome. Proving refinement of the latter does not certify arbitrary
externally supplied success labels. A rejection is a checked Boolean false,
whereas a fault is terminal without a statistical observation. Nothing here
proves that a real fault has that meaning, retries paid operations, or turns a
rejection into a censored observation.

The independent dictionary reference agreed with the Python reducer on all
69,905 command words of lengths 0–4 over two IDs, two keys, and begin plus three
terminal outcomes. There were 957 accepted runs, 68,948 rejected runs, and 349
ready runs. This exact bounded enumeration is not a universal host proof.

Twenty-seven independent raw-text probes passed on both actual Lean and Python
endpoints. They cover Boolean/negative/oversized/string IDs, decimal/exponent and
nonfinite tokens, malformed commands, unfinished terminal input, bad schemas,
invalid batch members, an escaped command token, exact integer boundaries,
unknown completion, changed terminal outcome, unrelated pending, late intent,
and invalid suffix. Valid inputs returned identical results; malformed inputs
returned nonzero rejection. Input files and complete endpoint outputs are saved.

The reviewer kernel check printed axioms for twelve focal declarations with
warnings as errors and exit status zero. Their axiom union was exactly
`propext`, `Classical.choice`, and `Quot.sound`. Full-project theorem inventory,
clean builds, negative suite, inherited regressions, and package integrity remain
separately checked release gates.

## Release and runtime provenance review

A separate reviewer inspected all eleven release tools and passed fifty-seven
isolated helper/schema probes. A later runtime-provenance addition received
fifteen more mutation probes, for seventy-two total. The final gate independently
constructs the transitive local import closure of `RecorderMain`, requires exact
source and compiled-object membership with current hashes, and binds the Lean
executable digest. The executable oracle records the same runtime before and
after its checks. These synthetic gate probes test validators; they are not
substitutes for the actual production build or Lean oracle execution.

Two bounded oracle attempts failed during Lean startup under additional 2 GiB
and 8 GiB virtual-address-space limits. The former could not create a thread; the
latter failed to read an existing compiled cache file. A diagnostic startup
without that additional address-space limit succeeded and recorded a virtual
peak of 8,974,552 KiB. The wrapper was corrected to retain both standard output
and standard error on abnormal exits, since the second diagnostic had appeared
on standard output. Failed manifests and logs remain archived. These were
execution/resource failures, not mathematical counterexamples; the final bounded
oracle must still pass under its declared effective resource configuration.

## Completion order is a substantive physical coupling assumption

Two independent fair outcomes assigned when operations begin need not remain
independent fair outcomes in completion order. If successes finish before
rejections, the first stored report is successful in three of the four equally
likely two-operation cases. Its success mass is 3/4, although each initiation
outcome has success mass 1/2. Both operations can finish before any plan is
requested, so the global pending gate does not remove this issue.

The exact interval consequence is also large. Start twenty independent fair
operations, let successes finish before rejections, wait until all twenty resolve,
and calibrate the first ten stored reports with ten grid cells and alpha=1/10.
Whenever the twenty initiation outcomes include at least ten successes, the first
ten stored reports are all successful. Their interval is [3/5,1], which excludes
the initiation parameter 1/2. That event has exact mass

    sum_{k=10}^{20} choose(20,k) / 2^20 = 308333/524288 > 1/10.

The independent computation also evaluates all twenty-one binomial count classes.
The first-ten success count is min(k,10) for every member of the k-success class,
because every success finishes before every rejection. Class multiplicities sum
to 2^20. The exact total miss mass is 616667/1048576, including the additional
all-failure outcome. The displayed lower bound already refutes the claimed
initiation-parameter coverage for this physical completion model.

Every representative lifecycle run is accepted and fully resolved, with all
outcomes recorded and no faults. This is a finite exact computational
counterexample to an external applicability implication, not a new Lean theorem
or a contradiction of `recorder_issued_failure_le`. That theorem assumes the
stationary primitive law for the report-order source it constructs. Completion
ordering in this example violates precisely that assumption. Preserving or
proving an appropriate observation order is therefore necessary alongside
identity, authentication, and completeness checks. The script and exact tables
are `review_completion_order.py` and `review_completion_order.json`.

## Remaining gap and next check

The formal lifecycle gap is closed for this source-generative finite model.
The next mathematical gap is a bridge from a physical attempt process with faults
to the required accepted-source conditional law, or finite multi-episode
composition under explicit update and accounting rules. The next empirical gap
is to demonstrate protected, complete, identity-correct observations and measured
costs from an actual workload. Passing this parser supplies neither result.

The cheapest continued check is a small authenticated workload with a fixed
schedule and explicit record provenance, while preserving rejection and fault
labels separately. Statistical assumptions and operational measurements must be
reported independently from the already proved finite theorem.
