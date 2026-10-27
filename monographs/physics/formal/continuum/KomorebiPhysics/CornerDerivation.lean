module

public import KomorebiPhysics.PointwiseNoGo
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose
public import Mathlib.Tactic.NoncommRing

/-!
Full physics master, Chapter 7.3, equations (7.12)--(7.23).
The finite differential operator is the actual inner derivation
`δ_K X = i [K,X]` on complex matrices. Multiplication order is never
commuted implicitly.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
set_option linter.unusedSectionVars false
namespace KomorebiPhysics.CornerDerivation

open scoped BigOperators

variable {n : Type*} [Fintype n] [DecidableEq n]
local notation "Mat" => Matrix n n ℂ

/-- The finite corner derivation `i[K,X]`. -/
def delta (K X : Mat) : Mat := Complex.I • (K * X - X * K)

@[simp] theorem delta_zero (K : Mat) : delta K 0 = 0 := by simp [delta]

@[simp] theorem delta_one (K : Mat) : delta K 1 = 0 := by simp [delta]

@[simp] theorem delta_self (K : Mat) : delta K K = 0 := by simp [delta]

@[simp] theorem delta_zero_generator (X : Mat) : delta 0 X = 0 := by simp [delta]

theorem delta_add (K X Y : Mat) : delta K (X + Y) = delta K X + delta K Y := by
  unfold delta
  rw [Matrix.mul_add, Matrix.add_mul, sub_eq_add_neg, neg_add_rev, smul_add]
  module

theorem delta_neg (K X : Mat) : delta K (-X) = -(delta K X) := by
  unfold delta
  simp only [Matrix.mul_neg, Matrix.neg_mul]
  module

theorem delta_sub (K X Y : Mat) : delta K (X - Y) = delta K X - delta K Y := by
  rw [sub_eq_add_neg, delta_add, delta_neg]
  rfl

theorem delta_smul (K X : Mat) (c : ℂ) : delta K (c • X) = c • delta K X := by
  unfold delta
  simp only [Matrix.mul_smul, Matrix.smul_mul, smul_sub, smul_smul]
  rw [mul_comm Complex.I c]

/-- Exact Leibniz identity, equation (7.14). -/
theorem delta_mul (K X Y : Mat) :
    delta K (X * Y) = delta K X * Y + X * delta K Y := by
  unfold delta
  calc
    Complex.I • (K * (X * Y) - (X * Y) * K) =
        Complex.I • ((K * X - X * K) * Y + X * (K * Y - Y * K)) := by
          congr 1
          noncomm_ring
    _ = (Complex.I • (K * X - X * K)) * Y +
        X * (Complex.I • (K * Y - Y * K)) := by
          rw [smul_add, smul_mul_assoc, mul_smul_comm]

/-- Commuting matrices are killed by the derivation. -/
theorem delta_eq_zero_of_commute {K X : Mat} (h : K * X = X * K) : delta K X = 0 := by
  unfold delta
  rw [h, sub_self, smul_zero]

/-- Vanishing is equivalent to commutation. -/
theorem delta_eq_zero_iff (K X : Mat) : delta K X = 0 ↔ K * X = X * K := by
  constructor
  · intro h
    have hi : (Complex.I : ℂ) ≠ 0 := by norm_num
    have hz : K * X - X * K = 0 := by
      have hs : Complex.I • (K * X - X * K) = 0 := by simpa [delta] using h
      exact (smul_eq_zero.mp hs).resolve_left hi
    exact sub_eq_zero.mp hz
  · exact delta_eq_zero_of_commute

/-- Hermitian `K` makes `δ_K` star compatible, equation (7.15). -/
theorem delta_conjTranspose (K X : Mat) (hK : K.conjTranspose = K) :
    (delta K X).conjTranspose = delta K X.conjTranspose := by
  unfold delta
  rw [Matrix.conjTranspose_smul, Matrix.conjTranspose_sub,
    Matrix.conjTranspose_mul, Matrix.conjTranspose_mul, hK]
  simp
  module

/-- Hermitian inputs are carried to Hermitian outputs. -/
theorem delta_preserves_hermitian (K X : Mat)
    (hK : K.conjTranspose = K) (hX : X.conjTranspose = X) :
    (delta K X).conjTranspose = delta K X := by
  rw [delta_conjTranspose K X hK, hX]

/-- Trace of an inner derivation vanishes. -/
theorem trace_delta (K X : Mat) : Matrix.trace (delta K X) = 0 := by
  unfold delta
  rw [Matrix.trace_smul, Matrix.trace_sub, Matrix.trace_mul_comm K X, sub_self, smul_zero]

/-- Exact finite integration by parts, equation (7.16). -/
theorem trace_integration_by_parts (K X Y : Mat) :
    Matrix.trace (delta K X * Y) = - Matrix.trace (X * delta K Y) := by
  have h := trace_delta K (X * Y)
  rw [delta_mul, Matrix.trace_add] at h
  exact eq_neg_of_add_eq_zero_left h

/-- Equivalent zero-sum trace pairing. -/
theorem trace_delta_mul_add (K X Y : Mat) :
    Matrix.trace (delta K X * Y) + Matrix.trace (X * delta K Y) = 0 := by
  rw [trace_integration_by_parts]
  simp

/-- Trace preservation is also a direct corollary of integration by parts. -/
theorem trace_delta_from_ibp (K X : Mat) : Matrix.trace (delta K X) = 0 := by
  have h := trace_integration_by_parts K X (1 : Mat)
  simpa using h

/-- Triple-product Leibniz expansion. -/
theorem delta_mul_three (K X Y Z : Mat) :
    delta K (X * Y * Z) =
      delta K X * Y * Z + X * delta K Y * Z + X * Y * delta K Z := by
  rw [delta_mul K (X * Y) Z, delta_mul K X Y]
  noncomm_ring

/-- Scalar multiples of the identity generate the zero derivation. -/
theorem delta_scalar_identity (K : Mat) (c : ℂ) : delta (c • (1 : Mat)) K = 0 := by
  unfold delta
  simp

end KomorebiPhysics.CornerDerivation
