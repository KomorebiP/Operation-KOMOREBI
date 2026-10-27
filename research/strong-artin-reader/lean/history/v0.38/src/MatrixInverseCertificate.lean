import PadicMatrixNorm
import Mathlib.Data.Matrix.Basis

namespace Komorebi.StrongArtin.MatrixHensel
noncomputable section
open scoped Matrix.Norms.Elementwise
attribute [local instance] padicMatrixNormedRing padicMatrixUltra

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def tangentLinear (A : Matrix ι ι (Padic p)) (d : ℕ) :
    Matrix ι ι (Padic p) →ₗ[Padic p] Matrix ι ι (Padic p) where
  toAddHom := tangentHom A d
  map_smul' c X := by
    change tangent A d (c • X) = c • tangent A d X
    induction d with
    | zero => simp [tangent]
    | succ d ih => simp [tangent, ih, smul_add]

/-- Integral coefficient matrix, indexed by the source and target matrix entries. -/
def coefficientAction (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) :
    Matrix ι ι (Padic p) →ₗ[Padic p] Matrix ι ι (Padic p) where
  toFun X i j := ∑ t : ι × ι, (B (i,j) t : Padic p) * X t.1 t.2
  map_add' X Y := by
    ext i j
    change (∑ t : ι × ι, (B (i,j) t : Padic p) * (X t.1 t.2 + Y t.1 t.2)) =
      (∑ t : ι × ι, (B (i,j) t : Padic p) * X t.1 t.2) +
      (∑ t : ι × ι, (B (i,j) t : Padic p) * Y t.1 t.2)
    simp [mul_add, Finset.sum_add_distrib]
  map_smul' c X := by
    ext i j
    change (∑ t : ι × ι, (B (i,j) t : Padic p) * (c * X t.1 t.2)) =
      c * (∑ t : ι × ι, (B (i,j) t : Padic p) * X t.1 t.2)
    simp [Finset.mul_sum, mul_left_comm]

