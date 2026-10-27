module

public import Mathlib.Algebra.Star.BigOperators
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose
public import Mathlib.Analysis.Normed.Algebra.Exponential
public import Mathlib.Tactic.NoncommRing

/-!
Author: Komorebi P.
Paper VII, first checked block. Finite packet algebra, arbitrary finite circuit
length, both unitarity identities, symmetry and dephasing. No physical continuum
claim is encoded here. Multiplication is operator composition, NOT commutative.
-/

public section
set_option autoImplicit false
namespace KomorebiPaperVII
open scoped BigOperators

/-- Finite exact idempotent resolution; adjoint conditions are supplied separately. -/
structure PacketFamily (R I : Type*) [Ring R] [Fintype I] [DecidableEq I] where
  proj : I → R
  mul_proj : ∀ i j, proj i * proj j = if i = j then proj i else 0
  sum_proj : ∑ i, proj i = 1

namespace PacketFamily
section Algebra
variable {R I : Type*} [Ring R] [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I)

@[simp] theorem idempotent (i : I) : P.proj i * P.proj i = P.proj i := by
  simp [P.mul_proj]

/-- Target index precedes source index. -/
def block (U : R) (b a : I) : R := P.proj b * U * P.proj a

theorem reconstruct (U : R) : (∑ b, ∑ a, P.block U b a) = U := by
  simp only [block, ← Finset.mul_sum, P.sum_proj, mul_one, ← Finset.sum_mul, one_mul]

theorem compose_blocks (U V : R) (b a : I) :
    P.block (U * V) b a = ∑ c, P.block U b c * P.block V c a := by
  have term (c : I) : P.block U b c * P.block V c a =
      P.proj b * U * P.proj c * V * P.proj a := by
    unfold block
    calc
      _ = P.proj b * U * (P.proj c * P.proj c) * V * P.proj a := by noncomm_ring
      _ = _ := by rw [P.idempotent]
  simp_rw [term]
  simp only [← Finset.sum_mul, ← Finset.mul_sum, P.sum_proj, block, mul_assoc, one_mul]

/-- Gates are listed from latest to earliest: [Um,...,U1]. -/
def circuit : List R → R
  | [] => 1
  | U :: Us => U * circuit Us

/-- An explicit nested finite sum. The zero-gate case fixes the boundary packet. -/
def pathSum : List R → I → I → R
  | [], b, a => P.proj b * P.proj a
  | U :: Us, b, a => ∑ c, P.block U b c * pathSum Us c a

/-- Theorem 4.1, all finite depths, not merely a two-gate example. -/
theorem circuit_path_expansion (Us : List R) (b a : I) :
    P.block (circuit Us) b a = P.pathSum Us b a := by
  induction Us generalizing b a with
  | nil => simp [circuit, pathSum, block]
  | cons U Us ih =>
      simp only [circuit, pathSum, P.compose_blocks, ih]

theorem circuit_reconstruction (Us : List R) :
    (∑ b, ∑ a, P.pathSum Us b a) = circuit Us := by
  simp_rw [← P.circuit_path_expansion]
  exact P.reconstruct _

/-- Algebraic part of Theorem 5.1. -/
theorem symmetry_no_transfer (H : R) (hH : ∀ i, H * P.proj i = P.proj i * H)
    (b a : I) (hba : b ≠ a) : P.block H b a = 0 := by
  simp [block, ← hH b, mul_assoc, P.mul_proj, hba]

theorem symmetry_diagonal (H : R) (hH : ∀ i, H * P.proj i = P.proj i * H) :
    (∑ a, P.block H a a) = H := by
  have term (a : I) : P.block H a a = H * P.proj a := by
    rw [block, ← hH a, mul_assoc, P.idempotent]
  simp_rw [term]
  rw [← Finset.mul_sum, P.sum_proj, mul_one]

/-- The dephasing map discards only off-diagonal packet corners. -/
def dephase (rho : R) : R := ∑ a, P.block rho a a

