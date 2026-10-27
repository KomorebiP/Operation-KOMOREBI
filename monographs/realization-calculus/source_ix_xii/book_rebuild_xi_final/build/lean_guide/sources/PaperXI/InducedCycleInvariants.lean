import PaperXI.CyclicInducedWrap
import PaperXI.CycleCoordinates

/-! Frobenius invariants of genuine degree-kernel induction. The basis and its
closing scalar are constructed from the inducing character. No cyclic matrix,
characteristic polynomial or return-map certificate is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InducedCycleInvariants
open Polynomial PaperXI.CyclicInduced
open scoped Classical
variable {G : Type*} [Group G]
variable (δ : G →* Multiplicative ℤ) (φ : G)
variable (hφ : δ φ = Multiplicative.ofAdd (1 : ℤ)) (n : ℕ) [NeZero n]
variable (ξ : TameDegree.degreeSubgroup δ n →* ℂˣ)

/-- Residues as bounded integers; the forward map is the literal natural cast. -/
def indexEquiv : Fin n ≃ ZMod n where
  toFun i := (i.val : ZMod n)
  invFun j := ⟨j.val, j.val_lt⟩
  left_inv i := by apply Fin.ext; simp [Nat.mod_eq_of_lt i.isLt]
  right_inv j := by simp

/-- The actual induced basis with a `Fin n` index for cyclic polynomial theorems. -/
def basis : Module.Basis (Fin n) ℂ (DegreeIndSpace δ n ξ) :=
  (degreeBasis δ φ hφ n ξ).reindex (indexEquiv n).symm

@[simp] theorem basis_apply (i : Fin n) :
    basis δ φ hφ n ξ i = degreeBasis δ φ hφ n ξ (i.val : ZMod n) := by
  simp [basis, indexEquiv]

/-- The whole return scalar belongs to the full inducing character. -/
def returnScalar : ℂˣ := ξ (degreePeriod φ δ hφ)

include hφ in
/-- The dimension of this induction does not require regularity. -/
theorem dimension : Module.finrank ℂ (DegreeIndSpace δ n ξ) = n := by
  simpa using Module.finrank_eq_card_basis (basis δ φ hφ n ξ)

/-- The actual Frobenius operator advances every non-wrapping basis vector. -/
theorem step (i : Fin n) (hi : i.val + 1 < n) :
    degreeInduced δ n ξ φ (basis δ φ hφ n ξ i) =
      basis δ φ hφ n ξ ⟨i.val + 1, hi⟩ := by
  rw [basis_apply, basis_apply]
  have hv : (i.val : ZMod n).val + 1 < n := by
    simpa [ZMod.val_natCast, Nat.mod_eq_of_lt i.isLt] using hi
  simpa [Nat.cast_add, Nat.cast_one] using
    degreeBasis_phi_of_lt φ δ hφ ξ (i.val : ZMod n) hv

/-- The wrapping step carries `ξ(φ^n)`, including degree one. -/
theorem closing_step (hn : 0 < n) :
    degreeInduced δ n ξ φ (basis δ φ hφ n ξ ⟨n - 1, by omega⟩) =
      (returnScalar δ φ hφ n ξ : ℂ) • basis δ φ hφ n ξ ⟨0, hn⟩ := by
  rw [basis_apply, basis_apply]
  have hl : ((n - 1 : ℕ) : ZMod n).val + 1 = n := by
    rw [ZMod.val_natCast, Nat.mod_eq_of_lt (by omega : n - 1 < n)]
    omega
  simpa [returnScalar] using degreeBasis_phi_of_last φ δ hφ ξ ((n - 1 : ℕ) : ZMod n) hl

/-- A cyclic orbit basis is a conclusion of the literal induction formulas. -/
theorem basis_powers (hn : 0 < n) (i : Fin n) :
    basis δ φ hφ n ξ i = (degreeInduced δ n ξ φ ^ (i : ℕ))
      (basis δ φ hφ n ξ ⟨0, hn⟩) :=
  CycleCoordinates.basis_eq_powers _ hn (basis δ φ hφ n ξ)
    (step δ φ hφ n ξ) i

include hφ in
/-- Finite dimension is derived from the constructed induced basis. -/
theorem finiteSpace : FiniteDimensional ℂ (DegreeIndSpace δ n ξ) :=
  Module.Finite.of_basis (basis δ φ hφ n ξ)

variable [FiniteDimensional ℂ (DegreeIndSpace δ n ξ)]

/-- The Frobenius characteristic polynomial and determinant of actual induction. -/
theorem cycle_invariants :
    (degreeInduced δ n ξ φ).charpoly = X ^ n - C (returnScalar δ φ hφ n ξ : ℂ) ∧
    (degreeInduced δ n ξ φ).det = (-1) ^ (n - 1) * (returnScalar δ φ hφ n ξ : ℂ) := by
  exact CycleCoordinates.cycle_formula _ (Nat.pos_of_ne_zero (NeZero.ne n))
    (basis δ φ hφ n ξ) (step δ φ hφ n ξ) _
    (closing_step δ φ hφ n ξ (Nat.pos_of_ne_zero (NeZero.ne n)))

/-- Read the return value from an intrinsic polynomial coefficient. -/
theorem returnScalar_from_charpoly :
    (returnScalar δ φ hφ n ξ : ℂ) = -((degreeInduced δ n ξ φ).charpoly.coeff 0) := by
  rw [(cycle_invariants δ φ hφ n ξ).1]
  simp [Ne.symm (NeZero.ne n)]

/-- The ambient determinant polynomial is not yet the inertia-fixed polynomial. -/
theorem ambient_polynomial :
    Matrix.det (1 - (X : ℂ[X]) •
      (LinearMap.toMatrix (basis δ φ hφ n ξ) (basis δ φ hφ n ξ)
        (degreeInduced δ n ξ φ)).map C) =
      1 - C (returnScalar δ φ hφ n ξ : ℂ) * X ^ n := by
  exact CycleCoordinates.cycle_local_polynomial _ (Nat.pos_of_ne_zero (NeZero.ne n))
    (basis δ φ hφ n ξ) (step δ φ hφ n ξ) _
    (closing_step δ φ hφ n ξ (Nat.pos_of_ne_zero (NeZero.ne n)))

/-- The full return operator is scalar, not just its action on one seed. -/
theorem return_operator :
    degreeInduced δ n ξ φ ^ n =
      (returnScalar δ φ hφ n ξ : ℂ) • LinearMap.id := by
  have h := (degreeInduced δ n ξ φ).aeval_self_charpoly
  rw [(cycle_invariants δ φ hφ n ξ).1] at h
  simpa only [map_sub, map_pow, aeval_X, aeval_C, Algebra.algebraMap_eq_smul_one,
    Module.End.one_eq_id, sub_eq_zero] using h

end PaperXI.InducedCycleInvariants
