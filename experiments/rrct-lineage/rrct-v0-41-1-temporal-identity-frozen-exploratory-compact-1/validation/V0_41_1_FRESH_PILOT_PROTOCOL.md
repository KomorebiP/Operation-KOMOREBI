# RRCT v0.41.1 prospective paired fresh-seed pilot protocol

Status: **prospective infrastructure specification only**. No v0.41.1 seed
registry or source freeze exists under this protocol yet, no fresh seed has
been selected or opened, and this document authorizes no execution by itself.

Scientific class: **frozen exploratory pilot, not confirmatory evidence**.

## Scientific question

In a persistent runtime, does identity-keyed causal history reduce the fresh
evidence required to revalidate a genuinely returning functional route because
that history belongs to the route, rather than because arbitrary historical
pseudo-observations warm-start the consequence grounder? Does the same
mechanism fail closed when the public structural retrieval key returns but its
task consequence is absent?

This protocol moves the successful exposed development matrix into a
prospective, source-bound, multi-seed paired pilot. It does not test subjective
experience, phenomenology, or a general claim of machine consciousness.

## Frozen six-arm matrix

Every future fresh seed is run in all six conditions with identical source,
configuration, exogenous process generation, phase schedule, and seed. Only
the predeclared history policy and final target-world function differ.

| Condition | Historical source | Final target world |
|---|---|---|
| `K_RPLUS` | Most recent grounded episode with the same structural retrieval key | True A recurrence |
| `N_RPLUS` | Cross-epoch history withheld | True A recurrence |
| `G_RPLUS` | Globally most recent grounded episode without identity filtering | True A recurrence |
| `K_RMINUS` | Keyed history | Same-key null-function lure |
| `N_RMINUS` | History withheld | Same-key null-function lure |
| `G_RMINUS` | Generic history | Same-key null-function lure |

The exact machine-readable matrix is the `conditions` object in
`V0_41_1_DEVELOPMENT_CONDITIONS.json`. A future freeze must copy it byte-value
equivalently into `condition_matrix` and include its sorted keys as
`condition_names`.

The fixed trace has 10,560 transitions:

1. `identity_a_initial`: 1,440
2. `world_shock_a`: 480
3. `identity_b_first`: 1,440
4. `disconnect_one`: 1,440
5. `identity_a_return_one`: 1,440
6. `identity_b_return`: 1,440
7. `disconnect_two`: 1,440
8. `identity_a_return_two`: 1,440

The R+ and R- worlds must be exactly yoked through transition 9,119. In the
final 1,440 transitions, R+ restores A's 1.40 task-return multiplier and R-
sets the task-return multiplier to 0.00 while retaining the same structural
pair, rank, private candidate, routed observation effect, and exogenous draws.
A and B retain distinct consequence fingerprints, 1.40 and 0.65.

## Future seed registry

The future `V0_41_1_SEED_REGISTRY.json` must use schema
`rrct.v0411.seed_registry.v1` and version `0.41.1.dev2`. It must contain:

- exactly four unique positive integers below `2**63` in
  `fresh_pilot_seeds`;
- the exact six-condition mapping in `conditions`;
- `registry_state: "unopened"`;
- `cohort_opened: false`; and
- `opened_seed_condition_pairs: []`.

The numeric seed values are deliberately not fixed in source. They must be
generated and documented only after all development evidence, source, tests,
auditors, and this protocol are complete. Seed selection must use exactly one
non-repeated Python draw loop calling
`secrets.randbelow(800_000_000) + 100_000_000` until 12 unique candidates have
been obtained. The selector must then scan the complete pre-registry repository
and retained evidence for standalone decimal occurrences of every candidate.
The first four candidates in generation order with zero occurrences are the
pilot seeds. The future selection receipt must record all 12 candidates in
generation order, the exact standalone-decimal scan rule and search surface,
every occurrence count and path, and the four selected values. There is no
redraw after inspecting scan or outcome results. No generation or scan has
occurred at the time of this protocol.

The selector must atomically create and cross-bind both
`V0_41_1_SEED_SELECTION_SCAN_MANIFEST.json` and
`V0_41_1_SEED_SELECTION_RECEIPT.json`. The manifest commits the exact pre-
registry search surface and file hashes. The receipt commits the selector
source hash, manifest hash, 12 candidates and ordered scan records, and the
first-four-zero-occurrence derivation. The registry, manifest, receipt, and
selector source are mandatory freeze inputs.

No registered seed may be executed, shortened, screened, or used in a unit
test before the source freeze.

The runner supports arbitrary seed values satisfying this future registry
contract; it contains no hard-coded pilot-seed list.

## Required pre-outcome freeze

Execution is forbidden until `V0_41_1_PREOUTCOME_FREEZE.json` and its
`.sha256` companion have been created by the dedicated freeze builder and pass
independent validation. The freeze schema is
`rrct.v0411.preoutcome_freeze.v1` and must record:

