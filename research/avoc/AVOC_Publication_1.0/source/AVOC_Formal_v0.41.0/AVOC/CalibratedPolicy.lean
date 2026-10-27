import AVOC.CalibrationSchedule
import AVOC.CalibrationBridge

namespace Komorebi.AVOC.Affine.CalibratedPolicy
open Komorebi.AVOC
open QuoteAuthority RobustQuote CalibrationBridge

/-- The proved numeric endpoints inhabit the existing v0.38 probability type. -/
def learnedBand (n k m : Nat) (alpha : ℚ) : ProbabilityBand :=
  ⟨⟨FiniteCalibration.lower n k m alpha, FiniteCalibration.upper n k m alpha,
    FiniteCalibration.lower_le_upper n k m alpha⟩,
    FiniteCalibration.lower_nonneg n k m alpha,
    FiniteCalibration.upper_le_one n k m alpha⟩

@[simp] theorem learnedBand_contains (n k m : Nat) (alpha p : ℚ) :
    (learnedBand n k m alpha).Contains p ↔ FiniteCalibration.Contains n k m alpha p :=
  Iff.rfl

/-- A fixed model admits the stated true probabilities and the full conditional
Bellman/Q/expected-policy-regret theorem. -/
def EpisodeCertified {r c : Nat} (md : QModel r c) (wp cp : ℚ)
    (ws cs : Nat) (wg cg : ℚ) : Prop :=
  ∃ realization : Realization md,
    realization.warm.probability = wp ∧ realization.cold.probability = cp ∧
      realization.warm.setup = ws ∧ realization.cold.setup = cs ∧
      realization.warm.gross = wg ∧ realization.cold.gross = cg ∧
      FrozenEpisodeGuarantee md realization

variable {Ω J : Type*} [Fintype Ω] [Fintype J] {r c : Nat}

/-- Coverage of the actual learned-band-to-policy composition. The warm/cold
selectors can depend on all observed data but must select their respective
fixed true parameter strata. The model is frozen after selection for each
policy episode. No independence between checkpoints is required. -/
theorem learned_episode_coverage
    (law : CalibrationSchedule.Law Ω) (md : QModel r c)
    (d : DeterministicRealization md)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      CalibrationSchedule.eventMass law (fun ω => count j ω = k) =
        FiniteCalibration.mass (n j) k.val (p j))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (selectWarm ω) = wp)
    (hcparam : ∀ ω, p (selectCold ω) = cp) :
    1 - ∑ j, alpha j ≤ CalibrationSchedule.eventMass law (fun ω =>
      EpisodeCertified (replaceProbabilityBands md
        (learnedBand (n (selectWarm ω)) (count (selectWarm ω) ω).val
          (m (selectWarm ω)) (alpha (selectWarm ω)))
        (learnedBand (n (selectCold ω)) (count (selectCold ω) ω).val
          (m (selectCold ω)) (alpha (selectCold ω)))) wp cp
        d.warmSetup d.coldSetup d.warmGross d.coldGross) := by
  let bad : J → Ω → Prop := fun j ω =>
    ¬ FiniteCalibration.Contains (n j) (count j ω).val (m j) (alpha j) (p j)
  have hb : ∀ j, CalibrationSchedule.eventMass law (bad j) ≤ alpha j := by
    intro j
    exact CalibrationSchedule.binomial_failure_le law (n j) (m j) (hm j)
      (alpha j) (p j) (ha j) (hp0 j) (hp1 j) (count j) (count_law j)
  have hg := CalibrationSchedule.simultaneous_coverage law bad alpha hb
  apply hg.trans
  apply CalibrationSchedule.eventMass_mono
  intro ω hall
  have hw : (learnedBand (n (selectWarm ω)) (count (selectWarm ω) ω).val
      (m (selectWarm ω)) (alpha (selectWarm ω))).Contains wp := by
    have h := Classical.not_not.mp (hall (selectWarm ω))
    change FiniteCalibration.Contains _ _ _ _ wp
    simpa only [hwparam ω] using h
  have hc : (learnedBand (n (selectCold ω)) (count (selectCold ω) ω).val
      (m (selectCold ω)) (alpha (selectCold ω))).Contains cp := by
    have h := Classical.not_not.mp (hall (selectCold ω))
    change FiniteCalibration.Contains _ _ _ _ cp
    simpa only [hcparam ω] using h
  exact ⟨calibratedRealization md _ _ d wp cp hw hc, rfl, rfl, rfl, rfl, rfl, rfl,
    calibrated_frozen_episode_guarantee md _ _ d wp cp hw hc⟩

end Komorebi.AVOC.Affine.CalibratedPolicy
