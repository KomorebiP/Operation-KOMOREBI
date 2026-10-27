import PaperX.CommonSpine

/-! Assemble the source's conditional completion statement using only positive
precision, continuous coefficient inclusions, and prescribed local predicates.
Closedness is an explicit hypothesis of the manuscript, not an unconditional claim. -/
set_option autoImplicit false
namespace PaperX.CompletionAssembly
open PaperX.RepresentationLimits PaperX.RepresentationTopology PaperX.RepresentationForests
open PaperX.SystemCompletion PaperX.CommonSpine

variable {R G ι : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]

theorem finite_zero_level (I : Ideal R) (C : Conditions (G := G) (ι := ι) I) :
    Finite {ρ : MatrixRep (R ⧸ I^0) G ι // C.allowed 0 ρ} := by
  have : Subsingleton (R ⧸ I^0) := by
    simp only [pow_zero, Ideal.one_eq_top]
    infer_instance
  have : Subsingleton (MatrixRep (R ⧸ I^0) G ι) := ⟨fun a b => by
    ext g i j
    exact Subsingleton.elim _ _⟩
  infer_instance

theorem positive_finite_levels (I : Ideal R) (C : Conditions (G := G) (ι := ι) I)
    (h : ∀ k, 0 < k → Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ}) :
    ∀ k, Finite {ρ : MatrixRep (R ⧸ I^k) G ι // C.allowed k ρ} := by
  intro k
  by_cases hk : k = 0
  · subst k
    exact finite_zero_level I C
  · exact h k (Nat.pos_of_ne_zero hk)

theorem positive_levels_iff_all (I : Ideal R) (C : Conditions (G := G) (ι := ι) I) :
    (∀ k, 0 < k → ∃ ρ, C.allowed k ρ) ↔ ∀ k, ∃ ρ, C.allowed k ρ := by
  constructor
  · intro h k
    by_cases hk : k = 0
    · subst k
      obtain ⟨ρ, hρ⟩ := h 1 (by decide)
      exact ⟨transition I (Nat.zero_le 1) ρ, C.downward _ _ hρ⟩
    · exact h k (Nat.pos_of_ne_zero hk)
  · intro h k _
    exact h k

theorem residual_and_higher_iff_all (I : Ideal R) (C : Conditions (G := G) (ι := ι) I) :
    ((∃ ρ, C.allowed 1 ρ) ∧ ∀ k, 2 ≤ k → ∃ ρ, C.allowed k ρ) ↔
      ∀ k, ∃ ρ, C.allowed k ρ := by
  rw [← positive_levels_iff_all]
  constructor
  · rintro ⟨h1, hh⟩ k hk
    by_cases h : k = 1
    · subst k; exact h1
    · exact hh k (by omega)
  · intro h
    exact ⟨h 1 (by decide), fun k hk => h k (by omega)⟩

/-- Prescribed local predicates are evaluated on the actual field-valued
representations produced by coefficient change. -/
theorem conditional_common_spine_completion
    {Λ V E : Type} [TopologicalSpace G] [Field E]
    (O K : Λ → Type) [∀ l, CommRing (O l)] [∀ l, Field (K l)]
    [∀ l, TopologicalSpace (K l)]
    (I : (l : Λ) → Ideal (O l)) [∀ l, IsAdicComplete (I l) (O l)]
    (C : (l : Λ) → Conditions (G := G) (ι := ι) (I l))
    (finite : ∀ l k, 0 < k → Finite {ρ : MatrixRep (O l ⧸ (I l)^k) G ι // (C l).allowed k ρ})
    (occupied : ∀ l k, 0 < k → ∃ ρ, (C l).allowed k ρ)
    (continuous : ∀ l k ρ, (C l).allowed k ρ → FiniteRepContinuous ρ)
    (inc : (l : Λ) → O l →+* K l)
    (hinc : ∀ l, @Continuous (O l) (K l) (I l).adicTopology inferInstance (inc l))
    (emb : (l : Λ) → E →+* K l)
    (Local : (l : Λ) → MatrixRep (K l) G ι → Prop)
    (stable : ∀ l ρ, Realizes (I l) (C l) ρ → Local l (changeCoefficients (inc l) ρ))
    (sample : V → G) (good : Λ → V → Prop)
    (P : V → Polynomial E) (localP : (l : Λ) → V → Polynomial (O l))
    (integrality : ∀ l v, good l v → (localP l v).map (inc l) = (P v).map (emb l))
    (spec : ∀ l k τ, (C l).allowed k τ → ∀ v, good l v →
      (τ (sample v)).charpoly = (localP l v).map (Ideal.Quotient.mk ((I l)^k))) :
    ∃ ρ : (l : Λ) → MatrixRep (O l) G ι,
      SystemRealizes O I C ρ ∧
      (∀ l, Continuous (changeCoefficients (inc l) (ρ l)) ∧
        Local l (changeCoefficients (inc l) (ρ l))) ∧
      ∀ l v, good l v →
        (changeCoefficients (inc l) (ρ l) (sample v)).charpoly = (P v).map (emb l) := by
  obtain ⟨ρ, hρ, hlocal, hpoly⟩ := common_spine_completion O K I C
    (fun l => positive_finite_levels (I l) (C l) (finite l))
    (fun l => (positive_levels_iff_all (I l) (C l)).mp (occupied l)) continuous
    (fun l r => Local l (changeCoefficients (inc l) r)) stable inc emb sample good
    P localP integrality spec
  exact ⟨ρ, hρ, fun l => ⟨coefficient_change_continuous (I l) (inc l) (hinc l) (ρ l)
    (hlocal l).1, (hlocal l).2⟩, hpoly⟩

end PaperX.CompletionAssembly
