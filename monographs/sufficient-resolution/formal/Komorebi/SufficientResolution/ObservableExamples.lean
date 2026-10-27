import Komorebi.SufficientResolution.FiniteCertificate
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum

/-! Exact two-operation example: noncommuting dynamics, one irrelevant state,
and a certificate-built two-dimensional minimal observation model. -/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.ObservableExamples

open Behavioral FiniteObservableModel FiniteCertificate Module

abbrev Fine := ℚ × ℚ × ℚ
abbrev Small := ℚ × ℚ

/-- Transfers the second visible coordinate to the first. -/
def stepA : Fine →ₗ[ℚ] Fine where
  toFun x := (x.2.1, 0, x.2.2)
  map_add' := by intro x y; simp
  map_smul' := by intro a x; simp

/-- Transfers the first visible coordinate to the second. -/
def stepB : Fine →ₗ[ℚ] Fine where
  toFun x := (0, x.1, x.2.2)
  map_add' := by intro x y; simp
  map_smul' := by intro a x; simp

def operations (i : Bool) : Fine →ₗ[ℚ] Fine := if i then stepB else stepA

def readout : Fine →ₗ[ℚ] ℚ where
  toFun x := x.1
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

def reduce : Fine →ₗ[ℚ] Small where
  toFun x := (x.1, x.2.1)
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

def smallA : Small →ₗ[ℚ] Small where
  toFun x := (x.2, 0)
  map_add' := by intro x y; simp
  map_smul' := by intro a x; simp

def smallB : Small →ₗ[ℚ] Small where
  toFun x := (0, x.1)
  map_add' := by intro x y; simp
  map_smul' := by intro a x; simp

def smallOperations (i : Bool) : Small →ₗ[ℚ] Small := if i then smallB else smallA

def smallReadout : Small →ₗ[ℚ] ℚ where
  toFun x := x.1
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

def nowIndex : ObservationIndex Bool 1 := ⟨[], by simp [mem_wordsUpTo]⟩
def nextAIndex : ObservationIndex Bool 1 := ⟨[false], by simp [mem_wordsUpTo]⟩

/-- The two coordinates are observations of the empty word and the word A. -/
def generate : (ObservationIndex Bool 1 → ℚ) →ₗ[ℚ] Small where
  toFun f := (f nowIndex, f nextAIndex)
  map_add' := by intro x y; rfl
  map_smul' := by intro a x; rfl

def exactCertificate : Certificate operations readout reduce 1 where
  generation := generate
  generated := by apply LinearMap.ext; intro x; rfl
  dynamics := smallOperations
  output := smallReadout
  intertwine := by intro i; cases i <;> apply LinearMap.ext <;> intro x <;> rfl
  output_exact := by apply LinearMap.ext; intro x; rfl

 theorem reduce_surjective : Function.Surjective reduce := by
  intro z
  exact ⟨(z.1, z.2, 0), rfl⟩

 theorem invisible_exact : invisible operations readout = LinearMap.ker reduce :=
  (certificate_kernel_eq exactCertificate).symm

 theorem invisible_coordinates (x : Fine) :
    x ∈ invisible operations readout ↔ x.1 = 0 ∧ x.2.1 = 0 := by
  rw [invisible_exact]
  change (x.1, x.2.1) = (0, 0) ↔ _
  simp only [Prod.mk.injEq]

 theorem smallest_dimension : finrank ℚ (State operations readout) = 2 := by
  rw [← (certificateEquiv exactCertificate reduce_surjective).finrank_eq]
  simp [Small, Module.finrank_prod]

 theorem operations_do_not_commute : stepA * stepB ≠ stepB * stepA := by
  intro h
  have he := congrArg (fun f : Fine →ₗ[ℚ] Fine => (f (1, 0, 0)).1) h
  norm_num [stepA, stepB, Module.End.mul_apply] at he

 theorem hidden_coordinate_irrelevant (x y h h' : ℚ) (w : List Bool) :
    readout (wordOp operations w (x, y, h)) =
      readout (wordOp operations w (x, y, h')) := by
  exact (certificate_same_future_iff exactCertificate (x, y, h) (x, y, h')).mp rfl w

 theorem current_observation_misses_distinction : readout (0, 1, 0) = readout (0, 0, 0) := rfl

 theorem one_step_detects_distinction :
    readout (wordOp operations [false] (0, 1, 0)) ≠
      readout (wordOp operations [false] (0, 0, 0)) := by
  norm_num [wordOp, operations, stepA, readout, Module.End.mul_apply]

end Komorebi.SufficientResolution.ObservableExamples
