module
public import PolynomialObstruction
public import AffineSharedCorrection

/-!
# A finite common quotient for simultaneous polynomial lifts

The two blocks use the same unknown vector. Their actual reduced Jacobians
define a finite common quotient, and equal labels are precisely the remaining
condition for a joint next-level lift after each block lifts individually.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialShared

open Komorebi.NativeAffine Komorebi.PolynomialObstruction Komorebi.SharedCorrection

variable {d e f : ℕ}

/-- The common quotient of the two actual reduced Jacobians. -/
abbrev SharedObstruction (q : ℕ)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :=
  Komorebi.AffinePair.SharedObstruction q (jacobian F x) (jacobian G x)

/-- A single vector must lift both polynomial systems. -/
def HasJointLift (q L : ℕ)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) : Prop :=
  ∃ y : Fin d → ℤ,
    (∀ i, (q : ℤ)^L ∣ (y - x) i) ∧
    (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F y i) ∧
    (∀ i, (q : ℤ)^(L+1) ∣ evalSystem G y i)

theorem shared_obstruction_finite (q : ℕ) (hq : 0 < q)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    Finite (SharedObstruction q F G x) :=
  Komorebi.AffinePair.shared_obstruction_finite q hq (jacobian F x) (jacobian G x)

/-- Polynomial Taylor expansion identifies the actual simultaneous-lift
problem with two correction equations at the same digit. -/
theorem joint_lift_iff_digit_correction (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (s : Fin f → ℤ)
    (hr : evalSystem F x = (q : ℤ)^L • r)
    (hs : evalSystem G x = (q : ℤ)^L • s) :
    HasJointLift q L F G x ↔
      ∃ t : Fin d → ℤ, reduction q e (r + jacobian F x t) = 0 ∧
        reduction q f (s + jacobian G x t) = 0 := by
  constructor
  · rintro ⟨y, hy, hF, hG⟩
    obtain ⟨t, rfl⟩ := (same_residue_iff ((q : ℤ)^L) x y).mp hy
    exact ⟨t, (next_level_iff_digit q L hq hL F x r hr t).mp hF,
      (next_level_iff_digit q L hq hL G x s hs t).mp hG⟩
  · rintro ⟨t, hF, hG⟩
    exact ⟨x + (q : ℤ)^L • t,
      (same_residue_iff ((q : ℤ)^L) x _).mpr ⟨t, rfl⟩,
      (next_level_iff_digit q L hq hL F x r hr t).mpr hF,
      (next_level_iff_digit q L hq hL G x s hs t).mpr hG⟩

/-- The left label is independent of the chosen actual polynomial lift. -/
theorem left_class_independent (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x u u' : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (hu : ∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • u) i)
    (hu' : ∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • u') i) :
    (Submodule.Quotient.mk u : SharedObstruction q F G x) =
      Submodule.Quotient.mk u' :=
  Komorebi.AffinePair.left_class_independent q (jacobian F x) (jacobian G x) r u u'
    ((next_level_iff_digit q L hq hL F x r hr u).mp hu)
    ((next_level_iff_digit q L hq hL F x r hr u').mp hu')

/-- The right label is independent of the chosen actual polynomial lift. -/
theorem right_class_independent (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x v v' : Fin d → ℤ)
    (s : Fin f → ℤ) (hs : evalSystem G x = (q : ℤ)^L • s)
    (hv : ∀ i, (q : ℤ)^(L+1) ∣ evalSystem G (x + (q : ℤ)^L • v) i)
    (hv' : ∀ i, (q : ℤ)^(L+1) ∣ evalSystem G (x + (q : ℤ)^L • v') i) :
    (Submodule.Quotient.mk v : SharedObstruction q F G x) =
      Submodule.Quotient.mk v' :=
  Komorebi.AffinePair.right_class_independent q (jacobian F x) (jacobian G x) s v v'
    ((next_level_iff_digit q L hq hL G x s hs v).mp hv)
    ((next_level_iff_digit q L hq hL G x s hs v').mp hv')

/-- Given actual individual polynomial lifts, equal common-quotient labels
are necessary and sufficient for a simultaneous polynomial lift. -/
theorem joint_lift_iff_class_eq (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x u v : Fin d → ℤ)
    (r : Fin e → ℤ) (s : Fin f → ℤ)
    (hr : evalSystem F x = (q : ℤ)^L • r)
    (hs : evalSystem G x = (q : ℤ)^L • s)
    (hu : ∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • u) i)
    (hv : ∀ i, (q : ℤ)^(L+1) ∣ evalSystem G (x + (q : ℤ)^L • v) i) :
    HasJointLift q L F G x ↔
      (Submodule.Quotient.mk u : SharedObstruction q F G x) =
        Submodule.Quotient.mk v := by
  have hu' := (next_level_iff_digit q L hq hL F x r hr u).mp hu
  have hv' := (next_level_iff_digit q L hq hL G x s hs v).mp hv
  rw [joint_lift_iff_digit_correction q L hq hL F G x r s hr hs,
    quotient_mk_eq_iff_common]
  exact exists_congr fun t => and_congr
    (Komorebi.AffinePair.digit_correction_iff_same_image q (jacobian F x) r u t hu')
    (Komorebi.AffinePair.digit_correction_iff_same_image q (jacobian G x) s v t hv')

/-- Individual polynomial solvability is included in the unconditioned
criterion, together with exactly the common compatibility relation. -/
theorem joint_lift_iff_compatible_corrections (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (s : Fin f → ℤ)
    (hr : evalSystem F x = (q : ℤ)^L • r)
    (hs : evalSystem G x = (q : ℤ)^L • s) :
    HasJointLift q L F G x ↔ ∃ u v : Fin d → ℤ,
      (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • u) i) ∧
      (∀ i, (q : ℤ)^(L+1) ∣ evalSystem G (x + (q : ℤ)^L • v) i) ∧
      (Submodule.Quotient.mk u : SharedObstruction q F G x) =
        Submodule.Quotient.mk v := by
  constructor
  · rintro ⟨y, hy, hF, hG⟩
    obtain ⟨t, rfl⟩ := (same_residue_iff ((q : ℤ)^L) x y).mp hy
    exact ⟨t, t, hF, hG, rfl⟩
  · rintro ⟨u, v, hu, hv, huv⟩
    exact (joint_lift_iff_class_eq q L hq hL F G x u v r s hr hs hu hv).mpr huv

/-- Every pair of actual lower-level polynomial solutions has a finite common
quotient and an exact criterion for the next simultaneous lift. -/
theorem finite_polynomial_pair_compatibility (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ)
    (G : Fin f → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hxF : ∀ i, (q : ℤ)^L ∣ evalSystem F x i)
    (hxG : ∀ i, (q : ℤ)^L ∣ evalSystem G x i) :
    Finite (SharedObstruction q F G x) ∧
      (HasJointLift q L F G x ↔ ∃ u v : Fin d → ℤ,
        (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • u) i) ∧
        (∀ i, (q : ℤ)^(L+1) ∣ evalSystem G (x + (q : ℤ)^L • v) i) ∧
        (Submodule.Quotient.mk u : SharedObstruction q F G x) =
          Submodule.Quotient.mk v) := by
  obtain ⟨r, hr⟩ := Komorebi.PolynomialObstruction.residual_exists q L F x hxF
  obtain ⟨s, hs⟩ := Komorebi.PolynomialObstruction.residual_exists q L G x hxG
  exact ⟨shared_obstruction_finite q hq F G x,
    joint_lift_iff_compatible_corrections q L hq hL F G x r s hr hs⟩

#print axioms SharedObstruction
#print axioms HasJointLift
#print axioms shared_obstruction_finite
#print axioms joint_lift_iff_digit_correction
#print axioms left_class_independent
#print axioms right_class_independent
#print axioms joint_lift_iff_class_eq
#print axioms joint_lift_iff_compatible_corrections
#print axioms finite_polynomial_pair_compatibility

end Komorebi.PolynomialShared
