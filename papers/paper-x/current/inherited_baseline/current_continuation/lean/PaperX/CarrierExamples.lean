import PaperX.CarrierCompatibility
import PaperX.TraceExamples
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

set_option autoImplicit false
noncomputable section
namespace PaperX.CarrierExamples
open scoped BigOperators Matrix
open Polynomial
open PaperX.CarrierSummands PaperX.CarrierPolynomials PaperX.CarrierCompatibility
open PaperX.TraceExamples

abbrev Selected := Copies (fun _ : Fin 3 => Fin 1 → ℚ) multiplicities
abbrev Ambient := Copies (fun _ : Fin 3 => Fin 1 → ℚ) capacities

def selectedRep : Representation ℚ G Selected := copiesRep rep multiplicities

def ambientRep : Representation ℚ G Ambient := copiesRep rep capacities

def embed : Selected →ₗ[ℚ] Ambient := inclusion multiplicities_admissible

def retract : Ambient →ₗ[ℚ] Selected := retraction multiplicities_admissible

theorem selected_dimension : Module.finrank ℚ Selected = 3 := by
  rw [copies_finrank]
  simp [multiplicities, Fin.sum_univ_succ]

theorem ambient_dimension : Module.finrank ℚ Ambient = 7 := by
  rw [copies_finrank]
  simp [capacities, Fin.sum_univ_succ]

theorem example_split (x : Selected) : retract (embed x) = x :=
  retraction_inclusion (R := ℚ) multiplicities_admissible x

theorem example_equivariant (g : G) (x : Selected) :
    embed (selectedRep g x) = ambientRep g (embed x) :=
  inclusion_equivariant rep multiplicities_admissible g x

theorem actual_observations :
    (fun j => LinearMap.trace ℚ _ (selectedRep (samples j))) = observed := by
  rw [show selectedRep = copiesRep rep multiplicities from rfl, sampled_trace]
  have hc : (fun j i => LinearMap.trace ℚ _ (rep i (samples j))) = separator :=
    actual_trace_matrix
  rw [hc]
  exact observed_trace

theorem constituent_charpoly (i : Fin 3) (g : G) :
    (rep i g).charpoly = X - C (chi i g) := by
  have he : rep i g = (Matrix.diagonal (fun _ : Fin 1 => chi i g)).toLin' := by
    apply LinearMap.ext
    intro x
    ext k
    simp [rep, chiHom, Matrix.toLin'_apply,
      Algebra.algebraMap_eq_smul_one]
  rw [he, Matrix.charpoly_toLin', Matrix.charpoly_diagonal]
  simp

theorem example_charpoly :
    (selectedRep (samples 2)).charpoly = (X - 1)^2 * (X + 1) := by
  rw [show selectedRep = copiesRep rep multiplicities from rfl, copies_charpoly]
  simp [constituent_charpoly, multiplicities, samples, chi, Fin.prod_univ_succ]

/-- A split pair of vector-space maps does not by itself preserve an action. -/
def swapMatrix : Matrix (Fin 2) (Fin 2) ℚ := !![0,1;1,0]
def partialInclusion : Matrix (Fin 2) (Fin 1) ℚ := fun i _ => if i = 0 then 1 else 0
def partialRetraction : Matrix (Fin 1) (Fin 2) ℚ := fun _ i => if i = 0 then 1 else 0

theorem partial_split : partialRetraction * partialInclusion = 1 := by
  ext i j
  fin_cases i; fin_cases j
  norm_num [partialRetraction, partialInclusion, Matrix.mul_apply, Fin.sum_univ_succ]

theorem swap_square : swapMatrix * swapMatrix = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [swapMatrix, Matrix.mul_apply, Fin.sum_univ_succ]

theorem compressed_swap_zero : partialRetraction * swapMatrix * partialInclusion = 0 := by
  ext i j
  fin_cases i; fin_cases j
  norm_num [partialRetraction, partialInclusion, swapMatrix, Matrix.mul_apply, Fin.sum_univ_succ]

theorem compression_fails_multiplication :
    (partialRetraction * swapMatrix * partialInclusion) *
      (partialRetraction * swapMatrix * partialInclusion) ≠
    partialRetraction * (swapMatrix * swapMatrix) * partialInclusion := by
  rw [compressed_swap_zero, swap_square, Matrix.mul_one, partial_split, Matrix.zero_mul]
  exact zero_ne_one

end PaperX.CarrierExamples
