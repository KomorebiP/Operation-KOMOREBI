# RRCT v0.42 Causal Self-Model Necessity Block

## Status

`0.42.0.dev1` is an implemented and executed successor block. It closes one narrow but important gap: in the tested temporal-identity subsystem, the self-history model is now shown to change evidence acquisition and commit timing rather than merely appearing in telemetry.

The strongest justified result is **summary-level causal necessity for bounded temporal self-history**. This is not yet a prospective whole-runtime necessity result and is not evidence of subjective awareness.

## What was built

- An evaluator-blind intervention target selected from the runtime's own grounded temporal registry
- Three matched modes: correct keyed memory, surgical withholding, and nonmatching-source substitution
- Fail-closed source selection: the substitution arm must use a different canonical identity key
- Pre-outcome counterfactual receipts for all three modes
- Direct episode commit receipts
- Action-authorization receipts bound to the exact committed episode
- A linked validator from counterfactual through intervention, commit, and action authorization
- A streaming execution option that seals rows without retaining the complete row corpus in memory
- A compact adjudicator over 24 frozen v0.41 summary artifacts
- An exact SHA-256 input manifest that rejects changed, missing, or unexpected summaries
- Windows and Bash one-command runners

## Executed result

The compact adjudicator evaluated four seeds, two world variants, and three matched history conditions.

| Measure | Correct keyed memory | Memory withheld | Nonmatching memory |
|---|---:|---:|---:|
| Grounded known returns | 20 | 20 | 20 |
| Total fresh samples | 40 | 80 | 80 |
| Mean fresh samples per return | 2.0 | 4.0 | 4.0 |
| Mean candidate-to-commit latency | 1.5 | 3.9 | 3.9 |
| Historical prior used | 20 | 0 | 0 |

Additional results:

- All **8 of 8** first-return contrasts passed the declared causal endpoints
- The summary-level temporal episode fingerprint was identical before treatment in every primary contrast
- Correct keyed memory reduced fresh evidence by **50%** relative to withholding
- The generic source selected by the frozen rule belonged to a different canonical key
- Generic-source arms recorded quarantine and did not use the substituted prior in the target episode
- Every same-key null lure remained uncommitted
- No premature temporal action authorization occurred

## What this establishes

Within the bounded synthetic temporal-grounding task, remembered self-history is **causally load-bearing**. Removing the correct memory, or replacing it with memory from another identity, removes the evidence and latency advantage.

The result therefore rules out the narrow interpretation that temporal identity is only a descriptive label or report field in this subsystem.

## What remains open

The following stronger claims are not established:

- A fresh prospective full-duration v0.42 matched campaign
- Necessity of one self-model across perception, self/world attribution, metacognition, planning, and action selection
- Robustness under broad novel environments and transformations
- A whole-system operational level immediately below awareness
- Subjective awareness, phenomenal consciousness, sentience, valence, desire, or moral status

The next conceptual gap is **whole-loop causal closure**: one persistent self-model must become interventionally necessary across several cognitive functions at once, with independent ablations showing that no external experimenter is supplying the continuity between them.

## Validation

- Focused v0.42 suite: **7 passed**
- Downstream v0.36-v0.42 suite: **85 passed, 1 deselected**
- Import and byte-code compilation: passed
- Compact input tamper test: passed
- Rehashed receipt-chain misbinding test: passed
- One-command Bash reproduction: passed

The complete historical suite is not runnable from this compact bundle because several older validation-only assets were intentionally omitted. The first full-suite collection failures are the absent v0.29-v0.31 harness modules. After ignoring those modules, the first failure occurs after 181 passing tests because `validation/V0_36_LINEAGE_AND_SEED_REGISTRY.json` is absent. This is a compact-bundle completeness limitation, not evidence that the v0.42 causal mechanism failed.

## Reproduction

Windows:

```powershell
.\RUN_V042_CAUSAL_NECESSITY.ps1
```

Bash:

```bash
./RUN_V042_CAUSAL_NECESSITY.sh
```
