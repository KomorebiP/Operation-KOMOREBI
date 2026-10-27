import MachineTheory.DecisionHistory
import MachineTheory.ApproximationExamples

/-!
Core4.1, checked boundaries and a single sensor record. The example is not a
physical observation or a new optimization theorem for the changed instrument.
It certifies one terminal decision after one positive report.
-/
namespace Komorebi.MachineTheory.ResponseExamples
open scoped BigOperators
open Instrument Variation ApproximateHistory ApproximateDecision ResponseDecision DecisionHistory
noncomputable section

/-- On the attained unit interval, either select zero or select one. -/
def scalarLoss (a : Bool) (y : ℝ) : ℝ := if a then 1-y else y

theorem scalarLoss_range (a : Bool) (y : ℝ) (hy : 0 ≤ y ∧ y ≤ 1) :
    0 ≤ scalarLoss a y ∧ scalarLoss a y ≤ 1 := by
  cases a <;> simp only [scalarLoss, Bool.false_eq_true, ite_false, ite_true]
  · exact hy
  · constructor <;> linarith [hy.1,hy.2]

theorem scalarLoss_lipschitz (a : Bool) (y z : ℝ) :
    |scalarLoss a y-scalarLoss a z| ≤ 1*dist y z := by
  cases a <;> simp [scalarLoss, Real.dist_eq, abs_sub_comm]

abbrev Pair := PlanningSensor.Pair
abbrev Outcome := Bool × Pair

def trueEvidence : Outcome → ℝ :=
  push (reportMap PlanningSensor.project)
    (jointEvidence ApproximationExamples.calibrated37 () PlanningSensor.initialFine.val)

def modelEvidence : Outcome → ℝ :=
  jointEvidence PlanningSensor.sensorLaw () (push PlanningSensor.project PlanningSensor.initialFine.val)

def reportOne : Finset Outcome := Finset.univ.filter (fun x => x.1 = true)

def truePosterior : Pair → ℝ := recordAfter Prod.snd reportOne trueEvidence

def modelPosterior : Pair → ℝ := recordAfter Prod.snd reportOne modelEvidence

/-- A deliberately specified finite stored record: exact hundredths, not inferred calibration. -/
def storedRecord (z : Pair) : ℝ := if z.1=z.2 then (if z.1 then 19/25 else 6/25) else 0

def targetResponse (z : Pair) : ℝ := if z.1 then 1 else 0

def approximateResponse (z : Pair) : ℝ := if z.1 then 99/100 else 1/100

theorem trueEvidence_dist : IsDist trueEvidence :=
  push_dist _ _ (jointEvidence_dist _ _ _ PlanningSensor.initialFine.property)

theorem modelEvidence_dist : IsDist modelEvidence :=
  jointEvidence_dist _ _ _ (push_dist _ _ PlanningSensor.initialFine.property)

/-- This law bound is derived from the inherited 37/50-versus-3/4 joint-row theorem. -/
theorem sensor_evidence_bound : tv trueEvidence modelEvidence ≤ 1/100 := by
  have h := jointEvidence_error PlanningSensor.project ApproximationExamples.calibrated37
    PlanningSensor.sensorLaw () PlanningSensor.initialFine.val
    (push PlanningSensor.project PlanningSensor.initialFine.val) PlanningSensor.initialFine.property
    0 (1/100) (by rw [tv_self])
    (fun x => le_of_eq (ApproximationExamples.sensor_joint_row_error () x))
  simpa only [trueEvidence, modelEvidence, zero_add] using h

theorem trueEvidence_value (o b s : Bool) :
    trueEvidence (o,b,s) = if b=s then (if o=s then 37/100 else 13/100) else 0 := by
  cases o <;> cases b <;> cases s <;>
    norm_num [trueEvidence, jointEvidence, jointKernel, jointRow, push, applyKernel,
      ApproximationExamples.calibrated37, PlanningSensor.initialFine,
      PlanningSensor.project, reportMap, Fintype.sum_prod_type, Fintype.sum_bool, ite_and]

