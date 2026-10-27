# RRCT v0.36 handoff

Current tree: **0.36.0.dev2**  
Executed pilot source: **0.36.0.dev1**, preserved exactly inside the evidence  
Scientific status: exploratory single-seed pilot; no development or
confirmatory campaign

## Read first

The fastest accurate orientation is:

1. `validation/V0_36_PILOT_REPORT.md` — result and scientific interpretation.
2. `validation/V0_36_DEVELOPMENT_PROTOCOL.md` — the pre-outcome D0 design.
3. `validation/V0_36_PILOT_ATTEMPTS.md` — append-only exposure history.
4. `validation/V0_36_POSTPILOT_HARDENING.md` — dev2 infrastructure changes.
5. `src/rrct/unified_causal_loop.py` and
   `src/rrct/unified_causal_loop_experiment.py` — live runtime and evaluator.

## What ran

P-0002 used pilot seed 6451 for 4,800 transitions in one persistent runtime:

- stable acquisition and warm-up: 1,440;
- world-only shock: 480;
- hidden interface remap: 960;
- disconnection: 960;
- restoration: 960; and
- one exact terminal flush.

Every literal per-seed endpoint E01-E08 and every recorded integrity field
passed. Independent audit reproduced the endpoints, ordering, phase counts,
hashes, bank replays, receipt chain, and terminal closure.

The correct result label is `PILOT_ENDPOINTS_MET`. The sealed dev1 summary's
`UNIFIED_DEVELOPMENT_TARGET_MET` string is a known pilot-label bug and is not
rewritten.

## What the result means

The run supports:

- initial truth-free rank-two boundary discovery;
- workspace-gated release of that learned identity;
- public identity-conditioned prediction/action after initial discovery;
- retained functional use during a large world-only shock; and
- later private revision, revocation, and reacquisition without resetting the
  persistent runtime.

It does **not** yet support post-change functional recovery. Revision,
revocation, and reacquisition occurred on terminal phase reveals, so remap,
disconnect, and restoration each had zero subsequent correctly gated actions.
The public certificate is capability-gated learned state, not a demonstrated
decoder of workspace content. Candidate transition predictions are logged but
not used in rollout planning. Nothing here establishes phenomenal awareness,
subjective experience, sentience, or valence.

## Evidence identity

The immutable P-0002 evidence is in
`validation/v0.36_unified_causal_loop_pilot_6451_d0_attempt2`.

- rows: `765ad5f32043e7dab9af42ca7d62263d5b11b8cb379e7b6972f51fd548e4839a`
- summary: `84fbbb412529828b5941727228e921350d4df0b9ef94c5f13198e570a8c20a36`
- exact dev1 executed source:
  `f352791b7b176325b2e4ecbc1fade93b37ea96c1d51015ac6985ad6e4a0acbf3`

The executed-source tar validates against its own embedded pre-execution
manifest. The current dev2 checksums are separate because dev2 was created
after outcome exposure.

## dev2 safety state

Dev2 adds durable pre-RNG claims/start receipt, a canonical locked ledger,
per-row fsync, strict tagged failure evidence, immediate pre-consequence hard
stops, explicit `INTEGRITY_FAIL` receipts, cohort-correct labels, and exhaustive
development-freeze verification. Retrospective permanent claims consume
P-0001, P-0002, and seed 6451.

No further reserved seed was opened. Development execution intentionally fails
closed because `validation/V0_36_PREOUTCOME_FREEZE.json` and its companion do
not exist. Do not create that freeze for D0 merely to obtain more green rows;
first write a successor protocol that includes a post-revision action tail.

## Verification

From the project root, using a compatible Python environment:

```bash
sha256sum -c validation/V0_36_DEV2_SOURCE_AND_EVIDENCE_SHA256SUMS.txt
python -m pytest -q tests/test_v036_unified_causal_loop.py tests/test_v036_development_protocol_spec.py
python -m pytest -q
```

The delivered tree passed 32 focused tests, 83 expanded lineage tests, and the
full suite of 427 tests plus 89 subtests, with two intentional skips. Ruff and
Python compilation checks passed.

## Next major block

Predeclare a D1/post-change-closure design with enough fixed time after each
confirmation for:

\[
\text{new private boundary}
\rightarrow
\text{new public certificate}
\rightarrow
K\text{ actions}
\rightarrow
\text{prediction/control recovery}
\rightarrow
\text{devaluation/revaluation}.
\]

Require separate bounds on alarm, revision, public-release, and first-correct-
action latency. Compare against frozen stale-certificate, no-certificate, and
shuffled-certificate controls. Then make the transition model drive actual
counterfactual rollouts before integrating continuity value, reflection, and
the anonymous meta-criterion into this same persistent runtime.
