import AVOC.QuoteAuthority
import AVOC.GuardedModelError
import AVOC.ApproximateStochastic
import AVOC.ExecutablePlanner
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC.Affine.RobustQuote

open Komorebi.AVOC
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.Staged (Status Action)
open Komorebi.AVOC.Affine.LazyStaged
open Komorebi.AVOC.Affine.QuoteAuthority

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

variable {n m : Nat}

abbrev QModel := QuoteAuthority.Model
abbrev State (md : QModel n m) := PlanState (nominal md)

/-- A concrete exact realization uses the same conservative action guard and
budget reservation as the nominal model, but receives its realized reward and
observation law. -/
def trueProbability (md : QModel n m) (r : Realization md)
    (_s : State md) (a : Action) (o : Bool) : ℚ :=
  match a with
  | .inspectWarm => if o then r.warm.probability else 1-r.warm.probability
  | .generateCold => if o then r.cold.probability else 1-r.cold.probability
  | _ => if o then 0 else 1

theorem trueProbability_nonneg (md : QModel n m) (r : Realization md)
    (s : State md) (a : Action) (o : Bool) :
    0 ≤ trueProbability md r s a o := by
  have hw := ProbabilityBand.contains_bounds r.warm.probability_mem
  have hc := ProbabilityBand.contains_bounds r.cold.probability_mem
  cases a <;> cases o <;>
    simp [trueProbability,hw.1,hw.2,hc.1,hc.2]

theorem trueProbability_sum_one (md : QModel n m) (r : Realization md)
    (s : State md) (a : Action) :
    ∑ o : Bool, trueProbability md r s a o = 1 := by
  cases a <;> simp [trueProbability]

def trueReward (md : QModel n m) (r : Realization md)
    (_s : State md) : Action → ℚ
  | .stop => 0
  | .inspectWarm => -(r.warm.setup : ℚ)
  | .generateCold => -(r.cold.setup : ℚ)
  | .deployWarm => r.warm.gross
  | .deployCold => r.cold.gross

def trueSystem (md : QModel n m) (r : Realization md) :
    Guarded.System (State md) Action Bool where
  actions := LazyStaged.actions (nominal md)
  actions_nonempty := fun s => ⟨.stop, LazyStaged.stop_mem_actions (nominal md) s⟩
  prob := trueProbability md r
  prob_nonneg := trueProbability_nonneg md r
  prob_sum_one := trueProbability_sum_one md r
  step := LazyStaged.step (nominal md)
  reward := trueReward md r

/-- Action-specific primitive reward uncertainty. -/
def rewardRadius (md : QModel n m) : Action → ℚ
  | .stop => 0
  | .inspectWarm => (setupBand md .warm).width
  | .generateCold => (setupBand md .cold).width
  | .deployWarm => (grossBand md .warm).width
  | .deployCold => (grossBand md .cold).width

/-- L1 uncertainty of the Boolean observation row. -/
def probabilityRadius (md : QModel n m) : Action → ℚ
  | .inspectWarm => 2 * (probBand md .warm).width
  | .generateCold => 2 * (probBand md .cold).width
  | _ => 0

def rewardError (md : QModel n m) : ℚ :=
  (setupBand md .warm).width + (setupBand md .cold).width +
  (grossBand md .warm).width + (grossBand md .cold).width

def probabilityError (md : QModel n m) : ℚ :=
  2 * ((probBand md .warm).width + (probBand md .cold).width)

/-- A deliberately simple uniform envelope for every nominal one-step reward. -/
def rewardEnvelope (md : QModel n m) : ℚ :=
  (setupBand md .warm).upper + (setupBand md .cold).upper +
  (grossBand md .warm).upper + (grossBand md .cold).upper

@[simp] theorem rewardError_nonneg (md : QModel n m) : 0 ≤ rewardError md := by
  unfold rewardError
  have h1 := NatBand.width_nonneg (setupBand md .warm)
  have h2 := NatBand.width_nonneg (setupBand md .cold)
  have h3 := RatBand.width_nonneg (grossBand md .warm)
  have h4 := RatBand.width_nonneg (grossBand md .cold)
  linarith

@[simp] theorem probabilityError_nonneg (md : QModel n m) : 0 ≤ probabilityError md := by
  unfold probabilityError
  have h1 := ProbabilityBand.width_nonneg (probBand md .warm)
  have h2 := ProbabilityBand.width_nonneg (probBand md .cold)
  linarith

