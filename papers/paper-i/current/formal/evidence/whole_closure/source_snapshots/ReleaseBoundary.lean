import PaperIRelease
import PaperICompletion8.SemisimpleExistence
import Mathlib.Algebra.Quaternion
import Mathlib.Algebra.TrivSqZeroExt.Basic

set_option autoImplicit false

namespace PaperIBlock08Tests
attribute [local instance] RingHomInvPair.of_ringEquiv
open scoped BigOperators DirectSum
open Komorebi.SeedRankBasics Komorebi.SeedRankOperations
open Komorebi.PaperICompletion8.DivisionRows
open Komorebi.PaperICompletion8.DivisionBlock
open Komorebi.PaperICompletion8.DivisionProduct
open Komorebi.PaperICompletion8.RegularMultiplicity
open Komorebi.PaperICompletion8.SemisimpleFormula
open Komorebi.PaperICompletion8.SemisimpleExistence

abbrev H := Quaternion ℚ
def qi : H := ⟨0, 1, 0, 0⟩
def qj : H := ⟨0, 0, 1, 0⟩

theorem quaternion_noncommutes : qi * qj ≠ qj * qi := by
  intro h
  have hh := congrArg (fun q : H ↦ q.imK) h
  norm_num [qi, qj, Quaternion.imK_mul] at hh

theorem quaternion_three_copies_rank_two :
    seedRank (Matrix (Fin 2) (Fin 2) H) (Fin 3 → Fin 2 → H) = 2 := by
  simpa [Nat.ceilDiv_eq_add_pred_div] using naturalCopies_seedRank (D := H) 2 3 (by decide)

theorem quaternion_five_copies_rank_three :
    seedRank (Matrix (Fin 2) (Fin 2) H) (Fin 5 → Fin 2 → H) = 3 := by
  simpa [Nat.ceilDiv_eq_add_pred_div] using naturalCopies_seedRank (D := H) 2 5 (by decide)

theorem quaternion_direct_sum_rank_two :
    seedRank (Matrix (Fin 2) (Fin 2) H) (⨁ _ : Fin 3, (Fin 2 → H)) = 2 := by
  simpa [Nat.ceilDiv_eq_add_pred_div] using naturalDirectSum_seedRank (D := H) 2 3 (by decide)

theorem quaternion_one_seed_insufficient
    (v : Fin 1 → Matrix (Fin 2) (Fin 3) H) : ¬ LeftGenerates v := by
  intro h
  have hb := multiplicity_le_of_leftGenerates (by decide : 0 < 2) h
  omega

theorem quaternion_two_seeds_exist :
    ∃ v : Fin 2 → Matrix (Fin 2) (Fin 3) H, LeftGenerates v :=
  exists_leftGenerators_of_le (by decide) (by decide)

theorem quaternion_regular_multiplicity_one :
    seedRank (Matrix (Fin 2) (Fin 2) H) (Fin 2 → Fin 2 → H) = 1 := by
  simpa [Nat.ceilDiv_eq_add_pred_div] using naturalCopies_seedRank (D := H) 2 2 (by decide)

theorem quaternion_zero_multiplicity :
    seedRank (Matrix (Fin 2) (Fin 2) H) (Fin 0 → Fin 2 → H) = 0 := by
  simpa [Nat.ceilDiv_eq_add_pred_div] using naturalCopies_seedRank (D := H) 2 0 (by decide)

theorem quaternion_natural_rank_one :
    seedRank (Matrix (Fin 2) (Fin 2) H) (Fin 2 → H) = 1 :=
  natural_seedRank_eq_one (by decide)

theorem quaternion_every_nonzero_is_cyclic (x : Fin 2 → H) (hx : x ≠ 0) :
    Generates (Matrix (Fin 2) (Fin 2) H) (Fin 2 → H) {x} := natural_nonzero_generates hx

def MixedD : Bool → Type := fun b ↦ if b then ℚ else H
noncomputable instance mixedDivision (b : Bool) : DivisionRing (MixedD b) := by
  cases b <;> dsimp [MixedD] <;> infer_instance

def dims : Bool → ℕ := fun b ↦ if b then 1 else 2
def mults : Bool → ℕ := fun b ↦ if b then 1 else 3

private theorem dims_pos (b : Bool) : 0 < dims b := by cases b <;> decide
private theorem mixed_count : maxCeilDiv dims mults = 2 := by decide

/-- This product genuinely has different division rings in its two factors. -/
theorem mixed_product_rank_max_not_sum :
    seedRank (DivisionProductAlgebra (D := MixedD) dims)
      (MultiplicityModule (D := MixedD) dims mults) = 2 := by
  rw [multiplicity_seedRank dims mults dims_pos, mixed_count]
  norm_num

theorem mixed_product_not_three :
    seedRank (DivisionProductAlgebra (D := MixedD) dims)
      (MultiplicityModule (D := MixedD) dims mults) ≠ 3 := by
  rw [mixed_product_rank_max_not_sum]
  norm_num

theorem mixed_direct_sum_rank :
    seedRank (DivisionProductAlgebra (D := MixedD) dims)
      (⨁ b : Bool, (Fin (mults b) → Simple (D := MixedD) dims b)) = 2 := by
  rw [directSum_seedRank dims mults dims_pos, mixed_count]
  norm_num

