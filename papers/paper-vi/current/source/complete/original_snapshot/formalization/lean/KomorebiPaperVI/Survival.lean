import KomorebiPaperVI.MarkovSemigroup
import KomorebiPaperVI.Semigroups
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.MeasureTheory.Integral.IntegralEqImproper
import Mathlib.Topology.Order.MonotoneConvergence

/-! Author: Komorebi P. Literal finite subgenerator survival, including defective exit mass. -/
namespace KomorebiPaperVI.Survival
open scoped BigOperators Matrix.Norms.Operator Topology
open Set Filter MeasureTheory
set_option backward.isDefEq.respectTransparency false
variable {I : Type*} [Fintype I] [DecidableEq I]

noncomputable def state (A : Matrix I I ℝ) (p : I → ℝ) (t : ℝ) : I → ℝ :=
  (NormedSpace.exp (t • A)).mulVec p
noncomputable def survival (A : Matrix I I ℝ) (p : I → ℝ) (t : ℝ) : ℝ := ∑ i, state A p t i
noncomputable def exitRate (A : Matrix I I ℝ) (j : I) : ℝ := -∑ i, A i j
noncomputable def density (A : Matrix I I ℝ) (p : I → ℝ) (t : ℝ) : ℝ :=
  ∑ j, exitRate A j*state A p t j
noncomputable def hazard (A : Matrix I I ℝ) (p : I → ℝ) (t : ℝ) : ℝ :=
  density A p t/survival A p t

theorem survival_zero (A : Matrix I I ℝ) (p : I → ℝ) : survival A p 0=∑ i,p i := by
  simp [survival,state]