@[simp] theorem rewardEnvelope_nonneg (md : QModel n m) : 0 ≤ rewardEnvelope md := by
  have hw : 0 ≤ (grossBand md .warm).upper :=
    (show 0 ≤ (grossBand md .warm).lower from md.warm.gross_nonneg).trans
      (grossBand md .warm).ordered
  have hc : 0 ≤ (grossBand md .cold).upper :=
    (show 0 ≤ (grossBand md .cold).lower from md.cold.gross_nonneg).trans
      (grossBand md .cold).ordered
  unfold rewardEnvelope
  positivity

@[simp] theorem rewardRadius_nonneg (md : QModel n m) (a : Action) :
    0 ≤ rewardRadius md a := by
  cases a <;> simp [rewardRadius]

@[simp] theorem probabilityRadius_nonneg (md : QModel n m) (a : Action) :
    0 ≤ probabilityRadius md a := by
  cases a <;> simp [probabilityRadius]

theorem rewardRadius_le (md : QModel n m) (a : Action) :
    rewardRadius md a ≤ rewardError md := by
  have hsw := NatBand.width_nonneg (setupBand md .warm)
  have hsc := NatBand.width_nonneg (setupBand md .cold)
  have hgw := RatBand.width_nonneg (grossBand md .warm)
  have hgc := RatBand.width_nonneg (grossBand md .cold)
  cases a <;> simp [rewardRadius,rewardError] <;> linarith

theorem probabilityRadius_le (md : QModel n m) (a : Action) :
    probabilityRadius md a ≤ probabilityError md := by
  have hw := ProbabilityBand.width_nonneg (probBand md .warm)
  have hc := ProbabilityBand.width_nonneg (probBand md .cold)
  cases a <;> simp [probabilityRadius,probabilityError] <;> linarith

theorem reward_close (md : QModel n m) (r : Realization md)
    (s : State md) (a : Action) :
    |trueReward md r s a - LazyStaged.reward (nominal md) s a| ≤ rewardRadius md a := by
  cases a with
  | stop => simp [trueReward,rewardRadius,LazyStaged.reward]
  | inspectWarm =>
      have h := NatBand.contains_upper_sub r.warm.setup_mem
      have h' : |((setupBand md .warm).upper : ℚ) - (r.warm.setup : ℚ)| ≤
          (setupBand md .warm).width := by
        simpa [abs_sub_comm] using h
      simpa [trueReward, LazyStaged.reward, nominal, nominalQuote,
        LazyStaged.warmFee, setupBand, rawQuote, rewardRadius,
        sub_eq_add_neg, add_comm] using h'
  | generateCold =>
      have h := NatBand.contains_upper_sub r.cold.setup_mem
      have h' : |((setupBand md .cold).upper : ℚ) - (r.cold.setup : ℚ)| ≤
          (setupBand md .cold).width := by
        simpa [abs_sub_comm] using h
      simpa [trueReward, LazyStaged.reward, nominal, nominalQuote,
        LazyStaged.coldFee, setupBand, rawQuote, rewardRadius,
        sub_eq_add_neg, add_comm] using h'
  | deployWarm =>
      change |r.warm.gross - (grossBand md .warm).lower| ≤ (grossBand md .warm).width
      exact RatBand.contains_lower_sub r.warm.gross_mem
  | deployCold =>
      change |r.cold.gross - (grossBand md .cold).lower| ≤ (grossBand md .cold).width
      exact RatBand.contains_lower_sub r.cold.gross_mem

theorem bernoulli_l1 (p q : ℚ) (hqp : q ≤ p) :
    (∑ o : Bool, |(if o then p else 1-p) - (if o then q else 1-q)|) = 2*(p-q) := by
  rw [Fintype.sum_bool]
  simp only [Bool.false_eq_true, ite_false, ite_true]
  rw [abs_of_nonneg (sub_nonneg.mpr hqp)]
  have hn : (1-p) - (1-q) ≤ 0 := by linarith
  rw [abs_of_nonpos hn]
  ring

