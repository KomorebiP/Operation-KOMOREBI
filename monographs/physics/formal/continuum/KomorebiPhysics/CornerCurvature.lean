module

public import KomorebiPhysics.CornerDerivation

/-!
Full physics master, Chapter 7.4, equations (7.24)--(7.30).
Curvature is the Hermitian matrix `F_ij = i[K_i,K_j]`; the commutator of
the two inner derivations is proved to equal `δ_F` by the Jacobi identity.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
set_option linter.unusedSectionVars false
namespace KomorebiPhysics.CornerCurvature

open CornerDerivation

variable {n : Type*} [Fintype n] [DecidableEq n]
local notation "Mat" => Matrix n n ℂ

/-- Ordinary noncommutative commutator. -/
def commutator (A B : Mat) : Mat := A * B - B * A

/-- Finite corner curvature `i[K,L]`. -/
def curvature (K L : Mat) : Mat := Complex.I • commutator K L

@[simp] theorem commutator_self (K : Mat) : commutator K K = 0 := by simp [commutator]

@[simp] theorem curvature_self (K : Mat) : curvature K K = 0 := by simp [curvature]

theorem commutator_swap (K L : Mat) : commutator L K = -(commutator K L) := by
  unfold commutator
  noncomm_ring

theorem curvature_swap (K L : Mat) : curvature L K = -(curvature K L) := by
  unfold curvature
  rw [commutator_swap]
  module

theorem curvature_eq_zero_of_commute {K L : Mat} (h : K * L = L * K) : curvature K L = 0 := by
  simp [curvature, commutator, h]

theorem curvature_eq_zero_iff (K L : Mat) : curvature K L = 0 ↔ K * L = L * K := by
  unfold curvature commutator
  constructor
  · intro h
    have hi : (Complex.I : ℂ) ≠ 0 := by norm_num
    have hs : K * L - L * K = 0 := (smul_eq_zero.mp h).resolve_left hi
    exact sub_eq_zero.mp hs
  · intro h
    rw [h, sub_self, smul_zero]

/-- Hermitian generators produce Hermitian curvature. -/
theorem curvature_hermitian (K L : Mat)
    (hK : K.conjTranspose = K) (hL : L.conjTranspose = L) :
    (curvature K L).conjTranspose = curvature K L := by
  unfold curvature commutator
  rw [Matrix.conjTranspose_smul, Matrix.conjTranspose_sub,
    Matrix.conjTranspose_mul, Matrix.conjTranspose_mul, hK, hL]
  simp
  module

/-- `δ_K` acts on the ordinary commutator by the Leibniz/Jacobi expansion. -/
theorem delta_commutator (K A B : Mat) :
    delta K (commutator A B) = commutator (delta K A) B + commutator A (delta K B) := by
  unfold commutator
  rw [delta_sub, delta_mul, delta_mul]
  noncomm_ring

/-- Ordinary adjoint actions satisfy the Jacobi commutator identity. -/
theorem commutator_jacobi (K L X : Mat) :
    commutator K (commutator L X) - commutator L (commutator K X) =
      commutator (commutator K L) X := by
  unfold commutator
  noncomm_ring

/-- Two successive `δ` operations expose the factor `i²=-1`. -/
theorem delta_delta (K L X : Mat) :
    delta K (delta L X) = -(commutator K (commutator L X)) := by
  unfold CornerDerivation.delta
  rw [mul_smul_comm, smul_mul_assoc, ← smul_sub, smul_smul]
  have hi : (Complex.I : ℂ) * Complex.I = -1 := by norm_num
  rw [hi, neg_one_smul]
  rfl

/-- Curvature acts through the same `i²=-1` factor. -/
theorem delta_curvature (K L X : Mat) :
    delta (curvature K L) X = -(commutator (commutator K L) X) := by
  unfold CornerDerivation.delta curvature
  rw [smul_mul_assoc, mul_smul_comm, ← smul_sub, smul_smul]
  have hi : (Complex.I : ℂ) * Complex.I = -1 := by norm_num
  rw [hi, neg_one_smul]
  rfl

/-- Finite curvature identity, equation (7.25). -/
theorem derivation_commutator (K L X : Mat) :
    delta K (delta L X) - delta L (delta K X) = delta (curvature K L) X := by
  rw [delta_delta, delta_delta, delta_curvature]
  have h := commutator_jacobi K L X
  rw [← h]
  abel

/-- Equivalent additive form of the curvature identity. -/
theorem derivation_commutator_add (K L X : Mat) :
    delta K (delta L X) = delta L (delta K X) + delta (curvature K L) X := by
  have h := derivation_commutator K L X
  have hh := congrArg (fun Z => Z + delta L (delta K X)) h
  simpa [sub_eq_add_neg, add_assoc, add_comm, add_left_comm] using hh

/-- Commuting generators yield commuting finite derivations. -/
theorem derivations_commute_of_generators_commute {K L : Mat}
    (h : K * L = L * K) (X : Mat) :
    delta K (delta L X) = delta L (delta K X) := by
  rw [derivation_commutator_add, curvature_eq_zero_of_commute h, delta_zero_generator, add_zero]

/-- Curvature itself is annihilated by either generator when the corresponding
nested commutator vanishes. -/
theorem delta_curvature_eq_zero_of_commute {K L : Mat}
    (h : K * L = L * K) : delta K (curvature K L) = 0 := by
  rw [curvature_eq_zero_of_commute h, delta_zero]

/-- The curvature derivation is traceless on every matrix. -/
theorem trace_curvature_derivation (K L X : Mat) :
    Matrix.trace (delta (curvature K L) X) = 0 :=
  trace_delta _ _

/-- The curvature derivation obeys the same finite integration-by-parts law. -/
theorem curvature_integration_by_parts (K L X Y : Mat) :
    Matrix.trace (delta (curvature K L) X * Y) =
      - Matrix.trace (X * delta (curvature K L) Y) :=
  trace_integration_by_parts _ _ _

/-- If the curvature matrix is scalar, the commutator of derivations vanishes.
This records the exact distinction between matrix curvature and its inner action. -/
theorem central_curvature_gives_commuting_derivations (K L X : Mat) (c : ℂ)
    (hF : curvature K L = c • (1 : Mat)) :
    delta K (delta L X) = delta L (delta K X) := by
  rw [derivation_commutator_add, hF, delta_scalar_identity, add_zero]

end KomorebiPhysics.CornerCurvature