theorem modelEvidence_value (o b s : Bool) :
    modelEvidence (o,b,s) = if b=s then (if o=s then 3/8 else 1/8) else 0 := by
  cases o <;> cases b <;> cases s <;>
    norm_num [modelEvidence, jointEvidence, jointKernel, jointRow, push, applyKernel,
      PlanningSensor.sensorLaw, PlanningSensor.accuracy, PlanningSensor.initialFine,
      PlanningSensor.project, Fintype.sum_prod_type, Fintype.sum_bool, ite_and]

theorem sensor_report_masses : mass (restrict reportOne trueEvidence) = 1/2 ∧
    mass (restrict reportOne modelEvidence) = 1/2 := by
  norm_num [mass, restrict, reportOne, Fintype.sum_prod_type, Fintype.sum_bool,
    trueEvidence_value, modelEvidence_value]

theorem truePosterior_value (b s : Bool) :
    truePosterior (b,s) = if b=s then (if b then 37/50 else 13/50) else 0 := by
  cases b <;> cases s <;>
    norm_num [truePosterior, recordAfter, push, normalize, restrict, reportOne, mass,
      Fintype.sum_prod_type, Fintype.sum_bool, trueEvidence_value, ite_and]

theorem modelPosterior_value (b s : Bool) :
    modelPosterior (b,s) = if b=s then (if b then 3/4 else 1/4) else 0 := by
  cases b <;> cases s <;>
    norm_num [modelPosterior, recordAfter, push, normalize, restrict, reportOne, mass,
      Fintype.sum_prod_type, Fintype.sum_bool, modelEvidence_value, ite_and]

theorem truePosterior_dist : IsDist truePosterior :=
  recordAfter_dist Prod.snd reportOne trueEvidence trueEvidence_dist
    (by rw [sensor_report_masses.1]; norm_num)

theorem modelPosterior_dist : IsDist modelPosterior :=
  recordAfter_dist Prod.snd reportOne modelEvidence modelEvidence_dist
    (by rw [sensor_report_masses.2]; norm_num)

theorem storedRecord_dist : IsDist storedRecord := by
  constructor
  · rintro ⟨b,s⟩; cases b <;> cases s <;> norm_num [storedRecord]
  · norm_num [mass, storedRecord, Fintype.sum_prod_type, Fintype.sum_bool]

theorem stored_record_error : tv modelPosterior storedRecord = 1/100 := by
  norm_num [tv, l1, Fintype.sum_prod_type, Fintype.sum_bool, modelPosterior_value, storedRecord]

/-- The true-model discrepancy is not replaced by this sharper, after-the-fact arithmetic. -/
theorem actual_record_error : tv truePosterior storedRecord = 1/50 := by
  norm_num [tv, l1, Fintype.sum_prod_type, Fintype.sum_bool, truePosterior_value, storedRecord]

theorem response_error (z : Pair) : dist (targetResponse z) (approximateResponse z) = 1/100 := by
  rcases z with ⟨b,s⟩; cases b <;> norm_num [targetResponse, approximateResponse, Real.dist_eq]

theorem target_range (z : Pair) : 0 ≤ targetResponse z ∧ targetResponse z ≤ 1 := by
  rcases z with ⟨b,s⟩; cases b <;> norm_num [targetResponse]

theorem approximate_range (z : Pair) : 0 ≤ approximateResponse z ∧ approximateResponse z ≤ 1 := by
  rcases z with ⟨b,s⟩; cases b <;> norm_num [approximateResponse]

theorem composed_allowance :
    allowance (recordAllowance reportOne trueEvidence modelEvidence (1/100) (1/100)) 1 (1/100) = 1/25 := by
  unfold allowance recordAllowance
  rw [sensor_report_masses.1, sensor_report_masses.2]
  norm_num

