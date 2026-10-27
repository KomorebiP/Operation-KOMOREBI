import DiagonalMatrixNormModel
import SimultaneousSpectralRestriction
import Mathlib.Algebra.Field.ZMod
import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-! Kernel-checked examples over actual dual-number matrix rings. No native_decide.
The positive cases use the general theorem, not finite root enumeration. -/
namespace Komorebi.StrongArtin.SquareZeroH2.NormExamples
open DiagonalModel
abbrev k := ZMod 3
abbrev n := Fin 2
abbrev D := datum k n

def lambda : n → kˣ := ![1,-1]
abbrev F : (Matrix n n (Dual k))ˣ := diagonalFrobenius k n lambda

def offDiagonal : D.Kernel :=
  (kernelCoordinates k n).symm (fun ij => if ij = (0,1) then 1 else 0)

def target (F0 : (Matrix n n (Dual k))ˣ) (d : ℕ) (e : D.Kernel) :=
  D.kernelUnit e * F0^d

theorem target_residue (F0 : (Matrix n n (Dual k))ˣ) (d : ℕ) (e : D.Kernel) :
    D.q (target F0 d e) = D.q (F0^d) := by
  change D.q ((D.kernelUnit e : Matrix n n (Dual k)) * (F0^d : Matrix n n (Dual k))) = _
  rw [map_mul,D.kernelUnit_residue,one_mul]

theorem target_mismatch (F0 : (Matrix n n (Dual k))ˣ) (d : ℕ) (e : D.Kernel) :
    D.unitMismatch (target F0 d e) (F0^d) (target_residue F0 d e) = e :=
  D.unitMismatch_kernel_perturbed (F0^d) e _

/-- Degree 2 is invertible in F3, but opposite eigenvalues collide after squaring. -/
theorem degree_unit_does_not_prevent_resonant_obstruction :
    (2 : k) ≠ 0 ∧
    ¬ ∃ F' : (Matrix n n (Dual k))ˣ,
      D.q F' = D.q F ∧ F'^2 = target F 2 offDiagonal := by
  refine ⟨by decide, ?_⟩
  apply (spectralModel k n lambda).no_prescribed_power_of_resonant_mismatch
    (target F 2 offDiagonal) 2 (target_residue F 2 offDiagonal) (0,1)
  · decide
  · rw [target_mismatch]
    decide

/-- A prime-degree restriction CAN lift when its mismatch is in a noninvariant mode. -/
theorem characteristic_three_offDiagonal_cube_lifts :
    ∃ F' : (Matrix n n (Dual k))ˣ,
      D.q F' = D.q F ∧ F'^3 = target F 3 offDiagonal := by
  apply ((spectralModel k n lambda).prescribed_prime_power_iff 3
    (target F 3 offDiagonal) (target_residue F 3 offDiagonal)).mpr
  rw [target_mismatch]
  decide

/-- The diagonal spectral criterion supplies an entire positive degree-5 sector. -/
theorem every_compatible_fifth_power_lifts
    (V : (Matrix n n (Dual k))ˣ) (hV : D.q V = D.q (F^5)) :
    ∃ F' : (Matrix n n (Dual k))ˣ, D.q F' = D.q F ∧ F'^5 = V := by
  apply (spectralModel k n lambda).prescribed_power_lifts_of_nonresonance 5 _ V hV
  decide

def repeatedLambda : n → kˣ := fun _ => 1
abbrev repeatedF : (Matrix n n (Dual k))ˣ := diagonalFrobenius k n repeatedLambda

/-- A repeated-eigenvalue block can obstruct although the total trace is zero. -/
theorem trace_zero_does_not_suffice_for_prime_power_lifting :
    Matrix.trace (fun i j => kernelCoordinates k n offDiagonal (i,j)) = 0 ∧
    ¬ ∃ F' : (Matrix n n (Dual k))ˣ,
      D.q F' = D.q repeatedF ∧ F'^3 = target repeatedF 3 offDiagonal := by
  refine ⟨by decide, ?_⟩
  apply (spectralModel k n repeatedLambda).no_prescribed_power_of_resonant_mismatch
    (target repeatedF 3 offDiagonal) 3
    (target_residue repeatedF 3 offDiagonal) (0,1)
  · decide
  · rw [target_mismatch]
    decide

/-- All coordinates are invariant here, so independent degree prescriptions
must arise from one common correction. -/
def familyDegree : Bool → ℕ := fun b => if b then 2 else 1
def diagonalError : D.Kernel :=
  (kernelCoordinates k n).symm (fun ij => if ij = (0,0) then 1 else 0)
def familyError : Bool → D.Kernel := fun b => if b then diagonalError else 0
def familyTarget (b : Bool) := target repeatedF (familyDegree b) (familyError b)

theorem family_residue (b : Bool) : D.q (familyTarget b) = D.q (repeatedF^familyDegree b) :=
  target_residue repeatedF _ _

/-- Each prescription individually lifts. This is insufficient for one shared Frobenius. -/
theorem each_family_prescription_lifts (b : Bool) :
    ∃ F' : (Matrix n n (Dual k))ˣ,
      D.q F' = D.q repeatedF ∧ F'^familyDegree b = familyTarget b := by
  apply (spectralModel k n repeatedLambda).prescribed_power_lifts_of_nonresonance
    (familyDegree b) _ (familyTarget b) (family_residue b)
  cases b <;> decide

theorem shared_family_matching_class_nonzero :
    D.frobeniusMatchingClass repeatedF familyDegree familyTarget family_residue ≠ 0 := by
  intro hz
  obtain ⟨_,a,ha⟩ := ((spectralModel k n repeatedLambda).matchingClass_zero_iff
    familyDegree familyTarget family_residue).mp hz
  have h0 := ha false (0,0) (by decide)
  have h1 := ha true (0,0) (by decide)
  change kernelCoordinates k n
    (D.unitMismatch (target repeatedF 1 0) (repeatedF^1) _) (0,0) = (1 : k)*a (0,0) at h0
  change kernelCoordinates k n
    (D.unitMismatch (target repeatedF 2 diagonalError) (repeatedF^2) _) (0,0) = (2 : k)*a (0,0) at h1
  rw [target_mismatch] at h0 h1
  have ha0 : a (0,0) = 0 := by simpa using h0.symm
  rw [ha0,mul_zero] at h1
  have hne : kernelCoordinates k n diagonalError (0,0) ≠ 0 := by decide
  exact hne h1

theorem individual_lifts_do_not_imply_simultaneous_local_gauge_matching :
    ¬ ∃ F' : (Matrix n n (Dual k))ˣ,
      D.q F' = D.q repeatedF ∧
      ∃ u : Bool → (Matrix n n (Dual k))ˣ,
        (∀ b, D.q (u b) = 1) ∧
        ∀ b, u b * F'^familyDegree b * (u b)⁻¹ = familyTarget b := by
  intro h
  exact shared_family_matching_class_nonzero
    ((D.simultaneous_frobenius_matching_iff_class_zero repeatedF familyDegree familyTarget
      family_residue).mp h)

end Komorebi.StrongArtin.SquareZeroH2.NormExamples
