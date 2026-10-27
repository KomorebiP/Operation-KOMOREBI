module
public import Euler.ResidualScalars
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.LinearCombination
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Depletion multiplier at a positive Euler coefficient index. -/
def depletionEpsilon (r : ℕ) : ℚ := (2:ℚ)^(2*r-1)

lemma depletionEpsilon_gt_one (r : ℕ) (hr : 0<r) : 1 < depletionEpsilon r := by
  unfold depletionEpsilon
  exact one_lt_pow₀ (by norm_num) (by omega)

lemma depletionFactor_ne_zero (r : ℕ) (hr : 0<r) : 1-depletionEpsilon r ≠ 0 := by
  have h := depletionEpsilon_gt_one r hr
  intro hz
  have : depletionEpsilon r=1 := by linear_combination -hz
  rw [this] at h
  exact (lt_irrefl _ h)

/-- Its zero-depth convention is separate from the positive-index depletion. -/
def depletedEulerBetaRat (m : ℕ) : ℚ :=
  if m=0 then 1 else (1-depletionEpsilon m)*eulerBetaRat m

lemma depletedEulerBetaRat_of_pos (m : ℕ) (hm : 0<m) :
    depletedEulerBetaRat m = (1-depletionEpsilon m)*eulerBetaRat m := by
  simp [depletedEulerBetaRat, Nat.ne_of_gt hm]

lemma depletedEulerBetaRat_ne_zero (m : ℕ) : depletedEulerBetaRat m ≠ 0 := by
  rcases Nat.eq_zero_or_pos m with rfl | hm
  · simp [depletedEulerBetaRat]
  · rw [depletedEulerBetaRat_of_pos m hm]
    exact mul_ne_zero (depletionFactor_ne_zero m hm) (eulerBetaRat_ne_zero m)

lemma depletionEpsilon_add (r q : ℕ) (hr : 0<r) :
    depletionEpsilon (r+q)=depletionEpsilon r*(4:ℚ)^q := by
  unfold depletionEpsilon
  rw [show 2*(r+q)-1=(2*r-1)+2*q by omega, pow_add]
  congr 1
  rw [pow_mul]
  norm_num

/-- Exact Euler-defined ratio. No claim of root preservation is made. -/
theorem eulerBeta_undepletion_ratio (r q : ℕ) (hr : 0<r) :
    eulerBetaRat (r+q)/eulerBetaRat r =
    (depletedEulerBetaRat (r+q)/depletedEulerBetaRat r) *
      ((1-depletionEpsilon r)/(1-depletionEpsilon r*(4:ℚ)^q)) := by
  rw [depletedEulerBetaRat_of_pos _ (by omega), depletedEulerBetaRat_of_pos _ hr,
    depletionEpsilon_add r q hr]
  have hden := depletionFactor_ne_zero (r+q) (by omega)
  rw [depletionEpsilon_add r q hr] at hden
  field_simp [depletionFactor_ne_zero r hr, eulerBetaRat_ne_zero r, hden]

section Field
variable {K : Type*} [Field K]

/-- The packetwise resolvent weight. -/
def spectralWeight (e z : K) : K := (1-e)/(1-e*z)

@[simp] lemma spectralWeight_zero (z : K) : spectralWeight 0 z=1 := by
  simp [spectralWeight]

lemma spectralWeight_one (e : K) (he : 1-e ≠ 0) : spectralWeight e 1=1 := by
  simp [spectralWeight, he]

lemma spectralWeight_first_defect (e z : K) (h : 1-e*z ≠ 0) :
    spectralWeight e z-1=e*(z-1)/(1-e*z) := by
  unfold spectralWeight
  field_simp [h]
  ring

lemma spectralWeight_second_remainder (e z : K) (h : 1-e*z ≠ 0) :
    spectralWeight e z-(1+e*(z-1))=e^2*z*(z-1)/(1-e*z) := by
  unfold spectralWeight
  field_simp [h]
  ring

/-- Every finite correction order with its exact rational remainder. -/
theorem spectralWeight_finite_expansion (e z : K) (h : 1-e*z ≠ 0) (M : ℕ) :
    spectralWeight e z = 1 +
      (∑ m ∈ Finset.range M, e^(m+1)*z^m*(z-1)) +
      e^(M+1)*z^M*(z-1)/(1-e*z) := by
  induction M with
  | zero =>
      simpa using (sub_eq_iff_eq_add.mp (spectralWeight_first_defect e z h)).trans
        (by ring)
  | succ M ih =>
      have step : e^(M+1)*z^M*(z-1)/(1-e*z) =
          e^(M+1)*z^M*(z-1) +
          e^(M+1+1)*z^(M+1)*(z-1)/(1-e*z) := by
        apply (div_eq_iff h).2
        rw [add_mul, div_mul_cancel₀ _ h]
        simp only [pow_succ]
        ring
      rw [Finset.sum_range_succ, ih, step]
      ring

end Field
end Komorebi.Euler
