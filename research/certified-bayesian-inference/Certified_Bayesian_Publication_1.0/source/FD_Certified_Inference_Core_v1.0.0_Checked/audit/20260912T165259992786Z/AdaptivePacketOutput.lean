import Komorebi.AdaptivePacketPosterior
import Komorebi.PosteriorOutputSolver

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior Komorebi.PosteriorOutput
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

def runAdaptive (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε δ : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) : Option (Result ι κ α β) :=
  if 0 < δ then
    match solveAdaptive M Q D seed scan ε probes B with
    | none => none
    | some (p,c) => some ⟨p,c,outputPrecision M c.gain δ,represent M c.gain δ⟩
  else none

theorem runAdaptive_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan)
    (ε δ : ℚ) (hε : 0 < ε) (hδ : 0 < δ) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ r, runAdaptive M Q D seed scan ε δ probes B = some r ∧ ResultValid M Q D ε δ r := by
  obtain ⟨p,c,hret,hc,ht,hw⟩ :=
    adaptive_solver_reaches_posterior_tolerance M hs Q D hQ hD seed scan hscan ε hε probes B
  refine ⟨⟨p,c,outputPrecision M c.gain δ,represent M c.gain δ⟩, ?_, ?_⟩
  · simp only [runAdaptive, ite_eq_left hδ, hret]
  · obtain ⟨he,hr⟩ := represent_spec M c.gain δ hδ
    exact ⟨hc,ht,hw,he,hr,rfl,rfl⟩

/-- Any successful return is sound, without validity assumptions supplied by the caller. -/
theorem runAdaptive_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε δ : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) (r : Result ι κ α β)
    (hr : runAdaptive M Q D seed scan ε δ probes B = some r) : ResultValid M Q D ε δ r := by
  unfold runAdaptive at hr
  split at hr
  next hδ =>
    cases hs : solveAdaptive M Q D seed scan ε probes B with
    | none => simp only [hs] at hr; contradiction
    | some pc =>
      obtain ⟨p,c⟩ := pc
      simp only [hs, Option.some.injEq] at hr
      subst r
      obtain ⟨hc,ht⟩ := solveAdaptive_sound M Q D seed scan ε probes B p c hs
      obtain ⟨he,hprec⟩ := represent_spec M c.gain δ hδ
      exact ⟨hc,ht,adaptive_solver_return_bounds_posterior M Q D seed scan ε probes B p c hs,
        he,hprec,rfl,rfl⟩
  next => contradiction

theorem runAdaptive_rejects_nonpositive_output_tolerance (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε δ : ℚ) (hδ : δ ≤ 0) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    runAdaptive M Q D seed scan ε δ probes B = none := by
  simp only [runAdaptive, ite_eq_right (not_lt.mpr hδ)]

end Komorebi.AdaptivePosterior
