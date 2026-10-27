module
public import PacketIR
import all PacketIR
import all QuantumPacketCore
public import Mathlib.Analysis.Matrix.Normed
public import Mathlib.Analysis.CStarAlgebra.Matrix
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII item 9.2.
Exact residual of arbitrary complete orthogonal projector families, not only
coordinate masks. Frobenius and Euclidean operator norms are kept distinct.
This certifies a supplied decomposition; it does not discover the projectors.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators Classical Matrix
open KomorebiPaperVII
variable {X I : Type*} [Fintype X] [DecidableEq X] [Fintype I] [DecidableEq I]
variable (P : PacketFamily (Matrix X X ℂ) I)

noncomputable def diagonalCompression (A : Matrix X X ℂ) : Matrix X X ℂ :=
  ∑ a, P.block A a a

noncomputable def offDiagonalTerm (A : Matrix X X ℂ) (e : I × I) : Matrix X X ℂ :=
  if e.1 = e.2 then 0 else P.block A e.1 e.2

theorem compression_decomposition (A : Matrix X X ℂ) :
    A = diagonalCompression P A + ∑ e, offDiagonalTerm P A e := by
  calc
    A = ∑ b, ∑ a, ((if b=a then P.block A b a else 0) +
        (if b=a then 0 else P.block A b a)) := by
      conv_lhs => rw [←P.reconstruct A]
      apply Finset.sum_congr rfl
      intro b _
      apply Finset.sum_congr rfl
      intro a _
      by_cases he : b=a <;> simp [he]
    _ = diagonalCompression P A + ∑ e, offDiagonalTerm P A e := by
      simp only [Finset.sum_add_distrib,Fintype.sum_prod_type,offDiagonalTerm,
        diagonalCompression]
      congr 1
      apply Finset.sum_congr rfl
      intro b _
      simp

theorem compression_residual (A : Matrix X X ℂ) :
    A-diagonalCompression P A = ∑ e, offDiagonalTerm P A e := by
  exact sub_eq_iff_eq_add.mpr ((compression_decomposition P A).trans (add_comm _ _))

/-- Distinct packet corners are Hilbert--Schmidt orthogonal. -/
theorem block_trace_orthogonal (hP : ∀ a, (P.proj a)ᴴ = P.proj a)
    (A B : Matrix X X ℂ) (b a d c : I) (hne : (b,a) ≠ (d,c)) :
    Matrix.trace ((P.block A b a)ᴴ * P.block B d c) = 0 := by
  have hadj : (P.block A b a)ᴴ = P.proj a*Aᴴ*P.proj b := by
    simp only [PacketFamily.block,Matrix.conjTranspose_mul,hP,Matrix.mul_assoc]
  rw [hadj]
  by_cases hbd : b=d
  · have hca : c ≠ a := by
      intro he
      apply hne
      exact Prod.ext hbd he.symm
    calc
      Matrix.trace ((P.proj a*Aᴴ*P.proj b)*P.block B d c) =
          Matrix.trace ((P.proj a*Aᴴ*P.proj b*P.proj d*B)*P.proj c) := by
        simp only [PacketFamily.block,Matrix.mul_assoc]
      _ = Matrix.trace (P.proj c*(P.proj a*Aᴴ*P.proj b*P.proj d*B)) :=
        Matrix.trace_mul_comm _ _
      _ = 0 := by
        simp only [←Matrix.mul_assoc]
        rw [P.mul_proj c a]
        simp [hca]
  · calc
      Matrix.trace ((P.proj a*Aᴴ*P.proj b)*P.block B d c) =
          Matrix.trace (P.proj a*Aᴴ*(P.proj b*P.proj d)*B*P.proj c) := by
        simp only [PacketFamily.block,Matrix.mul_assoc]
      _ = 0 := by
        rw [P.mul_proj b d]
        simp [hbd]

