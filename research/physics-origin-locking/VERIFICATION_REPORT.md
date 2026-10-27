# Verification report: Origin Locking and Cosmological Energy Exchange

Date: 21 October 2026. Research ledger: 0.3.0.

**19 passing gates, 2 failed gates. 29 finite configurations: 25 full-model runs and 4 intentional negative controls.**

## Correction and principal scope

The inherited density-locked branch is q=0. q=4 is an empty-sector tree vacuum, not the original locking point.

The new finite expanding action conserves pressure-work accounting and preserves the Friedmann constraint on regular solutions. This is not a completed covariant quantum renormalization. Origin local locking survives the stated matching, while the computed empty-sector minima leave nearly all the vacuum energy. Conditional snapshot transport is not a late-time prediction. No new Lean run was made.

## Failed acceptance gates

- **Expanding momentum cutoff:** at fixed 128-node quadrature the first-crossing mode fractions change from 0.4198449952094019 to 2.1854778815841622 when the cutoff doubles from 16 to 32. The relative shift is 4.205439880244692, far beyond the 0.001 criterion. These are deliberately accelerated-expansion tests, not the physical cosmological expansion rate.
- **Absolute hyperboloid preservation:** the tighter altered-model long run has maximum residual 0.0006847381591796875, above 0.00001. Its large occupations cause cancellation in this diagnostic. Tightening integration tolerances did not repair it. This is retained as a failure, not replaced with a scaled-norm pass. Accepted primary origin runs satisfy the absolute criterion.

## Gate details

### matching_symbolic — PASS

Scope: symbolic algebra, not Lean.

```json
{
  "barrier_curvature": "0",
  "origin_curvature": "0",
  "J_integral": "0",
  "K_derivative": "0"
}
```

### matching_independent_integrals — PASS

Scope: computational.

```json
4.547473508864641e-13
```

### quartic_polynomial_invariance — PASS

Scope: computational.

```json
8.673104090238902e-15
```

### trace_moment_identity — PASS

Scope: conditional collisionless moments.

```json
3.169510215561083e-16
```

### flrw_symbolic_exchange — PASS

Scope: finite action identities, not covariant renormalization.

```json
{
  "mode_exchange": "0",
  "hyperboloid": "0",
  "background_exchange": "0",
  "metric_pressure": "0",
  "friedmann_constraint": "0"
}
```

### independent_complex_variables — PASS

Scope: computational.

```json
{
  "config": {
    "depth": 14,
    "epsilon": 0.01,
    "branch": "origin",
    "barrier_fraction": 0.3,
    "zmax": 8,
    "nodes": 8,
    "duration": 6,
    "expansion": "stress",
    "initial_hubble": 0.02,
    "initial_state": "flat_wkb2",
    "tail": true,
    "control": "full",
    "rtol": 1e-13,
    "atol": 1e-16,
    "samples": 401
  },
  "max_q_difference": 1.34012540647932e-11,
  "max_velocity_difference": 8.257700079283836e-12,
  "max_mode_energy_difference_over_E0": 3.3089038292765606e-09,
  "max_work_balance_residual": 1.1355345552743756e-09,
  "max_wronskian_residual": 4.443889700667114e-12
}
```

### saved_state_audit — PASS

Scope: computational.

```json
{
  "configurations": 29,
  "maximum_scaled_discrepancy": 4.440892098500626e-16
}
```

### correct_finite_energy_work — PASS

Scope: sampled finite-model residual.

```json
6.218425774306979e-11
```

### friedmann_constraint — PASS

Scope: constraint evolved, not reset algebraically.

```json
6.218425774306979e-11
```

### positive_occupations — PASS

Scope: computational.

```json
0.0
```

### mode_hyperboloid — FAIL

Scope: computational.

```json
0.0006847381591796875
```

### control_no_coherence_force_rejected — PASS

Scope: intentional wrong-model control.

```json
0.0029239638819407165
```

### control_no_pressure_coherence_rejected — PASS

