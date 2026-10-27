module
public import SharedCorrection
public import AffinePairTransport

/-!
# A finite shared obstruction for two affine congruence lifts

Author: Komorebi P.
All coefficient and reduction maps below are the actual integer-linear maps.
No surjectivity, common correction, or compatibility premise is hidden in the
finite existence theorem. This concerns one lift at a time.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.AffinePair
open Komorebi.NativeAffine Komorebi.SharedCorrection

variable {d e f : ℕ}

abbrev SharedObstruction (p : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ)) :=
  Common (digitMap p A) (digitMap p B)

theorem shared_obstruction_finite (p : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ)) :
    Finite (SharedObstruction p A B) := by
  let : NeZero p := ⟨Nat.ne_of_gt hp⟩
  exact common_finite_of_left (digitMap p A) (digitMap p B)

/-- Any two individually valid correction vectors give the same left label. -/
theorem left_class_independent (p : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (r : Fin e → ℤ) (u u' : Fin d → ℤ)
    (hu : reduction p e (r + A u) = 0)
    (hu' : reduction p e (r + A u') = 0) :
    (Submodule.Quotient.mk u : SharedObstruction p A B) =
      Submodule.Quotient.mk u' := by
  apply (quotient_mk_eq_iff_common (digitMap p A) (digitMap p B) u u').mpr
  exact ⟨u', (digit_correction_iff_same_image p A r u u' hu).mp hu', rfl⟩

theorem right_class_independent (p : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (s : Fin f → ℤ) (v v' : Fin d → ℤ)
    (hv : reduction p f (s + B v) = 0)
    (hv' : reduction p f (s + B v') = 0) :
    (Submodule.Quotient.mk v : SharedObstruction p A B) =
      Submodule.Quotient.mk v' := by
  apply (quotient_mk_eq_iff_common (digitMap p A) (digitMap p B) v v').mpr
  exact ⟨v, rfl, ((digit_correction_iff_same_image p B s v v' hv).mp hv').symm⟩

/-- Given individual lifts, equality in the fixed finite common quotient is
exactly the remaining condition for a joint lift. -/
theorem joint_lift_iff_class_eq (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b r : Fin e → ℤ) (c s : Fin f → ℤ) (x u v : Fin d → ℤ)
    (hr : A x - b = (p : ℤ)^L • r)
    (hs : B x - c = (p : ℤ)^L • s)
    (hu : reduction p e (r + A u) = 0)
    (hv : reduction p f (s + B v) = 0) :
    HasJointLift p L A B b c x ↔
    (Submodule.Quotient.mk u : SharedObstruction p A B) =
      Submodule.Quotient.mk v := by
  rw [joint_lift_iff_digit_correction p L hp A B b r c s x hr hs,
    quotient_mk_eq_iff_common]
  exact exists_congr fun t => and_congr
    (digit_correction_iff_same_image p A r u t hu)
    (digit_correction_iff_same_image p B s v t hv)

/-- The unconditioned form includes individual solvability as part of the
criterion, so it cannot assert that arbitrary pairs of targets glue. -/
theorem joint_lift_iff_compatible_corrections (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b r : Fin e → ℤ) (c s : Fin f → ℤ) (x : Fin d → ℤ)
    (hr : A x - b = (p : ℤ)^L • r)
    (hs : B x - c = (p : ℤ)^L • s) :
    HasJointLift p L A B b c x ↔
    ∃ u v : Fin d → ℤ,
      reduction p e (r + A u) = 0 ∧ reduction p f (s + B v) = 0 ∧
      (Submodule.Quotient.mk u : SharedObstruction p A B) =
        Submodule.Quotient.mk v := by
  constructor
  · intro h
    obtain ⟨t, hA, hB⟩ :=
      (joint_lift_iff_digit_correction p L hp A B b r c s x hr hs).mp h
    exact ⟨t, t, hA, hB, rfl⟩
  · rintro ⟨u, v, hu, hv, huv⟩
    exact (joint_lift_iff_class_eq p L hp A B b r c s x u v hr hs hu hv).mpr huv

/-- Every actual lower-level solution supplies its residuals and a finite
quotient whose compatibility condition characterizes the next joint lift. -/
theorem finite_affine_pair_compatibility (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b : Fin e → ℤ) (c : Fin f → ℤ) (x : Fin d → ℤ)
    (hxA : ∀ i, (p : ℤ)^L ∣ (A x - b) i)
    (hxB : ∀ i, (p : ℤ)^L ∣ (B x - c) i) :
    ∃ (r : Fin e → ℤ) (s : Fin f → ℤ),
      A x - b = (p : ℤ)^L • r ∧ B x - c = (p : ℤ)^L • s ∧
      Finite (SharedObstruction p A B) ∧
      (HasJointLift p L A B b c x ↔
        ∃ u v : Fin d → ℤ,
          reduction p e (r + A u) = 0 ∧ reduction p f (s + B v) = 0 ∧
          (Submodule.Quotient.mk u : SharedObstruction p A B) =
            Submodule.Quotient.mk v) := by
  obtain ⟨r, hr⟩ := residual_exists p L A b x hxA
  obtain ⟨s, hs⟩ := residual_exists p L B c x hxB
  exact ⟨r, s, hr, hs, shared_obstruction_finite p hp A B,
    joint_lift_iff_compatible_corrections p L hp A B b r c s x hr hs⟩

end Komorebi.AffinePair

#print axioms Komorebi.AffinePair.SharedObstruction
#print axioms Komorebi.AffinePair.shared_obstruction_finite
#print axioms Komorebi.AffinePair.left_class_independent
#print axioms Komorebi.AffinePair.right_class_independent
#print axioms Komorebi.AffinePair.joint_lift_iff_class_eq
#print axioms Komorebi.AffinePair.joint_lift_iff_compatible_corrections
#print axioms Komorebi.AffinePair.finite_affine_pair_compatibility
