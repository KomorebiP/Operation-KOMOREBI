import PaperX.AbsoluteFrobeniusWitnesses

/-! Actual arithmetic Frobenius choices are conjugate modulo ideal inertia.
Their traces agree in a representation which kills that inertia. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.FrobeniusChoiceIndependence
open PaperX.AbsoluteIntegralFrobenius PaperX.AbsoluteFrobeniusWitnesses
open scoped Pointwise

local instance : TopologicalSpace IntegralClosure := ⊥
local instance : DiscreteTopology IntegralClosure := ⟨rfl⟩
attribute [local instance] continuous_integral_action

/-- Two actual Frobenius choices at one rational prime are conjugate modulo
inertia, even when they use different primes of the algebraic integers. -/
theorem witnesses_conjugate_mod_inertia (p : ℕ) (u v : Witness p) :
    ∃ a : GQ, v.primeIdeal = a • u.primeIdeal ∧
      v.element⁻¹ * (a * u.element * a⁻¹) ∈ v.primeIdeal.inertia GQ := by
  let : u.primeIdeal.IsMaximal := u.isMaximal
  let : v.primeIdeal.IsMaximal := v.isMaximal
  let : u.primeIdeal.LiesOver (Ideal.span {(p : ℤ)}) := u.liesOver
  let : v.primeIdeal.LiesOver (Ideal.span {(p : ℤ)}) := v.liesOver
  have heq : u.primeIdeal.under ℤ = v.primeIdeal.under ℤ := by
    rw [← Ideal.over_def u.primeIdeal (Ideal.span {(p : ℤ)}),
      ← Ideal.over_def v.primeIdeal (Ideal.span {(p : ℤ)})]
  obtain ⟨a, ha⟩ := Algebra.IsInvariant.exists_smul_of_under_eq_of_profinite
    (A := ℤ) (B := IntegralClosure) (G := GQ) u.primeIdeal v.primeIdeal heq
  refine ⟨a, ha, same_residue_div_mem_inertia v.primeIdeal v.element
    (a * u.element * a⁻¹) v.stabilizes ?_⟩
  intro x
  have h := residue_conjugate u.primeIdeal p u.element a u.residue x
  rw [← ha] at h
  exact h.trans (v.residue x).symm

/-- Killing inertia makes the conjugated Frobenius operators equal. -/
theorem witness_operator_conjugacy {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (ρ : Representation K GQ V) (p : ℕ) (u v : Witness p)
    (hunram : ∀ g ∈ v.primeIdeal.inertia GQ, ρ g = 1) :
    ∃ a : GQ, ρ (a * u.element * a⁻¹) = ρ v.element := by
  obtain ⟨a, _, ha⟩ := witnesses_conjugate_mod_inertia p u v
  refine ⟨a, ?_⟩
  have h := congrArg (fun z => ρ v.element * z) (hunram _ ha)
  simpa only [← map_mul, mul_inv_cancel_left, mul_one] using h

/-- The trace is independent of the actual prime and Frobenius lift once its
inertia acts trivially. -/
theorem witness_character_eq {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
    (ρ : Representation K GQ V) (p : ℕ) (u v : Witness p)
    (hunram : ∀ g ∈ v.primeIdeal.inertia GQ, ρ g = 1) :
    Representation.character ρ u.element = Representation.character ρ v.element := by
  obtain ⟨a, ha⟩ := witness_operator_conjugacy ρ p u v hunram
  rw [← Representation.char_conj ρ u.element a]
  exact congrArg (LinearMap.trace K V) ha

end PaperX.FrobeniusChoiceIndependence
