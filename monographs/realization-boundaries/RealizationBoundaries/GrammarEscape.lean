import RealizationBoundaries.ClassificationConsequences
import Mathlib.Data.Nat.Pairing
import Mathlib.SetTheory.Cardinal.Continuum

/-!
# Escape from an arbitrary fixed countable semantic table

The semantic table has no effectiveness assumption. Classical representatives
are chosen only for outputs isomorphic to an actual paired-prime group. The
repeated diagonal defeats eventual equality, and the independent odd blocks
retain the full space of free binary selectors.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries
attribute [local instance] Classical.propDecidable

/-- Even positions defeat a semantic output; odd positions repeat a free bit. -/
def repeatedDiagonal (B : ℕ → ℕ → Bool) (C : ℕ → Bool) (n : ℕ) : Bool :=
  if n % 2 = 0 then !(B (Nat.unpair (n / 2)).1 n)
  else C (Nat.unpair (n / 2)).1

@[simp] theorem repeatedDiagonal_even (B : ℕ → ℕ → Bool) (C : ℕ → Bool)
    (j k : ℕ) : repeatedDiagonal B C (2 * Nat.pair j k) =
      !(B j (2 * Nat.pair j k)) := by
  simp [repeatedDiagonal]

@[simp] theorem repeatedDiagonal_odd (B : ℕ → ℕ → Bool) (C : ℕ → Bool)
    (j k : ℕ) : repeatedDiagonal B C (2 * Nat.pair j k + 1) = C j := by
  have hdiv : (2 * Nat.pair j k + 1) / 2 = Nat.pair j k := by omega
  have hmod : (2 * Nat.pair j k + 1) % 2 = 1 := by omega
  simp [repeatedDiagonal, hdiv, hmod]

/-- Each semantic output is opposed at infinitely many distinct even indices. -/
theorem repeatedDiagonal_infinite_disagreement (B : ℕ → ℕ → Bool)
    (C : ℕ → Bool) (j : ℕ) :
    {n : ℕ | repeatedDiagonal B C n ≠ B j n}.Infinite := by
  have hi : Function.Injective (fun k => 2 * Nat.pair j k) := by
    intro k l h
    change 2 * Nat.pair j k = 2 * Nat.pair j l at h
    have hp : Nat.pair j k = Nat.pair j l := by omega
    exact (Nat.pair_eq_pair.mp hp).2
  apply (Set.infinite_range_of_injective hi).mono
  rintro n ⟨k, rfl⟩
  simp only [Set.mem_ofPred_eq, repeatedDiagonal_even]
  cases B j (2 * Nat.pair j k) <;> decide

/-- Different free selectors remain different modulo every finite set. -/
theorem repeatedDiagonal_free_infinite_disagreement (B : ℕ → ℕ → Bool)
    (C D : ℕ → Bool) (hCD : C ≠ D) :
    {n : ℕ | repeatedDiagonal B C n ≠ repeatedDiagonal B D n}.Infinite := by
  obtain ⟨j, hj⟩ : ∃ j, C j ≠ D j := by
    by_contra h
    apply hCD
    funext j
    by_contra hj
    exact h ⟨j, hj⟩
  have hi : Function.Injective (fun k => 2 * Nat.pair j k + 1) := by
    intro k l h
    change 2 * Nat.pair j k + 1 = 2 * Nat.pair j l + 1 at h
    have hp : Nat.pair j k = Nat.pair j l := by omega
    exact (Nat.pair_eq_pair.mp hp).2
  apply (Set.infinite_range_of_injective hi).mono
  rintro n ⟨k, rfl⟩
  simpa only [Set.mem_ofPred_eq, repeatedDiagonal_odd] using hj

universe u

/-- A family representative is selected only when the semantic output belongs
up to isomorphism to the actual paired-prime family. -/
def semanticRepresentative {Code : Type*} (R : Code → Type u)
    [∀ j, AddGroup (R j)] (j : Code) : ℕ → Bool :=
  if h : ∃ a : ℕ → Bool, Nonempty (R j ≃+ pairedGroup a)
  then h.choose else fun _ => false

