import PaperX.IrreducibleCharacterRigidity
import Mathlib.Data.ZMod.Basic
import Mathlib.RingTheory.RootsOfUnity.PrimitiveRoots
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.NumberTheory.Cyclotomic.Basic

/-! A generating sample that meets every rational power-conjugacy class need
not separate all absolutely irreducible characters over their splitting field.
The finite group is C3 and the samples are its identity and one generator. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.WeakCoverageBoundary

abbrev C3 := Multiplicative (ZMod 3)
def generator : C3 := Multiplicative.ofAdd 1
def sample (j : Fin 2) : C3 := if j = 0 then 1 else generator

theorem rational_power_coverage :
    ∀ g : C3, ∃ j : Fin 2, ∃ k : Fin 3,
      Nat.Coprime k.val 3 ∧ g = sample j ^ k.val := by
  decide +kernel

theorem generator_squared_missed :
    ∀ j : Fin 2, sample j ≠ generator ^ 2 := by
  decide +kernel

theorem sample_generates : Subgroup.closure (Set.range sample) = ⊤ := by
  apply top_unique
  intro g _
  obtain ⟨j, k, _, rfl⟩ := rational_power_coverage g
  exact (Subgroup.closure (Set.range sample)).pow_mem
    (Subgroup.subset_closure (Set.mem_range_self j)) k.val

/-- Both sampled classes recur at arbitrarily many distinct indices. -/
def recurringSample (p : ℕ × Fin 2) : C3 := sample p.2

theorem cofinite_rational_power_coverage (bad : Finset (ℕ × Fin 2)) (g : C3) :
    ∃ p : ℕ × Fin 2, p ∉ bad ∧ ∃ k : Fin 3,
      Nat.Coprime k.val 3 ∧ g = recurringSample p ^ k.val := by
  obtain ⟨j, k, hk, hg⟩ := rational_power_coverage g
  refine ⟨(bad.sup Prod.fst + 1, j), ?_, k, hk, hg⟩
  intro hp
  have hh := Finset.le_sup (f := Prod.fst) hp
  omega

variable {E : Type*} [Field E] (ζ : E) (hζ : IsPrimitiveRoot ζ 3)

/-- Actual scalar-valued characters on the finite cyclic group. -/
def scalarCharacter (i : Fin 3) : C3 →* E where
  toFun g := ζ ^ (i.val * g.toAdd.val)
  map_one' := by simp
  map_mul' g h := by
    change ζ ^ (i.val * ((g.toAdd + h.toAdd).val)) = _
    rw [ZMod.val_add]
    calc
      ζ ^ (i.val * ((g.toAdd.val + h.toAdd.val) % 3)) =
          (ζ ^ i.val) ^ ((g.toAdd.val + h.toAdd.val) % 3) := by rw [pow_mul]
      _ = (ζ ^ i.val) ^ (g.toAdd.val + h.toAdd.val) := by
        symm
        apply pow_eq_pow_mod
        rw [← pow_mul, Nat.mul_comm, pow_mul, hζ.pow_eq_one, one_pow]
      _ = ζ ^ (i.val * g.toAdd.val) * ζ ^ (i.val * h.toAdd.val) := by
        rw [pow_add, ← pow_mul, ← pow_mul]

/-- The actual one-dimensional representations whose traces are the characters. -/
def scalarRepresentation (i : Fin 3) : Representation E C3 E :=
  (algebraMap E (Module.End E E)).toMonoidHom.comp (scalarCharacter ζ hζ i)

theorem scalarRepresentation_irreducible (i : Fin 3) :
    (scalarRepresentation ζ hζ i).IsIrreducible := by
  change IsSimpleOrder (Subrepresentation (scalarRepresentation ζ hζ i))
  refine { exists_pair_ne := ?_, eq_bot_or_eq_top := ?_ }
  · refine ⟨⊥, ⊤, ?_⟩
    intro h
    have hh := congrArg Subrepresentation.toSubmodule h
    exact bot_ne_top hh
  · intro W
    rcases eq_bot_or_eq_top W.toSubmodule with h | h
    · exact Or.inl (Subrepresentation.toSubmodule_injective h)
    · exact Or.inr (Subrepresentation.toSubmodule_injective h)

theorem character_scalarRepresentation (i : Fin 3) (g : C3) :
    Representation.character (scalarRepresentation ζ hζ i) g =
      scalarCharacter ζ hζ i g := by
  simp [Representation.character, scalarRepresentation, Algebra.algebraMap_eq_smul_one]

