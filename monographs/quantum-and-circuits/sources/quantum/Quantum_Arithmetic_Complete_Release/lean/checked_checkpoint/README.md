# Komorebi quantum arithmetic bridge

Version 0.2.0. Checked publication companion, September 21, 2026.

## Scope

This project formalizes the finite case q = 12 from *Mathematics Between Minds*.
The central theorem is `Komorebi.QuantumArithmetic.publication_bridge` in
`Publication.lean`. The accompanying `fourier_entry_formula` identifies the
checked matrix with the usual positive sign complex exponential Fourier matrix.

The proof includes exact rational filtering and energy, exact phase arithmetic,
Fourier unitarity, projector transport, normalization, recovered probabilities,
orthogonality of two states with the same initial histogram, and their opposite
probability of a coprime outcome after a basis change. It also proves that no
function of that histogram alone can reconstruct both states.

The 96 named theorems include supporting lemmas. This count is not a count of
new discoveries. The classical Ramanujan and Fourier ingredients are identified
in the essay.

## Actual checks

A fresh source build passed with warnings treated as errors. All 96 theorems
were inspected through elaborated declarations and printed axiom dependencies.
The supplied Lean kernel replay utility checked all five modules separately.
Three negative controls were rejected: a false Fourier coefficient, a false
signal sign, and an admitted proof with warnings treated as errors.

The active modules contain no `sorry`, custom `axiom`, `native_decide`, or
`unsafe` declaration. Finite certificates use `decide +kernel`. The axiom union
is `propext`, `Classical.choice`, and `Quot.sound`. This is not an axiom free
formalization. Imported Mathlib results are used in the complex interpretation.

## Reproduce with the portable kit

Use the pinned Lean 4.34.0-rc2 installation and the cached packages recorded in
`lake-manifest.json`. Mathlib is pinned at
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```sh
python scripts/verify_lean.py \
  --toolchain /path/to/Komorebi_Portable_Lean_4.34.0-rc2/toolchain \
  --packages /path/to/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages \
  --out verification/reproduction
```

Choose a new output directory for each run. The script refuses to overwrite a
previous fresh build. It checks dependency revisions, copies fresh source files,
builds, audits all named theorems, replays them, and runs the negative controls.
It kills the process group on timeout. A timeout is a failure to verify, never
an acceptance. The script does not fetch or install dependencies.

The toolchain and Mathlib cache are not redistributed in this small package.
Their recorded provenance and hashes are included. New proof terms were rebuilt,
but the compiler and imported dependency cache were not rebuilt from source.
`leanchecker` uses the Lean kernel. It is not an independently implemented
proof verifier.

## Evidence and boundaries

`verification/final/REPORT.json` records commands, return codes, durations,
source hashes, dependency revisions, theorem count, and axiom union. Companion
logs contain compiler and kernel replay output. `THEOREM_INDEX.md` maps the
statements to their source locations. `development/` retains failed attempts
and the original draft for transparency. Those files are not active modules.

The general modulus formula and the Galois orbit argument are proved in the
essay, not newly formalized here. The six divisor projectors are tested by the
separate exact Python verifier, not supplied as a general Lean family here.
No hardware implementation, circuit synthesis, efficient state preparation,
quantum speedup, or new physical law is asserted.