theorem offDiagonal_trace_orthogonal (hP : ∀ a, (P.proj a)ᴴ = P.proj a)
    (A : Matrix X X ℂ) (e f : I × I) (hne : e ≠ f) :
    Matrix.trace ((offDiagonalTerm P A e)ᴴ * offDiagonalTerm P A f) = 0 := by
  by_cases he : e.1=e.2
  · simp [offDiagonalTerm,he]
  · by_cases hf : f.1=f.2
    · simp [offDiagonalTerm,hf]
    · simp only [offDiagonalTerm,he,hf,ite_false]
      exact block_trace_orthogonal P hP A A e.1 e.2 f.1 f.2 hne

section Frobenius
open scoped Matrix.Norms.Frobenius

/-- The actual Frobenius norm agrees with the Hilbert--Schmidt trace form. -/
theorem frobenius_sq_trace (A : Matrix X X ℂ) :
    ‖A‖^2 = (Matrix.trace (Aᴴ*A)).re := by
  rw [Matrix.frobenius_norm_def]
  simp only [Real.rpow_two,←Real.sqrt_eq_rpow]
  rw [Real.sq_sqrt (Finset.sum_nonneg (fun i _ => Finset.sum_nonneg
    (fun j _ => sq_nonneg ‖A i j‖)))]
  simp only [Matrix.trace,Matrix.diag,Matrix.mul_apply,Matrix.conjTranspose_apply,
    Complex.re_sum,Complex.star_def,Complex.conj_mul',←Complex.ofReal_pow,Complex.ofReal_re]
  exact Finset.sum_comm

/-- Pythagoras from the trace expansion, with every cross term eliminated. -/
theorem frobenius_sum_sq {J : Type*} [Fintype J] [DecidableEq J]
    (T : J → Matrix X X ℂ)
    (hT : ∀ i j, i ≠ j → Matrix.trace ((T i)ᴴ*T j) = 0) :
    ‖∑ j, T j‖^2 = ∑ j, ‖T j‖^2 := by
  simp_rw [frobenius_sq_trace]
  have ht : Matrix.trace ((∑ j,T j)ᴴ*(∑ j,T j)) =
      ∑ j, Matrix.trace ((T j)ᴴ*T j) := by
    simp only [Matrix.conjTranspose_sum,Matrix.sum_mul,Matrix.mul_sum,Matrix.trace_sum]
    apply Finset.sum_congr rfl
    intro i _
    apply Finset.sum_eq_single i
    · intro j _ hji
      exact hT j i hji
    · simp
  rw [ht]
  simp

/-- Frobenius half of item 9.2, for arbitrary self-adjoint projectors. -/
theorem discovery_frobenius_certificate (hP : ∀ a, (P.proj a)ᴴ = P.proj a)
    (A : Matrix X X ℂ) :
    ‖A-diagonalCompression P A‖^2 =
      ∑ b, ∑ a, if b=a then 0 else ‖P.block A b a‖^2 := by
  rw [compression_residual P A,
    frobenius_sum_sq (offDiagonalTerm P A) (offDiagonal_trace_orthogonal P hP A)]
  simp only [Fintype.sum_prod_type,offDiagonalTerm]
  apply Finset.sum_congr rfl
  intro b _
  apply Finset.sum_congr rfl
  intro a _
  by_cases h : b=a <;> simp [h]
end Frobenius

section Operator
open scoped Matrix.Norms.L2Operator

/-- Operator-norm half of item 9.2; this is the Euclidean induced matrix norm. -/
theorem discovery_operator_certificate (A : Matrix X X ℂ) :
    ‖A-diagonalCompression P A‖ ≤
      ∑ b, ∑ a, if b=a then 0 else ‖P.block A b a‖ := by
  rw [compression_residual P A]
  apply (norm_sum_le _ _).trans_eq
  simp only [Fintype.sum_prod_type,offDiagonalTerm]
  apply Finset.sum_congr rfl
  intro b _
  apply Finset.sum_congr rfl
  intro a _
  by_cases h : b=a <;> simp [h]
end Operator

end KomorebiPaperVIII
