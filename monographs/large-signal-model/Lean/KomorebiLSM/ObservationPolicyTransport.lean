import KomorebiLSM.ObservationEquivalence

set_option autoImplicit false
namespace Komorebi.LSM.ObservationEquivalence
open MeasureTheory ContinuousInstrument ContinuousRecords
noncomputable section
universe u
variable {Y Z : Type u} [MeasurableSpace Y] [MeasurableSpace Z]
variable {μ : Measure Y} {ν : Measure Z}

theorem history_roundtrip (e : Y ≃ᵐ Z) (N : ℕ) (h : History Y N) :
    historyEquiv e.symm N (historyEquiv e N h)=h := by
  induction N with
  | zero => cases h; rfl
  | succ N ih => exact Prod.ext (ih h.1) (e.symm_apply_apply h.2)

theorem history_roundtrip_reverse (e : Y ≃ᵐ Z) (N : ℕ) (h : History Z N) :
    historyEquiv e N (historyEquiv e.symm N h)=h := by
  exact history_roundtrip e.symm N h

variable {A : Type*} [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]

omit [Fintype A] [MeasurableSingletonClass A] in
@[simp] theorem stepEquiv_symm (e : Y ≃ᵐ Z) :
    stepEquiv (A := A) e.symm=(stepEquiv (A := A) e).symm := rfl

omit [MeasurableSingletonClass A] in
theorem policy_ext (π ρ : Policy (A := A) (Y := Y))
    (h : ∀ N x a,π.probability N x a=ρ.probability N x a) : π=ρ := by
  rcases π with ⟨p,hp,sp⟩
  rcases ρ with ⟨q,hq,sq⟩
  have he : p=q := by funext N x a; exact h N x a
  subst q
  rfl

omit [MeasurableSingletonClass A] in
/-- Inverse history recoding restores the same adaptive policy exactly. -/
theorem pullPolicy_roundtrip (e : Y ≃ᵐ Z) (π : Policy (A := A) (Y := Z)) :
    pullPolicy e.symm (pullPolicy e π)=π := by
  apply policy_ext
  intro N h a
  change π.probability N
    (historyEquiv (stepEquiv (A := A) e) N (historyEquiv (stepEquiv (A := A) e.symm) N h)) a=π.probability N h a
  rw [stepEquiv_symm,history_roundtrip_reverse]

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable {C : BaseNorm.ProbabilityCone E}

omit [MeasurableSingletonClass A] in
/-- A source fit and a target truth can be compared under exactly the same target history policy. -/
theorem forward_recordLaw (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν) [IsFiniteMeasure ν]
    (D : DensityInstrument (A := A) C μ) (π : Policy (A := A) (Y := Z)) (z : E) (N : ℕ) :
    (recordLaw D (pullPolicy e π) z N).map (historyEquiv (stepEquiv (A := A) e) N)=
      recordLaw (pullInstrument e.symm (he.symm e) D) π z N := by
  have h := recordLaw_map e.symm (he.symm e) D (pullPolicy e π) z N
  rw [pullPolicy_roundtrip] at h
  have hm := congrArg (fun ρ : Measure (History (A × Y) N) =>
    ρ.map (historyEquiv (stepEquiv (A := A) e) N)) h
  rw [Measure.map_map (historyEquiv _ N).measurable (historyEquiv _ N).measurable] at hm
  have hc : (historyEquiv (stepEquiv (A := A) e) N) ∘ (historyEquiv (stepEquiv (A := A) e.symm) N)=id := by
    funext h
    rw [stepEquiv_symm]
    exact history_roundtrip_reverse _ N h
  rw [hc,Measure.map_id] at hm
  exact hm.symm

end
end Komorebi.LSM.ObservationEquivalence
