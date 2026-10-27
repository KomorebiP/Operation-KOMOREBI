import AVOC.RecorderReveal
import AVOC.ObservationPolicy

namespace Komorebi.AVOC.RecorderPolicy

open CalibrationSchedule ObservationStream

variable {Ω : Type*} {J K : Type} [DecidableEq K]

/-- Only a completely accepted, fully resolved recorder run can supply samples.
Readiness of one identity does not bypass an unrelated pending operation. -/
def gatedCounts (n : J → Nat) (key : J → K)
    (source : Ω → K → List Bool) (commands : Ω → List (RecorderReveal.Command K))
    (j : J) (ω : Ω) : Option (Fin (n j + 1)) :=
  match RecorderReveal.run (source ω) (commands ω) with
  | none => none
  | some s => if s.recorder.pending = [] then
      ObservationPolicy.availableCount (n j) (CalibrationLog.samples (key j) s.recorder.log)
    else none

theorem rejected_run_no_count (n : J → Nat) (key : J → K)
    (source : Ω → K → List Bool) (commands : Ω → List (RecorderReveal.Command K))
    (ω : Ω) (h : RecorderReveal.run (source ω) (commands ω) = none) (j : J) :
    gatedCounts n key source commands j ω = none := by
  simp [gatedCounts, h]

theorem pending_run_no_count (n : J → Nat) (key : J → K)
    (source : Ω → K → List Bool) (commands : Ω → List (RecorderReveal.Command K))
    (ω : Ω) (s : RecorderReveal.State K)
    (h : RecorderReveal.run (source ω) (commands ω) = some s)
    (hp : s.recorder.pending ≠ []) (j : J) :
    gatedCounts n key source commands j ω = none := by
  simp [gatedCounts, h, hp]

/-- The entire recorder run proves count correspondence. No separate replay,
log-prefix, or per-step next-bit premise is supplied to this theorem. -/
theorem gatedCounts_faithful
    (n : J → Nat) (key : J → K)
    (source : Ω → K → List Bool) (commands : Ω → List (RecorderReveal.Command K))
    (stream : (j : J) → Ω → Sample (n j))
    (hprefix : ∀ j ω, sampleList (stream j ω) = (source ω (key j)).take (n j)) :
    ObservedCalibration.Faithful n (fun j => streamCount (stream j))
      (gatedCounts n key source commands) := by
  intro j ω k hk
  unfold gatedCounts at hk
  cases hr : RecorderReveal.run (source ω) (commands ω) with
  | none => simp [hr] at hk
  | some s =>
    simp only [hr] at hk
    split at hk
    · have hav := ObservationPolicy.availableCount_value (n j)
        (CalibrationLog.samples (key j) s.recorder.log) k hk
      apply Fin.ext
      change k.val = (stream j ω).card
      rw [hav.2, RecorderReveal.run_samples_eq_take (source ω) (commands ω) hr,
        List.take_take, Nat.min_eq_left hav.1, ← hprefix, sampleList_count_true]
    · simp at hk

open Komorebi.AVOC.Affine Affine.QuoteAuthority Affine.RobustQuote
  Affine.CalibrationBridge Affine.CalibratedPolicy

/-- Plan issuance reads the recorder's actual terminal log through its gates. -/
def recorderPlan {r c : Nat} (md : QModel r c) (n m : J → Nat) (alpha : J → ℚ)
    (key : J → K) (source : Ω → K → List Bool)
    (commands : Ω → List (RecorderReveal.Command K))
    (selectWarm selectCold : Ω → J) (ω : Ω) : Option (QModel r c) :=
  Affine.ObservedCalibration.observedPlan md n m alpha
    (gatedCounts n key source commands) selectWarm selectCold ω

theorem rejected_run_no_plan {r c : Nat} (md : QModel r c)
    (n m : J → Nat) (alpha : J → ℚ) (key : J → K)
    (source : Ω → K → List Bool) (commands : Ω → List (RecorderReveal.Command K))
    (selectWarm selectCold : Ω → J) (ω : Ω)
    (h : RecorderReveal.run (source ω) (commands ω) = none) :
    recorderPlan md n m alpha key source commands selectWarm selectCold ω = none := by
  apply Affine.ObservedCalibration.observedPlan_none_warm
  exact rejected_run_no_count n key source commands ω h (selectWarm ω)

theorem pending_run_no_plan {r c : Nat} (md : QModel r c)
    (n m : J → Nat) (alpha : J → ℚ) (key : J → K)
    (source : Ω → K → List Bool) (commands : Ω → List (RecorderReveal.Command K))
    (selectWarm selectCold : Ω → J) (ω : Ω) (s : RecorderReveal.State K)
    (h : RecorderReveal.run (source ω) (commands ω) = some s)
    (hp : s.recorder.pending ≠ []) :
    recorderPlan md n m alpha key source commands selectWarm selectCold ω = none := by
  apply Affine.ObservedCalibration.observedPlan_none_warm
  exact pending_run_no_count n key source commands ω s h hp (selectWarm ω)

