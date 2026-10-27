import FiniteFourier
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.LinearAlgebra.Matrix.ConjTranspose
import Mathlib.Tactic.Ring

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 2000000

open scoped BigOperators Matrix

namespace Komorebi.QuantumArithmetic

/-- The exact coordinate arithmetic is interpreted in the ordinary complex numbers. -/
noncomputable def interpret (x : Cyclo12) : ℂ :=
  ⟨(x.a : ℝ) + (x.b : ℝ) * Real.sqrt 3,
   (x.c : ℝ) + (x.d : ℝ) * Real.sqrt 3⟩

@[simp] theorem interpret_zero : interpret cZero = 0 := by
  apply Complex.ext <;> simp [interpret, cZero]

@[simp] theorem interpret_one : interpret cOne = 1 := by
  apply Complex.ext <;> simp [interpret, cOne]

@[simp] theorem interpret_rat (r : ℚ) : interpret (cRat r) = (r : ℂ) := by
  apply Complex.ext <;> simp [interpret, cRat]

@[simp] theorem interpret_add (x y : Cyclo12) :
    interpret (cAdd x y) = interpret x + interpret y := by
  apply Complex.ext <;> simp [interpret, cAdd] <;> ring

@[simp] theorem interpret_mul (x y : Cyclo12) :
    interpret (cMul x y) = interpret x * interpret y := by
  apply Complex.ext <;> simp [interpret, cMul, Complex.mul_re, Complex.mul_im] <;>
    ring_nf <;> norm_num [Real.sq_sqrt]

@[simp] theorem interpret_conj (x : Cyclo12) :
    interpret (cConj x) = star (interpret x) := by
  apply Complex.ext <;> simp [interpret, cConj]
  ring

@[simp] theorem interpret_pow (x : Cyclo12) (n : Nat) :
    interpret (cPow x n) = interpret x ^ n := by
  induction n with
  | zero => simp [cPow]
  | succ n ih => simp [cPow, ih, pow_succ]

@[simp] theorem interpret_sum (xs : List Cyclo12) :
    interpret (cSum xs) = (xs.map interpret).sum := by
  induction xs with
  | nil => simp [cSum]
  | cons x xs ih => simp [cSum, ih]

@[simp] theorem interpret_kSum (f : Index → Cyclo12) :
    interpret (kSum f) = ∑ i, interpret (f i) := by
  simp only [kSum, interpret_sum, List.map_ofFn, List.sum_ofFn]
  rfl

noncomputable def complexMatrix (A : KMatrix) : Matrix Index Index ℂ :=
  fun i j => interpret (A i j)

noncomputable def complexVector (v : KVector) : Index → ℂ :=
  fun i => interpret (v i)

@[simp] theorem complexMatrix_mul (A B : KMatrix) :
    complexMatrix (kMatMul A B) = complexMatrix A * complexMatrix B := by
  ext i j
  simp [complexMatrix, kMatMul, Matrix.mul_apply]

@[simp] theorem complexMatrix_adjoint (A : KMatrix) :
    complexMatrix (kAdjoint A) = (complexMatrix A)ᴴ := by
  ext i j
  simp [complexMatrix, kAdjoint, Matrix.conjTranspose_apply]

@[simp] theorem complexMatrix_identity :
    complexMatrix kIdentity = 1 := by
  ext i j
  by_cases h : i = j <;> simp [complexMatrix, kIdentity, h, Matrix.one_apply]

@[simp] theorem complexVector_mul (A : KMatrix) (v : KVector) :
    complexVector (kMatVec A v) = (complexMatrix A).mulVec (complexVector v) := by
  ext i
  simp [complexVector, complexMatrix, kMatVec, Matrix.mulVec, dotProduct]

noncomputable def F : Matrix Index Index ℂ := complexMatrix exactFourier
noncomputable def P : Matrix Index Index ℂ := complexMatrix exactProjector
noncomputable def D : Matrix Index Index ℂ :=
  Matrix.diagonal (fun i => if Nat.gcd i.val 12 = 1 then 1 else 0)
noncomputable def psi : Index → ℂ := complexVector exactPsi
noncomputable def chi : Index → ℂ := complexVector exactChi
noncomputable def unitState : Index → ℂ := complexVector exactUnitState

/-- Actual complex unitarity, not an assertion only about the coordinate checker. -/
theorem fourier_unitary_left : Fᴴ * F = 1 := by
  have h : kMatMul (kAdjoint exactFourier) exactFourier = kIdentity :=
    funext (fun i => funext (normalized_fourier_left i))
  simpa [F] using congrArg complexMatrix h

