# Komorebi Physics — persistent progress ledger

Checkpoint: **v0.50.0-g1 — strong generator checked**  
Recorded: **21 October 2026**  
Book: **Komorebi Physics: Continuum, Geometry and Refinement**, 570 pages  
Parent: **Komorebi_Physics_Lean_v0.49.0_Checked_Block_49.zip**  
Parent SHA-256: `413b107ea21130ce45ff6ae261263d3a326e63047dfe1d9a389543f0928891aa`

## Completed and accepted

- Recovered the exact offline Lean/Mathlib environment and verified the seven-part archive identity.
- Rebuilt the Block 49 operator target successfully. Reran its API and axiom checks.
- Proved and compiled the strong generator on the actual infinite coefficient and physical torus spaces. Both domain inclusions, physical first-order Fourier criterion, generator sign, invariant domain, commutation, strong Schrödinger equation, velocity continuity and conserved output norm are included.
- Accepted 37 named theorems and two definitions in `Relativistic3DGeneratorBridge.lean`. All 13 generator/compatibility gates passed, including four expected mutation rejections, the axiom audit, kernel replay, and exact-source separate-path compilation.
- Reran five computation suites. The energy-budget negative result was reproduced, not removed.
- Added original-material open licenses and the printed license notice. Preserved third-party exceptions and the baseline archive bytes.
- Updated the mathematical chapter's verification wording, the technical companion, central scope, and scope diagram. No original explicit proof environment or numerical plot data changed.
- Rebuilt five changed components, validated navigation, rendered all 570 pages, and inspected the changed pages.

The operative source is `formal/generator/KomorebiPhysics/Relativistic3DGeneratorBridge.lean`, SHA-256 `ee721cc3ab78f500bab87c1edb358be8b30a0892e7047c9e9cb5aa31a6d51499`. The old uncompiled scaffold is historical material under `audit/prior_formal/`, not the restart target.

## Exact verification status

| Component | Status |
|---|---|
| Physical self-adjoint Hamiltonian | Exact-target current replay passed, inherited source unchanged |
| Strong generator and complete domain | Current source, axiom audit and kernel replay passed |
| Abstract spectral-calculus expression | Written deduction, no formal API linkage yet |
| Centered resolvent and quadratic rate | Written proofs and finite checks, no new universal Lean certificates |
| Five stated computations | Current exit-0 records available |
| Entire historical physics aggregate | Not freshly certified by this pass |
| Whole-book independent specialist review | Not performed |
| Empirical or interacting-physics identification | Not established |

## Next restart point

Use the checked generator source, not the older draft. Run the supplied replay command against the exact external kit before changing theorem statements:

```text
python formal/generator/replay_generator.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work-dir /path/to/new-replay
```

The next formal development should define the bounded centered operator on the **same infinite coefficient space**, prove convergence on the continuum Hamiltonian domain, and then formalize the nonreal-resolvent estimate. Keep the abstract spectral-calculus API linkage as its own explicit obligation. The subsequent global quadratic-rate theorem must retain its third-order Fourier moment hypothesis.

Do not substitute a changing finite sampled lattice for this fixed-space multiplier family. Sampling, aliasing and interpolation need separate definitions and comparison theorems.

## Publication and audit work still separate

The design is frozen. Keep current status in the central scope and technical companion, not as a development diary in the mathematics. Any new numerical evidence must say which program and inputs were actually rerun. Preserve the backreaction obstruction and the prescribed-distribution hypothesis. Reconcile historical gauge receipts and arrange or perform the remaining whole-book scientific review without treating a successful PDF build as proof checking.

## Failure and trust record

See `RELEASE_VERIFICATION.md` and the retained development logs. Failed proof attempts and expected negative controls are separated from accepted passes. Only the exact source digest above and its documented dependency pins are covered. The compiler and all imported libraries were not rebuilt from source. No unrestricted completion or physical validation claim is authorized by this checkpoint.