theorem probability_l1_le (md : QModel n m) (r : Realization md)
    (s : State md) (a : Action) :
    l1RowDistance (trueProbability md r s a)
      (LazyStaged.probability (nominal md) s a) ≤ probabilityRadius md a := by
  cases a with
  | stop => simp [l1RowDistance,trueProbability,LazyStaged.probability,probabilityRadius]
  | deployWarm => simp [l1RowDistance,trueProbability,LazyStaged.probability,probabilityRadius]
  | deployCold => simp [l1RowDistance,trueProbability,LazyStaged.probability,probabilityRadius]
  | inspectWarm =>
      have hm := r.warm.probability_mem
      have he := bernoulli_l1 r.warm.probability (probBand md .warm).lower hm.1
      rw [l1RowDistance, show (∑ o : Bool,
        |trueProbability md r s .inspectWarm o -
          LazyStaged.probability (nominal md) s .inspectWarm o|) =
        2*(r.warm.probability-(probBand md .warm).lower) by
          simpa [trueProbability,LazyStaged.probability,nominal,nominalQuote,probBand,rawQuote] using he]
      unfold probabilityRadius ProbabilityBand.width
      linarith [hm.2]
  | generateCold =>
      have hm := r.cold.probability_mem
      have he := bernoulli_l1 r.cold.probability (probBand md .cold).lower hm.1
      rw [l1RowDistance, show (∑ o : Bool,
        |trueProbability md r s .generateCold o -
          LazyStaged.probability (nominal md) s .generateCold o|) =
        2*(r.cold.probability-(probBand md .cold).lower) by
          simpa [trueProbability,LazyStaged.probability,nominal,nominalQuote,probBand,rawQuote] using he]
      unfold probabilityRadius ProbabilityBand.width
      linarith [hm.2]

theorem expectation_transport (md : QModel n m) (r : Realization md)
    (W : State md → ℚ) (B : ℚ) (hB : 0 ≤ B)
    (hW : ∀ t, |W t| ≤ B) (s : State md) (a : Action) :
    |Guarded.expectation (trueSystem md r) W s a -
      Guarded.expectation (LazyStaged.system (nominal md)) W s a| ≤
      probabilityRadius md a * B := by
  unfold Guarded.expectation
  exact (weighted_sum_difference_le_l1
    (trueProbability md r s a)
    (LazyStaged.probability (nominal md) s a) (fun o => W (LazyStaged.step (nominal md) s a o))
    B (fun o => hW _)).trans
      (mul_le_mul_of_nonneg_right (probability_l1_le md r s a) hB)

theorem nominal_reward_abs_le (md : QModel n m) (s : State md) (a : Action) :
    |LazyStaged.reward (nominal md) s a| ≤ rewardEnvelope md := by
  have hgw : 0 ≤ (grossBand md .warm).lower := md.warm.gross_nonneg
  have hgc : 0 ≤ (grossBand md .cold).lower := md.cold.gross_nonneg
  have huw : (grossBand md .warm).lower ≤ (grossBand md .warm).upper :=
    (grossBand md .warm).ordered
  have huc : (grossBand md .cold).lower ≤ (grossBand md .cold).upper :=
    (grossBand md .cold).ordered
  have hwU : 0 ≤ (grossBand md .warm).upper := hgw.trans huw
  have hcU : 0 ≤ (grossBand md .cold).upper := hgc.trans huc
  cases a with
  | stop =>
      change 0 ≤ rewardEnvelope md
      exact rewardEnvelope_nonneg md
  | inspectWarm =>
      change |-((setupBand md .warm).upper : ℚ)| ≤ rewardEnvelope md
      rw [abs_neg, abs_of_nonneg (Nat.cast_nonneg _)]
      unfold rewardEnvelope
      have hsc : 0 ≤ ((setupBand md .cold).upper : ℚ) := Nat.cast_nonneg _
      linarith
  | generateCold =>
      change |-((setupBand md .cold).upper : ℚ)| ≤ rewardEnvelope md
      rw [abs_neg, abs_of_nonneg (Nat.cast_nonneg _)]
      unfold rewardEnvelope
      have hsw : 0 ≤ ((setupBand md .warm).upper : ℚ) := Nat.cast_nonneg _
      linarith
  | deployWarm =>
      change |(grossBand md .warm).lower| ≤ rewardEnvelope md
      rw [abs_of_nonneg hgw]
      unfold rewardEnvelope
      linarith
  | deployCold =>
      change |(grossBand md .cold).lower| ≤ rewardEnvelope md
      rw [abs_of_nonneg hgc]
      unfold rewardEnvelope
      linarith

