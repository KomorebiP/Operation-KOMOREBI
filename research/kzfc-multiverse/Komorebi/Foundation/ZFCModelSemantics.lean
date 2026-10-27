import Komorebi.Foundation.ZFCAxiomSyntax

/-!
# Exact axiom semantics for arbitrary membership structures

Every set witness below is an element of M. The schema predicates are indexed
by syntactic formulas, not by all external predicates on M.
-/

universe u

namespace Komorebi.ZFCModelSemantics

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax

variable {M : Type u} [language.Structure M]

@[simp]
theorem extensionalitySentence_realize :
    M ⊨ extensionalitySentence ↔
      ∀ x y : M, (∀ z : M, member z x ↔ member z y) → x = y := by
  simp [Sentence.Realize, extensionalitySentence, assign]

@[simp]
theorem emptySentence_realize : M ⊨ emptySentence ↔ ∃ x : M, IsEmpty x := by
  simp [Sentence.Realize, emptySentence, assign]

@[simp]
theorem pairingSentence_realize :
    M ⊨ pairingSentence ↔ ∀ x y : M, ∃ p : M, IsPair p x y := by
  simp [Sentence.Realize, pairingSentence, assign]

@[simp]
theorem unionSentence_realize :
    M ⊨ unionSentence ↔ ∀ x : M, ∃ r : M, IsUnion r x := by
  simp [Sentence.Realize, unionSentence, assign]

@[simp]
theorem powersetSentence_realize :
    M ⊨ powersetSentence ↔ ∀ x : M, ∃ p : M, IsPower p x := by
  simp [Sentence.Realize, powersetSentence, assign]

@[simp]
theorem infinitySentence_realize :
    M ⊨ infinitySentence ↔ ∃ w : M, GeneralMembershipSemantics.IsInductive w := by
  simp [Sentence.Realize, infinitySentence, assign]

@[simp]
theorem foundationSentence_realize :
    M ⊨ foundationSentence ↔ ∀ x : M, (∃ a : M, member a x) →
      ∃ y : M, member y x ∧ ∀ z : M, ¬ (member z x ∧ member z y) := by
  simp [Sentence.Realize, foundationSentence, assign]

@[simp]
theorem choiceSentence_realize :
    M ⊨ choiceSentence ↔ ∀ x : M,
      (∀ a : M, member a x → ∃ b : M, member b a) →
      ∃ g : M, IsChoiceGraph x g := by
  simp [Sentence.Realize, choiceSentence, assign]

/-- These fields are exactly the independently spelled-out axiom meanings.
They contain no compactness, ordinal classification, or absoluteness theorem. -/
structure AxiomSemantics (M : Type u) [language.Structure M] : Prop where
  extensionality : ∀ x y : M, (∀ z : M, member z x ↔ member z y) → x = y
  empty : ∃ x : M, IsEmpty x
  pairing : ∀ x y : M, ∃ p : M, IsPair p x y
  union : ∀ x : M, ∃ r : M, IsUnion r x
  powerset : ∀ x : M, ∃ p : M, IsPower p x
  infinity : ∃ w : M, GeneralMembershipSemantics.IsInductive w
  foundation : ∀ x : M, (∃ a : M, member a x) →
    ∃ y : M, member y x ∧ ∀ z : M, ¬ (member z x ∧ member z y)
  choice : ∀ x : M, (∀ a : M, member a x → ∃ b : M, member b a) →
    ∃ g : M, IsChoiceGraph x g
  separation : ∀ (n : ℕ) (φ : language.Formula (Option (Fin n))) (e : Fin n → M),
    SeparationInstance φ e
  replacement : ∀ (n : ℕ) (φ : language.Formula (Option (Option (Fin n))))
    (e : Fin n → M), ReplacementInstance φ e

