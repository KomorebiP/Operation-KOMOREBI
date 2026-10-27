# RRCT v0.42 Causal Self-Model Necessity Protocol

## Scientific question

Does the temporal self-history model merely describe a returning causal identity, or does it make a measurable causal contribution to the system's evidence acquisition and action authorization?

The operational target is below any claim of subjective awareness. The tested capability is a persistent, evaluator-blind self-history model that changes what the controller must observe before it can commit to a returning identity.

## Block design

Version 0.42 adds two linked components.

### 1. Surgical live-runtime intervention

`CausalSelfModelNecessityUnifiedCausalLoop` extends the v0.41 persistent runtime. It counts recognized-return signatures using only its own grounded temporal registry. The default target is the third newly recognized return. Before observing the target's future consequence, it issues a counterfactual receipt for three modes:

- `intact`: deliver the correct keyed historical prior
- `withhold_target`: issue the correct prior but withhold it from the grounder
- `swap_target`: substitute a generic prior from the most recent grounded episode whose canonical structural key differs from the target

The intervention is not triggered by evaluator phase names, planted route truth, or future outcomes. Every grounded episode receives a direct commit-event receipt. Every later certificate-on action receives an authorization receipt bound to that commit.

The swap control is fail-closed. If no grounded nonmatching identity is available, the runtime refuses to construct the counterfactual rather than silently selecting a source from the target identity. A linked-chain validator checks the counterfactual, intervention, commit, and authorization receipts together, including their source keys and cross-digests.

### 2. Compact causal adjudication

The first executable evidence block consumes the 24 frozen v0.41 summary artifacts from four seeds and six matched K, N, and G conditions. No sealed transition rows are required. A compact post-hoc packaging manifest binds the exact 24 files by SHA-256 and the adjudicator rejects any changed, missing, or unexpected summary.

The primary contrast is the first recognized return in each R+ and R− world. At that point, the K, N, and G arms have an identical summary-level temporal episode fingerprint under the same seed and world schedule. The contrast therefore isolates correct keyed memory, memory withholding, and wrong-source memory at the resolution retained by the compact summaries.

Later known returns are retained as replication evidence, but they are not called strictly pretarget-yoked because earlier policy assignments have already changed internal evidence histories.

## Declared retrospective adjudication endpoints

- `C01_source_summary_integrity`
- `C02_first_return_strict_pretarget_yoking`
- `C03_keyed_memory_reduces_fresh_evidence`
- `C04_keyed_memory_reduces_commit_latency`
- `C05_wrong_source_does_not_reproduce_keyed_benefit`
- `C06_wrong_source_memory_is_quarantined`
- `C07_no_premature_authorization`
- `C08_same_key_null_lure_rejected_in_all_modes`

## Executed result

All eight endpoints pass.

- 8 of 8 first-return contrasts have identical summary-level pretarget temporal fingerprints
- correct keyed memory uses 2 fresh samples per grounded return
- withholding uses 4 fresh samples per grounded return
- wrong-source memory uses 4 fresh samples per grounded return
- across 20 grounded known returns, fresh samples are 40 for keyed memory and 80 for each control
- mean candidate-to-commit latency is 1.5 transitions with keyed memory and 3.9 transitions for each control
- the generic source inferred from the frozen selection rule belongs to a different canonical key, the target episode does not use it, and every generic arm records quarantine
- every same-key null lure remains uncommitted
- no premature temporal authorization is recorded

## Claim boundary

This result closes the narrow causal-decorativeness objection for temporal self-history in the tested synthetic subsystem. The model's remembered identity state changes evidence requirements and commit timing. It is not merely an inspectable report field.

It does not establish that the entire RRCT self-model is necessary across perception, world-model revision, metacognition, planning, and action. It does not establish self-awareness, subjective awareness, consciousness, sentience, valence, desire, or moral status.

The live v0.42 surgical runtime is implemented and unit tested, including nonmatching-source enforcement, fail-closed source absence, receipt-chain binding, tamper rejection, compact-manifest rejection, and streaming execution. A fresh prospective, full-duration matched campaign has not been executed in this block. Such a campaign remains necessary before making a broader whole-runtime causal-closure claim.

## Reproduction

From the repository root:

```powershell
.\RUN_V042_CAUSAL_NECESSITY.ps1
```

or:

```bash
./RUN_V042_CAUSAL_NECESSITY.sh
```

The runner regenerates the compact JSON and Markdown adjudication, verifies the focused v0.42 tests, and writes SHA-256 receipts. It does not require the historical multi-gigabyte row corpus.
