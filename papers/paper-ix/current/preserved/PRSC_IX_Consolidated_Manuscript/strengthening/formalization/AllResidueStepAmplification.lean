module
public import StepAmplification
public import AllResidueEuler
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.AllResidueStepAmplification
open Mahler AllResidueEuler GlobalEulerBoundary
variable (p : ℕ) [Fact p.Prime]

/-- Step-sensitive ideal divisibility for every actual residue on the divisor branch. -/
theorem unnormalized_bound (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    (p:ℤ_[p])^(min (k*(padicValNat p u+1)) (m*n)) ∣
      difference (u*((p-1)/m)) k (unnormalizedLift p m j hm hmpos hj) n := by
  exact StepAmplification.repeated_precision p (unnormalizedLift p m j hm hmpos hj)
    ((p-1)/m) n u (m*n) (fun a => by
      simpa only [one_mul] using global_unnormalized_bound p m j 1 a n hm hmpos hj) k

/-- The bound is on the same original rational coefficients as the completed theorem. -/
theorem unnormalized_precision (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    precision p ((min (k*(padicValNat p u+1)) (m*n):ℕ):ℤ)
      (difference (u*((p-1)/m)) k (Congruential.unnormalized (m*p) j) n) := by
  apply StandardWindowPrecision.rational_precision_of_divisibility p
    (difference (u*((p-1)/m)) k (unnormalizedLift p m j hm hmpos hj) n)
  · change (algebraMap ℤ_[p] ℚ_[p]) (difference _ _ _ _) =
      (algebraMap ℚ ℚ_[p]) (difference _ _ _ _)
    rw [←DifferenceFiltration.difference_map,←DifferenceFiltration.difference_map]
    congr 1
    funext r
    exact unnormalizedLift_coe p m j r hm hmpos hj
  · exact unnormalized_bound p m j u k n hm hmpos hj

/-- Normalization on this branch retains the factorial loss already required by the baseline. -/
theorem normalized_precision (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    precision p (((min (k*(padicValNat p u+1)) (m*n):ℕ):ℤ)-padicValNat p j.factorial)
      (difference (u*((p-1)/m)) k (Congruential.coeff (m*p) j) n) :=
  factorial_loss_transfer p (m*p) j _ k n _
    (unnormalized_precision p m j u k n hm hmpos hj)

end KomorebiPaperIX.AllResidueStepAmplification
