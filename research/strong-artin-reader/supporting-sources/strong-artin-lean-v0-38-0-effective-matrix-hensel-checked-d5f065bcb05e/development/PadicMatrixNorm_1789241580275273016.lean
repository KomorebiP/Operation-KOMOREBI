import NCPowerEstimates
import Mathlib.Analysis.Matrix.Normed
import Mathlib.NumberTheory.Padics.RingHoms

namespace Komorebi.StrongArtin.MatrixHensel
noncomputable section
open scoped Matrix.Norms.Elementwise

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem padic_sum_bound {κ : Type*} (s : Finset κ) (f : κ → Padic p)
    (r : ℝ) (hr : 0 ≤ r) (hf : ∀ i ∈ s, ‖f i‖ ≤ r) : ‖∑ i ∈ s, f i‖ ≤ r := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using hr
  | @insert i s hi ih =>
    rw [Finset.sum_insert hi]
    apply norm_add_bound (hf i (Finset.mem_insert_self _ _))
    exact ih (fun j hj => hf j (Finset.mem_insert_of_mem hj))

omit [DecidableEq ι] in
theorem padic_matrix_mul_bound (A B : Matrix ι ι (Padic p)) : ‖A*B‖ ≤ ‖A‖ * ‖B‖ := by
  apply (Matrix.norm_le_iff (mul_nonneg (norm_nonneg A) (norm_nonneg B))).mpr
  intro i j
  apply padic_sum_bound Finset.univ (fun k => A i k * B k j) _
    (mul_nonneg (norm_nonneg A) (norm_nonneg B))
  intro k _
  exact (norm_mul_le _ _).trans (mul_le_mul
    (Matrix.norm_entry_le_entrywise_sup_norm A) (Matrix.norm_entry_le_entrywise_sup_norm B)
    (norm_nonneg _) (norm_nonneg _))

/-- The entrywise supremum norm is submultiplicative over the p-adic field. -/
@[instance_reducible]
def padicMatrixNormedRing : NormedRing (Matrix ι ι (Padic p)) :=
  { (inferInstance : Ring (Matrix ι ι (Padic p))), Matrix.normedAddCommGroup with
    norm_mul_le := padic_matrix_mul_bound }

attribute [local instance] padicMatrixNormedRing

@[instance_reducible]
def padicMatrixUltra : IsUltrametricDist (Matrix ι ι (Padic p)) :=
  IsUltrametricDist.isUltrametricDist_of_forall_norm_add_le_max_norm (by
    intro A B
    apply (Matrix.norm_le_iff (le_max_of_le_left (norm_nonneg A))).mpr
    intro i j
    exact (norm_ultra_add (A i j) (B i j)).trans (max_le_max
      (Matrix.norm_entry_le_entrywise_sup_norm A) (Matrix.norm_entry_le_entrywise_sup_norm B)))

attribute [local instance] padicMatrixUltra

def integralMatrix (A : Matrix ι ι (PadicInt p)) : Matrix ι ι (Padic p) :=
  A.map (fun x => (x : Padic p))

theorem integralMatrix_norm_le (A : Matrix ι ι (PadicInt p)) : ‖integralMatrix A‖ ≤ 1 := by
  apply (Matrix.norm_le_iff zero_le_one).mpr
  intro i j
  exact (A i j).property

omit [Fintype ι] [DecidableEq ι] in
theorem integralMatrix_injective : Function.Injective
    (integralMatrix : Matrix ι ι (PadicInt p) → Matrix ι ι (Padic p)) := by
  intro A B h
  ext i j
  apply Subtype.ext
  exact congrFun (congrFun h i) j

theorem matrix_reduction_iff_norm (m : ℕ) (A B : Matrix ι ι (PadicInt p)) :
    (PadicInt.toZModPow m).mapMatrix A = (PadicInt.toZModPow m).mapMatrix B ↔
      ‖integralMatrix A - integralMatrix B‖ ≤ (p : ℝ) ^ (-(m : ℤ)) := by
  have hp : (0 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).pos
  rw [Matrix.norm_le_iff (zpow_pos hp _).le, Matrix.ext_iff]
  apply forall_congr'
  intro i
  apply forall_congr'
  intro j
  change PadicInt.toZModPow m (A i j) = PadicInt.toZModPow m (B i j) ↔
    ‖(A i j : Padic p) - (B i j : Padic p)‖ ≤ _
  rw [← PadicInt.coe_sub, PadicInt.padic_norm_e_of_padicInt,
    PadicInt.norm_le_pow_iff_mem_span_pow, ← PadicInt.ker_toZModPow,
    RingHom.mem_ker, map_sub, sub_eq_zero]

theorem integralMatrix_pow (A : Matrix ι ι (PadicInt p)) (d : ℕ) :
    integralMatrix (A^d) = (integralMatrix A)^d := by
  exact map_pow (PadicInt.Coe.ringHom.mapMatrix) A d

end Komorebi.StrongArtin.MatrixHensel
