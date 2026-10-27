import KomorebiLSM.Normed
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Data.Matrix.Basic
import Mathlib.Tactic.Ring

/-! P21: weighted least squares in a common semantic space, with the actual
Frobenius-square specialization for finite real matrices. -/
set_option autoImplicit false
open scoped BigOperators RealInnerProductSpace
namespace Komorebi.LSM.Reconciliation
variable {I : Type*} [Fintype I]

noncomputable def weightedMean {E : Type*} [AddCommGroup E] [Module ℝ E]
    (w : I → ℝ) (x : I → E) : E := ∑ i, w i • x i

noncomputable def weightedCost {E : Type*} [NormedAddCommGroup E]
    (w : I → ℝ) (x : I → E) (z : E) : ℝ := ∑ i, w i*‖z-x i‖^2

section Hilbert
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

theorem weighted_cost_expansion (w : I → ℝ) (x : I → E)
    (total : ∑ i, w i=1) (z : E) :
    weightedCost w x z = ‖z‖^2-2*⟪z,weightedMean w x⟫_ℝ+∑ i, w i*‖x i‖^2 := by
  have hinner : ⟪z,weightedMean w x⟫_ℝ=∑ i, w i*⟪z,x i⟫_ℝ := by
    simp only [weightedMean, inner_sum, real_inner_smul_right]
  rw [hinner]
  calc
    weightedCost w x z =
        (∑ i, w i)*‖z‖^2-2*(∑ i, w i*⟪z,x i⟫_ℝ)+∑ i, w i*‖x i‖^2 := by
      unfold weightedCost
      rw [Finset.sum_mul, Finset.mul_sum, ← Finset.sum_sub_distrib, ← Finset.sum_add_distrib]
      apply Finset.sum_congr rfl
      intro i _
      rw [norm_sub_sq_real]
      ring
    _ = _ := by rw [total, one_mul]

theorem weighted_variance_identity (w : I → ℝ) (x : I → E)
    (total : ∑ i, w i=1) (z : E) :
    weightedCost w x z = ‖z-weightedMean w x‖^2+weightedCost w x (weightedMean w x) := by
  rw [weighted_cost_expansion w x total z,
    weighted_cost_expansion w x total (weightedMean w x), norm_sub_sq_real,
    real_inner_self_eq_norm_sq]
  ring

theorem weighted_cost_minimum (w : I → ℝ) (x : I → E)
    (total : ∑ i, w i=1) (z : E) :
    weightedCost w x (weightedMean w x) ≤ weightedCost w x z := by
  rw [weighted_variance_identity w x total z]
  exact le_add_of_nonneg_left (sq_nonneg _)

theorem weighted_cost_eq_minimum_iff (w : I → ℝ) (x : I → E)
    (total : ∑ i, w i=1) (z : E) :
    weightedCost w x z = weightedCost w x (weightedMean w x) ↔ z=weightedMean w x := by
  rw [weighted_variance_identity w x total z]
  constructor
  · intro h
    have hn : ‖z-weightedMean w x‖^2=0 := by linarith
    exact sub_eq_zero.mp (norm_eq_zero.mp (sq_eq_zero_iff.mp hn))
  · intro h
    rw [h, sub_self, norm_zero, zero_pow (by decide : (2:ℕ) ≠ 0), zero_add]

theorem weighted_unique_minimizer (w : I → ℝ) (x : I → E)
    (total : ∑ i, w i=1) :
    ∃! z : E, ∀ y, weightedCost w x z ≤ weightedCost w x y := by
  refine ⟨weightedMean w x, weighted_cost_minimum w x total, ?_⟩
  intro z hz
  apply (weighted_cost_eq_minimum_iff w x total z).mp
  exact le_antisymm (hz _) (weighted_cost_minimum w x total z)

end Hilbert

section Normed
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

theorem weighted_mean_sub (w : I → ℝ) (x : I → E)
    (total : ∑ i, w i=1) (target : E) :
    weightedMean w x-target=∑ i, w i • (x i-target) := by
  simp only [smul_sub, Finset.sum_sub_distrib, ← Finset.sum_smul, total, one_smul, weightedMean]

theorem weighted_target_error (w : I → ℝ) (x : I → E)
    (positive : ∀ i, 0 ≤ w i) (total : ∑ i, w i=1) (target : E) :
    ‖weightedMean w x-target‖ ≤ ∑ i, w i*‖x i-target‖ := by
  rw [weighted_mean_sub w x total target]
  apply (norm_sum_le _ _).trans
  apply Finset.sum_le_sum
  intro i _
  rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg (positive i)]

