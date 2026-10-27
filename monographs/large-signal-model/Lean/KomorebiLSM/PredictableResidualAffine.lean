import KomorebiLSM.PredictableResidual
import Mathlib.MeasureTheory.Function.ConditionalExpectation.Basic

/-! Exact interval-affine transport of actual conditional residuals on
arbitrary probability spaces. Countability is used only to put all transport
identities on one common full-measure event. -/
set_option autoImplicit false
namespace Komorebi.LSM.PredictableResidualAffine
open MeasureTheory
open scoped BigOperators
variable {Ω J : Type*} [mΩ : MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- Conditional expectation commutes with every real affine map, including
zero scale, on an arbitrary probability sample space. -/
theorem condExp_affine_ae {m : MeasurableSpace Ω} (hm : m≤mΩ)
    (X : Ω → ℝ) (hX : Integrable X μ) (a c : ℝ) :
    (μ[fun ω => a+c*X ω | m])=ᵐ[μ] (fun ω => a+c*(μ[X | m]) ω) := by
  have h := ContinuousLinearMap.comp_condExp_add_const_comm hm hX
    (c • ContinuousLinearMap.id ℝ ℝ) a
  simpa only [smul_apply,ContinuousLinearMap.id_apply,smul_eq_mul,add_comm] using h.symm

omit [IsProbabilityMeasure μ] in
/-- A.e. equality of the actual observations transports their actual centered
sums, since conditional expectation respects a.e. equality. -/
theorem centeredSum_congr_ae (ℱ : Filtration ℕ mΩ) (X Y : ℕ → Ω → ℝ)
    (hXY : ∀ i,X i=ᵐ[μ] Y i) (n : ℕ) :
    PredictableResidual.centeredSum (μ:=μ) ℱ X n=ᵐ[μ]
      PredictableResidual.centeredSum (μ:=μ) ℱ Y n := by
  have hce : ∀ᵐ ω∂μ,∀ i,(μ[X i | ℱ i]) ω=(μ[Y i | ℱ i]) ω :=
    ae_all_iff.mpr (fun i => condExp_congr_ae (hXY i))
  have hobs : ∀ᵐ ω∂μ,∀ i,X i ω=Y i ω := ae_all_iff.mpr hXY
  filter_upwards [hce,hobs] with ω hce hobs
  apply Finset.sum_congr rfl
  intro i _
  rw [hobs i,hce i]

/-- Every finite actual affine centered sum is exactly scaled a.e.; the
shift cancels inside the true conditional expectation. -/
theorem centeredSum_affine_ae (ℱ : Filtration ℕ mΩ) (X : ℕ → Ω → ℝ)
    (hX : ∀ i,Integrable (X i) μ) (a c : ℝ) (n : ℕ) :
    PredictableResidual.centeredSum (μ:=μ) ℱ (fun i ω => a+c*X i ω) n=ᵐ[μ]
      (fun ω => c*PredictableResidual.centeredSum (μ:=μ) ℱ X n ω) := by
  have hce : ∀ᵐ ω∂μ,∀ i,
      (μ[fun ω => a+c*X i ω | ℱ i]) ω=a+c*(μ[X i | ℱ i]) ω :=
    ae_all_iff.mpr (fun i => condExp_affine_ae (ℱ.le i) (X i) (hX i) a c)
  filter_upwards [hce] with ω hce
  simp only [PredictableResidual.centeredSum]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  rw [hce i]
  ring

/-- Normalize every declared interval. The degenerate interval uses zero,
so zero width is covered without an invalid division. -/
noncomputable def normalizedProcess (lower width : J → ℝ) (X : J → ℕ → Ω → ℝ)
    (j : J) (i : ℕ) (ω : Ω) : ℝ := by
  classical
  exact if width j=0 then 0 else (X j i ω-lower j)/width j

theorem normalized_adapted (ℱ : Filtration ℕ mΩ)
    (lower width : J → ℝ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i)) :
    ∀ j i,Measurable[ℱ (i+1)] (normalizedProcess lower width X j i) := by
  intro j i
  by_cases hw : width j=0
  · have he : normalizedProcess lower width X j i=(fun _ : Ω => (0:ℝ)) := by
      funext ω
      exact ite_eq_left hw
    rw [he]
    exact measurable_const
  · have he : normalizedProcess lower width X j i=(fun ω : Ω => (X j i ω-lower j)/width j) := by
      funext ω
      exact ite_eq_right hw
    rw [he]
    exact ((hX j i).sub_const (lower j)).div_const (width j)

