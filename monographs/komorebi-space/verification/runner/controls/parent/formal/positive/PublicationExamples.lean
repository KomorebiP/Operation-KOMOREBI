import KomorebiSpace.ProtectedLinearCertificates
import KomorebiSpace.ProtectedHilbertRepair
import KomorebiSpace.FinitePrefixBoundary
import KomorebiSpace.FiniteRealizationExistence
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.FinCases

set_option autoImplicit false
open Matrix
namespace KomorebiSpace.Regression

def A : Matrix (Fin 1) (Fin 2) ℚ := !![1, 1]
def P : Matrix (Fin 1) (Fin 2) ℚ := !![1, 0]
def input : Fin 2 → ℚ := ![2, 3]
def answer : Fin 2 → ℚ := ![2, -2]

theorem explicit_protected_answer : A *ᵥ answer = 0 ∧ P *ᵥ answer = P *ᵥ input := by
  constructor <;> ext i <;> fin_cases i <;>
    norm_num [A, P, answer, input, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]

theorem exact_but_wrong_observable : A *ᵥ (![0, 0] : Fin 2 → ℚ) = 0 ∧
    P *ᵥ (![0, 0] : Fin 2 → ℚ) ≠ P *ᵥ input := by
  constructor
  · ext i; fin_cases i
    norm_num [A, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]
  · intro h
    have he := congrFun h 0
    norm_num [P, input, Matrix.mulVec, dotProduct, Fin.sum_univ_succ] at he

theorem identity_preservation_obstructed :
    ¬ ∃ y : Fin 2 → ℚ, A *ᵥ y = 0 ∧ (1 : Matrix (Fin 2) (Fin 2) ℚ) *ᵥ y =
      (1 : Matrix (Fin 2) (Fin 2) ℚ) *ᵥ input := by
  apply (ProtectedLinearCertificates.matrix_certificate_iff A 1 input).mpr
  refine ⟨![1/5], ![1/5, 1/5], ?_, ?_⟩
  · ext i; fin_cases i <;>
      norm_num [A, Matrix.vecMul, dotProduct, Fin.sum_univ_succ, Matrix.one_apply]
  · norm_num [A, input, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]

theorem empty_observable_has_distinct_answers :
    ∃ y z : Fin 2 → ℚ, y ≠ z ∧ A *ᵥ y = 0 ∧ A *ᵥ z = 0 := by
  refine ⟨![0, 0], ![1, -1], ?_, ?_, ?_⟩
  · intro h
    have he := congrFun h 0
    norm_num at he
  · ext i; fin_cases i
    norm_num [A, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]
  · ext i; fin_cases i
    norm_num [A, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]

theorem unprotected_identity_repair (x : ℝ) :
    ProtectedHilbertRepair.repair (ContinuousLinearMap.id ℝ ℝ) (0 : ℝ →L[ℝ] ℝ) x
      (⟨⟨x, by simp⟩, rfl⟩) = 0 := by
  exact ProtectedHilbertRepair.repair_exact (ContinuousLinearMap.id ℝ ℝ)
    (0 : ℝ →L[ℝ] ℝ) x _

theorem preserving_everything_can_prevent_repair :
    ¬ ProtectedHilbertRepair.Feasible (ContinuousLinearMap.id ℝ ℝ)
      (ContinuousLinearMap.id ℝ ℝ) 1 := by
  rw [ProtectedHilbertRepair.feasible_iff_answer]
  rintro ⟨y, hy, hp⟩
  change y = 0 at hy
  change y = 1 at hp
  exact zero_ne_one (hy.symm.trans hp)

def booleanTower : Resolution where
  Obj _ := Bool
  restrict _ := id
  restrict_refl _ _ := rfl
  restrict_trans _ _ _ := rfl

instance : ∀ n, Finite (booleanTower.Obj n) := fun _ => inferInstanceAs (Finite Bool)
instance : ∀ n, Nonempty (booleanTower.Obj n) := fun _ => inferInstanceAs (Nonempty Bool)

theorem finite_tower_point : Nonempty booleanTower.Point :=
  Resolution.FiniteExistence.nonempty_point booleanTower

theorem prescribed_boolean_extends (n : ℕ) (b : Bool) :
    ∃ s : booleanTower.Point, s.val n = b := by
  apply (Resolution.FiniteExistence.extension_iff_persistent booleanTower n b).mpr
  intro m h
  exact ⟨b, rfl⟩

theorem finite_prefixes_are_not_a_global_point :
    (∀ N, Nonempty (FinitePrefixBoundary.escaping.views.Partial (Resolution.prefixViews N))) ∧
    IsEmpty FinitePrefixBoundary.escaping.Point :=
  ⟨FinitePrefixBoundary.every_prefix_nonempty, FinitePrefixBoundary.no_point⟩

end KomorebiSpace.Regression
