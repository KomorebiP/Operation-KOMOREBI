import Komorebi.HybridPosteriorGuarantee
import Komorebi.TaggedPrecisionSearch

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.QuadraticTransport
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Try cheaper requested precisions, with a proved sufficient precision as a finite fallback. -/
def hybridScheduled (probes : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (B : Matrix ι κ ℚ) :
    Option (ℕ × RationalCandidate ι κ α β) :=
  if 0 < ε then
    match solveGain M Q D (ε/2) B with
    | none => none
    | some c =>
      let p := sufficientPrecision M Q D c.gain (ε^2/4)
      certifyTagged (probes ++ [p]) M Q D c.gain ε
  else none

/-- Successful scheduled returns retain exact checker soundness. -/
theorem hybridScheduled_sound (probes : List ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : hybridScheduled probes M Q D ε B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  unfold hybridScheduled at hr
  split at hr
  · cases hc : solveGain M Q D (ε/2) B with
    | none => simp [hc] at hr
    | some d =>
      simp only [hc] at hr
      exact certifyRounded_sound p M Q D d.gain ε c (certifyTagged_origin _ M Q D _ ε p c hr).2
  · simp at hr

/-- Every finite probes is allowed: the sufficient fallback makes the hybrid schedule total. -/
theorem hybridScheduled_terminates (probes : List ℕ) (M : RationalModel ι κ υ ω)
    (hs : 0 < M.noiseFloor) (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (B : Matrix ι κ ℚ) :
    ∃ p c, hybridScheduled probes M Q D ε B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  obtain ⟨c,hc,hcheck,htol⟩ := solveGain_terminates M hs Q D hQ hD (ε/2) (by positivity) B
  let p := sufficientPrecision M Q D c.gain (ε^2/4)
  have hr := certifyRounded_of_slack M Q D c.gain hs hQ hD ε (ε^2/4) hε.le
    (by positivity) (half_tolerance_slack M Q D ε c hcheck htol) p le_rfl
  obtain ⟨q,d,hd⟩ := certifyTagged_complete (probes++[p]) p (by simp) M Q D c.gain ε _ hr
  have hrun : hybridScheduled probes M Q D ε B = some (q,d) := by
    simpa only [hybridScheduled,ite_eq_left hε,hc] using hd
  exact ⟨q,d,hrun,hybridScheduled_sound probes M Q D ε B q d hrun⟩

noncomputable section
/-- The scheduled program's total correctness is stated for actual posterior distributions. -/
theorem scheduled_hybrid_reaches_posterior_tolerance (probes : List ℕ)
    (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (B : Matrix ι κ ℚ) :
    ∃ p c, hybridScheduled probes M Q D ε B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true ∧
      wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  obtain ⟨p,c,hr,hcheck,htol⟩ := hybridScheduled_terminates probes M hs Q D hQ hD ε hε B
  exact ⟨p,c,hr,hcheck,htol,checked_tolerance_bounds_posterior M Q D c ε hcheck htol⟩
end
end Komorebi.RoundedPosterior
