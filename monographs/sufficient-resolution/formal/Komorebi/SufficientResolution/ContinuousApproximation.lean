import Komorebi.SufficientResolution.ContinuousDefect
import Komorebi.SufficientResolution.ExponentialBudgets
import Mathlib.Tactic.GCongr

/-!
# Quantitative continuous-time sufficiency

Whole-operator bounds on nonnegative times, with explicit flow-growth hypotheses.
Rates may have either sign; growth amplitudes and error allowances are nonnegative.
No spectral-radius or sampled-data assumption replaces a norm bound.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousApproximation

open ContinuousFlow ContinuousDefect ExponentialBudgets
variable {X Z Y W : Type*}
variable [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z] [CompleteSpace Z]
variable [NormedAddCommGroup Y] [NormedSpace ℝ Y]
variable [NormedAddCommGroup W] [NormedSpace ℝ W] [CompleteSpace W]

omit [CompleteSpace X] [CompleteSpace Z] in
theorem norm_transportKernel_le (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (t s : ℝ) :
    ‖transportKernel q L A t s‖ ≤
      ‖flow A (t-s)‖ * (‖generatorDefect q L A‖ * ‖flow L s‖) := by
  exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
    (mul_le_mul_of_nonneg_left (ContinuousLinearMap.opNorm_comp_le _ _) (norm_nonneg _))

/-- Arbitrary continuous envelopes on the interval, not necessarily exponential. -/
theorem norm_evolution_le_envelopes (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (u v : ℝ → ℝ) (hu : Continuous u) (hv : Continuous v)
    (ε t : ℝ) (he : 0 ≤ ε) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s ∈ Set.Icc 0 t, ‖flow L s‖ ≤ u s)
    (hA : ∀ s ∈ Set.Icc 0 t, ‖flow A s‖ ≤ v s) :
    ‖evolutionDefect q L A t‖ ≤ ε * ∫ s in (0:ℝ)..t, v (t-s) * u s := by
  rw [duhamel]
  have hc : Continuous (fun s => ε * (v (t-s) * u s)) :=
    continuous_const.mul ((hv.comp (continuous_const.sub continuous_id)).mul hu)
  calc
    _ ≤ ∫ s in (0:ℝ)..t, ε * (v (t-s) * u s) := by
      apply intervalIntegral.norm_integral_le_of_norm_le ht
      · apply Filter.Eventually.of_forall
        intro s hs
        have hs' : s ∈ Set.Icc 0 t := ⟨hs.1.le, hs.2⟩
        have hts : t-s ∈ Set.Icc 0 t := ⟨sub_nonneg.mpr hs.2, sub_le_self t hs.1.le⟩
        calc
          _ ≤ ‖flow A (t-s)‖ * (‖generatorDefect q L A‖ * ‖flow L s‖) :=
            norm_transportKernel_le q L A t s
          _ ≤ v (t-s) * (ε * u s) := by
            apply mul_le_mul (hA (t-s) hts)
            · exact mul_le_mul hd (hL s hs') (norm_nonneg _) he
            · positivity
            · exact (norm_nonneg _).trans (hA (t-s) hts)
          _ = ε * (v (t-s) * u s) := by ring
      · exact hc.intervalIntegrable 0 t
    _ = _ := intervalIntegral.integral_const_mul ε _

/-- The exact convolution majorant for two independently controlled flow growth rates. -/
theorem norm_evolution_le_response (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (ML MA a b ε t : ℝ)
    (_hML : 0 ≤ ML) (_hMA : 0 ≤ MA) (he : 0 ≤ ε) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML * Real.exp (a*s))
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (b*s)) :
    ‖evolutionDefect q L A t‖ ≤ (ML*MA*ε) * response a b t := by
  have h := norm_evolution_le_envelopes q L A
    (fun s => ML * Real.exp (a*s)) (fun s => MA * Real.exp (b*s))
    (continuous_const.mul (Real.continuous_exp.comp (continuous_const.mul continuous_id)))
    (continuous_const.mul (Real.continuous_exp.comp (continuous_const.mul continuous_id)))
    ε t he ht hd (fun s hs => hL s hs.1) (fun s hs => hA s hs.1)
  have hid : (fun s => MA * Real.exp (b*(t-s)) * (ML * Real.exp (a*s))) =
      (fun s => (ML*MA) * kernel a b t s) := by
    funext s
    unfold kernel
    ring
  rw [hid, intervalIntegral.integral_const_mul] at h
  convert h using 1
  unfold response
  ring

/- Readout mismatch and dynamical mismatch contribute separately. -/
omit [CompleteSpace X] [CompleteSpace Z] in
theorem norm_output_le (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y) (t η g e : ℝ) (hη : 0 ≤ η)
    (ho : ‖O - V.comp q‖ ≤ η) (hL : ‖flow L t‖ ≤ g)
    (hE : ‖evolutionDefect q L A t‖ ≤ e) :
    ‖outputDefect q L A O V t‖ ≤ η*g + ‖V‖*e := by
  rw [output_decomposition]
  calc
    _ ≤ ‖(O - V.comp q).comp (flow L t)‖ + ‖V.comp (evolutionDefect q L A t)‖ := norm_add_le _ _
    _ ≤ η*g + ‖V‖*e := by
      apply add_le_add
      · exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
          (mul_le_mul ho hL (norm_nonneg _) hη)
      · exact (ContinuousLinearMap.opNorm_comp_le _ _).trans
          (mul_le_mul_of_nonneg_left hE (norm_nonneg _))

/-- Exponential envelope for the whole readout operator. -/
theorem norm_output_le_response (q : X →L[ℝ] Z) (L : X →L[ℝ] X)
    (A : Z →L[ℝ] Z) (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y)
    (ML MA a b ε η t : ℝ)
    (hML : 0 ≤ ML) (hMA : 0 ≤ MA) (he : 0 ≤ ε) (hη : 0 ≤ η) (ht : 0 ≤ t)
    (hd : ‖generatorDefect q L A‖ ≤ ε) (ho : ‖O - V.comp q‖ ≤ η)
    (hL : ∀ s, 0 ≤ s → ‖flow L s‖ ≤ ML * Real.exp (a*s))
    (hA : ∀ s, 0 ≤ s → ‖flow A s‖ ≤ MA * Real.exp (b*s)) :
    ‖outputDefect q L A O V t‖ ≤ η*(ML*Real.exp (a*t)) +
      ‖V‖*((ML*MA*ε) * response a b t) :=
  norm_output_le q L A O V t η _ _ hη ho (hL t ht)
    (norm_evolution_le_response q L A ML MA a b ε t hML hMA he ht hd hL hA)

/- An arbitrary initial reduced state has its own transported error. -/
omit [CompleteSpace X] [CompleteSpace Z] in
theorem norm_initialization_le (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y) (t e g : ℝ) (x : X) (z : Z)
    (hE : ‖outputDefect q L A O V t‖ ≤ e) (hA : ‖flow A t‖ ≤ g) :
    ‖O (flow L t x) - V (flow A t z)‖ ≤ e*‖x‖ + ‖V‖*(g*‖q x-z‖) := by
  rw [initialization_decomposition]
  calc
    _ ≤ ‖outputDefect q L A O V t x‖ + ‖V (flow A t (q x-z))‖ := norm_add_le _ _
    _ ≤ _ := by
      apply add_le_add
      · exact (ContinuousLinearMap.le_opNorm _ _).trans
          (mul_le_mul_of_nonneg_right hE (norm_nonneg _))
      · apply (ContinuousLinearMap.le_opNorm _ _).trans
        apply mul_le_mul_of_nonneg_left _ (norm_nonneg V)
        exact (ContinuousLinearMap.le_opNorm _ _).trans
          (mul_le_mul_of_nonneg_right hA (norm_nonneg _))

/- States identified by q remain approximately observationally indistinguishable. -/
omit [CompleteSpace X] [CompleteSpace Z] in
theorem same_representation_bound (q : X →L[ℝ] Z) (L : X →L[ℝ] X) (A : Z →L[ℝ] Z)
    (O : X →L[ℝ] Y) (V : Z →L[ℝ] Y) (t e : ℝ) (x y : X) (hxy : q x = q y)
    (hE : ‖outputDefect q L A O V t‖ ≤ e) :
    ‖O (flow L t x) - O (flow L t y)‖ ≤ e*‖x-y‖ := by
  have hid : O (flow L t x) - O (flow L t y) = outputDefect q L A O V t (x-y) := by
    simp [outputDefect, map_sub, hxy]
  rw [hid]
  exact (ContinuousLinearMap.le_opNorm _ _).trans
    (mul_le_mul_of_nonneg_right hE (norm_nonneg _))

end Komorebi.SufficientResolution.ContinuousApproximation
