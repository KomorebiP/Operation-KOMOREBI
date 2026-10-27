# PRSC VIII — Checked First Lean Block v0.1.0

**Author: Komorebi P.**

Source paper: *Packet Operator Algorithms, Exact Compilation, and GPU Realization*, strengthened edition of August 14, 2026.

## Checked scope

Ten of the source manuscript's 56 proved theorem/proposition/corollary items are covered: **2.3, 2.5, 2.6, 5.1, 5.3, 5.4, 6.1, 6.2, 6.3, 8.1**. There are 46 not fully covered items and four separate classical inputs. The new positivity audit for 8.4 is not counted as a completed optimization theorem.

Five new modules contain **41 theorem declarations**. One unchanged Paper VII foundation module contributes **19 reused declarations**. All six modules and all 60 theorem axiom audits passed a fresh cumulative run. One actual coordinate-projector construction passed a separate audit. Both invalid controls were rejected. Seventeen Python verifier regression tests passed.

Allowed theorem dependencies are `propext`, `Classical.choice`, and `Quot.sound`. The active modules contain no admitted proofs, declared axioms, unsafe definitions, or native-decision proofs. The failed development snapshots are evidence, not part of the active import graph.

## Reproduce the Lean checks

Use the portable **Linux x86_64** kit (or a compatible Linux/WSL environment) with Lean **4.34.0-rc2** and Mathlib **aeb72f1e9981b6d35b426b16dca7759be3e7ba06**. The multi-gigabyte portable runtime and Mathlib cache are not duplicated in this paper ZIP.

From this extracted release directory:

```bash
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/rerun --timeout 240
python scripts/test_verifier.py
```

On a host that interrupts long commands, repeat this checkpointed command until it reports `COMPLETE PASS`:

```bash
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/rerun --timeout 240 --max-checks 2 --resume
```

Exit code 2 is a deliberate pause, not a completed check. Exit code 1 is failure. Only exit code 0 with a complete report is PASS. Sources, transitive local dependencies, compiled public/private artifacts, logs, runtime pins, and audit inventory are checked before cached results are accepted. Run without `--resume` to force a fresh sequence.

The launcher captures Lake's environment, lets Lake exit, then invokes ordinary Lean with one worker and warnings treated as errors. It does not impose a memory cap or weaken proof checking.

## Reproduce the original numerical suite

```bash
python scripts/rerun_numerical.py
```

This extracts the preserved original source ZIP to a temporary directory and runs its existing CPU verification code. The fresh run passed **37,392 checks in nine groups**. Some checks validate the consistency of historical CPU/GPU benchmark records. **No new GPU benchmark or historical hardware-timing reproduction was performed.**

## Contents

`formalization/` contains the six active Lean modules. `manuscript/` preserves the original PDF, TeX, bibliography, register, and original package. `notes/` contains the supplement, coverage ledger, and required statement amendment. `verification/final/` contains the successful fresh Lean run and compiled local outputs. `verification/development/` preserves all 15 captured development source snapshots and logs, including nine failed checks. `verification/numerical_rerun.json` is the fresh CPU-suite report. `scripts/verify_integrity.py` checks the distributed-file manifest.

## Boundaries

This is a first block, not a completed Paper VIII. The continuous-allocation statement needs a positive budget on a nonempty edge set. Its corrected optimality theorem, precision programs, tree compiler, recompression analysis, Krylov results, cost models, and other listed items remain to be formalized.

The original manuscript is unchanged. This supplement does not certify CUDA kernels, prove GPU speedups, establish a new matrix multiplication exponent, or solve unrestricted structure discovery. Imported Mathlib proofs were not independently rechecked, and Papers I–VII were not rebuilt in full.
