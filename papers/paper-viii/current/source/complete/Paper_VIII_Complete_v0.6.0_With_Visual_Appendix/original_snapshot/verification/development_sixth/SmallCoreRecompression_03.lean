module
public import SpectralOptimality
public import FrobeniusOptimality
public import CompactTruncation
public import SmallCoreTransfer
import all SmallCoreNorms
import all CompactRangeFactors
import all SmallCoreTransfer
import all KernelFrame
import all DiagonalTruncation
import all SpectralOptimality
import all FrobeniusOptimality
import all CompactTruncation
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VIII, Theorem 5.6.
An ordered thin SVD is supplied by its algebraic equations, exactly as in the
manuscript's phrase "let G = W Sigma Z* be an SVD". No best-approximation,
singular-value tail, rank, norm invariance, or ambient optimality is assumed.
The construction of compact column bases is independent of this SVD datum.
These are exact finite matrices, not a floating-point QR or SVD implementation. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {m n r s t : Type*} [Fintype m] [Fintype n] [Fintype r] [Fintype s] [Fintype t]
  [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] [DecidableEq t]
  {d : ℕ}

structure OrderedThinSVD (G : Matrix r s ℂ) (d : ℕ) where
  left : Matrix r (Fin d) ℂ
  right : Matrix s (Fin d) ℂ
  values : Fin d → ℝ
  left_isometry : leftᴴ*left=1
  right_isometry : rightᴴ*right=1
  nonnegative : ∀ i, 0 ≤ values i
  sorted : Antitone values
  reconstruction : G=lift left right (diag values)

omit [DecidableEq m] in
theorem isometry_comp (Q : Matrix m r ℂ) (W : Matrix r (Fin d) ℂ)
    (hQ : Qᴴ*Q=1) (hW : Wᴴ*W=1) : (Q*W)ᴴ*(Q*W)=1 := by
  simp only [Matrix.conjTranspose_mul,Matrix.mul_assoc]
  rw [←Matrix.mul_assoc Qᴴ Q W,hQ,Matrix.one_mul,hW]

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]
    [DecidableEq r] [DecidableEq s] in
