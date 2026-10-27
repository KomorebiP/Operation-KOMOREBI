import AVOC.ObservationStream
import AVOC.ObservationReveal
import AVOC.ObservedCalibration

namespace Komorebi.AVOC.ObservationPolicy

open CalibrationSchedule ObservationStream ObservationReveal

/-- First-n unique reports, available only once n reports have been stored.
Both success and rejection count toward readiness. -/
def availableCount (n : Nat) (reports : List Bool) : Option (Fin (n + 1)) :=
  if n ≤ reports.length then
    some ⟨(reports.take n).count true, Nat.lt_succ_iff.mpr
      (List.count_le_length.trans (by simp only [List.length_take]; omega))⟩
  else none

theorem availableCount_missing (n : Nat) (reports : List Bool)
    (h : reports.length < n) : availableCount n reports = none := by
  simp [availableCount, Nat.not_le.mpr h]

theorem availableCount_value (n : Nat) (reports : List Bool) (k : Fin (n + 1))
    (h : availableCount n reports = some k) :
    n ≤ reports.length ∧ k.val = (reports.take n).count true := by
  unfold availableCount at h
  split at h
  · rename_i hn
    exact ⟨hn, congrArg Fin.val (Option.some.inj h).symm⟩
  · simp at h

variable {Ω : Type*} {J K : Type} [DecidableEq K]

/-- Multiple checkpoints can read different prefixes of the same identity's
single report history. The trace itself may depend on the entire outcome. -/
def observedCounts (n : J → Nat) (key : J → K)
    (source : Ω → K → List Bool) (trace : Ω → List (Option K))
    (j : J) (ω : Ω) : Option (Fin (n j + 1)) :=
  availableCount (n j) ((run (source ω) (trace ω)).reports (key j))

/-- The recursive machine, rather than a supplied count correspondence, proves
that every available checkpoint count is its fixed latent prefix count. -/
theorem observedCounts_faithful
    (n : J → Nat) (key : J → K)
    (source : Ω → K → List Bool) (trace : Ω → List (Option K))
    (stream : (j : J) → Ω → Sample (n j))
    (hprefix : ∀ j ω, sampleList (stream j ω) = (source ω (key j)).take (n j)) :
    ObservedCalibration.Faithful n (fun j => streamCount (stream j))
      (observedCounts n key source trace) := by
  intro j ω k hk
  have hav := availableCount_value (n j)
    ((run (source ω) (trace ω)).reports (key j)) k hk
  apply Fin.ext
  change k.val = (stream j ω).card
  rw [hav.2, run_reports_eq_take, List.take_take, Nat.min_eq_left hav.1,
    ← hprefix, sampleList_count_true]

variable [Fintype Ω] [Fintype J]

/-- Universal calibration bound for actual available counts from the recursive
reveal machine. Its premise concerns primitive outcome vectors, not counts. -/
theorem revealed_failure_le
    (law : Law Ω) (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (key : J → K) (source : Ω → K → List Bool) (trace : Ω → List (Option K))
    (stream : (j : J) → Ω → Sample (n j))
    (hprefix : ∀ j ω, sampleList (stream j ω) = (source ω (key j)).take (n j))
    (hlaw : ∀ j, ProductLaw law (n j) (p j) (stream j)) :
    eventMass law (fun ω => ∃ j k, observedCounts n key source trace j ω = some k ∧
      ¬ FiniteCalibration.Contains (n j) k.val (m j) (alpha j) (p j)) ≤ ∑ j, alpha j := by
  exact ObservedCalibration.observed_failure_le law n m alpha p hm ha hp0 hp1
    (fun j => streamCount (stream j))
    (fun j => count_fiber_eq_binomial law (n j) (p j) (stream j) (hlaw j))
    (observedCounts n key source trace)
    (observedCounts_faithful n key source trace stream hprefix)

open Komorebi.AVOC.Affine Affine.QuoteAuthority Affine.RobustQuote Affine.CalibrationBridge
  Affine.CalibratedPolicy

/-- Full primitive-stream, recursive-observation, calibration, and policy chain.
An issued plan is certified with unconditional error at most the allocated
finite schedule budget. No independence of completion or cross-identity streams
is required, and no assertion is made conditional on issuing a plan. -/
theorem revealed_episode_coverage {r c : Nat}
    (law : Law Ω) (md : QModel r c) (d : DeterministicRealization md)
    (n m : J → Nat) (alpha p : J → ℚ)
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ j, 0 ≤ p j) (hp1 : ∀ j, p j ≤ 1)
    (key : J → K) (source : Ω → K → List Bool) (trace : Ω → List (Option K))
    (stream : (j : J) → Ω → Sample (n j))
    (hprefix : ∀ j ω, sampleList (stream j ω) = (source ω (key j)).take (n j))
    (hlaw : ∀ j, ProductLaw law (n j) (p j) (stream j))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (selectWarm ω) = wp)
    (hcparam : ∀ ω, p (selectCold ω) = cp) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ planned,
      Affine.ObservedCalibration.observedPlan md n m alpha
        (observedCounts n key source trace) selectWarm selectCold ω = some planned →
      EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross) := by
  exact Affine.ObservedCalibration.observed_episode_coverage law md d n m alpha p hm ha hp0 hp1
    (fun j => streamCount (stream j))
    (fun j => count_fiber_eq_binomial law (n j) (p j) (stream j) (hlaw j))
    (observedCounts n key source trace)
    (observedCounts_faithful n key source trace stream hprefix)
    selectWarm selectCold wp cp hwparam hcparam

