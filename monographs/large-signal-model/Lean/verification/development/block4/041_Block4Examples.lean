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


theorem completion_dimension_two :
    finrank ℝ (instrumentCompletion tinyInstrument.branch mass) = 2 := by
  rw [completion_exactly_two_rows,
    LinearMap.finrank_range_of_inj (LinearMap.dualMap_injective_of_surjective summary_surjective),
    Subspace.dual_finrank_eq, Module.finrank_fintype_fun_eq_card, Fintype.card_fin]

theorem mass_alone_cannot_predict :
    ¬ ∃ f : ℝ → ℝ, ∀ p, IsPrior p →
      f (mass p) = mass (tinyInstrument.branch ((),true) p) := by
  rintro ⟨f,hf⟩
  have h0 := hf (pointMass 0) (point_prior (0 : Fin 3))
  have h2 := hf (pointMass 2) (point_prior (2 : Fin 3))
  rw [mass_pointMass] at h0 h2
  norm_num [mass_apply, Instrument.branch_apply, tinyInstrument, hiddenMatrix,pointMass,
    Fin.sum_univ_succ] at h0 h2
  linarith

noncomputable def wrongMatrix : Matrix (Fin 2) (Fin 2) ℝ := fun j i =>
  if i.val=0 then (if j.val=0 then 1/2 else 1/4) else 0

noncomputable def wrongBranch : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) := wrongMatrix.mulVecLin

noncomputable def actualDefect : Fin 2 → ℝ :=
  closureDefect summary (tinyInstrument.branch ((),true)) wrongBranch initialPrior

theorem exact_likelihood_pair :
    mass (tinyInstrument.branch ((),true) initialPrior) = 5/8 ∧
    summaryMass (wrongBranch (summary initialPrior)) = 1/2 := by
  norm_num [tinyInstrument,Instrument.branch,hiddenMatrix,initialPrior,summaryMass,
    wrongBranch,wrongMatrix,summary,summaryMatrix,Matrix.mulVec,Matrix.mul_apply,dotProduct,Fin.sum_univ_succ]

theorem exact_defect_coordinates : actualDefect 0 = 1/8 ∧ actualDefect 1 = 3/8 := by
  norm_num [actualDefect,closureDefect,tinyInstrument,Instrument.branch,hiddenMatrix,initialPrior,
    wrongBranch,wrongMatrix,summary,summaryMatrix,Matrix.mulVec,Matrix.mul_apply,dotProduct,Fin.sum_univ_succ]

theorem likelihood_error_is_mass_defect :
    mass (tinyInstrument.branch ((),true) initialPrior) -
      summaryMass (wrongBranch (summary initialPrior)) = summaryMass actualDefect :=
  likelihood_defect summary _ wrongBranch mass summaryMass summary_preserves_mass initialPrior

theorem true_posterior_coordinates :
    summary (normalize mass (tinyInstrument.branch ((),true) initialPrior)) 0 = 1 ∧
    summary (normalize mass (tinyInstrument.branch ((),true) initialPrior)) 1 = 1 := by
  norm_num [FiniteInstruments.normalize,tinyInstrument,Instrument.branch,hiddenMatrix,initialPrior,
    summary,summaryMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]

theorem proposed_posterior_coordinates :
    normalize summaryMass (wrongBranch (summary initialPrior)) 0 = 1 ∧
    normalize summaryMass (wrongBranch (summary initialPrior)) 1 = 1/2 := by
  norm_num [FiniteInstruments.normalize,summaryMass,wrongBranch,wrongMatrix,initialPrior,
    summary,summaryMatrix,Matrix.mulVec,Matrix.mul_apply,dotProduct,Fin.sum_univ_succ]

theorem proposed_posterior_is_realizable :
    normalize summaryMass (wrongBranch (summary initialPrior)) ∈ realizableBeliefs summary := by
  refine ⟨initialPrior,initial_prior_valid, ?_⟩
  funext j
  fin_cases j
  · exact initial_predictive_state.1.trans proposed_posterior_coordinates.1.symm
  · exact initial_predictive_state.2.trans proposed_posterior_coordinates.2.symm

theorem oblique_defect_coordinates :
    oblique summaryMass (normalize summaryMass (wrongBranch (summary initialPrior))) actualDefect 0 = 0 ∧
    oblique summaryMass (normalize summaryMass (wrongBranch (summary initialPrior))) actualDefect 1 = 5/16 := by
  have hm : summaryMass actualDefect = 1/8 := exact_defect_coordinates.1
  simp only [oblique_apply,Pi.sub_apply,Pi.smul_apply,smul_eq_mul,hm,
    exact_defect_coordinates.1,exact_defect_coordinates.2,
    proposed_posterior_coordinates.1,proposed_posterior_coordinates.2]
  norm_num

theorem normalized_defect_coordinates :
    summary (normalize mass (tinyInstrument.branch ((),true) initialPrior)) 0 -
      normalize summaryMass (wrongBranch (summary initialPrior)) 0 = 0 ∧
    summary (normalize mass (tinyInstrument.branch ((),true) initialPrior)) 1 -
      normalize summaryMass (wrongBranch (summary initialPrior)) 1 = 1/2 := by
  rw [true_posterior_coordinates.1,true_posterior_coordinates.2,
    proposed_posterior_coordinates.1,proposed_posterior_coordinates.2]
  norm_num

