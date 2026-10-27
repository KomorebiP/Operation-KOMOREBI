import PaperX.RealAxisPoleRigidity
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-! Finite endpoint limits do not suffice for the pole argument: a square-root
factor cancels half a pole, and taking its square restores a simple pole. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RealAxisPoleBoundary
open Filter Asymptotics
open scoped Topology

def pole (h : ℝ) : ℂ := (h : ℂ)⁻¹
def rootFactor (h : ℝ) : ℂ := (Real.sqrt h : ℂ)

theorem rootFactor_zero : rootFactor 0 = 0 := by simp [rootFactor]

theorem rootFactor_tendsto : Tendsto rootFactor (𝓝[>] 0) (𝓝 0) := by
  have h := Complex.continuous_ofReal.comp Real.continuous_sqrt
  change Tendsto (fun x : ℝ => (Real.sqrt x : ℂ)) (𝓝[>] 0) (𝓝 0)
  simpa [Function.comp_def] using h.continuousAt.tendsto.mono_left
    (nhdsWithin_le_nhds : 𝓝[>] (0 : ℝ) ≤ 𝓝 0)

theorem pole_residue : Tendsto (fun h : ℝ => (h : ℂ) * pole h) (𝓝[>] 0) (𝓝 1) := by
  apply tendsto_const_nhds.congr'
  filter_upwards [self_mem_nhdsWithin] with h hh
  have hh0 : (h : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr (ne_of_gt hh)
  simp [pole, hh0]

/-- The identity holds on the entire positive real axis. -/
theorem squared_product (h : ℝ) (hh : 0 < h) :
    pole h = (pole h * rootFactor h) ^ 2 := by
  have hs : rootFactor h ^ 2 = (h : ℂ) := by
    simpa [rootFactor, ← Complex.ofReal_pow] using
      congrArg (fun x : ℝ => (x : ℂ)) (Real.sq_sqrt (le_of_lt hh))
  have hh0 : (h : ℂ) ≠ 0 := Complex.ofReal_ne_zero.mpr (ne_of_gt hh)
  rw [mul_pow, hs]
  simp only [pole]
  field_simp

theorem eventual_squared_product : pole =ᶠ[𝓝[>] 0]
    fun h => (pole h * rootFactor h) ^ 2 := by
  filter_upwards [self_mem_nhdsWithin] with h hh
  exact squared_product h hh

/-- The square-root factor has a finite endpoint limit but lacks the first-order
error bound used in the real-axis pole theorem. -/
theorem rootFactor_not_isBigO :
    ¬ ((fun h => rootFactor h - rootFactor 0) =O[𝓝[>] 0] fun h : ℝ => (h : ℂ)) := by
  intro hb
  have hid : pole =ᶠ[𝓝[>] 0] fun h =>
      (pole h * ∏ _ : Unit, rootFactor h) ^ 2 := by
    simpa using eventual_squared_product
  have hd := PaperX.RealAxisPoleRigidity.right_endpoint_index_one_and_factors_nonzero
    pole pole (fun _ : Unit => rootFactor) 1 1 2 pole_residue one_ne_zero
    pole_residue one_ne_zero (fun _ => hb) hid
  norm_num at hd

/-- An explicit witness refutes replacement of first-order errors by finite
limits alone, even when both normalized pole residues equal one. -/
theorem finite_limits_do_not_force_index_one :
    ∃ (p Z a : ℝ → ℂ) (d : ℕ),
      Tendsto (fun h : ℝ => (h : ℂ) * p h) (𝓝[>] 0) (𝓝 1) ∧
      Tendsto (fun h : ℝ => (h : ℂ) * Z h) (𝓝[>] 0) (𝓝 1) ∧
      Tendsto a (𝓝[>] 0) (𝓝 (a 0)) ∧
      (Z =ᶠ[𝓝[>] 0] fun h => (p h * a h) ^ d) ∧ d ≠ 1 ∧ a 0 = 0 := by
  exact ⟨pole, pole, rootFactor, 2, pole_residue, pole_residue,
    by simpa [rootFactor_zero] using rootFactor_tendsto,
    eventual_squared_product, by decide, rootFactor_zero⟩

end PaperX.RealAxisPoleBoundary
