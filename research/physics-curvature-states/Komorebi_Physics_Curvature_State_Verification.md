# Verification: curvature, states, and conserved subtraction

Date: 21 October 2026. Ledger: 0.4.0.

**13 scoped gates pass. Sixteen stored finite configurations were audited. One preliminary numerical-resolution failure remains recorded. The inherited coupled cosmological cutoff gate is not rerun.**

## Scope

The mode mass spectrum and degeneracies use depth 15. The background is the declared analytic path a=exp(0.02 t), q=-Q cos(nu t), on 0<=t<=2. Only k>=8 is included. These results do not establish a physical abundance, a renormalized coupled cosmology, or a repair of the original production benchmark. No new Lean certification.

## Principal observed comparisons

At t=2, fourth-order-subtracted ultraviolet density changes from 0.009750561294807994 at K128 to 0.009750305024059451 at K256. Pressure changes from 0.7129027467801475 to 0.712914830830536. Scalar force changes from -0.05564489937177049 to -0.055644905248939724.

The normalized full-interval maximum differences for density, pressure and force are respectively 6.27206073e-6, 9.13697860e-5 and 2.29217329e-7. All meet the stated 1e-3 ultraviolet diagnostic criterion.

Independent equal-tolerance momentum panelings at K128 give normalized differences 9.08624670e-9, 4.22638869e-7 and 1.86084348e-9.

## Gates

### symbolic_exchange_identities — PASS

Four exact symbolic cancellations; not Lean

```json
{
  "passed": true,
  "value": {
    "ward_order_0": "0",
    "ward_order_2": "0",
    "ward_order_4": "0",
    "finite_curvature_matching_ward": "0",
    "all_zero": true
  }
}
```

### high_precision_local_coefficients — PASS

Three points, r,s,W4,log derivative and oscillator residual

```json
{
  "passed": true,
  "value": 1.041404331773421e-15,
  "limit": 1e-11
}
```

### independent_canonical_modes — PASS

Three canonical complex modes versus squeeze variables

```json
{
  "passed": true,
  "value": 1.2114592735342483e-11,
  "limit": 1e-09
}
```

### integrated_alternate_variables — PASS

Same finite probe in Bogoliubov and squeeze variables

```json
{
  "passed": true,
  "value": [
    1.772222789181356e-08,
    6.426505530153307e-07,
    1.2391223474228187e-07
  ],
  "limit": 1e-05
}
```

### accepted_common_work_balance — PASS

Absolute exchange residual; prescribed background only

```json
{
  "passed": true,
  "value": 2.7204280494963484e-13,
  "limit": 1e-09
}
```

### fixed_cutoff_quadrature — PASS

Equal ODE tolerances, different independent momentum paneling

```json
{
  "passed": true,
  "value": [
    9.086246700854263e-09,
    4.2263886926144583e-07,
    1.8608434818937923e-09
  ],
  "limit": 1e-06
}
```

### uv_cutoff_doubling — PASS

k>=8, K128 to K256, normalized time sup norms; not inherited coupled gate

```json
{
  "passed": true,
  "value": [
    6.272060730811553e-06,
    9.136978596165848e-05,
    2.2921732930541187e-07
  ],
  "limit": 0.001
}
```

### accepted_normalization — PASS

Squeeze chart algebraic normalization

```json
{
  "passed": true,
  "value": 4.440892098500626e-16,
  "limit": 1e-12
}
```

### flat_state_asymptotic_prediction — PASS

Checks predicted failure, does NOT accept flat state

```json
{
  "passed": true,
  "value": 0.00015128356452454028,
  "limit": 0.002
}
```

### pressure_control_rejected — PASS

Intentionally inconsistent exchange accounting

```json
{
  "passed": true,
  "value": 0.6327241462472771,
  "minimum_expected_defect": 0.01
}
```

### force_control_rejected — PASS

Intentionally inconsistent exchange accounting

```json
{
  "passed": true,
  "value": 0.3917649602020282,
  "minimum_expected_defect": 0.01
}
```

### fresh_replay — PASS

Fresh same-code execution in a new process

```json
{
  "passed": true,
  "value": {
    "name": "ad4_K16",
    "scaled_discrepancies": {
      "final_rho": 0.0,
      "final_pressure": 0.0,
      "final_force": 0.0,
      "initial_rho": 0.0
    },
    "passed": true,
    "scope": "Same-code fresh execution, not an independent physical result"
  }
}
```

### saved_array_audit — PASS

Recalculation from stored final states, not independent physics

```json
{
  "passed": true,
  "configurations": 16
}
```

## Failed preliminary numerical setting

The initial K128 computation with atol=2e-15 and rtol=2e-11 fails the tighter pressure-resolution requirement. The maximum normalized pressure difference from the accepted refined run is 0.005614784860043429. This is a numerical failure, not an alternative physical prediction. Tighter tolerances and a separate momentum-panel check support the accepted values.

## Initial-state obstruction

Keeping the inherited flat rest-point rule while applying the new bulk subtraction gives initial ultraviolet densities approximately -16.406 at K16, -336.234 at K64, -1356.705 at K128, and -21755.873 at K512. The observed ratio to the predicted negative H^2 K^2 coefficient is 1.00015128 at K512. This confirms that this state prescription is not suitable for the continuum stress test. It is not passed as a physical state.

## Open obligations

- Inherited coupled origin-branch cutoff gate
- Covariant finite physical matching
- Low momentum production and incoming state
- Self-consistent mean-field and gravity evolution
- Capture and late spectrum
- Original energy benchmark recovery
- Empty-sector vacuum-energy release
- New Lean certification

## Execution failure and repair

A first fresh-replay report failed JSON serialization on a NumPy boolean. The writer now converts it to a Python bool. The replay was executed again and produced zero discrepancy in the four reported observables. The failed serialization was not counted as a successful report.

## Evidence limits

Ordinary mathematical proofs and symbolic checks are not Lean certificates. Numerical convergence comparisons are not interval-certified errors. The momentum-window calculation is a diagnostic, not by itself a locally covariant finite matching prescription. The subtracted density can be negative and is not an instantaneous particle-energy bound.

## Publication checks

The final 12-page PDF was rendered in full. Internal links and page boundaries passed the automated checks. The final LaTeX log contains no undefined references, missing-glyph reports, font warnings or overfull boxes. Five explicit proof environments and three scientific figures are present. Rendered pages were inspected, including the mathematical formulas and final references. These are publication checks, not theorem certification.