Scope: intentional wrong-model control.

```json
0.01341479460697137
```

### control_no_tail_pressure_rejected — PASS

Scope: intentional wrong-model control.

```json
3.42648927285083e-05
```

### control_no_volume_squeeze_rejected — PASS

Scope: intentional wrong-model control.

```json
0.011380533057276043
```

### short_physical_scale_comparison — PASS

Scope: short microscopic interval only; no late-time inference.

```json
{
  "max_q_difference": 3.566591466608315e-15,
  "H_over_A": 3.3545617129394536e-25,
  "final_log_a": 4.025474055527354e-24
}
```

### flat_limit_reference — PASS

Scope: new code replay against inherited first-crossing reference.

```json
1.0975262939094423e-16
```

### fixed_cutoff_quadrature — PASS

Scope: stress-test interval 0<=tau<=4, 64 to 128 nodes.

```json
5.831446436843635e-13
```

### expanding_momentum_cutoff_acceptance — FAIL

Scope: FAILED scientific gate: state and curvature subtractions not completed.

```json
{
  "first_crossing_relative_shift": 4.205439880244692,
  "z16_mode_fraction": 0.4198449952094019,
  "z32_mode_fraction": 2.1854778815841622
}
```

### modified_model_matching_window — PASS

Scope: counterfactual model classification, not a selected cosmology.

```json
[
  {
    "depth": 10,
    "gaussian_fraction": 0.006026854441197023,
    "threshold_over_budget": 0.006695213658872942
  },
  {
    "depth": 11,
    "gaussian_fraction": 0.03922473989380388,
    "threshold_over_budget": 0.032918879897931304
  },
  {
    "depth": 12,
    "gaussian_fraction": 0.20072375034977855,
    "threshold_over_budget": 0.20585259083159002
  },
  {
    "depth": 13,
    "gaussian_fraction": 0.6368231823980182,
    "threshold_over_budget": 2.0762814014574116
  },
  {
    "depth": 14,
    "gaussian_fraction": 0.9787470490413113,
    "threshold_over_budget": 43.22993585482754
  },
  {
    "depth": 15,
    "gaussian_fraction": 0.9999921260149733,
    "threshold_over_budget": 1353.9681698661404
  }
]
```

### fresh_replay — PASS

Scope: computational.

```json
[
  {
    "name": "origin_stress64",
    "final_q_difference": 0.0,
    "work_residual_difference": 0.0
  },
  {
    "name": "origin_static_refined",
    "final_q_difference": 0.0,
    "work_residual_difference": 0.0
  },
  {
    "name": "candidate_static",
    "final_q_difference": 0.0,
    "work_residual_difference": 0.0
  },
  {
    "name": "control_no_tail_pressure",
    "final_q_difference": 0.0,
    "work_residual_difference": 0.0
  }
]
```

## Unestablished physical obligations

- covariant fourth-order renormalized stress tensor
- physical incoming state
- late-time capture and out-state
- intended abundance
- physical ultraviolet endpoint
- old post-release vacuum-energy relaxation

## Execution and preservation

Four separate solver replays match saved final background coordinates exactly at stored precision in this environment. The saved-state audit uses the delivered 21 exact full-mode snapshots per configuration. Complete saved diagnostic time series and final modes are also retained. The mode solution at every internal adaptive step is not distributed. Negative controls and failed acceptance gates are retained.

All original figures are computed from saved arrays or explicit stated analytic formulas. Publication preflight is a separate document check and cannot upgrade a scientific failure. `results/publication_preflight.json` records the final page count, full-page render check, warning scan, text bounds, and link validation.

## Environment

```json
{
  "python": "3.13.5",
  "numpy": "2.3.5",
  "scipy": "1.17.0",
  "sympy": "1.14.0",
  "mpmath": "1.3.0"
}
```

Frozen input SHA-256: `7a08c0964796a8cd607b2a59ed8b2bfb6cfb8e4df31b7b03627c8201bc2c796e`.
