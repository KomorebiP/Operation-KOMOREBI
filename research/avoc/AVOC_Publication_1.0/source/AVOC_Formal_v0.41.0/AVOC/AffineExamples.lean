import AVOC.AffineFusion
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.Notation

namespace Komorebi.AVOC.Affine.Examples

abbrev F := ZMod 5

def firstMap : Signature F 2 3 :=
  ⟨!![1,2; 0,1; 1,1], ![1,0,2]⟩

def secondMap : Signature F 3 2 :=
  ⟨!![1,0,1; 2,1,0], ![0,3]⟩

def expected : Signature F 2 2 := ⟨!![2,3; 2,0], ![3,0]⟩

def pipeline : DenseProgram F 2 2 := .seq (.atom firstMap) (.atom secondMap)

theorem pipeline_coefficients : check (coefficients pipeline) expected = true := by decide

theorem pipeline_all_inputs (x : Fin 2 → F) : execute pipeline x = eval expected x := by
  have h := (check_iff _ _).1 pipeline_coefficients x
  simpa only [coefficients_correct] using h

theorem pipeline_three_probes : checkProbes (coefficients pipeline) expected = true := by decide

theorem pipeline_costs : executionCost pipeline = 29 ∧ normalizationCost pipeline = 38 ∧
    executionCost (fuse pipeline) = 10 := by decide

theorem pipeline_three_calls : fusedLifecycle pipeline 3 = 68 ∧ baselineLifecycle pipeline 3 = 87 := by decide

def narrow : Signature F 4 1 := ⟨fun _ _ => 1, fun _ => 0⟩
def expand : Signature F 1 4 := ⟨fun _ _ => 1, fun _ => 0⟩
def bottleneck : DenseProgram F 4 4 := .seq (.atom narrow) (.atom expand)

theorem bottleneck_costs : executionCost bottleneck = 21 ∧ executionCost (fuse bottleneck) = 36 := by decide

theorem bottleneck_not_selected : chooseNoSlower bottleneck = bottleneck := by
  unfold chooseNoSlower
  have h : ¬ denseCost 4 4 ≤ executionCost bottleneck := by decide
  simp only [h, ↓reduceIte]

theorem bottleneck_never_worth (calls : Nat) : ¬ WorthFusing bottleneck calls := by
  change ¬ (44 + calls * 36 ≤ calls * 21)
  omega

def constantOne : Signature F 1 1 := ⟨0, fun _ => 1⟩

theorem basis_without_zero_insufficient :
    (∀ j : Fin 1, eval (identity 1 : Signature F 1 1) (basis j) = eval constantOne (basis j)) ∧
    eval (identity 1 : Signature F 1 1) 0 ≠ eval constantOne 0 := by decide

/-- Once nonlinear operations are allowed, basis probes are not a complete test. -/
def nonlinear (x : F) : F := x*x

theorem affine_domain_is_essential :
    nonlinear 0 = (0:F) ∧ nonlinear 1 = (1:F) ∧ nonlinear 2 ≠ (2:F) := by decide

def zeroInput : Signature F 0 2 := ⟨fun _ j => Fin.elim0 j, ![2,4]⟩

theorem zero_input_is_offset (x : Fin 0 → F) : eval zeroInput x = ![2,4] := by
  have hx : x = 0 := by funext i; exact Fin.elim0 i
  rw [hx, eval_zero]; rfl

theorem zero_output_equivalent (f g : Signature F 3 0) : ∀ x, eval f x = eval g x := by
  intro x; funext i; exact Fin.elim0 i

end Komorebi.AVOC.Affine.Examples
