module
public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.LinearAlgebra.Matrix.Kronecker
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.Analysis.Complex.Basic
/-! Author: Komorebi P. Paper VII second block, Classical input 7.2.
Actual block amplification identified with identity-tensor Kraus operators. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVII.Kraus
open scoped BigOperators Kronecker ComplexOrder
variable {n A : Type*} [Fintype n] [Fintype A]
def channel (K : A → Matrix n n ℂ) (rho : Matrix n n ℂ) : Matrix n n ℂ :=
  ∑ a, K a * rho * (K a).conjTranspose

theorem channel_add (K : A → Matrix n n ℂ) (rho sigma : Matrix n n ℂ) :
    channel K (rho + sigma) = channel K rho + channel K sigma := by
  simp [channel, Matrix.mul_add, Matrix.add_mul, Finset.sum_add_distrib]

theorem channel_smul (K : A → Matrix n n ℂ) (c : ℂ) (rho : Matrix n n ℂ) :
    channel K (c • rho) = c • channel K rho := by
  simp [channel, Finset.smul_sum]

def linearMap (K : A → Matrix n n ℂ) : Matrix n n ℂ →ₗ[ℂ] Matrix n n ℂ where
  toFun := channel K
  map_add' := channel_add K
  map_smul' := channel_smul K

theorem channel_positive (K : A → Matrix n n ℂ) {rho : Matrix n n ℂ}
    (hrho : rho.PosSemidef) : (channel K rho).PosSemidef := by
  exact Matrix.posSemidef_sum _ (fun a _ => hrho.mul_mul_conjTranspose_same (K a))

theorem channel_trace_preserving [DecidableEq n] (K : A → Matrix n n ℂ)
    (hK : ∑ a, (K a).conjTranspose * K a = 1) (rho : Matrix n n ℂ) :
    Matrix.trace (channel K rho) = Matrix.trace rho := by
  unfold channel
  rw [Matrix.trace_sum]
  have cyclic (a : A) : Matrix.trace (K a * rho * (K a).conjTranspose) =
      Matrix.trace (((K a).conjTranspose * K a) * rho) := by
    rw [Matrix.trace_mul_comm, Matrix.mul_assoc]
  simp_rw [cyclic]
  rw [← Matrix.trace_sum, ← Finset.sum_mul, hK, Matrix.one_mul]

def amplify {J : Type*} (Phi : Matrix n n ℂ → Matrix n n ℂ)
    (rho : Matrix (J × n) (J × n) ℂ) : Matrix (J × n) (J × n) ℂ :=
  fun x y => Phi (fun u v => rho (x.1, u) (y.1, v)) x.2 y.2

theorem amplification_eq_kraus {J : Type*} [Fintype J] [DecidableEq J]
    (K : A → Matrix n n ℂ) (rho : Matrix (J × n) (J × n) ℂ) :
    amplify (channel K) rho =
      channel (fun a => (1 : Matrix J J ℂ) ⊗ₖ K a) rho := by
  ext ⟨i, u⟩ ⟨j, v⟩
  simp_rw [amplify, channel, Matrix.sum_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, Matrix.kroneckerMap_apply]
  simp [Fintype.sum_prod_type, Matrix.one_apply, apply_ite]
  rfl

theorem channel_completely_positive {J : Type*} [Fintype J] [DecidableEq J]
    (K : A → Matrix n n ℂ) {rho : Matrix (J × n) (J × n) ℂ}
    (hrho : rho.PosSemidef) : (amplify (channel K) rho).PosSemidef := by
  rw [amplification_eq_kraus]
  exact channel_positive _ hrho

theorem channel_density_matrix [DecidableEq n] (K : A → Matrix n n ℂ)
    (hK : ∑ a, (K a).conjTranspose * K a = 1) {rho : Matrix n n ℂ}
    (hp : rho.PosSemidef) (ht : Matrix.trace rho = 1) :
    (channel K rho).PosSemidef ∧ Matrix.trace (channel K rho) = 1 := by
  exact ⟨channel_positive K hp, (channel_trace_preserving K hK rho).trans ht⟩
end KomorebiPaperVII.Kraus

#print axioms KomorebiPaperVII.Kraus.channel_add
#print axioms KomorebiPaperVII.Kraus.channel_smul
#print axioms KomorebiPaperVII.Kraus.channel_positive
#print axioms KomorebiPaperVII.Kraus.channel_trace_preserving
#print axioms KomorebiPaperVII.Kraus.amplification_eq_kraus
#print axioms KomorebiPaperVII.Kraus.channel_completely_positive
#print axioms KomorebiPaperVII.Kraus.channel_density_matrix