theorem semanticRepresentative_spec {Code : Type*} (R : Code → Type u)
    [∀ j, AddGroup (R j)] (j : Code) (h : ∃ a : ℕ → Bool, Nonempty (R j ≃+ pairedGroup a)) :
    Nonempty (R j ≃+ pairedGroup (semanticRepresentative R j)) := by
  unfold semanticRepresentative
  rw [dite_eq_left h]
  exact h.choose_spec

/-- Selector escaping the fixed table, with an unrestricted free binary input. -/
def grammarEscapeSelector (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C : ℕ → Bool) : ℕ → Bool := repeatedDiagonal (semanticRepresentative R) C

/-- No semantic output is isomorphic to the escaped group. This includes outputs
outside the paired family; no membership test or evaluator is assumed. -/
theorem grammarEscape_not_output (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C : ℕ → Bool) (j : ℕ) :
    ¬ Nonempty (pairedGroup (grammarEscapeSelector R C) ≃+ R j) := by
  rintro ⟨e⟩
  have hex : ∃ a : ℕ → Bool, Nonempty (R j ≃+ pairedGroup a) :=
    ⟨grammarEscapeSelector R C, ⟨e.symm⟩⟩
  obtain ⟨er⟩ := semanticRepresentative_spec R j hex
  have hf := finite_disagreement_of_pairedEquiv _ _ (e.trans er)
  exact repeatedDiagonal_infinite_disagreement (semanticRepresentative R) C j hf

/-- The entire continuum of free binary inputs gives distinct group isomorphism types. -/
theorem grammarEscape_pairwise_nonisomorphic (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C D : ℕ → Bool) (hCD : C ≠ D) :
    ¬ Nonempty (pairedGroup (grammarEscapeSelector R C) ≃+
      pairedGroup (grammarEscapeSelector R D)) := by
  rw [pairedGroup_isomorphic_iff]
  exact repeatedDiagonal_free_infinite_disagreement (semanticRepresentative R) C D hCD

/-- Stronger separation: there is no embedding in either direction. -/
theorem grammarEscape_no_embedding (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C D : ℕ → Bool) (hCD : C ≠ D)
    (f : pairedGroup (grammarEscapeSelector R C) →+
      pairedGroup (grammarEscapeSelector R D)) : ¬ Function.Injective f :=
  no_injective_hom_of_infinite_disagreement _ _
    (repeatedDiagonal_free_infinite_disagreement (semanticRepresentative R) C D hCD) f

/-- Distinct free selectors yield distinct actual ambient subgroups. -/
theorem grammarEscape_groups_injective (R : ℕ → Type u) [∀ j, AddGroup (R j)] :
    Function.Injective (fun C : ℕ → Bool => pairedGroup (grammarEscapeSelector R C)) := by
  intro C D h
  by_contra hCD
  exact grammarEscape_pairwise_nonisomorphic R C D hCD
    ⟨AddEquiv.addSubgroupCongr h⟩

/-- An exact cardinal statement, paired with the stronger isomorphism separation
above: the actual escaped family has continuum many members. -/
theorem grammarEscape_family_cardinality (R : ℕ → Type u) [∀ j, AddGroup (R j)] :
    Cardinal.mk (Set.range (fun C : ℕ → Bool => pairedGroup (grammarEscapeSelector R C))) =
      Cardinal.continuum := by
  rw [Cardinal.mk_range_eq _ (grammarEscape_groups_injective R), Cardinal.mk_arrow]
  simp only [Cardinal.mk_bool, Cardinal.mk_nat, Cardinal.lift_ofNat, Cardinal.lift_aleph0]
  exact Cardinal.two_power_aleph0

