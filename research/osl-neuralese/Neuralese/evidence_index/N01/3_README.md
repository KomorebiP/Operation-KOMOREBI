# Post-hoc analysis tools

These scripts are outside the immutable experimental-code digest. They consume a completed run without changing its frozen protocol, checkpoints, or primary metrics.

## Interrupted-run recovery

The original Stage-A primary process was stopped by the execution supervisor
after 17 of 48 cells, without an exception or `FAILED.json`. Because the
frozen runner resets NumPy and Torch to the cell's seed before every training
run, the remaining cells can be scheduled independently without changing
their computation. `resume_primary.py` validates the copied protocol, frozen
digests, coordinate split, existing JSON/checkpoint pairs, initialization
receipts, configs, tensor schemas, and sampling audits before skipping any
cell. It then commits a bounded number of missing cells, using atomic
replacement for each record and checkpoint file and fail-closed pair checks
on the next invocation.

The completed run was recovered with bounded invocations equivalent to:

```bash
python analysis_tools/resume_primary.py --protocol protocols/V0_3_STAGE_A_PRIMARY.json --output-dir results/v0.3.0/stage_a_primary_v3 --device cpu --threads 4 --max-new-cells 8 --max-new-transports 0
```

The final invocation used `--max-new-cells 0 --max-new-transports 6`. Recovery
events are recorded in `RECOVERY_EVENTS.json`; finalization is refused until
all 48 frozen cells and all six transport pairs are present. This tool is for
recovering an interrupted run, not for changing a completed receipt.

## Paired bootstrap

```bash
python analysis_tools/paired_bootstrap.py --primary-dir results/v0.3.0/stage_a_primary_v3 --output-dir results/v0.3.0/stage_a_primary_v3 --replicates 100000
```

The default is 100,000 seed-paired bootstrap replicates per available metric and contrast. Every NumPy `PCG64` seed is derived from the SHA-256 digest of the complete input-file inventory plus a canonical contrast specification. The JSON output records raw per-seed deltas, hashes, seeds, and confidence-interval conventions. These are explicitly exploratory summaries, not retroactive confirmatory gates.

Run its synthetic deterministic check with:

```bash
python analysis_tools/paired_bootstrap.py --self-check
```

## Single-cell exact replay

After the primary run is complete, replay the default `hard_correct`, seed-300
cell with the primary runtime settings and compare its scientific payload:

```bash
python analysis_tools/replay_verifier.py --primary-dir results/v0.3.0/stage_a_primary_v3 --output-dir results/v0.3.0/stage_a_reproducibility --arm hard_correct --seed 300 --device cpu --threads 4
```

The output directory must be absent or empty and cannot be inside the primary
directory. The tool executes a one-arm, one-seed protocol with transport and
the oracle disabled, then writes `REPRODUCIBILITY.json`, `REPRODUCIBILITY.md`,
`REPLAY_PROTOCOL.json`, and `REPLAY.log` alongside the ordinary runner output.

The pass condition requires recursively exact metrics, an exact semantic arm
record after the declared provenance/time/path exclusions, identical state
keys/dtypes/shapes/layouts, bit-identical tensor data, and equal canonical
state and checkpoint SHA-256 digests. Raw `.pt` hashes are retained as
informational values because the replay checkpoint necessarily records a new
protocol identifier and digest.

Run the comparison-primitive check without training with:

```bash
python analysis_tools/replay_verifier.py --self-check
```
