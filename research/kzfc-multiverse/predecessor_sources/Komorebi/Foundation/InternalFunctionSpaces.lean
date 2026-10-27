import Komorebi.Foundation.InternalResidualSentence

/-!
# Internal products, function spaces and bounded relation tables

Every constructed set is an element of the supplied membership structure.
Only explicit first-order Separation instances are used. No closure under
arbitrary external subsets or functions is postulated.
-/

universe u v

namespace Komorebi.InternalFunctionSpaces

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax
open ZFCModelSemantics InternalResidualSentence

variable {M : Type u} [language.Structure M]

theorem singleton_exists (h : AxiomSemantics M) (x : M) :
    ∃ s : M, IsSingleton s x := by
  obtain ⟨s, hs⟩ := h.pairing x x
  exact ⟨s, fun z => (hs z).trans (Iff.of_eq (or_self _))⟩

theorem orderedPair_exists (h : AxiomSemantics M) (x y : M) :
    ∃ p : M, IsOrderedPair p x y := by
  obtain ⟨a, ha⟩ := singleton_exists h x
  obtain ⟨b, hb⟩ := h.pairing x y
  obtain ⟨p, hp⟩ := h.pairing a b
  exact ⟨p, a, b, ha, hb, hp⟩

theorem orderedPair_unique (h : AxiomSemantics M) {p q x y : M}
    (hp : IsOrderedPair p x y) (hq : IsOrderedPair q x y) : p = q := by
  obtain ⟨a, b, ha, hb, hp⟩ := hp
  obtain ⟨c, d, hc, hd, hq⟩ := hq
  have hac : a = c := h.extensionality a c (fun z => (ha z).trans (hc z).symm)
  have hbd : b = d := h.extensionality b d (fun z => (hb z).trans (hd z).symm)
  subst c; subst d
  exact h.extensionality p q (fun z => (hp z).trans (hq z).symm)

theorem orderedPair_common {p x y z : M} (hp : IsOrderedPair p x y) :
    (∀ t : M, member t p → member z t) ↔ z = x := by
  obtain ⟨a, b, ha, hb, hp⟩ := hp
  constructor
  · intro hz
    exact (ha z).mp (hz a ((hp a).mpr (Or.inl rfl)))
  · intro hz t ht
    subst z
    rcases (hp t).mp ht with rfl | rfl
    · exact (ha x).mpr rfl
    · exact (hb x).mpr (Or.inl rfl)

theorem orderedPair_union {p x y z : M} (hp : IsOrderedPair p x y) :
    (∃ t : M, member t p ∧ member z t) ↔ z = x ∨ z = y := by
  obtain ⟨a, b, ha, hb, hp⟩ := hp
  constructor
  · rintro ⟨t, ht, hz⟩
    rcases (hp t).mp ht with rfl | rfl
    · exact Or.inl ((ha z).mp hz)
    · exact (hb z).mp hz
  · intro hz
    exact ⟨b, (hp b).mpr (Or.inr rfl), (hb z).mpr hz⟩

