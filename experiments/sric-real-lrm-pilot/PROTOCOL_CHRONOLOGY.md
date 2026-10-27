# Protocol Chronology

## Phase A — immutable external identity

1. Clone the external repository.
2. Check out commit `32f413d8d55239d9bc54bb6b6ec37b0630891ed4`.
3. Download `checkpoint_37` from the declared Hugging Face repository.
4. Download or identify the GPT-2 base-model snapshot.
5. Hash the complete checkpoint file.
6. Verify the PrOntoQA data file and repository commit.

## Phase B — adapter smoke

1. Load the checkpoint through the external wrapper.
2. Run a small non-final smoke subset.
3. Capture latent traces.
4. verify trace dimensions and finiteness.
5. verify exact replay in float32.
6. compare direct, verbalized, and latent execution for formatting sanity.

No primary scientific result is taken from this set.

## Phase C — calibration

1. Estimate replay numerical tolerance.
2. Estimate effect variance on a disjoint calibration subset.
3. decide task count and group structure.
4. freeze thresholds in the config.
5. freeze intervention seeds and donor rules.

## Phase D — pre-audit seal

The `stage-real` command freezes:

- config;
- repository commit;
- checkpoint hash;
- dataset hash;
- deterministic task subset;
- donor assignment;
- maximum claim.

The seal contains no outcomes.

## Phase E — final execution

1. Recompute and verify every sealed identity.
2. run ordinary trace capture.
3. run exact replay.
4. terminate interpretation if replay fails.
5. run zero, permutation, and noise interventions.
6. run procedure-donor and twin-donor interventions.
7. generate paired rows and grouped intervals.
8. assign the first failed status in the gate hierarchy.
9. write a canonical result receipt.

## Phase F — preservation

1. preserve the raw result regardless of sign;
2. do not alter thresholds;
3. rerun receipt verification;
4. record environment and runtime logs;
5. add the result to the SRIC evidence ledger;
6. begin Pilot 0.2 only if scientifically justified by Pilot 0.1.
