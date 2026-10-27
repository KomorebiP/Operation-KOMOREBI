import KomorebiVerification.PaperII.TypedLinearDefects
import Mathlib.Analysis.Normed.Algebra.GelfandFormula
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseAnalyticContour
open scoped BigOperators Topology
open MeasureTheory Set
open TypedLinearDefects
universe u v

/-- A finite family of oriented closed absolutely continuous curves, represented
by their actual integrable velocities. Repeated entries count multiplicity.
This is an analytic representation, not an assertion that all rectifiable
parameterizations already have this form. -/
structure IntegralCycle where
  count : ℕ
  base : Fin count → ℂ
  velocity : Fin count → ℝ → ℂ
  velocity_integrable : ∀ i, IntervalIntegrable (velocity i) volume 0 1
  closed : ∀ i, (∫ s : ℝ in (0:ℝ)..1, velocity i s) = 0

namespace IntegralCycle

def curve (Γ : IntegralCycle) (i : Fin Γ.count) (s : ℝ) : ℂ :=
  Γ.base i + ∫ r : ℝ in 0..s, Γ.velocity i r

def trace (Γ : IntegralCycle) : Set ℂ :=
  {z | ∃ i s, s ∈ uIcc (0:ℝ) 1 ∧ Γ.curve i s = z}

/-- Velocity length counts each curve occurrence, hence multiplicity. Its
identification with geometric rectifiable length is a separate bridge. -/
def length (Γ : IntegralCycle) : ℝ :=
  ∑ i : Fin Γ.count, ∫ s : ℝ in (0:ℝ)..1, ‖Γ.velocity i s‖

@[simp] theorem curve_zero (Γ : IntegralCycle) (i : Fin Γ.count) :
    Γ.curve i 0 = Γ.base i := by simp [curve]

@[simp] theorem curve_one (Γ : IntegralCycle) (i : Fin Γ.count) :
    Γ.curve i 1 = Γ.base i := by simp [curve, Γ.closed]