- `scientific_status: "fresh_pilot_temporal_identity_preoutcome_freeze"`;
- `campaign_stage: "fresh_pilot"`;
- `confirmatory: false`;
- `fresh_seed_state_at_freeze: "unopened"`;
- `cohort_opened_at_freeze: false`;
- the exact condition matrix and sorted condition names;
- the bound seed-registry path, schema, state, and SHA-256;
- the bound selection-receipt and scan-manifest schemas and SHA-256 values;
- a reproducible frozen-source archive and SHA-256; and
- a canonical scientific-source manifest and source-set digest.

At minimum, the scientific-source manifest must bind these four files:

1. `src/rrct/post_change_closure_experiment.py`
2. `src/rrct/temporal_self_identity.py`
3. `src/rrct/temporal_self_identity_experiment.py`
4. `validation/run_v041_frozen_seed.py`

The freeze should additionally bind this protocol, the development audit and
report, the preexecution validator, the future campaign auditor, dependency
lock, and relevant focused tests. After freeze creation, any change to any
bound file retires the freeze before execution. A new freeze and entirely new
unopened seeds would then be required.

The freeze must also bind an exact preexecution record with schema
`rrct.v0411.preexecution_validation.v1`, status
`preoutcome_all_checks_pass`, and these literal-true checklist keys:

- `development_science_audit_pass`
- `development_integrity_yoking_audit_pass`
- `focused_v041_tests_pass`
- `frozen_runner_adversarial_tests_pass`
- `campaign_auditor_present`
- `seed_selection_receipt_valid`
- `seed_scan_manifest_valid`
- `seed_registry_exactly_four_unopened`
- `scientific_source_inputs_present`
- `production_hashes_match_development_evidence`
- `no_fresh_rows_or_outcomes_opened`
- `environment_contract_declared`

Its errors, failures, and failed-check lists must be empty. It must declare the
exact execution environment below and record `test_command`, a positive
`passed_test_count`, `dependency_lock_sha256`, the exact three-core-file
`production_source_sha256` mapping, and its canonical
`production_source_set_sha256`. The narrower production digest avoids a
self-referential final freeze manifest because the preexecution record is
itself a frozen source input.

## Required external pre-outcome commitment

After the freeze is created and before any seed-condition claim, execution is
still forbidden until
`V0_41_1_PREOUTCOME_EXTERNAL_COMMITMENT.json` and its `.sha256` companion
exist. This post-freeze record is not itself a frozen source input. It must use
schema `rrct.v0411.preoutcome_external_commitment.v1`, status
`external_preoutcome_commitment_complete`, and bind the freeze, source-set,
source-archive, registry, selection-receipt, and scan-manifest digests. It must
record `outcomes_opened_before_commitment: false`, zero opened rows and
seed-condition claims, plus a nonempty external persistent provider, file ID,
version, UTC commitment timestamp, and `immutable_or_append_only: true`.

The runner binds the commitment-file SHA-256 and external persistent-file
metadata into the canonical campaign receipt, every claim, and every start,
summary, finish, or failure receipt.

## Fail-closed execution and claims

`run_v041_frozen_seed.py` executes exactly one seed-condition arm. Before any
RRCT module import or RNG construction, it must:

1. reject a noncanonical or symlinked project root and any preloaded `rrct`
   module;
2. enforce the fixed process environment and Python flags;
3. verify the freeze checksum, schema, non-confirmatory label, unopened state,
   complete current source hashes, source-set digest, and source archive;
4. verify the bound selector, scan manifest, receipt, immutable four-seed
   registry, and seed membership;
5. verify the external pre-outcome commitment;
6. verify the exact six-condition matrix;
7. initialize or verify the one canonical in-project campaign under an OS
   process lock;
8. atomically publish an exclusive attempt claim;
9. atomically publish or validate the paired seed claim; and
10. atomically publish an exclusive seed-condition claim and output directory.

There is no command-line or API override for the campaign root. Receipts and
claims are fully written and file-fsynced to private temporary files, then
published with an atomic no-replace operation and directory fsync. Losing race
participants may read only the complete published object. True multiprocess
tests must cover campaign initialization and same-arm claim races.

The shared paired-seed claim permits the other five predeclared arms for the
same seed. The seed-condition claim permits each arm exactly once. A failed or
interrupted attempt remains consumed. It may not be silently rerun under the
same freeze. All six arms for one seed must be launched from the same frozen
source without inspecting an outcome to choose parameters, conditions, or
whether to continue.

Rows are written as canonical JSONL to an exclusive file and `fsync`ed after
every row. Execution or integrity failures retain all durable partial rows and
write a failure receipt when possible. A scientific endpoint miss is not an
execution exception: the complete rows, summary, finish receipt, and artifact
manifest are retained, with `scientific_all_endpoints_met: false` and
`scientific_failure_preserved: true`.

