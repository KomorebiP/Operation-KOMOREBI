import KomorebiLSM.ContinuousRecords
import Mathlib.Probability.Kernel.Composition.IntegralCompProd

/-! Actual finite causal record laws from total history-indexed observation
kernels and a common measurable action-policy kernel. No latent state is used. -/
set_option autoImplicit false
namespace Komorebi.LSM.ObservationLawKernels
open MeasureTheory ProbabilityTheory
open scoped ENNReal
variable {I A Y : Type*} [MeasurableSpace I] [MeasurableSpace A] [MeasurableSpace Y]

abbrev History (I A Y : Type*) (n : ℕ) := I × ContinuousRecords.History (A × Y) n

def initial (i : I) : History I A Y 0 := (i,PUnit.unit)

def append (n : ℕ) (r : (History I A Y n × A) × Y) : History I A Y (n+1) :=
  (r.1.1.1,(r.1.1.2,(r.1.2,r.2)))

def drop (n : ℕ) (h : History I A Y (n+1)) : History I A Y n := (h.1,h.2.1)

omit [MeasurableSpace A] [MeasurableSpace Y] in
theorem initial_measurable : Measurable (initial (I := I) (A := A) (Y := Y)) :=
  measurable_id.prodMk measurable_const

theorem append_measurable (n : ℕ) : Measurable (append (I := I) (A := A) (Y := Y) n) :=
  ((measurable_fst.comp measurable_fst).comp measurable_fst).prodMk
    (((measurable_snd.comp measurable_fst).comp measurable_fst).prodMk
      ((measurable_snd.comp measurable_fst).prodMk measurable_snd))

theorem drop_measurable (n : ℕ) : Measurable (drop (I := I) (A := A) (Y := Y) n) :=
  measurable_fst.prodMk (measurable_fst.comp measurable_snd)

/-- Policies are actual Markov kernels on the full recorded history. -/
abbrev Policy (I A Y : Type*) [MeasurableSpace I] [MeasurableSpace A] [MeasurableSpace Y] :=
  (n : ℕ) → Kernel (History I A Y n) A

/-- An observation kernel is defined on every history and action, including
histories null under its own generated law. -/
abbrev ObservationKernel (I A Y : Type*) [MeasurableSpace I] [MeasurableSpace A] [MeasurableSpace Y] :=
  (n : ℕ) → Kernel (History I A Y n × A) Y

variable (π : Policy I A Y) (P : ObservationKernel I A Y)

/-- Choose an action, then an observation, and append both to the actual record. -/
noncomputable def law (μ0 : Measure I) : (n : ℕ) → Measure (History I A Y n)
  | 0 => μ0.map initial
  | n+1 => (((law μ0 n) ⊗ₘ π n) ⊗ₘ P n).map (append n)

variable [∀ n,IsMarkovKernel (π n)] [∀ n,IsMarkovKernel (P n)]

theorem law_probability_aux (μ0 : Measure I) [IsProbabilityMeasure μ0] :
    (n : ℕ) → IsProbabilityMeasure (law π P μ0 n)
  | 0 => inferInstanceAs (IsProbabilityMeasure (μ0.map initial))
  | n+1 => by
    have := law_probability_aux μ0 n
    exact inferInstanceAs (IsProbabilityMeasure ((((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n).map (append n)))

instance law_probability (μ0 : Measure I) [IsProbabilityMeasure μ0] (n : ℕ) :
    IsProbabilityMeasure (law π P μ0 n) := law_probability_aux π P μ0 n

instance law_zero_probability (μ0 : Measure I) [IsProbabilityMeasure μ0] :
    IsProbabilityMeasure (law π P μ0 0) := law_probability_aux π P μ0 0

/-- The explicit successor instance keeps the recursively expanded history type
visible to instance search. -/
instance law_succ_probability (μ0 : Measure I) [IsProbabilityMeasure μ0] (n : ℕ) :
    IsProbabilityMeasure (law π P μ0 (n+1)) := law_probability_aux π P μ0 (n+1)

/-- The policy-chosen action has the actual current P-history distribution. -/
noncomputable def policyPrefix (μ0 : Measure I) (n : ℕ) : Measure (History I A Y n × A) :=
  (law π P μ0 n) ⊗ₘ π n

instance policyPrefix_probability (μ0 : Measure I) [IsProbabilityMeasure μ0] (n : ℕ) :
    IsProbabilityMeasure (policyPrefix π P μ0 n) := by
  unfold policyPrefix
  infer_instance

/-- Marginal consistency follows from normalized kernels and the actual append map. -/
theorem law_consistent (μ0 : Measure I) [IsProbabilityMeasure μ0] (n : ℕ) :
    (law π P μ0 (n+1)).map (drop n)=law π P μ0 n := by
  change (((((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n).map (append n)).map (drop n))=_
  rw [Measure.map_map (drop_measurable n) (append_measurable n)]
  have he : (drop (I := I) (A := A) (Y := Y) n) ∘ append n=Prod.fst ∘ Prod.fst := rfl
  rw [he,← Measure.map_map measurable_fst measurable_fst]
  change (((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n).fst.fst=_
  rw [Measure.fst_compProd,Measure.fst_compProd]

/-- The defining joint law has the chronological iterated-kernel integral. -/
theorem lintegral_law_succ (μ0 : Measure I) [IsProbabilityMeasure μ0] (n : ℕ)
    (f : History I A Y (n+1) → ℝ≥0∞) (hf : Measurable f) :
    (∫⁻ h,f h∂law π P μ0 (n+1))=
      ∫⁻ h,∫⁻ a,∫⁻ y,f (append n ((h,a),y))∂P n (h,a)∂π n h∂law π P μ0 n := by
  have hm : Measurable (fun r : (History I A Y n × A) × Y => f (append n r)) :=
    hf.comp (append_measurable n)
  calc (∫⁻ h,f h∂law π P μ0 (n+1))=
      ∫⁻ r,f (append n r)∂((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n :=
        lintegral_map (μ := ((law π P μ0 n) ⊗ₘ π n) ⊗ₘ P n) hf (append_measurable n)
    _ = ∫⁻ ha,∫⁻ y,f (append n (ha,y))∂P n ha∂(law π P μ0 n) ⊗ₘ π n :=
      Measure.lintegral_compProd hm
    _ = _ := Measure.lintegral_compProd (hm.lintegral_kernel_prod_right' (κ := P n))

end Komorebi.LSM.ObservationLawKernels
