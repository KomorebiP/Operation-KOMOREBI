import Komorebi.Foundation.InternalSmallSupports

/-!
# Definable induction and ordinal comparison inside arbitrary ZFC models

All comprehension uses supplied finite-parameter first-order formulas.
No external well-foundedness of the membership relation is assumed.
-/

universe u v

namespace Komorebi.InternalOrdinalOrder

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence InternalFunctionSpaces
open InternalSelection InternalGraphTransport InternalSmallSupports

variable {M : Type u} [language.Structure M]

theorem member_irrefl (h : AxiomSemantics M) (x : M) : ¬ member x x :=
  member_irrefl_of_pairing_foundation h.pairing h.foundation x

theorem member_asymm (h : AxiomSemantics M) {x y : M}
    (hxy : member x y) : ¬ member y x :=
  member_asymm_of_pairing_foundation h.pairing h.foundation hxy

theorem ordinal_member {a b : M} (ha : OrdinalPredicate a) (hb : member b a) :
    OrdinalPredicate b :=
  ⟨ha.2 b hb, fun c hc => ha.2 c (ha.1 b hb c hc)⟩

/-- Foundation is applied to an actual Separation set of counterexamples. -/
theorem definable_minimal_member (h : AxiomSemantics M) {n : ℕ}
    (φ : language.Formula (Option (Fin n))) (e : Fin n → M) (t : M)
    (hex : ∃ x : M, member x t ∧ φ.Realize (assign e x)) :
    ∃ x : M, member x t ∧ φ.Realize (assign e x) ∧
      ∀ y : M, member y t → member y x → ¬ φ.Realize (assign e y) := by
  obtain ⟨s, hs⟩ := h.separation n φ e t
  have hn : ∃ x : M, member x s := by
    obtain ⟨x, hx, hφ⟩ := hex
    exact ⟨x, (hs x).mpr ⟨hx, hφ⟩⟩
  obtain ⟨x, hx, hmin⟩ := h.foundation s hn
  exact ⟨x, ((hs x).mp hx).1, ((hs x).mp hx).2,
    fun y hyt hyx hφ => hmin y ⟨(hs y).mpr ⟨hyt, hφ⟩, hyx⟩⟩

/-- Induction for a definable property on a transitive internal bound.
This does not claim induction for all external predicates on M. -/
theorem bounded_definable_induction (h : AxiomSemantics M) {n : ℕ}
    (φ : language.Formula (Option (Fin n))) (e : Fin n → M)
    (t : M) (ht : Transitive t)
    (step : ∀ x : M, member x t →
      (∀ y : M, member y x → φ.Realize (assign e y)) →
      φ.Realize (assign e x)) :
    ∀ x : M, member x t → φ.Realize (assign e x) := by
  classical
  intro x hxt
  by_contra hbad
  obtain ⟨a, hat, ha, hmin⟩ :=
    definable_minimal_member h φ.not e t ⟨x, hxt, hbad⟩
  apply ha
  apply step a hat
  intro b hba
  by_contra hb
  exact hmin b (ht a hat b hba) hba hb