theorem nominal_value_abs_le (md : QModel n m) :
    ∀ h s, |Guarded.value (LazyStaged.system (nominal md)) h s| ≤
      (h : ℚ) * rewardEnvelope md := by
  intro h
  induction h with
  | zero => intro s; simp
  | succ h ih =>
      intro s
      let sys := LazyStaged.system (nominal md)
      obtain ⟨a,ha,hm⟩ := Guarded.optimal_action_exists sys h s
      rw [Guarded.value_eq_q_of_optimal sys h s a ha hm]
      have hr := nominal_reward_abs_le md s a
      have he := Guarded.expectation_uniform_error sys (Guarded.value sys h) (fun _ => 0)
        ((h : ℚ) * rewardEnvelope md) (fun t => by simpa using ih t) s a
      have he' : |Guarded.expectation sys (Guarded.value sys h) s a| ≤
          (h : ℚ) * rewardEnvelope md := by
        simpa [Guarded.expectation_const] using he
      unfold Guarded.qValue
      calc
        |sys.reward s a + Guarded.expectation sys (Guarded.value sys h) s a|
            ≤ |sys.reward s a| + |Guarded.expectation sys (Guarded.value sys h) s a| :=
              abs_add_le _ _
        _ ≤ rewardEnvelope md + (h : ℚ) * rewardEnvelope md := add_le_add hr he'
        _ = ((h+1 : Nat) : ℚ) * rewardEnvelope md := by push_cast; ring

def transportBudget (md : QModel n m) (h : Nat) : ℚ :=
  probabilityError md * ((h : ℚ) * rewardEnvelope md)

def residualBudget (_md : QModel n m) (_h : Nat) : ℚ := 0

def valueRadius (md : QModel n m) (h : Nat) : ℚ :=
  Guarded.modelValueBudget (rewardError md) (transportBudget md) (residualBudget md) h

def globalQRadius (md : QModel n m) (h : Nat) : ℚ :=
  Guarded.modelQBudget (rewardError md) (transportBudget md) (residualBudget md) h

def localQRadius (md : QModel n m) (h : Nat) (a : Action) : ℚ :=
  valueRadius md h + rewardRadius md a +
    probabilityRadius md a * ((h : ℚ) * rewardEnvelope md)

@[simp] theorem valueRadius_nonneg (md : QModel n m) (h : Nat) : 0 ≤ valueRadius md h := by
  unfold valueRadius Guarded.modelValueBudget transportBudget residualBudget
  apply Finset.sum_nonneg
  intro k hk
  have he := rewardError_nonneg md
  have hp := probabilityError_nonneg md
  have hr := rewardEnvelope_nonneg md
  positivity

@[simp] theorem localQRadius_nonneg (md : QModel n m) (h : Nat) (a : Action) :
    0 ≤ localQRadius md h a := by
  unfold localQRadius
  have hv := valueRadius_nonneg md h
  have hr := rewardRadius_nonneg md a
  have hp := probabilityRadius_nonneg md a
  have he := rewardEnvelope_nonneg md
  positivity

theorem localQRadius_le_global (md : QModel n m) (h : Nat) (a : Action) :
    localQRadius md h a ≤ globalQRadius md h := by
  have hr := rewardRadius_le md a
  have hp := probabilityRadius_le md a
  have hB : 0 ≤ (h : ℚ) * rewardEnvelope md :=
    mul_nonneg (Nat.cast_nonneg h) (rewardEnvelope_nonneg md)
  have hm := mul_le_mul_of_nonneg_right hp hB
  unfold localQRadius globalQRadius Guarded.modelQBudget transportBudget
  change valueRadius md h + rewardRadius md a +
      probabilityRadius md a * ((h : ℚ) * rewardEnvelope md) ≤
    Guarded.modelValueBudget (rewardError md) (transportBudget md) (residualBudget md) h +
      rewardError md + probabilityError md * ((h : ℚ) * rewardEnvelope md)
  change Guarded.modelValueBudget (rewardError md) (transportBudget md) (residualBudget md) h +
      rewardRadius md a + probabilityRadius md a * ((h : ℚ) * rewardEnvelope md) ≤
    Guarded.modelValueBudget (rewardError md) (transportBudget md) (residualBudget md) h +
      rewardError md + probabilityError md * ((h : ℚ) * rewardEnvelope md)
  linarith