/-- The certificate uses the full chain of proved allowances, not the exact observed error. -/
theorem sensor_decision_error (a : Bool) :
    |responseRisk truePosterior targetResponse scalarLoss a-
      responseRisk storedRecord approximateResponse scalarLoss a| ≤ 1/25 := by
  rw [← composed_allowance]
  exact conditioned_response_error Prod.snd reportOne trueEvidence modelEvidence storedRecord
    trueEvidence_dist modelEvidence_dist storedRecord_dist
    (by rw [sensor_report_masses.1]; norm_num) (by rw [sensor_report_masses.2]; norm_num)
    (1/100) (1/100) sensor_evidence_bound (le_of_eq stored_record_error)
    targetResponse approximateResponse scalarLoss a 1 (1/100) (by norm_num)
    (fun z => le_of_eq (response_error z)) (fun z => scalarLoss_lipschitz a _ _)
    (fun z => scalarLoss_range a _ (target_range z))
    (fun z => scalarLoss_range a _ (approximate_range z))

theorem sensor_risk_values :
    responseRisk truePosterior targetResponse scalarLoss true = 13/50 ∧
    responseRisk truePosterior targetResponse scalarLoss false = 37/50 ∧
    responseRisk storedRecord approximateResponse scalarLoss true = 613/2500 ∧
    responseRisk storedRecord approximateResponse scalarLoss false = 1887/2500 := by
  norm_num [responseRisk, risk, Fintype.sum_prod_type, Fintype.sum_bool,
    truePosterior_value, storedRecord, targetResponse, approximateResponse, scalarLoss]

theorem sensor_true_unique_from_certificate :
    ∀ a : Bool, a ≠ true → responseRisk truePosterior targetResponse scalarLoss true <
      responseRisk truePosterior targetResponse scalarLoss a := by
  have h := unique_minimizer_transfer truePosterior storedRecord targetResponse approximateResponse
    scalarLoss Finset.univ (1/25) true (Finset.mem_univ _) (fun a _ => sensor_decision_error a)
    (by intro a _ hne; cases a <;> simp_all [sensor_risk_values.2.2.1, sensor_risk_values.2.2.2]; norm_num)
  intro a hne
  exact h.1 a (Finset.mem_univ _) hne

theorem sensor_risk_upper_certificate :
    responseRisk truePosterior targetResponse scalarLoss true ≤ 713/2500 := by
  apply risk_threshold truePosterior storedRecord targetResponse approximateResponse scalarLoss true
    (1/25) (713/2500) (sensor_decision_error true)
  rw [sensor_risk_values.2.2.1]
  norm_num

theorem sensor_threshold_certificate :
    responseRisk truePosterior targetResponse scalarLoss true ≤ 3/10 :=
  sensor_risk_upper_certificate.trans (by norm_num)

theorem sensor_error_and_margin :
    |responseRisk truePosterior targetResponse scalarLoss true-
      responseRisk storedRecord approximateResponse scalarLoss true| = 37/2500 ∧
    responseRisk storedRecord approximateResponse scalarLoss true+2*(1/25) <
      responseRisk storedRecord approximateResponse scalarLoss false := by
  rw [sensor_risk_values.1, sensor_risk_values.2.2.1, sensor_risk_values.2.2.2]
  norm_num

/-- Exact probabilities alone do not justify an inaccurate response. -/
theorem response_term_is_necessary :
    tv (basis () : Unit → ℝ) (basis ()) = 0 ∧
    |responseRisk (basis () : Unit → ℝ) (fun _ => (0 : ℝ)) scalarLoss false-
      responseRisk (basis () : Unit → ℝ) (fun _ => (1/5 : ℝ)) scalarLoss false| = 1/5 := by
  norm_num [tv, l1, responseRisk, risk, basis, scalarLoss]