omit [IsProbabilityMeasure μ] in
theorem normalized_mem_unit_ae (lower width : J → ℝ) (X : J → ℕ → Ω → ℝ)
    (hw : ∀ j,0≤width j)
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j)) :
    ∀ j i,∀ᵐ ω∂μ,normalizedProcess lower width X j i ω∈Set.Icc (0:ℝ) 1 := by
  intro j i
  by_cases hj : width j=0
  · simp only [normalizedProcess,ite_eq_left hj,Set.mem_Icc]
    exact Filter.Eventually.of_forall (fun _ => ⟨le_rfl,zero_le_one⟩)
  · have hp : 0<width j := lt_of_le_of_ne (hw j) (Ne.symm hj)
    filter_upwards [hb j i] with ω hω
    simp only [normalizedProcess,ite_eq_right hj,Set.mem_Icc]
    exact ⟨div_nonneg (sub_nonneg.mpr hω.1) hp.le,
      (div_le_iff₀ hp).mpr (by linarith [hω.2])⟩

omit [IsProbabilityMeasure μ] in
/-- The original observation equals its normalized affine representation,
including zero-width intervals, rather than merely sharing a range bound. -/
theorem affine_normalized_ae (lower width : J → ℝ) (X : J → ℕ → Ω → ℝ)
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j)) :
    ∀ j i,X j i=ᵐ[μ] (fun ω => lower j+width j*normalizedProcess lower width X j i ω) := by
  intro j i
  by_cases hj : width j=0
  · filter_upwards [hb j i] with ω hω
    simp only [normalizedProcess,hj,zero_mul,add_zero]
    linarith [hω.1,hω.2]
  · apply Filter.Eventually.of_forall
    intro ω
    simp only [normalizedProcess,ite_eq_right hj]
    field_simp [hj]
    ring

/-- All actual interval-width centered sums and their unit-range versions
share one common full-measure transport event. -/
theorem centeredSum_normalized_ae [Countable J] (ℱ : Filtration ℕ mΩ)
    (lower width : J → ℝ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i)) (hw : ∀ j,0≤width j)
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j)) :
    ∀ᵐ ω∂μ,∀ j n,PredictableResidual.centeredSum (μ:=μ) ℱ (X j) n ω=
      width j*PredictableResidual.centeredSum (μ:=μ) ℱ
        (normalizedProcess lower width X j) n ω := by
  have hunit := normalized_mem_unit_ae lower width X hw hb
  have hadapt := normalized_adapted ℱ lower width X hX
  have hi (j : J) (i : ℕ) : Integrable (normalizedProcess lower width X j i) μ :=
    Integrable.of_mem_Icc (0:ℝ) 1 ((hadapt j i).mono (ℱ.le (i+1)) le_rfl).aemeasurable
      (hunit j i)
  have hobs := affine_normalized_ae lower width X hb
  apply ae_all_iff.mpr
  intro j
  apply ae_all_iff.mpr
  intro n
  exact (centeredSum_congr_ae ℱ (X j)
    (fun i ω => lower j+width j*normalizedProcess lower width X j i ω) (hobs j) n).trans
      (centeredSum_affine_ae ℱ (normalizedProcess lower width X j) (hi j) (lower j) (width j) n)

/-- On one full-measure event, every simultaneous positive-time bound for
the normalized process implies the width-scaled bound for the actual process. -/
theorem normalized_bound_transfer_ae [Countable J] (ℱ : Filtration ℕ mΩ)
    (lower width : J → ℝ) (X : J → ℕ → Ω → ℝ)
    (hX : ∀ j i,Measurable[ℱ (i+1)] (X j i)) (hw : ∀ j,0≤width j)
    (hb : ∀ j i,∀ᵐ ω∂μ,X j i ω∈Set.Icc (lower j) (lower j+width j))
    (boundary : J → ℕ → ℝ) :
    ∀ᵐ ω∂μ,(∀ j n,|PredictableResidual.centeredSum (μ:=μ) ℱ
      (normalizedProcess lower width X j) (n+1) ω|≤boundary j n) →
      ∀ j n,|PredictableResidual.centeredSum (μ:=μ) ℱ (X j) (n+1) ω|≤width j*boundary j n := by
  filter_upwards [centeredSum_normalized_ae ℱ lower width X hX hw hb] with ω he hall j n
  rw [he j (n+1),abs_mul,abs_of_nonneg (hw j)]
  exact mul_le_mul_of_nonneg_left (hall j n) (hw j)

end Komorebi.LSM.PredictableResidualAffine
