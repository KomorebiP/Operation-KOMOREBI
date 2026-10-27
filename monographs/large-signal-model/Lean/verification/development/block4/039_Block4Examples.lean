import KomorebiLSM.InstrumentRealization
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.BigOperators.Fin

/-! Exact examples distinguish prediction from reconstruction, word order,
likelihood from posterior, and linear uniqueness from admissible-state equality. -/
set_option autoImplicit false
namespace Komorebi.LSM.Block4Examples
open scoped BigOperators
open Module FiniteBayes FiniteInstruments

noncomputable def hiddenMatrix (o : Bool) : Matrix (Fin 3) (Fin 3) ℝ := fun j i =>
  if o then
    if j.val = 2 then (if i.val = 2 then 3/4 else 1/2) else 0
  else
    if j.val = 2 then 0 else (if i.val = 2 then 1/8 else 1/4)

noncomputable def tinyInstrument : Instrument (Fin 3) Unit Bool where
  matrix _ := hiddenMatrix
  nonneg := by
    intro a o j i
    cases o <;> fin_cases j <;> fin_cases i <;> norm_num [hiddenMatrix]
  mass_one := by
    intro a i
    fin_cases i <;> norm_num [hiddenMatrix, Fin.sum_univ_succ]

noncomputable def summaryMatrix : Matrix (Fin 2) (Fin 3) ℝ := fun j i =>
  if j.val = 0 then 1 else if i.val = 2 then 1 else 0

noncomputable def summary : (Fin 3 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) := summaryMatrix.mulVecLin

def summaryMass : (Fin 2 → ℝ) →ₗ[ℝ] ℝ := LinearMap.proj 0

noncomputable def reducedMatrix (o : Bool) : Matrix (Fin 2) (Fin 2) ℝ := fun j i =>
  if o then (if i.val = 0 then 1/2 else 1/4)
  else if j.val = 0 then (if i.val = 0 then 1/2 else -1/4) else 0

noncomputable def reducedBranch (s : Unit × Bool) :
    (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) := (reducedMatrix s.2).mulVecLin

theorem summary_coordinates (p : Fin 3 → ℝ) :
    summary p 0 = mass p ∧ summary p 1 = p 2 := by
  simp [summary, summaryMatrix, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]

theorem summary_preserves_mass : summaryMass.comp summary = mass := by
  apply LinearMap.ext
  intro p
  exact (summary_coordinates p).1

theorem summary_surjective : Function.Surjective summary := by
  intro z
  let p : Fin 3 → ℝ := fun i => if i.val=0 then z 0-z 1 else if i.val=2 then z 1 else 0
  refine ⟨p, ?_⟩
  funext j
  fin_cases j <;> simp [summary,summaryMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ,p]

theorem reduced_intertwining (s : Unit × Bool) :
    (reducedBranch s).comp summary = summary.comp (tinyInstrument.branch s) := by
  apply LinearMap.ext
  intro p
  funext j
  rcases s with ⟨a,o⟩
  cases o <;> fin_cases j <;>
    simp [reducedBranch,reducedMatrix,summary,summaryMatrix,tinyInstrument,
      Instrument.branch,hiddenMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] <;> ring

theorem reduced_maps_unique (s : Unit × Bool)
    (D : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ))
    (hD : D.comp summary = summary.comp (tinyInstrument.branch s)) : D = reducedBranch s :=
  closed_operator_unique summary summary_surjective _ _ D (reduced_intertwining s) hD

theorem all_word_readouts (w : List (Unit × Bool)) (p : Fin 3 → ℝ) :
    summaryMass (wordAction reducedBranch w (summary p)) =
      mass (wordAction tinyInstrument.branch w p) :=
  reduced_word_readout tinyInstrument summary reducedBranch summaryMass
    summary_preserves_mass reduced_intertwining w p

