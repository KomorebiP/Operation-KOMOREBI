# Independent mathematical and interface review — AVOC v0.40.0

**Primary verdict: proved as written.** The frozen `shared_stream_episode_coverage`
and `shared_stream_issued_failure_le` statements follow from their explicit
primitive source-law, fixed-schedule, parameter-stratum, and deterministic
realization hypotheses. No mathematical blocker remains for those statements.
The actual-provider interpretation is conditional on those hypotheses; the
theorems do not establish empirical sampling assumptions or log authenticity.

This review independently reconstructed the key implications from raw source.
It did not take the authors' proof-status descriptions as mathematical evidence.
It uses the same Lean/kernel trust boundary as the project and is not an
alternative-kernel check. The exact reviewed source hashes, supporting artifacts,
and current-source successful compilation records are in `independent_review.json`.
The verified predecessor archive identifier supplied to this review is
`298b6daed3875697a59c15caa6d8546c9cfe2d30aa8cfbc4aab0275ad63be44c`.

## Normalized claim

On a finite rational probability space, each identity k has a fixed latent
source of length N(k), with rational success parameter p(k) in [0,1]. Its
`ConditionalLaw` states that a fresh position has success mass p(k) times the
mass of every specified pattern on previously chosen positions. This is a
within-identity joint-law premise. Cross-identity independence is not required.

A finite checkpoint set fixes identities, n(j)<=N(key(j)), positive grid sizes,
and nonnegative error allocations. A recursive reveal machine appends exactly
the next latent Boolean on a report and consumes nothing on a fault. Availability
requires n(j) reports of either binary outcome, and counts only their first n(j).
The warm/cold selectors can depend on the entire outcome but must select the
prescribed true-probability strata. The optional planner needs both selected
checkpoints. Supplied deterministic realization bounds remain in force.

The conclusion is the unconditional bound

    P(an issued plan lacks the stated fixed-episode certificate) <= sum_j alpha(j).

The certificate includes the specified true probabilities and deterministic
values, together with the inherited fixed-model Q/value and expected-regret
guarantee. It does not assert completion or condition on completion. If the
schedule sum exceeds one, the bound is valid but may be uninformative.

## Reconstructed dependency chain

1. `conditional_pattern_mass` inducts on the set of inspected positions. The
   success branch uses `ConditionalLaw`; the failure branch subtracts that
   success mass from the exact event partition. The empty pattern has mass one.
   No division by an impossible history occurs.
2. On all positions, pattern matching is exactly vector equality, giving
   `conditional_implies_product`. `vectorMass_card_sum` aggregates success-position
   subsets of cardinality k: each has the same product weight and there are
   choose(n,k) of them. This derives the count law, rather than assuming it.
3. `truncateSample` embeds the first n coordinates injectively into N. Its
   membership/pattern equalities prove `conditional_truncate`, and
   `sampleList_truncate` connects that restriction to the ordered list prefix.
4. Reveal transitions preserve `source = reports ++ remaining` for every
   identity. Induction over the trace proves conservation, hence the exact report
   prefix invariant. Rejections append false and consume one position; faults
   and exhausted-source steps leave state unchanged.
5. `availableCount_value` requires list length >=n and counts true only in
   `take n`. Combining it with the invariant proves `observedCounts_faithful`.
   The final shared-source wrapper constructs each checkpoint by truncation,
   discharging both the generic prefix-equality and count-law premises.
6. Available bad intervals are a subset of the union of fixed-prefix bad events.
   The inherited finite union bound therefore applies without independence of
   checkpoints, identity allocation, or completion. Arbitrary trace dependence
   cannot skip a latent bit under the actual transition definition.
7. `observedPlan` returns none unless both selected counts exist. On simultaneous
   coverage, its concrete replaced probability bands admit the inherited
   realization and frozen-episode certificate. Taking the complement yields the
   direct bad-issuance bound.

There is no circular count-law premise in the final shared-source theorems.
Intermediate generic wrappers deliberately retain such a premise for reuse.

## Obligation matrix

| Obligation | Result | Evidence or limit |
| --- | --- | --- |
| Primitive conditional law -> full vector -> binomial count | Passed | Pattern induction and exact powerset-cardinality aggregation |
| Several checkpoints share one source | Passed | Injective truncation, preserved conditional law, list-prefix equality |
| Zero-length source/checkpoint | Passed | Empty-product proof and `availableCount 0` use no exceptional division |
| Parameters p=0 or p=1 | Passed | Nonnegative product masses; impossible histories use multiplication |
| Rejection counts toward readiness | Passed | Length gate counts both Booleans; true count affects successes only |
| Faults cannot supply reports | Passed | `step none` is identity; actual incomplete-parser probes reject |
| Exhausted source | Passed | Report request is a no-op; prefix invariant remains valid |
| Arbitrary adaptive allocation and availability | Passed | Pointwise prefix equality plus unconditional event inclusion |
| Conditioning on completion preserves nominal bound | Refuted and excluded | Lean two-bit obstruction and exact interval-specific witnesses |
| Equal marginal frequencies imply independence | Refuted and excluded | Correlated-pair count-one mass is zero |
| Identity separation | Passed in model | Exact equality updates only the selected identity |
| Replay and arbitrary host logs | Conditional boundary preserved | One-step fresh-record bridge; trace itself has no operation IDs |
| Fixed-episode policy composition | Passed | Both bands cover prescribed targets; supplied deterministic memberships retained |
| Availability/performance guarantee | Out of scope | No issuance is allowed and makes the implication vacuous |
| Physical attempt law -> universal accepted-stream coupling | Not claimed | One-attempt retention law plus bounded executable examples only |
| Actual sampling authenticity/stationarity | Not addressed | Explicit supplied modeling assumptions |

