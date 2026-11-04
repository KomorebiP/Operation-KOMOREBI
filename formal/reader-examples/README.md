# Lean companions for the reading examples

Author: Komorebi P.

This project formalizes selected claims from the factorial-lane, residue-projector, and Stirling/Bell/Fubini reading examples. The [site guide](../../docs/LEAN_READER_COMPANIONS.md) explains the correspondence and limits. [CLAIM_MAP.json](CLAIM_MAP.json) gives the exact theorem names and assumptions.

## Sources and scope

| Module | Scope |
|---|---|
| `KomorebiReader/FactorialLanes.lean` | Universal finite factorial reconstruction, rational Pochhammer scaling, reciprocal-binomial normalization, and the binomial diagonal bridge. |
| `KomorebiReader/ResiduePackets.lean` | Coefficient residue projectors, exact divisible refinement, and additive coordinate transport with complete block reconstruction. |
| `KomorebiReader/StirlingRecovery.lean` | Recovery from a complete factorial-weighted polynomial and the explicit obstruction to recovery from two scalar summaries. |

The general transport results require a supplied additive equivalence on the actual carriers. They do not identify infinite sequences with polynomials or construct the concrete falling-factorial basis map. The project does not claim a full Lean formalization of these reading examples or their source monographs.

## Verification

Lean and Mathlib pins are retained in `lean-toolchain`, `lakefile.toml`, and `lake-manifest.json`. The exact production declaration list and controls are in `verification.json`.

From the repository root, with the portable runtime available:

```text
python -B tools/verify_lean_companion.py --project formal/reader-examples --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --output /tmp/reader-examples-replay
```

The runner makes a fresh temporary build, checks dependency revisions, treats warnings as errors, audits the production declarations, replays project modules with the same Lean kernel, and executes positive and deliberate rejection controls. It refuses to overwrite an existing nonempty evidence directory. On a standard Lean installation with the pinned dependencies prepared in this project's `.lake/packages`, omit `--runtime`.

The [recorded pass](verification/2026-11-04/run.json) identifies checked source and log hashes. Its mathematical claims remain bounded by the exact formal statements. Kernel replay covers the project modules against the pinned imported environments. It does not rebuild all Mathlib or use an independent verifier.

The `Controls/*Reject*.lean` and `Controls/RejectUnfinishedProof.lean` files are deliberately invalid. They must not be imported by the production library.

## Attribution

The underlying factorial, binomial, Stirling, and projector identities are classical. This companion records their formal correspondence to the reading site's constructions. Imported Mathlib results retain their upstream authorship and license. This source follows the repository's [code license](../../LICENSE-CODE.txt).