theorem orderedPair_injective {p x y x' y' : M}
    (hp : IsOrderedPair p x y) (hp' : IsOrderedPair p x' y') : x = x' ∧ y = y' := by
  have hx : x = x' := orderedPair_common hp' |>.mp (orderedPair_common hp |>.mpr rfl)
  subst x'
  have hy : y = x ∨ y = y' := orderedPair_union hp' |>.mp
    (orderedPair_union hp |>.mpr (Or.inr rfl))
  refine ⟨rfl, ?_⟩
  rcases hy with hxy | hy
  · have hy' : y' = x ∨ y' = y := orderedPair_union hp |>.mp
      (orderedPair_union hp' |>.mpr (Or.inr rfl))
    rcases hy' with hy' | hy'
    · exact hxy.trans hy'.symm
    · exact hy'.symm
  · exact hy

theorem product_unique (h : AxiomSemantics M) {p q x y : M}
    (hp : Product p x y) (hq : Product q x y) : p = q :=
  h.extensionality p q (fun z => (hp z).trans (hq z).symm)

/-- The product-entry predicate is actual first-order syntax. -/
def productEntryF {α : Type v} (z x y : α) : language.Formula α :=
  exF (let z := some z; let x := some x; let y := some y; let a := none
    memF a x ⊓ exF (memF none (some y) ⊓ pairF (some z) (some a) none))

@[simp]
theorem productEntryF_realize {α : Type v} (z x y : α) (e : α → M) :
    (productEntryF z x y).Realize e ↔
      ∃ a : M, member a (e x) ∧ ∃ b : M, member b (e y) ∧
        IsOrderedPair (e z) a b := by
  simp [productEntryF, assign]

/-- Pairing, Union, two Powersets and one Separation instance suffice. -/
theorem product_exists (h : AxiomSemantics M) (x y : M) : ∃ p : M, Product p x y := by
  obtain ⟨xy, hxy⟩ := h.pairing x y
  obtain ⟨s, hs⟩ := h.union xy
  obtain ⟨ps, hps⟩ := h.powerset s
  obtain ⟨pps, hpps⟩ := h.powerset ps
  let φ : language.Formula (Option (Fin 2)) := productEntryF none (some 0) (some 1)
  obtain ⟨p, hp⟩ := h.separation 2 φ ![x,y] pps
  refine ⟨p, ?_⟩
  intro z
  have hz := hp z
  simp only [φ, productEntryF_realize, assign, Matrix.cons_val_zero,
    Matrix.cons_val_one] at hz
  refine hz.trans ?_
  constructor
  · exact fun hz => hz.2
  · intro he
    obtain ⟨a, ha, b, hb, hab⟩ := he
    refine ⟨(hpps z).mpr ?_, a, ha, b, hb, hab⟩
    obtain ⟨aa, ab, haa, hab', hpab⟩ := hab
    intro t ht
    apply (hps t).mpr
    intro w hw
    rcases (hpab t).mp ht with rfl | rfl
    · have hw' : w = a := (haa w).mp hw
      subst w
      exact (hs a).mpr ⟨x, (hxy x).mpr (Or.inl rfl), ha⟩
    · rcases (hab' w).mp hw with hwa | hwb
      · subst w
        exact (hs a).mpr ⟨x, (hxy x).mpr (Or.inl rfl), ha⟩
      · subst w
        exact (hs b).mpr ⟨y, (hxy y).mpr (Or.inr rfl), hb⟩

theorem pairMember_product_iff (h : AxiomSemantics M) {p x y a b : M}
    (hp : Product p x y) : PairMember a b p ↔ member a x ∧ member b y := by
  constructor
  · rintro ⟨z, hz, hzp⟩
    obtain ⟨c, hc, d, hd, hcd⟩ := (hp z).mp hzp
    obtain ⟨rfl, rfl⟩ := orderedPair_injective hz hcd
    exact ⟨hc, hd⟩
  · rintro ⟨ha,hb⟩
    obtain ⟨z,hz⟩ := orderedPair_exists h a b
    exact ⟨z,hz,(hp z).mpr ⟨a,ha,b,hb,hz⟩⟩

theorem functionGraph_pair_bounds {x y g a b : M}
    (hg : FunctionGraph x y g) (hab : PairMember a b g) : member a x ∧ member b y := by
  obtain ⟨p,hp,hgp⟩ := hg.1
  obtain ⟨z,hz,hzg⟩ := hab
  obtain ⟨c,hc,d,hd,hcd⟩ := (hp z).mp (hgp z hzg)
  obtain ⟨rfl,rfl⟩ := orderedPair_injective hz hcd
  exact ⟨hc,hd⟩

theorem functionGraph_value_unique {x y g a b c : M}
    (hg : FunctionGraph x y g) (hab : PairMember a b g) (hac : PairMember a c g) : b = c := by
  obtain ⟨d,_,hd⟩ := hg.2 a (functionGraph_pair_bounds hg hab).1
  exact (hd b hab).trans (hd c hac).symm

/-- The internal function space contains exactly the internally existing graphs. -/
def FunctionSpace (e x y : M) : Prop := ∀ g : M, member g e ↔ FunctionGraph x y g

theorem functionSpace_exists (h : AxiomSemantics M) (x y : M) :
    ∃ e : M, FunctionSpace e x y := by
  obtain ⟨p,hp⟩ := product_exists h x y
  obtain ⟨pp,hpp⟩ := h.powerset p
  let φ : language.Formula (Option (Fin 2)) := funcF (some 0) (some 1) none
  obtain ⟨e,he⟩ := h.separation 2 φ ![x,y] pp
  refine ⟨e,?_⟩
  intro g
  have he' : member g e ↔ member g pp ∧ FunctionGraph x y g := by
    simpa [φ,assign] using he g
  refine he'.trans ?_
  constructor
  · exact fun hg => hg.2
  · intro hg
    obtain ⟨p',hp',hgp'⟩ := hg.1
    have hpp' : p' = p := product_unique h hp' hp
    subst p'
    exact ⟨(hpp g).mpr hgp',hg⟩

theorem functionSpace_unique (h : AxiomSemantics M) {e f x y : M}
    (he : FunctionSpace e x y) (hf : FunctionSpace f x y) : e = f :=
  h.extensionality e f (fun g => (he g).trans (hf g).symm)

/-- Compile a binary formula into a predicate on Kuratowski pair codes. -/
def relationEntryF {n : ℕ} {α : Type v}
    (φ : language.Formula (Option (Option (Fin n)))) (z : α) (p : Fin n → α) :
    language.Formula α :=
  exF (exF (pairF (some (some z)) (some none) none ⊓
    applyTwo φ (some none) none (some ∘ some ∘ p)))

@[simp]
theorem relationEntryF_realize {n : ℕ} {α : Type v}
    (φ : language.Formula (Option (Option (Fin n)))) (z : α) (p : Fin n → α) (e : α → M) :
    (relationEntryF φ z p).Realize e ↔
      ∃ a b : M, IsOrderedPair (e z) a b ∧
        φ.Realize (assign (assign (e ∘ p) b) a) := by
  simp [relationEntryF, assign, Function.comp_def]

/-- Bounded relation comprehension uses an explicitly supplied formula, never an
arbitrary external relation. The resulting relation is an element of M. -/
theorem relationSet_exists (h : AxiomSemantics M) {n : ℕ}
    (φ : language.Formula (Option (Option (Fin n)))) (e : Fin n → M) (x y : M) :
    ∃ r p : M, Product p x y ∧ subset r p ∧
      ∀ a b : M, PairMember a b r ↔ member a x ∧ member b y ∧
        φ.Realize (assign (assign e b) a) := by
  obtain ⟨p,hp⟩ := product_exists h x y
  let ψ : language.Formula (Option (Fin n)) := relationEntryF φ none some
  obtain ⟨r,hr⟩ := h.separation n ψ e p
  have hr' : ∀ z : M, member z r ↔ member z p ∧
      ∃ a b : M, IsOrderedPair z a b ∧ φ.Realize (assign (assign e b) a) := by
    intro z
    simpa [ψ,assign,Function.comp_def] using hr z
  refine ⟨r,p,hp,fun z hz => ((hr' z).mp hz).1,?_⟩
  intro a b
  constructor
  · rintro ⟨z,hz,hzr⟩
    obtain ⟨hzp,c,d,hcd,hφ⟩ := (hr' z).mp hzr
    have hab := (pairMember_product_iff h hp).mp ⟨z,hz,hzp⟩
    obtain ⟨rfl,rfl⟩ := orderedPair_injective hz hcd
    exact ⟨hab.1,hab.2,hφ⟩
  · rintro ⟨ha,hb,hφ⟩
    obtain ⟨z,hz⟩ := orderedPair_exists h a b
    exact ⟨z,hz,(hr' z).mpr ⟨(hp z).mpr ⟨a,ha,b,hb,hz⟩,a,b,hz,hφ⟩⟩

end Komorebi.InternalFunctionSpaces
