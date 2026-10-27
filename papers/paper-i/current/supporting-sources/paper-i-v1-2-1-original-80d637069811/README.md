# Projector-Resolved Seed Calculus I

Version 1.2.1 is the audit-hardening, provenance, and figure-correction revision of **Typed Seeds, Operator Grammars, and Exact Reconstruction** by **Komorebi P.** Earlier release archives remain unchanged; this is a new immutable release.

The paper develops a typed operator-module language for generated hulls, cardinal-valued seed rank, exact packet coordinates, transfer blocks, relations, completion, and realization. It distinguishes classical inputs from paper proofs, sampled computations, and the precise certificate-explicit statements checked in Lean.

## Main files

- `paper/Projector_Resolved_Seed_Calculus_I.pdf` — final 40-page v1.2.1 paper.
- `paper/Projector_Resolved_Seed_Calculus_I.tex` — complete LaTeX source with local bibliography.
- `code/python/` — symbolic and numerical companion package v1.1.1, tests, and wheel.
- `formalization/lean/` — Lean 4/Mathlib theorem-completion component v1.0.1.
- `results/` — machine-readable results, run record, and build logs.
- `provenance/` — source/claim map, verification report, render audit, and the preserved v1.0 audit ledger.

## Reproduce

The runners copy the release to a temporary directory, verify that copy, and
remove it afterward. The canonical extracted release is not modified. Unless
the caller supplies another value, they export the fixed release epoch
`SOURCE_DATE_EPOCH=1788393600` for reproducible artifact metadata.

On Windows PowerShell:

```powershell
.\Run_All.ps1
```

On a Unix-like system:

```bash
./Run_All.sh
```

Exact versions, seeds, tolerances, and scope boundaries are in `REPRODUCIBILITY.md` and `results/run_record.json`.

## Verification boundary

The Python suite passes 18/18 tests. Within the completion contract, all 32 revised named statements and three algorithm specifications are matched by 84 unique imported Lean declarations classified `Exact` or `Stronger`. The executable map checker enforces all 35 rows and direct axiom reports for all 84 declarations. The standalone namespace audit fails closed on project axioms, explicit opaque constants, unsafe declarations, `sorryAx`, or any axiom outside `propext`, `Classical.choice`, and `Quot.sound`. Classical classification and existence inputs, executable extraction, performance claims, bibliography, and historical priority remain outside the completion denominator. No claim of external peer certification is made.

## Rights

No copyright license has been selected for this release. See `LICENSE_STATUS.md`; absence of a license is not permission to reuse the work.
