import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.Tactic

/-! Author: Komorebi P. Finite Bayesian normalization with explicit evidence conditions. -/
namespace KomorebiPaperVI.FiniteBayes
open scoped BigOperators
variable {I : Type*} [Fintype I]

def mass (p : I → ℝ) : ℝ := ∑ i, p i
noncomputable def normalize (p : I → ℝ) (i : I) : ℝ := p i / mass p
def evidence (p l : I → ℝ) : ℝ := ∑ i, l i*p i
noncomputable def update (p l : I → ℝ) (i : I) : ℝ := l i*p i / evidence p l
def l1 (p : I → ℝ) : ℝ := ∑ i, |p i|

theorem normalized_mass (p : I → ℝ) (hp : mass p ≠ 0) : mass (normalize p) = 1 := by
  simp only [mass, normalize, ← Finset.sum_div]
  exact div_self hp

theorem posterior_mass (p l : I → ℝ) (hz : evidence p l ≠ 0) : mass (update p l) = 1 := by
  simp only [mass, update, ← Finset.sum_div]
  exact div_self hz

theorem posterior_nonnegative (p l : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hl : ∀ i, 0 ≤ l i) (hz : 0 < evidence p l) (i : I) : 0 ≤ update p l i :=
  div_nonneg (mul_nonneg (hl i) (hp i)) hz.le

theorem evidence_scale (p l : I → ℝ) (c : ℝ) :
    evidence p (fun i => c*l i) = c*evidence p l := by
  simp only [evidence, Finset.mul_sum, mul_assoc]

theorem posterior_scale (p l : I → ℝ) (c : ℝ) (hc : c ≠ 0)
    (hz : evidence p l ≠ 0) : update p (fun i => c*l i) = update p l := by
  funext i
  simp only [update, evidence_scale]
  field_simp

theorem sequential_evidence (p l k : I → ℝ) :
    evidence (update p l) k = evidence p (fun i => l i*k i) / evidence p l := by
  simp only [evidence, update, ← mul_div_assoc, ← Finset.sum_div]
  congr 1
  apply Finset.sum_congr rfl
  intro i _
  ring

theorem posterior_composition (p l k : I → ℝ) (hz : evidence p l ≠ 0)
    (hzk : evidence p (fun i => l i*k i) ≠ 0) :
    update (update p l) k = update p (fun i => l i*k i) := by
  funext i
  rw [update, sequential_evidence]
  dsimp [update]
  field_simp

theorem posterior_difference (p l k : I → ℝ) (hl : evidence p l ≠ 0)
    (hk : evidence p k ≠ 0) (i : I) :
    update p l i-update p k i =
      (p i*(l i-k i)-update p k i*(∑ j, p j*(l j-k j))) / evidence p l := by
  have hs : (∑ j, p j*(l j-k j)) = evidence p l-evidence p k := by
    simp only [evidence, mul_sub, Finset.sum_sub_distrib]
    congr 1 <;> apply Finset.sum_congr rfl <;> intros <;> ring
  rw [hs]
  dsimp [update]
  field_simp
  ring

theorem scale_null_direction (p k : I → ℝ) (hk : evidence p k ≠ 0) (i : I) :
    p i*k i-update p k i*(∑ j, p j*k j)=0 := by
  have hs : (∑ j, p j*k j) = evidence p k := by simp [evidence, mul_comm]
  rw [hs]
  dsimp [update]
  field_simp
  ring