theorem fourier_unitary_right : F * Fᴴ = 1 := by
  have h : kMatMul exactFourier (kAdjoint exactFourier) = kIdentity :=
    funext (fun i => funext (normalized_fourier_right i))
  simpa [F] using congrArg complexMatrix h

theorem projector_transport : F * D * Fᴴ = P := by
  ext i j
  have h := congrArg interpret (exact_projector_transport i j)
  simp only [selectedKernel, interpret_kSum] at h
  rw [Matrix.mul_apply]
  simpa [D, P, F, complexMatrix, Matrix.mul_diagonal, Matrix.conjTranspose_apply,
    apply_ite interpret, mul_ite] using h

theorem state_preparation : F.mulVec unitState = psi := by
  have h : kMatVec exactFourier exactUnitState = exactPsi :=
    funext exact_state_preparation
  simpa [F, unitState, psi] using congrArg complexVector h

theorem state_recovery : Fᴴ.mulVec psi = unitState := by
  have h : kMatVec (kAdjoint exactFourier) exactPsi = exactUnitState :=
    funext exact_state_recovery
  simpa [F, unitState, psi] using congrArg complexVector h

@[simp] theorem interpret_normSq (z : Cyclo12) :
    interpret (kNormSq z) = (Complex.normSq (interpret z) : ℂ) := by
  simp only [kNormSq, interpret_mul, interpret_conj]
  exact Complex.normSq_eq_conj_mul_self.symm

noncomputable def totalProbability (v : Index → ℂ) : ℝ :=
  ∑ i, Complex.normSq (v i)

noncomputable def coprimeProbability (v : Index → ℂ) : ℝ :=
  ∑ i, if Nat.gcd i.val 12 = 1 then Complex.normSq (v i) else 0

@[simp] theorem interpret_mass (v : KVector) :
    interpret (kMass v) = (totalProbability (complexVector v) : ℂ) := by
  simp [kMass, totalProbability, complexVector]

@[simp] theorem interpret_coprimeMass (v : KVector) :
    interpret (kCoprimeMass v) = (coprimeProbability (complexVector v) : ℂ) := by
  simp only [kCoprimeMass, interpret_kSum, coprimeProbability, Complex.ofReal_sum]
  apply Finset.sum_congr rfl
  intro i hi
  by_cases h : Nat.gcd i.val 12 = 1 <;>
    simp [h, complexVector]

theorem psi_normalized : totalProbability psi = 1 := by
  have h := congrArg interpret exact_psi_normalized
  simpa [psi] using congrArg Complex.re h

theorem chi_normalized : totalProbability chi = 1 := by
  have h := congrArg interpret exact_chi_normalized
  simpa [chi] using congrArg Complex.re h

theorem unitState_normalized : totalProbability unitState = 1 := by
  have h := congrArg interpret exact_unit_normalized
  simpa [unitState] using congrArg Complex.re h

theorem same_initial_probabilities (i : Index) :
    Complex.normSq (psi i) = Complex.normSq (chi i) := by
  have h := congrArg interpret (exact_same_initial_probabilities i)
  simpa [psi, chi, complexVector] using congrArg Complex.re h

theorem states_orthogonal : ∑ i, star (psi i) * chi i = 0 := by
  have h := congrArg interpret exact_orthogonal_states
  simpa [psi, chi, complexVector] using h

theorem signed_state_recovers_arithmetic :
    coprimeProbability (Fᴴ.mulVec psi) = 1 := by
  have h := congrArg interpret exact_coprime_mass_psi
  simpa [F, psi] using congrArg Complex.re h

theorem unsigned_state_erases_arithmetic :
    coprimeProbability (Fᴴ.mulVec chi) = 0 := by
  have h := congrArg interpret exact_coprime_mass_chi
  simpa [F, chi] using congrArg Complex.re h

theorem projector_fixes_psi : P.mulVec psi = psi := by
  have h : kMatVec exactProjector exactPsi = exactPsi :=
    funext exact_projector_fixes_psi
  simpa [P, psi] using congrArg complexVector h

theorem projector_kills_chi : P.mulVec chi = 0 := by
  have h : kMatVec exactProjector exactChi = fun _ => cZero :=
    funext exact_projector_kills_chi
  have hh := congrArg complexVector h
  rw [complexVector_mul] at hh
  change P.mulVec chi = complexVector (fun _ => cZero) at hh
  rw [hh]
  funext i
  exact interpret_zero

end Komorebi.QuantumArithmetic
