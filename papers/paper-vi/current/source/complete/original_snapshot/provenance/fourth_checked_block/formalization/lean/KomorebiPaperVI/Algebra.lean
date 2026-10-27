import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic

/-! Author: Komorebi P. Exact packet and rectangular refinement identities. -/
namespace KomorebiPaperVI.Algebra
open scoped BigOperators

variable {R I : Type*} [Ring R] [Fintype I]

def block (P : I → R) (A : R) (b a : I) : R := P b * A * P a

theorem block_reconstruction (P : I → R) (hP : ∑ i, P i = 1) (A : R) :
    ∑ b, ∑ a, block P A b a = A := by
  simp only [block, ← Finset.mul_sum, hP, mul_one, ← Finset.sum_mul, one_mul]

theorem block_multiplication (P : I → R) (hP : ∑ i, P i = 1)
    (hid : ∀ i, P i * P i = P i) (A B : R) (b a : I) :
    block P (A*B) b a = ∑ c, block P A b c * block P B c a := by
  have term (c : I) : block P A b c * block P B c a =
      P b * A * P c * B * P a := by
    dsimp [block]
    calc
      _ = P b * A * (P c * P c) * B * P a := by noncomm_ring
      _ = _ := by rw [hid]
  simp_rw [term]
  simp only [← Finset.sum_mul, ← Finset.mul_sum, hP, block, mul_assoc, one_mul]

theorem packet_semigroup_convolution (P : I → R) (hP : ∑ i, P i = 1)
    (hid : ∀ i, P i * P i = P i) (T : ℝ → R)
    (hT : ∀ s t, T (s+t) = T s*T t) (s t : ℝ) (b a : I) :
    block P (T (s+t)) b a = ∑ c, block P (T s) b c * block P (T t) c a := by
  rw [hT]
  exact block_multiplication P hP hid _ _ _ _

theorem difference_idempotent (P Q : R) (hP : P*P=P) (hQ : Q*Q=Q)
    (hPQ : P*Q=P) (hQP : Q*P=P) : (Q-P)*(Q-P)=Q-P := by
  noncomm_ring [hP,hQ,hPQ,hQP]

theorem difference_annihilates_coarse (P Q : R) (hP : P*P=P)
    (hPQ : P*Q=P) (hQP : Q*P=P) :
    P*(Q-P)=0 ∧ (Q-P)*P=0 := by
  constructor <;> noncomm_ring [hP,hPQ,hQP]

theorem tower_telescope (P : ℕ → R) (n : ℕ) :
    P 0 + ∑ j ∈ Finset.range n, (P (j+1)-P j) = P n := by
  induction n with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ]; rw [← add_assoc, ih]; abel

section Rectangular
variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n]

theorem intertwining_powers (C : Matrix m n R) (A : Matrix n n R) (B : Matrix m m R)
    (h : C*A=B*C) (k : ℕ) : C*A^k=B^k*C := by
  induction k with
  | zero => simp
  | succ k ih =>
    calc
      C*A^(k+1) = (C*A^k)*A := by rw [pow_succ, Matrix.mul_assoc]
      _ = (B^k*C)*A := by rw [ih]
      _ = (B^k*B)*C := by rw [Matrix.mul_assoc, h, ← Matrix.mul_assoc]
      _ = B^(k+1)*C := by rw [pow_succ]

theorem finite_horizon_defect (C : Matrix m n R) (A : Matrix n n R) (B : Matrix m m R)
    (k : ℕ) :
    C*A^k-B^k*C = ∑ j ∈ Finset.range k, B^(k-1-j)*(C*A-B*C)*A^j := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ]
    have hs : (∑ j ∈ Finset.range k, B^(k+1-1-j)*(C*A-B*C)*A^j) =
        B*(∑ j ∈ Finset.range k, B^(k-1-j)*(C*A-B*C)*A^j) := by
      rw [Matrix.mul_sum]
      apply Finset.sum_congr rfl
      intro j hj
      have hjk := Finset.mem_range.mp hj
      have he : k+1-1-j = (k-1-j)+1 := by omega
      rw [he, pow_succ']
      simp only [Matrix.mul_assoc]
    rw [hs, ← ih]
    simp only [Nat.add_sub_cancel, Nat.sub_self, pow_zero, Matrix.one_mul]
    simp only [pow_succ', Matrix.mul_sub, Matrix.sub_mul, Matrix.mul_assoc]
    abel

theorem rectangular_resolvent_identity (C : Matrix m n R)
    (A : Matrix n n R) (B : Matrix m m R)
    (Rf : Matrix n n R) (Rc : Matrix m m R) (z : R)
    (hz : ∀ i j, z*C i j = C i j*z)
    (hf : (Matrix.scalar n z-A)*Rf=1)
    (hc : Rc*(Matrix.scalar m z-B)=1) :
    C*Rf-Rc*C=Rc*(C*A-B*C)*Rf := by
  have hzC : Matrix.scalar m z*C=C*Matrix.scalar n z := by
    ext i j
    simpa using hz i j
  have hd : C*A-B*C=(Matrix.scalar m z-B)*C-C*(Matrix.scalar n z-A) := by
    rw [Matrix.sub_mul, Matrix.mul_sub, hzC]
    abel
  rw [hd, Matrix.mul_sub, Matrix.sub_mul]
  simp only [← Matrix.mul_assoc, hc, Matrix.one_mul]
  rw [Matrix.mul_assoc (Rc*C), hf, Matrix.mul_one]

end Rectangular
end KomorebiPaperVI.Algebra
