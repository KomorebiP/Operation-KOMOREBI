# Komorebi × IUT — Checked Continuation Bundle

**Version:** 0.3.0  
**Date:** 2026-09-17

This archive is the authoritative checked handoff for the Komorebi analysis of
the IUT III Corollary 3.12 transport and witness boundary.

## What changed in Block 03

- Introduced distinct Lean types for the multiradial output, fixed q-pilot,
  hull input, determinant-line object, prime-strip, trace, structure, and
  log-volume measurement.
- Encoded IPL, SHE, and APT as typed certificates rather than Boolean labels.
- Enumerated Ind1–Ind3 and six additional live obstruction channels.
- Added a two-stage determinant/procession normalization with an explicit
  `KGradeBridge`.
- Tracked determinant powers, multiplicities, structure-sheaf correction,
  averaging scale, and the downstream IUT IV `j²` weight.
- Isolated the exact open theorem as `StepXiEWitnessPreservation` and
  `SourceWitnessTheorem`.
- Proved a finite countermodel in which every pre-witness field holds but the
  q-pilot containment fails.
- Added a positive equality model that exercises the complete source-faithful
  route.
- Refined the Block 02 `Cor312Interface` without reintroducing circularity.
- Mapped every new field to exact IUT III or IUT IV source locations.

Read `BLOCK_03_FORMAL_REPORT.md` for the theorem-level account and
`verification/block03_final/verification.json` for the machine-readable audit.

## Critical boundary

This bundle does **not** prove, disprove, repair, or refute IUT III Corollary
3.12. It verifies a source-faithful typed interface and a logical independence
result. The actual IUT instantiation of `SourceWitnessTheorem` remains open.

The finite countermodel is not an IUT counterexample. It proves only that IPL,
SHE, APT, obstruction control, and normalization do not imply the required
measurement-level containment by logic alone.

## Begin here

1. Read `BLOCK_03_FORMAL_REPORT.md`.
2. Read `notes/IUT_312_FIELD_TO_SOURCE_MAP.md`.
3. Read `notes/IUT_312_OPEN_OBLIGATIONS.md`.
4. Inspect `formalization/lean/KTG/IUT312WitnessObligation.lean`.
5. Inspect `formalization/lean/KTG/IUT312SourceCountermodel.lean`.
6. Run the verification command in `formalization/lean/README.md`.
7. Continue from `CONTINUE_HERE.md`.