/-- Accurate responses do not compensate for an incorrect probability record. -/
theorem probability_term_is_necessary :
    tv (basis false : Bool → ℝ) (basis true) = 1 ∧
    |responseRisk (basis false) (fun b : Bool => if b then (1 : ℝ) else 0) scalarLoss false-
      responseRisk (basis true) (fun b : Bool => if b then (1 : ℝ) else 0) scalarLoss false| = 1 := by
  norm_num [tv, l1, responseRisk, risk, basis, scalarLoss, Fintype.sum_bool]

/-- At exactly twice the error, a unique approximate choice can become a true tie. -/
theorem gap_equality_is_not_uniqueness :
    responseRisk (basis () : Unit → ℝ) (fun _ => (2/5 : ℝ)) scalarLoss false+2*(1/10) =
      responseRisk (basis () : Unit → ℝ) (fun _ => (2/5 : ℝ)) scalarLoss true ∧
    responseRisk (basis () : Unit → ℝ) (fun _ => (1/2 : ℝ)) scalarLoss false =
      responseRisk (basis () : Unit → ℝ) (fun _ => (1/2 : ℝ)) scalarLoss true := by
  norm_num [responseRisk, risk, basis, scalarLoss]

/-- A smaller approximate gap can actually reverse the decision. -/
theorem small_gap_reverses :
    responseRisk (basis () : Unit → ℝ) (fun _ => (9/20 : ℝ)) scalarLoss false <
      responseRisk (basis () : Unit → ℝ) (fun _ => (9/20 : ℝ)) scalarLoss true ∧
    responseRisk (basis () : Unit → ℝ) (fun _ => (11/20 : ℝ)) scalarLoss true <
      responseRisk (basis () : Unit → ℝ) (fun _ => (11/20 : ℝ)) scalarLoss false := by
  norm_num [responseRisk, risk, basis, scalarLoss]

/-- Same laws and responses, different objectives: this is not an approximation chain. -/
theorem changed_loss_is_unaccounted :
    |responseRisk (basis () : Unit → ℝ) (fun _ => (0 : ℝ)) (fun (_ : Unit) _ => (0 : ℝ)) ()-
      responseRisk (basis () : Unit → ℝ) (fun _ => (0 : ℝ)) (fun (_ : Unit) _ => (1 : ℝ)) ()| = 1 := by
  norm_num [responseRisk, risk, basis]

/-- A bounded discontinuous loss need not have unit sensitivity. -/
theorem bounded_is_not_lipschitz_one :
    dist (0 : ℝ) (1/100) = 1/100 ∧
    |(if (0 : ℝ)>0 then (1 : ℝ) else 0)-(if (1/100 : ℝ)>0 then (1 : ℝ) else 0)| = 1 := by
  norm_num [Real.dist_eq]

/-- The loss range is necessary for the cap one and the coefficient on total variation. -/
theorem unbounded_loss_breaks_cap :
    risk (basis false : Bool → ℝ) (fun b => if b then 10 else 0) = 0 ∧
    risk (basis true : Bool → ℝ) (fun b => if b then 10 else 0) = 10 := by
  norm_num [risk, basis, Fintype.sum_bool]

/-- Perfect numerical estimation does not certify a deliberately nonoptimal selected action. -/
theorem optimization_residual_cannot_disappear :
    responseRisk (basis () : Unit → ℝ) (fun _ => (1/4 : ℝ)) scalarLoss true-
      responseRisk (basis () : Unit → ℝ) (fun _ => (1/4 : ℝ)) scalarLoss false = 1/2 := by
  norm_num [responseRisk, risk, basis, scalarLoss]

/-- An impossible event is excluded before the conditional decision theorem is used. -/
theorem impossible_report_has_no_probability_record :
    mass (restrict (∅ : Finset Bool) (basis false)) = 0 ∧
    ¬ IsDist (recordAfter id (∅ : Finset Bool) (basis false)) := by
  norm_num [IsDist, recordAfter, mass, push, normalize, restrict, Fintype.sum_bool]

end
end Komorebi.MachineTheory.ResponseExamples
