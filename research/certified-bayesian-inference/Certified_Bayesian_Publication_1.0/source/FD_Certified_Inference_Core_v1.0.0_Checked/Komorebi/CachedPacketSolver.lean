import Komorebi.CachedPacketSearch
import Komorebi.AdaptivePacketPosterior
import Komorebi.RoundedSolverOrigin

set_option autoImplicit false
namespace Komorebi.CachedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.AdaptivePosterior
open Komorebi.RoundedPosterior Komorebi.RoundoffSolver Komorebi.QuadraticTransport
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Precompute model constants, run cached iteration, and invoke rounded certification once. -/
def solveCached (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) : Option (ℕ × RationalCandidate ι κ α β) :=
  if 0 < ε ∧ checkSetup M Q D = true ∧ ∀ a, a ∈ scan then
    let K := prepare M
    match search K seed scan ε (adaptiveFuel M B ε (Fintype.card α)) (initialState M Q B) with
    | none => none
    | some c => certifyGain M Q D ε probes c.gain
  else none

theorem solveCached_sound (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β) (hr : solveCached M Q D seed scan ε probes B = some (p,c)) :
    checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  unfold solveCached at hr
  split at hr
  · dsimp only at hr
    split at hr
    · contradiction
    · exact certifyGain_sound M Q D ε probes _ p c hr
  · contradiction

theorem solveCached_terminates (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ p c, solveCached M Q D seed scan ε probes B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true := by
  let init := initialState M Q B
  let fuel := adaptiveFuel M B ε (Fintype.card α)
  have hv : Valid M Q init := initialState_valid M Q B
  have hp := trajectory_score_at_fuel M hs Q hQ init hv seed scan hscan ε hε fuel le_rfl
  obtain ⟨out,hr⟩ := search_complete (prepare M) seed scan ε fuel init hp
  obtain ⟨k,_,he⟩ := search_origin (prepare M) seed scan ε fuel init out hr
  have ho : Valid M Q out := by rw [he]; exact trajectory_valid M Q hQ init hv seed scan k
  have hb : M.residualScore out.gain ≤ ε^2/4 := by
    rw [← score_eq M Q hQ out ho]
    exact search_score (prepare M) seed scan ε fuel init out hr
  obtain ⟨p,c,hc⟩ := certifyGain_complete M hs Q D hQ hD ε hε probes out.gain hb
  have hg := (checkSetup_eq_true M Q D).mpr ⟨hs,hQ,hD⟩
  have hout : solveCached M Q D seed scan ε probes B = some (p,c) := by
    rw [solveCached,ite_eq_left ⟨hε,hg,hscan⟩]
    change (match search (prepare M) seed scan ε fuel init with | none => none | some x => certifyGain M Q D ε probes x.gain) = _
    rw [hr]; exact hc
  exact ⟨p,c,hout,solveCached_sound M Q D seed scan ε probes B p c hout⟩

theorem cached_solver_return_bounds_posterior (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ)
    (p : ℕ) (c : RationalCandidate ι κ α β) (hr : solveCached M Q D seed scan ε probes B = some (p,c)) :
    wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  have h := solveCached_sound M Q D seed scan ε probes B p c hr
  exact checked_tolerance_bounds_posterior M Q D c ε h.1 h.2

theorem cached_solver_reaches_posterior_tolerance (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan)
    (ε : ℚ) (hε : 0 < ε) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    ∃ p c, solveCached M Q D seed scan ε probes B = some (p,c) ∧
      checkCandidate M Q D c = true ∧ checkTolerance M c ε = true ∧
      wasserstein2 M.posterior (M.approximation c.gain) ≤ ENNReal.ofReal (ε : ℝ) := by
  obtain ⟨p,c,hr,hc,ht⟩ := solveCached_terminates M hs Q D hQ hD seed scan hscan ε hε probes B
  exact ⟨p,c,hr,hc,ht,cached_solver_return_bounds_posterior M Q D seed scan ε probes B p c hr⟩

end Komorebi.CachedPosterior