theorem dephase_idempotent (rho : R) : P.dephase (P.dephase rho) = P.dephase rho := by
  unfold dephase block
  simp only [Finset.mul_sum, Finset.sum_mul]
  have term (a b : I) : P.proj a * (P.proj b * rho * P.proj b) * P.proj a =
      if a = b then P.proj a * rho * P.proj a else 0 := by
    by_cases hab : a = b
    · subst b
      simp only [ite_true]
      calc
        _ = (P.proj a * P.proj a) * rho * (P.proj a * P.proj a) := by noncomm_ring
        _ = _ := by rw [P.idempotent]
    · calc
        _ = (P.proj a * P.proj b) * rho * (P.proj b * P.proj a) := by noncomm_ring
        _ = _ := by simp [P.mul_proj, hab]
  simp_rw [term]
  simp

end Algebra

section Adjoint
variable {R I : Type*} [Ring R] [StarRing R] [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I) (hstar : ∀ i, star (P.proj i) = P.proj i)
include hstar

theorem adjoint_block (U : R) (b a : I) :
    star (P.block U b a) = P.block (star U) a b := by
  simp only [block, star_mul, hstar, mul_assoc]

/-- The column identity in Theorem 4.2. Only U*U=1 is needed here. -/
theorem unitarity_columns (U : R) (hU : star U * U = 1) (a c : I) :
    (∑ b, star (P.block U b a) * P.block U b c) =
      if a = c then P.proj a else 0 := by
  have term (b : I) : star (P.block U b a) * P.block U b c =
      P.proj a * star U * P.proj b * U * P.proj c := by
    rw [P.adjoint_block hstar]
    unfold block
    calc
      _ = P.proj a * star U * (P.proj b * P.proj b) * U * P.proj c := by noncomm_ring
      _ = _ := by rw [P.idempotent]
  simp_rw [term]
  rw [← Finset.sum_mul, ← Finset.sum_mul, ← Finset.mul_sum, P.sum_proj, mul_one]
  rw [mul_assoc (P.proj a), hU, mul_one, P.mul_proj]

/-- The row identity in Theorem 4.2. Only UU*=1 is needed here. -/
theorem unitarity_rows (U : R) (hU : U * star U = 1) (b d : I) :
    (∑ a, P.block U b a * star (P.block U d a)) =
      if b = d then P.proj b else 0 := by
  have term (a : I) : P.block U b a * star (P.block U d a) =
      P.proj b * U * P.proj a * star U * P.proj d := by
    rw [P.adjoint_block hstar]
    unfold block
    calc
      _ = P.proj b * U * (P.proj a * P.proj a) * star U * P.proj d := by noncomm_ring
      _ = _ := by rw [P.idempotent]
  simp_rw [term]
  rw [← Finset.sum_mul, ← Finset.sum_mul, ← Finset.mul_sum, P.sum_proj, mul_one]
  rw [mul_assoc (P.proj b), hU, mul_one, P.mul_proj]

end Adjoint

section Dynamics
variable {R I : Type*} [NormedRing R] [NormedAlgebra ℂ R]
variable [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I)

/-- Commutation propagates to the actual operator exponential, not an assumed flow. -/
theorem symmetry_exponential_commutes (H : R)
    (hH : ∀ i, H * P.proj i = P.proj i * H) (z : ℂ) (i : I) :
    NormedSpace.exp (z • H) * P.proj i = P.proj i * NormedSpace.exp (z • H) := by
  have h : Commute H (P.proj i) := hH i
  exact (h.smul_left z).exp_left.eq

/-- Theorem 5.1 includes real-time Schrodinger evolution by z = -it. -/
theorem symmetry_exponential_diagonal (H : R)
    (hH : ∀ i, H * P.proj i = P.proj i * H) (z : ℂ) :
    (∑ a, P.block (NormedSpace.exp (z • H)) a a) = NormedSpace.exp (z • H) :=
  P.symmetry_diagonal _ (P.symmetry_exponential_commutes H hH z)

theorem symmetry_exponential_no_transfer (H : R)
    (hH : ∀ i, H * P.proj i = P.proj i * H) (z : ℂ)
    (b a : I) (hba : b ≠ a) : P.block (NormedSpace.exp (z • H)) b a = 0 :=
  P.symmetry_no_transfer _ (P.symmetry_exponential_commutes H hH z) b a hba

end Dynamics
end PacketFamily