theorem nominal_certificate (md : QModel n m) (r : Realization md) :
    Guarded.ModelCertificate (trueSystem md r) (LazyStaged.system (nominal md)) id
      (fun h s => Guarded.value (LazyStaged.system (nominal md)) h s)
      (rewardError md) (transportBudget md) (residualBudget md) := by
  refine {
    actions_eq := fun s => rfl
    initial := fun s => rfl
    reward_error := ?_
    transport_error := ?_
    residual_error := ?_ }
  · intro s a ha
    exact (reward_close md r s a).trans (rewardRadius_le md a)
  · intro h s a ha
    have ht := expectation_transport md r
      (Guarded.value (LazyStaged.system (nominal md)) h)
      ((h : ℚ) * rewardEnvelope md)
      (mul_nonneg (Nat.cast_nonneg h) (rewardEnvelope_nonneg md))
      (nominal_value_abs_le md h) s a
    exact ht.trans (mul_le_mul_of_nonneg_right (probabilityRadius_le md a)
      (mul_nonneg (Nat.cast_nonneg h) (rewardEnvelope_nonneg md)))
  · intro h s
    rw [Guarded.backup_optimal_value]
    simp [residualBudget]

theorem value_error (md : QModel n m) (r : Realization md) (h : Nat) (s : State md) :
    |Guarded.value (trueSystem md r) h s -
      Guarded.value (LazyStaged.system (nominal md)) h s| ≤ valueRadius md h := by
  simpa [valueRadius] using Guarded.model_value_error
    (trueSystem md r) (LazyStaged.system (nominal md)) id
    (fun h s => Guarded.value (LazyStaged.system (nominal md)) h s)
    (rewardError md) (transportBudget md) (residualBudget md)
    (nominal_certificate md r) h s

theorem local_q_error (md : QModel n m) (r : Realization md)
    (h : Nat) (s : State md) (a : Action) :
    |Guarded.qValue (trueSystem md r) h s a -
      Guarded.qValue (LazyStaged.system (nominal md)) h s a| ≤ localQRadius md h a := by
  have hv := Guarded.expectation_uniform_error (trueSystem md r)
    (Guarded.value (trueSystem md r) h)
    (Guarded.value (LazyStaged.system (nominal md)) h)
    (valueRadius md h) (value_error md r h) s a
  have ht := expectation_transport md r
    (Guarded.value (LazyStaged.system (nominal md)) h)
    ((h : ℚ) * rewardEnvelope md)
    (mul_nonneg (Nat.cast_nonneg h) (rewardEnvelope_nonneg md))
    (nominal_value_abs_le md h) s a
  have hr := reward_close md r s a
  have he : |Guarded.expectation (trueSystem md r)
      (Guarded.value (trueSystem md r) h) s a -
      Guarded.expectation (LazyStaged.system (nominal md))
        (Guarded.value (LazyStaged.system (nominal md)) h) s a| ≤
      valueRadius md h + probabilityRadius md a * ((h : ℚ) * rewardEnvelope md) := by
    have hh := abs_sub_le
      (Guarded.expectation (trueSystem md r) (Guarded.value (trueSystem md r) h) s a)
      (Guarded.expectation (trueSystem md r)
        (Guarded.value (LazyStaged.system (nominal md)) h) s a)
      (Guarded.expectation (LazyStaged.system (nominal md))
        (Guarded.value (LazyStaged.system (nominal md)) h) s a)
    linarith
  change |trueReward md r s a +
      Guarded.expectation (trueSystem md r) (Guarded.value (trueSystem md r) h) s a -
      (LazyStaged.reward (nominal md) s a +
        Guarded.expectation (LazyStaged.system (nominal md))
          (Guarded.value (LazyStaged.system (nominal md)) h) s a)| ≤ localQRadius md h a
  unfold localQRadius
  have hh := abs_add_le
    (trueReward md r s a - LazyStaged.reward (nominal md) s a)
    (Guarded.expectation (trueSystem md r) (Guarded.value (trueSystem md r) h) s a -
      Guarded.expectation (LazyStaged.system (nominal md))
        (Guarded.value (LazyStaged.system (nominal md)) h) s a)
  have hid :
      (trueReward md r s a +
        Guarded.expectation (trueSystem md r) (Guarded.value (trueSystem md r) h) s a) -
      (LazyStaged.reward (nominal md) s a +
        Guarded.expectation (LazyStaged.system (nominal md))
          (Guarded.value (LazyStaged.system (nominal md)) h) s a) =
      (trueReward md r s a - LazyStaged.reward (nominal md) s a) +
      (Guarded.expectation (trueSystem md r) (Guarded.value (trueSystem md r) h) s a -
        Guarded.expectation (LazyStaged.system (nominal md))
          (Guarded.value (LazyStaged.system (nominal md)) h) s a) := by ring
  rw [hid]
  linarith

