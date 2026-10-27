# Komorebi Large Signal Model — Lean 0.9.0

Komorebi P. · Block 9 · 12 October 2026

This cumulative formalization maps **35 of the 87 propositions** in frozen Foundations 1.0.0. None is marked partial. **52 remain unformalized.** The new block completes P14–P17 and P25: causal delay closure, data-span identification, fixed-space perturbation, finite-prefix indistinguishability, and conditional observable learning.

Read `LEAN_GUIDE.md` for the proof construction, `COVERAGE.md` for statement-level mappings, `AUDIT.md` for scope and checks, and `PROGRESS.md` for the restart point. Actual build outcomes belong to `verification/block9_release_run/report.json` and the separately delivered fresh-extraction verification report.

## Reproduce

Use a fresh extraction and the separately supplied Linux x86-64 runtime with Lean 4.34.0-rc2 and the pinned Mathlib revision. Run integrity checks before creating reports or compiled files.

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

On hosts exhibiting the kit's documented executable-discovery error, enable its supplied `compat/app_path.so` adapter through `LD_PRELOAD`, as its `run.sh` does. This changes executable-path discovery, not Lean's proof checking. The current run used that adapter. No new Windows execution is claimed.

There are 74 proof modules, 1,256 explicitly named declarations and 968 named theorems, of which 300 are in example modules. These are source counts, not novelty measures. Axiom dependencies are restricted to `propext`, `Classical.choice`, and `Quot.sound`. Project module replay uses Lean's own kernel implementation. The imported Mathlib environment is pinned, not exhaustively rebuilt or replayed here.

The real pseudoinverse is a noncomputable mathematical construction with proved properties. This is not a verified floating-point implementation. Production PR-LASM 2.3.0 and the frozen manuscript sources are unchanged. `PUBLICATION_STATUS.md` explains the dated wording in those historical sources.
