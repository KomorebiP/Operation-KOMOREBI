# Komorebi Space Theory — Lean core v0.8.0

**Komorebi P.**

56 proof modules, 656 named theorem declarations, 271 indexed non-theorem declarations. Six new modules add 97 theorems and 23 constructions. All 50 v0.7 proof modules are unchanged. Counts include auxiliary declarations, not discoveries.

## Infinite reconstruction, with the convergence mode specified

For the actual dyadic tower residual hierarchy,

```text
x = sum_(j<N) L_j h_j(x) + Q_N x
Q_N x = L_N x_N
S_N x = x - Q_N x.
```

The new results distinguish:

```text
all details determine every bounded residual;
each fixed coordinate is reconstructed exactly once k+1 < 2^N;
uniform-norm reconstruction holds iff Q_N x tends to zero.
```

For general split cascades, define the persistent submodule and finite core:

```text
P_infinity = {x : all Q_N x = x}
F = union_N ker Q_N
D = {x : Q_N x tends to zero}.
```

Lean proves equality of all detail records iff the input difference is persistent. With uniformly bounded Q_N, `D = closure F`. The actual dyadic hierarchy has `P_infinity = 0`, proved from its parity lift, without a convergence assumption.

Norm criteria include absolute summability of transported details for the actual complete dyadic residual space, and `product_(j<N) ||J_j|| * ||x_N|| -> 0`. For contractive target sections the actual hierarchy has contractive restoration lifts. A separate bounded-sequence cascade has recovery domain exactly the sequences tending to zero. The constant-one sequence gives a checked nonconvergence witness; geometric sequences have exact error q^N. A scalar half/double cascade proves that raw coarse decay does not suffice without controlling restoration.

## Reading and reproduction

- `docs/INFINITE_RECONSTRUCTION_EXTENSION.md`: new theorems, proof sketches, hypotheses, boundaries.
- `docs/CONSOLIDATED_THEORY.md`: cumulative mathematical development with versioned sections.
- `docs/THEOREM_INDEX.md`: every named theorem and its source line.
- `docs/OUTLINE_STATUS.md`: the original research outline versus proved scope.
- `docs/VERIFICATION.md`: commands, evidence, negative controls, and trust boundary.

The multi-gigabyte compiler/runtime cache is not included. Use the pinned offline runtime:

```bash
python3 scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --audit-dir audit/my_replay --timeout 120
python3 scripts/audit_constructions.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --audit-dir audit/my_constructions
python3 checks/computation/infinite_reconstruction_exact.py \
  --output audit/my_infinite_reconstruction_exact.json
python3 scripts/check_hashes.py
python3 scripts/validate_manifest.py audit/computation-manifest.json --root .
```

Use new output paths rather than overwriting archived evidence. Lean is pinned to 4.34.0-rc2, mathlib to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The supplementary computations use only the Python standard library and exact rational arithmetic.

## Evidence and limits

Current primary evidence: `audit/current_v080/VERIFICATION.json`, `audit/constructions_v080/CONSTRUCTION_AUDIT.json`, `audit/infinite_reconstruction_exact.json`, and `audit/BASELINE_PRESERVATION.json`. The fresh replay has a separate report. Historical logs retain their versioned paths and should not be substituted for current verification.

The positive library contains no admitted proof or custom axiom. The theorem and construction audits permit only `propext`, `Classical.choice`, and `Quot.sound`. Negative fixtures intentionally contain invalid material and are excluded from the library. The compiler and cached dependencies remain trusted and were not independently rebuilt.

The finite rational audit has 8,778 assertions across 36 variable-dimension cascades, 48 dyadic configurations, and 230 sequence/scalar cases, plus three mutation controls that are all rejected. This is supplementary evidence, not extrapolation to infinite theorems.

The release does not claim norm recovery for all bounded dyadic residuals, arbitrary infinite detail synthesis, an orthogonal decomposition or basis, compression, a runtime bound, arbitrary-block invariance, full pro-category equivalence, higher obstruction theory, stacks/descent, unrestricted arithmetic correspondence, or mathematical novelty relative to prior literature.
