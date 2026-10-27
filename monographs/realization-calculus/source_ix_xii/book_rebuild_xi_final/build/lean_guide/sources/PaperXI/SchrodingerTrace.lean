import PaperXI.SchrodingerOperator
import Mathlib.LinearAlgebra.Trace
import Mathlib.NumberTheory.GaussSum
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic

/-! Character support for the literal finite function-space Schrödinger operators. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchrodingerTrace
open scoped Classical

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- A nonzero linear functional onto the scalar field is surjective. -/
theorem functional_surjective {ξ : X →ₗ[K] K} (hξ : ξ ≠ 0) :
    Function.Surjective ξ := by
  obtain ⟨u, hu⟩ := DFunLike.ne_iff.mp hξ
  change ξ u ≠ 0 at hu
  intro a
  refine ⟨(a / ξ u) • u, ?_⟩
  simp [map_smul, smul_eq_mul, hu]

/-- A nontrivial character remains nontrivial after a nonzero functional. -/
theorem functional_character_ne_one {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    {ξ : X →ₗ[K] K} (hξ : ξ ≠ 0) :
    ψ.compAddMonoidHom ξ.toAddMonoidHom ≠ 1 := by
  intro h
  apply hψ
  ext a
  obtain ⟨u, rfl⟩ := functional_surjective hξ a
  have hu := congrArg (fun χ : AddChar X ℂ => χ u) h
  simpa using hu

variable [Fintype X]

/-- Exact finite Fourier cancellation for every nonzero scalar functional. -/
theorem sum_functional_character {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    {ξ : X →ₗ[K] K} (hξ : ξ ≠ 0) : (∑ u : X, ψ (ξ u)) = 0 := by
  exact AddChar.sum_eq_zero_of_ne_one (functional_character_ne_one hψ hξ)

/-- The diagonal matrix entries are computed in the actual delta-function basis. -/
theorem operator_diagonal (ψ : AddChar K ℂ) (x : X) (ξ : X →ₗ[K] K)
    (z : K) (u : X) :
    LinearMap.toMatrix (Pi.basisFun ℂ X) (Pi.basisFun ℂ X)
      (Schrodinger.operator ψ x ξ z) u u =
      if x = 0 then ψ (z + ξ u) else 0 := by
  classical
  rw [LinearMap.toMatrix_apply, Pi.basisFun_repr, Schrodinger.operator_apply,
    Pi.basisFun_apply]
  by_cases hx : x = 0
  · subst x
    simp
  · have hux : u + x ≠ u := by simpa using hx
    simp [hx, hux]

/-- Translation by a nonzero vector has no diagonal contribution. -/
theorem trace_of_translation_ne_zero (ψ : AddChar K ℂ) {x : X} (hx : x ≠ 0)
    (ξ : X →ₗ[K] K) (z : K) :
    LinearMap.trace ℂ (X → ℂ) (Schrodinger.operator ψ x ξ z) = 0 := by
  classical
  rw [LinearMap.trace_eq_matrix_trace ℂ (Pi.basisFun ℂ X)]
  simp [Matrix.trace, hx]

/-- Pure modulation has trace equal to its literal finite character sum. -/
theorem trace_of_translation_zero (ψ : AddChar K ℂ) (ξ : X →ₗ[K] K) (z : K) :
    LinearMap.trace ℂ (X → ℂ) (Schrodinger.operator ψ 0 ξ z) =
      ψ z * ∑ u : X, ψ (ξ u) := by
  classical
  rw [LinearMap.trace_eq_matrix_trace ℂ (Pi.basisFun ℂ X)]
  simp [Matrix.trace, ψ.map_add_eq_mul, Finset.mul_sum]

/-- Proposition 7.3: exact character support, without assuming the trace formula. -/
theorem character_support {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    (x : X) (ξ : X →ₗ[K] K) (z : K) :
    LinearMap.trace ℂ (X → ℂ) (Schrodinger.operator ψ x ξ z) =
      if x = 0 ∧ ξ = 0 then (Fintype.card X : ℂ) * ψ z else 0 := by
  classical
  by_cases hx : x = 0
  · subst x
    rw [trace_of_translation_zero]
    by_cases hξ : ξ = 0
    · subst ξ
      simp [mul_comm]
    · simp [hξ, sum_functional_character hψ hξ]
  · simp [hx, trace_of_translation_ne_zero ψ hx]

end PaperXI.SchrodingerTrace
