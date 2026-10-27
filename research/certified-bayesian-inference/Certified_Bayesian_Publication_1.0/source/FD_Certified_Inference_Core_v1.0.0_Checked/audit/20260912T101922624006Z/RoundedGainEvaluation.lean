import Komorebi.PrecisionModel
import Komorebi.PrecisionSelection
import Komorebi.RationalRichardsonDefs
import Komorebi.RoundoffEnergy

set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior
variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [DecidableEq κ]

/-- The ideal update is a specification, not the executed gain calculation. -/
def exactGainStep (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : Matrix ι κ ℚ :=
  B+M.solverStep • M.residual B

/-- Execute the retained outward-rounded arithmetic graph for the entire gain update. -/
def updateBall (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BallMatrix ι κ :=
  fun i j => rAdd p (rExact p (B i j))
    (rMul p (rExact p M.solverStep) (residualBall p M B i j))

/-- Magnitude/radius prediction for that same graph, without evaluating the exact residual. -/
def updateBudget (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BudgetMatrix ι κ :=
  fun i j => Budget.plus (Budget.input (B i j))
    (Budget.times (Budget.input M.solverStep) (residualBudget M B i j))

theorem updateBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    MatrixBudgetBounds p (updateBall p M B) (exactGainStep M B) (updateBudget M B) := by
  intro i j
  exact Budget.plus_bounds p (Budget.input_bounds p _) (Budget.times_bounds p
    (Budget.input_bounds p _) (residualBudget_bounds p M B i j))

/-- Sum rather than maximum keeps the predictor valid for empty index types. -/
def updateRadiusCoeff (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : ℚ :=
  ∑ i, ∑ j, (updateBudget M B i j).coeff

theorem update_coeff_le (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (i : ι) (j : κ) :
    (updateBudget M B i j).coeff ≤ updateRadiusCoeff M B := by
  apply (Finset.single_le_sum (f := fun j => (updateBudget M B i j).coeff)
    (fun j _ => (updateBudget M B i j).coeff_nonneg) (Finset.mem_univ j)).trans
  exact Finset.single_le_sum
    (fun i _ => Finset.sum_nonneg fun j _ => (updateBudget M B i j).coeff_nonneg)
    (Finset.mem_univ i)

/-- t specifies local accuracy; the actual arithmetic precision is recomputed for each state. -/
def updatePrecision (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) : ℕ :=
  precisionFor (updateRadiusCoeff M B) (mesh t)

def roundedGainStep (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) : Matrix ι κ ℚ :=
  fun i j => (updateBall (updatePrecision M t B) M B i j).center

/-- Whole-update error includes all rounding in the model/residual and final correction graph. -/
theorem rounded_step_entry_error (M : RationalModel ι κ υ ω) (t : ℕ)
    (B : Matrix ι κ ℚ) (i : ι) (j : κ) :
    |(roundedGainStep M t B-exactGainStep M B) i j| ≤ mesh t := by
  let p := updatePrecision M t B
  have hb := updateBudget_bounds p M B i j
  have he : |(roundedGainStep M t B-exactGainStep M B) i j| ≤
      (updateBall p M B i j).radius := by
    change |(updateBall p M B i j).center-(exactGainStep M B) i j| ≤ _
    rw [abs_sub_comm]
    exact hb.2.1
  have hk := mul_le_mul_of_nonneg_right (update_coeff_le M B i j) (mesh_pos p).le
  exact he.trans (hb.2.2.trans (hk.trans
    (coefficient_mesh_le (updateRadiusCoeff M B) (mesh t) (mesh_pos t) p le_rfl)))

/-- Number of entries, in the rational squared-energy normalization. -/
def entryCount (ι κ : Type*) [Fintype ι] [Fintype κ] : ℚ :=
  (Fintype.card ι : ℚ)*(Fintype.card κ : ℚ)

omit [Fintype υ] [Fintype ω] [DecidableEq κ] in
theorem entryCount_nonneg : 0 ≤ entryCount ι κ := by unfold entryCount; positivity

theorem rounded_step_energy_error (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) :
    rationalEnergy (roundedGainStep M t B-exactGainStep M B) ≤ entryCount ι κ*(mesh t)^2 := by
  have h := Finset.sum_le_sum fun i (_ : i ∈ Finset.univ) =>
    Finset.sum_le_sum fun j (_ : j ∈ Finset.univ) =>
      (show ((roundedGainStep M t B-exactGainStep M B) i j)^2 ≤ (mesh t)^2 by
        have hh := rounded_step_entry_error M t B i j
        have ha := abs_nonneg ((roundedGainStep M t B-exactGainStep M B) i j)
        nlinarith only [hh, ha, (mesh_pos t).le,
          sq_abs ((roundedGainStep M t B-exactGainStep M B) i j)])
  simpa only [rationalEnergy, Finset.sum_const, Finset.card_univ, nsmul_eq_mul,
    entryCount, mul_assoc] using h

theorem rounded_step_grid (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ)
    (i : ι) (j : κ) : ∃ z : ℤ,
    roundedGainStep M t B i j = (z : ℚ)/scale (updatePrecision M t B) := by
  exact ⟨_,rfl⟩

end Komorebi.RoundoffSolver
