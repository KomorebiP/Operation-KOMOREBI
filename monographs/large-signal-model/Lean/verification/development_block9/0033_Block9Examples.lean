import KomorebiLSM.FinitePrefix
import KomorebiLSM.LearnedRealization

set_option autoImplicit false
namespace Komorebi.LSM.Block9Examples
open Identification Delay

theorem no_observed_prefix_identifies_all_futures (T : ℕ) :
    (∀ t ≤ T, output T ((shift (T+2)^t) (delayedInitial T)) = 0) ∧
    output T ((shift (T+2)^(T+1)) (delayedInitial T)) = 1 := by
  constructor
  · intro t ht; rw [delayed_output]; simp [show t ≠ T+1 by omega]
  · rw [delayed_output]; simp

theorem warmup_zero_boundary :
    observation (LinearMap.id : ℚ →ₗ[ℚ] ℚ) LinearMap.id 0 = 0 ∧
    observation (LinearMap.id : ℚ →ₗ[ℚ] ℚ) LinearMap.id 1 1 ⟨0,by decide⟩ = 1 := by
  constructor
  · apply LinearMap.ext; intro x; funext i; exact Fin.elim0 i
  · rfl

def inputPlane : ℚ →ₗ[ℚ] (ℚ × ℚ) := LinearMap.inl ℚ ℚ ℚ

def firstFit : (ℚ × ℚ) →ₗ[ℚ] (ℚ × ℚ) := LinearMap.id

def secondFit : (ℚ × ℚ) →ₗ[ℚ] (ℚ × ℚ) :=
  LinearMap.prod (LinearMap.fst ℚ ℚ ℚ) (2 • LinearMap.snd ℚ ℚ ℚ)

theorem empirical_closed_span_not_coverage :
    firstFit.comp inputPlane = inputPlane ∧ secondFit.comp inputPlane = inputPlane ∧
    firstFit (0,1) ≠ secondFit (0,1) := by
  constructor
  · rfl
  constructor
  · apply LinearMap.ext; intro x; ext <;> simp [secondFit,inputPlane]
  · norm_num [firstFit,secondFit]

theorem inconsistent_zero_input :
    ¬ ∃ B : ℚ →ₗ[ℚ] ℚ, B.comp (0 : ℚ →ₗ[ℚ] ℚ) = LinearMap.id := by
  rintro ⟨B,hB⟩
  have he := congrArg (fun F : ℚ →ₗ[ℚ] ℚ => F 1) hB
  norm_num at he

theorem pinv_identity : pinv (LinearMap.id : ℝ →ₗ[ℝ] ℝ) = LinearMap.id := by
  apply LinearMap.ext
  intro x
  have he := apply_retained (LinearMap.id : ℝ →ₗ[ℝ] ℝ) x
  simpa using (pinv_apply_image (LinearMap.id : ℝ →ₗ[ℝ] ℝ) x).trans he

theorem learned_scalar_exact :
    learned (LinearMap.id : ℝ →ₗ[ℝ] ℝ) (3 • LinearMap.id) = 3 • LinearMap.id := by
  apply learned_eq_true
  · exact Function.surjective_id
  · simp

/-- With true B=1, input=1, input perturbation=-1/2 and no output error,
the fitted scalar is 2 and the denominator bound is attained. -/
theorem scalar_perturbation_sharp :
    |(1 : ℝ)/(1-1/2)-1| = (1*(1/2))/(1-1/2) := by norm_num

theorem perturbation_boundary_collapses_rank : (1 : ℝ) + (-1) = 0 ∧ |(-1 : ℝ)| = 1 := by norm_num

theorem unstable_rollout_amplifies (t : ℕ) : (2 : ℚ)^(t+1) = 2*2^t := by ring

end Komorebi.LSM.Block9Examples