noncomputable def lowerValue (md : QModel n m) (h : Nat) (s : State md) : ℚ :=
  Guarded.value (LazyStaged.system (nominal md)) h s - valueRadius md h

noncomputable def upperValue (md : QModel n m) (h : Nat) (s : State md) : ℚ :=
  Guarded.value (LazyStaged.system (nominal md)) h s + valueRadius md h

noncomputable def lowerQ (md : QModel n m) (h : Nat) (s : State md) (a : Action) : ℚ :=
  Guarded.qValue (LazyStaged.system (nominal md)) h s a - localQRadius md h a

noncomputable def upperQ (md : QModel n m) (h : Nat) (s : State md) (a : Action) : ℚ :=
  Guarded.qValue (LazyStaged.system (nominal md)) h s a + localQRadius md h a

theorem value_between (md : QModel n m) (r : Realization md) (h : Nat) (s : State md) :
    lowerValue md h s ≤ Guarded.value (trueSystem md r) h s ∧
      Guarded.value (trueSystem md r) h s ≤ upperValue md h s := by
  have h := abs_le.mp (value_error md r h s)
  unfold lowerValue upperValue
  constructor <;> linarith

theorem q_between (md : QModel n m) (r : Realization md) (h : Nat)
    (s : State md) (a : Action) :
    lowerQ md h s a ≤ Guarded.qValue (trueSystem md r) h s a ∧
      Guarded.qValue (trueSystem md r) h s a ≤ upperQ md h s a := by
  have hq := abs_le.mp (local_q_error md r h s a)
  unfold lowerQ upperQ
  constructor <;> linarith

/-- Preserve the inherited executable work field while replacing only the score. -/
def robustCandidate (md : QModel n m) (h : Nat) (s : State md) (a : Action) :
    ExecutablePlanner.Candidate Action :=
  let c := ExecutablePlanner.actionEval (LazyStaged.executable (nominal md))
    (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) h) s a
  { c with score := c.score - localQRadius md h a }

def robustRows (md : QModel n m) (h : Nat) (s : State md) :
    List (ExecutablePlanner.Candidate Action) :=
  (LazyStaged.actionList (nominal md) s).map (robustCandidate md h s)

def robustChoice (md : QModel n m) (h : Nat) (s : State md) : Action :=
  ((ExecutablePlanner.best (robustRows md h s)).map
    ExecutablePlanner.Candidate.action).getD .stop

@[simp] theorem robustCandidate_action (md : QModel n m) (h : Nat) (s : State md) (a : Action) :
    (robustCandidate md h s a).action = a := by
  simp [robustCandidate]

theorem robustCandidate_score (md : QModel n m) (h : Nat) (s : State md) (a : Action) :
    (robustCandidate md h s a).score = lowerQ md h s a := by
  change (ExecutablePlanner.actionEval (LazyStaged.executable (nominal md))
    (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) h) s a).score -
      localQRadius md h a = lowerQ md h s a
  rw [ExecutablePlanner.actionEval_exact
    (LazyStaged.executable (nominal md)) (LazyStaged.system (nominal md))
    (LazyStaged.executable_realizes (nominal md)) _ h
    (LazyStaged.evaluated_value_exact (nominal md) h) s a]
  rfl

theorem robust_best_exists (md : QModel n m) (h : Nat) (s : State md) :
    ∃ c, ExecutablePlanner.best (robustRows md h s) = some c ∧
      c ∈ robustRows md h s ∧ ∀ d ∈ robustRows md h s, d.score ≤ c.score := by
  apply ExecutablePlanner.best_spec
  intro he
  have hs := LazyStaged.stop_mem_actions (nominal md) s
  have hl : Action.stop ∈ LazyStaged.actionList (nominal md) s :=
    (LazyStaged.mem_actionList (nominal md) s .stop).2 hs
  have hm : robustCandidate md h s .stop ∈ robustRows md h s :=
    List.mem_map.mpr ⟨.stop,hl,rfl⟩
  rw [he] at hm
  simp at hm