/-- One latent source per identity supports all scheduled prefixes. This final
form discharges both the count-law and checkpoint-prefix correspondence premises
from the conditional fresh-outcome contract and the concrete reveal machine. -/
theorem shared_stream_episode_coverage {r c : Nat}
    (law : Law Ω) (md : QModel r c) (d : DeterministicRealization md)
    (N : K → Nat) (p : K → ℚ) (base : (k : K) → Ω → Sample (N k))
    (hlaw : ∀ k, ConditionalLaw law (N k) (p k) (base k))
    (n m : J → Nat) (alpha : J → ℚ) (key : J → K)
    (hn : ∀ j, n j ≤ N (key j))
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ k, 0 ≤ p k) (hp1 : ∀ k, p k ≤ 1)
    (trace : Ω → List (Option K))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (key (selectWarm ω)) = wp)
    (hcparam : ∀ ω, p (key (selectCold ω)) = cp) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ planned,
      Affine.ObservedCalibration.observedPlan md n m alpha
        (observedCounts n key (fun ω k => sampleList (base k ω)) trace)
        selectWarm selectCold ω = some planned →
      EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross) := by
  exact revealed_episode_coverage law md d n m alpha (fun j => p (key j)) hm ha
    (fun j => hp0 (key j)) (fun j => hp1 (key j)) key
    (fun ω k => sampleList (base k ω)) trace
    (fun j ω => truncateSample (n j) (hn j) (base (key j) ω))
    (fun j ω => sampleList_truncate (hn j) (base (key j) ω))
    (fun j => conditional_implies_product law (n j) (p (key j)) _
      (conditional_truncate law (N (key j)) (p (key j)) (base (key j))
        (hlaw (key j)) (n j) (hn j)))
    selectWarm selectCold wp cp hwparam hcparam

/-- Direct error-budget form. An arbitrary probability of completing enough
reports is allowed; the bound concerns bad issuance over the original law. -/
theorem shared_stream_issued_failure_le {r c : Nat}
    (law : Law Ω) (md : QModel r c) (d : DeterministicRealization md)
    (N : K → Nat) (p : K → ℚ) (base : (k : K) → Ω → Sample (N k))
    (hlaw : ∀ k, ConditionalLaw law (N k) (p k) (base k))
    (n m : J → Nat) (alpha : J → ℚ) (key : J → K)
    (hn : ∀ j, n j ≤ N (key j))
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ k, 0 ≤ p k) (hp1 : ∀ k, p k ≤ 1)
    (trace : Ω → List (Option K))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (key (selectWarm ω)) = wp)
    (hcparam : ∀ ω, p (key (selectCold ω)) = cp) :
    eventMass law (fun ω => ∃ planned,
      Affine.ObservedCalibration.observedPlan md n m alpha
        (observedCounts n key (fun ω k => sampleList (base k ω)) trace)
        selectWarm selectCold ω = some planned ∧
      ¬ EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross) ≤
      ∑ j, alpha j := by
  have hg := shared_stream_episode_coverage law md d N p base hlaw n m alpha key hn
    hm ha hp0 hp1 trace selectWarm selectCold wp cp hwparam hcparam
  have hc := eventMass_add_compl law (fun ω => ∃ planned,
      Affine.ObservedCalibration.observedPlan md n m alpha
        (observedCounts n key (fun ω k => sampleList (base k ω)) trace)
        selectWarm selectCold ω = some planned ∧
      ¬ EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross)
  simp only [not_exists, not_and, not_not] at hc
  linarith

end Komorebi.AVOC.ObservationPolicy
