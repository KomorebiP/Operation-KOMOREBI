import AVOC.ApproximateBayesian
import AVOC.BayesianExamples
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- Rare evidence favoring `false`. -/
def rareLikelihoodFalse (ε : ℚ) : Bool → ℚ :=
  fun b => if b then 0 else ε

/-- Rare evidence favoring `true`. -/
def rareLikelihoodTrue (ε : ℚ) : Bool → ℚ :=
  fun b => if b then ε else 0

theorem rareLikelihoodFalse_nonneg (ε : ℚ) (hε : 0 ≤ ε) :
    ∀ b, 0 ≤ rareLikelihoodFalse ε b := by
  intro b
  cases b <;> simp [rareLikelihoodFalse, hε]

theorem rareLikelihoodTrue_nonneg (ε : ℚ) (hε : 0 ≤ ε) :
    ∀ b, 0 ≤ rareLikelihoodTrue ε b := by
  intro b
  cases b <;> simp [rareLikelihoodTrue, hε]

theorem rareLikelihoodFalse_mass (ε : ℚ) :
    evidenceMass uniformBoolBelief (rareLikelihoodFalse ε) = ε / 2 := by
  unfold evidenceMass uniformBoolBelief rareLikelihoodFalse
  rw [Fintype.sum_bool]
  simp
  ring

theorem rareLikelihoodTrue_mass (ε : ℚ) :
    evidenceMass uniformBoolBelief (rareLikelihoodTrue ε) = ε / 2 := by
  unfold evidenceMass uniformBoolBelief rareLikelihoodTrue
  rw [Fintype.sum_bool]
  simp
  ring

theorem rareLikelihoodFalse_mass_pos (ε : ℚ) (hε : 0 < ε) :
    0 < evidenceMass uniformBoolBelief (rareLikelihoodFalse ε) := by
  rw [rareLikelihoodFalse_mass]
  linarith

theorem rareLikelihoodTrue_mass_pos (ε : ℚ) (hε : 0 < ε) :
    0 < evidenceMass uniformBoolBelief (rareLikelihoodTrue ε) := by
  rw [rareLikelihoodTrue_mass]
  linarith

/-- The two rare likelihoods are pointwise at most `ε` apart. -/
theorem rareLikelihood_pointwise_close (ε : ℚ) (hε : 0 ≤ ε) :
    ∀ b, |rareLikelihoodFalse ε b - rareLikelihoodTrue ε b| ≤ ε := by
  intro b
  cases b <;> simp [rareLikelihoodFalse, rareLikelihoodTrue, abs_of_nonneg hε]

/-- Conditioning on the rare-false signal yields certainty in `false`. -/
theorem rareFalse_posterior_false
    (ε : ℚ) (hε : 0 < ε) :
    (conditionByWeight uniformBoolBelief (rareLikelihoodFalse ε)
      (rareLikelihoodFalse_nonneg ε (le_of_lt hε))
      (rareLikelihoodFalse_mass_pos ε hε)).prob false = 1 := by
  let hL := rareLikelihoodFalse_nonneg ε (le_of_lt hε)
  let hpos := rareLikelihoodFalse_mass_pos ε hε
  have h := conditionByWeight_mul_evidence
    uniformBoolBelief (rareLikelihoodFalse ε) hL hpos false
  have hm := rareLikelihoodFalse_mass ε
  have hrhs : uniformBoolBelief.prob false * rareLikelihoodFalse ε false = ε / 2 := by
    simp [uniformBoolBelief, rareLikelihoodFalse]
    ring
  have hden : ε / 2 ≠ 0 := by positivity
  apply mul_right_cancel₀ hden
  simpa [hm, hrhs] using h

/-- Conditioning on the rare-false signal eliminates `true`. -/
theorem rareFalse_posterior_true
    (ε : ℚ) (hε : 0 < ε) :
    (conditionByWeight uniformBoolBelief (rareLikelihoodFalse ε)
      (rareLikelihoodFalse_nonneg ε (le_of_lt hε))
      (rareLikelihoodFalse_mass_pos ε hε)).prob true = 0 := by
  let hL := rareLikelihoodFalse_nonneg ε (le_of_lt hε)
  let hpos := rareLikelihoodFalse_mass_pos ε hε
  have h := conditionByWeight_mul_evidence
    uniformBoolBelief (rareLikelihoodFalse ε) hL hpos true
  have hm := rareLikelihoodFalse_mass ε
  have hrhs : uniformBoolBelief.prob true * rareLikelihoodFalse ε true = 0 := by
    simp [uniformBoolBelief, rareLikelihoodFalse]
  have hden : ε / 2 ≠ 0 := by positivity
  rw [hm, hrhs] at h
  exact (mul_eq_zero.mp h).resolve_right hden