theorem robustChoice_allowed (md : QModel n m) (h : Nat) (s : State md) :
    robustChoice md h s ∈ LazyStaged.actions (nominal md) s := by
  obtain ⟨c,hc,hcm,hmax⟩ := robust_best_exists md h s
  obtain ⟨a,ha,hca⟩ := List.mem_map.mp hcm
  subst c
  have hchoice : robustChoice md h s = a := by simp [robustChoice,hc]
  rw [hchoice]
  exact (LazyStaged.mem_actionList (nominal md) s a).1 ha

theorem robustChoice_lower_max (md : QModel n m) (h : Nat) (s : State md) :
    ∀ a ∈ LazyStaged.actions (nominal md) s,
      lowerQ md h s a ≤ lowerQ md h s (robustChoice md h s) := by
  obtain ⟨c,hc,hcm,hmax⟩ := robust_best_exists md h s
  obtain ⟨a,ha,hca⟩ := List.mem_map.mp hcm
  subst c
  have hchoice : robustChoice md h s = a := by simp [robustChoice,hc]
  intro b hb
  have hbl : b ∈ LazyStaged.actionList (nominal md) s :=
    (LazyStaged.mem_actionList (nominal md) s b).2 hb
  have hh := hmax (robustCandidate md h s b) (List.mem_map.mpr ⟨b,hbl,rfl⟩)
  rw [robustCandidate_score,robustCandidate_score] at hh
  simpa [hchoice] using hh

theorem certified_dominance (md : QModel n m) (h : Nat) (s : State md)
    (a : Action) (_ha : a ∈ LazyStaged.actions (nominal md) s)
    (hd : ∀ b ∈ LazyStaged.actions (nominal md) s, upperQ md h s b ≤ lowerQ md h s a)
    (r : Realization md) :
    ∀ b ∈ (trueSystem md r).actions s,
      Guarded.qValue (trueSystem md r) h s b ≤ Guarded.qValue (trueSystem md r) h s a := by
  intro b hb
  have qb := q_between md r h s b
  have qa := q_between md r h s a
  exact qb.2.trans ((hd b hb).trans qa.1)

theorem robust_action_gap (md : QModel n m) (r : Realization md)
    (h : Nat) (s : State md) :
    Guarded.value (trueSystem md r) (h+1) s -
      Guarded.qValue (trueSystem md r) h s (robustChoice md h s) ≤
      2 * globalQRadius md h := by
  let a := Guarded.optimalAction (trueSystem md r) h s
  have ha0 := Guarded.optimalAction_mem (trueSystem md r) h s
  have ha : a ∈ LazyStaged.actions (nominal md) s := by
    dsimp [a] at ha0 ⊢
    exact ha0
  have hm := robustChoice_lower_max md h s a ha
  have qa := q_between md r h s a
  have qc := q_between md r h s (robustChoice md h s)
  have hra := localQRadius_le_global md h a
  have hrc := localQRadius_le_global md h (robustChoice md h s)
  rw [Guarded.optimalAction_realizes]
  unfold lowerQ upperQ at *
  linarith

/-- Complete adaptive policy induced by robust lower-Q maximization. -/
def robustPolicy (md : QModel n m) : Nat → State md → Action :=
  fun h s => robustChoice md h s

theorem robustPolicy_allowed (md : QModel n m) :
    ∀ h s, robustPolicy md h s ∈ LazyStaged.actions (nominal md) s :=
  fun h s => robustChoice_allowed md h s

theorem robust_policy_nearGreedy (md : QModel n m) (r : Realization md) :
    ∀ h s, Guarded.NearGreedy (trueSystem md r)
      (fun k => 2 * globalQRadius md k) s
      (Guarded.policyPlan (trueSystem md r) (robustPolicy md) h s) := by
  intro h
  induction h with
  | zero => intro s; trivial
  | succ h ih =>
      intro s
      exact ⟨robust_action_gap md r h s, fun o => ih _⟩