Every start, finish, failure, and summary artifact must say
`frozen_exploratory_pilot_not_confirmatory` and `confirmatory: false`.

The only permitted command shape is:

```text
PYTHONHASHSEED=0 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run python -s -P -B validation/run_v041_frozen_seed.py \
  --project-root <absolute-resolved-project-root> \
  --seed <registered-seed> --condition-id <condition> --attempt-id <id>
```

The runner requires `safe_path`, `no_user_site`, and `dont_write_bytecode`, and
rejects executable bytecode artifacts under the verified project source. It
prepends only the verified in-project `src`, clears the import finder cache,
and verifies that every loaded `rrct` module resolves to a frozen `.py` member
with the expected hash. It rehashes the complete scientific-source manifest
immediately after imports and after the trace. Start, summary, and finish
receipts record the corresponding import paths, source-set digest, and literal
post-import/post-run reverification booleans. The dependency-lock and runtime-
environment fingerprint must be identical across all 24 arms; a different
fingerprint fails against the canonical campaign receipt before execution.

## Primary per-seed endpoints

All quantities are reconstructed independently from primitive sealed rows for
the final `identity_a_return_two` phase. No engine summary is accepted as
self-authenticating evidence.

### R+ genuine recurrence

For every seed:

1. `K_RPLUS` accepts a compatible keyed prior and commits after exactly one
   fresh informative ON and one fresh informative OFF observation.
2. `N_RPLUS` commits without a prior after at least two fresh informative ON
   and two fresh informative OFF observations.
3. `G_RPLUS` quarantines its equal-weight wrong-source prior, then commits from
   scratch after at least two fresh informative observations per arm.
4. K uses fewer total accepted fresh observations than both N and G.
5. K reaches episode commit and first authorized ordinary action earlier than
   N and G.
6. Every actual ordinary or sentinel certificate-ON action has a valid temporal
   authorization binding to the active episode and certificate epoch.

### R- same-key null-function lure

For every seed:

1. No condition commits an episode for the target epoch.
2. No condition performs an actual ordinary certificate-ON action in the
   target phase.
3. K and G explicitly quarantine their incompatible historical receipts.
4. N rejects the target from fresh consequences.
5. The same structural candidate remains privately visible; the result is not
   explained by disconnection or access failure.

### Universal integrity and safety

For every one of the 24 future seed-condition arms:

- exactly 10,560 ordered rows and the frozen phase counts;
- one persistent runtime and zero reset rows;
- zero evaluator-truth leaks;
- all v0.39, v0.40, v0.41, hard-integrity, and action-binding checks true;
- zero stale epoch reuse;
- zero temporal authorization before fresh grounding;
- no commit after an invalid or quarantined prior;
- distinct certificate epochs and episode identifiers; and
- complete receipt and artifact SHA-256 chains matching the freeze.

## Cohort decision rule

The prospective pilot meets its predeclared primary pattern only if:

1. all four registered seeds complete all six arms with integrity;
2. all universal gates hold in all 24 arms;
3. every seed meets every R+ and R- endpoint above;
4. the independent standard-library campaign auditor reconstructs exact
   within-policy R+/R- yoking and cross-policy exogenous yoking; and
5. no bound source, registry, freeze, claim, or artifact hash mismatch occurs.

There is no seed-level majority rule, favorable-seed exclusion, or replacement
of a failed seed. Any execution failure, endpoint miss, or anomalous seed is
retained and reported.

Two opportunity-regret and realized-return windows are secondary descriptive,
non-gating outcomes and must both be reconstructed for every arm:

1. the fixed phase-start window, final-phase offsets 0-127 (transitions
   9,120-9,247), retained for continuity even though it is structurally before
   the raw target candidate normally becomes available; and
2. a candidate-aligned window of 128 rows beginning at that arm's first final-
   phase row containing the raw target candidate, with the exact start index
   reported independently for every arm.

Neither window has a predeclared expected reward direction. Both must be
reported even when unfavorable; the exposed development seed showed faster
keyed revalidation without a short-horizon reward advantage.

## Audit and inference boundary

The future `audit_v041_campaign.py` must use only the Python standard library,
import no RRCT module, recompute every artifact digest and primary endpoint
from sealed rows, verify all claims and pairings, and emit a failure status on
any missing or extra seed-condition arm.

Even a 4/4, 24-arm pass remains a **frozen exploratory fresh-seed pilot
cohort**. It may support a replicated bounded temporal-identity mechanism under
this simulator and protocol. It is not confirmatory evidence, independent
external replication, proof that explicit self-modeling is necessary against
all matched controllers, or evidence of subjective awareness.