theorem generator_character (i : Fin 3) :
    Representation.character (scalarRepresentation ζ hζ i) generator = ζ ^ i.val := by
  rw [character_scalarRepresentation]
  norm_num [scalarCharacter, generator, ZMod.val_one_eq_one_mod]

theorem pairwise_nonisomorphic (i j : Fin 3) (hij : i ≠ j) :
    ¬ Nonempty (Representation.Equiv
      (scalarRepresentation ζ hζ i) (scalarRepresentation ζ hζ j)) := by
  intro he
  have hc := PaperX.IrreducibleCharacterRigidity.character_eq_of_equiv
    (scalarRepresentation ζ hζ i) (scalarRepresentation ζ hζ j) he
  have hg := congrFun hc generator
  rw [generator_character, generator_character] at hg
  exact hij (Fin.ext (hζ.pow_inj i.isLt j.isLt hg))

/-- A nonzero coefficient vector annihilating all sampled trace rows. -/
def annihilator : Fin 3 → E := ![ζ ^ 2 - ζ, 1 - ζ ^ 2, ζ - 1]

include hζ in
theorem annihilator_nonzero : annihilator ζ ≠ 0 := by
  intro h
  have hh := congrFun h 2
  simp [annihilator] at hh
  exact hζ.ne_one (by decide) (sub_eq_zero.mp hh)

theorem sampled_character_relation (j : Fin 2) :
    ∑ i : Fin 3, annihilator ζ i *
      Representation.character (scalarRepresentation ζ hζ i) (sample j) = 0 := by
  fin_cases j
  · simp [sample, annihilator, Fin.sum_univ_succ]
  · simp [sample, character_scalarRepresentation, scalarCharacter, generator,
      annihilator, Fin.sum_univ_succ, ZMod.val_one_eq_one_mod]
    ring

theorem recurring_character_relation (p : ℕ × Fin 2) :
    ∑ i : Fin 3, annihilator ζ i *
      Representation.character (scalarRepresentation ζ hζ i) (recurringSample p) = 0 :=
  sampled_character_relation ζ hζ p.2

theorem every_sample_matrix_singular (p : Fin 3 → ℕ × Fin 2) :
    Matrix.det (fun j i : Fin 3 =>
      Representation.character (scalarRepresentation ζ hζ i) (recurringSample (p j))) = 0 := by
  have hn : ¬ Function.Injective (fun j : Fin 3 => (p j).2) := by
    intro hi
    have hh := Fintype.card_le_of_injective _ hi
    norm_num at hh
  obtain ⟨i, j, hij, hne⟩ := Function.not_injective_iff.mp hn
  apply Matrix.det_zero_of_row_eq hne
  simp only [recurringSample, hij]

/-- An actual number-field realization of the primitive-root hypothesis. -/
abbrev CoefficientField := CyclotomicField 3 ℚ

theorem coefficient_root_exists : ∃ z : CoefficientField, IsPrimitiveRoot z 3 := by
  let : Algebra ℚ CoefficientField := CyclotomicField.algebra 3 ℚ
  exact IsCyclotomicExtension.exists_isPrimitiveRoot ℚ CoefficientField
    (by simp : 3 ∈ ({3} : Set ℕ)) (by decide)

def coefficientRoot : CoefficientField := coefficient_root_exists.choose

theorem coefficientRoot_primitive : IsPrimitiveRoot coefficientRoot 3 :=
  coefficient_root_exists.choose_spec

/-- Three inequivalent irreducible representations over a number field, with
no invertible three-row trace matrix drawn from the recurring sample. -/
theorem actual_number_field_boundary :
    (∀ i : Fin 3,
      (scalarRepresentation coefficientRoot coefficientRoot_primitive i).IsIrreducible) ∧
    (∀ i j : Fin 3, i ≠ j → ¬ Nonempty (Representation.Equiv
      (scalarRepresentation coefficientRoot coefficientRoot_primitive i)
      (scalarRepresentation coefficientRoot coefficientRoot_primitive j))) ∧
    (∀ p : Fin 3 → ℕ × Fin 2, Matrix.det (fun j i : Fin 3 =>
      Representation.character
        (scalarRepresentation coefficientRoot coefficientRoot_primitive i)
        (recurringSample (p j))) = 0) := by
  exact ⟨scalarRepresentation_irreducible _ _, pairwise_nonisomorphic _ _,
    every_sample_matrix_singular _ _⟩

end PaperX.WeakCoverageBoundary