/-- Conditioning on the rare-true signal yields certainty in `true`. -/
theorem rareTrue_posterior_true
    (ε : ℚ) (hε : 0 < ε) :
    (conditionByWeight uniformBoolBelief (rareLikelihoodTrue ε)
      (rareLikelihoodTrue_nonneg ε (le_of_lt hε))
      (rareLikelihoodTrue_mass_pos ε hε)).prob true = 1 := by
  let hL := rareLikelihoodTrue_nonneg ε (le_of_lt hε)
  let hpos := rareLikelihoodTrue_mass_pos ε hε
  have h := conditionByWeight_mul_evidence
    uniformBoolBelief (rareLikelihoodTrue ε) hL hpos true
  have hm := rareLikelihoodTrue_mass ε
  have hrhs : uniformBoolBelief.prob true * rareLikelihoodTrue ε true = ε / 2 := by
    simp [uniformBoolBelief, rareLikelihoodTrue]
    ring
  have hden : ε / 2 ≠ 0 := by positivity
  apply mul_right_cancel₀ hden
  simpa [hm, hrhs] using h

/-- Conditioning on the rare-true signal eliminates `false`. -/
theorem rareTrue_posterior_false
    (ε : ℚ) (hε : 0 < ε) :
    (conditionByWeight uniformBoolBelief (rareLikelihoodTrue ε)
      (rareLikelihoodTrue_nonneg ε (le_of_lt hε))
      (rareLikelihoodTrue_mass_pos ε hε)).prob false = 0 := by
  let hL := rareLikelihoodTrue_nonneg ε (le_of_lt hε)
  let hpos := rareLikelihoodTrue_mass_pos ε hε
  have h := conditionByWeight_mul_evidence
    uniformBoolBelief (rareLikelihoodTrue ε) hL hpos false
  have hm := rareLikelihoodTrue_mass ε
  have hrhs : uniformBoolBelief.prob false * rareLikelihoodTrue ε false = 0 := by
    simp [uniformBoolBelief, rareLikelihoodTrue]
  have hden : ε / 2 ≠ 0 := by positivity
  rw [hm, hrhs] at h
  exact (mul_eq_zero.mp h).resolve_right hden

/-- Arbitrarily small positive likelihood perturbations can produce maximal
posterior L1 separation when the evidence mass is equally small. -/
theorem rare_evidence_maximal_posterior_flip
    (ε : ℚ) (hε : 0 < ε) :
    beliefL1Distance
      (conditionByWeight uniformBoolBelief (rareLikelihoodFalse ε)
        (rareLikelihoodFalse_nonneg ε (le_of_lt hε))
        (rareLikelihoodFalse_mass_pos ε hε))
      (conditionByWeight uniformBoolBelief (rareLikelihoodTrue ε)
        (rareLikelihoodTrue_nonneg ε (le_of_lt hε))
        (rareLikelihoodTrue_mass_pos ε hε)) = 2 := by
  unfold beliefL1Distance
  rw [Fintype.sum_bool]
  rw [rareFalse_posterior_false ε hε, rareTrue_posterior_false ε hε]
  rw [rareFalse_posterior_true ε hε, rareTrue_posterior_true ε hε]
  norm_num

/-- No finite Lipschitz constant can control posterior L1 distance solely by
pointwise likelihood error without a positive lower bound on evidence mass. -/
theorem no_uniform_likelihood_lipschitz :
    ¬ ∃ C : ℚ, 0 ≤ C ∧
      ∀ ε : ℚ, ∀ hε : 0 < ε,
        beliefL1Distance
          (conditionByWeight uniformBoolBelief (rareLikelihoodFalse ε)
            (rareLikelihoodFalse_nonneg ε (le_of_lt hε))
            (rareLikelihoodFalse_mass_pos ε hε))
          (conditionByWeight uniformBoolBelief (rareLikelihoodTrue ε)
            (rareLikelihoodTrue_nonneg ε (le_of_lt hε))
            (rareLikelihoodTrue_mass_pos ε hε))
        ≤ C * ε := by
  rintro ⟨C, hC, hbound⟩
  let ε : ℚ := 1 / (C + 1)
  have hCp : 0 < C + 1 := by linarith
  have hε : 0 < ε := by
    dsimp [ε]
    positivity
  have hb := hbound ε hε
  rw [rare_evidence_maximal_posterior_flip ε hε] at hb
  have hratio : C * ε < 1 := by
    have hdiv : C / (C + 1) < 1 :=
      (div_lt_one hCp).2 (by linarith : C < C + 1)
    simpa [ε, div_eq_mul_inv] using hdiv
  linarith

end Komorebi.AVOC