/-- A transitive internal set containing two given transitive sets as members. -/
theorem transitive_pair_bound (h : AxiomSemantics M) {a b : M}
    (ha : Transitive a) (hb : Transitive b) :
    ∃ t : M, Transitive t ∧ member a t ∧ member b t := by
  obtain ⟨p, hp⟩ := h.pairing a b
  obtain ⟨r, hr⟩ := h.union p
  obtain ⟨q, hq⟩ := h.pairing r p
  obtain ⟨t, ht⟩ := h.union q
  have hr' : ∀ z : M, member z r ↔ member z a ∨ member z b := by
    intro z
    constructor
    · rintro hz
      obtain ⟨s, hs, hzs⟩ := (hr z).mp hz
      rcases (hp s).mp hs with rfl | rfl
      · exact Or.inl hzs
      · exact Or.inr hzs
    · rintro (hz | hz)
      · exact (hr z).mpr ⟨a, (hp a).mpr (Or.inl rfl), hz⟩
      · exact (hr z).mpr ⟨b, (hp b).mpr (Or.inr rfl), hz⟩
  have ht' : ∀ z : M, member z t ↔ member z r ∨ member z p := by
    intro z
    constructor
    · intro hz
      obtain ⟨s, hs, hzs⟩ := (ht z).mp hz
      rcases (hq s).mp hs with rfl | rfl
      · exact Or.inl hzs
      · exact Or.inr hzs
    · rintro (hz | hz)
      · exact (ht z).mpr ⟨r, (hq r).mpr (Or.inl rfl), hz⟩
      · exact (ht z).mpr ⟨p, (hq p).mpr (Or.inr rfl), hz⟩
  refine ⟨t, ?_, (ht' a).mpr (Or.inr ((hp a).mpr (Or.inl rfl))),
    (ht' b).mpr (Or.inr ((hp b).mpr (Or.inr rfl)))⟩
  intro z hz w hw
  apply (ht' w).mpr
  apply Or.inl
  apply (hr' w).mpr
  rcases (ht' z).mp hz with hz | hz
  · rcases (hr' z).mp hz with hza | hzb
    · exact Or.inl (ha z hza w hw)
    · exact Or.inr (hb z hzb w hw)
  · rcases (hp z).mp hz with rfl | rfl
    · exact Or.inl hw
    · exact Or.inr hw

def Comparable (a b : M) : Prop := member a b ∨ a = b ∨ member b a

def comparableF {α : Type v} (a b : α) : language.Formula α :=
  memF a b ⊔ (eqF a b ⊔ memF b a)

@[simp]
theorem comparableF_realize {α : Type v} (a b : α) (e : α → M) :
    (comparableF a b).Realize e ↔ Comparable (e a) (e b) := by
  simp [comparableF, Comparable]

/-- Nested definable induction replaces the external well-founded recursion
available for concrete ZFSet. The bound is transitive, not externally well-founded. -/
theorem ordinal_comparable_in_bound (h : AxiomSemantics M) {t : M}
    (ht : Transitive t) :
    ∀ a : M, member a t → OrdinalPredicate a →
      ∀ b : M, member b t → OrdinalPredicate b → Comparable a b := by
  let φ : language.Formula (Option (Fin 1)) :=
    (ordinalF none).imp
      (allF ((memF none (some (some 0))).imp
        ((ordinalF none).imp (comparableF (some none) none))))
  have hφ : ∀ a : M, φ.Realize (assign ![t] a) ↔
      (OrdinalPredicate a → ∀ b : M, member b t → OrdinalPredicate b → Comparable a b) := by
    intro a
    simp [φ, assign]
  have hall : ∀ a : M, member a t → φ.Realize (assign ![t] a) := by
    apply bounded_definable_induction h φ ![t] t ht
    intro a hat ih
    apply (hφ a).mpr
    intro ha
    let ψ : language.Formula (Option (Fin 1)) :=
      (ordinalF none).imp (comparableF (some 0) none)
    have hψ : ∀ b : M, ψ.Realize (assign ![a] b) ↔
        (OrdinalPredicate b → Comparable a b) := by
      intro b
      simp [ψ, assign]
    have inner : ∀ b : M, member b t → ψ.Realize (assign ![a] b) := by
      apply bounded_definable_induction h ψ ![a] t ht
      intro b hbt jih
      apply (hψ b).mpr
      intro hb
      classical
      by_cases hba : member b a
      · exact Or.inr (Or.inr hba)
      have hab : subset a b := by
        intro x hxa
        rcases (hφ x).mp (ih x hxa) (ordinal_member ha hxa) b hbt hb with hx | hx | hx
        · exact hx
        · subst x
          exact False.elim (hba hxa)
        · exact False.elim (hba (ha.1 x hxa b hx))
      by_cases he : a = b
      · exact Or.inr (Or.inl he)
      have hd : ∃ m : M, member m b ∧ ¬ member m a := by
        by_contra hn
        apply he
        apply h.extensionality a b
        intro x
        constructor
        · exact hab x
        · intro hxb
          by_contra hxa
          exact hn ⟨x, hxb, hxa⟩
      let δ : language.Formula (Option (Fin 1)) := (memF none (some 0)).not
      obtain ⟨m, hmb, hma, hmmin⟩ := definable_minimal_member h δ ![a] b
        (by simpa [δ, assign] using hd)
      have hma' : ¬ member m a := by simpa [δ, assign] using hma
      have hsub : subset m a := by
        intro x hxm
        by_contra hxa
        apply hmmin x (hb.1 m hmb x hxm) hxm
        simpa [δ, assign] using hxa
      rcases (hψ m).mp (jih m hmb) (ordinal_member hb hmb) with ham | heq | hma
      · exact False.elim (member_irrefl h a (hsub a ham))
      · exact Or.inl (heq.symm ▸ hmb)
      · exact False.elim (hma' hma)
    intro b hbt hb
    exact (hψ b).mp (inner b hbt) hb
  intro a hat ha
  exact (hφ a).mp (hall a hat) ha

theorem ordinal_comparable (h : AxiomSemantics M) {a b : M}
    (ha : OrdinalPredicate a) (hb : OrdinalPredicate b) : Comparable a b := by
  obtain ⟨t, ht, hat, hbt⟩ := transitive_pair_bound h ha.1 hb.1
  exact ordinal_comparable_in_bound h ht a hat ha b hbt hb

theorem ordinal_subset_iff (h : AxiomSemantics M) {a b : M}
    (ha : OrdinalPredicate a) (hb : OrdinalPredicate b) :
    subset a b ↔ a = b ∨ member a b := by
  constructor
  · intro hab
    rcases ordinal_comparable h ha hb with hab' | he | hba
    · exact Or.inr hab'
    · exact Or.inl he
    · exact False.elim (member_irrefl h b (hab b hba))
  · rintro (rfl | hab)
    · exact fun _ hx => hx
    · exact hb.1 a hab

theorem ordinal_subset_total (h : AxiomSemantics M) {a b : M}
    (ha : OrdinalPredicate a) (hb : OrdinalPredicate b) :
    subset a b ∨ subset b a := by
  rcases ordinal_comparable h ha hb with hab | rfl | hba
  · exact Or.inl (hb.1 a hab)
  · exact Or.inl (fun _ hx => hx)
  · exact Or.inr (ha.1 b hba)

/-- Nonempty internally represented sets of ordinals have a genuine least member. -/
theorem ordinal_set_has_least (h : AxiomSemantics M) {s : M}
    (hord : ∀ a : M, member a s → OrdinalPredicate a)
    (hne : ∃ a : M, member a s) :
    ∃ a : M, member a s ∧ ∀ b : M, member b s → a = b ∨ member a b := by
  obtain ⟨a, ha, hmin⟩ := h.foundation s hne
  refine ⟨a, ha, ?_⟩
  intro b hb
  rcases ordinal_comparable h (hord a ha) (hord b hb) with hab | he | hba
  · exact Or.inr hab
  · exact Or.inl he
  · exact False.elim (hmin b ⟨hb, hba⟩)

end Komorebi.InternalOrdinalOrder