omit [DecidableEq ι] in
@[simp]
theorem coefficientAction_apply (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (X : Matrix ι ι (Padic p)) (i j : ι) :
    coefficientAction B X i j = ∑ t : ι × ι, (B (i,j) t : Padic p) * X t.1 t.2 := rfl

def integralAction (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (X : Matrix ι ι (PadicInt p)) : Matrix ι ι (PadicInt p) :=
  fun i j => ∑ t : ι × ι, B (i,j) t * X t.1 t.2

omit [DecidableEq ι] in
theorem coefficientAction_integral (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (X : Matrix ι ι (PadicInt p)) :
    coefficientAction B (integralMatrix X) = integralMatrix (integralAction B X) := by
  ext i j
  change (∑ t : ι × ι, (B (i,j) t : Padic p) * (X t.1 t.2 : Padic p)) =
    ((∑ t : ι × ι, B (i,j) t * X t.1 t.2 : PadicInt p) : Padic p)
  simp

theorem coefficientAction_norm (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (X : Matrix ι ι (Padic p)) : ‖coefficientAction B X‖ ≤ ‖X‖ := by
  apply (Matrix.norm_le_iff (norm_nonneg X)).mpr
  intro i j
  apply padic_sum_bound Finset.univ _ _ (norm_nonneg X)
  intro t _
  calc
    ‖(B (i,j) t : Padic p) * X t.1 t.2‖ ≤ ‖(B (i,j) t : Padic p)‖ * ‖X t.1 t.2‖ := norm_mul_le _ _
    _ ≤ 1 * ‖X‖ := mul_le_mul (B (i,j) t).property
      (Matrix.norm_entry_le_entrywise_sup_norm X) (norm_nonneg _) zero_le_one
    _ = ‖X‖ := one_mul _

def inverseLinear (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) (s : ℕ) :
    Matrix ι ι (Padic p) →ₗ[Padic p] Matrix ι ι (Padic p) :=
  ((p : Padic p)^s)⁻¹ • coefficientAction B

omit [DecidableEq ι] in
@[simp]
theorem inverseLinear_apply (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) (s : ℕ)
    (X : Matrix ι ι (Padic p)) (i j : ι) :
    inverseLinear B s X i j = ((p : Padic p)^s)⁻¹ * coefficientAction B X i j := rfl

theorem inverseLinear_norm (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) (s : ℕ)
    (X : Matrix ι ι (Padic p)) : ‖inverseLinear B s X‖ ≤ (p : ℝ)^s * ‖X‖ := by
  have hp : (0 : ℝ) ≤ p := by positivity
  calc
    ‖inverseLinear B s X‖ = (p : ℝ)^s * ‖coefficientAction B X‖ := by
      simp [inverseLinear, norm_smul]
    _ ≤ (p : ℝ)^s * ‖X‖ := mul_le_mul_of_nonneg_left (coefficientAction_norm B X) (pow_nonneg hp s)

/-- Finitely many exact identities certify a two-sided inverse. -/
def InverseCertificate (A : Matrix ι ι (Padic p)) (d s : ℕ)
    (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) : Prop :=
  ∀ i j,
    inverseLinear B s (tangent A d (Matrix.single i j 1)) = Matrix.single i j 1 ∧
    tangent A d (inverseLinear B s (Matrix.single i j 1)) = Matrix.single i j 1

theorem linear_identity_of_matrix_basis (L : Matrix ι ι (Padic p) →ₗ[Padic p] Matrix ι ι (Padic p))
    (hL : ∀ i j, L (Matrix.single i j 1) = Matrix.single i j 1) : ∀ X, L X = X := by
  intro X
  refine Matrix.induction_on' (P := fun X => L X = X) X ?_ ?_ ?_
  · exact map_zero L
  · intro X Y hX hY
    rw [map_add, hX, hY]
  · intro i j c
    have he : Matrix.single i j c = c • (Matrix.single i j (1 : Padic p)) := by
      simp [Matrix.smul_single]
    rw [he, map_smul, hL]

theorem inverseCertificate_left (A : Matrix ι ι (Padic p)) (d s : ℕ)
    (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) (hc : InverseCertificate A d s B) :
    ∀ X, inverseLinear B s (tangent A d X) = X :=
  linear_identity_of_matrix_basis ((inverseLinear B s).comp (tangentLinear A d)) (fun i j => (hc i j).1)

theorem inverseCertificate_right (A : Matrix ι ι (Padic p)) (d s : ℕ)
    (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) (hc : InverseCertificate A d s B) :
    ∀ X, tangent A d (inverseLinear B s X) = X :=
  linear_identity_of_matrix_basis ((tangentLinear A d).comp (inverseLinear B s)) (fun i j => (hc i j).2)

/-- The analytic inverse-image test is exactly one integral coefficient congruence. -/
theorem inverse_norm_iff_congruence (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (s m : ℕ) (X : Matrix ι ι (PadicInt p)) :
    ‖inverseLinear B s (integralMatrix X)‖ ≤ (p : ℝ)^(-(m : ℤ)) ↔
    (PadicInt.toZModPow (m+s)).mapMatrix (integralAction B X) = 0 := by
  have hp : (0 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).pos
  have he : (p : ℝ)^s * (p : ℝ)^(-((m+s : ℕ) : ℤ)) = (p : ℝ)^(-(m : ℤ)) := by
    rw [← zpow_natCast, ← zpow_add₀ (ne_of_gt hp)]
    congr 1
    omega
  have hn : ‖inverseLinear B s (integralMatrix X)‖ =
      (p : ℝ)^s * ‖integralMatrix (integralAction B X)‖ := by
    simp [inverseLinear, norm_smul, coefficientAction_integral]
  rw [hn, ← he, mul_le_mul_iff_right₀ (pow_pos hp s)]
  have hz : integralMatrix (0 : Matrix ι ι (PadicInt p)) = 0 := by
    ext i j
    simp [integralMatrix]
  simpa only [hz, sub_zero, map_zero] using
    (matrix_reduction_iff_norm (m+s) (integralAction B X) 0).symm

end
end Komorebi.StrongArtin.MatrixHensel
