module
public import AffineSharedCorrection

@[expose] public section
set_option autoImplicit false

open Komorebi.NativeAffine Komorebi.AffinePair

/-- Exact application contract: both original congruences and the lower
residue condition are expanded, as is the quotient by the two actual kernels. -/
example (d e f p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b r : Fin e → ℤ) (c s : Fin f → ℤ) (x u v : Fin d → ℤ)
    (hr : A x - b = (p : ℤ)^L • r)
    (hs : B x - c = (p : ℤ)^L • s)
    (hu : reduction p e (r + A u) = 0)
    (hv : reduction p f (s + B v) = 0) :
    (∃ y : Fin d → ℤ,
      (∀ i, (p : ℤ)^L ∣ (y - x) i) ∧
      (∀ i, (p : ℤ)^(L+1) ∣ (A y - b) i) ∧
      (∀ i, (p : ℤ)^(L+1) ∣ (B y - c) i)) ↔
    (Submodule.Quotient.mk u : (Fin d → ℤ) ⧸
        (LinearMap.ker (digitMap p A) ⊔ LinearMap.ker (digitMap p B))) =
      Submodule.Quotient.mk v :=
  joint_lift_iff_class_eq p L hp A B b r c s x u v hr hs hu hv

example (d e f p : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ)) :
    Finite ((Fin d → ℤ) ⧸
      (LinearMap.ker (digitMap p A) ⊔ LinearMap.ker (digitMap p B))) :=
  shared_obstruction_finite p hp A B
