# Verification report — Vacuum Matching and Dynamical Energy Transfer

Date: 21 October 2026. Study ledger: 0.2.0.

## Summary

**19 computational gates passed, 0 failed.** These gates concern the explicitly specified finite mathematical model and its numerical implementation. They do not certify a physical cosmological completion.

The independent saved-array audit covers **40 finite configurations**, including three negative controls. The analytic pulse suite covers **15 prescribed-pulse cases**. Four accepted short configurations were reexecuted separately; their crossing-fraction differences from the references were zero at stored precision in this environment.

## Principal findings

- The matched static potential retains a positive nonpolynomial remainder after fixing vacuum energy, mass, and quartic at the origin.
- At H=15 and epsilon=0.01, the old q=10 preparation and q=4 tree-vacuum target are outside the specified total budget under this matching.
- A positive two-derivative term for omitted momentum modes improves first-crossing cutoff stability by a factor 257.409587 in the tested like-for-like comparison.
- The matched z=32-to-64 relative first-crossing shift is 4.06090784403e-06.
- The refined long run reaches 39 crossings, with mode fraction 0.699921772793 and background speed 0.547793964284 at its last crossing. No permanent locking or relic abundance follows.

## Gates and observations

### symbolic_core — PASS

Scope: Written finite identities, independently simplified by SymPy; not Lean.

Observed: `{"F_third_derivative": "2/(s + 1)", "F_first_three_values": ["0", "0", "0"], "matching_remainder_identity": "0", "force_identity": "0", "energy_derivative": "0", "invariant_derivative": "0", "stable_sqrt_remainder": "0"}`

### variable_kinetic_energy_identity — PASS

Scope: Exact action-level conservation at any finite quadrature.

Observed: `"0"`

### independent_static_integral — PASS

Scope: Five finite parameter points; empirical integration error.

Observed: `6.250555628639631e-14`

### adiabatic_tail_integral — PASS

Scope: Independent numerical integral of the second-order coefficient.

Observed: `6.661338147750939e-16`

### adiabatic_tail_derivative — PASS

Scope: Numerical derivative of the same action coefficient.

Observed: `1.8274270985330077e-12`

### independent_complex_oscillator — PASS

Scope: Alternative variables for the same specified model.

Observed: `{"config": {"depth": 14, "epsilon": 0.01, "zmax": 8, "nodes": 8, "duration": 4, "rtol": 2e-11, "atol": 2e-14, "max_step": 0.02, "force": "full", "initial": "turning_wkb2", "samples": 401}, "max_q_difference": 2.2926105458509483e-13, "max_p_difference": 5.624667398507199e-13, "max_mode_fraction_difference": 1.908503919145488e-11, "independent_energy_error": 1.911293345813192e-11, "initial_acceleration": 1.7380947042025126}`

### all_saved_arrays — PASS

Scope: Checks saved data, not a fresh rerun of every configuration.

Observed: `{"count": 40, "max_difference": 0.0}`

### finite_energy_residuals — PASS

Scope: All correct-force finite runs, including preliminary configurations.

Observed: `1.221562850872715e-09`

### finite_mode_invariants — PASS

Scope: Floating-point sampled hyperboloid identities.

Observed: `4.209778126096353e-08`

### negative_half_force — PASS

Scope: Intentional conservation-breaking modification correctly detected.

Observed: `0.4886724185806841`

### negative_no_coherence — PASS

Scope: Intentional conservation-breaking modification correctly detected.

Observed: `0.36017620646581516`

### negative_tail_connection — PASS

Scope: Intentional conservation-breaking modification correctly detected.

Observed: `0.02375076374895202`

### pulse_exact_vs_ode — PASS

Scope: Prescribed tanh pulse; not closed-system production.

Observed: `{"cases": 15, "max_absolute_n_error": 1.6407070146939873e-11}`

### pulse_work_balance — PASS

Scope: Energy supplied by the prescribed external source is included.

Observed: `1.010407035817451e-13`

### short_cutoff_improvement — PASS

Scope: Observed improvement for 32-to-64 momentum cutoff; no universal error bound.

Observed: `{"unmatched_change": 0.006518530557370283, "tail_matched_change": 2.5323573393798426e-05, "factor": 257.40958655410884}`

### short_cutoff_resolution — PASS

Scope: Relative change of first q=0 energy for two cutoffs with 24 nodes per segment.

Observed: `4.060907844034849e-06`

### long_quadrature_resolution — PASS

Scope: Finite interval through tau=100, absolute fraction change, not certified error.

Observed: `{"common_crossings": 39, "max_mode_fraction_change": 0.0001502072103510832, "last_change": 0.00012545358452231703}`

### long_cutoff_resolution — PASS

Scope: Same 96-node quadrature with tail at zmax 32 and 64.

Observed: `2.5791859353807567e-07`

### accepted_principal_budget — PASS

Scope: Saved accepted short run.

Observed: `1.5139001163788635e-12`

## Explicit non-certifications

Written proofs and SymPy identities are not Lean certificates. Floating-point residuals are not interval-certified integration errors. The finite tail is not a completed covariant renormalization. The matched potential is conditional on stated physical matching data. Physical depth and initial state remain choices. There is no full FLRW stress tensor, derived late-time abundance, or recovery of the original energy-overdraw benchmark.

## Publication checks

The final PDF is built from the supplied LaTeX source and six plots generated from actual saved data. Its final page count, render count, text bounds, internal navigation checks, and build-warning audit are recorded in `results/publication_preflight.json`. Source and result hashes are listed separately. A successful PDF build is not a scientific verification gate.

## Repaired failures

The rejected initial bracket, first export permission error, malformed TeX command, and overlapping chart ticks are documented in `notes/EXECUTION_ISSUES.md`. Incorrect-force controls remain deliberately incorrect. Early coarse long-time quadratures remain archived as exploratory rather than accepted converged evidence.
