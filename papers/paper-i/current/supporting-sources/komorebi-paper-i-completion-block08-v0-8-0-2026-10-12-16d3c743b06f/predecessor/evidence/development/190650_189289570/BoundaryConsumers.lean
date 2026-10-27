import PaperICompletion7.LocalResidue
import Mathlib.Algebra.TrivSqZeroExt.Basic
import Mathlib.Algebra.Quaternion
import Mathlib.RingTheory.PowerSeries.Inverse
import Mathlib.RingTheory.Localization.FractionRing

set_option autoImplicit false

namespace PaperIBlock07Tests
open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion7.Nakayama
open Komorebi.PaperICompletion7.ModuleTop
open Komorebi.PaperICompletion7.LocalResidue

abbrev H := Quaternion ℚ
abbrev DH := TrivSqZeroExt H H

noncomputable instance : IsLocalRing H :=
  IsLocalRing.of_isUnit_or_isUnit_one_sub_self fun a ↦ by
    by_cases h : a = 0
    · exact Or.inr (by simp [h])
    · exact Or.inl (isUnit_iff_ne_zero.mpr h)

noncomputable instance : IsLocalRing DH :=
  IsLocalRing.of_isUnit_or_isUnit_of_isUnit_add fun a b h ↦ by
    have h' : IsUnit (a.fst + b.fst) :=
      TrivSqZeroExt.isUnit_iff_isUnit_fst.mp h
    exact (IsLocalRing.isUnit_or_isUnit_of_isUnit_add h').imp
      TrivSqZeroExt.isUnit_iff_isUnit_fst.mpr TrivSqZeroExt.isUnit_iff_isUnit_fst.mpr

def dhFst : DH →+* H where
  toFun := TrivSqZeroExt.fst
  map_zero' := rfl
  map_one' := rfl
  map_add' := fun _ _ ↦ rfl
  map_mul' := TrivSqZeroExt.fst_mul

private theorem dhFst_surj : Function.Surjective dhFst :=
  TrivSqZeroExt.fst_surjective

/-- The test ring's radical is the literal nonzero square-zero coordinate ideal. -/
theorem dual_quaternion_radical : Ring.jacobson DH = RingHom.ker dhFst :=
  maximal_left_ideal_unique _ _ jacobson_isMaximal
    (RingHom.ker_isMaximal_of_surjective dhFst dhFst_surj)

def epsilon : DH := TrivSqZeroExt.inr 1

theorem epsilon_nonzero : epsilon ≠ 0 := by
  intro h
  have he := congrArg TrivSqZeroExt.snd h
  exact one_ne_zero he

theorem epsilon_square_zero : epsilon * epsilon = 0 :=
  TrivSqZeroExt.inr_mul_inr H 1 1

theorem epsilon_in_radical : epsilon ∈ Ring.jacobson DH := by
  rw [dual_quaternion_radical]
  rfl

def qi : H := ⟨0, 1, 0, 0⟩
def qj : H := ⟨0, 0, 1, 0⟩

theorem quaternion_noncommutes : qi * qj ≠ qj * qi := by
  intro h
  have hh := congrArg Quaternion.imK h
  norm_num [qi, qj, Quaternion.imK_mul] at hh

theorem dual_quaternion_noncommutes :
    (TrivSqZeroExt.inl qi : DH) * TrivSqZeroExt.inl qj ≠
      (TrivSqZeroExt.inl qj : DH) * TrivSqZeroExt.inl qi := by
  intro h
  apply quaternion_noncommutes
  exact congrArg TrivSqZeroExt.fst h

theorem dual_quaternion_actual_kernel :
    LinearMap.ker (idealTopMap (M := DH) (Ring.jacobson DH)) =
      Ring.jacobson DH • (⊤ : Submodule DH DH) := idealTopMap_ker _

theorem dual_quaternion_quotient_action (a x : DH) :
    idealTopMap (Ring.jacobson DH) (a * x) =
      Ideal.Quotient.mk (Ring.jacobson DH) a • idealTopMap (Ring.jacobson DH) x := rfl

theorem dual_quaternion_seed_rank_one : seedRank DH DH = 1 := by
  apply (seedRank_eq_one_iff_cyclic DH DH).mpr
  exact ⟨1, by simp [Generates, ← Ideal.submodule_span_eq, Ideal.span_singleton_one]⟩

theorem dual_quaternion_residue_dimension_one :
    letI := residueDivisionRing DH
    Module.rank (DH ⧸ Ring.jacobson DH) (RadicalTop DH DH) = 1 := by
  let := residueDivisionRing DH
  rw [← seedRank_eq_residue_dimension]
  exact dual_quaternion_seed_rank_one

theorem nontrivial_radical_lift_generates : Generates DH DH {1 + epsilon} := by
  apply (image_generates_iff (Ring.jacobson DH) le_rfl _).mp
  have he : idealTopMap (M := DH) (Ring.jacobson DH) epsilon = 0 := by
    apply Submodule.Quotient.mk_eq_zero _ |>.mpr
    simpa using Submodule.smul_mem_smul epsilon_in_radical
      (show (1 : DH) ∈ (⊤ : Submodule DH DH) from trivial)
  have hset : idealTopMap (M := DH) (Ring.jacobson DH) '' {1 + epsilon} =
      idealTopMap (M := DH) (Ring.jacobson DH) '' {1} := by
    simp only [Set.image_singleton, map_add, he, add_zero]
  rw [hset]
  apply (image_generates_iff (Ring.jacobson DH) le_rfl _).mpr
  simp [Generates, ← Ideal.submodule_span_eq, Ideal.span_singleton_one]

/-- The zero module remains a zero-dimensional top, not a rank-one convention. -/
theorem zero_space_top_rank (R : Type*) [Ring R] :
    seedRank (R ⧸ Ring.jacobson R) (RadicalTop R (Fin 0 → R)) = 0 := by
  rw [← seedRank_eq_radicalTop]
  exact (seedRank_eq_zero_iff R (Fin 0 → R)).mpr inferInstance

end PaperIBlock07Tests
