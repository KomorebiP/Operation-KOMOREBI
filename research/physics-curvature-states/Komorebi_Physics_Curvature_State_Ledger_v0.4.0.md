# Komorebi Physics: curvature and initial-state ledger

Version: **0.4.0**
Date: **21 October 2026**
Predecessor: Origin Locking and Cosmological Energy Exchange, 0.3.0.
Status: common fourth-order spectral subtraction and a controlled ultraviolet diagnostic. Original cosmological recovery is not established.

## Completed

1. Recovered and read the predecessor's exact finite action, origin correction, failed cutoff gate, and restart instructions. Inspected its actual code and recorded configurations.
2. Derived one set of mode density, pressure, and scalar-force subtraction terms through adiabatic order four, retaining the full positive mass in the leading frequency and all expansion terms.
3. Proved modewise exchange and separate exact cancellation at orders zero, two and four. SymPy verifies all three identities without assuming constant H or a special background.
4. Proved a sufficient ultraviolet-tail criterion for smooth prescribed backgrounds with compatible fourth-order data at fixed finite species depth. This is a written proof, not a Lean result or an infinite-depth theorem.
5. Proved that the inherited flat rest-point state has a negative quadratic initial stress divergence under the common fourth-order subtraction. Confirmed its leading coefficient numerically through K512.
6. Implemented stable factored stress remainders, fourth-order mode preparation, Bogoliubov variables and a normalized squeeze-ratio evolution.
7. Ran and audited 16 finite configurations, including two intentional accounting controls, the incompatible state, a second-order state, quadrature and tolerance refinements, and alternate variables.
8. Passed a new ultraviolet cutoff comparison, K128 to K256, on a fixed analytic background. All three full-interval normalized comparisons meet 1e-3. This is NOT a rerun or pass of the inherited coupled gate.
9. Checked an independently coded canonical oscillator representation and high-precision local derivative formulas. Replayed one selected configuration in a fresh process with zero stored-observable discrepancy.
10. Proved that a finite R q^2 term leaves all static flat potential data unchanged but changes curved-background force and stress consistently. The finite physical matching problem is therefore explicit.
11. Prepared a scientific supplement, reproducible figures, a verification report, and this ledger. The main monograph and previous archives remain unchanged.

## Verification status

- Thirteen scoped gates pass. Sixteen configuration records are audited.
- The preliminary loose-tolerance K128 run failed the tighter pressure-resolution test and is retained.
- The incompatible flat rest-point state fails ultraviolet stress removal. Its diagnostic rejection is not an accepted cosmological state.
- Fourth-order subtraction preserves the exchange identity but does not preserve the old nonnegative instantaneous-energy interpretation.
- The state construction is fourth order in the ultraviolet. No unique physical vacuum or Hadamard-state claim is made.
- No new Lean compilation, independent external review, capture theorem, late spectrum, relic-abundance fit, or vacuum-release repair.

## Remaining obligations

1. Select a common locally covariant finite matching prescription, including background curvature coupling, gravitational counterterms and finite derivative terms. Static origin-potential matching does not uniquely determine these.
2. Complete the physical incoming state through the low-momentum sector without using the ultraviolet approximation as a nonadiabatic low-mode state rule. The numerical sector k<8 is deliberately outside this study.
3. Implement the matched stress and force in the original coupled origin-branch equations. Fourth-order terms introduce higher derivatives and require control of the physical semiclassical branch.
4. Rerun the original `origin_stress128` versus `origin_stress128_cut32` comparison while holding the completed physical matching data and state fixed. That original failure is still open.
5. Establish capture, coherence control, an out-state, and the destination of residual scalar energy before using moment transport as a prediction.
6. Address the separate static vacuum-fate issue. The original matched depth-15 empty sector still releases only about 1.14e-12 of its reference vacuum energy.
7. The earlier altered-model high-occupation invariant failure remains unaddressed. The present squeeze chart has only been tested in the well-conditioned ultraviolet sector.

## Exact restart point

Read manuscript sections 3, 4 and 7, then `code/curvature_modes.py`. The accepted numerical references are `ad4_K128_panel16`, `ad4_K256_panel16`, and the independent panel check `ad4_K128_dyadic_tight`. The symbolic common-exchange source is `code/symbolic_ward.py`.

Do not feed the ultraviolet-sector density into cosmological transport as a total abundance. Do not add the old omitted-momentum kinetic tail on top of a subtraction/add-back construction without explicitly checking double counting. Any restoration of finite local terms must carry its force and stress together.

## Failures and provenance

Numerical and execution failures are recorded in `notes/EXECUTION_ISSUES.md`, including the default-tolerance pressure failure and a repaired replay-report serialization error. The predecessor archive is preserved unchanged with its checksum. No physical failed gate has been silently converted into a pass.

## Publication checks

The final 12-page PDF was rendered in full. Internal links and page boundaries passed the automated checks. The final LaTeX log contains no undefined references, missing-glyph reports, font warnings or overfull boxes. Five explicit proof environments and three scientific figures are present. Rendered pages were inspected, including the mathematical formulas and final references. These are publication checks, not theorem certification.
