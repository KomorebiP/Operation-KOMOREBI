module
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Analysis.Calculus.Deriv.Star
public import Mathlib.Analysis.Calculus.Deriv.Add
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.Abel
/-! Author: Komorebi P. Paper VII second block, Theorem 6.1.
Actual differentiated coordinates y = U* psi and the corrected Hamiltonian. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVII.MovingFrames
open scoped BigOperators Matrix
variable {n : Type*} [Fintype n]
theorem matrix_product_derivative (A B : ℝ → Matrix n n ℂ)
    (dA dB : Matrix n n ℂ) (t : ℝ)
    (ha : ∀ i j, HasDerivAt (fun s => A s i j) (dA i j) t)
    (hb : ∀ i j, HasDerivAt (fun s => B s i j) (dB i j) t) (i j : n) :
    HasDerivAt (fun s => (A s * B s) i j) ((dA * B t + A t * dB) i j) t := by
  simpa only [Matrix.mul_apply, Matrix.add_apply, Pi.mul_apply, Finset.sum_add_distrib] using
    HasDerivAt.fun_sum (u := Finset.univ) (fun k _ => (ha i k).mul (hb k j))

theorem matrix_vector_derivative (A : ℝ → Matrix n n ℂ) (y : ℝ → n → ℂ)
    (dA : Matrix n n ℂ) (dy : n → ℂ) (t : ℝ)
    (ha : ∀ i j, HasDerivAt (fun s => A s i j) (dA i j) t)
    (hy : ∀ i, HasDerivAt (fun s => y s i) (dy i) t) (i : n) :
    HasDerivAt (fun s => (A s *ᵥ y s) i) ((dA *ᵥ y t + A t *ᵥ dy) i) t := by
  simpa only [Matrix.mulVec, dotProduct, Pi.add_apply, Pi.mul_apply, Finset.sum_add_distrib] using
    HasDerivAt.fun_sum (u := Finset.univ) (fun j _ => (ha i j).mul (hy j))

omit [Fintype n] in
theorem adjoint_derivative (U : ℝ → Matrix n n ℂ) (dU : Matrix n n ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t) (i j : n) :
    HasDerivAt (fun s => (U s).conjTranspose i j) (dU.conjTranspose i j) t := by
  exact (hu j i).star

theorem differentiated_unitarity [DecidableEq n]
    (U : ℝ → Matrix n n ℂ) (dU : Matrix n n ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t)
    (hunit : ∀ s, (U s).conjTranspose * U s = 1) :
    dU.conjTranspose * U t + (U t).conjTranspose * dU = 0 := by
  ext i j
  have h := matrix_product_derivative (fun s => (U s).conjTranspose) U
    dU.conjTranspose dU t (adjoint_derivative U dU t hu) hu i j
  have heq : (fun s => ((U s).conjTranspose * U s) i j) =
      fun _ => (1 : Matrix n n ℂ) i j := by
    funext s
    rw [hunit]
  rw [heq] at h
  exact h.unique (hasDerivAt_const t ((1 : Matrix n n ℂ) i j))

theorem frame_velocity_skew [DecidableEq n]
    (U : ℝ → Matrix n n ℂ) (dU : Matrix n n ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t)
    (hunit : ∀ s, (U s).conjTranspose * U s = 1) :
    ((U t).conjTranspose * dU).conjTranspose = -((U t).conjTranspose * dU) := by
  rw [Matrix.conjTranspose_mul, Matrix.conjTranspose_conjTranspose]
  exact (add_eq_zero_iff_eq_neg).mp (differentiated_unitarity U dU t hu hunit)

theorem connection_hermitian [DecidableEq n]
    (U : ℝ → Matrix n n ℂ) (dU : Matrix n n ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t)
    (hunit : ∀ s, (U s).conjTranspose * U s = 1) :
    ((-Complex.I) • ((U t).conjTranspose * dU)).conjTranspose =
      (-Complex.I) • ((U t).conjTranspose * dU) := by
  rw [Matrix.conjTranspose_smul, frame_velocity_skew U dU t hu hunit]
  simp

def effectiveHamiltonian (U H dU : Matrix n n ℂ) : Matrix n n ℂ :=
  U.conjTranspose * H * U + (-Complex.I) • (U.conjTranspose * dU)

theorem effective_hamiltonian_hermitian [DecidableEq n]
    (U : ℝ → Matrix n n ℂ) (H dU : Matrix n n ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t)
    (hunit : ∀ s, (U s).conjTranspose * U s = 1)
    (hH : H.conjTranspose = H) :
    (effectiveHamiltonian (U t) H dU).conjTranspose =
      effectiveHamiltonian (U t) H dU := by
  simp only [effectiveHamiltonian, Matrix.conjTranspose_add,
    connection_hermitian U dU t hu hunit, Matrix.conjTranspose_mul,
    Matrix.conjTranspose_conjTranspose, hH, Matrix.mul_assoc]

