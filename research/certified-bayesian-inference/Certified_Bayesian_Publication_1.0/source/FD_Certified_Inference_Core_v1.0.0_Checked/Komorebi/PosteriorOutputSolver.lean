import Komorebi.PosteriorOutputSemantics
import Komorebi.RoundedSolverPosterior

set_option autoImplicit false
namespace Komorebi.PosteriorOutput
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior
open Komorebi.RoundoffSolver Komorebi.QuadraticTransport
variable {ι κ υ ω α β : Type*}

structure Result (ι κ α β : Type*) where
  verificationPrecision : ℕ
  candidate : RationalCandidate ι κ α β
  parameterPrecision : ℕ
  arrays : Arrays ι

variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

def run (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε δ : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) : Option (Result ι κ α β) :=
  if 0 < δ then
    match solveRounded M Q D ε probes B with
    | none => none
    | some (p,c) => some ⟨p,c,outputPrecision M c.gain δ,represent M c.gain δ⟩
  else none

noncomputable def ResultValid (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε δ : ℚ) (r : Result ι κ α β) : Prop :=
  checkCandidate M Q D r.candidate = true ∧
  checkTolerance M r.candidate ε = true ∧
  wasserstein2 M.posterior (M.approximation r.candidate.gain) ≤ ENNReal.ofReal (ε : ℝ) ∧
  EnclosesParameters M r.candidate.gain r.arrays ∧ RadiiAtMost r.arrays δ ∧
  r.parameterPrecision = outputPrecision M r.candidate.gain δ ∧
  r.arrays = evaluate r.parameterPrecision M r.candidate.gain

theorem run_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε δ : ℚ) (hε : 0 < ε) (hδ : 0 < δ) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ r, run M Q D ε δ probes B = some r ∧ ResultValid M Q D ε δ r := by
  obtain ⟨p,c,hret,hc,ht,hw⟩ :=
    rounded_solver_reaches_posterior_tolerance M hs Q D hQ hD ε hε probes B
  refine ⟨⟨p,c,outputPrecision M c.gain δ,represent M c.gain δ⟩, ?_, ?_⟩
  · simp only [run, ite_eq_left hδ, hret]
  · obtain ⟨he,hr⟩ := represent_spec M c.gain δ hδ
    exact ⟨hc,ht,hw,he,hr,rfl,rfl⟩

/-- Any successful return is sound, without validity assumptions supplied by the caller. -/
theorem run_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε δ : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) (r : Result ι κ α β)
    (hr : run M Q D ε δ probes B = some r) : ResultValid M Q D ε δ r := by
  unfold run at hr
  split at hr
  next hδ =>
    cases hs : solveRounded M Q D ε probes B with
    | none => simp only [hs] at hr; contradiction
    | some pc =>
      obtain ⟨p,c⟩ := pc
      simp only [hs, Option.some.injEq] at hr
      subst r
      obtain ⟨hc,ht⟩ := solveRounded_sound M Q D ε probes B p c hs
      obtain ⟨he,hprec⟩ := represent_spec M c.gain δ hδ
      exact ⟨hc,ht,rounded_solver_return_bounds_posterior M Q D ε probes B p c hs,
        he,hprec,rfl,rfl⟩
  next => contradiction

theorem run_rejects_nonpositive_output_tolerance (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε δ : ℚ) (hδ : δ ≤ 0) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    run M Q D ε δ probes B = none := by
  simp only [run, ite_eq_right (not_lt.mpr hδ)]

end Komorebi.PosteriorOutput