theorem robust_policy_regret (md : QModel n m) (r : Realization md)
    (h : Nat) (s : State md) :
    0 ≤ Guarded.value (trueSystem md r) h s -
      Guarded.planValue (trueSystem md r) s
        (Guarded.policyPlan (trueSystem md r) (robustPolicy md) h s) ∧
    Guarded.value (trueSystem md r) h s -
      Guarded.planValue (trueSystem md r) s
        (Guarded.policyPlan (trueSystem md r) (robustPolicy md) h s) ≤
      Guarded.regretBudget (fun k => 2 * globalQRadius md k) h := by
  constructor
  · apply sub_nonneg.mpr
    exact Guarded.planValue_le_value (trueSystem md r) s _
      (Guarded.policyPlan_legal (trueSystem md r) (robustPolicy md)
        (fun k t => robustChoice_allowed md k t) h s)
  · exact Guarded.plan_regret_le (trueSystem md r)
      (fun k => 2 * globalQRadius md k) s _
      (robust_policy_nearGreedy md r h s)

/-- All intervals are exact singleton evidence. -/
def ExactBands (md : QModel n m) : Prop :=
  (setupBand md .warm).width = 0 ∧
  (setupBand md .cold).width = 0 ∧
  (grossBand md .warm).width = 0 ∧
  (grossBand md .cold).width = 0 ∧
  (probBand md .warm).width = 0 ∧
  (probBand md .cold).width = 0

theorem exact_rewardError (md : QModel n m) (h : ExactBands md) : rewardError md = 0 := by
  rcases h with ⟨h1,h2,h3,h4,h5,h6⟩
  simp [rewardError,h1,h2,h3,h4]

theorem exact_probabilityError (md : QModel n m) (h : ExactBands md) :
    probabilityError md = 0 := by
  rcases h with ⟨h1,h2,h3,h4,h5,h6⟩
  simp [probabilityError,h5,h6]

theorem exact_valueRadius (md : QModel n m) (h : ExactBands md) (k : Nat) :
    valueRadius md k = 0 := by
  have hr := exact_rewardError md h
  have hp := exact_probabilityError md h
  simp [valueRadius,Guarded.modelValueBudget,transportBudget,residualBudget,hr,hp]

theorem exact_localQRadius (md : QModel n m) (h : ExactBands md)
    (k : Nat) (a : Action) : localQRadius md k a = 0 := by
  rcases h with ⟨h1,h2,h3,h4,h5,h6⟩
  cases a <;>
    simp [localQRadius,exact_valueRadius md ⟨h1,h2,h3,h4,h5,h6⟩,
      rewardRadius,probabilityRadius,h1,h2,h3,h4,h5,h6]

theorem robustCandidate_exact (md : QModel n m) (hex : ExactBands md)
    (h : Nat) (s : State md) (a : Action) :
    robustCandidate md h s a =
      ExecutablePlanner.actionEval (LazyStaged.executable (nominal md))
        (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) h) s a := by
  unfold robustCandidate
  generalize hc : ExecutablePlanner.actionEval (LazyStaged.executable (nominal md))
      (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) h) s a = c
  cases c
  simp [exact_localQRadius md hex h a]

theorem robustChoice_exact (md : QModel n m) (hex : ExactBands md)
    (h : Nat) (s : State md) :
    robustChoice md h s =
      (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) (h+1) s).choice.getD .stop := by
  unfold robustChoice robustRows
  have hrows : (LazyStaged.actionList (nominal md) s).map (robustCandidate md h s) =
      (LazyStaged.actionList (nominal md) s).map
        (ExecutablePlanner.actionEval (LazyStaged.executable (nominal md))
          (ExecutablePlanner.evaluate (LazyStaged.executable (nominal md)) h) s) := by
    induction (LazyStaged.actionList (nominal md) s) with
    | nil => rfl
    | cons a xs ih =>
        simp only [List.map_cons]
        rw [robustCandidate_exact md hex h s a, ih]
  rw [hrows]
  rfl

theorem robustChoice_recovers_v037 (md : QModel n m) (hex : ExactBands md)
    (h : Nat) (s : LazyStaged.RuntimeState (nominal md)) :
    robustChoice md h s.plan = LazyStaged.recommend (nominal md) h s := by
  exact robustChoice_exact md hex h s.plan

end Komorebi.AVOC.Affine.RobustQuote
