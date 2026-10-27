# Energy-budget research ledger

Version: 0.1.0
Date: 21 October 2026
Scope: finite-depth quantum backreaction and conditional parameter analysis
Predecessor: Komorebi Physics Open Edition, Covariant Refinement-Fiber Dynamics, chapters 2 and 4–6

## Completed

1. Read the existing energy, interaction-strength, Hartree, and ultraviolet analysis. Inspected the
   production-threshold figure and source equations. Recovered the frozen input and verification code.
2. Reexecuted the inherited audit: 19 checks passed, 0 failed. Reproduced eta0 =
   3.806206917830343e-21 and the reciprocal energy overdraw 2.627287537404906e20.
3. Independently evaluated the discrete energy integral using adaptive momentum integration.
   Agreement with the inherited quadrature: relative error 1.6584511541850588e-12.
4. Derived a conditional abundance-preserving family lambda = eta0 * epsilon^2,
   A/mu = (A0/mu0)/sqrt(epsilon), at fixed vacuum density, gamma, and Lambda/A.
   Proved the corresponding reservoir and physical-mass scaling laws.
5. Derived the finite real kinetic-mode system with the coherent reaction force. Proved energy
   conservation, nonnegative occupations, a finite energy bound, and global existence at a fixed
   finite regulator. These are ordinary mathematical proofs, with symbolic identities checked
   by SymPy. No new Lean work was performed.
6. Implemented an independent complex-oscillator representation. It agrees with the real system
   on the tested finite case. This is an implementation cross-check, not independent physical evidence.
7. Completed 17 configurations: principal solution, tower-depth variation, momentum quadrature,
   momentum-cutoff variation, incoming-state location, nominal-efficiency variation, tolerance
   variation, and two deliberate conservation-breaking controls.
8. Identified the invariant fourth-mass-moment curvature proxy and a leading adiabatic kinetic
   response diagnostic. Kept finite counterterms and logarithms outside the proxy's claim.
9. Wrote a standalone research manuscript, rendered its 12 pages, inspected the layout, and verified
   no off-page text or invalid internal links. Did not overwrite the main monograph.
10. Independently audited all 17 saved energy arrays against their JSON reports.

## Verification status

| Component | Status | Boundary |
|---|---|---|
| Original overdraw | Reproduced | Confirms a failed approximation, not a viable event |
| Gaussian abundance family | Algebraically proved and numerically checked | Stipulated Gaussian spectrum only |
| Finite conservation and positivity | Written proof and symbolic checks | Declared finite Hamiltonian and state |
| Principal energy residual | 7.33950678011297e-11 | Sampled floating-point residual, not certified error bound |
| Principal mode invariant residual | 3.7259084706420253e-13 | Same finite run |
| Independent oscillator comparison | Passed | Same finite model in different variables |
| Two negative controls | Correctly rejected | Omitting reaction or coherence breaks closed-system conservation |
| Fixed-cutoff momentum quadrature | Locally stable in tested resolutions | Does not imply cutoff independence |
| Depth-independence gate | FAILED | Maximum mode fraction ranges from 0.0794 to 0.9999998 |
| Momentum-cutoff robustness | Not established; substantial variation | Vacuum response and state must be treated consistently |
| Incoming-state robustness | Not established | Current state is instantaneous vacuum at finite initial q |
| Full renormalized FLRW production | NOT established | Gravity, state, subtraction, stress, and locking remain |
| Original cosmological benchmark | NOT repaired | Main book's negative result remains valid |
| New Lean certification | None | Existing formal sources unchanged |

The study reports 11 passing gates and 1 failed scientific gate. The independent saved-array audit
passes; the strict physical-acceptance command intentionally returns exit code 3.

## Failed approaches and execution issues

- The original after-the-fact occupation projection remains invalid as a dynamical energy source.
- A smaller quartic alone does not resolve the problem while preserving the intended density:
  the abundance-preserving family leaves a large unused reservoir and an invariant curvature proxy.
- Increasing tower depth does not stabilize this instantaneous-vacuum finite model. Higher modes
  change the response even after the real-production Gaussian tail is effectively saturated.
- Omitting the full reaction force produced a relative energy defect of 1.47269. Omitting only
  the coherence force produced a defect of 5.29845. These are deliberately incorrect closed models.
- Long numerical invocations exceeded the execution window. Completed configurations were saved
  and reused only with matching settings; remaining runs were resumed. No interrupted run was
  counted as a completed result. The final arrays contain all 17 configurations.
- The first TeX build failed because amsthm and newpxmath both defined openbox in the chosen package
  order. Reordering the packages repaired it. Cover paragraph spacing was also corrected before
  the final render. The accepted build has no undefined-reference or overfull-box warnings.

## Important numerical interpretation

The principal run is epsilon = 0.01, depth 16, 48 nodes per level, momentum parameter z in [0,3.5],
q initially -10, speed 1, and dimensionless time 0 to 20. It uses the modified parameter family,
not the original lambda = 1 parameters. Its maximum instantaneous mode-energy fraction is
0.6486339048 and endpoint fraction 0.1267474363. Neither is a late-time relic abundance.

At fixed original vacuum density the abundance-preserving family reduces physical tower masses
by eta0^(1/4) relative to the old projected benchmark. The normalized Gaussian shape and target
density can agree while occupations, masses, and number density differ. Old observables have not
been refitted and cannot simply be claimed unchanged.

## Next restart point

Do not fit the previous cosmology to these instantaneous mode fractions. First specify whether the
tower has a physical endpoint or is a regulator for a larger theory. Depth 15 is a useful test case
because it retains 99.9992126 percent of the Gaussian energy; that fact does not derive a physical cutoff.

Construct one consistent finite-depth renormalized effective action with explicit finite matching
conditions. Derive the background force, field normalization, energy, and pressure from the same
prescription. Use a suitable adiabatic incoming state and test its preparation time. Revisit the large
curvature and kinetic-response diagnostics rather than subtracting them independently by hand.

Then include the scale factor and solve the coupled background/mode/gravity system. In expanding
spacetime the check is the appropriate continuity equation, including pressure work, not constancy
of a flat-space density. Follow the field far enough to determine trapping or release, the destination
of remaining scalar energy, and a controlled late-time spectrum. Only then refit downstream transport.

Acceptance requires numerical resolution convergence, explicit regulator/state control, consistent
stress exchange, a closed reservoir accounting, and the intended abundance and locking behavior.
An independent mathematical and physical review remains appropriate.

The numerical reference A sets the incoming speed; the actual speed at q = 0 is solved, not imposed. Thus the nominal Gaussian depletion parameter is not a measured dynamical efficiency.
