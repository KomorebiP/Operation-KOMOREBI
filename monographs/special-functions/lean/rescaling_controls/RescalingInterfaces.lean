import CoupledRescaling
open Komorebi.SpecialFunctions.Coupled
open Scales

noncomputable section

def swapSurface : Scales := ⟨1 / 2, 1 / 8, 1 / 2, 1 / 2⟩
def orderedSurface : Scales := ⟨1 / 4, 1 / 4, 1 / 2, 1 / 2⟩

example : swapSurface.q = swapSurface.b ∧
    swapSurface.q * swapSurface.b ≠ swapSurface.a * swapSurface.r := by
  norm_num [swapSurface]

example : orderedSurface.q ≠ orderedSurface.b ∧
    orderedSurface.q * orderedSurface.b = orderedSurface.a * orderedSurface.r := by
  norm_num [orderedSurface]

example (z : ℂ) : swapSurface.V z = (swapSurface.reductionScale : ℂ)⁻¹ *
    swapSurface.U ((swapSurface.reductionScale : ℂ) * z) :=
  swapSurface.canonical_component_rescaling (by norm_num [positive, swapSurface])
    (by norm_num [swapSurface]) (Or.inl rfl) z

example (z : ℂ) : orderedSurface.U z = (orderedSurface.reductionRoot : ℂ) *
    scalarT orderedSurface.q (orderedSurface.reductionScale * orderedSurface.r)
      ((orderedSurface.reductionRoot : ℂ)⁻¹ * z) :=
  (orderedSurface.coupled_scalar_representation (by norm_num [positive, orderedSurface])
    (by norm_num [orderedSurface]) (Or.inr (by norm_num [orderedSurface])) z).1

example : swapSurface.reductionScale = 2 ∧ orderedSurface.reductionScale = 2 := by
  have hsqrt : Real.sqrt (4 : ℝ) = 2 := by
    apply (Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)).mpr
    norm_num
  norm_num [reductionScale, k, p, swapSurface, orderedSurface, hsqrt]

example : boundaryLeft.U = boundaryRight.U ∧ boundaryLeft.V = boundaryRight.V ∧
    boundaryLeft ≠ boundaryRight := boundary_entire_collision

-- A normalized nonreal candidate has AB=1, but fails the positive cubic term.
example (he : ∀ z, boundaryLeft.V z = -Complex.I * boundaryLeft.U (Complex.I * z)) :
    False := by
  have h := boundaryLeft.rescaling_coefficient_identity boundary_collision.1
    (by norm_num [boundaryLeft]) he 1
  norm_num [coefficients_one, u1, v1, p, k, boundaryLeft, pow_succ, Complex.I_sq] at h
  have hI : Complex.I * (1 / 24 : ℂ) * Complex.I = -(1 / 24 : ℂ) := by
    linear_combination (1 / 24 : ℂ) * Complex.I_sq
  rw [hI] at h
  norm_num at h
