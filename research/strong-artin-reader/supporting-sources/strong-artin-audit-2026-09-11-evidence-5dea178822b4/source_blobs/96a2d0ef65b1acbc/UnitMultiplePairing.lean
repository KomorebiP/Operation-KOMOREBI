import Mathlib.LinearAlgebra.Dual.Lemmas

/-!
# Pairings compared up to a unit

A Taylor--Wiles selection argument only uses whether a local pairing is zero.
Consequently an arithmetic pairing need not be normalized identically to a
model pairing: equality up to a unit preserves perfectness and every nonzero
detection statement.
-/

namespace Komorebi.StrongArtin.UnitMultiplePairing

universe u
noncomputable section

variable {k T H : Type u} [Field k]
  [AddCommGroup T] [Module k T]
  [AddCommGroup H] [Module k H]

/-- Two bilinear pairings, bundled as maps into the dual, agree up to a unit. -/
structure Comparison where
  model : T →ₗ[k] Module.Dual k H
  arithmetic : T →ₗ[k] Module.Dual k H
  scale : kˣ
  compatibility : arithmetic = (scale : k) • model

@[simp]
theorem Comparison.arithmetic_apply
    (C : Comparison (k := k) (T := T) (H := H)) (t : T) (h : H) :
    C.arithmetic t h = (C.scale : k) * C.model t h := by
  rw [C.compatibility]
  rfl

/-- Multiplication by a unit preserves pointwise nonvanishing of the pairing. -/
theorem Comparison.arithmetic_apply_ne_zero_iff
    (C : Comparison (k := k) (T := T) (H := H)) (t : T) (h : H) :
    C.arithmetic t h ≠ 0 ↔ C.model t h ≠ 0 := by
  rw [C.arithmetic_apply]
  exact mul_ne_zero_iff_left C.scale.ne_zero

/-- Detection of every nonzero class transfers from the model pairing to any
unit-normalized arithmetic pairing. -/
theorem Comparison.detects_of_model_detects
    (C : Comparison (k := k) (T := T) (H := H))
    (hmodel : ∀ h : H, h ≠ 0 → ∃ t : T, C.model t h ≠ 0) :
    ∀ h : H, h ≠ 0 → ∃ t : T, C.arithmetic t h ≠ 0 := by
  intro h hh
  obtain ⟨t, ht⟩ := hmodel h hh
  exact ⟨t, C.arithmetic_apply_ne_zero_iff t h |>.2 ht⟩

/-- Detection transfers in the reverse direction as well. -/
theorem Comparison.model_detects_of_arithmetic_detects
    (C : Comparison (k := k) (T := T) (H := H))
    (harithmetic : ∀ h : H, h ≠ 0 → ∃ t : T, C.arithmetic t h ≠ 0) :
    ∀ h : H, h ≠ 0 → ∃ t : T, C.model t h ≠ 0 := by
  intro h hh
  obtain ⟨t, ht⟩ := harithmetic h hh
  exact ⟨t, C.arithmetic_apply_ne_zero_iff t h |>.1 ht⟩

/-- A unit multiple of an injective model pairing is injective. -/
theorem Comparison.arithmetic_injective
    (C : Comparison (k := k) (T := T) (H := H))
    (hmodel : Function.Injective C.model) :
    Function.Injective C.arithmetic := by
  intro x y hxy
  apply hmodel
  have hscaled : (C.scale : k) • C.model x = (C.scale : k) • C.model y := by
    simpa [C.compatibility] using hxy
  have hcancel := congrArg (fun φ : Module.Dual k H => (↑C.scale⁻¹ : k) • φ) hscaled
  simpa [smul_smul] using hcancel

/-- A unit multiple of a surjective model pairing is surjective. -/
theorem Comparison.arithmetic_surjective
    (C : Comparison (k := k) (T := T) (H := H))
    (hmodel : Function.Surjective C.model) :
    Function.Surjective C.arithmetic := by
  intro φ
  obtain ⟨t, ht⟩ := hmodel ((↑C.scale⁻¹ : k) • φ)
  refine ⟨t, ?_⟩
  rw [C.compatibility, LinearMap.smul_apply, ht]
  simp [smul_smul]

/-- A unit multiple of a linear equivalence is again a linear equivalence. -/
def Comparison.arithmeticEquiv
    (C : Comparison (k := k) (T := T) (H := H))
    (e : T ≃ₗ[k] Module.Dual k H) :
    T ≃ₗ[k] Module.Dual k H :=
  C.scale • e

@[simp]
theorem Comparison.arithmeticEquiv_toLinearMap
    (C : Comparison (k := k) (T := T) (H := H))
    (e : T ≃ₗ[k] Module.Dual k H)
    (he : e.toLinearMap = C.model) :
    (C.arithmeticEquiv e).toLinearMap = C.arithmetic := by
  rw [Comparison.arithmeticEquiv, LinearEquiv.toLinearMap_smul, he, C.compatibility]

end
end Komorebi.StrongArtin.UnitMultiplePairing

#print axioms Komorebi.StrongArtin.UnitMultiplePairing.Comparison.arithmetic_apply_ne_zero_iff
#print axioms Komorebi.StrongArtin.UnitMultiplePairing.Comparison.detects_of_model_detects
#print axioms Komorebi.StrongArtin.UnitMultiplePairing.Comparison.arithmetic_injective
#print axioms Komorebi.StrongArtin.UnitMultiplePairing.Comparison.arithmetic_surjective
#print axioms Komorebi.StrongArtin.UnitMultiplePairing.Comparison.arithmeticEquiv_toLinearMap