## Censoring and completion audit

`ObservationCensoring` defines a normalized four-outcome attempt law. Summing its
fibers gives retained success pa and rejection (1-p)b. With positive retention,
the retained Boolean law has success parameter pa/(pa+(1-p)b). The theorem for
equal positive retention is valid, and necessity assumes the required interior
condition 0<p<1. No zero-denominator conditional probability is used as a law.

The deadline example has two independent fair potential outcomes. A second
report is enabled only after the first success, without inspecting the current
bit. Conditioned on completion, the zero-success count has mass zero instead
of the binomial mass 1/4. The unconditional subset bound and the conditional
bound divided by completion mass are correctly distinguished.

The separate 1,024-path witness in `observation_review_counterexample.json`
uses n=m=10, alpha=1/10, p=1/2. It permits report ten only after nine successes.
Completion mass is 1/512; conditional miscoverage is 1/2; unconditional bad
issuance is 1/1024. At k=9 the interval is [2/5,1], and at k=10 it is [3/5,1].
This was derived independently with exact Fraction arithmetic. It is executable
evidence for that finite counterexample, not a new Lean theorem.

## Executable and interface review

The raw oracle code was inspected and rerun independently with:

    python3 checks/test_observation_process.py --output results/v0.40.0/observation_review_oracle_replay.json

The rerun passed 100 declared experiments: horizons 0 through 4, four predictable
policies, and five probability pairs. It covered 93,620 latent/auxiliary table
rows, 187,240 pathwise prefix checks including zero-weight rows, 600 prefix-law
checks, 843 positive trace-mass comparisons, and 736 unique actual parser
trace/checkpoint cases, plus five interface-boundary checks. The source-pinned
bounded-run result and independent rerun agree on their mathematical results.

The two constructions are meaningfully distinct. One preloads complete
independent report streams plus an auxiliary fault tape; the other recursively
branches into a fault or an admitted Bernoulli report. The auxiliary tape uses
history-dependent weights with explicit normalization for each latent stream.
The independent interval routine enumerates binary vectors rather than calling
the production interval function or using its binomial-coefficient formula.

The attempt tree samples a binary report only after the fault gate admits it.
It does not sample an uncensored physical outcome on each fault branch. Its
equivalence to the latent table is established only for the declared finite
cases. The universal Lean conclusion instead starts from the explicit source
contract; no general stochastic-scheduler coupling theorem is claimed.

Actual parser tests retain successes and rejections, exclude faults, ignore
identical replay, reject conflicting replay and unregistered/insufficient
checkpoints, and ignore reports beyond the selected prefix. They also explicitly
show that a supplied log with omitted rejections can be accepted: completeness
and authenticity are not inferred by the parser. No checked path invokes a
paid operation, retries one, deploys, or acknowledges a durable plan.

## Release-gate findings and resolution

Two concrete fail-closed defects were identified during review and fixed by
the release-infrastructure author:

1. Required evidence parsed as an empty object/list could skip truthiness-guarded
   validation. The loader now rejects empty or wrong-type evidence; only the two
   specified list artifacts accept nonempty lists, and other evidence requires
   nonempty dictionaries.
2. A negative proof record could accept an arbitrary nonzero exit code if a
   preceding log diagnostic looked substantive. The validator now requires the
   ordinary Lean error exit code exactly 1, excluding crashes and timeouts.

Fourteen isolated mutation probes against the actual revised loader/classifier
passed. They exercised malformed evidence, valid structural cases, and abnormal
negative exit codes. No project source or production evidence was mutated.
`observation_review_gate_mutations.json` pins both reviewed script revisions.
The collector's added bounded-oracle manifest checks were also inspected.
This is a focused gate review, not a universal verifier-correctness theorem.

The shortcut scanner was also inspected. Its `admit` check must distinguish the
inherited domain identifier from a proof tactic. The refined regular expression
is a heuristic for selected tactic forms, not a complete Lean parser; warnings
as errors and the exact axiom audit provide the substantive protection against
admitted proofs. The scanner's zero-hit count is interpreted within that scope.

## Exact remaining limits

The final sources contain a real primitive-law derivation and an actual recursive
prefix proof. Remaining assumptions concern the physical applicability of that
model, predeclared schedules, true parameter strata, full authenticated input
logs, and deterministic realization values. Quotes remain frozen within the
episode; no cumulative reward/accounting or physical-spending identity is added.
The trace-level operation-ID and host-refinement boundary remains explicit.

The general converse `ProductLaw -> ConditionalLaw` is not formalized here and
is unnecessary for the proved direction. `bernoulliLaw_product` supplies a
normalized product model for every admissible n,p; `fairOne_conditional` gives a
concrete nontrivial conditional-contract example. No stronger converse claim is
used in the final theorem.

Current-source successful warnings-as-errors development compilation records
were checked for all five new modules, including their log hashes and unchanged
source/import flags. The project's clean full rebuild, full axiom inventory,
negative suite, and inherited regressions are separate release gates. This
review does not replace them. No external mathematical citation was needed.

Open blockers for the stated mathematical/interface scope: **none**.