/-- Every escaped group has the original common profinite completion. -/
def grammarEscape_completion (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C : ℕ → Bool) :
    ProfiniteAddGrp.ProfiniteCompletion.completion
      (AddGrpCat.of (pairedGroup (grammarEscapeSelector R C))) ≃ₜ+ Ambient :=
  pairedCompletionEquiv _

theorem grammarEscape_countably_infinite (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C : ℕ → Bool) : Countable (pairedGroup (grammarEscapeSelector R C)) ∧
      Infinite (pairedGroup (grammarEscapeSelector R C)) := paired_countably_infinite _

theorem grammarEscape_residuallyFinite (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C : ℕ → Bool) : AddGroup.ResiduallyFinite (pairedGroup (grammarEscapeSelector R C)) :=
  preimage_residuallyFinite _

/-- Reducedness is expressed by exclusion of every nonzero divisible subgroup,
not only exclusion of a rational summand. -/
theorem grammarEscape_reduced (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (C : ℕ → Bool) (E : Type*) [AddGroup E] [Nontrivial E]
    (hdiv : ∀ m : ℕ, 0 < m → ∀ x : E, ∃ y : E, m • y = x)
    (f : E →+ pairedGroup (grammarEscapeSelector R C)) : ¬ Function.Injective f := by
  intro hf
  exact not_injective_hom_of_divisible E hdiv
    ((pairedGroup (grammarEscapeSelector R C)).subtype.comp f)
    (Subtype.val_injective.comp hf)

/-- Extend representatives from an arbitrary countable code domain along an
injection into the natural-number table. Unused indices receive a dummy selector. -/
def reindexedSemanticRepresentative {Code : Type*} (R : Code → Type u)
    [∀ c, AddGroup (R c)] (index : Code → ℕ) (j : ℕ) : ℕ → Bool :=
  if h : ∃ c, index c = j then semanticRepresentative R h.choose else fun _ => false

theorem reindexedSemanticRepresentative_at {Code : Type*} (R : Code → Type u)
    [∀ c, AddGroup (R c)] (index : Code → ℕ) (hi : Function.Injective index)
    (c : Code) : reindexedSemanticRepresentative R index (index c) =
      semanticRepresentative R c := by
  have h : ∃ d, index d = index c := ⟨c, rfl⟩
  unfold reindexedSemanticRepresentative
  rw [dite_eq_left h, hi h.choose_spec]

/-- Countability alone supplies the code injection. There is no computability
assumption on syntax validity, the index, evaluation or family membership. -/
def countableDescriptionIndex (Code : Type*) [Countable Code] : Code → ℕ :=
  (Countable.exists_injective_nat Code).choose

theorem countableDescriptionIndex_injective (Code : Type*) [Countable Code] :
    Function.Injective (countableDescriptionIndex Code) :=
  (Countable.exists_injective_nat Code).choose_spec

def countableGrammarEscapeSelector {Code : Type*} [Countable Code]
    (R : Code → Type u) [∀ c, AddGroup (R c)] (C : ℕ → Bool) : ℕ → Bool :=
  repeatedDiagonal (reindexedSemanticRepresentative R (countableDescriptionIndex Code)) C

theorem countableGrammarEscape_not_output {Code : Type*} [Countable Code]
    (R : Code → Type u) [∀ c, AddGroup (R c)] (C : ℕ → Bool) (c : Code) :
    ¬ Nonempty (pairedGroup (countableGrammarEscapeSelector R C) ≃+ R c) := by
  rintro ⟨e⟩
  have hex : ∃ a : ℕ → Bool, Nonempty (R c ≃+ pairedGroup a) :=
    ⟨countableGrammarEscapeSelector R C, ⟨e.symm⟩⟩
  obtain ⟨er⟩ := semanticRepresentative_spec R c hex
  have hf := finite_disagreement_of_pairedEquiv _ _ (e.trans er)
  have hi := repeatedDiagonal_infinite_disagreement
    (reindexedSemanticRepresentative R (countableDescriptionIndex Code)) C
    (countableDescriptionIndex Code c)
  rw [reindexedSemanticRepresentative_at R (countableDescriptionIndex Code)
    (countableDescriptionIndex_injective Code) c] at hi
  exact hi hf

theorem countableGrammarEscape_free_infinite_disagreement {Code : Type*} [Countable Code]
    (R : Code → Type u) [∀ c, AddGroup (R c)] (C D : ℕ → Bool) (hCD : C ≠ D) :
    {n : ℕ | countableGrammarEscapeSelector R C n ≠
      countableGrammarEscapeSelector R D n}.Infinite :=
  repeatedDiagonal_free_infinite_disagreement _ C D hCD

theorem countableGrammarEscape_pairwise_nonisomorphic {Code : Type*} [Countable Code]
    (R : Code → Type u) [∀ c, AddGroup (R c)] (C D : ℕ → Bool) (hCD : C ≠ D) :
    ¬ Nonempty (pairedGroup (countableGrammarEscapeSelector R C) ≃+
      pairedGroup (countableGrammarEscapeSelector R D)) := by
  rw [pairedGroup_isomorphic_iff]
  exact countableGrammarEscape_free_infinite_disagreement R C D hCD

theorem countableGrammarEscape_no_embedding {Code : Type*} [Countable Code]
    (R : Code → Type u) [∀ c, AddGroup (R c)] (C D : ℕ → Bool) (hCD : C ≠ D)
    (f : pairedGroup (countableGrammarEscapeSelector R C) →+
      pairedGroup (countableGrammarEscapeSelector R D)) : ¬ Function.Injective f :=
  no_injective_hom_of_infinite_disagreement _ _
    (countableGrammarEscape_free_infinite_disagreement R C D hCD) f

theorem countableGrammarEscape_family_cardinality {Code : Type*} [Countable Code]
    (R : Code → Type u) [∀ c, AddGroup (R c)] :
    Cardinal.mk (Set.range (fun C : ℕ → Bool =>
      pairedGroup (countableGrammarEscapeSelector R C))) = Cardinal.continuum := by
  have hi : Function.Injective (fun C : ℕ → Bool =>
      pairedGroup (countableGrammarEscapeSelector R C)) := by
    intro C D h
    by_contra hCD
    exact countableGrammarEscape_pairwise_nonisomorphic R C D hCD
      ⟨AddEquiv.addSubgroupCongr h⟩
  rw [Cardinal.mk_range_eq _ hi, Cardinal.mk_arrow]
  simp only [Cardinal.mk_bool, Cardinal.mk_nat, Cardinal.lift_ofNat, Cardinal.lift_aleph0]
  exact Cardinal.two_power_aleph0

/-- The exact semantic/length interface for admissible grammar expansion.
Validity and group isomorphism semantics can both be included in `denotes`. -/
structure DescriptionGrammar (Code : Type*) (Object : Type*) where
  denotes : Code → Object → Prop
  length : Code → ℕ

namespace DescriptionGrammar
variable {Code Object : Type*}

def Realizes (G : DescriptionGrammar Code Object) (x : Object) : Prop :=
  ∃ d, G.denotes d x

private theorem exists_length (G : DescriptionGrammar Code Object) (x : Object)
    (h : G.Realizes x) : ∃ n, ∃ d, G.denotes d x ∧ G.length d = n := by
  obtain ⟨d, hd⟩ := h
  exact ⟨G.length d, d, hd, rfl⟩

/-- Exact shortest length, used only when a description exists. -/
def shortestLength (G : DescriptionGrammar Code Object) (x : Object)
    (h : G.Realizes x) : ℕ := Nat.find (exists_length G x h)

theorem shortestLength_spec (G : DescriptionGrammar Code Object) (x : Object)
    (h : G.Realizes x) : ∃ d, G.denotes d x ∧ G.length d = G.shortestLength x h :=
  Nat.find_spec (exists_length G x h)

theorem shortestLength_le (G : DescriptionGrammar Code Object) (x : Object)
    (h : G.Realizes x) (d : Code) (hd : G.denotes d x) :
    G.shortestLength x h ≤ G.length d :=
  Nat.find_min' (exists_length G x h) ⟨d, hd, rfl⟩

/-- Description complexity is infinite exactly when no valid description exists. -/
def complexity (G : DescriptionGrammar Code Object) (x : Object) : WithTop ℕ :=
  if h : G.Realizes x then (G.shortestLength x h : WithTop ℕ) else ⊤

theorem complexity_eq_top_iff (G : DescriptionGrammar Code Object) (x : Object) :
    G.complexity x = ⊤ ↔ ¬ G.Realizes x := by
  by_cases h : G.Realizes x <;> simp [complexity, h]

variable {OtherCode : Type*}

/-- Monograph 10.2: semantic translation preserves realizability. -/
theorem admissible_expansion (G : DescriptionGrammar Code Object)
    (H : DescriptionGrammar OtherCode Object) (translate : Code → OtherCode)
    (preserves : ∀ d x, G.denotes d x → H.denotes (translate d) x)
    (x : Object) : G.Realizes x → H.Realizes x := by
  rintro ⟨d, hd⟩
  exact ⟨translate d, preserves d x hd⟩

/-- Translate a shortest valid description; no monotonicity of the overhead
function is required because this is the actual shortest source witness. -/
theorem admissible_expansion_length (G : DescriptionGrammar Code Object)
    (H : DescriptionGrammar OtherCode Object) (translate : Code → OtherCode)
    (preserves : ∀ d x, G.denotes d x → H.denotes (translate d) x)
    (f : ℕ → ℕ)
    (length_bound : ∀ d x, G.denotes d x → H.length (translate d) ≤ f (G.length d))
    (x : Object) (h : G.Realizes x) :
    H.shortestLength x (admissible_expansion G H translate preserves x h) ≤
      f (G.shortestLength x h) := by
  obtain ⟨d, hd, hlen⟩ := G.shortestLength_spec x h
  exact (H.shortestLength_le x _ (translate d) (preserves d x hd)).trans
    ((length_bound d x hd).trans_eq (congrArg f hlen))

/-- The finite source-complexity version of the printed complexity inequality. -/
theorem admissible_expansion_complexity (G : DescriptionGrammar Code Object)
    (H : DescriptionGrammar OtherCode Object) (translate : Code → OtherCode)
    (preserves : ∀ d x, G.denotes d x → H.denotes (translate d) x)
    (f : ℕ → ℕ)
    (length_bound : ∀ d x, G.denotes d x → H.length (translate d) ≤ f (G.length d))
    (x : Object) (h : G.Realizes x) :
    H.complexity x ≤ (f (G.shortestLength x h) : WithTop ℕ) := by
  have hH := admissible_expansion G H translate preserves x h
  rw [complexity, dite_eq_left hH]
  exact_mod_cast admissible_expansion_length G H translate preserves f length_bound x h

end DescriptionGrammar

/-- The fixed countable table interpreted as a genuine isomorphism semantics.
The length function is arbitrary; invalid descriptions can be assigned a dummy output. -/
def semanticDescriptionGrammar (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (length : ℕ → ℕ) : DescriptionGrammar ℕ (AddSubgroup Ambient) where
  denotes j H := Nonempty (H ≃+ R j)
  length := length

/-- Every escaped group has infinite description complexity in the fixed grammar. -/
theorem grammarEscape_complexity_infinite (R : ℕ → Type u) [∀ j, AddGroup (R j)]
    (length : ℕ → ℕ) (C : ℕ → Bool) :
    (semanticDescriptionGrammar R length).complexity
      (pairedGroup (grammarEscapeSelector R C)) = ⊤ := by
  rw [DescriptionGrammar.complexity_eq_top_iff]
  rintro ⟨j, hj⟩
  exact grammarEscape_not_output R C j hj

end RealizationBoundaries
