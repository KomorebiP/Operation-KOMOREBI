# Komorebi Physics — Lean Formalization
## Full edition, checked Blocks 01–02 · v0.2.0

**PASS: 127 theorem declarations, 160 audited named declarations, 10 mathematical modules, 9/9 negative controls.** Block 02 adds **51** theorem declarations. All seven earlier mathematical source modules remain byte-identical. Of the cumulative total, 88 declarations were authored in this full-edition program and 39 are preserved Paper VII declarations, all freshly rechecked.

The source is the included **550-page Projector-Refinement Physics: Complete Unified Theory**. This is not a formalization of the shorter Physics Guide. The present source map covers the core Chapter 2 identities in a finite-atlas, bounded-operator setting and explicitly separates input laws, definitions, proven consequences, and remaining scope.

## Main additions

`KomorebiPhysics/Deformation.lean` proves the actual inverse and moving-projector derivatives and the full three-term corner rule. Its strongest inverse interface derives local inverse differentiability from the derivative of U, completeness, and invertibility at the base point. Reconstruction cancels all moving-frame terms. Finite regrouping is compatible with transport.

`KomorebiPhysics/MovingAtlas.lean` extends the finite-matrix moving-frame foundation to bounded operators on arbitrary-dimensional complex Hilbert spaces. It constructs a genuine transported orthogonal atlas under two-sided unitarity and proves actual transformed state and packet-energy derivatives with the connection term retained.

`KomorebiPhysics/DeformationExamples.lean` supplies eleven exact theorems. These include the invertible shear, its nonstationary idempotent, the three nonzero rates 4N, -3N, 2N, the full rate 3N, and failures of term deletion, reversed commutator sign, and nonunitary self-adjointness.

Read `STATUS.md` for counts and limitations, `docs/BLOCK_02_PROOF_GUIDE.md` for the mathematical argument, and `docs/SOURCE_MAP.md` for the literal equation-to-declaration map.

## Verify locally

Use Linux x86-64 or WSL with the exact restored portable kit:

```bash
bash run_checks.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Equivalently:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

The compiler is Lean 4.34.0-rc2 and Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The verifier checks all nine pinned dependencies, deletes local compiled outputs, recompiles every mathematical module with one Lean worker and warnings as errors, audits the complete declaration inventory in module batches, and requires all nine deliberately invalid files to fail for the intended diagnostic. Each command has a 240-second default limit; timeouts and missing imports are failures, never proofs.

`verification/final/report.json` is the fresh cumulative machine-readable result. `verification/block01_final/` preserves the earlier evidence. Failed development attempts and the interrupted baseline audit are preserved separately. All named declarations, including proof-bearing definitions, have axiom dependencies restricted to `propext`, `Classical.choice`, and `Quot.sound`. There are no admissions, custom axioms, or native-evaluation proof escapes in active sources. The imported Lean/Mathlib cache was not rebuilt wholesale.

The multi-gigabyte runtime is not duplicated in the ZIP. The original seven-part assembler and exact chunk checksums are in `runtime_restore_support/`; all seven parts were restored successfully in this session. Source-only delivery is intentional, not a claim that the runtime is bundled.

## Limits and next steps

These are mathematical proofs under explicit hypotheses, not experimental confirmation. Unbounded Hamiltonians, strong-only operator differentiability, countable projector sums, continuum limits, nonlinear gravity, cosmology, and empirical predictions remain outside this block. Generic similarity preserves exact idempotent resolutions but is not treated as unitary. No full-edition completion percentage is claimed.

The next mathematical block is Chapter 4: state-dependent skew flow and associative refinement, followed by mixed-state trace dynamics with explicit finite-dimensional or trace-class hypotheses. Chapter 3's independent physical-unit, variational, and asymptotic targets remain separate.

See `CONTINUE_HERE.md` before continuing. Preserve all existing proof boundaries and source files.
