module
public import InverseSupport
import all InverseSupport
import all PacketIR
import all QuantumPacketCore
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII item 6.8.
Actual rectangular coupling matrices and arbitrary packet projectors on both
retained and hidden spaces. The hidden inverse is Mathlib's matrix inverse.
A length-zero hidden path is allowed (enter and exit through the same packet).
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators Classical
open KomorebiPaperVII
variable {K X Y I J : Type*} [Field K]
variable [Fintype X] [DecidableEq X] [Fintype Y] [DecidableEq Y]
variable [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]
variable (P : PacketFamily (Matrix X X K) I) (Q : PacketFamily (Matrix Y Y K) J)

/-- The correction is expanded through all actual hidden packet inverse blocks. -/
theorem schur_correction_expansion (B : Matrix X Y K) (Hinv : Matrix Y Y K)
    (C : Matrix Y X K) (b a : I) :
    P.block (B*Hinv*C) b a =
      ∑ j, ∑ k, (P.proj b*B) * Q.block Hinv j k * (C*P.proj a) := by
  conv_lhs => rw [←Q.reconstruct Hinv]
  simp only [PacketFamily.block,Matrix.mul_sum,Matrix.sum_mul,Matrix.mul_assoc]

/-- A nonzero correction has an actual nonzero entrance, inverse block, and exit. -/
theorem schur_correction_support (B : Matrix X Y K) (H : Matrix Y Y K)
    (C : Matrix Y X K) (hH : IsUnit H.det) (b a : I)
    (h : P.block (B*H⁻¹*C) b a ≠ 0) :
    ∃ j k, P.proj b*B*Q.proj j ≠ 0 ∧ Reachable Q H j k ∧
      Q.proj k*C*P.proj a ≠ 0 := by
  rw [schur_correction_expansion P Q] at h
  obtain ⟨j,_,hj⟩ := Finset.exists_ne_zero_of_sum_ne_zero h
  obtain ⟨k,_,hk⟩ := Finset.exists_ne_zero_of_sum_ne_zero hj
  have hinv : Q.block H⁻¹ j k ≠ 0 := by
    intro hz
    apply hk
    rw [hz,Matrix.mul_zero,Matrix.zero_mul]
  have he : (P.proj b*B)*Q.block H⁻¹ j k*(C*P.proj a) =
      (P.proj b*B*Q.proj j)*H⁻¹*(Q.proj k*C*P.proj a) := by
    simp only [PacketFamily.block,Matrix.mul_assoc]
  refine ⟨j,k,?_,matrix_inverse_support Q H hH j k hinv,?_⟩
  · intro hz
    apply hk
    rw [he,hz,Matrix.zero_mul,Matrix.zero_mul]
  · intro hz
    apply hk
    rw [he,hz,Matrix.mul_zero]

/-- Item 6.8: the actual Schur support lies in direct edges or hidden walks. -/
theorem schur_support_inclusion (A : Matrix X X K) (B : Matrix X Y K)
    (H : Matrix Y Y K) (C : Matrix Y X K) (hH : IsUnit H.det) (b a : I)
    (h : P.block (A-B*H⁻¹*C) b a ≠ 0) :
    P.block A b a ≠ 0 ∨
      ∃ j k, P.proj b*B*Q.proj j ≠ 0 ∧ Reachable Q H j k ∧
        Q.proj k*C*P.proj a ≠ 0 := by
  by_cases ha : P.block A b a ≠ 0
  · exact Or.inl ha
  · right
    apply schur_correction_support P Q B H C hH b a
    intro hc
    apply h
    have hz : P.block A b a = 0 := not_ne_iff.mp ha
    change P.proj b*(A-B*H⁻¹*C)*P.proj a = 0
    rw [Matrix.mul_sub,Matrix.sub_mul]
    change P.block A b a - P.block (B*H⁻¹*C) b a = 0
    rw [hz,hc,sub_self]

/-- No permitted route certifies a zero retained Schur block. -/
theorem schur_zero_of_no_route (A : Matrix X X K) (B : Matrix X Y K)
    (H : Matrix Y Y K) (C : Matrix Y X K) (hH : IsUnit H.det) (b a : I)
    (ha : P.block A b a = 0)
    (hr : ∀ j k, P.proj b*B*Q.proj j ≠ 0 → Q.proj k*C*P.proj a ≠ 0 →
      ¬ Reachable Q H j k) : P.block (A-B*H⁻¹*C) b a = 0 := by
  by_contra hn
  obtain h | ⟨j,k,hj,hp,hk⟩ := schur_support_inclusion P Q A B H C hH b a hn
  · exact h ha
  · exact hr j k hj hk hp

end KomorebiPaperVIII

-- FIFTH BLOCK AXIOM AUDIT
#print axioms KomorebiPaperVIII.schur_correction_expansion
#print axioms KomorebiPaperVIII.schur_correction_support
#print axioms KomorebiPaperVIII.schur_support_inclusion
#print axioms KomorebiPaperVIII.schur_zero_of_no_route
