# Centered spacing rates: checked mathematical map

Base: checked Block 49 plus the accepted `Relativistic3DGeneratorBridge` source.
New source: `KomorebiPhysics/Relativistic3DCenteredRates.lean`.
Accepted strict-compilation source SHA-256:
`30b1f44184da49cdd84851b84f0c08bd7bed362587de1268c2acb5adc4b65e27`.

The exact coefficient space remains `ℓ²(ℤ³, ℂ⁴)` with the inherited physical
torus Fourier isometry. The new moment is

`M3(f)^2 = Σ_n (k_n,0^6 + k_n,1^6 + k_n,2^6) ‖f_n‖²`.

`HasThirdOrderMoment f` means summability of this actual nonnegative series.
The separate proof `HasThirdOrderMoment.mem_continuumDiracDomain` constructs
the first-order-domain witness needed to apply the unbounded Hamiltonian.
It uses `x² ≤ 1 + x⁶` and the ambient coefficient norm; no domain assumption
or desired convergence is inserted as a field.

| Manuscript target | Formal representative | Exact boundary |
| --- | --- | --- |
| Uniform sine error | `sinQuot_cubic_bound` | All real spacing and momentum, with removable zero value; sharp coefficient 1/6 from Mathlib's proved global `Real.abs_sub_sin_le`. |
| Exact Clifford error and generator envelope | `centered_mode_quadratic_sq`, `centered_mode_quadratic_bound` | Uses the centered module's exact sum-of-three-squared-errors identity. |
| Global generator rate | `centered_generator_quadratic_bound` | All masses, nonzero real spacing, and fields with finite M3; bound `h² M3/6`. |
| Modal propagator rate | `centered_mode_propagator_quadratic_bound` | Actual exponentials, all signed real times, no commutation of different Hamiltonians. |
| Global propagator rate | `centered_propagator_quadratic_bound` | Actual infinite coefficient field, all real spacing and signed time; bound `|t| h² M3/6`. |
| Compact-time uniform rate | `centered_propagator_compactTime_bound` | Explicit nonnegative horizon T, every t in `[-T,T]`. |
| Physical coefficient correspondence | `physical_generator_quadratic_bound`, `physical_propagator_quadratic_bound`, `physical_propagator_compactTime_bound` | Uses the actual inherited torus Fourier equivalence and physical Hamiltonian domain. |

The propagator step uses the independently implemented module
`Relativistic3DModalPerturbation`. Its interpolation is
`F(s) = U_A(t-s) U_B(s) ψ`, with derivative
`i U_A(t-s) (A-B) U_B(s) ψ`. Unitarity bounds the derivative, and a real
mean-value estimate gives the same absolute-time factor for positive and
negative t. The proof does not move A across B's exponential.

The final full rate module contains 18 named theorem declarations, 4
definitions, and 3 type abbreviations. These are support and interface counts,
not 18 independent physical conclusions. Its strict development compilation
passed with an empty diagnostic log. Parent-owned fresh API, axiom, kernel and
control gates are separate from this development receipt.

## Retained failures

Three development commands failed before the accepted full compile. The first
support probe found a deprecated simp name, an unnecessary tactic after a
completed field calculation, and an absolute-power normalization issue. A
physical-generator probe exposed an insufficiently reduced partial-map
coercion; an explicit definitional conversion fixed it. The first full compile
found another deprecated simp name, replaced by a definitional conversion.
All source snapshots, diagnostics, commands and exit statuses are retained.

No sampled-lattice comparison, abstract unbounded functional-calculus
identification, interacting field theorem, or cosmological repair is claimed.
