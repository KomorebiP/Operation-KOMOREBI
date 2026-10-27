import RealizationBoundaries.TailSignature

/-!
# Unmarked and marked classification of the paired-prime groups

The unmarked invariant is eventual equality of selectors. Finite changes give
literal equality of the ambient subgroups. Homomorphism root preservation is
used directly; no coordinate diagonality is assumed.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- At a differing bit, the source's chosen prime is the target's omitted prime. -/
theorem chosenIndex_eq_omittedIndex_of_ne (a b : ℕ → Bool) (n : ℕ)
    (h : a n ≠ b n) : chosenIndex a n = omittedIndex b n := by
  cases ha : a n <;> cases hb : b n <;> simp_all [chosenIndex, omittedIndex]

/-- Membership of one selector's chosen prime in another reads equality of that bit. -/
theorem chosen_mem_other_iff (a b : ℕ → Bool) (n : ℕ) :
    primeAt (chosenIndex a n) ∈ pairedSelector b ↔ a n = b n := by
  constructor
  · intro hm
    by_contra h
    rw [chosenIndex_eq_omittedIndex_of_ne a b n h] at hm
    exact omitted_not_mem b n hm
  · intro h
    have hi : chosenIndex a n = chosenIndex b n := by simp [chosenIndex, h]
    rw [hi]
    exact chosen_mem b n

/-- One-sided tail containment is enough for paired selectors: one prime is chosen
from each pair, so a genuine mismatch violates the containment in one coordinate. -/
theorem finite_bit_disagreement_of_tail_inclusion (a b : ℕ → Bool)
    (E : Set Prime) (hE : E.Finite)
    (h : ∀ p ∉ E, p ∈ pairedSelector b → p ∈ pairedSelector a) :
    {n : ℕ | a n ≠ b n}.Finite := by
  have hi : Function.Injective (fun n => primeAt (chosenIndex b n)) :=
    primeAt_injective.comp (chosenIndex_injective b)
  apply (hE.preimage hi.injOn).subset
  intro n hn
  change primeAt (chosenIndex b n) ∈ E
  by_contra hp
  have hm := h _ hp (chosen_mem b n)
  exact hn ((chosen_mem_other_iff b a n).mp hm).symm

/-- A finite change in bits changes only finitely many prime coordinates. -/
theorem pairedSelectors_agree_off_finite (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) :
    ∃ E : Set Prime, E.Finite ∧
      ∀ p ∉ E, (p ∈ pairedSelector a ↔ p ∈ pairedSelector b) := by
  let E := (fun n => primeAt (chosenIndex a n)) '' {n | a n ≠ b n} ∪
    (fun n => primeAt (chosenIndex b n)) '' {n | a n ≠ b n}
  refine ⟨E, (h.image _).union (h.image _), ?_⟩
  intro p hp
  constructor
  · rintro ⟨n, rfl⟩
    apply (chosen_mem_other_iff a b n).mpr
    by_contra hn
    exact hp (Or.inl ⟨n, hn, rfl⟩)
  · rintro ⟨n, rfl⟩
    apply (chosen_mem_other_iff b a n).mpr
    by_contra hn
    exact hp (Or.inr ⟨n, Ne.symm hn, rfl⟩)

/-- Finite changes in a selector leave its actual quotient line and preimage unchanged. -/
theorem selectorGroup_eq_of_agree_off (S T : Set Prime) (E : Set Prime)
    (hE : E.Finite) (h : ∀ p ∉ E, (p ∈ S ↔ p ∈ T)) :
    selectorGroup S = selectorGroup T := by
  classical
  have hd : indicator S - indicator T ∈ finiteSupport := by
    apply hE.subset
    intro p hp
    by_contra he
    have hh := h p he
    apply hp
    change indicator S p - indicator T p = 0
    simp [indicator, hh]
  have hq := (quotientMap_eq_iff (indicator S) (indicator T)).mpr hd
  unfold selectorGroup selectorLine
  rw [hq]

/-- The converse classification is literal subgroup equality, not merely isomorphism. -/
theorem pairedGroup_eq_of_finite_disagreement (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) : pairedGroup a = pairedGroup b := by
  obtain ⟨E, hE, he⟩ := pairedSelectors_agree_off_finite a b h
  exact selectorGroup_eq_of_agree_off _ _ E hE he

/-- An explicitly constructed isomorphism that leaves the underlying ambient point unchanged. -/
def pairedEquivOfFiniteDisagreement (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) : pairedGroup a ≃+ pairedGroup b :=
  AddEquiv.addSubgroupCongr (pairedGroup_eq_of_finite_disagreement a b h)

@[simp] theorem pairedEquivOfFiniteDisagreement_val (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (x : pairedGroup a) :
    (pairedEquivOfFiniteDisagreement a b h x).val = x.val :=
  AddEquiv.addSubgroupCongr_apply _ x


#check pairedEquivOfFiniteDisagreement_val
end RealizationBoundaries
