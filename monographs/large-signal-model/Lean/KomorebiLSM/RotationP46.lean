import KomorebiLSM.RotationConeGeometry

/-! The complete Proposition 46 statement for the actual rational process.
The finite-generator obstruction quantifies over every generator count,
including zero and redundant generating families. -/
set_option autoImplicit false
namespace Komorebi.LSM.RotationP46
open scoped BigOperators
open RotationModel
open FiniteInstruments (wordAction)

/-- The exact rational rotation process is probability-valid on its canonical
Lorentz cone, has predictive dimension three, and admits no finite normalized
positive-generator certificate. All objects are constructed in the imported
proof modules; no rank, orbit-density or cone-characterization hypothesis is
assumed by this endpoint. -/
theorem rational_rank_three_nonpolyhedral_model :
    (∀ s, ∃ M : Matrix (Fin 3) (Fin 3) ℚ,
      M.map (algebraMap ℚ ℝ) = matrix s) ∧
    IsClosed cone ∧ Convex ℝ cone ∧ initial ∈ cone ∧ mass initial = 1 ∧
    (∀ s z, z ∈ cone → operator s z ∈ cone) ∧
    (∀ a z, ∑ o, mass (operator (a,o) z) = mass z) ∧
    (∀ z, z ∈ cone → mass z = 1 →
      Behavior.CausalLaw (fun w => mass (wordAction operator w z)) ∧
      ∀ w, 0 ≤ mass (wordAction operator w z) ∧
        mass (wordAction operator w z) ≤ 1) ∧
    Behavior.CausalLaw process ∧
    TestDomains.allTests operator mass = cone ∧
    (∀ C : Set State, IsClosed C → Convex ℝ C →
      (∀ a : ℝ, 0 ≤ a → ∀ z ∈ C, a • z ∈ C) → initial ∈ C →
      (∀ z ∈ C, 0 ≤ mass z) →
      (∀ s z, z ∈ C → operator s z ∈ C) → C = cone) ∧
    (∀ n : ℕ, ¬ ∃ V : (Fin n → ℝ) →ₗ[ℝ] State,
      mass.comp V = FiniteInstruments.mass ∧
      initial ∈ PositiveLift.hull V ∧
      ∀ s z, z ∈ PositiveLift.hull V → operator s z ∈ PositiveLift.hull V) ∧
    realization.IsReachable ∧ realization.IsObservable ∧
    Module.finrank ℝ (Behavior.space process) = 3 := by
  refine ⟨matrix_is_rational, LorentzBaseNorm.model_cone_closed,
    LorentzBaseNorm.model_cone_convex, initial_mem, initial_mass,
    fun s z hz => operator_cone s hz, operator_mass, ?_, process_causal,
    RotationConeGeometry.canonical_cone_eq, ?_, ?_, realization_reachable,
    realization_observable, behavior_dimension_three⟩
  · intro z hz hm
    exact ⟨causal_of_normalized_cone z hz hm, normalized_word_probability z hz hm⟩
  · intro C hc hv hs hi hm hb
    exact RotationConeGeometry.invariant_probability_cone_unique hc hv hs hi hm hb
  · intro n
    rintro ⟨V, hn, hi, hb⟩
    exact RotationConeGeometry.no_finite_normalized_generator_certificate V hn hi hb

end Komorebi.LSM.RotationP46
