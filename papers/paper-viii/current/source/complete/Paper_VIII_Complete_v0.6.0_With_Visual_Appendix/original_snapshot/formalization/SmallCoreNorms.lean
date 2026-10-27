module
public import Mathlib.Analysis.CStarAlgebra.Matrix
public import Mathlib.LinearAlgebra.Matrix.Rank
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.Tactic

/-! Author: Komorebi P. Rectangular isometric embedding and compression.
All norms and ranks below are the actual matrix norms and rank.
No optimality or norm-preservation hypotheses are used. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {m n r s : Type*} [Fintype m] [Fintype n] [Fintype r] [Fintype s]
  [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s]

/-- Embed a small matrix into the ambient row and column spaces. -/
def lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ) (G : Matrix r s ℂ) : Matrix m n ℂ :=
  Q * G * Vᴴ
/-- Compress an arbitrary ambient competitor into the small core. -/
def compress (Q : Matrix m r ℂ) (V : Matrix n s ℂ) (B : Matrix m n ℂ) : Matrix r s ℂ :=
  Qᴴ * B * V

omit [DecidableEq m] [DecidableEq n] in
theorem compress_lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G : Matrix r s ℂ) :
    compress Q V (lift Q V G) = G := by
  simp only [compress,lift,←Matrix.mul_assoc]
  rw [hQ,Matrix.one_mul]
  simp only [Matrix.mul_assoc,hV,Matrix.mul_one]

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
theorem lift_sub (Q : Matrix m r ℂ) (V : Matrix n s ℂ) (G H : Matrix r s ℂ) :
    lift Q V (G-H) = lift Q V G - lift Q V H := by
  simp only [lift,Matrix.mul_sub,Matrix.sub_mul]

omit [Fintype r] [Fintype s] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
theorem compress_sub (Q : Matrix m r ℂ) (V : Matrix n s ℂ) (A B : Matrix m n ℂ) :
    compress Q V (A-B) = compress Q V A - compress Q V B := by
  simp only [compress,Matrix.mul_sub,Matrix.sub_mul]

omit [Fintype r] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
theorem rank_compress_le (Q : Matrix m r ℂ) (V : Matrix n s ℂ) (B : Matrix m n ℂ) :
    (compress Q V B).rank ≤ B.rank :=
  (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)

omit [Fintype m] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] in
theorem rank_lift_le (Q : Matrix m r ℂ) (V : Matrix n s ℂ) (G : Matrix r s ℂ) :
    (lift Q V G).rank ≤ G.rank :=
  (Matrix.rank_mul_le_left _ _).trans (Matrix.rank_mul_le_right _ _)

omit [DecidableEq m] [DecidableEq n] in
theorem rank_lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G : Matrix r s ℂ) :
    (lift Q V G).rank = G.rank := by
  apply le_antisymm (rank_lift_le Q V G)
  simpa only [compress_lift Q V hQ hV] using rank_compress_le Q V (lift Q V G)

section Operator
open scoped Matrix.Norms.L2Operator
noncomputable def spectralNorm (A : Matrix m n ℂ) : ℝ := ‖A‖

omit [DecidableEq m] in
theorem spectral_left_isometry (Q : Matrix m r ℂ) (hQ : Qᴴ*Q=1)
    (G : Matrix r s ℂ) : ‖Q*G‖ = ‖G‖ := by
  have he : (Q*G)ᴴ*(Q*G) = Gᴴ*G := by
    simp only [Matrix.conjTranspose_mul,Matrix.mul_assoc]
    rw [←Matrix.mul_assoc Qᴴ Q G,hQ,Matrix.one_mul]
  have hn := congrArg (fun A : Matrix s s ℂ => ‖A‖) he
  simp only [Matrix.l2_opNorm_conjTranspose_mul_self] at hn
  nlinarith [norm_nonneg (Q*G),norm_nonneg G]

theorem spectral_right_isometry (V : Matrix n s ℂ) (hV : Vᴴ*V=1)
    (G : Matrix r s ℂ) : ‖G*Vᴴ‖ = ‖G‖ := by
  calc
    ‖G*Vᴴ‖ = ‖(G*Vᴴ)ᴴ‖ := (Matrix.l2_opNorm_conjTranspose _).symm
    _ = ‖V*Gᴴ‖ := by simp only [Matrix.conjTranspose_mul,Matrix.conjTranspose_conjTranspose]
    _ = ‖Gᴴ‖ := spectral_left_isometry V hV Gᴴ
    _ = ‖G‖ := Matrix.l2_opNorm_conjTranspose _

