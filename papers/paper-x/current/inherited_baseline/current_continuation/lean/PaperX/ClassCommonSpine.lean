import PaperX.ClassCompletion
import PaperX.ClassInvariants

/-! The full conditional common-spine completion interface on unframed levels.
The local closure input remains a stated hypothesis; no arithmetic invariant is
silently defined to be this predicate. -/
set_option autoImplicit false
namespace PaperX.ClassCommonSpine
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationClasses
open PaperX.RepresentationForests PaperX.ClassCompletion PaperX.ClassInvariants
open PaperX.CompletionAssembly PaperX.SystemCompletion

/-- A class with one continuous representative has all its frames continuous. -/
theorem all_frames_continuous {R G ι : Type} [CommRing R] [Group G]
    [TopologicalSpace G] [Fintype ι] [DecidableEq ι]
    (c : ClassRep R G ι) (h : ∃ σ, classOf σ = c ∧ FiniteRepContinuous σ)
    (ρ : MatrixRep R G ι) (hρ : classOf ρ = c) : FiniteRepContinuous ρ := by
  obtain ⟨σ, hσ, hc⟩ := h
  exact finiteContinuous_of_classOf_eq (hρ.trans hσ.symm) hc

/-- An actual continuous integral representation realizes all admissible classes. -/
theorem continuous_class_completion {R G ι : Type} [CommRing R] [Group G]
    [TopologicalSpace G] [Fintype ι] [DecidableEq ι]
    (I : Ideal R) [IsAdicComplete I R]
    (C : ClassConditions (G := G) (ι := ι) I)
    (finiteR : ∀ k, Finite (R ⧸ I^k))
    (finiteC : ∀ k, 0 < k → Finite {c // C.allowed k c})
    (occupied : ∀ k, 0 < k → ∃ c, C.allowed k c)
    (continuous : ∀ k c, C.allowed k c → ∃ ρ, classOf ρ = c ∧ FiniteRepContinuous ρ) :
    ∃ ρ : MatrixRep R G ι,
      (∀ k, C.allowed k (classOf (reduce I ρ k))) ∧ AdicRepContinuous I ρ := by
  apply exists_continuous_realization I (framed I C)
  · apply positive_finite_levels
    intro k hk
    let : Finite (R ⧸ I^k) := finiteR k
    let : Finite {c // C.allowed k c} := finiteC k hk
    exact framed_finite I C k
  · apply (positive_levels_iff_all I (framed I C)).mp
    intro k hk
    exact (framed_nonempty_iff I C k).mpr (occupied k hk)
  · intro k ρ hρ
    exact all_frames_continuous (classOf ρ) (continuous k _ hρ) ρ rfl

/-- Positive finite unframed levels over finite-residue complete coefficient
rings give continuous realizations with the whole common polynomial spine and
the explicitly supplied inverse-limit-closed local conditions. -/
theorem unframed_common_spine_completion
    {Λ G ι V E : Type} [Group G] [TopologicalSpace G] [Fintype ι] [DecidableEq ι]
    [Field E] (O K : Λ → Type) [∀ l, CommRing (O l)] [∀ l, Field (K l)]
    [∀ l, TopologicalSpace (K l)]
    (I : (l : Λ) → Ideal (O l)) [∀ l, IsAdicComplete (I l) (O l)]
    (hI : ∀ l, (I l).FG) [∀ l, Finite (O l ⧸ I l)]
    (C : (l : Λ) → ClassConditions (G := G) (ι := ι) (I l))
    (finite : ∀ l k, 0 < k → Finite {c // (C l).allowed k c})
    (occupied : ∀ l k, 0 < k → ∃ c, (C l).allowed k c)
    (continuous : ∀ l k c, (C l).allowed k c →
      ∃ ρ, classOf ρ = c ∧ FiniteRepContinuous ρ)
    (inc : (l : Λ) → O l →+* K l)
    (hinc : ∀ l, @Continuous (O l) (K l) (I l).adicTopology inferInstance (inc l))
    (emb : (l : Λ) → E →+* K l)
    (Local : (l : Λ) → MatrixRep (K l) G ι → Prop)
    (stable : ∀ l ρ, (∀ k, (C l).allowed k (classOf (reduce (I l) ρ k))) →
      Local l (changeCoefficients (inc l) ρ))
    (sample : V → G) (good : Λ → V → Prop)
    (P : V → Polynomial E) (localP : (l : Λ) → V → Polynomial (O l))
    (integrality : ∀ l v, good l v → (localP l v).map (inc l) = (P v).map (emb l))
    (spec : ∀ l k c, (C l).allowed k c → ∀ v, good l v →
      classCharpoly c (sample v) = (localP l v).map (Ideal.Quotient.mk ((I l)^k))) :
    ∃ ρ : (l : Λ) → MatrixRep (O l) G ι,
      (∀ l k, (C l).allowed k (classOf (reduce (I l) (ρ l) k))) ∧
      (∀ l, Continuous (changeCoefficients (inc l) (ρ l)) ∧
        Local l (changeCoefficients (inc l) (ρ l))) ∧
      ∀ l v, good l v →
        (changeCoefficients (inc l) (ρ l) (sample v)).charpoly = (P v).map (emb l) := by
  apply conditional_common_spine_completion O K I (fun l => framed (I l) (C l))
    ?_ ?_ ?_ inc hinc emb Local stable sample good P localP integrality ?_
  · intro l k hk
    let : Finite (O l ⧸ (I l)^k) := finite_coefficients (I l) (hI l) k
    let : Finite {c // (C l).allowed k c} := finite l k hk
    exact framed_finite (I l) (C l) k
  · intro l k hk
    exact (framed_nonempty_iff (I l) (C l) k).mpr (occupied l k hk)
  · intro l k ρ hρ
    exact all_frames_continuous (classOf ρ) (continuous l k _ hρ) ρ rfl
  · intro l k ρ hρ v hv
    exact spec l k (classOf ρ) hρ v hv

end PaperX.ClassCommonSpine