variable [Fintype Ω] [Fintype J]

/-- Full lifecycle-recording-to-policy theorem. All rejected, unfinished, and
insufficient-sample runs remain in the probability space and issue no plan.
The fixed latent sources retain their primitive conditional law; no law is
inferred from accepting the raw external log. -/
theorem recorder_episode_coverage {r c : Nat}
    (law : Law Ω) (md : QModel r c) (d : DeterministicRealization md)
    (N : K → Nat) (p : K → ℚ) (base : (k : K) → Ω → Sample (N k))
    (hlaw : ∀ k, ConditionalLaw law (N k) (p k) (base k))
    (n m : J → Nat) (alpha : J → ℚ) (key : J → K)
    (hn : ∀ j, n j ≤ N (key j))
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ k, 0 ≤ p k) (hp1 : ∀ k, p k ≤ 1)
    (commands : Ω → List (RecorderReveal.Command K))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (key (selectWarm ω)) = wp)
    (hcparam : ∀ ω, p (key (selectCold ω)) = cp) :
    1 - ∑ j, alpha j ≤ eventMass law (fun ω => ∀ planned,
      recorderPlan md n m alpha key (fun ω k => sampleList (base k ω)) commands
        selectWarm selectCold ω = some planned →
      EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross) := by
  let stream : (j : J) → Ω → Sample (n j) :=
    fun j ω => truncateSample (n j) (hn j) (base (key j) ω)
  have hc : ∀ j (k : Fin (n j + 1)),
      eventMass law (fun ω => streamCount (stream j) ω = k) =
        FiniteCalibration.mass (n j) k.val (p (key j)) := by
    intro j k
    exact prefix_count_fiber_eq_binomial law (N (key j)) (p (key j))
      (base (key j)) (hlaw (key j)) (n j) (hn j) k
  exact Affine.ObservedCalibration.observed_episode_coverage law md d n m alpha
    (fun j => p (key j)) hm ha (fun j => hp0 (key j)) (fun j => hp1 (key j))
    (fun j => streamCount (stream j)) hc
    (gatedCounts n key (fun ω k => sampleList (base k ω)) commands)
    (gatedCounts_faithful n key (fun ω k => sampleList (base k ω)) commands stream
      (fun j ω => sampleList_truncate (hn j) (base (key j) ω)))
    selectWarm selectCold wp cp hwparam hcparam

/-- Direct unconditional bad-issuance form, without conditioning on successful
execution, absence of pending operations, or sample completion. -/
theorem recorder_issued_failure_le {r c : Nat}
    (law : Law Ω) (md : QModel r c) (d : DeterministicRealization md)
    (N : K → Nat) (p : K → ℚ) (base : (k : K) → Ω → Sample (N k))
    (hlaw : ∀ k, ConditionalLaw law (N k) (p k) (base k))
    (n m : J → Nat) (alpha : J → ℚ) (key : J → K)
    (hn : ∀ j, n j ≤ N (key j))
    (hm : ∀ j, 0 < m j) (ha : ∀ j, 0 ≤ alpha j)
    (hp0 : ∀ k, 0 ≤ p k) (hp1 : ∀ k, p k ≤ 1)
    (commands : Ω → List (RecorderReveal.Command K))
    (selectWarm selectCold : Ω → J) (wp cp : ℚ)
    (hwparam : ∀ ω, p (key (selectWarm ω)) = wp)
    (hcparam : ∀ ω, p (key (selectCold ω)) = cp) :
    eventMass law (fun ω => ∃ planned,
      recorderPlan md n m alpha key (fun ω k => sampleList (base k ω)) commands
        selectWarm selectCold ω = some planned ∧
      ¬ EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross) ≤
      ∑ j, alpha j := by
  have hg := recorder_episode_coverage law md d N p base hlaw n m alpha key hn hm ha
    hp0 hp1 commands selectWarm selectCold wp cp hwparam hcparam
  have hc := eventMass_add_compl law (fun ω => ∃ planned,
      recorderPlan md n m alpha key (fun ω k => sampleList (base k ω)) commands
        selectWarm selectCold ω = some planned ∧
      ¬ EpisodeCertified planned wp cp d.warmSetup d.coldSetup d.warmGross d.coldGross)
  simp only [not_exists, not_and, not_not] at hc
  linarith

end Komorebi.AVOC.RecorderPolicy
