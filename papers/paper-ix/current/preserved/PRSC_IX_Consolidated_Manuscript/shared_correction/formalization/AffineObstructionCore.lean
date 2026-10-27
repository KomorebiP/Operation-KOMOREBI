module
public import Mathlib.Data.ZMod.Basic
public import Mathlib.LinearAlgebra.Quotient.Basic
public import Mathlib.Algebra.Module.Pi

/-!
# A finite obstruction for affine integer systems

For any finite affine system A x = b, any modulus p > 0, and any L >= 0,
the next lift of a fixed solution modulo p^L exists exactly when its residual
digit vanishes in an explicitly constructed finite cokernel. No lift or
surjectivity criterion is assumed. This is an affine-linear result, not a
formalization of arbitrary nonlinear native tower objects.
-/

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.NativeAffine

variable {d e : ℕ}

/-- Coordinate reduction, viewed as an integer-linear map. -/
def reduction (p n : ℕ) : (Fin n → ℤ) →ₗ[ℤ] (Fin n → ZMod p) where
  toFun x i := (x i : ZMod p)
  map_add' x y := by ext i; simp
  map_smul' k x := by ext i; simp

/-- The reduction of the actual integer coefficient map. -/
def digitMap (p : ℕ) (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) :
    (Fin d → ℤ) →ₗ[ℤ] (Fin e → ZMod p) :=
  (reduction p e).comp A

/-- A finite cokernel, taken over the underlying integer module. -/
abbrev Obstruction (p : ℕ) (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) :=
  (Fin e → ZMod p) ⧸ LinearMap.range (digitMap p A)

def obstruction (p : ℕ) (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (r : Fin e → ℤ) : Obstruction p A :=
  Submodule.Quotient.mk (reduction p e r)

theorem obstruction_finite (p : ℕ) [NeZero p]
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) : Finite (Obstruction p A) := by
  infer_instance

/-- Cokernel zero is equivalent to an actual correcting vector. -/
theorem obstruction_zero_iff_correction (p : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) (r : Fin e → ℤ) :
    obstruction p A r = 0 ↔ ∃ t : Fin d → ℤ, reduction p e (r + A t) = 0 := by
  change Submodule.Quotient.mk (reduction p e r) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨t, ht⟩
    refine ⟨-t, ?_⟩
    change digitMap p A t = reduction p e r at ht
    simp only [map_add, map_neg]
    change reduction p e r + -(digitMap p A t) = 0
    rw [ht, add_neg_cancel]
  · rintro ⟨t, ht⟩
    refine ⟨-t, ?_⟩
    rw [map_neg]
    have h : reduction p e r + digitMap p A t = 0 := by
      simpa only [map_add, digitMap, LinearMap.comp_apply] using ht
    exact (eq_neg_of_add_eq_zero_left h).symm

/-- Changing the base representative by p^L times a vector adds A s to
the residual, without changing its cokernel class. -/
theorem obstruction_representative_independent (p : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) (r : Fin e → ℤ) (s : Fin d → ℤ) :
    obstruction p A (r + A s) = obstruction p A r := by
  change Submodule.Quotient.mk (reduction p e (r + A s)) = _
  rw [map_add, Submodule.Quotient.mk_add]
  have hs : (Submodule.Quotient.mk (reduction p e (A s)) : Obstruction p A) = 0 := by
    rw [Submodule.Quotient.mk_eq_zero]
    exact ⟨s, rfl⟩
  rw [hs, add_zero]
  rfl

theorem reduction_zero_iff (p : ℕ) (r : Fin e → ℤ) :
    reduction p e r = 0 ↔ ∀ i, (p : ℤ) ∣ r i := by
  constructor
  · intro h i
    exact (ZMod.intCast_zmod_eq_zero_iff_dvd (r i) p).mp (congrFun h i)
  · intro h
    ext i
    exact (ZMod.intCast_zmod_eq_zero_iff_dvd (r i) p).mpr (h i)

