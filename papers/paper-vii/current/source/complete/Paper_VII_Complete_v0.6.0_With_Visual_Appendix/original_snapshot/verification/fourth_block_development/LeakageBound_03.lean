module
public import Mathlib.Analysis.CStarAlgebra.Classes
public import Mathlib.Analysis.CStarAlgebra.Basic
public import Mathlib.Analysis.SpecialFunctions.Exponential
public import Mathlib.Analysis.Calculus.MeanValue
public import Mathlib.Analysis.CStarAlgebra.Matrix
public import Mathlib.LinearAlgebra.Matrix.Hermitian
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII, fourth block.
Quantitative leakage for the actual exponential, proved from its derivative.
The norm is the C-star norm, specialized below to the matrix operator norm. -/
public section
set_option autoImplicit false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.Leakage
open NormedSpace
open scoped Matrix.Norms.L2Operator
variable {A : Type*} [CStarAlgebra A]
noncomputable local instance : NormedAlgebra ℚ A := .restrictScalars ℚ ℂ A

/-- Conjugation by the actual exponential of a fixed generator. -/
noncomputable def transported (G P : A) (t : ℝ) : A :=
  exp (t • G) * P * exp (t • (-G))

theorem exp_unitary (G : A) (hG : star G = -G) (t : ℝ) :
    exp (t • G) ∈ unitary A := by
  apply exp_mem_unitary_of_mem_skewAdjoint
  change star (t • G) = -(t • G)
  simp [hG]

theorem transported_derivative (G P : A) (t : ℝ) :
    HasDerivAt (transported G P)
      (exp (t • G) * (G * P - P * G) * exp (t • (-G))) t := by
  have hd := ((hasDerivAt_exp_smul_const G t).mul_const P).mul
    (hasDerivAt_exp_smul_const' (-G) t)
  convert hd using 1
  · rfl
  · noncomm_ring

theorem transported_derivative_norm (G P : A) (hG : star G = -G) (t : ℝ) :
    ‖deriv (transported G P) t‖ = ‖G * P - P * G‖ := by
  rw [(transported_derivative G P t).deriv,
    CStarRing.norm_mul_mem_unitary _ (exp_unitary (-G) (by simp [hG]) t),
    CStarRing.norm_mem_unitary_mul _ (exp_unitary G hG t)]

theorem transported_lipschitz (G P : A) (hG : star G = -G) (t s : ℝ) :
    ‖transported G P t - transported G P s‖ ≤
      |t-s| * ‖G*P-P*G‖ := by
  have hh := Convex.norm_image_sub_le_of_norm_deriv_le
    (f := transported G P) (s := Set.univ)
    (fun x _ => (transported_derivative G P x).differentiableAt)
    (fun x _ => (transported_derivative_norm G P hG x).le)
    convex_univ (Set.mem_univ s) (Set.mem_univ t)
  simpa [Real.norm_eq_abs, mul_comm] using hh

theorem exponential_commutator_bound (G P : A) (hG : star G = -G) (t : ℝ) :
    ‖exp (t • G) * P - P * exp (t • G)‖ ≤ |t| * ‖G*P-P*G‖ := by
  have hcancel : exp (t • (-G)) * exp (t • G) = 1 := by
    rw [smul_neg, ← exp_add_of_commute ((Commute.refl (t • G)).neg_left),
      neg_add_cancel, NormedSpace.exp_zero]
  have heq : (transported G P t - P) * exp (t • G) =
      exp (t • G) * P - P * exp (t • G) := by
    simp only [transported, sub_mul, mul_assoc, hcancel, mul_one]
  rw [← heq, CStarRing.norm_mul_mem_unitary _ (exp_unitary G hG t)]
  simpa [transported] using transported_lipschitz G P hG t 0

theorem leakage_corner (P U : A) (hP : IsStarProjection P) :
    (1-P)*U*P = (1-P)*(U*P-P*U)*P := by
  symm
  rw [mul_sub, sub_mul]
  have hzero : (1-P)*(P*U)*P = 0 := by
    rw [← mul_assoc (1-P) P U, hP.one_sub_mul_self, zero_mul, zero_mul]
  rw [hzero, sub_zero, mul_assoc (1-P), mul_assoc U, hP.isIdempotentElem.eq, mul_assoc]

theorem leakage_corner_norm (P U : A) (hP : IsStarProjection P) :
    ‖(1-P)*U*P‖ ≤ ‖U*P-P*U‖ := by
  rw [leakage_corner P U hP]
  calc
    _ ≤ ‖(1-P)*(U*P-P*U)‖ * ‖P‖ := norm_mul_le _ _
    _ ≤ (‖1-P‖ * ‖U*P-P*U‖) * ‖P‖ :=
      mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _)
    _ ≤ (1 * ‖U*P-P*U‖) * 1 := by
      gcongr
      · exact IsStarProjection.norm_le _ hP.one_sub
      · exact IsStarProjection.norm_le _ hP
    _ = _ := by ring

theorem skew_generator_leakage_bound (G P : A) (hG : star G = -G)
    (hP : IsStarProjection P) (t : ℝ) :
    ‖(1-P) * exp (t • G) * P‖ ≤ |t| * ‖G*P-P*G‖ :=
  (leakage_corner_norm P _ hP).trans (exponential_commutator_bound G P hG t)

/-- Schrodinger generator with the sign fixed by exp(-itH). -/
noncomputable def generator (H : A) : A := (-Complex.I) • H

theorem generator_skew (H : A) (hH : IsSelfAdjoint H) :
    star (generator H) = -generator H := by
  simp [generator, star_smul, hH.star_eq]

theorem generator_commutator_norm (H P : A) :
    ‖generator H * P - P * generator H‖ = ‖H*P-P*H‖ := by
  simp only [generator, smul_mul_assoc, mul_smul_comm, ← smul_sub, norm_smul,
    norm_neg, Complex.norm_I, one_mul]

/-- Theorem 5.2 with no nonzero-rank or nonzero-time restriction. -/
theorem commutator_leakage_bound (H P : A) (hH : IsSelfAdjoint H)
    (hP : IsStarProjection P) (t : ℝ) :
    ‖(1-P) * exp ((-(t : ℂ)*Complex.I) • H) * P‖ ≤ |t| * ‖H*P-P*H‖ := by
  have hh := skew_generator_leakage_bound (generator H) P (generator_skew H hH) hP t
  rw [generator_commutator_norm] at hh
  convert hh using 1
  simp [generator, ← Complex.real_smul]

theorem exact_symmetry_zero_leakage (H P : A) (hH : IsSelfAdjoint H)
    (hP : IsStarProjection P) (hcomm : H*P=P*H) (t : ℝ) :
    (1-P) * exp ((-(t : ℂ)*Complex.I) • H) * P = 0 := by
  apply norm_eq_zero.mp
  apply le_antisymm _ (norm_nonneg _)
  simpa [hcomm] using commutator_leakage_bound H P hH hP t

/-- Concrete complex matrices, equipped with the operator norm. -/
theorem matrix_commutator_leakage_bound {n : Type*} [Fintype n] [DecidableEq n]
    (H P : Matrix n n ℂ) (hH : H.IsHermitian) (hP : P.IsHermitian)
    (hPP : P*P=P) (t : ℝ) :
    ‖(1-P) * exp ((-(t : ℂ)*Complex.I) • H) * P‖ ≤ |t| * ‖H*P-P*H‖ := by
  exact commutator_leakage_bound H P hH.isSelfAdjoint ⟨hPP, hP.isSelfAdjoint⟩ t
end KomorebiPaperVII.Leakage