theorem normalized_l1_bound_left (w v : I → ℝ) (hv : ∀ i, 0 ≤ v i)
    (hW : 0 < mass w) (hV : 0 < mass v) :
    l1 (fun i => normalize w i-normalize v i) ≤
      2*l1 (fun i => w i-v i)/mass w := by
  have hd : |mass v-mass w| ≤ l1 (fun i => w i-v i) := by
    rw [mass, mass, ← Finset.sum_sub_distrib]
    simpa only [l1, abs_sub_comm] using Finset.abs_sum_le_sum_abs (fun i => v i-w i) Finset.univ
  have point (i : I) : |normalize w i-normalize v i| ≤
      |w i-v i|/mass w + (v i/mass v)*(|mass v-mass w|/mass w) := by
    have he : normalize w i-normalize v i =
        (w i-v i)/mass w+(v i/mass v)*((mass v-mass w)/mass w) := by
      dsimp [normalize]
      field_simp
      ring
    rw [he]
    calc
      _ ≤ |(w i-v i)/mass w|+|(v i/mass v)*((mass v-mass w)/mass w)| := abs_add_le _ _
      _ = _ := by simp only [abs_mul, abs_div, abs_of_pos hW, abs_of_pos hV, abs_of_nonneg (hv i)]
  calc
    _ ≤ ∑ i, (|w i-v i|/mass w+(v i/mass v)*(|mass v-mass w|/mass w)) :=
      Finset.sum_le_sum (fun i _ => point i)
    _ = l1 (fun i => w i-v i)/mass w+|mass v-mass w|/mass w := by
      rw [Finset.sum_add_distrib, ← Finset.sum_div, ← Finset.sum_mul, ← Finset.sum_div]
      simp only [mass, l1] at *
      rw [div_self (ne_of_gt hV), one_mul]
    _ ≤ l1 (fun i => w i-v i)/mass w+l1 (fun i => w i-v i)/mass w :=
      add_le_add_right (div_le_div_of_nonneg_right hd hW.le) _
    _ = _ := by ring

theorem likelihood_perturbation_bound (p l k : I → ℝ)
    (hp : ∀ i, 0 ≤ p i) (_hl : ∀ i, 0 ≤ l i) (hk : ∀ i, 0 ≤ k i)
    (hZl : 0 < evidence p l) (hZk : 0 < evidence p k) :
    l1 (fun i => update p l i-update p k i) ≤
      2*(∑ i, |l i-k i| *p i)/min (evidence p l) (evidence p k) := by
  have he : l1 (fun i => l i*p i-k i*p i) = ∑ i, |l i-k i| *p i := by
    simp only [l1, ← sub_mul, abs_mul, abs_of_nonneg (hp _)]
  have h := normalized_l1_bound_left (fun i => l i*p i) (fun i => k i*p i)
    (fun i => mul_nonneg (hk i) (hp i)) hZl hZk
  change l1 (fun i => update p l i-update p k i) ≤
    2*l1 (fun i => l i*p i-k i*p i)/evidence p l at h
  rw [he] at h
  exact h.trans (div_le_div_of_nonneg_left
    (mul_nonneg (by norm_num) (Finset.sum_nonneg (fun i _ => mul_nonneg (abs_nonneg _) (hp i))))
    (lt_min hZl hZk) (min_le_left _ _))

def IsProbability (p : I → ℝ) : Prop := (∀ i, 0 ≤ p i) ∧ mass p = 1

theorem posterior_probability (p l : I → ℝ) (hp : IsProbability p)
    (hl : ∀ i, 0 ≤ l i) (hz : 0 < evidence p l) : IsProbability (update p l) :=
  ⟨posterior_nonnegative p l hp.1 hl hz, posterior_mass p l hz.ne'⟩

theorem prediction_probability (K : Matrix I I ℝ) (hK : ∀ i j, 0 ≤ K i j)
    (hs : ∀ j, ∑ i, K i j=1) (p : I → ℝ) (hp : IsProbability p) :
    IsProbability (K.mulVec p) := by
  constructor
  · intro i
    exact Finset.sum_nonneg (fun j _ => mul_nonneg (hK i j) (hp.1 j))
  · dsimp [mass, Matrix.mulVec, dotProduct]
    rw [Finset.sum_comm]
    simp only [← Finset.sum_mul, hs, one_mul]
    exact hp.2

theorem prediction_update_probability (K : Matrix I I ℝ) (hK : ∀ i j, 0 ≤ K i j)
    (hs : ∀ j, ∑ i, K i j=1) (p l : I → ℝ) (hp : IsProbability p)
    (hl : ∀ i, 0 ≤ l i) (hz : 0 < evidence (K.mulVec p) l) :
    IsProbability (update (K.mulVec p) l) :=
  posterior_probability _ _ (prediction_probability K hK hs p hp) hl hz

end KomorebiPaperVI.FiniteBayes