/-- Exact residual transport is derived from linearity. -/
theorem affine_residual_transport (q : ℤ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (b r : Fin e → ℤ) (x t : Fin d → ℤ) (hr : A x - b = q • r) :
    A (x + q • t) - b = q • (r + A t) := by
  rw [map_add, map_smul, add_sub_right_comm, hr, smul_add]

/-- A fixed residual digit determines exactly whether the solution lifts
from modulus p^L to p^(L+1). This includes all finite affine integer systems. -/
theorem affine_lift_iff_obstruction_zero (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (b r : Fin e → ℤ) (x : Fin d → ℤ)
    (hr : A x - b = (p : ℤ)^L • r) :
    (∃ t : Fin d → ℤ, ∀ i,
      (p : ℤ)^(L+1) ∣ (A (x + (p : ℤ)^L • t) - b) i) ↔
    obstruction p A r = 0 := by
  rw [obstruction_zero_iff_correction]
  have hq : (p : ℤ)^L ≠ 0 := pow_ne_zero _ (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hp))
  constructor
  · rintro ⟨t, ht⟩
    refine ⟨t, (reduction_zero_iff p (r + A t)).mpr ?_⟩
    intro i
    have hi := ht i
    rw [affine_residual_transport _ A b r x t hr] at hi
    change (p : ℤ)^(L+1) ∣ (p : ℤ)^L * (r + A t) i at hi
    rwa [pow_succ, mul_dvd_mul_iff_left hq] at hi
  · rintro ⟨t, ht⟩
    refine ⟨t, ?_⟩
    intro i
    rw [affine_residual_transport _ A b r x t hr]
    change (p : ℤ)^(L+1) ∣ (p : ℤ)^L * (r + A t) i
    rw [pow_succ, mul_dvd_mul_iff_left hq]
    exact (reduction_zero_iff p (r + A t)).mp ht i

/-- Every solution modulo p^L has a residual vector; the criterion above
does not require an unexplained residual representation assumption. -/
theorem residual_exists (p L : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) (b : Fin e → ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ (A x - b) i) :
    ∃ r : Fin e → ℤ, A x - b = (p : ℤ)^L • r := by
  choose r hr using hx
  exact ⟨r, funext hr⟩

/-- All representatives of one residue vector are obtained by digit correction. -/
theorem same_residue_iff (q : ℤ) (x y : Fin d → ℤ) :
    (∀ i, q ∣ (y - x) i) ↔ ∃ t : Fin d → ℤ, y = x + q • t := by
  constructor
  · intro h
    choose t ht using h
    refine ⟨t, ?_⟩
    ext i
    have hi := ht i
    change y i - x i = q * t i at hi
    change y i = x i + q * t i
    exact sub_eq_iff_eq_add'.mp hi
  · rintro ⟨t, rfl⟩ i
    change q ∣ x i + q * t i - x i
    simp

/-- Every finite affine system has an explicit finite obstruction at each
actual solution, and its vanishing is equivalent to existence of a next-level
solution with the same lower-level residue. -/
theorem finite_affine_obstruction (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ)) (b : Fin e → ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ (A x - b) i) :
    ∃ r : Fin e → ℤ,
      A x - b = (p : ℤ)^L • r ∧
      Finite (Obstruction p A) ∧
      ((∃ y : Fin d → ℤ,
        (∀ i, (p : ℤ)^L ∣ (y - x) i) ∧
        (∀ i, (p : ℤ)^(L+1) ∣ (A y - b) i)) ↔ obstruction p A r = 0) := by
  obtain ⟨r, hr⟩ := residual_exists p L A b x hx
  let : NeZero p := ⟨Nat.ne_of_gt hp⟩
  refine ⟨r, hr, obstruction_finite p A, ?_⟩
  rw [← affine_lift_iff_obstruction_zero p L hp A b r x hr]
  constructor
  · rintro ⟨y, hy, hAy⟩
    obtain ⟨t, rfl⟩ := (same_residue_iff ((p : ℤ)^L) x y).mp hy
    exact ⟨t, hAy⟩
  · rintro ⟨t, ht⟩
    exact ⟨x + (p : ℤ)^L • t,
      (same_residue_iff ((p : ℤ)^L) x _).mpr ⟨t, rfl⟩, ht⟩

#print axioms reduction
#print axioms digitMap
#print axioms Obstruction
#print axioms obstruction
#print axioms obstruction_finite
#print axioms obstruction_zero_iff_correction
#print axioms obstruction_representative_independent
#print axioms reduction_zero_iff
#print axioms affine_residual_transport
#print axioms affine_lift_iff_obstruction_zero
#print axioms residual_exists
#print axioms same_residue_iff
#print axioms finite_affine_obstruction

end Komorebi.NativeAffine