theorem example_satisfies_general_defect :
    summary (normalize mass (tinyInstrument.branch ((),true) initialPrior)) -
      normalize summaryMass (wrongBranch (summary initialPrior)) =
    (mass (tinyInstrument.branch ((),true) initialPrior))⁻¹ •
      oblique summaryMass (normalize summaryMass (wrongBranch (summary initialPrior))) actualDefect := by
  exact normalized_closure_defect summary _ wrongBranch summaryMass summary_preserves_mass initialPrior
    (by rw [exact_likelihood_pair.1]; norm_num) (by rw [exact_likelihood_pair.2]; norm_num)

noncomputable def coinInstrument (theta : ℝ) (h0 : 0 ≤ theta) (h1 : theta ≤ 1) :
    Instrument (Fin 1) Unit Bool where
  matrix _ o _ _ := if o then theta else 1-theta
  nonneg := by intro a o j i; cases o <;> simp [h0,sub_nonneg.mpr h1]
  mass_one := by intro a i; simp

noncomputable def coinOne : Instrument (Fin 1) Unit Bool := coinInstrument (1/3) (by norm_num) (by norm_num)
noncomputable def coinTwo : Instrument (Fin 1) Unit Bool := coinInstrument (2/3) (by norm_num) (by norm_num)

theorem coins_posterior_agrees_all_priors (p : Fin 1 → ℝ) (hp : IsPrior p) :
    normalize mass (coinOne.branch ((),true) p) = normalize mass (coinTwo.branch ((),true) p) := by
  have hp0 : p 0 = 1 := by simpa [Fin.sum_univ_succ] using hp.2
  funext j
  fin_cases j
  norm_num [FiniteInstruments.normalize,coinOne,coinTwo,coinInstrument,Instrument.branch,Matrix.mulVecLin_apply,
    Matrix.mulVec,dotProduct,Fin.sum_univ_succ,hp0]

theorem coins_likelihoods_differ_all_priors (p : Fin 1 → ℝ) (hp : IsPrior p) :
    mass (coinOne.branch ((),true) p) = 1/3 ∧ mass (coinTwo.branch ((),true) p) = 2/3 := by
  have hp0 : p 0 = 1 := by simpa [Fin.sum_univ_succ] using hp.2
  norm_num [coinOne,coinTwo,coinInstrument,Instrument.branch,Matrix.mulVecLin_apply,Matrix.mulVec,dotProduct,
    Fin.sum_univ_succ,hp0]

theorem coins_branches_distinct : coinOne.branch ((),true) ≠ coinTwo.branch ((),true) := by
  intro h
  have hx := congrArg (fun F : (Fin 1 → ℝ) →ₗ[ℝ] (Fin 1 → ℝ) => mass (F (pointMass 0))) h
  have hd := coins_likelihoods_differ_all_priors (pointMass 0) (point_prior 0)
  rw [hd.1,hd.2] at hx
  norm_num at hx

theorem posterior_alone_does_not_imply_closure :
    (∀ p, IsStrictPrior p →
      normalize mass (coinOne.branch ((),true) p) = normalize mass (coinTwo.branch ((),true) p)) ∧
    (LinearMap.id : (Fin 1 → ℝ) →ₗ[ℝ] (Fin 1 → ℝ)).comp (coinOne.branch ((),true)) ≠
      (coinTwo.branch ((),true)).comp LinearMap.id := by
  refine ⟨fun p hp => coins_posterior_agrees_all_priors p hp.1, ?_⟩
  simpa using coins_branches_distinct

theorem impossible_branch_not_prior :
    ¬ IsPrior (normalize mass ((coinInstrument 0 le_rfl (by norm_num)).branch ((),true) (pointMass 0))) := by
  intro h
  have hh := h.2
  norm_num [FiniteInstruments.normalize,coinInstrument,Instrument.branch,Matrix.mulVecLin_apply,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] at hh

/-- This is an intentionally non-onto representation. -/
def embeddedScalar : ℝ →ₗ[ℝ] (Fin 2 → ℝ) :=
  LinearMap.pi (fun j => if j.val=0 then LinearMap.id else 0)

def invisibleDirection : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) :=
  LinearMap.pi (fun j => if j.val=1 then LinearMap.proj 1 else 0)

theorem invisible_on_representation : invisibleDirection.comp embeddedScalar = 0 := by
  apply LinearMap.ext
  intro x
  funext j
  fin_cases j <;> simp [invisibleDirection,embeddedScalar]

theorem invisible_is_not_zero : invisibleDirection ≠ 0 := by
  intro h
  have hh := congrArg (fun F : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ) => F (pointMass 1) 1) h
  norm_num [invisibleDirection,pointMass] at hh

theorem onto_required_for_uniqueness :
    invisibleDirection.comp embeddedScalar = (0 : (Fin 2 → ℝ) →ₗ[ℝ] (Fin 2 → ℝ)).comp embeddedScalar ∧
      invisibleDirection ≠ 0 := by
  exact ⟨by simpa using invisible_on_representation, invisible_is_not_zero⟩


end Komorebi.LSM.Block4Examples
