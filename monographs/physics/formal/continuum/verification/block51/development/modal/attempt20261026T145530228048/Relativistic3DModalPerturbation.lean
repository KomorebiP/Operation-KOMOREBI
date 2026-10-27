import KomorebiPhysics.Relativistic3DGeneratorBridge

/-!
# Unitary modal perturbation estimate

The interpolation proof keeps the two Hamiltonians in their original order.
No commutation assumption between them is used.
Copyright (c) 2026 Komorebi P. Released under the MIT license.
-/
noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

namespace KomorebiPhysics
namespace Relativistic3DModalPerturbation

open Relativistic3DFourierHilbertStability
open Relativistic3DGeneratorBridge

local instance : NormedAlgebra ℚ HilbertSpinorEnd :=
  NormedAlgebra.restrictScalars ℚ ℂ HilbertSpinorEnd

/-- The actual Banach-algebra exponential for a Hermitian mode Hamiltonian. -/
def modalEvolution (A : HilbertSpinorEnd) (t : ℝ) : HilbertSpinorEnd :=
  NormedSpace.exp (hilbertTimeScaledOperator t A)

@[simp] theorem modalEvolution_zero (A : HilbertSpinorEnd) : modalEvolution A 0 = 1 := by
  have hz : hilbertTimeScaledOperator 0 A = 0 := by
    ext ψ j
    simp [hilbertTimeScaledOperator]
  rw [modalEvolution, hz, NormedSpace.exp_zero]

/-- Self-adjoint mode Hamiltonians generate norm-preserving maps. -/
theorem modalEvolution_norm (A : HilbertSpinorEnd) (hA : IsSelfAdjoint A)
    (t : ℝ) (ψ : HilbertSpinor) : ‖modalEvolution A t ψ‖ = ‖ψ‖ := by
  exact ContinuousLinearMap.norm_map_of_mem_unitary
    (NormedSpace.exp_mem_unitary_of_mem_skewAdjoint
      (hilbertTimeScaledOperator_mem_skewAdjoint t hA)) ψ

/-- Right-ordered derivative of one modal evolution. -/
theorem modalEvolution_hasDerivAt (A : HilbertSpinorEnd) (t : ℝ) :
    HasDerivAt (modalEvolution A)
      (modalEvolution A t * ((-Complex.I) • A)) t := by
  change HasDerivAt (fun u => NormedSpace.exp (hilbertTimeScaledOperator u A)) _ t
  simpa only [modalEvolution, timeScaled_eq_real_smul] using
    (hasDerivAt_exp_smul_const ((-Complex.I) • A) t)

/-- Left-ordered derivative, commuting a Hamiltonian only with its own exponential. -/
theorem modalEvolution_hasDerivAt_left (A : HilbertSpinorEnd) (t : ℝ) :
    HasDerivAt (modalEvolution A)
      (((-Complex.I) • A) * modalEvolution A t) t := by
  change HasDerivAt (fun u => NormedSpace.exp (hilbertTimeScaledOperator u A)) _ t
  simpa only [modalEvolution, timeScaled_eq_real_smul] using
    (hasDerivAt_exp_smul_const' ((-Complex.I) • A) t)

/-- Differentiated interpolation with the original noncommutative order intact. -/
theorem modal_interpolation_hasDerivAt (A B : HilbertSpinorEnd) (t s : ℝ)
    (ψ : HilbertSpinor) :
    HasDerivAt (fun u => modalEvolution A (t-u) (modalEvolution B u ψ))
      (Complex.I • modalEvolution A (t-s) ((A-B) (modalEvolution B s ψ))) s := by
  have hA := (modalEvolution_hasDerivAt A (t-s)).scomp s
    ((hasDerivAt_const s t).sub (hasDerivAt_id s))
  have hB := modalEvolution_hasDerivAt_left B s
  have hp := hA.mul hB
  have he := (((ContinuousLinearMap.apply ℂ HilbertSpinor) ψ).restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt s hp
  simpa [Function.comp_def, mul_apply_eq_comp, smul_sub, map_sub] using he

/-- Sharp time factor for perturbing two self-adjoint modal Hamiltonians.
The hypothesis is an actual pointwise bound on their difference, not commutation. -/
theorem modal_perturbation_bound (A B : HilbertSpinorEnd)
    (hA : IsSelfAdjoint A) (hB : IsSelfAdjoint B) (D : ℝ) (_hD : 0 ≤ D)
    (hAB : ∀ φ : HilbertSpinor, ‖(A-B) φ‖ ≤ D * ‖φ‖)
    (t : ℝ) (ψ : HilbertSpinor) :
    ‖modalEvolution A t ψ - modalEvolution B t ψ‖ ≤ |t| * D * ‖ψ‖ := by
  have h := Convex.norm_image_sub_le_of_norm_hasDerivWithin_le
    (s := Set.univ)
    (fun s _ => (modal_interpolation_hasDerivAt A B t s ψ).hasDerivWithinAt)
    (C := D * ‖ψ‖)
    (fun s _ => by
      simp only [norm_smul, Complex.norm_I, one_mul, modalEvolution_norm A hA]
      simpa only [modalEvolution_norm B hB] using hAB (modalEvolution B s ψ))
    (convex_univ : Convex ℝ (Set.univ : Set ℝ))
    (Set.mem_univ t) (Set.mem_univ 0)
  simpa [Real.norm_eq_abs, mul_assoc, mul_comm, mul_left_comm] using h

end Relativistic3DModalPerturbation
end KomorebiPhysics
