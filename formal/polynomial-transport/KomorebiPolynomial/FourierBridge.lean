import KomorebiPolynomial.FallingPackets
import KomorebiPolynomial.RootsOfUnity

/-!
# The rational falling-coordinate and complex Fourier formulas agree

The comparison takes place in `ℂ[X]` after extending rational coefficients.
There is no inverse coefficient map from all complex polynomials to rational
polynomials. The inverse map used below is only the constructed rational
falling-factorial equivalence, on its declared carrier `ℚ[X]`.
-/

set_option autoImplicit false

open scoped Polynomial

namespace Komorebi.Polynomial.FourierBridge

open Komorebi.Polynomial.FallingFactorial
open Komorebi.Polynomial.FallingPackets
open Komorebi.Polynomial.RootsOfUnity

/-- Encode the actual falling-factorial packet in ordinary coordinates and
extend coefficients to `ℂ`. The result is exactly the finite cyclotomic
average of the encoded input. -/
theorem fallingPacket_fourier_bridge {ζ : ℂ} {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (hζ : IsPrimitiveRoot ζ N) (p : ℚ[X]) :
    average N r ζ ((fallingEquiv.symm p).map (algebraMap ℚ ℂ)) =
      (fallingEquiv.symm (fallingPacket N r p)).map (algebraMap ℚ ℂ) := by
  rw [average_rat_map_eq_packet hN hr hζ, fallingPacket_coordinates]

/-- The standard exponential root realizes the same bridge for every
positive modulus and every canonical residue. -/
theorem fallingPacket_canonical_fourier_bridge {N r : ℕ}
    (hN : 0 < N) (hr : r < N) (p : ℚ[X]) :
    average N r (Complex.exp (2 * Real.pi * Complex.I / (N : ℂ)))
        ((fallingEquiv.symm p).map (algebraMap ℚ ℂ)) =
      (fallingEquiv.symm (fallingPacket N r p)).map (algebraMap ℚ ℂ) := by
  exact fallingPacket_fourier_bridge hN hr (Complex.isPrimitiveRoot_exp N hN.ne') p

end Komorebi.Polynomial.FourierBridge