omit [DecidableEq m] in
theorem spectral_isometry_bound (Q : Matrix m r ℂ) (hQ : Qᴴ*Q=1) : ‖Q‖ ≤ 1 := by
  have hn := Matrix.l2_opNorm_conjTranspose_mul_self Q
  rw [hQ] at hn
  have h1 : ‖(1 : Matrix r r ℂ)‖ ≤ 1 := by
    rw [←Matrix.diagonal_one,Matrix.l2_opNorm_diagonal]
    exact (pi_norm_le_iff_of_nonneg zero_le_one).mpr (fun i => by simp)
  nlinarith [norm_nonneg Q]

theorem spectral_lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G : Matrix r s ℂ) :
    spectralNorm (lift Q V G) = spectralNorm G := by
  unfold spectralNorm lift
  rw [spectral_right_isometry V hV,spectral_left_isometry Q hQ]

theorem spectral_compress_le (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (B : Matrix m n ℂ) :
    spectralNorm (compress Q V B) ≤ spectralNorm B := by
  unfold spectralNorm compress
  calc
    ‖Qᴴ*B*V‖ ≤ ‖Qᴴ*B‖*‖V‖ := Matrix.l2_opNorm_mul _ _
    _ ≤ (‖Qᴴ‖*‖B‖)*‖V‖ := mul_le_mul_of_nonneg_right (Matrix.l2_opNorm_mul _ _) (norm_nonneg _)
    _ ≤ (1*‖B‖)*1 := by
      apply mul_le_mul
      · exact mul_le_mul_of_nonneg_right (by simpa only [Matrix.l2_opNorm_conjTranspose] using spectral_isometry_bound Q hQ) (norm_nonneg B)
      · exact spectral_isometry_bound V hV
      · exact norm_nonneg V
      · positivity
    _ = ‖B‖ := by ring
end Operator

section Frobenius
open scoped Matrix.Norms.Frobenius
noncomputable def frobeniusNorm (A : Matrix m n ℂ) : ℝ := ‖A‖

omit [DecidableEq m] [DecidableEq n] in
theorem frobenius_rect_sq_trace (A : Matrix m n ℂ) :
    ‖A‖^2 = (Matrix.trace (Aᴴ*A)).re := by
  rw [Matrix.frobenius_norm_def]
  simp only [Real.rpow_two,←Real.sqrt_eq_rpow]
  rw [Real.sq_sqrt (Finset.sum_nonneg (fun i _ => Finset.sum_nonneg
    (fun j _ => sq_nonneg ‖A i j‖)))]
  simp only [Matrix.trace,Matrix.diag,Matrix.mul_apply,Matrix.conjTranspose_apply,
    Complex.re_sum,Complex.star_def,Complex.conj_mul',←Complex.ofReal_pow,Complex.ofReal_re]
  exact Finset.sum_comm

omit [DecidableEq m] [DecidableEq s] in
theorem frobenius_left_isometry (Q : Matrix m r ℂ) (hQ : Qᴴ*Q=1)
    (G : Matrix r s ℂ) : ‖Q*G‖ = ‖G‖ := by
  have he : (Q*G)ᴴ*(Q*G) = Gᴴ*G := by
    simp only [Matrix.conjTranspose_mul,Matrix.mul_assoc]
    rw [←Matrix.mul_assoc Qᴴ Q G,hQ,Matrix.one_mul]
  have hn := congrArg (fun A : Matrix s s ℂ => (Matrix.trace A).re) he
  rw [←frobenius_rect_sq_trace,←frobenius_rect_sq_trace] at hn
  nlinarith [norm_nonneg (Q*G),norm_nonneg G]

omit [DecidableEq n] [DecidableEq r] in
theorem frobenius_right_isometry (V : Matrix n s ℂ) (hV : Vᴴ*V=1)
    (G : Matrix r s ℂ) : ‖G*Vᴴ‖ = ‖G‖ := by
  calc
    ‖G*Vᴴ‖ = ‖(G*Vᴴ)ᴴ‖ := (Matrix.frobenius_norm_conjTranspose _).symm
    _ = ‖V*Gᴴ‖ := by simp only [Matrix.conjTranspose_mul,Matrix.conjTranspose_conjTranspose]
    _ = ‖Gᴴ‖ := frobenius_left_isometry V hV Gᴴ
    _ = ‖G‖ := Matrix.frobenius_norm_conjTranspose _

omit [DecidableEq m] [DecidableEq n] in
/-- Orthogonal residual Pythagoras. The nonnegative discarded energy proves contraction. -/
theorem frobenius_projection_pythagoras (Q : Matrix m r ℂ) (hQ : Qᴴ*Q=1)
    (B : Matrix m n ℂ) :
    ‖B-Q*(Qᴴ*B)‖^2 = ‖B‖^2 - ‖Qᴴ*B‖^2 := by
  have hleft : Bᴴ*(Q*(Qᴴ*B)) = (Qᴴ*B)ᴴ*(Qᴴ*B) := by
    simp only [Matrix.conjTranspose_mul,Matrix.conjTranspose_conjTranspose,Matrix.mul_assoc]
  have hright : (Q*(Qᴴ*B))ᴴ*B = (Qᴴ*B)ᴴ*(Qᴴ*B) := by
    simp only [Matrix.conjTranspose_mul,Matrix.conjTranspose_conjTranspose,Matrix.mul_assoc]
  have hlast : (Q*(Qᴴ*B))ᴴ*(Q*(Qᴴ*B)) = (Qᴴ*B)ᴴ*(Qᴴ*B) := by
    simp only [Matrix.conjTranspose_mul,Matrix.mul_assoc]
    rw [←Matrix.mul_assoc Qᴴ Q (Qᴴ*B),hQ,Matrix.one_mul]
  simp only [frobenius_rect_sq_trace,Matrix.conjTranspose_sub,Matrix.sub_mul,Matrix.mul_sub,
    hleft,hright,hlast,Matrix.trace_sub,Complex.sub_re]
  ring

omit [DecidableEq m] [DecidableEq n] in
theorem frobenius_left_compress_le (Q : Matrix m r ℂ) (hQ : Qᴴ*Q=1)
    (B : Matrix m n ℂ) : ‖Qᴴ*B‖ ≤ ‖B‖ := by
  have h := frobenius_projection_pythagoras Q hQ B
  nlinarith [sq_nonneg ‖B-Q*(Qᴴ*B)‖, norm_nonneg (Qᴴ*B),norm_nonneg B]

omit [DecidableEq m] [DecidableEq n] in
theorem frobenius_right_compress_le (V : Matrix n s ℂ) (hV : Vᴴ*V=1)
    (B : Matrix m n ℂ) : ‖B*V‖ ≤ ‖B‖ := by
  calc
    ‖B*V‖ = ‖(B*V)ᴴ‖ := (Matrix.frobenius_norm_conjTranspose _).symm
    _ = ‖Vᴴ*Bᴴ‖ := by rw [Matrix.conjTranspose_mul]
    _ ≤ ‖Bᴴ‖ := frobenius_left_compress_le V hV Bᴴ
    _ = ‖B‖ := Matrix.frobenius_norm_conjTranspose _

omit [DecidableEq m] [DecidableEq n] in
theorem frobenius_lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G : Matrix r s ℂ) :
    frobeniusNorm (lift Q V G) = frobeniusNorm G := by
  unfold frobeniusNorm lift
  rw [frobenius_right_isometry V hV,frobenius_left_isometry Q hQ]

omit [DecidableEq m] [DecidableEq n] in
theorem frobenius_compress_le (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (B : Matrix m n ℂ) :
    frobeniusNorm (compress Q V B) ≤ frobeniusNorm B :=
  (frobenius_right_compress_le V hV (Qᴴ*B)).trans (frobenius_left_compress_le Q hQ B)
end Frobenius
end KomorebiPaperVIII.SmallCore

-- SIXTH AXIOM AUDITS
#print axioms KomorebiPaperVIII.SmallCore.compress_lift
#print axioms KomorebiPaperVIII.SmallCore.lift_sub
#print axioms KomorebiPaperVIII.SmallCore.compress_sub
#print axioms KomorebiPaperVIII.SmallCore.rank_compress_le
#print axioms KomorebiPaperVIII.SmallCore.rank_lift_le
#print axioms KomorebiPaperVIII.SmallCore.rank_lift
#print axioms KomorebiPaperVIII.SmallCore.spectral_left_isometry
#print axioms KomorebiPaperVIII.SmallCore.spectral_right_isometry
#print axioms KomorebiPaperVIII.SmallCore.spectral_isometry_bound
#print axioms KomorebiPaperVIII.SmallCore.spectral_lift
#print axioms KomorebiPaperVIII.SmallCore.spectral_compress_le
#print axioms KomorebiPaperVIII.SmallCore.frobenius_rect_sq_trace
#print axioms KomorebiPaperVIII.SmallCore.frobenius_left_isometry
#print axioms KomorebiPaperVIII.SmallCore.frobenius_right_isometry
#print axioms KomorebiPaperVIII.SmallCore.frobenius_projection_pythagoras
#print axioms KomorebiPaperVIII.SmallCore.frobenius_left_compress_le
#print axioms KomorebiPaperVIII.SmallCore.frobenius_right_compress_le
#print axioms KomorebiPaperVIII.SmallCore.frobenius_lift
#print axioms KomorebiPaperVIII.SmallCore.frobenius_compress_le
#print axioms KomorebiPaperVIII.SmallCore.compress
#print axioms KomorebiPaperVIII.SmallCore.frobeniusNorm
#print axioms KomorebiPaperVIII.SmallCore.lift
#print axioms KomorebiPaperVIII.SmallCore.spectralNorm
