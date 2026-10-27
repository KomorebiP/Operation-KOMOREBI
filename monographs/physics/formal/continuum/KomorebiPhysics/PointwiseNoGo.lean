module

public import Mathlib.Algebra.Algebra.Basic
public import Mathlib.LinearAlgebra.Pi
public import Mathlib.Tactic

/-!
Full physics master, Chapter 7.1--7.2, equations (7.1)--(7.11).
The no-go theorem is stated only for a finite product of copies of `ℂ` with
pointwise multiplication and an actual `ℂ`-linear Leibniz map.  It is not
promoted to an arbitrary finite-dimensional commutative algebra.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.PointwiseNoGo

open scoped BigOperators

/-- The finite pointwise algebra `ℂ^ι`. -/
abbrev PointAlgebra (ι : Type*) := ι → ℂ

/-- Primitive coordinate idempotent. -/
def atom {ι : Type*} [DecidableEq ι] (a : ι) : PointAlgebra ι :=
  fun b => if b = a then 1 else 0

@[simp] theorem atom_apply_same {ι : Type*} [DecidableEq ι] (a : ι) :
    atom a a = 1 := by simp [atom]

@[simp] theorem atom_apply_ne {ι : Type*} [DecidableEq ι] {a b : ι} (h : b ≠ a) :
    atom a b = 0 := by simp [atom, h]

@[simp] theorem atom_mul_self {ι : Type*} [DecidableEq ι] (a : ι) :
    atom a * atom a = atom a := by
  funext b
  by_cases h : b = a <;> simp [atom, h]

@[simp] theorem atom_mul_atom {ι : Type*} [DecidableEq ι] (a b : ι) :
    atom a * atom b = if a = b then atom a else 0 := by
  by_cases h : a = b
  · subst b
    simp
  · funext c
    by_cases hca : c = a
    · subst c
      simp [atom, h]
    · simp [atom, h, hca]

/-- Multiplying by a primitive idempotent isolates one coordinate. -/
theorem atom_mul_function {ι : Type*} [DecidableEq ι] (a : ι) (f : PointAlgebra ι) :
    atom a * f = (f a) • atom a := by
  funext b
  by_cases h : b = a
  · subst b
    simp [atom]
  · simp [atom, h]

/-- The primitive idempotents resolve the pointwise identity. -/
theorem sum_atoms {ι : Type*} [Fintype ι] [DecidableEq ι] :
    (∑ a : ι, atom a) = (1 : PointAlgebra ι) := by
  funext b
  simp [atom]

/-- Exact Leibniz property for a complex-linear map on the pointwise algebra. -/
def IsDerivation {ι : Type*} (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) : Prop :=
  ∀ f g, D (f * g) = D f * g + f * D g

/-- Every derivation kills the multiplicative identity. -/
theorem map_one_eq_zero {ι : Type*} (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι)
    (hD : IsDerivation D) : D 1 = 0 := by
  have h := hD 1 1
  have h' : D 1 = D 1 + D 1 := by simpa using h
  have hs := congrArg (fun x => x - D 1) h'
  simpa [sub_eq_add_neg, add_assoc] using hs.symm

/-- Coordinate form of the idempotent argument `D e_a = 2 e_a D e_a`. -/
theorem atom_derivative_coordinate {ι : Type*} [DecidableEq ι]
    (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) (hD : IsDerivation D)
    (a b : ι) :
    D (atom a) b = 2 * atom a b * D (atom a) b := by
  have h := hD (atom a) (atom a)
  rw [atom_mul_self] at h
  have hb := congrFun h b
  simp only [Pi.add_apply, Pi.mul_apply] at hb
  calc
    D (atom a) b = atom a b * D (atom a) b + atom a b * D (atom a) b := by
      simpa [mul_comm] using hb
    _ = 2 * atom a b * D (atom a) b := by ring

/-- Primitive idempotents have zero derivative, coordinate by coordinate. -/
theorem map_atom_eq_zero {ι : Type*} [DecidableEq ι]
    (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) (hD : IsDerivation D) (a : ι) :
    D (atom a) = 0 := by
  funext b
  change D (atom a) b = 0
  have h := atom_derivative_coordinate D hD a b
  by_cases hba : b = a
  · subst b
    simp only [atom_apply_same, mul_one] at h
    have hh : (0 : ℂ) + D (atom a) a = D (atom a) a + D (atom a) a := by
      simpa [two_mul] using h
    exact (add_right_cancel hh).symm
  · simp [atom, hba] at h
    exact h

/-- The Leibniz rule on `e_a f = f(a)e_a` forces every output coordinate to vanish. -/
theorem map_apply_eq_zero {ι : Type*} [DecidableEq ι]
    (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) (hD : IsDerivation D)
    (f : PointAlgebra ι) (a : ι) : D f a = 0 := by
  have hm := atom_mul_function a f
  have hleft : D (atom a * f) = 0 := by
    rw [hm, D.map_smul, map_atom_eq_zero D hD a, smul_zero]
  have hleib := hD (atom a) f
  rw [map_atom_eq_zero D hD a, zero_mul, zero_add] at hleib
  rw [hleib] at hleft
  have ha := congrFun hleft a
  simpa [atom] using ha

/-- Main finite pointwise no-go theorem: the only complex-linear derivation is zero. -/
theorem derivation_eq_zero {ι : Type*} [DecidableEq ι]
    (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) (hD : IsDerivation D) :
    D = 0 := by
  ext f a
  exact map_apply_eq_zero D hD f a

/-- There is exactly one complex-linear derivation on the finite pointwise algebra. -/
theorem derivation_iff_zero {ι : Type*} [DecidableEq ι]
    (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) :
    IsDerivation D ↔ D = 0 := by
  constructor
  · exact derivation_eq_zero D
  · intro h
    subst D
    intro f g
    simp

/-- The zero map really is a derivation, so the no-go theorem is not vacuous. -/
theorem zero_isDerivation {ι : Type*} :
    IsDerivation (0 : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) := by
  intro f g
  simp

/-- Finite-dimensionality is present in the source model, although the algebraic
proof itself only uses coordinate idempotents and scalar linearity. -/
theorem finite_source_no_go {ι : Type*} [Fintype ι] [DecidableEq ι]
    (D : PointAlgebra ι →ₗ[ℂ] PointAlgebra ι) (hD : IsDerivation D) :
    D = 0 := derivation_eq_zero D hD

end KomorebiPhysics.PointwiseNoGo
