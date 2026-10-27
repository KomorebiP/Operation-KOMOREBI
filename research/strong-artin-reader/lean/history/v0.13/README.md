# Strong Artin Lean v0.13.0 — Relative Projector Detection / Finite Probe Basis — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.12.0_Transverse_Obstruction_Checked.zip`  
**Status:** ten additive Lean modules replayed successfully with warnings as errors.

## What this checkpoint closes

This checkpoint connects the abstract transverse-obstruction layer of v0.12 to the actual trace-projector mechanism used in the Komorebi automorphy-lifting program.

The main progression is:

1. a separating probe family can be centered against one probe that detects the retained defect line;
2. the centered probes have joint kernel exactly that line;
3. for trace probes `X |-> tr(P X)`, functional centering is exactly trace pairing with centered projector combinations;
4. conjugation-covariant projectors give covariant trace probes for the actual conjugation representation on `End(W)`;
5. on a finite-dimensional representation of a finite group, detection of every simple invariant packet implies joint separation, without assuming modular semisimplicity;
6. it is enough to detect every simple packet **outside** the scalar/cyclic defect line, provided one reference projector has nonzero trace;
7. the quotient-prime first-order obstruction then has dimension exactly one and vanishes exactly when the retained cyclic residual vanishes;
8. a finite linearly independent basis of actual centered quotient-projector probes can be extracted, of cardinality exactly the transverse deformation dimension.

## Main capstone

The final theorem is

`Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone.full_obstruction_eq_zero_iff_cyclic_residual_zero_of_relative_detection`.

It assumes:

- a finite group `G` acting through a finite-dimensional representation `rho`;
- a projector family `P` covariant under conjugation;
- one reference projector `P i0` with nonzero trace;
- every simple conjugation packet not contained in the scalar line `k • 1` is detected by at least one trace probe `X |-> tr(P i X)`.

It proves that the complete first-order block obstruction vanishes if and only if the scalar cyclic residual is zero.

The numerical companion theorem proves that the obstruction cokernel has `k`-dimension exactly one.

## Finite Taylor--Wiles target

`exists_finite_transverse_projector_probe_basis_of_relative_detection` proves the existence of a finite family of actual centered quotient-projector probes which:

- is drawn from the original projector family after centering and quotienting by the scalar line;
- is linearly independent;
- spans the entire transverse dual;
- has cardinality exactly
  `finrank k (End_k(W) / (k • 1))`.

Thus the future global selection problem is finite and dimension-controlled.

## Important boundary

This checkpoint does **not** prove that every Strong Artin quotient-prime residual image satisfies the relative spectral detection hypothesis.

It also does **not** prove the Chebotarev/Taylor--Wiles theorem needed to realize a selected finite transverse basis by auxiliary primes while retaining the desired local and automorphic conditions.

The terms "relative adequacy" and "relative spectral detection" in this release name the exact local representation-theoretic condition formalized here. They are not a claim that a published automorphy-lifting theorem applies automatically in the singular quotient-prime setting.

## Verification

Pinned environment:

- Lean `4.34.0-rc2`
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- `-DwarningAsError=true`
- no `sorry`
- no `admit`
- no custom `axiom` declarations
- audited theorem dependencies confined to ordinary Lean/Mathlib foundations such as `propext`, `Classical.choice`, and `Quot.sound`.

A single ten-module outer replay hit the execution wall after four successful modules. It is not counted as a passing aggregate run. The ten modules were replayed in smaller batches and every module has an observed compiler return code `0` in `verification/replay_logs/`.

## Replay

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-checks 3 --resume
```

Repeat the same command until it reports completion. Omitting `--max-checks` compiles all remaining modules in one invocation.
