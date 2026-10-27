module

public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.FinCases

/-!
Author: Komorebi P.
A scope audit of Paper VII Section 12. When the physical projector has image in
the exact common kernel, the proposed physical anomaly test vanishes identically.
This is not an operator-closure theorem or an existence theorem for a continuum tower.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVII.ConstraintAudit
open scoped BigOperators

section Algebra
variable {R I : Type*} [Ring R] [Fintype I]

/-- Scalar structure coefficients, including any factor i, may be embedded in R. -/
def anomaly (C : I → R) (f : I → R) (a b : I) : R :=
  C a * C b - C b * C a - ∑ c, f c * C c

/-- No projector axioms are needed: right annihilation alone suffices. -/
theorem anomaly_annihilates_common_kernel (C : I → R) (f : I → R)
    (P : R) (hP : ∀ c, C c * P = 0) (a b : I) :
    anomaly C f a b * P = 0 := by
  simp [anomaly, sub_mul, Finset.sum_mul, mul_assoc, hP]

theorem compressed_anomaly_zero (C : I → R) (f : I → R)
    (P : R) (hP : ∀ c, C c * P = 0) (a b : I) :
    P * anomaly C f a b * P = 0 := by
  rw [mul_assoc, anomaly_annihilates_common_kernel C f P hP, mul_zero]
end Algebra

/-- A nonzero exact physical packet, with two noncommuting Hermitian constraints
acting only on its complement. Rational matrices suffice for this counterexample. -/
def physical : Matrix (Fin 3) (Fin 3) ℚ := !![1,0,0; 0,0,0; 0,0,0]
def constraintX : Matrix (Fin 3) (Fin 3) ℚ := !![0,0,0; 0,0,1; 0,1,0]
def constraintZ : Matrix (Fin 3) (Fin 3) ℚ := !![0,0,0; 0,1,0; 0,0,-1]

theorem physical_idempotent : physical * physical = physical := by
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [physical, Matrix.mul_apply, Fin.sum_univ_succ]

theorem physical_nonzero : physical ≠ 0 := by
  intro h
  have h00 := congrArg (fun A : Matrix (Fin 3) (Fin 3) ℚ => A 0 0) h
  norm_num [physical] at h00

theorem constraints_annihilate_physical :
    constraintX * physical = 0 ∧ constraintZ * physical = 0 := by
  constructor <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    norm_num [physical, constraintX, constraintZ, Matrix.mul_apply, Fin.sum_univ_succ]

theorem commutator_nonzero : constraintX * constraintZ - constraintZ * constraintX ≠ 0 := by
  intro h
  have h12 := congrArg (fun A : Matrix (Fin 3) (Fin 3) ℚ => A 1 2) h
  norm_num [constraintX, constraintZ, Matrix.mul_apply, Fin.sum_univ_succ] at h12
  norm_num [Matrix.cons_val_two] at h12

theorem physical_commutator_zero :
    physical * (constraintX * constraintZ - constraintZ * constraintX) * physical = 0 := by
  simp only [mul_assoc, mul_sub, sub_mul, constraints_annihilate_physical.1,
    constraints_annihilate_physical.2, mul_zero, sub_self]

end KomorebiPaperVII.ConstraintAudit

/-! Exported theorem axiom audit. -/
#print axioms KomorebiPaperVII.ConstraintAudit.anomaly_annihilates_common_kernel
#print axioms KomorebiPaperVII.ConstraintAudit.compressed_anomaly_zero
#print axioms KomorebiPaperVII.ConstraintAudit.physical_idempotent
#print axioms KomorebiPaperVII.ConstraintAudit.physical_nonzero
#print axioms KomorebiPaperVII.ConstraintAudit.constraints_annihilate_physical
#print axioms KomorebiPaperVII.ConstraintAudit.commutator_nonzero
#print axioms KomorebiPaperVII.ConstraintAudit.physical_commutator_zero
