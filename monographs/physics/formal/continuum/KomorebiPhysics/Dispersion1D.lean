module

public import KomorebiPhysics.DiracWalk1D
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Inverse

/-!
Exact principal-branch dispersion shell for the one-dimensional discrete relativistic update.
No small-spacing expansion is used in this module.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Dispersion1D

open scoped Matrix ComplexConjugate
open KomorebiPhysics.RelativisticPauli KomorebiPhysics.DiracWalk1D

/-- The real exact shell appearing in the normalized trace. -/
def shell (m k ε : ℝ) : ℝ := Real.cos (m * ε) * Real.cos (k * ε)

/-- Principal phase in `[0,π]`. -/
def principalPhase (m k ε : ℝ) : ℝ := Real.arccos (shell m k ε)

/-- Principal frequency. The nonzero-spacing proof is explicit in the interface. -/
def principalFrequency (m k ε : ℝ) (_hε : ε ≠ 0) : ℝ :=
  principalPhase m k ε / ε

/-- The shell always lies in the domain of the real arccosine. -/
theorem abs_shell_le_one (m k ε : ℝ) : |shell m k ε| ≤ 1 := by
  rw [shell, abs_mul]
  calc
    |Real.cos (m * ε)| * |Real.cos (k * ε)|
        ≤ 1 * 1 := mul_le_mul (Real.abs_cos_le_one _) (Real.abs_cos_le_one _)
          (abs_nonneg _) (by norm_num)
    _ = 1 := by norm_num

/-- Lower shell bound needed by `cos(arccos x)=x`. -/
theorem neg_one_le_shell (m k ε : ℝ) : -1 ≤ shell m k ε :=
  (abs_le.mp (abs_shell_le_one m k ε)).1

/-- Upper shell bound needed by `cos(arccos x)=x`. -/
theorem shell_le_one (m k ε : ℝ) : shell m k ε ≤ 1 :=
  (abs_le.mp (abs_shell_le_one m k ε)).2

/-- The principal phase is nonnegative. -/
theorem principalPhase_nonneg (m k ε : ℝ) : 0 ≤ principalPhase m k ε := by
  exact Real.arccos_nonneg _

/-- The principal phase lies below π. -/
theorem principalPhase_le_pi (m k ε : ℝ) : principalPhase m k ε ≤ Real.pi := by
  exact Real.arccos_le_pi _

/-- Exact shell equation at the level of the principal phase. -/
theorem cos_principalPhase (m k ε : ℝ) :
    Real.cos (principalPhase m k ε) = shell m k ε := by
  exact Real.cos_arccos (neg_one_le_shell m k ε) (shell_le_one m k ε)

/-- Equation (8.6) on the explicitly selected principal branch. -/
theorem principalFrequency_shell (m k ε : ℝ) (hε : ε ≠ 0) :
    Real.cos (principalFrequency m k ε hε * ε) = shell m k ε := by
  have hcancel : principalFrequency m k ε hε * ε = principalPhase m k ε := by
    rw [principalFrequency]
    exact div_mul_cancel₀ _ hε
  rw [hcancel, cos_principalPhase]

/-- Equation (8.7), with the nonzero-spacing hypothesis kept explicit. -/
theorem principalFrequency_formula (m k ε : ℝ) (hε : ε ≠ 0) :
    principalFrequency m k ε hε =
      Real.arccos (Real.cos (m * ε) * Real.cos (k * ε)) / ε := by
  rfl

/-- For positive spacing, the principal frequency is nonnegative. -/
theorem principalFrequency_nonneg_of_pos (m k ε : ℝ) (hε : 0 < ε) :
    0 ≤ principalFrequency m k ε (ne_of_gt hε) := by
  exact div_nonneg (principalPhase_nonneg m k ε) (le_of_lt hε)

/-- For positive spacing, the principal frequency is at most `π/ε`. -/
theorem principalFrequency_le_pi_div_of_pos (m k ε : ℝ) (hε : 0 < ε) :
    principalFrequency m k ε (ne_of_gt hε) ≤ Real.pi / ε := by
  exact div_le_div_of_nonneg_right (principalPhase_le_pi m k ε) (le_of_lt hε)

/-- The principal branch is unique once `ω ε` is restricted to `[0,π]`. -/
theorem principalFrequency_unique (m k ε ω : ℝ) (hε : ε ≠ 0)
    (h0 : 0 ≤ ω * ε) (hπ : ω * ε ≤ Real.pi)
    (hcos : Real.cos (ω * ε) = shell m k ε) :
    ω = principalFrequency m k ε hε := by
  have hphase : principalPhase m k ε = ω * ε := by
    unfold principalPhase
    exact Real.arccos_eq_of_eq_cos h0 hπ hcos.symm
  rw [principalFrequency, hphase]
  field_simp

/-- The shell is even in the mass parameter. -/
theorem shell_neg_mass (m k ε : ℝ) : shell (-m) k ε = shell m k ε := by
  simp [shell]

/-- The shell is even in the momentum parameter. -/
theorem shell_neg_momentum (m k ε : ℝ) : shell m (-k) ε = shell m k ε := by
  simp [shell]

/-- Mass and momentum enter the exact 1D shell symmetrically. -/
theorem shell_swap (m k ε : ℝ) : shell m k ε = shell k m ε := by
  simp [shell, mul_comm]

/-- The principal frequency inherits mass-sign symmetry. -/
theorem principalFrequency_neg_mass (m k ε : ℝ) (hε : ε ≠ 0) :
    principalFrequency (-m) k ε hε = principalFrequency m k ε hε := by
  simp [principalFrequency, principalPhase, shell]

/-- The principal frequency inherits momentum-sign symmetry. -/
theorem principalFrequency_neg_momentum (m k ε : ℝ) (hε : ε ≠ 0) :
    principalFrequency m (-k) ε hε = principalFrequency m k ε hε := by
  simp [principalFrequency, principalPhase, shell]

/-- A general 2x2 characteristic-polynomial identity. -/
theorem det_scalar_sub (A : Mat2) (z : ℂ) :
    Matrix.det (z • (1 : Mat2) - A) =
      z ^ 2 - z * Matrix.trace A + Matrix.det A := by
  rw [Matrix.det_fin_two, Matrix.trace_fin_two, Matrix.det_fin_two]
  simp [Matrix.sub_apply, Matrix.smul_apply]
  ring

/-- Exact characteristic polynomial of the one-dimensional update. -/
theorem characteristic_polynomial (m k ε : ℝ) (z : ℂ) :
    Matrix.det (z • (1 : Mat2) - update m k ε) =
      z ^ 2 - 2 * (shell m k ε : ℂ) * z + 1 := by
  rw [det_scalar_sub, trace_update, det_update]
  simp [shell]
  ring

/-- Every exact eigenvalue satisfies the quadratic shell equation. -/
theorem eigenvalue_shell {m k ε : ℝ} {z : ℂ}
    (hz : Matrix.det (z • (1 : Mat2) - update m k ε) = 0) :
    z ^ 2 - 2 * (shell m k ε : ℂ) * z + 1 = 0 := by
  rw [characteristic_polynomial] at hz
  exact hz

/-- The update trace is literally twice the real shell. -/
theorem trace_eq_two_shell (m k ε : ℝ) :
    Matrix.trace (update m k ε) = 2 * (shell m k ε : ℂ) := by
  simpa [shell] using trace_update m k ε

end KomorebiPhysics.Dispersion1D