theorem moving_frame_equation [DecidableEq n]
    (U : ℝ → Matrix n n ℂ) (psi y : ℝ → n → ℂ)
    (H dU : Matrix n n ℂ) (dpsi dy : n → ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t)
    (hp : ∀ i, HasDerivAt (fun s => psi s i) (dpsi i) t)
    (hy : ∀ i, HasDerivAt (fun s => y s i) (dy i) t)
    (hunit : (U t).conjTranspose * U t = 1)
    (hcoord : ∀ s, psi s = U s *ᵥ y s)
    (hsch : Complex.I • dpsi = H *ᵥ psi t) :
    Complex.I • dy = effectiveHamiltonian (U t) H dU *ᵥ y t := by
  have hdiff : dpsi = dU *ᵥ y t + U t *ᵥ dy := by
    funext i
    have h := matrix_vector_derivative U y dU dy t hu hy i
    have heq : (fun s => (U s *ᵥ y s) i) = fun s => psi s i := by
      funext s
      rw [hcoord]
    rw [heq] at h
    exact (h.unique (hp i)).symm
  rw [hdiff, smul_add, hcoord t] at hsch
  have he := congrArg (fun v => (U t).conjTranspose *ᵥ v) hsch
  simp only [Matrix.mulVec_add, Matrix.mulVec_smul, Matrix.mulVec_mulVec,
    hunit, Matrix.one_mulVec] at he
  simp only [effectiveHamiltonian, Matrix.add_mulVec, neg_smul, Matrix.neg_mulVec, Matrix.smul_mulVec]
  rw [← sub_eq_add_neg]
  apply eq_sub_iff_add_eq.mpr
  simpa only [add_comm, Matrix.mul_assoc] using he

theorem moving_frame_coordinates [DecidableEq n]
    (U : ℝ → Matrix n n ℂ) (psi : ℝ → n → ℂ)
    (H dU : Matrix n n ℂ) (dpsi : n → ℂ) (t : ℝ)
    (hu : ∀ i j, HasDerivAt (fun s => U s i j) (dU i j) t)
    (hp : ∀ i, HasDerivAt (fun s => psi s i) (dpsi i) t)
    (hleft : ∀ s, (U s).conjTranspose * U s = 1)
    (hright : ∀ s, U s * (U s).conjTranspose = 1)
    (hsch : Complex.I • dpsi = H *ᵥ psi t)
    (hH : H.conjTranspose = H) :
    let y := fun s => (U s).conjTranspose *ᵥ psi s
    let dy := dU.conjTranspose *ᵥ psi t + (U t).conjTranspose *ᵥ dpsi
    (∀ i, HasDerivAt (fun s => y s i) (dy i) t) ∧
      Complex.I • dy = effectiveHamiltonian (U t) H dU *ᵥ y t ∧
      (effectiveHamiltonian (U t) H dU).conjTranspose =
        effectiveHamiltonian (U t) H dU := by
  dsimp only
  have hy := matrix_vector_derivative (fun s => (U s).conjTranspose) psi
    dU.conjTranspose dpsi t (adjoint_derivative U dU t hu) hp
  refine ⟨hy, ?_, effective_hamiltonian_hermitian U H dU t hu hleft hH⟩
  apply moving_frame_equation U psi (fun s => (U s).conjTranspose *ᵥ psi s)
    H dU dpsi _ t hu hp hy (hleft t) _ hsch
  intro s
  rw [Matrix.mulVec_mulVec, hright, Matrix.one_mulVec]
end KomorebiPaperVII.MovingFrames

#print axioms KomorebiPaperVII.MovingFrames.matrix_product_derivative
#print axioms KomorebiPaperVII.MovingFrames.matrix_vector_derivative
#print axioms KomorebiPaperVII.MovingFrames.adjoint_derivative
#print axioms KomorebiPaperVII.MovingFrames.differentiated_unitarity
#print axioms KomorebiPaperVII.MovingFrames.frame_velocity_skew
#print axioms KomorebiPaperVII.MovingFrames.connection_hermitian
#print axioms KomorebiPaperVII.MovingFrames.effective_hamiltonian_hermitian
#print axioms KomorebiPaperVII.MovingFrames.moving_frame_equation
#print axioms KomorebiPaperVII.MovingFrames.moving_frame_coordinates
