import KomorebiLSM.FiniteInstrument
import KomorebiLSM.PredictiveCompletion

/-! P26: the bounded invariant completion of the mass row equals the span
of all chronological word tests. Minimality is against actual belief readouts. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteInstruments
open scoped BigOperators
open Module FiniteBayes
universe u v

section WordRows
variable {X : Type*} [AddCommGroup X] [Module ℝ X] {S : Type*}

noncomputable def wordRow (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) (w : List S) :
    Dual ℝ X := mu.comp (wordAction L w)

@[simp] theorem wordRow_nil (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    wordRow L mu [] = mu := by simp [wordRow]

@[simp] theorem wordRow_cons (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) (s : S) (w : List S) :
    wordRow L mu (s::w) = (L s).dualMap (wordRow L mu w) := rfl

noncomputable def wordSpan (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    Submodule ℝ (Dual ℝ X) := Submodule.span ℝ (Set.range (wordRow L mu))

theorem wordRow_mem (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) (w : List S) :
    wordRow L mu w ∈ wordSpan L mu := Submodule.subset_span ⟨w,rfl⟩

theorem massRow_mem_wordSpan (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    mu ∈ wordSpan L mu := by simpa using wordRow_mem L mu []

theorem wordSpan_invariant (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    CommonInvariant (fun s => (L s).dualMap) (wordSpan L mu) := by
  intro s z hz
  obtain ⟨r,hr,rfl⟩ := Submodule.mem_map.mp hz
  induction hr using Submodule.span_induction with
  | mem r hr =>
    obtain ⟨w,rfl⟩ := hr
    exact wordRow_mem L mu (s::w)
  | zero => simpa using (wordSpan L mu).zero_mem
  | add x y hx hy ihx ihy => simpa using (wordSpan L mu).add_mem ihx ihy
  | smul a x hx ih => simpa using (wordSpan L mu).smul_mem a ih

variable [FiniteDimensional ℝ X]

/-- The initial row is not assumed to be a fixed point. -/
noncomputable def instrumentCompletion (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    Submodule ℝ (Dual ℝ X) := predictiveCompletion L (Submodule.span ℝ {mu})

theorem massRow_mem_completion (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    mu ∈ instrumentCompletion L mu :=
  (predictiveCompletion_isLeast L _).1.1 (Submodule.subset_span (Set.mem_singleton mu))

theorem instrumentCompletion_invariant (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    CommonInvariant (fun s => (L s).dualMap) (instrumentCompletion L mu) :=
  (predictiveCompletion_isLeast L _).1.2

theorem wordRow_mem_completion (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) (w : List S) :
    wordRow L mu w ∈ instrumentCompletion L mu := by
  induction w with
  | nil => simpa using massRow_mem_completion L mu
  | cons s w ih =>
    exact instrumentCompletion_invariant L mu s (Submodule.mem_map.mpr ⟨_,ih,rfl⟩)

/-- The finite iteration recovers exactly the span of all finite tests. -/
theorem instrumentCompletion_eq_wordSpan (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X) :
    instrumentCompletion L mu = wordSpan L mu := by
  apply le_antisymm
  · apply invariantCompletion_minimal
    · exact Submodule.span_le.mpr (by intro x hx; rcases Set.mem_singleton_iff.mp hx with rfl
                                    exact massRow_mem_wordSpan L mu)
    · exact wordSpan_invariant L mu
  · apply Submodule.span_le.mpr
    rintro _ ⟨w,rfl⟩
    exact wordRow_mem_completion L mu w

/-- A nonzero mass row starts with dimension one. -/
theorem instrumentCompletion_stabilizes (L : S → X →ₗ[ℝ] X) (mu : Dual ℝ X)
    (hmu : mu ≠ 0) :
    ∃ n ≤ finrank ℝ X - 1,
      invariantSequence (fun s => (L s).dualMap) (Submodule.span ℝ {mu}) (n+1) =
        invariantSequence (fun s => (L s).dualMap) (Submodule.span ℝ {mu}) n := by
  simpa only [finrank_span_singleton hmu] using
    predictiveCompletion_stopping_bound L (Submodule.span ℝ {mu})

end WordRows

section FiniteBeliefs
variable {I : Type u} [Fintype I] {S : Type v}
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- Linear readouts on all priors, not a supplied invariant-row condition. -/
def ReadsAllWords (L : S → (I → ℝ) →ₗ[ℝ] (I → ℝ)) (R : (I → ℝ) →ₗ[ℝ] E) : Prop :=
  ∀ w : List S, ∃ f : E →ₗ[ℝ] ℝ,
    ∀ p, IsPrior p → f (R p) = mass (wordAction L w p)

theorem completion_le_word_reading_summary
    (L : S → (I → ℝ) →ₗ[ℝ] (I → ℝ)) (R : (I → ℝ) →ₗ[ℝ] E)
    (h : ReadsAllWords L R) :
    instrumentCompletion L mass ≤ LinearMap.range R.dualMap := by
  rw [instrumentCompletion_eq_wordSpan]
  apply Submodule.span_le.mpr
  rintro r ⟨w,rfl⟩
  obtain ⟨f,hf⟩ := h w
  refine ⟨f, ?_⟩
  exact linearMap_eq_of_priors (f.comp R) (wordRow L mass w) hf

theorem finite_instrument_stopping_bound [Nonempty I]
    (L : S → (I → ℝ) →ₗ[ℝ] (I → ℝ)) :
    ∃ n ≤ Fintype.card I - 1,
      invariantSequence (fun s => (L s).dualMap) (Submodule.span ℝ {mass}) (n+1) =
        invariantSequence (fun s => (L s).dualMap) (Submodule.span ℝ {mass}) n := by
  simpa only [Module.finrank_fintype_fun_eq_card] using instrumentCompletion_stabilizes L mass mass_ne_zero

end FiniteBeliefs
end Komorebi.LSM.FiniteInstruments
