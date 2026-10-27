import Komorebi.SufficientResolution.ContinuousJets
import Komorebi.SufficientResolution.ContinuousSplit
import Mathlib.Analysis.Calculus.Deriv.Prod

/-!
# Exact continuous-time examples and initialized-closure boundaries

The nilpotent hidden system has memory kernel t times the identity and first
feedback at the third derivative. A second system has two nonzero couplings but
zero prepared memory, while arbitrary hidden initialization remains observable.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousExamples
open ContinuousFlow ContinuousBlockDynamics

/-- One visible coordinate and two hidden coordinates, with delayed return. -/
def delayed : ContinuousBlockDynamics ℝ (ℝ × ℝ) where
  A := 0
  B := ContinuousLinearMap.fst ℝ ℝ ℝ
  G := ContinuousLinearMap.inr ℝ ℝ ℝ
  D := (ContinuousLinearMap.snd ℝ ℝ ℝ).prod 0

@[simp] theorem delayed_D_apply (z : ℝ × ℝ) : delayed.D z = (z.2, 0) := rfl

 theorem delayed_D_sq : delayed.D^2 = 0 := by
  apply ContinuousLinearMap.ext
  intro z
  simp [pow_two]

/-- This is the actual exponential, proved by the linear ODE and uniqueness. -/
 theorem delayed_hidden_flow (t : ℝ) (z : ℝ × ℝ) :
    flow delayed.D t z = (z.1 + t*z.2, z.2) := by
  have hsol := homogeneous_solution delayed.D (fun u : ℝ => (z.1 + u*z.2, z.2))
    (fun u => by
      simpa using ((hasDerivAt_const u z.1).add
        ((hasDerivAt_id u).mul_const z.2)).prodMk (hasDerivAt_const u z.2)) t
  simpa using hsol.symm

 theorem delayed_memory (t : ℝ) : delayed.memory t = t • (1 : ℝ →L[ℝ] ℝ) := by
  apply ContinuousLinearMap.ext
  intro y
  change (flow delayed.D t (0,y)).1 = t*y
  rw [delayed_hidden_flow]
  simp

 theorem delayed_moment_zero : delayed.memoryMoment 0 = 0 := by
  apply ContinuousLinearMap.ext
  intro y
  rfl

 theorem delayed_moment_one : delayed.memoryMoment 1 = 1 := by
  apply ContinuousLinearMap.ext
  intro y
  rfl

 theorem delayed_derivative_prefix (n : ℕ) (hn : n ≤ 2) :
    iteratedDeriv n delayed.prepared 0 = delayed.A^n := by
  apply delayed.derivative_prefix_of_memory_prefix 1 _ n hn
  intro j hj
  have : j = 0 := by omega
  subst j
  exact delayed_moment_zero

 theorem delayed_first_return_derivative :
    iteratedDeriv 3 delayed.prepared 0 - delayed.A^3 = 1 := by
  have h := delayed.first_return_derivative 1 (by
    intro j hj
    have : j = 0 := by omega
    subst j
    exact delayed_moment_zero)
  simpa only [delayed_moment_one] using h

 theorem delayed_nonclosure : ∃ t : ℝ, delayed.prepared t ≠ flow delayed.A t := by
  apply delayed.nonzero_moment_forces_nonclosure 1
  rw [delayed_moment_one]
  exact one_ne_zero

 theorem delayed_not_semigroup :
    ¬ (∀ s t, delayed.prepared (s+t) = (delayed.prepared s).comp (delayed.prepared t)) := by
  intro h
  obtain ⟨t, ht⟩ := delayed_nonclosure
  exact ht ((delayed.prepared_semigroup_iff_exact).mp h t)

/-- Both couplings are nonzero, but the injected and observed hidden lanes differ. -/
def disconnectedReturn : ContinuousBlockDynamics ℝ (ℝ × ℝ) where
  A := 0
  B := ContinuousLinearMap.fst ℝ ℝ ℝ
  G := ContinuousLinearMap.inr ℝ ℝ ℝ
  D := 0

 theorem disconnected_B_ne_zero : disconnectedReturn.B ≠ 0 := by
  intro h
  have hh := congrArg (fun F : (ℝ × ℝ) →L[ℝ] ℝ => F (1,0)) h
  norm_num [disconnectedReturn] at hh

 theorem disconnected_G_ne_zero : disconnectedReturn.G ≠ 0 := by
  intro h
  have hh := congrArg (fun F : ℝ →L[ℝ] (ℝ × ℝ) => (F 1).2) h
  norm_num [disconnectedReturn] at hh

 theorem disconnected_memory_zero (t : ℝ) : disconnectedReturn.memory t = 0 := by
  apply ContinuousLinearMap.ext
  intro y
  simp [memory, disconnectedReturn, flow]

 theorem disconnected_prepared_exact (t : ℝ) :
    disconnectedReturn.prepared t = flow disconnectedReturn.A t :=
  (disconnectedReturn.prepared_exact_iff_memory_zero).mpr disconnected_memory_zero t

 theorem disconnected_all_state_not_closed :
    ¬ (∀ t y z, disconnectedReturn.visible y z t = flow disconnectedReturn.A t y) := by
  intro h
  exact disconnected_B_ne_zero ((disconnectedReturn.all_state_closure_iff_B_zero).mp h)

/-- Hidden initialization is observed immediately despite exact prepared closure. -/
 theorem disconnected_initial_derivative :
    HasDerivAt (disconnectedReturn.visible 0 (1,0)) 1 0 := by
  simpa [disconnectedReturn] using disconnectedReturn.hasDerivAt_visible 0 (1,0) 0

end Komorebi.SufficientResolution.ContinuousExamples