/-- No arbitrary-model comparison is being assumed: this is proved by unfolding
all eight fixed sentences and both fully parameterized syntactic schemas. -/
theorem model_zfc_iff_axiomSemantics : M ⊨ zfcTheory ↔ AxiomSemantics M := by
  rw [model_zfc_iff_sentences]
  constructor
  · intro h
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
    · exact extensionalitySentence_realize.mp (h .extensionality)
    · exact emptySentence_realize.mp (h .empty)
    · exact pairingSentence_realize.mp (h .pairing)
    · exact unionSentence_realize.mp (h .union)
    · exact powersetSentence_realize.mp (h .powerset)
    · exact infinitySentence_realize.mp (h .infinity)
    · exact foundationSentence_realize.mp (h .foundation)
    · exact choiceSentence_realize.mp (h .choice)
    · intro n φ
      exact (separationSentence_realize φ).mp (h (.separation n φ))
    · intro n φ
      exact (replacementSentence_realize φ).mp (h (.replacement n φ))
  · intro h c
    cases c with
    | extensionality => exact extensionalitySentence_realize.mpr h.extensionality
    | empty => exact emptySentence_realize.mpr h.empty
    | pairing => exact pairingSentence_realize.mpr h.pairing
    | union => exact unionSentence_realize.mpr h.union
    | powerset => exact powersetSentence_realize.mpr h.powerset
    | infinity => exact infinitySentence_realize.mpr h.infinity
    | foundation => exact foundationSentence_realize.mpr h.foundation
    | choice => exact choiceSentence_realize.mpr h.choice
    | separation n φ => exact (separationSentence_realize φ).mpr (h.separation n φ)
    | replacement n φ => exact (replacementSentence_realize φ).mpr (h.replacement n φ)

/-- Internal membership is irreflexive using only Pairing and Foundation.
External well-foundedness of M is neither required nor concluded. -/
theorem member_irrefl_of_pairing_foundation
    (hp : ∀ x y : M, ∃ p : M, IsPair p x y)
    (hf : ∀ x : M, (∃ a : M, member a x) →
      ∃ y : M, member y x ∧ ∀ z : M, ¬ (member z x ∧ member z y))
    (x : M) : ¬ member x x := by
  intro hxx
  obtain ⟨p, hp⟩ := hp x x
  have hx : member x p := (hp x).mpr (Or.inl rfl)
  obtain ⟨y, hy, hd⟩ := hf p ⟨x, hx⟩
  have he : y = x := (hp y).mp hy |>.elim id id
  subst y
  exact hd x ⟨hx, hxx⟩

/-- A two-cycle is ruled out internally, without an external rank function. -/
theorem member_asymm_of_pairing_foundation
    (hp : ∀ x y : M, ∃ p : M, IsPair p x y)
    (hf : ∀ x : M, (∃ a : M, member a x) →
      ∃ y : M, member y x ∧ ∀ z : M, ¬ (member z x ∧ member z y))
    {x y : M} (hxy : member x y) : ¬ member y x := by
  intro hyx
  obtain ⟨p, hp⟩ := hp x y
  have hx : member x p := (hp x).mpr (Or.inl rfl)
  have hy : member y p := (hp y).mpr (Or.inr rfl)
  obtain ⟨z, hz, hd⟩ := hf p ⟨x, hx⟩
  rcases (hp z).mp hz with rfl | rfl
  · exact hd y ⟨hy, hyx⟩
  · exact hd x ⟨hx, hxy⟩

/-- Russell's argument uses one actual zero-parameter Separation instance.
It does not appeal to Foundation or to arbitrary external comprehension. -/
theorem no_universal_of_separation
    (hs : ∀ (φ : language.Formula (Option (Fin 0))) (e : Fin 0 → M),
      SeparationInstance φ e) : ¬ ∃ a : M, ∀ x : M, member x a := by
  rintro ⟨a, ha⟩
  let φ : language.Formula (Option (Fin 0)) := (memF none none).not
  obtain ⟨b, hb⟩ := hs φ Fin.elim0 a
  have h : member b b ↔ member b a ∧ ¬ member b b := by
    simpa [φ, assign] using hb b
  have hn : ¬ member b b := fun hx => (h.mp hx).2 hx
  exact hn (h.mpr ⟨ha b, hn⟩)

theorem model_zfc_member_irrefl (h : M ⊨ zfcTheory) (x : M) : ¬ member x x := by
  have h := model_zfc_iff_axiomSemantics.mp h
  exact member_irrefl_of_pairing_foundation h.pairing h.foundation x

theorem model_zfc_no_universal (h : M ⊨ zfcTheory) : ¬ ∃ a : M, ∀ x : M, member x a := by
  have h := model_zfc_iff_axiomSemantics.mp h
  exact no_universal_of_separation (h.separation 0)

end Komorebi.ZFCModelSemantics
