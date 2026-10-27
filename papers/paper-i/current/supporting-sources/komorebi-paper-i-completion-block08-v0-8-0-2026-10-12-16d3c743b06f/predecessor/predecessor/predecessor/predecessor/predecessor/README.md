# Paper I completion: Block 03, v0.3.0

This package continues the final Lean completion of Projector-Resolved Seed Calculus I. Read `REPORT.md` and `VERIFICATION.json` for the actual accepted execution result. This is not a claim that all 108 records in the expanded monograph are fully formalized.

## Mathematical additions

The three new mathematical modules construct an actual positive primary presentation for every finite-dimensional operator over an arbitrary field, prove the exact seed count by residue-field lower bounds and Chinese-remainder generators, connect it to the canonical seed rank, and prove a presentation-independent primary maximum. They also prove cyclicity is equivalent to distinct primary labels and establish the displayed conditional invariant-factor count.

Higher-degree irreducibles are included. The constructions are noncomputable mathematics, not executable factorization or normal-form procedures.

The exact intrinsic-primary quotient `X_p/p(T)X_p` identification remains open in this formalization. This is why the general printed single-operator theorem remains partially mapped even though its primary-block count formula is proved.

## Package layout

- `predecessor/`: complete, unchanged Block 02 source and evidence, including its frozen original baseline.
- `source/extension/`: the three new mathematical Lean modules and import root.
- `tests/`: complete ownership gate, exact module replay wrapper, 18 new mathematical assertions, and deliberate misuse controls.
- `scripts/`: reproducible clean audit launcher, deterministic coverage update, and development records helper.
- `coverage/`: all 108 unchanged publication statements, their updated declaration map and the precise delta.
- `evidence/`: fresh compilation, declaration/type/axiom checks, serial replays, controls, runtime authentication and unsuccessful development attempts.
- `PROOF_GUIDE.md`, `docs/SEMANTIC_REVIEW.md`, `CONTINUE_HERE.md`: mathematical explanation, exact limits and restart obligations.

Source-level public declarations and compiler-owned inventory counts have different meanings. The latter includes private proofs, generated helpers, structure fields and recursors. Neither is a count of independent discoveries.

**Production-source scope:** do not recursively compile every `.lean` file in the archive. `evidence/` retains rejected drafts, and the negative-control directories deliberately contain invalid claims or injected axioms. The supported launcher compiles the 28 listed production modules and tests each fixture against its intended outcome.

## Reproduce the accepted workflow

Run on Linux or WSL with Python 3 and the matching portable runtime:

```bash
bash scripts/run_block03.sh /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 /absolute/path/to/new-output
```

The output directory must not already exist. The script reconstructs the entire 28-module project closure from source. It does not import the predecessor's saved project objects. Only pinned external Mathlib and Lean dependencies are reused.

`scripts/dev_check.py` is a session-bound historical development helper. The supported portable reproducer is `run_block03.sh`, which supplies its environment from the runtime.

The large runtime is not included in this compact handoff. Runtime hashes, dependency pins and restoration evidence are included. Do not run `lake update`. No network access is required once the matching runtime is present.

The archive's `MANIFEST_SHA256.json` and `scripts/verify_bundle.py` verify payload integrity without Lean. The manifest excludes itself. The ZIP checksum is published outside the ZIP to avoid a self-reference.

The publication PDFs are not rebuilt in this block. License-status records are inherited unchanged. No new publication license has been selected.
