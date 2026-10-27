import Komorebi.PosteriorOutput
import Komorebi.PrecisionSelection

set_option autoImplicit false
namespace Komorebi.PosteriorOutput
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior
variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq ι] [DecidableEq κ]

def outputCoefficient (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : ℚ :=
  (∑ i, (meanBudget M B i).coeff) + ∑ i, ∑ j, (covarianceBudget M B i j).coeff

def outputPrecision (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (δ : ℚ) : ℕ :=
  precisionFor (outputCoefficient M B) δ

def represent (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (δ : ℚ) : Arrays ι :=
  evaluate (outputPrecision M B δ) M B

def RadiiAtMost (a : Arrays ι) (δ : ℚ) : Prop :=
  (∀ i, (a.mean i).radius ≤ δ) ∧ (∀ i j, (a.covariance i j).radius ≤ δ)

theorem mean_coeff_le (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (i : ι) :
    (meanBudget M B i).coeff ≤ outputCoefficient M B := by
  have hm := Finset.single_le_sum
    (fun j (_ : j ∈ Finset.univ) => (meanBudget M B j).coeff_nonneg) (Finset.mem_univ i)
  have hc : 0 ≤ ∑ i, ∑ j, (covarianceBudget M B i j).coeff :=
    Finset.sum_nonneg fun i _ => Finset.sum_nonneg fun j _ => (covarianceBudget M B i j).coeff_nonneg
  unfold outputCoefficient
  exact hm.trans (le_add_of_nonneg_right hc)

theorem covariance_coeff_le (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (i j : ι) :
    (covarianceBudget M B i j).coeff ≤ outputCoefficient M B := by
  have hrow := Finset.single_le_sum
    (fun k (_ : k ∈ Finset.univ) => (covarianceBudget M B i k).coeff_nonneg) (Finset.mem_univ j)
  have htotal := Finset.single_le_sum
    (fun k (_ : k ∈ Finset.univ) => Finset.sum_nonneg
      (fun l (_ : l ∈ Finset.univ) => (covarianceBudget M B k l).coeff_nonneg)) (Finset.mem_univ i)
  have hm : 0 ≤ ∑ i, (meanBudget M B i).coeff :=
    Finset.sum_nonneg fun i _ => (meanBudget M B i).coeff_nonneg
  unfold outputCoefficient
  exact (hrow.trans htotal).trans (le_add_of_nonneg_left hm)

theorem evaluate_radii_le (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (δ : ℚ) (hδ : 0 < δ) (p : ℕ) (hp : outputPrecision M B δ ≤ p) :
    RadiiAtMost (evaluate p M B) δ := by
  have hc := coefficient_mesh_le (outputCoefficient M B) δ hδ p hp
  constructor
  · intro i
    exact (mean_bounds p M B i).2.2.trans
      ((mul_le_mul_of_nonneg_right (mean_coeff_le M B i) (mesh_pos p).le).trans hc)
  · intro i j
    exact (covariance_bounds p M B i j).2.2.trans
      ((mul_le_mul_of_nonneg_right (covariance_coeff_le M B i j) (mesh_pos p).le).trans hc)

theorem represent_spec (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (δ : ℚ) (hδ : 0 < δ) :
    EnclosesParameters M B (represent M B δ) ∧ RadiiAtMost (represent M B δ) δ :=
  ⟨evaluate_encloses _ M B, evaluate_radii_le M B δ hδ _ le_rfl⟩

end Komorebi.PosteriorOutput
