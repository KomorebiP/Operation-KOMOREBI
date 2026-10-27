# Komorebi Euler Lean v21

This source release adds actual lower-root charts and slope-matching localization
to the end-to-end dyadic Euler formalization. It has 727 theorem/lemma declarations
in 79 modules. The new block has 74 declarations in nine modules.

**Main result:** if the actual carry-defined lower residue polynomial has only
simple roots modulo two, every critical zero of the actual normalized Euler
residual lies in one of at most two explicitly defined skeleton balls, with exact
slope equality and one additional bit of lower-center alignment. Outside that
condition the appropriate local root-free or simple-root atlas is proved.

The bound is for a fixed residual. Universal Euler simplicity, candidate stability
across all multipliers and wall distances, and exact critical-scalar nonvanishing
are not claimed. See `PROOF_AND_STATUS.md` for all hypotheses and remaining tasks.

## Contents

- `Euler/`: all 79 mathematical source modules, including the 70 unchanged v20 modules.
- `Euler.lean`: root import.
- `Audit.lean`, `THEOREM_INDEX.json`: complete declaration and axiom-audit inputs.
- `evidence/`: successful baseline/final replay logs, development diagnostics and finite audit.
- `history/v20/`: unchanged incoming v20 ZIP.
- `scripts/`: replay, integrity and supplementary checking tools.
- `RELEASE_STATUS.json`, `PROVENANCE.json`: execution status and immutable dependency pins.

## Run

Use Lean 4.34.0-rc2 with mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The portable runtime is not included.
Python tools use the standard library and require Python 3.10+.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_slope_localization.py --output /path/to/NEW_slope_audit.json
```

The replay needs a configured dependency cache or the pinned portable kit. It
starts with no compiled project objects, treats warnings as errors, compiles all
modules, and inspects every indexed theorem's transitive axioms. Only
`Classical.choice`, `Quot.sound` and `propext` are allowed. Pinned mathlib compiled
dependencies are reused; neither Lean nor mathlib is bootstrapped from source.
The replay and finite-audit scripts refuse existing evidence output paths.

Integrity verification is not a mathematical proof checker. Finite synthetic tests
are corroboration, not substitutes for the compiled universal statements.
