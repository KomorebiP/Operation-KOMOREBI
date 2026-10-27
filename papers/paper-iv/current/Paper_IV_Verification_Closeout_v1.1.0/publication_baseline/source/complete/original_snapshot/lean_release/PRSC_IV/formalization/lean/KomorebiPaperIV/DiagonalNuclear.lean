/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import Mathlib.Analysis.InnerProductSpace.l2Space
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Topology.Algebra.InfiniteSum.ContinuousEval

namespace Komorebi.PaperIV
noncomputable section
open InnerProductSpace
open scoped InnerProductSpace Classical

/-- The nuclear rank-one characterization of trace class on a Hilbert space. -/
def IsHilbertTraceClass {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (T : E →L[ℂ] E) : Prop :=
  ∃ (ι : Type) (x y : ι → E), Summable (fun i => ‖x i‖ * ‖y i‖) ∧
    HasSum (fun i => rankOne ℂ (x i) (y i)) T

def diagonalHilbertBasis (ι : Type) : HilbertBasis ι ℂ (lp (fun _ : ι => ℂ) 2) :=
  HilbertBasis.ofRepr (LinearIsometryEquiv.refl ℂ _)

@[simp] theorem diagonalHilbertBasis_inner {ι : Type} (i : ι) (x : lp (fun _ : ι => ℂ) 2) :
    ⟪diagonalHilbertBasis ι i, x⟫_ℂ = x i := by
  exact ((diagonalHilbertBasis ι).repr_apply_apply x i).symm

@[simp] theorem diagonalHilbertBasis_norm {ι : Type} (i : ι) : ‖diagonalHilbertBasis ι i‖ = 1 :=
  (diagonalHilbertBasis ι).orthonormal.norm_eq_one i

@[simp] theorem diagonalHilbertBasis_apply {ι : Type} (i j : ι) :
    diagonalHilbertBasis ι i j = if j = i then 1 else 0 := by
  have h := congrArg (fun v : lp (fun _ : ι => ℂ) 2 => v j) ((diagonalHilbertBasis ι).repr_self i)
  simpa [diagonalHilbertBasis, lp.single_apply, Pi.single_apply, eq_comm] using h

def diagonalRankOne {ι : Type} (a : ι → ℂ) (i : ι) :
    lp (fun _ : ι => ℂ) 2 →L[ℂ] lp (fun _ : ι => ℂ) 2 :=
  rankOne ℂ (a i • diagonalHilbertBasis ι i) (diagonalHilbertBasis ι i)

@[simp] theorem diagonalRankOne_norm {ι : Type} (a : ι → ℂ) (i : ι) :
    ‖diagonalRankOne a i‖ = ‖a i‖ := by simp [diagonalRankOne, norm_smul]

theorem diagonalRankOne_summable {ι : Type} {a : ι → ℂ} (ha : Summable (fun i => ‖a i‖)) :
    Summable (diagonalRankOne a) := by
  apply Summable.of_norm
  simpa using ha

def diagonalOperator {ι : Type} (a : ι → ℂ) :
    lp (fun _ : ι => ℂ) 2 →L[ℂ] lp (fun _ : ι => ℂ) 2 := ∑' i, diagonalRankOne a i

theorem diagonalOperator_traceClass {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) : IsHilbertTraceClass (diagonalOperator a) := by
  refine ⟨ι, (fun i => a i • diagonalHilbertBasis ι i), diagonalHilbertBasis ι, ?_, ?_⟩
  · simpa [norm_smul] using ha
  · exact (diagonalRankOne_summable ha).hasSum

theorem diagonalOperator_apply {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (x : lp (fun _ : ι => ℂ) 2) (j : ι) :
    diagonalOperator a x j = a j * x j := by
  have hs := hasSum_apply (diagonalRankOne_summable ha).hasSum x
  have hv := hs.mapL (lp.evalCLM ℂ (fun _ : ι => ℂ) 2 j)
  have he (i : ι) : (lp.evalCLM ℂ (fun _ : ι => ℂ) 2 j) (diagonalRankOne a i x) =
      x i * (a i * (if j = i then 1 else 0)) := by
    change (diagonalRankOne a i x) j = _
    simp [diagonalRankOne, rankOne_apply, lp.coeFn_smul, diagonalHilbertBasis_apply, mul_comm]
  simp only [he] at hv
  change HasSum _ (diagonalOperator a x j) at hv
  simpa [mul_assoc, mul_comm, mul_left_comm, eq_comm] using hv.tsum_eq.symm

theorem diagonalOperator_apply_basis {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (i : ι) :
    diagonalOperator a (diagonalHilbertBasis ι i) = a i • diagonalHilbertBasis ι i := by
  ext j
  simp [diagonalOperator_apply ha, diagonalHilbertBasis_apply]
  split_ifs with h <;> simp_all

theorem diagonalOperator_pow_apply {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (m : ℕ) (x : lp (fun _ : ι => ℂ) 2) (j : ι) :
    (diagonalOperator a ^ m) x j = a j ^ m * x j := by
  induction m with
  | zero => simp
  | succ m ih =>
      rw [pow_succ']
      change diagonalOperator a ((diagonalOperator a ^ m) x) j = _
      rw [diagonalOperator_apply ha, ih, pow_succ']
      ring

end
end Komorebi.PaperIV