theorem state_nonnegative (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (p : I → ℝ) (hp : ∀ i,0 ≤ p i) (t : ℝ) (ht : 0 ≤ t) (i : I) : 0 ≤ state A p t i :=
  Finset.sum_nonneg (fun j _ => mul_nonneg (MarkovSemigroup.markov_nonnegative A hA t ht i j) (hp j))

theorem survival_positive (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (p : I → ℝ) (hp : ∀ i,0 ≤ p i) (hs : ∑ i,p i=1) (t : ℝ) (ht : 0 ≤ t) :
    0 < survival A p t := by
  have hn := state_nonnegative A hA p hp t ht
  have hnon : 0 ≤ survival A p t := Finset.sum_nonneg (fun i _ => hn i)
  apply lt_of_le_of_ne hnon
  intro he
  have hz : state A p t=0 := by
    funext i
    have hle := Finset.single_le_sum (fun j _ => hn j) (Finset.mem_univ i)
    change state A p t i=0
    change state A p t i ≤ survival A p t at hle
    linarith [hn i]
  have hpz : p=0 := (Matrix.mulVec_injective_of_isUnit (Matrix.isUnit_exp (t • A)))
    (by simpa [state] using hz)
  rw [hpz] at hs
  simp at hs

theorem density_nonnegative (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (hc : ∀ j,∑ i,A i j ≤ 0) (p : I → ℝ) (hp : ∀ i,0 ≤ p i)
    (t : ℝ) (ht : 0 ≤ t) : 0 ≤ density A p t :=
  Finset.sum_nonneg (fun j _ => mul_nonneg (neg_nonneg.mpr (hc j))
    (state_nonnegative A hA p hp t ht j))

theorem survival_derivative (A : Matrix I I ℝ) (p : I → ℝ) (t : ℝ) :
    HasDerivAt (survival A p) (-density A p t) t := by
  have he := Semigroups.transfer_derivative_left A t
  have hij (i j : I) : HasDerivAt (fun u => NormedSpace.exp (u • A) i j)
      ((A*NormedSpace.exp (t • A)) i j) t := by
    exact hasDerivAt_pi.mp (hasDerivAt_pi.mp he i) j
  have h := HasDerivAt.fun_sum (fun i (_ : i∈Finset.univ) =>
    HasDerivAt.fun_sum (fun j (_ : j∈Finset.univ) => (hij i j).mul_const (p j)))
  change HasDerivAt (survival A p) (∑ i,(A*NormedSpace.exp (t • A)).mulVec p i) t at h
  rw [← Matrix.mulVec_mulVec] at h
  have hd : (∑ i,A.mulVec (state A p t) i)=-density A p t := by
    simp [density,exitRate,Matrix.mulVec,dotProduct,Finset.sum_comm,← Finset.sum_mul]
  change HasDerivAt (survival A p) (∑ i,A.mulVec (state A p t) i) t at h
  rwa [hd] at h

theorem survival_antitone (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (hc : ∀ j,∑ i,A i j ≤ 0) (p : I → ℝ) (hp : ∀ i,0 ≤ p i) :
    AntitoneOn (survival A p) (Ici 0) := by
  have hd : Differentiable ℝ (survival A p) := fun t => (survival_derivative A p t).differentiableAt
  apply antitoneOn_of_deriv_nonpos (convex_Ici 0) hd.continuous.continuousOn hd.differentiableOn
  intro t ht
  rw [(survival_derivative A p t).deriv]
  exact neg_nonpos.mpr (density_nonnegative A hA hc p hp t (interior_subset ht))

theorem density_continuous (A : Matrix I I ℝ) (p : I → ℝ) : Continuous (density A p) := by
  unfold density state
  fun_prop

theorem survival_hazard (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (p : I → ℝ) (hp : ∀ i,0 ≤ p i) (hs : ∑ i,p i=1) (t : ℝ) (ht : 0 ≤ t) :
    survival A p t=Real.exp (-∫ r in 0..t,hazard A p r) := by
  have hd : ∀ r∈Icc 0 t, HasDerivAt (fun u => Real.log (survival A p u)) (-hazard A p r) r := by
    intro r hr
    simpa [hazard,neg_div] using (survival_derivative A p r).log
      (survival_positive A hA p hp hs r hr.1).ne'
  have hscont : Continuous (survival A p) :=
    (show Differentiable ℝ (survival A p) from fun r => (survival_derivative A p r).differentiableAt).continuous
  have hhcont : ContinuousOn (hazard A p) (Icc 0 t) :=
    (density_continuous A p).continuousOn.div hscont.continuousOn
      (fun r hr => (survival_positive A hA p hp hs r hr.1).ne')
  have hi := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (by simpa [uIcc_of_le ht] using hd)
    (hhcont.neg.intervalIntegrable_of_Icc ht)
  simp only [Pi.neg_apply,intervalIntegral.integral_neg,survival_zero,hs,Real.log_one,sub_zero] at hi
  rw [hi,Real.exp_log (survival_positive A hA p hp hs t ht)]

theorem survival_has_limit (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (hc : ∀ j,∑ i,A i j ≤ 0) (p : I → ℝ) (hp : ∀ i,0 ≤ p i) :
    ∃ l,0 ≤ l ∧ Tendsto (survival A p) atTop (𝓝 l) := by
  let f : ℝ → ℝ := fun t => survival A p (max t 0)
  have hn (t : ℝ) : 0 ≤ f t := Finset.sum_nonneg
    (fun i _ => state_nonnegative A hA p hp _ (le_max_right _ _) i)
  have ha : Antitone f := fun s t hst => survival_antitone A hA hc p hp
    (show max s 0∈Ici (0:ℝ) from le_max_right s 0)
    (show max t 0∈Ici (0:ℝ) from le_max_right t 0) (max_le_max_right 0 hst)
  have hb : BddBelow (range f) := ⟨0,by rintro _ ⟨t,rfl⟩; exact hn t⟩
  refine ⟨⨅ t,f t,le_ciInf hn,?_⟩
  apply (tendsto_atTop_ciInf ha hb).congr'
  filter_upwards [eventually_ge_atTop (0:ℝ)] with t ht
  simp [f,max_eq_left ht]

theorem defective_density_mass (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (hc : ∀ j,∑ i,A i j ≤ 0) (p : I → ℝ) (hp : ∀ i,0 ≤ p i) (hs : ∑ i,p i=1) :
    ∃ l,0 ≤ l ∧ Tendsto (survival A p) atTop (𝓝 l) ∧
      IntegrableOn (density A p) (Ioi 0) ∧ (∫ t in Ioi 0,density A p t)=1-l := by
  obtain ⟨l,hl,ht⟩ := survival_has_limit A hA hc p hp
  have hd := fun t (_ : t∈Ici (0:ℝ)) => survival_derivative A p t
  have hn := fun t (ht : t∈Ioi (0:ℝ)) =>
    neg_nonpos.mpr (density_nonnegative A hA hc p hp t ht.le)
  have hi := integrableOn_Ioi_deriv_of_nonpos' hd hn ht
  have he := integral_Ioi_of_hasDerivAt_of_nonpos' hd hn ht
  refine ⟨l,hl,ht,integrable_neg_iff.mp hi,?_⟩
  simp only [integral_neg,survival_zero,hs] at he
  linarith

theorem eventual_absorption_density (A : Matrix I I ℝ) (hA : ∀ i j, i≠j → 0 ≤ A i j)
    (hc : ∀ j,∑ i,A i j ≤ 0) (p : I → ℝ) (hp : ∀ i,0 ≤ p i) (hs : ∑ i,p i=1)
    (habs : Tendsto (survival A p) atTop (𝓝 0)) :
    IntegrableOn (density A p) (Ioi 0) ∧ (∫ t in Ioi 0,density A p t)=1 := by
  obtain ⟨l,_,hl,hi,hm⟩ := defective_density_mass A hA hc p hp hs
  have he : l=0 := tendsto_nhds_unique hl habs
  exact ⟨hi,by simpa [he] using hm⟩

end KomorebiPaperVI.Survival
