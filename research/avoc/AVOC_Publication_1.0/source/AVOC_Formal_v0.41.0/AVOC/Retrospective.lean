import AVOC.BayesianCompression
import AVOC.BayesianExamples
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- Coarse open-world hypothesis vocabulary: named hypotheses plus an unresolved
residual bucket. -/
abbrev OpenHypothesis (H : Type) := Option H

/-- Refining the residual bucket by naming new proposals while retaining an
unresolved remainder. -/
abbrev RefinedOpenHypothesis (H P : Type) := Option (Sum H P)

/-- Forget newly proposed distinctions back into the old residual bucket. -/
def forgetProposals {H P : Type} : RefinedOpenHypothesis H P → OpenHypothesis H
  | none => none
  | some (Sum.inl h) => some h
  | some (Sum.inr _) => none

@[simp] theorem forgetProposals_known {H P : Type} (h : H) :
    forgetProposals (P := P) (some (Sum.inl h)) = some h := rfl

@[simp] theorem forgetProposals_proposed {H P : Type} (p : P) :
    forgetProposals (H := H) (some (Sum.inr p)) = none := rfl

@[simp] theorem forgetProposals_residual {H P : Type} :
    forgetProposals (H := H) (P := P) none = none := rfl

/-- Naming hypotheses is a representation refinement: the old vocabulary is a
deterministic decoding of the refined one. -/
theorem proposal_is_refinement {H P : Type} :
    Refines (id : RefinedOpenHypothesis H P → RefinedOpenHypothesis H P)
      (forgetProposals : RefinedOpenHypothesis H P → OpenHypothesis H) := by
  exact ⟨forgetProposals, by intro x; rfl⟩

/-- Concrete likelihood that favors `true`. -/
def retrospectiveLikelihoodTrue : Bool → ℚ
  | false => 1
  | true => 9

/-- Concrete likelihood that favors `false`. -/
def retrospectiveLikelihoodFalse : Bool → ℚ
  | false => 9
  | true => 1

theorem retrospectiveLikelihoodTrue_nonneg : ∀ ω, 0 ≤ retrospectiveLikelihoodTrue ω := by
  intro ω
  cases ω <;> norm_num [retrospectiveLikelihoodTrue]

theorem retrospectiveLikelihoodFalse_nonneg : ∀ ω, 0 ≤ retrospectiveLikelihoodFalse ω := by
  intro ω
  cases ω <;> norm_num [retrospectiveLikelihoodFalse]

theorem retrospectiveLikelihoodTrue_mass :
    evidenceMass uniformBoolBelief retrospectiveLikelihoodTrue = 5 := by
  unfold evidenceMass uniformBoolBelief retrospectiveLikelihoodTrue
  rw [Fintype.sum_bool]
  norm_num

theorem retrospectiveLikelihoodFalse_mass :
    evidenceMass uniformBoolBelief retrospectiveLikelihoodFalse = 5 := by
  unfold evidenceMass uniformBoolBelief retrospectiveLikelihoodFalse
  rw [Fintype.sum_bool]
  norm_num

theorem retrospectiveLikelihoodTrue_positive :
    0 < evidenceMass uniformBoolBelief retrospectiveLikelihoodTrue := by
  rw [retrospectiveLikelihoodTrue_mass]
  norm_num

theorem retrospectiveLikelihoodFalse_positive :
    0 < evidenceMass uniformBoolBelief retrospectiveLikelihoodFalse := by
  rw [retrospectiveLikelihoodFalse_mass]
  norm_num

/-- The first evidence history yields posterior mass 9/10 on `true`. -/
theorem retrospectivePosteriorTrue_true :
    (conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
      retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive).prob true = 9 / 10 := by
  have h := conditionByWeight_mul_evidence
    uniformBoolBelief retrospectiveLikelihoodTrue
    retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive true
  have hrhs : uniformBoolBelief.prob true * retrospectiveLikelihoodTrue true = 9 / 2 := by
    norm_num [uniformBoolBelief, retrospectiveLikelihoodTrue]
  rw [retrospectiveLikelihoodTrue_mass, hrhs] at h
  linarith

/-- The reversed evidence history yields posterior mass 1/10 on `true`. -/
theorem retrospectivePosteriorFalse_true :
    (conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
      retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive).prob true = 1 / 10 := by
  have h := conditionByWeight_mul_evidence
    uniformBoolBelief retrospectiveLikelihoodFalse
    retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive true
  have hrhs : uniformBoolBelief.prob true * retrospectiveLikelihoodFalse true = 1 / 2 := by
    norm_num [uniformBoolBelief, retrospectiveLikelihoodFalse]
  rw [retrospectiveLikelihoodFalse_mass, hrhs] at h
  linarith

/-- The two fine posteriors are genuinely different. -/
theorem retrospectiveFinePosteriors_ne :
    conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
        retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive ≠
      conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
        retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive := by
  intro h
  have hp := congrArg (fun b : RationalBelief Bool => b.prob true) h
  rw [retrospectivePosteriorTrue_true, retrospectivePosteriorFalse_true] at hp
  norm_num at hp

/-- Any belief pushed through the constant one-cell representation becomes the
unique point mass on `Unit`. -/
theorem pushforward_constantUnit
    (b : RationalBelief Bool) :
    pushforwardBelief (fun _ : Bool => ()) b = diracBelief () := by
  apply RationalBelief.ext
  intro z
  cases z
  change (∑ x ∈ Finset.univ.filter (fun _ : Bool => True), b.prob x) = 1
  simpa using b.sum_one

/-- The two distinct evidence histories become indistinguishable after the
one-cell compression. -/
theorem retrospectiveCoarsePosteriors_eq :
    pushforwardBelief (fun _ : Bool => ())
        (conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
          retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive) =
      pushforwardBelief (fun _ : Bool => ())
        (conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
          retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive) := by
  rw [pushforward_constantUnit, pushforward_constantUnit]

/-- No decoder from the compressed posterior can retrospectively determine
which of the two fine evidence-conditioned posteriors occurred. -/
theorem no_retrospective_decoder_for_evidence_split :
    ¬ ∃ recover : RationalBelief Unit → RationalBelief Bool,
      recover (pushforwardBelief (fun _ : Bool => ())
        (conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
          retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive)) =
        conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
          retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive ∧
      recover (pushforwardBelief (fun _ : Bool => ())
        (conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
          retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive)) =
        conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
          retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive := by
  rintro ⟨recover, htrue, hfalse⟩
  have hcoarse := retrospectiveCoarsePosteriors_eq
  have hsame :
      conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
          retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive =
        conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
          retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive := by
    calc
      conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
          retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive =
          recover (pushforwardBelief (fun _ : Bool => ())
            (conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
              retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive)) := htrue.symm
      _ = recover (pushforwardBelief (fun _ : Bool => ())
            (conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
              retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive)) :=
            congrArg recover hcoarse
      _ = conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
          retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive := hfalse
  exact retrospectiveFinePosteriors_ne hsame

end Komorebi.AVOC
