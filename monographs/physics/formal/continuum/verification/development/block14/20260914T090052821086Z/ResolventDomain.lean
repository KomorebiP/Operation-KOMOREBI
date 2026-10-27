module
public import KomorebiPhysics.GraphDomain
public import Mathlib.Tactic.NoncommRing

/-! Section 6.7. Actual bounded inverses of a partial shifted operator.
The range and both inverse identities are explicit hypotheses, not conclusions
installed by naming an expression a resolvent. No boundedness of T is assumed. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResolventDomain

variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]

/-- The shifted map has exactly the original operator domain. -/
def shifted (T : H →ₗ.[ℂ] H) (z : ℂ) : T.domain →ₗ[ℂ] H :=
  T.toFun - z • T.domain.subtype

theorem shifted_apply (T : H →ₗ.[ℂ] H) (z : ℂ) (x : T.domain) :
    shifted T z x = T x - z • (x : H) := rfl

/-- A genuine bounded two-sided inverse, with its domain membership proof. -/
structure Certificate (T : H →ₗ.[ℂ] H) (z : ℂ) where
  op : H →L[ℂ] H
  range_mem : ∀ x, op x ∈ T.domain
  right_inverse : ∀ x, shifted T z ⟨op x, range_mem x⟩ = x
  left_inverse : ∀ x : T.domain, op (shifted T z x) = x

namespace Certificate
variable {T : H →ₗ.[ℂ] H} {z : ℂ} (R : Certificate T z)

/-- Applying R produces an actual element of D(T). -/
def lift : H →ₗ[ℂ] T.domain where
  toFun x := ⟨R.op x, R.range_mem x⟩
  map_add' x y := Subtype.ext (map_add R.op x y)
  map_smul' c x := Subtype.ext (map_smul R.op c x)

theorem lift_coe (x : H) : (R.lift x : H) = R.op x := rfl

theorem shifted_lift (x : H) : shifted T z (R.lift x) = x := R.right_inverse x

theorem lift_shifted (x : T.domain) : R.lift (shifted T z x) = x :=
  Subtype.ext (R.left_inverse x)

theorem op_injective : Function.Injective R.op := by
  intro x y h
  have hl : R.lift x = R.lift y := Subtype.ext h
  simpa only [R.shifted_lift] using congrArg (shifted T z) hl

theorem shifted_injective : Function.Injective (shifted T z) := by
  intro x y h
  have h' := congrArg R.lift h
  simpa only [R.lift_shifted] using h'

theorem shifted_surjective : Function.Surjective (shifted T z) :=
  fun x => ⟨R.lift x, R.shifted_lift x⟩

theorem op_range : Set.range R.op = (T.domain : Set H) := by
  apply Set.Subset.antisymm
  · rintro y ⟨x, rfl⟩
    exact R.range_mem x
  · intro y hy
    exact ⟨shifted T z ⟨y, hy⟩, R.left_inverse ⟨y, hy⟩⟩

theorem action_lift (x : H) : T (R.lift x) = x + z • R.op x := by
  have h := R.shifted_lift x
  change T (R.lift x) - z • R.op x = x at h
  exact sub_eq_iff_eq_add.mp h

/-- No choice of a second bounded inverse can change the operator. -/
theorem unique (S : Certificate T z) : R.op = S.op := by
  ext x
  calc
    R.op x = R.op (shifted T z (S.lift x)) := by rw [S.shifted_lift]
    _ = S.op x := R.left_inverse (S.lift x)

end Certificate

/-- A bounded map restricted to a domain that it actually preserves. -/
def restrict (T : H →ₗ.[ℂ] H) (P : H →L[ℂ] H)
    (hP : ∀ x : T.domain, P x ∈ T.domain) : T.domain →ₗ[ℂ] T.domain where
  toFun x := ⟨P x, hP x⟩
  map_add' x y := Subtype.ext (map_add P (x : H) (y : H))
  map_smul' c x := Subtype.ext (map_smul P c (x : H))

theorem restrict_coe (T : H →ₗ.[ℂ] H) (P : H →L[ℂ] H)
    (hP : ∀ x : T.domain, P x ∈ T.domain) (x : T.domain) :
    (restrict T P hP x : H) = P x := rfl

/-- A bounded extension of the actual domain commutator [T,P]. -/
structure BoundedCommutator (T : H →ₗ.[ℂ] H) (P : H →L[ℂ] H) where
  preserves : ∀ x : T.domain, P x ∈ T.domain
  bound : H →L[ℂ] H
  agrees : ∀ x : T.domain,
    T (restrict T P preserves x) - P (T x) = bound x

namespace BoundedCommutator
variable {T : H →ₗ.[ℂ] H} {P : H →L[ℂ] H}
variable (B : BoundedCommutator T P)

theorem shifted_commutator (z : ℂ) (x : T.domain) :
    shifted T z (restrict T P B.preserves x) - P (shifted T z x) = B.bound x := by
  simp only [shifted_apply, restrict_coe, map_sub, map_smul]
  calc
    _ = T (restrict T P B.preserves x) - P (T x) := by abel
    _ = _ := B.agrees x

/-- The shifted scalar term cancels without assuming P reduces T. -/
theorem shifted_intertwining (z : ℂ) (x : T.domain) :
    shifted T z (restrict T P B.preserves x) = P (shifted T z x) + B.bound x := by
  have h := B.shifted_commutator z x
  exact (sub_eq_iff_eq_add.mp h).trans (add_comm _ _)

end BoundedCommutator
end ResolventDomain
end KomorebiPhysics
