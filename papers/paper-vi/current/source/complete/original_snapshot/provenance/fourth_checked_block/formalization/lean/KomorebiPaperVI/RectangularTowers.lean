import KomorebiPaperVI.RectangularSemigroup
import Mathlib.Analysis.Normed.Group.FunctionSeries

/-! Author: Komorebi P. Generator criteria for varying-Hilbert-space refinement towers.
Summability across different operator spaces means summability of the real norms. -/
namespace KomorebiPaperVI.RectangularTowers
open Set
open scoped NNReal
open KomorebiPaperVI.RectangularFractional KomorebiPaperVI.RectangularSemigroup
set_option backward.isDefEq.respectTransparency false
variable {H : ℕ → Type*} [∀ n,NormedAddCommGroup (H n)] [∀ n,InnerProductSpace ℂ (H n)]
    [∀ n,CompleteSpace (H n)]

noncomputable def generatorNorm (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n) (n : ℕ) : ℝ :=
  ‖defect (A (n+1)) (A n) (C n)‖
noncomputable def fractionalNorm (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (p : ℝ≥0) (n : ℕ) : ℝ := ‖fractionalDefect (A (n+1)) (A n) (C n) p‖
noncomputable def timeNorm (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (p : ℝ≥0) (t : ℝ) (n : ℕ) : ℝ := ‖timeDefect (A (n+1)) (A n) (C n) p t‖

theorem holder_constant_positive (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1) :
    0 < FractionalNormBounds.holderConstant p := by
  unfold FractionalNormBounds.holderConstant
  exact div_pos (mul_pos (Real.rpow_pos_of_pos (by norm_num) _)
    (BetaNormalization.sine_factor_positive p hp)) (mul_pos hp.1 (sub_pos.mpr hp.2))

theorem holder_majorant (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (M : ℝ) (hC : ∀ n,‖C n‖ ≤ M) (n : ℕ) :
    fractionalNorm A C p n ≤ FractionalNormBounds.holderConstant p*M^(1-(p:ℝ))*(generatorNorm A C n)^(p:ℝ) := by
  calc
    _ ≤ FractionalNormBounds.holderConstant p*‖C n‖^(1-(p:ℝ))*(generatorNorm A C n)^(p:ℝ) :=
      holder_estimate p hp (A (n+1)) (A n) (C n) (hA _) (hA _)
    _ ≤ _ := by
      have hk := (holder_constant_positive p hp).le
      have hg : 0 ≤ (generatorNorm A C n)^(p:ℝ) := Real.rpow_nonneg (norm_nonneg _) _
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left
        (Real.rpow_le_rpow (norm_nonneg _) (hC n) (sub_nonneg.mpr hp.2.le)) hk) hg

theorem generator_holder_summable (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (M : ℝ) (hC : ∀ n,‖C n‖ ≤ M)
    (hs : Summable (fun n => (generatorNorm A C n)^(p:ℝ))) : Summable (fractionalNorm A C p) := by
  apply (hs.mul_left (FractionalNormBounds.holderConstant p*M^(1-(p:ℝ)))).of_norm_bounded
  intro n
  rw [Real.norm_of_nonneg (show 0 ≤ fractionalNorm A C p n from norm_nonneg _)]
  exact holder_majorant A C hA p hp M hC n

theorem generator_gap_summable (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (m : ℝ) (hm : 0 < m) (hgap : ∀ n,algebraMap ℝ (H n →L[ℂ] H n) m ≤ A n)
    (hs : Summable (generatorNorm A C)) : Summable (fractionalNorm A C p) := by
  apply (hs.mul_left ((p:ℝ)*m^((p:ℝ)-1))).of_norm_bounded
  intro n
  rw [Real.norm_of_nonneg (show 0 ≤ fractionalNorm A C p n from norm_nonneg _)]
  exact common_gap_estimate p hp m hm (A (n+1)) (A n) (C n) (hA _) (hA _) (hgap _) (hgap _)

theorem bounded_time_majorant (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : 0 < p) (T t : ℝ) (ht : t∈Icc 0 T) (n : ℕ) :
    timeNorm A C p t n ≤ T*fractionalNorm A C p n :=
  (fractional_contraction_bound (A (n+1)) (A n) (C n) (hA _) (hA _) p hp t ht.1).trans
    (mul_le_mul_of_nonneg_right ht.2 (norm_nonneg _))

theorem time_norms_summable (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : 0 < p) (t : ℝ) (ht : 0 ≤ t)
    (hs : Summable (fractionalNorm A C p)) : Summable (timeNorm A C p t) := by
  apply (hs.mul_left t).of_norm_bounded
  intro n
  rw [Real.norm_of_nonneg (show 0 ≤ timeNorm A C p t n from norm_nonneg _)]
  exact bounded_time_majorant A C hA p hp t t ⟨ht,le_rfl⟩ n

theorem bounded_time_uniform_convergence (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : 0 < p) (T : ℝ)
    (hs : Summable (fractionalNorm A C p)) :
    TendstoUniformlyOn (fun N t => ∑ n ∈ Finset.range N,timeNorm A C p t n)
      (fun t => ∑' n,timeNorm A C p t n) Filter.atTop (Icc 0 T) := by
  apply tendstoUniformlyOn_tsum_nat (hs.mul_left T)
  intro n t ht
  rw [Real.norm_of_nonneg (show 0 ≤ timeNorm A C p t n from norm_nonneg _)]
  exact bounded_time_majorant A C hA p hp T t ht n

theorem holder_tower (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (M : ℝ) (hC : ∀ n,‖C n‖ ≤ M) (hs : Summable (fun n => (generatorNorm A C n)^(p:ℝ))) :
    Summable (fractionalNorm A C p) ∧
    (∀ t,0 ≤ t → Summable (timeNorm A C p t)) ∧
    (∀ T,TendstoUniformlyOn (fun N t => ∑ n ∈ Finset.range N,timeNorm A C p t n)
      (fun t => ∑' n,timeNorm A C p t n) Filter.atTop (Icc 0 T)) := by
  have h := generator_holder_summable A C hA p hp M hC hs
  exact ⟨h,fun t ht => time_norms_summable A C hA p hp.1 t ht h,
    fun T => bounded_time_uniform_convergence A C hA p hp.1 T h⟩

theorem gap_tower (A : ∀ n,H n →L[ℂ] H n) (C : ∀ n,H (n+1) →L[ℂ] H n)
    (hA : ∀ n,0 ≤ A n) (p : ℝ≥0) (hp : (p:ℝ)∈Ioo 0 1)
    (m : ℝ) (hm : 0 < m) (hgap : ∀ n,algebraMap ℝ (H n →L[ℂ] H n) m ≤ A n)
    (hs : Summable (generatorNorm A C)) :
    Summable (fractionalNorm A C p) ∧
    (∀ t,0 ≤ t → Summable (timeNorm A C p t)) ∧
    (∀ T,TendstoUniformlyOn (fun N t => ∑ n ∈ Finset.range N,timeNorm A C p t n)
      (fun t => ∑' n,timeNorm A C p t n) Filter.atTop (Icc 0 T)) := by
  have h := generator_gap_summable A C hA p hp m hm hgap hs
  exact ⟨h,fun t ht => time_norms_summable A C hA p hp.1 t ht h,
    fun T => bounded_time_uniform_convergence A C hA p hp.1 T h⟩

end KomorebiPaperVI.RectangularTowers