theorem same_summary : summary (pointMass (0 : Fin 3)) = summary (pointMass 1) := by
  funext j
  fin_cases j <;> norm_num [summary,summaryMatrix,pointMass,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem distinct_hidden_priors : pointMass (0 : Fin 3) ≠ pointMass 1 := by
  exact fun h => (by norm_num : (0 : Fin 3) ≠ 1) (pointMass_injective h)

theorem same_every_future_word (w : List (Unit × Bool)) :
    mass (wordAction tinyInstrument.branch w (pointMass 0)) =
      mass (wordAction tinyInstrument.branch w (pointMass 1)) := by
  rw [← all_word_readouts, ← all_word_readouts, same_summary]

theorem mass_row_in_completion :
    (mass : (Fin 3 → ℝ) →ₗ[ℝ] ℝ) ∈ instrumentCompletion tinyInstrument.branch mass :=
  massRow_mem_completion _ _

theorem coordinate_two_from_word :
    (LinearMap.proj 2 : (Fin 3 → ℝ) →ₗ[ℝ] ℝ) =
      (4 : ℝ) • wordRow tinyInstrument.branch mass [((),true)] - (2 : ℝ) • mass := by
  apply LinearMap.ext
  intro p
  simp [wordRow,wordAction,tinyInstrument,Instrument.branch,hiddenMatrix,
    Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
  ring

theorem coordinate_two_in_completion :
    (LinearMap.proj 2 : (Fin 3 → ℝ) →ₗ[ℝ] ℝ) ∈ instrumentCompletion tinyInstrument.branch mass := by
  rw [coordinate_two_from_word]
  exact (instrumentCompletion tinyInstrument.branch mass).sub_mem
    ((instrumentCompletion tinyInstrument.branch mass).smul_mem _ (wordRow_mem_completion _ _ _))
    ((instrumentCompletion tinyInstrument.branch mass).smul_mem _ mass_row_in_completion)

/-- The actual completed row space is exactly the two-row summary space. -/
theorem completion_exactly_two_rows : instrumentCompletion tinyInstrument.branch mass =
    LinearMap.range summary.dualMap := by
  apply le_antisymm
  · exact completion_le_word_reading_summary _ summary
      (realization_reads_all_words tinyInstrument summary reducedBranch summaryMass
        summary_preserves_mass reduced_intertwining)
  · apply summary_rowspace_le
    intro j
    fin_cases j
    · change summaryMass.comp summary ∈ instrumentCompletion tinyInstrument.branch mass
      rw [summary_preserves_mass]
      exact mass_row_in_completion
    · have he : (LinearMap.proj (1 : Fin 2)).comp summary =
          (LinearMap.proj (2 : Fin 3) : (Fin 3 → ℝ) →ₗ[ℝ] ℝ) := by
        apply LinearMap.ext
        intro p
        exact (summary_coordinates p).2
      change (LinearMap.proj (1 : Fin 2)).comp summary ∈ instrumentCompletion tinyInstrument.branch mass
      rw [he]
      exact coordinate_two_in_completion

theorem first_hidden_coordinate_is_omitted :
    (LinearMap.proj 0 : (Fin 3 → ℝ) →ₗ[ℝ] ℝ) ∉ instrumentCompletion tinyInstrument.branch mass := by
  rw [completion_exactly_two_rows]
  rintro ⟨f,hf⟩
  have h0 := congrArg (fun g : (Fin 3 → ℝ) →ₗ[ℝ] ℝ => g (pointMass 0)) hf
  have h1 := congrArg (fun g : (Fin 3 → ℝ) →ₗ[ℝ] ℝ => g (pointMass 1)) hf
  change f (summary (pointMass 0)) = pointMass (0 : Fin 3) 0 at h0
  change f (summary (pointMass 1)) = pointMass (1 : Fin 3) 0 at h1
  rw [same_summary] at h0
  norm_num [pointMass] at h0 h1
  linarith

noncomputable def initialPrior (i : Fin 3) : ℝ := if i.val=2 then 1/2 else 1/4

theorem initial_prior_valid : IsPrior initialPrior := by
  constructor
  · intro i; fin_cases i <;> norm_num [initialPrior]
  · norm_num [initialPrior,Fin.sum_univ_succ]

theorem initial_predictive_state : summary initialPrior 0 = 1 ∧ summary initialPrior 1 = 1/2 := by
  norm_num [summary,summaryMatrix,initialPrior,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem initial_likelihoods :
    mass (tinyInstrument.branch ((),false) initialPrior) = 3/8 ∧
    mass (tinyInstrument.branch ((),true) initialPrior) = 5/8 := by
  norm_num [tinyInstrument,Instrument.branch,hiddenMatrix,initialPrior,
    Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem true_then_false_probability :
    mass (wordAction tinyInstrument.branch [((),true),((),false)] initialPrior) = 5/32 := by
  norm_num [wordAction,tinyInstrument,Instrument.branch,hiddenMatrix,initialPrior,Matrix.mul_apply,
    Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem false_then_true_probability :
    mass (wordAction tinyInstrument.branch [((),false),((),true)] initialPrior) = 3/16 := by
  norm_num [wordAction,tinyInstrument,Instrument.branch,hiddenMatrix,initialPrior,Matrix.mul_apply,
    Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem order_matters :
    mass (wordAction tinyInstrument.branch [((),true),((),false)] initialPrior) ≠
      mass (wordAction tinyInstrument.branch [((),false),((),true)] initialPrior) := by
  rw [true_then_false_probability,false_then_true_probability]
  norm_num

theorem complete_tree_mass (as : List Unit) :
    tinyInstrument.observationTreeMass as initialPrior = 1 := by
  rw [Instrument.observationTreeMass_eq,mass_prior _ initial_prior_valid]

theorem signed_reduced_entry : reducedMatrix false 0 1 = -1/4 := by
  norm_num [reducedMatrix]

theorem reduced_probabilities_valid (w : List (Unit × Bool)) :
    0 ≤ summaryMass (wordAction reducedBranch w (summary initialPrior)) ∧
      summaryMass (wordAction reducedBranch w (summary initialPrior)) ≤ 1 := by
  rw [all_word_readouts]
  exact tinyInstrument.word_probability w initialPrior initial_prior_valid

end Komorebi.LSM.Block4Examples
