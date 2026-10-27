import Komorebi.Foundation.ZFCModelSemantics

/-!
# ZFSet satisfies the explicit first-order ZFC axiom theory

This is a theorem in Lean's surrounding type theory. In particular it is not
an internal ZFC proof of its own consistency. Both schemas are proved uniformly
for every formula and every finite tuple of parameters.
-/

universe u

namespace Komorebi.ZFSetZFCModel

open FirstOrder FirstOrder.Language
open MembershipFormula GeneralMembershipSemantics ZFCAxiomSyntax ZFCModelSemantics
open SetFilterCoding (Carrier element element_mem element_injective exists_element)

@[simp]
theorem isSingleton_zfset (s x : ZFSet.{u}) : IsSingleton s x ↔ s = {x} := by
  simp [IsSingleton, ZFSet.ext_iff]

@[simp]
theorem isPair_zfset (p x y : ZFSet.{u}) : IsPair p x y ↔ p = {x, y} := by
  simp [IsPair, ZFSet.ext_iff]

@[simp]
theorem isOrderedPair_zfset (p x y : ZFSet.{u}) :
    IsOrderedPair p x y ↔ p = ZFSet.pair x y := by
  simp [IsOrderedPair, ZFSet.pair]

@[simp]
theorem pairMember_zfset (x y g : ZFSet.{u}) :
    PairMember x y g ↔ ZFSet.pair x y ∈ g := by
  simp [PairMember]

/-- The graph is itself a set, not an external function substituted into syntax. -/
theorem choiceGraph_exists (X : ZFSet.{u})
    (h : ∀ a : ZFSet.{u}, a ∈ X → ∃ b : ZFSet.{u}, b ∈ a) :
    ∃ g : ZFSet.{u}, IsChoiceGraph X g := by
  classical
  have ht : ∀ i : Carrier X, ∃ b : ZFSet.{u}, b ∈ element X i :=
    fun i => h (element X i) (element_mem X i)
  choose f hf using ht
  let g := ZFSet.range (fun i : Carrier X => ZFSet.pair (element X i) (f i))
  refine ⟨g, ?_, ?_⟩
  · intro p hp
    obtain ⟨i, rfl⟩ := ZFSet.mem_range.mp hp
    exact ⟨element X i, element_mem X i, f i, hf i, (isOrderedPair_zfset _ _ _).mpr rfl⟩
  · intro a ha
    obtain ⟨i, rfl⟩ := exists_element X ha
    refine ⟨f i, hf i, ?_, ?_⟩
    · exact (pairMember_zfset _ _ _).mpr (ZFSet.mem_range_self i)
    · intro c hc
      obtain ⟨j, hj⟩ := ZFSet.mem_range.mp ((pairMember_zfset _ _ _).mp hc)
      obtain ⟨he, hv⟩ := ZFSet.pair_inj.mp hj
      have hi : j = i := element_injective X he
      subst j
      exact hv.symm

/-- Uniform Separation, including all free parameter assignments. -/
theorem separation_zfset (n : ℕ) (φ : language.Formula (Option (Fin n)))
    (e : Fin n → ZFSet.{u}) : SeparationInstance φ e := by
  intro a
  refine ⟨ZFSet.sep (fun x => φ.Realize (assign e x)) a, ?_⟩
  intro x
  simpa only [member_zfset] using
    (ZFSet.mem_sep (x := a) (y := x) (p := fun z => φ.Realize (assign e z)))

/-- Uniform exact Replacement. The chosen image is indexed by a genuinely small
carrier of a, so its range is a ZFSet; unique outputs give the reverse inclusion. -/
theorem replacement_zfset (n : ℕ)
    (φ : language.Formula (Option (Option (Fin n)))) (e : Fin n → ZFSet.{u}) :
    ReplacementInstance φ e := by
  classical
  intro a h
  have ht : ∀ i : Carrier a, ∃ y : ZFSet.{u},
      φ.Realize (assign (assign e y) (element a i)) :=
    fun i => (h (element a i) (element_mem a i)).exists
  choose f hf using ht
  refine ⟨ZFSet.range f, ?_⟩
  intro y
  rw [member_zfset, ZFSet.mem_range]
  constructor
  · rintro ⟨i, rfl⟩
    exact ⟨element a i, element_mem a i, hf i⟩
  · rintro ⟨x, hx, hxy⟩
    obtain ⟨i, rfl⟩ := exists_element a hx
    have he : y = f i := (h (element a i) (element_mem a i)).unique hxy (hf i)
    exact ⟨i, he.symm⟩

/-- All meanings are established from the concrete ZFSet construction. -/
theorem zfset_axiomSemantics : AxiomSemantics ZFSet.{u} := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, separation_zfset, replacement_zfset⟩
  · intro x y h
    exact ZFSet.ext h
  · exact ⟨∅, fun z => ZFSet.notMem_empty z⟩
  · intro x y
    exact ⟨{x, y}, (isPair_zfset _ _ _).mpr rfl⟩
  · intro x
    exact ⟨ZFSet.sUnion x, fun z => ZFSet.mem_sUnion⟩
  · intro x
    exact ⟨ZFSet.powerset x, fun z => ZFSet.mem_powerset⟩
  · refine ⟨ZFSet.omega, ⟨∅, fun z => ZFSet.notMem_empty z, ZFSet.omega_zero⟩, ?_⟩
    intro x hx
    refine ⟨insert x x, ?_, ZFSet.omega_succ hx⟩
    intro z
    exact ZFSet.mem_insert_iff
  · intro x hx
    have hn : x ≠ ∅ := by
      rintro rfl
      obtain ⟨a, ha⟩ := hx
      exact ZFSet.notMem_empty a ha
    obtain ⟨y, hy, hi⟩ := ZFSet.regularity x hn
    refine ⟨y, hy, ?_⟩
    intro z hz
    have hz' : z ∈ x ∩ y := ZFSet.mem_inter.mpr hz
    rw [hi] at hz'
    exact ZFSet.notMem_empty z hz'
  · exact choiceGraph_exists

/-- Every fixed axiom and every instance of both schemas is satisfied. -/
theorem zfset_models_zfc : ZFSet.{u} ⊨ zfcTheory :=
  model_zfc_iff_axiomSemantics.mpr zfset_axiomSemantics

end Komorebi.ZFSetZFCModel
