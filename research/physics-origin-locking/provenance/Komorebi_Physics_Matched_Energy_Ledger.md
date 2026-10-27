# Matched energy research ledger

Version: **0.2.0**  
Date: **21 October 2026**  
Predecessor: Energy-Conserving Production and Energy Study Ledger 0.1.0  
Status: Completed finite-model research block; cosmological recovery remains open.

## Completed work

1. Read the predecessor paper, its verification record, and its restart ledger. Preserved the frozen benchmark input. This pass does not claim a new replay of all 19 historical benchmark checks.
2. Derived the static Gaussian determinant remainder after matching vacuum energy, mass, and quartic at `q=0`: `F(s)=(1+s)^2 log(1+s)-s-3s^2/2`. Proved its positive integral representation and upper/lower bounds.
3. Independently checked the convergent subtracted momentum integral at five points. Maximum relative discrepancy: 6.250555628639631e-14.
4. Derived the matching-induced field-excursion constraint. At depth 15 and epsilon 0.01, the ground-state turning point is about 0.789942. `q=10` costs 451795.564228 times the specified total budget; the old tree-vacuum point `q=4` costs 5916.76712766 times that budget. These restrictions are conditional on the specified matching data.
5. Constructed a common finite action with the matched potential, coherent oscillator force, and optional positive kinetic tail. Proved exact finite energy conservation, occupation positivity, and global existence.
6. Integrated the omitted high-momentum second-adiabatic-order kinetic response. Included its energy and derivative force consistently, without double-counting explicit modes. No uniform higher-order error theorem is asserted.
7. Constructed a self-consistent second-order adiabatic rest-point state, proved the unique acceleration root at a fixed restoring displacement, and solved the total-energy condition numerically on the outer branch.
8. Completed 40 finite configurations, including three intentionally incorrect-force controls and the final like-for-like 24-node raw/tail comparison. Audited every stored array.
9. Replayed four accepted short configurations in a separate output directory. Their crossing observables reproduced exactly at the reported precision in this environment. Duplicate replay arrays are not redistributed.
10. Refined long-time quadrature through 192 nodes per segment. Followed 39 crossings through tau=100. The field is not locked.
11. Derived the exact symmetric tanh-pulse occupation and its Gaussian limit. Compared 15 oscillator integrations with the exact formula, including external work.
12. Wrote an 18-page research supplement, generated six Python figures, and preserved full source and evidence records. No new Lean work was performed and the main monograph remains unchanged.

## Accepted numerical results

| Quantity | Result | Boundary |
|---|---:|---|
| Accepted short energy residual | 1.51390011638e-12 | Sampled floating-point error |
| Accepted short initial mode energy | 4.93199318671 | Already inside the initial budget, not new production |
| First-crossing mode fraction | 0.0285398077804 | Instantaneous basis, not an out-state |
| Cutoff-doubling shift improvement | 257.409586554 | Like-for-like 24-node comparison, z=32 to 64 |
| Matched relative first-crossing shift | 4.06090784403e-06 | Empirical resolution comparison |
| Long accepted energy residual | 1.8936252566e-10 | Finite interval through tau=100 |
| Long quadrature fraction change | 0.000150207210351 | 96 to 192 nodes, maximum across 39 crossings |
| Long momentum-cutoff fraction change | 2.57918593538e-07 | z=32 to 64 at fixed 96-node quadrature |
| Last crossing time | 98.237832988 | Within the stored finite trajectory |
| Last crossing mode fraction | 0.699921772793 | Not a dark-matter abundance |
| Last crossing background speed | 0.547793964284 | Nonzero: no permanent locking established |

All **19 scoped computational gates pass**. The physical acceptance conditions below remain unestablished and are not converted into computational passes.

## Mathematical and physical scope

- Matching is at the origin and fixes three static local coefficients. A changed physical matching prescription, extra effective operators, or a protected completion can change the global potential. A compensated renormalization scheme change must not be confused with changing physical matching data.
- The receiving fields are Gaussian and the background is classical. No complete interacting quantum or gravitational theory is claimed.
- Physical tower depth 15 is a useful finite test, not a derived ultraviolet endpoint.
- The second-order adiabatic state is a specified finite state, not a unique physically derived cosmological vacuum.
- The high-momentum tail is a two-derivative effective term. Its finite action conserves energy exactly, but the tail approximation itself is not an exact ultraviolet completion.
- The finite energy sum includes coherent polarization. It is not automatically an asymptotic particle number or relic density.
- No new Lean certification, renormalized covariant FLRW stress tensor, original benchmark recovery, or observed locking is claimed.

## Failed attempts and rejected models

See `notes/EXECUTION_ISSUES.md` for the rejected root bracket, initial export permissions, malformed first TeX fraction, and chart tick-label repair. Early failures are retained separately from final successful logs. Long-time coarse quadratures were refined rather than relabeled as converged. The three wrong-force controls are intentionally rejected by their energy defects.

## Exact next restart point

1. Decide the physical matching data and tower content before fitting anything. In particular, origin matching at the tested budget cannot retain the old `q=4` locking target. A branch matched at the intended physical vacuum would be a different specified problem and must keep its counterterm/parameter relations explicit.
2. Starting from that declared model, derive one covariant effective action or consistent subtraction scheme for the background force, energy density, pressure, and gravitational equations. Do not append Hubble friction to the current flat-space mode energy while ignoring pressure work.
3. Derive or prepare an incoming state from a physical history and test preparation dependence. A fourth-order stress prescription and mode-state regularity may require more than the current finite rest-point construction.
4. Evolve background, modes, and scale factor together. Test the total continuity equation, time and momentum resolution, and physical ultraviolet assumptions. Follow the residual energy reservoir until locking or continued motion is established.
5. Extract an operationally justified outgoing spectrum or late-time particle definition. Only then refit cosmological transport. Do not reuse the old Gaussian occupation projection.

Immediate reusable source: `code/matched_study.py`, `tail_inertia`, `turning_state`, and the exact pulse regression. Accepted short reference: `accepted_tail32`. Refined long reference: `long_tail32_quad192`. Use `code/replay.py` rather than overwriting these reference files.

## Input identity

Frozen input SHA-256: `7a08c0964796a8cd607b2a59ed8b2bfb6cfb8e4df31b7b03627c8201bc2c796e`.

The package manifest identifies all delivered files. It certifies byte identity, not mathematical truth or empirical validity.