theorem continuousOn_curve (Γ : IntegralCycle) (i : Fin Γ.count) :
    ContinuousOn (Γ.curve i) (uIcc (0:ℝ) 1) := by
  exact continuousOn_const.add
    (intervalIntegral.continuousOn_primitive_interval' (Γ.velocity_integrable i) left_mem_uIcc)

section Integral
variable {E : Type u} [NormedAddCommGroup E] [NormedSpace ℂ E]
variable [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]

/-- Actual Bochner line integral over the represented finite cycle. -/
def lineIntegral (Γ : IntegralCycle) (f : ℂ → E) : E :=
  ∑ i : Fin Γ.count, ∫ s : ℝ in (0:ℝ)..1, Γ.velocity i s • f (Γ.curve i s)

omit [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E] in
theorem integrable_lineIntegrand (Γ : IntegralCycle) {f : ℂ → E}
    (hf : ContinuousOn f Γ.trace) (i : Fin Γ.count) :
    IntervalIntegrable (fun s : ℝ => Γ.velocity i s • f (Γ.curve i s)) volume 0 1 := by
  apply (Γ.velocity_integrable i).smul_continuousOn
  exact hf.comp (Γ.continuousOn_curve i) (fun s hs => ⟨i,s,hs,rfl⟩)

/-- No scalar surrogate is used: bounded linear maps commute with the actual
Banach-valued cycle integral. -/
theorem lineIntegral_map {F : Type v} [NormedAddCommGroup F] [NormedSpace ℂ F]
    [NormedSpace ℝ F] [IsScalarTower ℝ ℂ F] [CompleteSpace F]
    (Γ : IntegralCycle) (L : E →L[ℂ] F) {f : ℂ → E} (hf : ContinuousOn f Γ.trace) :
    Γ.lineIntegral (fun z => L (f z)) = L (Γ.lineIntegral f) := by
  unfold lineIntegral
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro i hi
  simpa only [map_smul] using
    L.intervalIntegral_comp_comm (Γ.integrable_lineIntegrand hf i)

theorem lineIntegral_sub (Γ : IntegralCycle) {f g : ℂ → E}
    (hf : ContinuousOn f Γ.trace) (hg : ContinuousOn g Γ.trace) :
    Γ.lineIntegral (fun z => f z - g z) = Γ.lineIntegral f - Γ.lineIntegral g := by
  unfold lineIntegral
  simp_rw [smul_sub]
  rw [← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro i hi
  exact intervalIntegral.integral_sub (Γ.integrable_lineIntegrand hf i)
    (Γ.integrable_lineIntegrand hg i)

omit [IsScalarTower ℝ ℂ E] [CompleteSpace E] in
/-- The exact length-times-uniform-bound estimate for the actual integral. -/
theorem norm_lineIntegral_le (Γ : IntegralCycle) {f : ℂ → E} (M : ℝ)
    (hM : ∀ z ∈ Γ.trace, ‖f z‖ ≤ M) :
    ‖Γ.lineIntegral f‖ ≤ Γ.length * M := by
  unfold lineIntegral length
  refine (norm_sum_le _ _).trans ?_
  rw [Finset.sum_mul]
  apply Finset.sum_le_sum
  intro i hi
  calc
    _ ≤ ∫ s : ℝ in (0:ℝ)..1, ‖Γ.velocity i s‖ * M := by
      apply intervalIntegral.norm_integral_le_of_norm_le (by norm_num)
      · exact Filter.Eventually.of_forall fun s hs => by
          rw [norm_smul]
          exact mul_le_mul_of_nonneg_left
            (hM (Γ.curve i s) ⟨i,s,by simpa using Ioc_subset_Icc_self hs,rfl⟩)
            (norm_nonneg _)
      · exact (Γ.velocity_integrable i).norm.mul_const M
    _ = _ := intervalIntegral.integral_mul_const _ _
end Integral
end IntegralCycle

section Resolvent
variable {Ef : Type u} {Ec : Type v}
variable [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
variable [NormedSpace ℂ Ef] [NormedSpace ℂ Ec]
variable [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
variable [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
variable [CompleteSpace Ef] [CompleteSpace Ec]

/-- A chosen-cycle Dunford integral. This definition does not itself assert
independence of the admissible cycle. -/
def dunfordIntegral (Γ : IntegralCycle) (h : ℂ → ℂ)
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]
    (T : E →L[ℂ] E) : E →L[ℂ] E :=
  (2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
    Γ.lineIntegral (fun z => h z • resolvent T z)

/-- Actual spectrum resolvents satisfy the typed inverse-witness equations. -/
theorem resolvent_inverse_witnesses
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (T : E →L[ℂ] E) (z : ℂ) (hz : z ∈ resolventSet ℂ T) :
    (continuousScalarShift z T).comp (resolvent T z) = 1 ∧
      (resolvent T z).comp (continuousScalarShift z T) = 1 := by
  rw [spectrum.resolvent_eq hz]
  have hs : continuousScalarShift z T = (hz.unit : E →L[ℂ] E) := by
    simpa [continuousScalarShift, Algebra.algebraMap_eq_smul_one] using hz.unit_spec.symm
  rw [hs]
  constructor
  · exact hz.unit.mul_inv
  · exact hz.unit.inv_mul

omit [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
  [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
  [CompleteSpace Ef] [CompleteSpace Ec] in
/-- The pointwise sandwich uses actual spectrum resolvents. -/
theorem resolvent_defect_actual
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (z : ℂ) (hf : z ∈ resolventSet ℂ Tf) (hc : z ∈ resolventSet ℂ Tc) :
    C.comp (resolvent Tf z) - (resolvent Tc z).comp C =
      (resolvent Tc z).comp
        ((continuousDefect C Tf Tc).comp (resolvent Tf z)) := by
  simpa only [ContinuousLinearMap.comp_assoc] using
    continuous_scalarShift_resolvent_identity z C Tf (resolvent Tf z)
      Tc (resolvent Tc z)
      (resolvent_inverse_witnesses Tf z hf).1
      (resolvent_inverse_witnesses Tc z hc).2

/-- Actual resolvent continuity on the trace follows from differentiability
on its resolvent set. -/
theorem continuousOn_resolvent_trace
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] [CompleteSpace E]
    (Γ : IntegralCycle) (T : E →L[ℂ] E)
    (hT : Γ.trace ⊆ resolventSet ℂ T) :
    ContinuousOn (resolvent T) Γ.trace := by
  intro z hz
  exact (spectrum.hasDerivAt_resolvent_const_left (hT hz)).continuousAt.continuousWithinAt

/-- Integral defect for an actual finite absolutely continuous cycle. No
conclusion-valued functional-calculus certificate is a premise. -/
theorem dunfordIntegral_defect
    (Γ : IntegralCycle) (h : ℂ → ℂ) (hh : ContinuousOn h Γ.trace)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hf : Γ.trace ⊆ resolventSet ℂ Tf) (hc : Γ.trace ⊆ resolventSet ℂ Tc) :
    C.comp (dunfordIntegral Γ h Tf) - (dunfordIntegral Γ h Tc).comp C =
      (2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
        Γ.lineIntegral (fun z => h z •
          ((resolvent Tc z).comp
            ((continuousDefect C Tf Tc).comp (resolvent Tf z)))) := by
  let post : (Ef →L[ℂ] Ef) →L[ℂ] (Ef →L[ℂ] Ec) :=
    ContinuousLinearMap.compL ℂ Ef Ef Ec C
  let pre : (Ec →L[ℂ] Ec) →L[ℂ] (Ef →L[ℂ] Ec) :=
    (ContinuousLinearMap.compL ℂ Ef Ec Ec).flip C
  have hff := hh.smul (continuousOn_resolvent_trace Γ Tf hf)
  have hcc := hh.smul (continuousOn_resolvent_trace Γ Tc hc)
  have hp := Γ.lineIntegral_map post hff
  have hq := Γ.lineIntegral_map pre hcc
  have hdiff := Γ.lineIntegral_sub (post.continuous.comp_continuousOn hff)
    (pre.continuous.comp_continuousOn hcc)
  have hpoint : Γ.lineIntegral (fun z => post (h z • resolvent Tf z) -
      pre (h z • resolvent Tc z)) =
      Γ.lineIntegral (fun z => h z • ((resolvent Tc z).comp
        ((continuousDefect C Tf Tc).comp (resolvent Tf z)))) := by
    unfold IntegralCycle.lineIntegral
    apply Finset.sum_congr rfl
    intro i hi
    apply intervalIntegral.integral_congr
    intro s hs
    have hz : Γ.curve i s ∈ Γ.trace := ⟨i,s,hs,rfl⟩
    congr 1
    change h (Γ.curve i s) • (C.comp (resolvent Tf (Γ.curve i s))) -
      h (Γ.curve i s) • ((resolvent Tc (Γ.curve i s)).comp C) = _
    rw [← smul_sub, resolvent_defect_actual C Tf Tc _ (hf hz) (hc hz)]
  rw [← hpoint, hdiff, hp, hq]
  ext x
  simp [dunfordIntegral, post, pre, smul_sub]
end Resolvent
end Komorebi.PaperII.ReleaseAnalyticContour