section Measurement
variable {n I : Type*} [Fintype n] [DecidableEq n] [Fintype I] [DecidableEq I]
variable (P : PacketFamily (Matrix n n ℂ) I)

/-- Concrete complex-matrix specialization, with adjoint = conjugate transpose. -/
theorem matrix_unitarity_columns (hstar : ∀ i, (P.proj i).conjTranspose = P.proj i)
    (U : Matrix n n ℂ) (hU : U.conjTranspose * U = 1) (a c : I) :
    (∑ b, (P.block U b a).conjTranspose * P.block U b c) =
      if a = c then P.proj a else 0 := by
  exact P.unitarity_columns hstar U hU a c

/-- The second conservation identity for finite complex matrices. -/
theorem matrix_unitarity_rows (hstar : ∀ i, (P.proj i).conjTranspose = P.proj i)
    (U : Matrix n n ℂ) (hU : U * U.conjTranspose = 1) (b d : I) :
    (∑ a, P.block U b a * (P.block U d a).conjTranspose) =
      if b = d then P.proj b else 0 := by
  exact P.unitarity_rows hstar U hU b d

/-- Trace duality for dephasing, valid for all matrices, not only density matrices. -/
theorem dephase_trace_duality (E rho : Matrix n n ℂ) :
    Matrix.trace (P.dephase E * rho) = Matrix.trace (E * P.dephase rho) := by
  unfold PacketFamily.dephase PacketFamily.block
  simp only [Finset.sum_mul, Finset.mul_sum, Matrix.trace_sum]
  apply Finset.sum_congr rfl
  intro a _
  calc
    _ = Matrix.trace ((E * P.proj a * rho) * P.proj a) := by
      rw [show P.proj a * E * P.proj a * rho =
        P.proj a * (E * P.proj a * rho) by noncomm_ring, Matrix.trace_mul_comm]
    _ = _ := by congr 1; noncomm_ring

/-- Theorem 7.1, exactly the stated block-diagonal-observable hypothesis. -/
theorem measurement_invariance (E rho : Matrix n n ℂ) (hE : P.dephase E = E) :
    Matrix.trace (E * rho) = Matrix.trace (E * P.dephase rho) := by
  rw [← hE] at ⊢
  simpa only [P.dephase_idempotent] using dephase_trace_duality P (P.dephase E) rho

theorem dephase_trace_preserving (rho : Matrix n n ℂ) :
    Matrix.trace (P.dephase rho) = Matrix.trace rho := by
  have h : P.dephase 1 = 1 := by
    simp only [PacketFamily.dephase, PacketFamily.block, mul_one, P.idempotent, P.sum_proj]
  simpa only [Matrix.one_mul] using (measurement_invariance P 1 rho h).symm

end Measurement

end KomorebiPaperVII

/-! Exported theorem axiom audit. -/
#print axioms KomorebiPaperVII.PacketFamily.idempotent
#print axioms KomorebiPaperVII.PacketFamily.reconstruct
#print axioms KomorebiPaperVII.PacketFamily.compose_blocks
#print axioms KomorebiPaperVII.PacketFamily.circuit_path_expansion
#print axioms KomorebiPaperVII.PacketFamily.circuit_reconstruction
#print axioms KomorebiPaperVII.PacketFamily.symmetry_no_transfer
#print axioms KomorebiPaperVII.PacketFamily.symmetry_diagonal
#print axioms KomorebiPaperVII.PacketFamily.dephase_idempotent
#print axioms KomorebiPaperVII.PacketFamily.adjoint_block
#print axioms KomorebiPaperVII.PacketFamily.unitarity_columns
#print axioms KomorebiPaperVII.PacketFamily.unitarity_rows
#print axioms KomorebiPaperVII.PacketFamily.symmetry_exponential_commutes
#print axioms KomorebiPaperVII.PacketFamily.symmetry_exponential_diagonal
#print axioms KomorebiPaperVII.PacketFamily.symmetry_exponential_no_transfer
#print axioms KomorebiPaperVII.matrix_unitarity_columns
#print axioms KomorebiPaperVII.matrix_unitarity_rows
#print axioms KomorebiPaperVII.dephase_trace_duality
#print axioms KomorebiPaperVII.measurement_invariance
#print axioms KomorebiPaperVII.dephase_trace_preserving
