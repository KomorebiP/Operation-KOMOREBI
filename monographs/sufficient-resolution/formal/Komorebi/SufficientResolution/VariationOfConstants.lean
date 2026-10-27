import Komorebi.SufficientResolution.ContinuousFlow

/-!
# Forced bounded linear dynamics

A backward propagator gives the variation-of-constants identity by the
fundamental theorem of calculus. No memory equation is assumed.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousFlow

variable {X : Type*} [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]

 theorem hasDerivAt_backward_flow (D : X →L[ℝ] X) (t s : ℝ) :
    HasDerivAt (fun u => flow D (t-u)) (-(flow D (t-s) * D)) s := by
  simpa [Function.comp_def] using
    (hasDerivAt_flow_right D (t-s)).scomp s
      ((hasDerivAt_const s t).sub (hasDerivAt_id s))

/-- The hidden generator cancels exactly when differentiating backward transport. -/
 theorem backward_forced_derivative (D : X →L[ℝ] X) (z f : ℝ → X)
    (hz : ∀ s, HasDerivAt z (D (z s) + f s) s) (t s : ℝ) :
    HasDerivAt (fun u => flow D (t-u) (z u)) (flow D (t-s) (f s)) s := by
  have h := (hasDerivAt_backward_flow D t s).clm_apply (hz s)
  simpa [map_add] using h

/-- Exact variation of constants, valid also for oriented negative time intervals. -/
 theorem variation_of_constants (D : X →L[ℝ] X) (z f : ℝ → X)
    (hf : Continuous f) (hz : ∀ s, HasDerivAt z (D (z s) + f s) s) (t : ℝ) :
    z t = flow D t (z 0) + ∫ s in (0:ℝ)..t, flow D (t-s) (f s) := by
  have hc : Continuous (fun s => flow D (t-s) (f s)) :=
    ((continuous_flow D).comp (continuous_const.sub continuous_id)).clm_apply hf
  have h := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun s _ => backward_forced_derivative D z f hz t s) (hc.intervalIntegrable 0 t)
  simp only [sub_self, flow_zero, one_apply_eq_self, sub_zero] at h
  rw [h]
  abel

/-- Every homogeneous solution is the actual exponential trajectory. -/
 theorem homogeneous_solution (D : X →L[ℝ] X) (z : ℝ → X)
    (hz : ∀ s, HasDerivAt z (D (z s)) s) (t : ℝ) : z t = flow D t (z 0) := by
  have h := variation_of_constants D z (fun _ => 0) continuous_const
    (fun s => by simpa using hz s) t
  simpa using h

/-- Homogeneous solutions with the same initial value are identical. -/
 theorem homogeneous_unique (D : X →L[ℝ] X) (u v : ℝ → X)
    (hu : ∀ s, HasDerivAt u (D (u s)) s)
    (hv : ∀ s, HasDerivAt v (D (v s)) s) (h0 : u 0 = v 0) : u = v := by
  funext t
  rw [homogeneous_solution D u hu t, homogeneous_solution D v hv t, h0]

/-- Equal forcing and equal initial values give the same global solution. -/
 theorem forced_unique (D : X →L[ℝ] X) (u v f : ℝ → X) (hf : Continuous f)
    (hu : ∀ s, HasDerivAt u (D (u s) + f s) s)
    (hv : ∀ s, HasDerivAt v (D (v s) + f s) s) (h0 : u 0 = v 0) : u = v := by
  funext t
  rw [variation_of_constants D u f hf hu t, variation_of_constants D v f hf hv t, h0]

end Komorebi.SufficientResolution.ContinuousFlow
