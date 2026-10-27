module
public import Euler.NormalizedLowerChart
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- A coefficientwise four-weighted series, without any convergence hypothesis
on the unscaled seed.  The image itself is automatically restricted. -/
def FourScaled (f : Series) : Prop := ∃ e : Series, f = rescale (4:D) e

lemma fourScaled_of_coeff (f : Series)
    (h : ∀ n, ∃ c:D, coeff n f = (4:D)^n*c) : FourScaled f := by
  choose c hc using h
  refine ⟨mk c, ?_⟩
  ext n
  simp only [coeff_rescale, coeff_mk]
  exact hc n

lemma fourScaled_coeff {f : Series} (h : FourScaled f) (n : ℕ) :
    ∃ c:D, coeff n f = (4:D)^n*c := by
  obtain ⟨e,rfl⟩ := h
  exact ⟨coeff n e, coeff_rescale _ _ _⟩

lemma fourScaled_C (c : D) : FourScaled (C c) := by
  refine fourScaled_of_coeff _ ?_
  intro n
  cases n with
  | zero => exact ⟨c, by simp⟩
  | succ n => exact ⟨0, by simp⟩

lemma fourScaled_one : FourScaled (1:Series) := by
  simpa only [map_one] using fourScaled_C (1:D)

lemma fourScaled_mul {f g : Series} (hf : FourScaled f) (hg : FourScaled g) :
    FourScaled (f*g) := by
  obtain ⟨e,rfl⟩ := hf
  obtain ⟨d,rfl⟩ := hg
  exact ⟨e*d, (map_mul (rescale (4:D)) e d).symm⟩

lemma fourScaled_neg {f : Series} (hf : FourScaled f) : FourScaled (-f) := by
  obtain ⟨e,rfl⟩ := hf
  exact ⟨-e, (map_neg (rescale (4:D)) e).symm⟩

lemma fourScaled_prod {ι : Type*} (s : Finset ι) (f : ι → Series)
    (h : ∀ i∈s, FourScaled (f i)) : FourScaled (∏ i∈s, f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using fourScaled_one
  | @insert a s ha ih =>
    rw [Finset.prod_insert ha]
    exact fourScaled_mul (h a (by simp)) (ih (fun i hi => h i (by simp [hi])))

lemma fourScaled_linear (a c : D) : FourScaled (C a+C (4*c)*X) := by
  apply fourScaled_of_coeff
  intro n
  rcases n with _ | _ | n
  · exact ⟨a, by simp⟩
  · exact ⟨c, by simp⟩
  · exact ⟨0, by simp⟩

lemma fourScaled_restricted {f : Series} (hf : FourScaled f) : Restricted f := by
  obtain ⟨e,rfl⟩ := hf
  rw [restricted_iff]
  apply squeeze_zero (g := fun n => ‖(4:D)‖^n) (fun _ => norm_nonneg _)
  · intro n
    rw [coeff_rescale, norm_mul, norm_pow]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)
  · apply tendsto_pow_atTop_nhds_zero_of_lt_one (norm_nonneg _)
    have h4 : ‖(4:D)‖=(1/4:ℝ) := by
      rw [show (4:D)=(2:D)^2 by norm_num, norm_pow, norm_two]
      norm_num
    rw [h4]
    norm_num

lemma two_power_split_four (k : ℕ) (hk : 2≤k) :
    (2:D)^k = (4:D)*(2:D)^(k-2) := by
  rw [show (4:D)=(2:D)^2 by norm_num, ← pow_add, Nat.add_sub_of_le hk]

/-- Hasse-defined affine localization has the required weighted seed. -/
lemma restrictedAffine_fourScaled (f : Series) (a:D) (k:ℕ) (hk:2≤k) :
    FourScaled (restrictedAffine f a ((2:D)^k)) := by
  apply fourScaled_of_coeff
  intro n
  refine ⟨((2:D)^(k-2))^n*rjet n f a, ?_⟩
  rw [coeff_restrictedAffine, two_power_split_four k hk, mul_pow]
  ring

/-- The slope tail centered at the skeleton point has the same weighted form. -/
lemma lowerAffineTail_fourScaled (f : Series) (a:D) (k:ℕ) (hk:2≤k) :
    FourScaled (lowerAffineTail f a k) := by
  apply fourScaled_of_coeff
  intro n
  refine ⟨((2:D)^(k-2))^n*rjet (n+1) f a, ?_⟩
  rw [coeff_lowerAffineTail, two_power_split_four k hk, mul_pow]
  ring

end Komorebi.Euler
