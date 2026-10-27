# Projector-Resolved Seed Calculus VII
## v0.4.0 — Checked fourth block

**Author: Komorebi P.**  
**Date: September 6, 2026**

This release fully closes Theorem 5.2 and adds substantial, explicitly bounded formalizations for items 6.4 and 8.1. It does **not** claim that Paper VII is fully formalized.

| New module | Declarations | Verified scope | Manuscript status |
|---|---:|---|---|
| `LeakageBound.lean` | 17 | Actual exponential, quantitative leakage, unitary cap, symmetry-breaking perturbation estimate, concrete complex matrices with the Hilbert operator norm | 5.2 fully checked |
| `ProjectedCurvature.lean` | 20 | Actual Fréchet derivatives, projected connection, vector-field Lie bracket, curvature formula, bilinearity, alternation, and differentiable pullback | 6.4 partial: normed parameter-space formulation |
| `SyndromeRecovery.lean` | 18 | Explicit recovery from orthogonal partial isometries, complement Kraus operator, cross-error correction, mixtures and coherent superpositions, trace preservation and complete positivity | 8.1 partial: constructive recovery stage |
| **Added** | **55** | Supporting lemmas are included in this count | **One additional full manuscript item** |

## Cumulative status

**201 theorem declarations in 15 modules.** The exact inventory is `verification/theorem_inventory.json`. There are **17 of 19 named finite-sector manuscript statements fully checked**, with two partial formalizations. This is not a difficulty-weighted percentage. All five continuum conjectures remain unproved.

The twelve upstream Lean modules and the original manuscript PDF and TeX are unchanged. The prior supplements are also preserved. `verification/UPSTREAM_PRESERVATION.json` checks 21 retained files against the exact third-block archive.

## Exact boundaries

**5.2 is complete.** The source proves the actual matrix-exponential bound for every real time, every finite complex matrix dimension, and every orthogonal projector, including the zero projector. The matrix norm is `Matrix.Norms.L2Operator`, not the entrywise norm or the row-sum operator norm. The proof works more generally in a unital complex C-star algebra. No unbounded-generator or time-dependent-Hamiltonian theorem is claimed.

**6.4 remains partial.** The formula is established for actual vector-valued sections and vector fields on normed real parameter spaces, including the noncommuting-vector-field correction. The functions in the main theorem have global parameter-space regularity hypotheses. Localization to arbitrary chart domains, construction of the global smooth range bundle, and chart gluing over an arbitrary manifold are not implemented. The pullback theorem proves the first-derivative tensor transformation, not the missing bundle construction.

**8.1 remains partial.** Recovery is constructed from a supplied orthogonal syndrome family satisfying explicit partial-isometry relations. This is not a definition of exact correctability designed to make the equivalence tautological: the decoder is an actual finite Kraus map, and its correction, trace and positivity properties are proved. Still missing are reduction of general Knill–Laflamme Gram data to such a family, including zero eigenvalues, and the full necessity direction. Algebraic normalized-mixture recovery permits complex weights; a physical noise mixture additionally uses nonnegative real probabilities.

## Reproduce

Use the extracted portable Linux x86_64 kit containing Lean 4.34.0-rc2 and its pinned dependencies:

```bash
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

On hosts with short command limits, use resumable chunks and the same output directory:

```bash
python scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run --max-checks 3 --resume
```

Exit codes are 0 for a complete PASS, 1 for a failure, and 2 for a deliberately paused/incomplete run. Successful resume entries require matching source, log, runner, verifier and runtime hashes. The low-memory launcher itself is unchanged.

The audit parser was corrected to recognize explicitly axiom-free theorem reports. Seven parser regression tests passed, and all fifteen Lean modules were then checked afresh. The initial audit failure is preserved separately; no theorem was changed to fix the parser. Run `python scripts/test_verifier.py` to repeat the parser tests.

The verifier checks every active module with warnings treated as errors, scans active source for proof escapes, audits every theorem's axioms, and rejects two deliberate negative controls. Allowed theorem dependencies are `propext`, `Classical.choice`, and `Quot.sound`. The report's `pass` flag concerns the stated source checks, not completion of all manuscript statements.

## Evidence and documents

- `verification/fourth_block_release_run/SUMMARY.json`: fresh cumulative checks, commands, exit codes, timings, hashes and axiom audits.
- `verification/fourth_block_development/`: attempted sources, failed diagnostics and intermediate successful runs. These are not the release proof modules.
- `verification/UPSTREAM_PRESERVATION.json`: byte-for-byte upstream preservation.
- `verification/ARTIFACT_CHECK.json`: final package and document audit.
- `THEOREM_LEDGER.json` and `THEOREM_LEDGER.md`: current manuscript coverage and remaining work.
- `manuscript/Paper_VII_Fourth_Lean_Block_Supplement.pdf` and `.tex`: mathematical details and proof boundaries.
- `SHA256SUMS.txt`: hashes of the delivered files.

Papers I–VI were not rebuilt in this block. The original numerical suite was not rerun. Imported Mathlib proofs were not independently rechecked or rebuilt. No continuum or quantum-gravity conjecture is newly claimed.
