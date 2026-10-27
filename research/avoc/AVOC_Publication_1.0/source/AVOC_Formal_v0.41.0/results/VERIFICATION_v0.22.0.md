# AVOC v0.22.0 — final verification

## Source and proof checks

- Baseline archive SHA-256:
  `0574ac8e89e14858a81d76a3140c116fe1ab2d9c6bb6f6ca1b04139d1f8060d2`.
- Baseline ZIP CRC and 4,174 delivered hashes matched before editing.
- The seven portable-runtime parts and combined archive SHA-256 matched before extraction.
- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine dependency revision checks pass.
- 104 inherited non-audit mathematical source modules are byte-identical to v0.21.
- Six new modules contain 62 theorem/lemma declarations.
- Complete inventory: 1,132 named theorem/lemma declarations in 110 non-audit modules,
  17,639 non-audit Lean source lines. Counts include helpers and examples.
- Final clean local build: 119/119 targets passed with warnings treated as errors.
- Full axiom audit: 1,132/1,132 exact expected names; only `propext`,
  `Classical.choice`, `Quot.sound` appear.
- Positive-source scan found no proof placeholders, project axioms,
  native-evaluation shortcuts, or unsafe declarations.
- Negative suite: 50/50 current-source substantive rejections, without missing
  imports, setup failure, or timeout counted as evidence.

The final local build began with an empty project output directory AFTER proof
source was finalized. A host execution limit interrupted the first build slice;
no Lean child remained running, and unfinished targets were resumed. External
binary caches were retained. This is not a new source rebuild of all mathlib,
an independently implemented kernel check, or a verification of the physical host.

## New negative witnesses

- `FalseFaultKeepsReliability`: incorrectly equates the after-fault predictive
  resolve rate 9/50 with its initial value 1/2.
- `FalseMyopicRetryAlways`: incorrectly gives zero value to the improving-service
  two-step counterexample whose proved value is 8.
- `FalseMarginalDeterminesRetryValue`: incorrectly equates persistent-mixture value
  1 with fresh-i.i.d. value 7/4 at the same initial marginal and three attempts.

Positive theorems establish the counterexamples independently. A failing proof
script alone would not be proof of the mathematical negation.

## Executed advisor and independent oracle

`checks/test_retry_advisor.py` ran the actual Lean JSON entrypoint and compared it
with a separately implemented exact-rational oracle. The oracle evaluates all
possible stopping cutoffs by integrating completed-operation benefit and each
attempt cost directly over hidden types; it does not implement Bayes recursion.

- 5,400 base comparisons.
- 491 explicitly supplied operational-fault comparisons.
- 72 impossible fault observations correctly rejected within those 491.
- 11,624 independent cutoff values evaluated across supported cases.
- 10 invalid wire requests rejected.
- 2 phase guards: published result requests reconciliation; terminal ledger returns
  no action.
- 4 Python-wrapper schema/type rejections.
- All output values, actions, predicted ledger updates, evaluation-node counts,
  and threshold-versus-DP comparisons matched.

Three current-source CLI demonstrations are retained as `demo_persistent.json`,
`demo_fault.json`, and `demo_iid.json`. They are read-only advice from declared
inputs, not live-store retries or empirical tool observations. Earlier filesystem
and crash test logs stay historical; those full old suites were not rerun here.

## Evidence files

`results/v0.22.0/verification_summary.json` is produced by a fresh evidence
collector that rechecks source, output and log hashes for each compilation;
substantive negative diagnostics; the exact axiom inventory; preserved baseline
mathematical sources; and the current differential-test data and source hashes.
The raw batch requests/results and process records are retained.

The optional computation manifest times the evidence collector only. The
included v1-only manifest validator checks metadata/output bytes, not theorem
meaning or the universal implementation boundary.
