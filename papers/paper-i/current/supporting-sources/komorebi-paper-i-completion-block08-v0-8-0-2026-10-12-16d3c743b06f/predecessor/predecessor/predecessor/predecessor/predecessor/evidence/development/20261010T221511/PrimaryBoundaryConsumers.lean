import PaperICompletion3
import Mathlib.Algebra.Polynomial.SpecificDegree

set_option autoImplicit false
noncomputable section

namespace PaperIBlock03Tests
open Polynomial
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion3.OperatorPrimaryAPI
open Komorebi.PaperICompletion3.InvariantFactorCount
open Komorebi.SeedRankBasics

def quadratic : ℚ[X] := X ^ 2 + C 1

theorem quadratic_degree : quadratic.natDegree = 2 := by
  exact Polynomial.natDegree_X_pow_add_C

theorem quadratic_no_rational_root (x : ℚ) : ¬ quadratic.IsRoot x := by
  intro h
  have hzero : x ^ 2 + 1 = 0 := by simpa [quadratic, Polynomial.IsRoot] using h
  nlinarith [sq_nonneg x]

theorem quadratic_irreducible : Irreducible quadratic := by
  apply Polynomial.irreducible_of_degree_le_three_of_not_isRoot
  · simp [quadratic_degree]
  · exact quadratic_no_rational_root

theorem repeated_three_labels :
    maxMultiplicity (fun _ : Fin 3 ↦ (7 : ℕ)) = 3 := by
  simp [maxMultiplicity, fiberMultiplicity, Finset.sup_const Finset.univ_nonempty]

theorem empty_labels_count_zero :
    maxMultiplicity (fun i : Fin 0 ↦ i.val) = 0 := by
  simp [maxMultiplicity]

-- Two nonlinear primary chains require two seeds, not four and not one.
theorem nonlinear_repeated_primary_minimum_two :
    IsLeast {r : ℕ | ∃ s : Fin r → ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}),
      FamilyGenerates ℚ[X] ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}) s} 2 := by
  simpa [maxMultiplicity, fiberMultiplicity, Finset.sup_const Finset.univ_nonempty] using
    primePowerProduct_seedNumber_isLeast (fun _ : Fin 2 ↦ quadratic)
      (fun _ ↦ quadratic_irreducible) (fun i : Fin 2 ↦ i.val + 1) (fun _ ↦ Nat.succ_pos _)

theorem nonlinear_repeated_primary_not_one_seed :
    ¬ ∃ s : Fin 1 → ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}),
      FamilyGenerates ℚ[X] ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}) s := by
  intro h
  have hbad : 2 ≤ 1 := nonlinear_repeated_primary_minimum_two.2 h
  omega

theorem nonlinear_single_chain_minimum_one :
    IsLeast {r : ℕ | ∃ s : Fin r → ((i : Fin 1) → ℚ[X] ⧸ Ideal.span {quadratic ^ 2}),
      FamilyGenerates ℚ[X] ((i : Fin 1) → ℚ[X] ⧸ Ideal.span {quadratic ^ 2}) s} 1 := by
  simpa [maxMultiplicity, fiberMultiplicity] using
    primePowerProduct_seedNumber_isLeast (fun _ : Fin 1 ↦ quadratic)
      (fun _ ↦ quadratic_irreducible) (fun _ : Fin 1 ↦ 2) (fun _ ↦ by decide)

theorem nonlinear_single_chain_base_dimension_four :
    Module.finrank ℚ (ℚ[X] ⧸ Ideal.span {quadratic ^ 2}) = 4 := by
  rw [finrank_quotient_span_eq_natDegree, Polynomial.natDegree_pow, quadratic_degree]

theorem nonlinear_residue_base_dimension_two :
    Module.finrank ℚ (ℚ[X] ⧸ Ideal.span {quadratic}) = 2 := by
  rw [finrank_quotient_span_eq_natDegree, quadratic_degree]

-- The positive-exponent guard cannot silently include trivial summands.
theorem exponent_zero_is_zero_module :
    Subsingleton (ℚ[X] ⧸ Ideal.span {quadratic ^ 0}) :=
  primePower_quotient_subsingleton_of_exponent_zero quadratic rfl

theorem deleting_zero_blocks_is_injective :
    Function.Injective
      (dropZeroExponentEquiv (fun _ : Fin 3 ↦ quadratic) (fun i : Fin 3 ↦ i.val)) :=
  (dropZeroExponentEquiv (fun _ : Fin 3 ↦ quadratic) (fun i : Fin 3 ↦ i.val)).injective

theorem zero_operator_on_zero_space_count_zero :
    primaryGeneratorCount (0 : Module.End ℚ (Fin 0 → ℚ)) = 0 :=
  (primaryGeneratorCount_eq_zero_iff _).mpr inferInstance

-- Labels are ideals: changing an irreducible by a unit does not split a primary fiber.
theorem associated_irreducibles_same_label :
    Ideal.span {(-quadratic)} = Ideal.span {quadratic} := by simp

theorem associated_labels_count_together :
    maxMultiplicity (fun i : Fin 2 ↦ if i = 0 then Ideal.span {quadratic}
      else Ideal.span {(-quadratic)}) = 2 := by
  simp [maxMultiplicity, fiberMultiplicity, Finset.sup_const Finset.univ_nonempty]

-- The publication's invariant-factor chain theorem includes a nonlinear example.
theorem nonlinear_invariant_factor_chain_count_two :
    IsLeast {r : ℕ | ∃ s : Fin r → ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}),
      FamilyGenerates ℚ[X] ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}) s} 2 := by
  apply invariantFactorProduct_seedNumber_isLeast
  · intro i
    rw [Polynomial.natDegree_pow, quadratic_degree]
    omega
  · intro i j hij
    exact pow_dvd_pow quadratic (Nat.succ_le_succ (Fin.le_iff_val_le_val.mp hij))

-- This cyclic criterion requires no nonzero-space assumption.
theorem chosen_zero_presentation_has_distinct_labels :
    Function.Injective (chosenPrimaryPresentation (0 : Module.End ℚ (Fin 0 → ℚ))).label := by
  apply PrimaryPresentation.label_injective_of_cyclic
  refine ⟨fun _ : Fin 1 ↦ 0, ?_⟩
  exact Subsingleton.elim _ _


-- Distinct coprime factors share one seed under the same polynomial action.
theorem coprime_distinct_factors_share_one_seed :
    FamilyGenerates ℚ[X]
      ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {if i = 0 then (X : ℚ[X]) else X - C 1})
      (coloredSeeds (fun i : Fin 2 ↦ Ideal.span {if i = 0 then (X : ℚ[X]) else X - C 1})
        (fun _ ↦ (0 : Fin 1))) := by
  apply coloredSeeds_generate
  intro i j hij _
  have hc : IsCoprime (Ideal.span {(X : ℚ[X])}) (Ideal.span {X - C 1}) := by
    apply (Ideal.isCoprime_span_singleton_iff _ _).mpr
    exact ⟨1, -1, by simp; ring⟩
  fin_cases i <;> fin_cases j <;> simp_all [IsCoprime.symm hc]

end PaperIBlock03Tests
