import AVOC.BayesianEvidence
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

/-- Uniform rational prior on Bool. -/
def uniformBoolBelief : RationalBelief Bool where
  prob _ := 1 / 2
  nonneg := by intro ω; norm_num
  sum_one := by
    rw [Fintype.sum_bool]
    norm_num

/-- Under perfect Bool observation, `true` has prior predictive probability 1/2. -/
theorem uniformBool_perfect_true_predictive :
    predictiveProb uniformBoolBelief (identityChannel Bool) true = 1 / 2 := by
  unfold predictiveProb uniformBoolBelief identityChannel
  rw [Fintype.sum_bool]
  norm_num

/-- The perfect true observation has positive evidence. -/
theorem uniformBool_perfect_true_positive :
    0 < predictiveProb uniformBoolBelief (identityChannel Bool) true := by
  rw [uniformBool_perfect_true_predictive]
  norm_num

/-- Perfect observation collapses the uniform prior to the observed world. -/
theorem perfectBoolPosterior_true :
    (bayesUpdate uniformBoolBelief (identityChannel Bool) true
      uniformBool_perfect_true_positive).prob true = 1 := by
  have h := bayesUpdate_mul_predictive
    uniformBoolBelief (identityChannel Bool) true
    uniformBool_perfect_true_positive true
  have hrhs : uniformBoolBelief.prob true * (identityChannel Bool).prob true true = 1 / 2 := by
    norm_num [uniformBoolBelief, identityChannel]
  rw [uniformBool_perfect_true_predictive, hrhs] at h
  linarith

/-- The unobserved Bool world receives zero posterior mass. -/
theorem perfectBoolPosterior_false :
    (bayesUpdate uniformBoolBelief (identityChannel Bool) true
      uniformBool_perfect_true_positive).prob false = 0 := by
  have h := bayesUpdate_mul_predictive
    uniformBoolBelief (identityChannel Bool) true
    uniformBool_perfect_true_positive false
  have hrhs : uniformBoolBelief.prob false * (identityChannel Bool).prob false true = 0 := by
    norm_num [uniformBoolBelief, identityChannel]
  rw [uniformBool_perfect_true_predictive, hrhs] at h
  linarith

/-- Two positive likelihood factors used for a concrete order-invariance test. -/
def boolLikelihoodOne : Bool → ℚ
  | false => 1
  | true => 2

def boolLikelihoodTwo : Bool → ℚ
  | false => 3
  | true => 1

theorem boolLikelihoodOne_nonneg : ∀ ω, 0 ≤ boolLikelihoodOne ω := by
  intro ω
  cases ω <;> norm_num [boolLikelihoodOne]

theorem boolLikelihoodTwo_nonneg : ∀ ω, 0 ≤ boolLikelihoodTwo ω := by
  intro ω
  cases ω <;> norm_num [boolLikelihoodTwo]

theorem boolLikelihoodOne_mass :
    evidenceMass uniformBoolBelief boolLikelihoodOne = 3 / 2 := by
  unfold evidenceMass uniformBoolBelief boolLikelihoodOne
  rw [Fintype.sum_bool]
  norm_num

theorem boolLikelihoodOne_positive :
    0 < evidenceMass uniformBoolBelief boolLikelihoodOne := by
  rw [boolLikelihoodOne_mass]
  norm_num

theorem boolLikelihoodTwo_mass :
    evidenceMass uniformBoolBelief boolLikelihoodTwo = 2 := by
  unfold evidenceMass uniformBoolBelief boolLikelihoodTwo
  rw [Fintype.sum_bool]
  norm_num

theorem boolLikelihoodTwo_positive :
    0 < evidenceMass uniformBoolBelief boolLikelihoodTwo := by
  rw [boolLikelihoodTwo_mass]
  norm_num

theorem boolLikelihoodProduct_mass :
    evidenceMass uniformBoolBelief
      (fun ω => boolLikelihoodOne ω * boolLikelihoodTwo ω) = 5 / 2 := by
  unfold evidenceMass uniformBoolBelief boolLikelihoodOne boolLikelihoodTwo
  rw [Fintype.sum_bool]
  norm_num

theorem boolLikelihoodTwo_after_one_positive :
    0 < evidenceMass
      (conditionByWeight uniformBoolBelief boolLikelihoodOne
        boolLikelihoodOne_nonneg boolLikelihoodOne_positive)
      boolLikelihoodTwo := by
  have hcomp := evidenceMass_condition_compose
    uniformBoolBelief boolLikelihoodOne boolLikelihoodTwo
    boolLikelihoodOne_nonneg boolLikelihoodTwo_nonneg
    boolLikelihoodOne_positive
  rw [boolLikelihoodOne_mass, boolLikelihoodProduct_mass] at hcomp
  linarith

theorem boolLikelihoodProductReverse_mass :
    evidenceMass uniformBoolBelief
      (fun ω => boolLikelihoodTwo ω * boolLikelihoodOne ω) = 5 / 2 := by
  unfold evidenceMass uniformBoolBelief boolLikelihoodOne boolLikelihoodTwo
  rw [Fintype.sum_bool]
  norm_num

theorem boolLikelihoodOne_after_two_positive :
    0 < evidenceMass
      (conditionByWeight uniformBoolBelief boolLikelihoodTwo
        boolLikelihoodTwo_nonneg boolLikelihoodTwo_positive)
      boolLikelihoodOne := by
  have hcomp := evidenceMass_condition_compose
    uniformBoolBelief boolLikelihoodTwo boolLikelihoodOne
    boolLikelihoodTwo_nonneg boolLikelihoodOne_nonneg
    boolLikelihoodTwo_positive
  rw [boolLikelihoodTwo_mass, boolLikelihoodProductReverse_mass] at hcomp
  linarith

/-- Concrete evidence-order invariance on a finite Bayesian model. -/
theorem boolEvidence_order_invariant :
    conditionByWeight
        (conditionByWeight uniformBoolBelief boolLikelihoodOne
          boolLikelihoodOne_nonneg boolLikelihoodOne_positive)
        boolLikelihoodTwo boolLikelihoodTwo_nonneg boolLikelihoodTwo_after_one_positive =
      conditionByWeight
        (conditionByWeight uniformBoolBelief boolLikelihoodTwo
          boolLikelihoodTwo_nonneg boolLikelihoodTwo_positive)
        boolLikelihoodOne boolLikelihoodOne_nonneg boolLikelihoodOne_after_two_positive := by
  exact conditionByWeight_commute
    uniformBoolBelief boolLikelihoodOne boolLikelihoodTwo
    boolLikelihoodOne_nonneg boolLikelihoodTwo_nonneg
    boolLikelihoodOne_positive boolLikelihoodTwo_after_one_positive
    boolLikelihoodTwo_positive boolLikelihoodOne_after_two_positive

end Komorebi.AVOC
