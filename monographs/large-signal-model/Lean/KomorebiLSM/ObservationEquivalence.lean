import KomorebiLSM.ContinuousRecords
import Mathlib.MeasureTheory.Integral.Lebesgue.Map

set_option autoImplicit false
namespace Komorebi.LSM.ObservationEquivalence
open MeasureTheory ContinuousInstrument ContinuousRecords
open scoped ENNReal
noncomputable section

universe u
variable {Y Z : Type u} [MeasurableSpace Y] [MeasurableSpace Z]
variable {μ : Measure Y} {ν : Measure Z}

/-- A measurable observation equivalence transports an actual density measure. -/
theorem map_withDensity (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν) (f : Z → ℝ≥0∞) :
    (μ.withDensity (fun y => f (e y))).map e = ν.withDensity f := by
  ext S hS
  rw [Measure.map_apply e.measurable hS,withDensity_apply _ (e.measurable hS),withDensity_apply _ hS]
  exact he.setLIntegral_comp_preimage_emb e.measurableEmbedding f S

/-- The equivalence is applied in chronological order to every coordinate of a history. -/
def historyEquiv (e : Y ≃ᵐ Z) : (N : ℕ) → History Y N ≃ᵐ History Z N
  | 0 => MeasurableEquiv.refl _
  | N+1 => (historyEquiv e N).prodCongr e

theorem historyEquiv_eq_mapHistory (e : Y ≃ᵐ Z) (N : ℕ) (h : History Y N) :
    historyEquiv e N h=mapHistory e N h := by
  induction N with
  | zero => cases h; rfl
  | succ N ih => exact Prod.ext (ih h.1) rfl

theorem history_preserving (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν) [IsFiniteMeasure μ] :
    (N : ℕ) → MeasurePreserving (historyEquiv e N) (reference μ N) (reference ν N)
  | 0 => by
    change MeasurePreserving (id : PUnit → PUnit) (Measure.dirac PUnit.unit) (Measure.dirac PUnit.unit)
    exact MeasurePreserving.id _
  | N+1 => (history_preserving e he N).prod he

variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable {C : BaseNorm.ProbabilityCone E}

/-- Pullback changes the actual operator density and derives all instrument fields. -/
def pullInstrument (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν)
    (D : DensityInstrument (A := A) C ν) : DensityInstrument (A := A) C μ where
  op a y := D.op a (e y)
  measurable_op a := (D.measurable_op a).comp e.measurable
  integrable_op a := he.integrable_comp_of_integrable (D.integrable_op a)
  positive a := he.quasiMeasurePreserving.ae (D.positive a)
  mass_preserving a z := by
    rw [he.integral_comp' (D.op a)]
    exact D.mass_preserving a z

@[simp] theorem pullInstrument_op (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν)
    (D : DensityInstrument (A := A) C ν) (a : A) (y : Y) :
    (pullInstrument e he D).op a y=D.op a (e y) := rfl

section Records
variable [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]

/-- Actions are retained, and only the observation component is recoded. -/
def stepEquiv (e : Y ≃ᵐ Z) : (A × Y) ≃ᵐ (A × Z) :=
  (MeasurableEquiv.refl A).prodCongr e

omit [MeasurableSingletonClass A] in
theorem step_preserving (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν) [IsFiniteMeasure μ] :
    MeasurePreserving (stepEquiv (A := A) e) (stepReference (A := A) μ) (stepReference (A := A) ν) :=
  (MeasurePreserving.id Measure.count).prod he

/-- The pulled policy sees exactly the corresponding recoded full history. -/
def pullPolicy (e : Y ≃ᵐ Z) (π : Policy (A := A) (Y := Z)) : Policy (A := A) (Y := Y) where
  probability N h a := π.probability N (historyEquiv (stepEquiv (A := A) e) N h) a
  measurable_probability N a := (π.measurable_probability N a).comp (historyEquiv _ N).measurable
  sum_one N _h := π.sum_one N _

omit [MeasurableSingletonClass A] in
theorem pullPolicy_weight (e : Y ≃ᵐ Z) (π : Policy (A := A) (Y := Z)) (N : ℕ)
    (h : History (A × Y) N) :
    (pullPolicy e π).weight N h=π.weight N (historyEquiv (stepEquiv (A := A) e) N h) := by
  induction N with
  | zero => rfl
  | succ N ih =>
    change (pullPolicy e π).weight N h.1 * π.probability N
      (historyEquiv (stepEquiv (A := A) e) N h.1) h.2.1 =
      π.weight N (historyEquiv (stepEquiv (A := A) e) N h.1) * π.probability N
        (historyEquiv (stepEquiv (A := A) e) N h.1) h.2.1
    rw [ih]

omit [Fintype A] [MeasurableSingletonClass A] in
theorem pull_run (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν)
    (D : DensityInstrument (A := A) C ν) (z : E) (N : ℕ) (h : History (A × Y) N) :
    run (pullInstrument e he D) z N h=run D z N (historyEquiv (stepEquiv (A := A) e) N h) := by
  induction N with
  | zero => rfl
  | succ N ih =>
    change D.op h.2.1 (e h.2.2) (run (pullInstrument e he D) z N h.1) =
      D.op h.2.1 (e h.2.2) (run D z N (historyEquiv (stepEquiv (A := A) e) N h.1))
    rw [ih]

omit [MeasurableSingletonClass A] in
theorem pull_recordDensity (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν)
    (D : DensityInstrument (A := A) C ν) (π : Policy (A := A) (Y := Z))
    (z : E) (N : ℕ) (h : History (A × Y) N) :
    recordDensity (pullInstrument e he D) (pullPolicy e π) z N h=
      recordDensity D π z N (historyEquiv (stepEquiv (A := A) e) N h) := by
  unfold recordDensity
  rw [pullPolicy_weight,pull_run]

omit [MeasurableSingletonClass A] in
/-- The actual finite full record law is pushed forward, with the corresponding history policy. -/
theorem recordLaw_map (e : Y ≃ᵐ Z) (he : MeasurePreserving e μ ν) [IsFiniteMeasure μ]
    (D : DensityInstrument (A := A) C ν) (π : Policy (A := A) (Y := Z)) (z : E) (N : ℕ) :
    (recordLaw (pullInstrument e he D) (pullPolicy e π) z N).map
      (historyEquiv (stepEquiv (A := A) e) N)=recordLaw D π z N := by
  have hd : recordDensity (pullInstrument e he D) (pullPolicy e π) z N=
      fun h => recordDensity D π z N (historyEquiv (stepEquiv (A := A) e) N h) := by
    funext h
    exact pull_recordDensity e he D π z N h
  unfold recordLaw
  rw [hd]
  exact map_withDensity _ (history_preserving (stepEquiv (A := A) e) (step_preserving e he) N) _

end Records
end
end Komorebi.LSM.ObservationEquivalence