end Normed

/-- Frobenius square, explicitly distinct from an induced operator norm. -/
noncomputable def frobeniusSq {J K : Type*} [Fintype J] [Fintype K]
    (A : Matrix J K ℝ) : ℝ := ∑ j, ∑ k, (A j k)^2

noncomputable def frobeniusNorm {J K : Type*} [Fintype J] [Fintype K]
    (A : Matrix J K ℝ) : ℝ := Real.sqrt (frobeniusSq A)

theorem frobeniusNorm_sq {J K : Type*} [Fintype J] [Fintype K] (A : Matrix J K ℝ) :
    frobeniusNorm A^2=frobeniusSq A := by
  apply Real.sq_sqrt
  exact Finset.sum_nonneg (fun _ _ => Finset.sum_nonneg (fun _ _ => sq_nonneg _))

theorem frobeniusSq_nonneg {J K : Type*} [Fintype J] [Fintype K] (A : Matrix J K ℝ) :
    0 ≤ frobeniusSq A :=
  Finset.sum_nonneg (fun _ _ => Finset.sum_nonneg (fun _ _ => sq_nonneg _))

theorem frobeniusSq_eq_zero_iff {J K : Type*} [Fintype J] [Fintype K] (A : Matrix J K ℝ) :
    frobeniusSq A=0 ↔ A=0 := by
  classical
  constructor
  · intro h
    ext j k
    have hj := (Finset.sum_eq_zero_iff_of_nonneg
      (fun j _ => Finset.sum_nonneg (fun k _ => sq_nonneg (A j k)))).mp h j (Finset.mem_univ j)
    have hjk := (Finset.sum_eq_zero_iff_of_nonneg (fun k _ => sq_nonneg (A j k))).mp hj k (Finset.mem_univ k)
    exact sq_eq_zero_iff.mp hjk
  · rintro rfl
    simp [frobeniusSq]

noncomputable def frobeniusCost {J K : Type*} [Fintype J] [Fintype K]
    (w : I → ℝ) (A : I → Matrix J K ℝ) (M : Matrix J K ℝ) : ℝ :=
  ∑ i, w i*frobeniusSq (M-A i)

/-- The general least-squares identity is instantiated at every matrix entry. -/
theorem frobenius_variance_identity {J K : Type*} [Fintype J] [Fintype K]
    (w : I → ℝ) (A : I → Matrix J K ℝ) (total : ∑ i, w i=1) (M : Matrix J K ℝ) :
    frobeniusCost w A M = frobeniusSq (M-weightedMean w A)+frobeniusCost w A (weightedMean w A) := by
  have hc : ∀ j k, (∑ i, w i*(M j k-A i j k)^2) =
      (M j k-weightedMean w A j k)^2+
      (∑ i, w i*(weightedMean w A j k-A i j k)^2) := by
    intro j k
    simpa only [weightedCost, weightedMean, Finset.sum_apply, Pi.smul_apply, smul_eq_mul,
      Real.norm_eq_abs, sq_abs] using
      weighted_variance_identity w (fun i => A i j k) total (M j k)
  unfold frobeniusCost frobeniusSq
  simp only [Matrix.sub_apply, Finset.mul_sum]
  rw [Finset.sum_comm]
  conv_lhs => arg 2; ext j; rw [Finset.sum_comm]
  simp_rw [hc, Finset.sum_add_distrib]
  congr 1
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  rw [Finset.sum_comm]

theorem frobenius_unique_minimizer {J K : Type*} [Fintype J] [Fintype K]
    (w : I → ℝ) (A : I → Matrix J K ℝ) (total : ∑ i, w i=1) :
    ∃! M : Matrix J K ℝ, ∀ N, frobeniusCost w A M ≤ frobeniusCost w A N := by
  have hmin : ∀ N, frobeniusCost w A (weightedMean w A) ≤ frobeniusCost w A N := by
    intro N
    rw [frobenius_variance_identity w A total N]
    exact le_add_of_nonneg_left (frobeniusSq_nonneg _)
  refine ⟨weightedMean w A,hmin,?_⟩
  intro M hM
  have hz : frobeniusSq (M-weightedMean w A)=0 := by
    have h := hM (weightedMean w A)
    rw [frobenius_variance_identity w A total M] at h
    linarith [frobeniusSq_nonneg (M-weightedMean w A)]
  exact sub_eq_zero.mp ((frobeniusSq_eq_zero_iff _).mp hz)

end Komorebi.LSM.Reconciliation
