# PRSC VIII — Checked Second Block v0.2.0

**Author: Komorebi P.**

## Status

**31/56 named manuscript-proved items checked; 25 remain. Four classical inputs are tracked separately.**

This cumulative release contains **129 theorem declarations across 11 modules**: 69 new declarations, 41 earlier Paper VIII declarations, and 19 unchanged reused Paper VII declarations. Five separately audited constructed objects are not added to the theorem count. All 11 modules passed a fresh cumulative Lean run. Both deliberately invalid controls were rejected, and the verifier's 17 regression tests passed.

## New work

| Area | Source items | New declarations |
|---|---|---:|
| Exact compiler, shared family, frontier, stability, cached local updates | 9.4–9.7, 9.11, 9.12 | 21 |
| Actual logarithmic allocation optimizer | 8.4, corrected positive-budget statement | 9 |
| Scalar storage, modeled arithmetic, streaming, roofline, capacity, materialization | 3.1, 3.2, 3.4, 3.6, 3.8–3.10, 4.2 | 22 |
| Output contracts, grouping, reuse thresholds, fair-match equivalence | 2.9, 10.2, 10.4–10.6, 11.3 | 17 |

`notes/COVERAGE_LEDGER.md` gives every source item, exact formal scope, and named Lean witnesses. `notes/Paper_VIII_Second_Lean_Block_Supplement.pdf` gives the mathematical exposition. The original manuscript is preserved unchanged, so its missing positive-budget hypothesis is corrected explicitly in the supplement and amendment ledger.

## Reproduction

The runtime must be the existing Linux x86-64/WSL portable Lean 4.34.0-rc2 kit, with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. It is not duplicated in this source ZIP.

From this release directory:

```bash
python3 scripts/verify_integrity.py
python3 scripts/test_verifier.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck --timeout 240
python3 scripts/run_compiler_examples.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --build verification/recheck/build --out verification/recheck_execution
```

In a host with short command limits, run the verifier repeatedly with `--max-checks 2 --resume` and the same `--out` directory. An incomplete checkpoint is not a successful verification. The launcher runs one Lean worker, uses the pinned project environment, and treats warnings as errors. It does not impose a RAM cap or weaken proof checking.

## Verification evidence

`verification/final/SUMMARY.json` records source hashes, commands, exit codes, dependency hashes, theorem/constructor axiom audits, and negative controls. `verification/execution/SUMMARY.json` records **600 exact-rational compiler cases**, comparison against **85,320 exhaustively enumerated pruning scores**, and **600 cached updates compared with full recomputation**. The test source is in `verification/test_sources/CompilerExecution.lean`. Tests are separate from universal Lean theorems.

8 of 13 captured development checks failed before repair. Their source snapshots and logs are retained under `verification/development/`. Previous block evidence and verifier sources are retained under `verification/prior/`.

## Boundaries

The compiler optimizes finite candidate trees with additive scores, not arbitrary overlapping decompositions or a universal hardware cost. No running-time theorem is claimed for the returned-cut wrapper. The cached update algorithm uses stored sibling values.

The continuous optimizer is real-valued and noncomputable; it is not a numerical precision-selection implementation. Clipped allocation and quantized-budget optimization remain unformalized. Cost counts are declared mathematical event models, not measured wall times or verified CUDA kernels. Contract matching cannot certify measurement accuracy.

This block did not rerun the original 37,392-check CPU suite or any GPU measurements, rebuild Papers I–VII in full, or independently recheck all imported Mathlib proofs. The original CPU/GPU reports in prior evidence remain historical records.

## Preserved source

The original manuscript PDF/TeX/bibliography/register/source package, the first supplement, and all six upstream Lean source files match v0.1.0 byte for byte. See `verification/preservation.json`. No completed earlier paper is modified by this release.

The manifest verifies file integrity, not external authorship or a cryptographic signature of truth.
