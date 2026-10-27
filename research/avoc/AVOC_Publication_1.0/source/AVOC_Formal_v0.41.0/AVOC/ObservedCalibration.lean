import AVOC.CalibratedPolicy

namespace Komorebi.AVOC.ObservedCalibration

open CalibrationSchedule

variable {Ω J : Type*} [Fintype Ω] [Fintype J]

/-- An observation may be unavailable. Any available count must be the fixed
latent prefix count for its scheduled checkpoint; completeness is not conditioned on. -/
def Faithful (n : J → Nat) (count : (j : J) → Ω → Fin (n j + 1))
    (observed : (j : J) → Ω → Option (Fin (n j + 1))) : Prop :=
  ∀ j ω k, observed j ω = some k → k = count j ω

/-- The bad-issued event is a subset of the simultaneous fixed-prefix bad event,
even if availability and selection depend on all outcomes. -/
theorem observed_failure_le
    (law : Law Ω) (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) = FiniteCalibration.mass (n j) k.val (p j))
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (faithful : Faithful n count observed) :
    eventMass law (fun ω => ∃ j k, observed j ω = some k ∧
      ¬ FiniteCalibration.Contains (n j) k.val (m j) (alpha j) (p j)) ≤
      ∑ j, alpha j := by
  apply (eventMass_mono law (b := fun ω => ∃ j,
    ¬ FiniteCalibration.Contains (n j) (count j ω).val (m j) (alpha j) (p j)) ?_).trans
  · exact scheduled_binomial_failure_le law n m alpha p hm ha hp0 hp1 count count_law
  · rintro ω ⟨j, k, hk, hbad⟩
    exact ⟨j, by simpa only [faithful j ω k hk] using hbad⟩

/-- Availability is a gate, not an assumption that completion was independent. -/
theorem observed_coverage
    (law : Law Ω) (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) = FiniteCalibration.mass (n j) k.val (p j))
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (faithful : Faithful n count observed) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ j k,
      observed j ω = some k → FiniteCalibration.Contains (n j) k.val (m j) (alpha j) (p j)) := by
  have hb := observed_failure_le law n m alpha p hm ha hp0 hp1 count count_law observed faithful
  have hc := eventMass_add_compl law (fun ω => ∃ j k, observed j ω = some k ∧
    ¬ FiniteCalibration.Contains (n j) k.val (m j) (alpha j) (p j))
  simp only [not_exists, not_and, not_not] at hc
  linarith

end Komorebi.AVOC.ObservedCalibration

namespace Komorebi.AVOC.Affine.ObservedCalibration

open Komorebi.AVOC
open CalibrationSchedule QuoteAuthority RobustQuote CalibrationBridge CalibratedPolicy

variable {Ω J : Type*} {r c : Nat}

/-- A plan exists only when both selected checkpoints are available. -/
def observedPlan (md : QModel r c) (n m : J → Nat) (alpha : J → ℚ)
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (selectWarm selectCold : Ω → J) (ω : Ω) : Option (QModel r c) := do
  let warm ← observed (selectWarm ω) ω
  let cold ← observed (selectCold ω) ω
  pure (replaceProbabilityBands md
    (learnedBand (n (selectWarm ω)) warm.val (m (selectWarm ω)) (alpha (selectWarm ω)))
    (learnedBand (n (selectCold ω)) cold.val (m (selectCold ω)) (alpha (selectCold ω))))

/-- A missing selected checkpoint prevents plan issuance. -/
theorem observedPlan_none_warm (md : QModel r c) (n m : J → Nat) (alpha : J → ℚ)
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (selectWarm selectCold : Ω → J) (ω : Ω)
    (h : observed (selectWarm ω) ω = none) :
    observedPlan md n m alpha observed selectWarm selectCold ω = none := by
  simp [observedPlan, h]

theorem observedPlan_none_cold (md : QModel r c) (n m : J → Nat) (alpha : J → ℚ)
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (selectWarm selectCold : Ω → J) (ω : Ω)
    (h : observed (selectCold ω) ω = none) :
    observedPlan md n m alpha observed selectWarm selectCold ω = none := by
  cases hw : observed (selectWarm ω) ω <;> simp [observedPlan, hw, h]

/-- On simultaneous coverage, every issued plan admits the stated realization
and frozen-episode Bellman, Q, and expected-policy-regret guarantee. -/
theorem observedPlan_certified (md : QModel r c) (d : DeterministicRealization md)
    (n m : J → Nat) (alpha p : J → ℚ)
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (selectWarm ω) = wp)
    (hcparam : ∀ ω, p (selectCold ω) = cp) (ω : Ω)
    (hall : ∀ j k, observed j ω = some k →
      FiniteCalibration.Contains (n j) k.val (m j) (alpha j) (p j)) :
    ∀ planned, observedPlan md n m alpha observed selectWarm selectCold ω = some planned →
      EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross := by
  intro planned hplan
  cases hw : observed (selectWarm ω) ω with
  | none => simp [observedPlan, hw] at hplan
  | some w =>
    cases hc : observed (selectCold ω) ω with
    | none => simp [observedPlan, hw, hc] at hplan
    | some c =>
      simp [observedPlan, hw, hc] at hplan
      subst planned
      have hwb : (learnedBand (n (selectWarm ω)) w.val
          (m (selectWarm ω)) (alpha (selectWarm ω))).Contains wp := by
        change FiniteCalibration.Contains _ _ _ _ wp
        simpa only [hwparam ω] using hall (selectWarm ω) w hw
      have hcb : (learnedBand (n (selectCold ω)) c.val
          (m (selectCold ω)) (alpha (selectCold ω))).Contains cp := by
        change FiniteCalibration.Contains _ _ _ _ cp
        simpa only [hcparam ω] using hall (selectCold ω) c hc
      exact ⟨calibratedRealization md _ _ d wp cp hwb hcb, rfl, rfl, rfl, rfl, rfl, rfl,
        calibrated_frozen_episode_guarantee md _ _ d wp cp hwb hcb⟩

/-- With probability at least one minus the finite allocated budget, either no
plan is issued or every issued plan is certified. This is an unconditional
statement; it does not divide by the probability of obtaining enough reports. -/
theorem observed_episode_coverage [Fintype Ω] [Fintype J]
    (law : Law Ω) (md : QModel r c) (d : DeterministicRealization md)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (count : (j : J) → Ω → Fin (n j + 1))
    (count_law : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => count j ω = k) = FiniteCalibration.mass (n j) k.val (p j))
    (observed : (j : J) → Ω → Option (Fin (n j + 1)))
    (faithful : Komorebi.AVOC.ObservedCalibration.Faithful n count observed)
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (selectWarm ω) = wp)
    (hcparam : ∀ ω, p (selectCold ω) = cp) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ planned,
      observedPlan md n m alpha observed selectWarm selectCold ω = some planned →
        EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross) := by
  apply (Komorebi.AVOC.ObservedCalibration.observed_coverage law n m alpha p hm ha hp0 hp1
    count count_law observed faithful).trans
  exact eventMass_mono law (observedPlan_certified md d n m alpha p observed
    selectWarm selectCold wp cp hwparam hcparam)

end Komorebi.AVOC.Affine.ObservedCalibration