theorem lift_comp (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (W : Matrix r (Fin d) ℂ) (Z : Matrix s (Fin d) ℂ)
    (D : Matrix (Fin d) (Fin d) ℂ) :
    lift Q V (lift W Z D)=lift (Q*W) (V*Z) D := by
  simp only [lift,Matrix.conjTranspose_mul,Matrix.mul_assoc]

omit [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
noncomputable def recompressLeft (Q : Matrix m r ℂ) {G : Matrix r s ℂ}
    (svd : OrderedThinSVD G d) (k : ℕ) : Matrix m (KeptColumn d k) ℂ :=
  Q*svd.left*rootMask svd.values k

omit [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
noncomputable def recompressRight (V : Matrix n s ℂ) {G : Matrix r s ℂ}
    (svd : OrderedThinSVD G d) (k : ℕ) : Matrix n (KeptColumn d k) ℂ :=
  V*svd.right*rootMask svd.values k

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
theorem recompressed_product (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    {G : Matrix r s ℂ} (svd : OrderedThinSVD G d) (k : ℕ) :
    recompressLeft Q svd k * (recompressRight V svd k)ᴴ =
      lift (Q*svd.left) (V*svd.right) (diag (kept svd.values k)) := by
  exact thin_factor_product _ _ _ svd.nonnegative k

/-- The core's singular-vector equations are derived from the SVD equations. -/
theorem core_gram_eigenvectors {G : Matrix r s ℂ} (svd : OrderedThinSVD G d) :
    Gᴴ*G*svd.right = svd.right*diag (fun i => svd.values i ^ 2) := by
  have hself : (diag svd.values)ᴴ = diag svd.values := by
    simp [diag,Matrix.diagonal_conjTranspose]
  have hsquare : diag svd.values*diag svd.values = diag (fun i => svd.values i^2) := by
    simp only [diag,Matrix.diagonal_mul_diagonal]
    congr 1
    funext i
    simp [pow_two]
  calc
    Gᴴ*G*svd.right = (lift svd.left svd.right (diag svd.values))ᴴ *
        lift svd.left svd.right (diag svd.values) * svd.right :=
      congrArg (fun X : Matrix r s ℂ => Xᴴ*X*svd.right) svd.reconstruction
    _ = _ := by
      simp only [lift,Matrix.conjTranspose_mul,Matrix.conjTranspose_conjTranspose,hself,Matrix.mul_assoc]
      rw [←Matrix.mul_assoc svd.leftᴴ svd.left _,svd.left_isometry,Matrix.one_mul]
      rw [svd.right_isometry,Matrix.mul_one,hsquare]

/-- Both global optimality inequalities and exact errors, against arbitrary ambient competitors. -/
theorem recompression_optimality (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) {G : Matrix r s ℂ}
    (svd : OrderedThinSVD G d) (k : ℕ) :
    let A := lift Q V G
    let B := recompressLeft Q svd k * (recompressRight V svd k)ᴴ
    BestRank spectralNorm A B k ∧ BestRank frobeniusNorm A B k ∧
    spectralNorm (A-B)=nextSingular svd.values k ∧
    frobeniusNorm (A-B)^2=tailEnergy svd.values k ∧
    frobeniusNorm (A-B)=Real.sqrt (tailEnergy svd.values k) := by
  dsimp only
  have hG : lift Q V G=lift (Q*svd.left) (V*svd.right) (diag svd.values) :=
    (congrArg (lift Q V) svd.reconstruction).trans (lift_comp Q V _ _ _)
  rw [recompressed_product,hG]
  have hU := isometry_comp Q svd.left hQ svd.left_isometry
  have hZ := isometry_comp V svd.right hV svd.right_isometry
  have hs := spectral_best_lift (Q*svd.left) (V*svd.right) hU hZ _ _ k
    (diagonal_spectral_best svd.values svd.nonnegative svd.sorted k)
  have hf := frobenius_best_lift (Q*svd.left) (V*svd.right) hU hZ _ _ k
    (diagonal_frobenius_best svd.values svd.nonnegative svd.sorted k)
  refine ⟨hs,hf,?_,?_,?_⟩
  · rw [←lift_sub,spectral_lift _ _ hU hZ,diagonal_residual]
    exact spectral_diagonal_tail _ svd.nonnegative svd.sorted k
  · rw [←lift_sub,frobenius_lift _ _ hU hZ,diagonal_residual]
    exact frobenius_diagonal_tail _ k
  · rw [←lift_sub,frobenius_lift _ _ hU hZ,diagonal_residual]
    rw [←frobenius_diagonal_tail svd.values k,Real.sqrt_sq_eq_abs]
    have hn : 0 ≤ frobeniusNorm (diag (discarded svd.values k)) := by
      unfold frobeniusNorm
      exact norm_nonneg _
    exact (abs_of_nonneg hn).symm

/-- Theorem 5.6 with independently constructed compact factors of the original inputs.
The output has min(d,k) columns, including k=0 and zero-rank factors. -/
theorem small_core_optimal_recompression (L : Matrix m t ℂ) (R : Matrix n t ℂ)
    (svd : OrderedThinSVD (factorCore L R) d) (k : ℕ) :
    let Lk := recompressLeft (compactQ L) svd k
    let Rk := recompressRight (compactQ R) svd k
    BestRank spectralNorm (L*Rᴴ) (Lk*Rkᴴ) k ∧
    BestRank frobeniusNorm (L*Rᴴ) (Lk*Rkᴴ) k ∧
    spectralNorm (L*Rᴴ-Lk*Rkᴴ)=nextSingular svd.values k ∧
    frobeniusNorm (L*Rᴴ-Lk*Rkᴴ)^2=tailEnergy svd.values k ∧
    frobeniusNorm (L*Rᴴ-Lk*Rkᴴ)=Real.sqrt (tailEnergy svd.values k) ∧
    compactDim L=L.rank ∧ compactDim R=R.rank ∧
    Fintype.card (KeptColumn d k)=min d k := by
  dsimp only
  have h := recompression_optimality (compactQ L) (compactQ R)
    (compactQ_isometry L) (compactQ_isometry R) svd k
  dsimp only at h
  rw [←compact_product_reconstruction L R] at h
  exact ⟨h.1,h.2.1,h.2.2.1,h.2.2.2.1,h.2.2.2.2,
    compactDim_eq_rank L,compactDim_eq_rank R,keptColumn_card k⟩

end KomorebiPaperVIII.SmallCore
