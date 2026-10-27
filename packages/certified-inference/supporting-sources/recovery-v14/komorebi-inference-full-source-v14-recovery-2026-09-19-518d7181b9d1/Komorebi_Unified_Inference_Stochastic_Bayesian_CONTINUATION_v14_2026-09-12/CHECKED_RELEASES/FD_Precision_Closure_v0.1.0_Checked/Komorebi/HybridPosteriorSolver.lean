import Komorebi.PrecisionCompleteness
import Komorebi.ExactCandidateMinimal
import Komorebi.RationalSolverSearch

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Manufacture exact slack using the retained solver, then choose and run a sufficient
outward-certification precision. Gain iteration remains exact rational arithmetic. -/
def hybridSolve (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (B : Matrix ι κ ℚ) :
    Option (ℕ × RationalCandidate ι κ α β) :=
  if 0 < ε then
    match solveGain M Q D (ε/2) B with
    | none => none
    | some c =>
      let p := sufficientPrecision M Q D c.gain (ε^2/4)
      match certifyRounded p M Q D c.gain ε with
      | none => none
      | some d => some (p,d)
  else none

/-- Every successful hybrid return passes the exact candidate and tolerance checks. -/
theorem hybridSolve_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β) (hr : hybridSolve M Q D ε B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  unfold hybridSolve at hr
  split at hr
  · cases hc : solveGain M Q D (ε/2) B with
    | none => simp [hc] at hr
    | some d =>
      simp only [hc] at hr
      cases hd : certifyRounded (sufficientPrecision M Q D d.gain (ε^2/4)) M Q D d.gain ε with
      | none => simp [hd] at hr
      | some e =>
        simp only [hd,Option.some.injEq,Prod.mk.injEq] at hr
        rw [← hr.2]
        exact certifyRounded_sound _ M Q D d.gain ε e hd
  · simp at hr

/-- A half-tolerance certificate supplies enough strict slack for the rounded verifier. -/
theorem half_tolerance_slack (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ)
    (c : RationalCandidate ι κ α β) (hc : checkCandidate M Q D c = true)
    (ht : checkTolerance M c (ε/2) = true) :
    candidateScore M (exactCandidate M Q D c.gain)+ε^2/4 ≤ ε^2 := by
  have h := (checkCandidate_eq_true M Q D c).mp hc
  have hscore := (checkTolerance_iff_score M c (ε/2) h.1).mp ht
  have hm := exactCandidate_score_le_valid M Q D c h
  nlinarith only [hm,hscore.2,sq_nonneg ε]

/-- Positive tolerance forces an actual return of the executable hybrid program. -/
theorem hybridSolve_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (B : Matrix ι κ ℚ) :
    ∃ p c, hybridSolve M Q D ε B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  obtain ⟨c,hc,hcheck,htol⟩ := solveGain_terminates M hs Q D hQ hD (ε/2) (by positivity) B
  let p := sufficientPrecision M Q D c.gain (ε^2/4)
  have hr := certifyRounded_of_slack M Q D c.gain hs hQ hD ε (ε^2/4) hε.le
    (by positivity) (half_tolerance_slack M Q D ε c hcheck htol) p le_rfl
  have hrun : hybridSolve M Q D ε B = some (p,roundedCandidate p M Q D c.gain) := by
    simp only [hybridSolve,ite_eq_left hε,hc]
    exact congrArg (fun r => match r with | none => none | some d => some (p,d)) hr
  exact ⟨p,roundedCandidate p M Q D c.gain,hrun,hybridSolve_sound M Q D ε B _ _ hrun⟩

end Komorebi.RoundedPosterior
