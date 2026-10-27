import MixedCharacteristicSimultaneous
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

/-! Actual mixed-characteristic controls: Z/9 -> Z/3, not dual numbers. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic.Examples
open SquareZeroH2 NonsemisimpleNorm SimultaneousNorm
abbrev k := ZMod 3
abbrev n := Fin 2
abbrev Mat := Matrix n n k
abbrev UpperMat := Matrix n n (ZMod 9)
abbrev D := matrixDatum 3 3 (by decide) n
abbrev E := kernelCoordinates 3 3 (by decide) n (by decide)
abbrev embed := matrixKernelEmbedding 3 3 (by decide) n

def F : UpperMatˣ where
  val := !![1,1;0,1]
  inv := !![1,-1;0,1]
  val_inv := by decide
  inv_val := by decide

def baseF : Matˣ where
  val := !![1,1;0,1]
  inv := !![1,-1;0,1]
  val_inv := by decide
  inv_val := by decide

theorem residual_F : residualFrobenius 3 3 n F = baseF := by
  apply Units.ext
  decide

abbrev T : Module.End k Mat := residualAdjoint 3 3 n F

def upper : Mat := !![0,1;0,0]
def lower : Mat := !![0,0;1,0]
def diagonalError : Mat := !![1,0;0,0]

theorem nilpotent_square_apply (X : Mat) :
    ((T-1 : Module.End k Mat)^2) X = X 1 0 • upper := by
  change (T-1 : Module.End k Mat) ((T-1 : Module.End k Mat) X) = _
  simp only [LinearMap.sub_apply, Module.End.one_apply]
  simp only [T, residualAdjoint, residual_F, baseF, LinearMap.coe_mk, AddHom.coe_mk]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.vecMul, dotProduct, Fin.sum_univ_two, upper, Matrix.mul_apply]
  ring_nf
  simp [show (2 : k) = -1 by decide]

theorem nilpotent_cube_zero : (T-1)^3 = 0 := by
  apply LinearMap.ext
  intro X
  rw [pow_succ', Module.End.mul_apply, nilpotent_square_apply]
  simp only [LinearMap.sub_apply, Module.End.one_apply]
  simp only [T, residualAdjoint, residual_F, baseF, LinearMap.coe_mk, AddHom.coe_mk]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [upper]

theorem norm_three_apply (X : Mat) : operatorNorm T 3 X = X 1 0 • upper := by
  rw [operatorNorm_prime T 3]
  exact nilpotent_square_apply X

theorem norm_image_iff (e : Mat) :
    e ∈ LinearMap.range (operatorNorm T 3) ↔ ∃ a : k, e = a • upper := by
  constructor
  · rintro ⟨x,rfl⟩
    exact ⟨x 1 0,norm_three_apply x⟩
  · rintro ⟨a,rfl⟩
    refine ⟨a • lower,?_⟩
    rw [norm_three_apply]
    simp [lower,Matrix.smul_apply]

def target (e : Mat) (d : ℕ) : UpperMatˣ := D.kernelUnit (embed e) * F^d

theorem target_residue (e : Mat) (d : ℕ) : D.q (target e d) = D.q (F^d) := by
  change D.q ((D.kernelUnit (embed e) : UpperMat) * (F^d : UpperMat)) = _
  rw [map_mul,D.kernelUnit_residue,one_mul]

theorem target_mismatch (e : Mat) (d : ℕ) :
    E (D.unitMismatch (target e d) (F^d) (target_residue e d)) = e := by
  rw [show D.unitMismatch (target e d) (F^d) (target_residue e d) = embed e from
    D.unitMismatch_kernel_perturbed (F^d) (embed e) (target_residue e d)]
  exact coordinates_embedding 3 3 (by decide) n (by decide) e

/-- Exact classification of actual cubes over Z/9 for this nonsemisimple residue. -/
theorem actual_cube_lift_iff (e : Mat) :
    (∃ F' : UpperMatˣ, D.q F' = D.q F ∧ F'^3 = target e 3) ↔
      ∃ a : k, e = a • upper := by
  rw [prescribed_power_iff 3 3 (by decide) (by decide) n F (target e 3) 3
    (target_residue e 3)]
  rw [target_mismatch,norm_image_iff]

theorem nonzero_mismatch_lifts :
    ∃ F' : UpperMatˣ, D.q F' = D.q F ∧ F'^3 = target upper 3 :=
  (actual_cube_lift_iff upper).2 ⟨1,by simp⟩

theorem diagonal_mismatch_does_not_lift :
    ¬ ∃ F' : UpperMatˣ, D.q F' = D.q F ∧ F'^3 = target diagonalError 3 := by
  intro h
  obtain ⟨a,ha⟩ := (actual_cube_lift_iff diagonalError).1 h
  have := congrArg (fun X : Mat => X 0 0) ha
  norm_num [diagonalError,upper,Matrix.smul_apply] at this

/-- A literal mixed-characteristic order-three lift, not merely a kernel model. -/
def orderThreeLift : UpperMatˣ where
  val := !![1,1;6,7]
  inv := !![7,8;3,1]
  val_inv := by decide
  inv_val := by decide

theorem orderThreeLift_residue : D.q orderThreeLift = D.q F := by decide

theorem orderThreeLift_cube : orderThreeLift^3 = 1 := by apply Units.ext; decide

theorem provisional_cube_not_one : F^3 ≠ 1 := by
  intro h
  have hh := congrArg (fun u : UpperMatˣ => (u : UpperMat) 0 1) h
  change (3 : ZMod 9) = 0 at hh
  contradiction

end Komorebi.StrongArtin.MixedCharacteristic.Examples
