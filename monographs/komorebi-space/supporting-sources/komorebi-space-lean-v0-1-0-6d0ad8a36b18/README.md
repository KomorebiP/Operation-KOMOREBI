# Komorebi Space Theory — Lean core v0.1.0

**Komorebi P.**

A consolidated, machine-checked resolution–transport core. This release contains **14 proof modules and 96 explicitly named theorems**, together with a mathematical consolidation, a full outline-status ledger, negative controls, and reproducible verification.

The original fifty-section proposal is not advertised as fully proved. Its valid core is formalized here. Unsupported general identifications and incorrect claims are corrected or retained as clearly marked research targets.

## Start here

- `docs/CONSOLIDATED_THEORY.md`: symbolic definitions and principal theorem statements, with exact Lean names.
- `docs/THEOREM_INDEX.md`: all 96 named theorems, with file/line references.
- `docs/OUTLINE_STATUS.md`: status of every original outline section.
- `docs/CORRECTIONS.md`: mathematical repairs and operational failures.
- `docs/VERIFICATION.md`: actual build and audit evidence, assumptions, and trust boundary.
- `audit/latest/VERIFICATION.json`: machine-readable release verification.

## Central result

For a complete normed candidate space E, continuous linear residual d and protected semantic map p, a semantics-preserving sequence satisfying

    ‖d(fₙ₊₁)‖ ≤ q ‖d(fₙ)‖,        0 ≤ q < 1
    dist(fₙ, fₙ₊₁) ≤ C ‖d(fₙ)‖,  C ≥ 0
    p(fₙ) = p(f₀)

has a limit f∞ satisfying

    d(f∞) = 0
    p(f∞) = p(f₀)
    dist(fₙ, f∞) ≤ C / (1-q) · ‖d(fₙ)‖.

The semantic obstruction is `[d(f)] ∈ R / d(ker p)`. Its vanishing is equivalent to existence of an exact candidate with the same protected semantics. `TowerCorrection.lean` instantiates this quotient with the **actual naturality differential of resolution towers**.

These are theorems with explicit hypotheses, not an assertion that a convergent correction procedure exists for every mathematical problem.

## Files and modules

| Module | Checked content |
|---|---|
| Towers | Levelwise candidate maps, exact-map category, naturality differential and composition law. |
| Squares | Typed horizontal/vertical defect pasting and flatness preservation. |
| Realization | Coherent inverse-limit point type, actual induced maps and universal property. |
| Cofinal | Monotone unbounded resampling equivalence for inverse-limit points. |
| Correction | Semantics-constrained quotient, flattening equivalence, invariance and dual certificates. |
| TowerCorrection | Concrete bridge from tower compatibility defects to the constrained obstruction quotient. |
| Cohomology | Explicit additive three-term complex, H², correction and the differential-sign repair. |
| Exactification | Summable, variable-rate and geometric convergence; residual-based tail bounds. |
| WeightedGeometry | Independent transport cost, directed triangle inequality, zero-distance relation and collapse diagnostic. |
| NormedDefects | Amplification bounds, transported finite Stokes identity and compression-shell algebra. |
| ObstructionFloor | Distance to boundaries, closedness distinction and persistent obstruction. |
| Profiles | Restricted cofinal vanishing theorem and counterexample to unrestricted invariance. |
| ProjectiveExample | A nontrivial finite additive 2-cocycle and proof it is not a scalar coboundary. |
| LinearExactification | Exactification preserving continuous linear semantics and annihilating the constrained obstruction. |

## Verified offline replay

Python 3 and the previously available portable runtime are required. This archive does **not** contain the multi-gigabyte compiler or mathlib cache.

```bash
python3 scripts/verify.py \
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The runtime directory must contain:

```text
toolchain/bin/lean
workspace/.lake/packages/mathlib
workspace/.lake/packages/*/.lake/build/lib/lean
```

The script creates a clean `.lake/replay/lib/lean` directory, compiles every project module with warnings treated as errors, audits all named theorem axioms, runs three negative controls, and writes `audit/latest/VERIFICATION.json`.

It does not download dependencies or alter the runtime. The existing compiler and dependency cache are reused, but every project `.olean` is rebuilt from source in the clean replay directory.

To preserve the bundled release evidence while performing another replay:

```bash
python3 scripts/verify.py \
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --audit-dir audit/my_replay
```

For Windows, the supplied offline runtime is a Linux runtime and should be run under WSL or another Linux environment.

## Standard Lake project

The project also supplies `lean-toolchain`, `lakefile.toml`, and a pinned `lake-manifest.json`. With the required Lean installation and network access, the standard dependency/bootstrap route is:

```bash
lake exe cache get
lake build
lake env lean -DwarningAsError=true checks/AxiomAudit.lean
```

The recorded verification in this release uses the clean **offline direct-compiler replay** above, not a fresh online bootstrap or a full rebuild of mathlib. Network/bootstrap success on another machine is not claimed as an already tested result.

## Pins

```text
Lean:    leanprover/lean4:v4.34.0-rc2
Commit:  6a10ac8c22beadecabdbb0919c2b50214762f91d
mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
```

## Audit boundary

The positive library and root import contain no `sorry`, `admit`, custom `axiom`, `unsafe`, `native_decide`, or `implemented_by` declarations. Each named theorem's reported axiom dependencies are checked against:

```text
propext
Classical.choice
Quot.sound
```

The deliberately invalid files in `tests/negative/` are **not library modules**. They test rejection of a false statement, rejection of a proof placeholder, and detection of an injected custom axiom. A search over the entire archive will therefore find those deliberately prohibited constructs in the negative fixtures and in explanatory documentation.

The axiom audit is not an independent implementation of Lean's kernel. The trusted compiler, pinned cached dependencies, and standard axioms remain in the trust boundary. The theorem count refers to explicit source theorems, not generated projections, imported library theorems, or a claim of 96 novel mathematical discoveries.

## Scope not proved here

Full pro-category equivalence, universal stacks of representations, higher obstruction towers, automatic Bianchi identities, general spectral sequences, arbitrary cofinal residual invariance, p-adic classification, compact-operator convergence, Galois/holonomy identification, and unrestricted descent remain outside this release.
