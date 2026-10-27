module
public import AffineObstructionCore
public import Mathlib.SetTheory.Cardinal.Finite

/-!
# Integer and residue-ring cokernels

Reduction from integer vectors onto residue vectors identifies the range of an
integer coefficient map modulo `q` with the range of its residue-ring-linear
model. The resulting quotient equivalence preserves actual residual classes.
This bridge works for every natural modulus, including zero and composites.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.IntegerFiniteCokernel

open NativeAffine

variable {d e : ℕ}

theorem reduction_surjective (q n : ℕ) : Function.Surjective (reduction q n) := by
  intro u
  choose t ht using fun i => ZMod.intCast_surjective (u i)
  exact ⟨t, funext ht⟩

/-- The two coefficient maps have exactly the same range after scalar restriction. -/
theorem digit_range_eq_restrict (q : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q))
    (h : ∀ t, B (reduction q d t) = reduction q e (A t)) :
    LinearMap.range (digitMap q A) = (LinearMap.range B).restrictScalars ℤ := by
  ext u
  constructor
  · rintro ⟨t, rfl⟩
    exact ⟨reduction q d t, h t⟩
  · rintro ⟨v, rfl⟩
    obtain ⟨t, rfl⟩ := reduction_surjective q d v
    exact ⟨t, (h t).symm⟩

/-- The previous integer-module obstruction is the residue-ring cokernel. -/
def cokernelEquiv (q : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q))
    (h : ∀ t, B (reduction q d t) = reduction q e (A t)) :
    Obstruction q A ≃ₗ[ℤ] ((Fin e → ZMod q) ⧸ LinearMap.range B) :=
  (Submodule.quotEquivOfEq _ _ (digit_range_eq_restrict q A B h)).trans
    (Submodule.Quotient.restrictScalarsEquiv ℤ (LinearMap.range B))

@[simp]
theorem cokernelEquiv_mk (q : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q))
    (h : ∀ t, B (reduction q d t) = reduction q e (A t))
    (u : Fin e → ZMod q) :
    cokernelEquiv q A B h (Submodule.Quotient.mk u) =
      Submodule.Quotient.mk u := by
  rfl

@[simp]
theorem cokernelEquiv_obstruction (q : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q))
    (h : ∀ t, B (reduction q d t) = reduction q e (A t))
    (r : Fin e → ℤ) :
    cokernelEquiv q A B h (obstruction q A r) =
      Submodule.Quotient.mk (reduction q e r) := by
  rfl

theorem cokernel_card_eq (q : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q))
    (h : ∀ t, B (reduction q d t) = reduction q e (A t)) :
    Nat.card (Obstruction q A) =
      Nat.card ((Fin e → ZMod q) ⧸ LinearMap.range B) := by
  exact Nat.card_congr (cokernelEquiv q A B h).toEquiv

#print axioms reduction_surjective
#print axioms digit_range_eq_restrict
#print axioms cokernelEquiv
#print axioms cokernelEquiv_mk
#print axioms cokernelEquiv_obstruction
#print axioms cokernel_card_eq

end Komorebi.IntegerFiniteCokernel
