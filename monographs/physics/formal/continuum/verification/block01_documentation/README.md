# Komorebi Physics — Lean Formalization
## Full-edition program, first checked block · v0.1.0

**Result: PASS.** The first block has **37 newly written theorem declarations** and **39 byte-preserved, freshly rechecked Paper VII theorem declarations**, for **76 active theorems in seven modules**. The audit covers **96 named declarations**, including definitions with proof obligations. All four deliberately invalid controls were rejected.

This begins formalization of the **550-page Projector-Refinement Physics: Complete Unified Theory**, not the narrower Physics Guide v1.0. The complete source manuscript is included under `reference/`. The current proof map targets Chapter 2, physical PDF pages 17–19, printed pages 4–6.

“New” means new Lean declarations in this release. It is not a claim that the underlying mathematical results are newly discovered, nor a percentage of the full physics edition completed.

## What is now checked

For a finite complete orthogonal projector family on a complex inner-product space, the new modules prove state reconstruction, orthogonality, the inner-product decomposition, and the squared-norm identity. The ambient space need not be finite-dimensional. Projectors and generators are bounded maps defined on the whole space.

For a differentiable trajectory satisfying the stated flow equation, packet energy has an actual `HasDerivAt` proof. The current is defined by the inner product, not by the desired balance law. Under the separately stated skew-adjointness hypothesis, currents are antisymmetric, diagonal currents vanish, internal currents cancel, and total energy is constant for a trajectory satisfying the equation at every real time.

A coarser atlas is constructed from an address map. Its projector multiplication and completeness are proved using the preserved upstream algebra. Coarse packet energies and currents are then proved equal to sums of fine energies and currents. An arbitrary subset's energy derivative equals only its incoming boundary flux.

The exact example module constructs coordinate atlases in all finite dimensions and a two-sector skew generator with currents −2 and +2. It also proves that the identity generator is not skew and has a nonzero self-current. These demonstrate nonzero realizations and the necessity of the skew hypothesis without floating-point calculations.

The preserved `MovingFrames.lean` additionally rechecks the finite-matrix differentiated-unitarity and moving-frame coordinate theorems. These are historical source reuse, not new proofs credited to this block.

## Verification

| Item | Result |
|---|---:|
| New theorem declarations | 37 |
| Preserved and rechecked theorem declarations | 39 |
| Active theorem declarations | 76 |
| Active mathematical modules | 7 |
| Named declarations with axiom audits | 96 |
| Invalid controls correctly rejected | 4 / 4 |
| Fresh final verification run | PASS |

Compiler: **Lean 4.34.0-rc2**, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.

Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine locked dependency revisions and tracked source trees were checked. The verifier deletes the local build directory and recompiles the seven proof modules plus the aggregate import, one worker at a time, with warnings treated as errors.

Every audited axiom dependency is in `{propext, Classical.choice, Quot.sound}`. There are no custom axioms, admitted active proofs, or native-evaluation proof escapes in the active source. The audit includes the proof-bearing atlas constructions, not only the theorem declarations.

The existing pinned Mathlib/Lean caches were used. Their entire imported proof library was **not** independently rebuilt or rechecked from scratch. Formal checking certifies the elaborated statements under their explicit hypotheses; the source-to-statement map is a separate editorial/mathematical audit.

## Run it again

The recovered runtime is Linux x86-64. Use Linux or WSL with the restored portable kit:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Or:

```bash
bash run_checks.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The default output is `verification/local_run/`, preserving the delivered `verification/final/` evidence. Every command is bounded by 120 seconds by default. Timeouts, missing files and compiler errors fail the run. Progress is saved after every check, and a complete pass is printed only after the axiom and negative-control audits finish.

The multi-gigabyte runtime and Mathlib cache are not duplicated in this package. `runtime_restore_support/` contains the recovered original assembler and its checksum manifest for the seven `Lean_Offline_01.zip` through `Lean_Offline_07.zip` parts. These parts were successfully restored in this session.

## Files

- `KomorebiPhysics/`: four new active modules.
- `QuantumPacketCore.lean`, `TensorRefinement.lean`, `MovingFrames.lean`: unchanged upstream modules, freshly checked.
- `Audit.lean`, `declaration_inventory.json`: complete named-declaration inventory and axiom commands.
- `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json`: equations, hypotheses, source mapping, and exact coverage limits.
- `docs/FULL_EDITION_ROADMAP.md`: remaining work, without a fabricated completion percentage.
- `verification/final/`: fresh compiler output, dependency checks, axiom output, negative controls and machine-readable report.
- `verification/development/`: failed proof attempts, restoration diagnostics and the interrupted first audit.
- `reference/`: the 550-page master, source provenance and byte-preservation record.
- `CONTINUE_HERE.md`: continuation instructions and proof boundaries.

## Not established by this release

This does not formalize all 550 pages, prove a quantum-gravity theory, or validate any cosmological prediction. The continuum, countable-atlas, unbounded-generator, nonlinear constraint, strong-field and dark-sector sectors remain outside this block. The bounded flow equation and skew-adjointness are explicit hypotheses; existence of arbitrary prescribed flows is not proved here. The fine atlas laws are input structure, not consequences claimed without hypotheses.

Chapter 2.6's whole-object deformation rule is not yet implemented in the new library. The moving-frame material rechecked here is the preserved finite-matrix theorem, not a new general bounded-operator moving-atlas theorem.

The master distinguishes proved mathematics, numerical checks, conditional results, corrections and open physical targets. Its supersession of the historical additive dark-sector branches must be preserved in later formalization.

## Development failures

Initial attempts encountered an archive-decoder mismatch, deprecated or missing API names, finite-sum ordering and case-splitting errors, and an upstream definition hidden by the module boundary. One failed refinement attempt also produced a compiler panic after unresolved metavariables. These were repaired without adding assumptions or proof escapes. The first cumulative audit was interrupted by the outer command deadline and was not counted as a complete pass. A fresh run subsequently completed all checks. See `verification/development/FAILURES.md` and the retained logs.
