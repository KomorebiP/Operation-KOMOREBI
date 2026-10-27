import KomorebiPaperVI.BetaNormalization
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic

/-! Author: Komorebi P. Exact scalar integrals for the split fractional-defect bound. -/
namespace KomorebiPaperVI.FractionalScalarBounds
open Set MeasureTheory Real

theorem low_integral (p r : ℝ) (hp : 0 < p) (hr : 0 < r) :
    (∫ t in Ioc 0 r,t^(p-1))=r^p/p := by
  rw [← intervalIntegral.integral_of_le hr.le,
    integral_rpow (Or.inl (by linarith : -1 < p-1))]
  simp [hp.ne']

theorem high_integral (p r : ℝ) (hp : p < 1) (hr : 0 < r) :
    (∫ t in Ioi r,t^(p-2))=r^(p-1)/(1-p) := by
  rw [integral_Ioi_rpow_of_lt (by linarith : p-2 < -1) hr]
  have he : p-2+1=p-1 := by ring
  rw [he,show p-1= -(1-p) by ring,div_neg,neg_div,neg_neg]

theorem split_domain (r : ℝ) (hr : 0 ≤ r) : Ioi (0:ℝ)=Ioc 0 r∪Ioi r := by
  ext t
  simp only [mem_Ioi,mem_union,mem_Ioc]
  constructor
  · intro ht
    by_cases h : t ≤ r
    · exact Or.inl ⟨ht,h⟩
    · exact Or.inr (lt_of_not_ge h)
  · rintro (h|h)
    · exact h.1
    · exact hr.trans_lt h

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
theorem split_norm_bound (f : ℝ → E) (p c d r : ℝ) (hp : p∈Ioo 0 1) (hr : 0 < r)
    (hf : IntegrableOn f (Ioi 0))
    (hlow : ∀ t,0 < t → ‖f t‖ ≤ c*t^(p-1))
    (hhigh : ∀ t,0 < t → ‖f t‖ ≤ d*t^(p-2)) :
    ‖∫ t in Ioi 0,f t‖ ≤ c*r^p/p+d*r^(p-1)/(1-p) := by
  have hf1 := hf.mono_set (Ioc_subset_Ioi_self : Ioc (0:ℝ) r ⊆ Ioi 0)
  have hf2 := hf.mono_set (Ioi_subset_Ioi hr.le)
  have hg1 : IntegrableOn (fun t : ℝ => c*t^(p-1)) (Ioc 0 r) := by
    exact (intervalIntegral.intervalIntegrable_rpow' (by linarith [hp.1] : -1 < p-1)).1.const_mul c
  have hg2 := (integrableOn_Ioi_rpow_of_lt (by linarith [hp.2] : p-2 < -1) hr).const_mul d
  have hdis : Disjoint (Ioc (0:ℝ) r) (Ioi r) := by
    apply disjoint_left.mpr
    intro t ht hu
    exact (not_lt_of_ge ht.2) hu
  rw [split_domain r hr.le,setIntegral_union hdis measurableSet_Ioi hf1 hf2]
  calc
    _ ≤ ‖∫ t in Ioc 0 r,f t‖+‖∫ t in Ioi r,f t‖ := norm_add_le _ _
    _ ≤ (∫ t in Ioc 0 r,c*t^(p-1))+(∫ t in Ioi r,d*t^(p-2)) := by
      apply add_le_add
      · exact (norm_integral_le_integral_norm _).trans (setIntegral_mono_on hf1.norm hg1 measurableSet_Ioc (fun t ht => hlow t ht.1))
      · exact (norm_integral_le_integral_norm _).trans (setIntegral_mono_on hf2.norm hg2 measurableSet_Ioi (fun t ht => hhigh t (hr.trans ht)))
    _ = _ := by rw [integral_const_mul,integral_const_mul,low_integral p r hp.1 hr,high_integral p r hp.2 hr]; ring

theorem optimize_split (p c d : ℝ) (hp : p∈Ioo 0 1) (hc : 0 < c) (hd : 0 < d) :
    c*(d/c)^p/p+d*(d/c)^(p-1)/(1-p)=c^(1-p)*d^p/(p*(1-p)) := by
  rw [Real.rpow_sub (div_pos hd hc),Real.rpow_one,Real.div_rpow hd.le hc.le,
    Real.rpow_sub hc,Real.rpow_one]
  have hcPow : c^p ≠ 0 := (Real.rpow_pos_of_pos hc p).ne'
  field_simp [hc.ne',hd.ne',hp.1.ne',(sub_pos.mpr hp.2).ne',hcPow]
  ring

end KomorebiPaperVI.FractionalScalarBounds
