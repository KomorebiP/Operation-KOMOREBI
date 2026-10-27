import Komorebi.SufficientResolution.ContinuousApproximation

/-!
# Stable continuous-time approximation and multilevel error transport

Prepared-state estimates and arbitrary initialization are separated. Flow norm
hypotheses are explicit; no stability conclusion is inferred from eigenvalues.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousStability

open ContinuousFlow ContinuousDefect ExponentialBudgets ContinuousApproximation
variable {X Z Y W : Type*}
variable [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z] [CompleteSpace Z]
variable [NormedAddCommGroup Y] [NormedSpace ℝ Y]
variable [NormedAddCommGroup W] [NormedSpace ℝ W] [CompleteSpace W]

/-- Distinct growth rates have a divided-difference bound. -/
theorem norm_evolution_distinct (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (ML MA a b ε t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (ht : 0 ≤ t) (hab : a ≠ b)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML * Real.exp (a*s))
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (b*s)) :
    ‖evolutionDefect q L A t‖ ≤ (ML*MA*ε) *
      ((Real.exp (a*t)-Real.exp (b*t))/(a-b)) := by
  simpa only [response_of_ne a b t hab] using
    norm_evolution_le_response q L A ML MA a b ε t hML hMA he ht hd hL hA

/-- Equal growth rates are handled without a singular denominator. -/
theorem norm_evolution_equal (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (ML MA a ε t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML * Real.exp (a*s))
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (a*s)) :
    ‖evolutionDefect q L A t‖ ≤ (ML*MA*ε) * (t * Real.exp (a*t)) := by
  simpa only [response_self] using
    norm_evolution_le_response q L A ML MA a a ε t hML hMA he ht hd hL hA

/-- Uniformly bounded flows give linear-in-time accumulated error. -/
theorem norm_evolution_bounded (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (ML MA ε t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML)
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA) :
    ‖evolutionDefect q L A t‖ ≤ (ML*MA*ε)*t := by
  simpa using norm_evolution_le_response q L A ML MA 0 0 ε t hML hMA he ht hd
    (by simpa using hL) (by simpa using hA)

/-- Full time-dependent stable estimate before discarding exponential decay. -/
theorem norm_evolution_stable (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (ML MA ε rate t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (hr : 0 < rate) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML)
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (-rate*s)) :
    ‖evolutionDefect q L A t‖ ≤ (ML*MA*ε) * ((1-Real.exp (-rate*t))/rate) := by
  simpa only [response_stable_formula rate t hr] using
    norm_evolution_le_response q L A ML MA 0 (-rate) ε t hML hMA he ht hd
      (by simpa using hL) hA

/-- Bounded true dynamics and exponentially stable reduced dynamics give a uniform bound. -/
theorem norm_evolution_uniform (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (ML MA ε rate t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (hr : 0 < rate) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML)
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (-rate*s)) :
    ‖evolutionDefect q L A t‖ ≤ (ML*MA*ε)/rate := by
  have h := norm_evolution_le_response q L A ML MA 0 (-rate) ε t hML hMA he ht hd
    (by simpa using hL) hA
  calc
    _ ≤ (ML*MA*ε)*response 0 (-rate) t := h
    _ ≤ (ML*MA*ε)*(1/rate) :=
      mul_le_mul_of_nonneg_left (response_stable_le rate t hr) (by positivity)
    _ = _ := by ring

/-- A uniform bound on the entire readout map. -/
theorem norm_output_uniform (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y)
    (ML MA ε η rate t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (hη : 0 ≤ η)
    (hr : 0 < rate) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML)
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (-rate*s)) :
    ‖outputDefect q L A O V t‖ ≤ η*ML + ‖V‖*((ML*MA*ε)/rate) :=
  norm_output_le q L A O V t η ML _ hη ho (hL t ht)
    (norm_evolution_uniform q L A ML MA ε rate t hML hMA he hr ht hd hL hA)

/-- Initialization error decays separately; the model-error allowance is uniform. -/
theorem norm_initialization_uniform (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y)
    (ML MA ε η rate t : ℝ) (x : X) (z : Z)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (hη : 0 ≤ η)
    (hr : 0 < rate) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML)
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (-rate*s)) :
    ‖O (flow L t x) - V (flow A t z)‖ ≤
      (η*ML + ‖V‖*((ML*MA*ε)/rate))*‖x‖ +
      ‖V‖*((MA*Real.exp (-rate*t))*‖q x-z‖) :=
  norm_initialization_le q L A O V t _ _ x z
    (norm_output_uniform q L A O V ML MA ε η rate t hML hMA he hη hr ht hd ho hL hA)
    (hA t ht)

/-- Finite-time fidelity when both flows are uniformly bounded. -/
theorem norm_output_bounded (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y)
    (ML MA ε η t : ℝ) (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε)
    (hη : 0 ≤ η) (ht : 0 ≤ t) (hd : ‖generatorDefect q L A‖ ≤ ε)
    (ho : ‖O - V.comp q‖ ≤ η)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML)
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA) :
    ‖outputDefect q L A O V t‖ ≤ η*ML + ‖V‖*((ML*MA*ε)*t) :=
  norm_output_le q L A O V t η ML _ hη ho (hL t ht)
    (norm_evolution_bounded q L A ML MA ε t hML hMA he ht hd hL hA)

omit [CompleteSpace X] [CompleteSpace Z] [CompleteSpace W] in
/-- Error allowances propagate through two successive representation maps. -/
theorem norm_composite_evolution (q : X →L[ℝ] Z) (p : Z →L[ℝ] W)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) (B : W →L[ℝ] W) (t e₁ e₂ : ℝ)
    (h₁ : ‖evolutionDefect q L A t‖ ≤ e₁) (h₂ : ‖evolutionDefect p A B t‖ ≤ e₂) :
    ‖evolutionDefect (p.comp q) L B t‖ ≤ ‖p‖*e₁ + e₂*‖q‖ := by
  rw [evolutionDefect_composite q p L A B t]
  exact (norm_add_le _ _).trans (add_le_add
    ((ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul_of_nonneg_left h₁ (norm_nonneg _)))
    ((ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul_of_nonneg_right h₂ (norm_nonneg _))))

omit [CompleteSpace X] [CompleteSpace Z] [CompleteSpace W] in
/-- Generator-error accounting is compatible with multilevel model composition. -/
theorem norm_composite_generator (q : X →L[ℝ] Z) (p : Z →L[ℝ] W)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) (B : W →L[ℝ] W) (ε₁ ε₂ : ℝ)
    (h₁ : ‖generatorDefect q L A‖ ≤ ε₁) (h₂ : ‖generatorDefect p A B‖ ≤ ε₂) :
    ‖generatorDefect (p.comp q) L B‖ ≤ ‖p‖*ε₁ + ε₂*‖q‖ := by
  rw [generatorDefect_composite q p L A B]
  exact (norm_add_le _ _).trans (add_le_add
    ((ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul_of_nonneg_left h₁ (norm_nonneg _)))
    ((ContinuousLinearMap.opNorm_comp_le _ _).trans
      (mul_le_mul_of_nonneg_right h₂ (norm_nonneg _))))

end Komorebi.SufficientResolution.ContinuousStability