theorem regular_columns_literal (a : DivisionProductAlgebra (D := MixedD) dims)
    (b : Bool) (j i : Fin (dims b)) : regularColumnsEquiv dims a b j i = a b i j := rfl

theorem regular_columns_intertwines
    (a x : DivisionProductAlgebra (D := MixedD) dims) :
    regularColumnsEquiv dims (a * x) = a • regularColumnsEquiv dims x :=
  (regularColumnsEquiv (D := MixedD) dims).map_smul a x

theorem regular_direct_sum_roundtrip
    (a : DivisionProductAlgebra (D := MixedD) dims) :
    (regularDirectSumEquiv dims).symm (regularDirectSumEquiv dims a) = a :=
  (regularDirectSumEquiv dims).symm_apply_apply a

theorem wrong_factor_acts_zero
    (a : Matrix (Fin (dims true)) (Fin (dims true)) (MixedD true))
    (x : Simple (D := MixedD) dims false) :
    (Pi.single true a : DivisionProductAlgebra (D := MixedD) dims) • x = 0 :=
  other_factor_smul_zero dims false true (by decide) a x

theorem mixed_natural_is_simple :
    IsSimpleModule (DivisionProductAlgebra (D := MixedD) dims)
      (Simple (D := MixedD) dims false) := simple_isSimple dims false (by decide)

theorem absent_factor_contributes_zero :
    seedRank (DivisionProductAlgebra (D := MixedD) dims)
      (MultiplicityModule (D := MixedD) dims (fun b ↦ if b then 0 else 3)) = 2 := by
  rw [multiplicity_seedRank dims _ dims_pos]
  have h : maxCeilDiv dims (fun b ↦ if b then 0 else 3) = 2 := by decide
  rw [h]
  norm_num

theorem empty_product_rank_zero :
    seedRank (DivisionProductAlgebra (D := fun _ : Fin 0 ↦ H) (fun _ ↦ 1))
      (MultiplicityModule (D := fun _ : Fin 0 ↦ H) (fun _ ↦ 1) (fun _ ↦ 7)) = 0 := by
  rw [multiplicity_seedRank _ _ (fun _ ↦ by decide)]
  simp [maxCeilDiv]

/-- Without d>0 all rectangular targets vanish even when the row-space bound fails. -/
theorem zero_matrix_size_breaks_unguarded_bound :
    (∃ v : Fin 0 → Matrix (Fin 0) (Fin 1) H, LeftGenerates v) ∧ ¬ (1 ≤ 0 * 0) := by
  constructor
  · refine ⟨fun i ↦ Fin.elim0 i, ?_⟩
    intro X
    refine ⟨fun i ↦ Fin.elim0 i, ?_⟩
    exact Subsingleton.elim _ _
  · decide

/-- The coefficient is on the correct side of the quaternion coordinate. -/
theorem right_division_coefficient (a b : H) (hb : b ≠ 0) : (a / b) * b = a :=
  div_mul_cancel₀ a hb

/-- The abstract construction is applied with no supplied module decomposition. -/
theorem abstract_quaternion_presentation :
    ∃ m : Bool → ℕ, Nonempty
      (DivisionProductAlgebra (D := MixedD) dims ≃ₗ[DivisionProductAlgebra (D := MixedD) dims]
        MultiplicityModule (D := MixedD) dims m) :=
  Komorebi.PaperICompletion8.ProductPresentation.exists_multiplicity_presentation
    dims (DivisionProductAlgebra (D := MixedD) dims) dims_pos


/-- Reversing a coefficient fails in an actual quaternion calculation. -/
theorem reversed_quaternion_coefficient_fails : (-qi * qj) * qi ≠ qj := by
  intro h
  have hh := congrArg (fun q : H ↦ q.imJ) h
  norm_num [qi, qj, Quaternion.imJ_mul, Quaternion.re_mul,
    Quaternion.imI_mul, Quaternion.imK_mul] at hh

abbrev DH := TrivSqZeroExt H H

def dualLinearEquiv : (H × H) ≃ₗ[ℚ] DH where
  toFun x := ⟨x.1, x.2⟩
  invFun x := (x.fst, x.snd)
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

instance dualFinite : Module.Finite ℚ DH :=
  Module.Finite.of_surjective dualLinearEquiv.toLinearMap dualLinearEquiv.surjective


/-- The public finite-algebra theorem constructs both decompositions for a
noncommutative square-zero extension, not merely for an already split ring. -/
theorem nonsplit_finite_algebra_api :
    ∃ (q : ℕ) (D : Fin q → Type) (d m : Fin q → ℕ) (_ : ∀ i, DivisionRing (D i)),
      (∀ i, 0 < d i) ∧
      ∃ eR : (DH ⧸ Ring.jacobson DH) ≃+* DivisionProductAlgebra (D := D) d,
        Nonempty (Komorebi.PaperICompletion7.ModuleTop.RadicalTop DH DH
          ≃ₛₗ[(RingHomClass.toRingHom eR)]
            (⨁ i : Fin q, (Fin (m i) → Simple (D := D) d i))) ∧
        seedRank DH DH = (maxCeilDiv d m : Cardinal) :=
  exists_finiteAlgebra_seed_formula DH DH ℚ

end PaperIBlock08Tests
