import Komorebi.RoundoffConvergence
import Komorebi.TaggedPrecisionSearch

set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Try requested certificate precisions, with a sufficient-precision fallback for a good gain. -/
def certifyGain (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) : Option (ℕ × RationalCandidate ι κ α β) :=
  certifyTagged (probes++[sufficientPrecision M Q D B (ε^2/4)]) M Q D B ε

theorem certifyGain_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : certifyGain M Q D ε probes B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  have h := certifyTagged_origin _ M Q D B ε p c hr
  exact certifyRounded_sound p M Q D B ε c h.2

/-- The computed verification fallback succeeds once rounded gain iteration has made enough progress. -/
theorem certifyGain_complete (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (hscore : M.residualScore B ≤ ε^2/4) :
    ∃ p c, certifyGain M Q D ε probes B = some (p,c) := by
  let p := sufficientPrecision M Q D B (ε^2/4)
  have hm : candidateScore M (exactCandidate M Q D B)+ε^2/4 ≤ ε^2 := by
    rw [exactCandidate_score M Q D hQ hD]
    nlinarith only [hscore,sq_nonneg ε]
  have hr := certifyRounded_of_slack M Q D B hs hQ hD ε (ε^2/4) hε.le
    (by positivity) hm p le_rfl
  exact certifyTagged_complete _ p (by simp [p]) M Q D B ε _ hr

/-- Every failed verification is followed by a genuinely rounded gain update. -/
def solveRoundedFuel (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (t : ℕ) : ℕ → Matrix ι κ ℚ → Option (ℕ × RationalCandidate ι κ α β)
  | 0, B => certifyGain M Q D ε probes B
  | n+1, B =>
    match certifyGain M Q D ε probes B with
    | some r => some r
    | none => solveRoundedFuel M Q D ε probes t n (roundedGainStep M t B)

theorem solveRoundedFuel_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (t n : ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveRoundedFuel M Q D ε probes t n B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  induction n generalizing B with
  | zero => exact certifyGain_sound M Q D ε probes B p c hr
  | succ n ih =>
    cases hc : certifyGain M Q D ε probes B with
    | none =>
      exact ih _ (by simpa only [solveRoundedFuel,hc] using hr)
    | some r =>
      have he : r = (p,c) := by simpa only [solveRoundedFuel,hc,Option.some.injEq] using hr
      rw [he] at hc
      exact certifyGain_sound M Q D ε probes B p c hc

omit [Fintype α] [Fintype β] [DecidableEq ι] [DecidableEq α] [DecidableEq β] in
theorem roundedGain_shift (M : RationalModel ι κ υ ω) (t : ℕ) (B : Matrix ι κ ℚ) (n : ℕ) :
    roundedGain M t (roundedGainStep M t B) n = roundedGain M t B (n+1) := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [roundedGain_succ,ih]

/-- A passing final permitted iterate guarantees successful early-stopping execution. -/
theorem solveRoundedFuel_complete (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (t n : ℕ) (B : Matrix ι κ ℚ)
    (hp : ∃ p c, certifyGain M Q D ε probes (roundedGain M t B n) = some (p,c)) :
    ∃ p c, solveRoundedFuel M Q D ε probes t n B = some (p,c) := by
  induction n generalizing B with
  | zero => exact hp
  | succ n ih =>
    cases hc : certifyGain M Q D ε probes B with
    | some r => exact ⟨r.1,r.2,by simp only [solveRoundedFuel,hc]⟩
    | none =>
      have hp' : ∃ p c, certifyGain M Q D ε probes
          (roundedGain M t (roundedGainStep M t B) n) = some (p,c) := by
        simpa only [roundedGain_shift] using hp
      obtain ⟨p,c,hr⟩ := ih _ hp'
      exact ⟨p,c,by simpa only [solveRoundedFuel,hc] using hr⟩

/-- Total rounded-update solver. Exact rational preprocessing chooses precision and finite fuel. -/
def solveRounded (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) : Option (ℕ × RationalCandidate ι κ α β) :=
  if 0 < ε ∧ checkSetup M Q D = true then
    solveRoundedFuel M Q D ε probes (updateAccuracy M ε) (roundedFuel M B ε) B
  else none

theorem solveRounded_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β)
    (hr : solveRounded M Q D ε probes B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  unfold solveRounded at hr
  split at hr
  · exact solveRoundedFuel_sound M Q D ε probes _ _ B p c hr
  · simp at hr

/-- Success is guaranteed for every positive rational tolerance, not just asserted after a passing run. -/
theorem solveRounded_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ p c, solveRounded M Q D ε probes B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  have hscore := rounded_score_at_fuel M hs ε hε (updateAccuracy M ε) le_rfl
    B (roundedFuel M B ε) le_rfl
  have hp := certifyGain_complete M hs Q D hQ hD ε hε probes _ hscore
  obtain ⟨p,c,hr⟩ := solveRoundedFuel_complete M Q D ε probes _ _ B hp
  have hs0 := (checkSetup_eq_true M Q D).mpr ⟨hs,hQ,hD⟩
  have hout : solveRounded M Q D ε probes B = some (p,c) := by
    simpa only [solveRounded,hε,hs0,and_self,ite_true] using hr
  exact ⟨p,c,hout,solveRounded_sound M Q D ε probes B p c hout⟩

end Komorebi.RoundoffSolver
