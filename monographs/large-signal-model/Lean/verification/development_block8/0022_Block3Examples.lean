import KomorebiLSM.FiniteStochastic
import KomorebiLSM.BayesianDefect
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Algebra.BigOperators.Fin

/-! Exact finite Bayesian defects, boundary cases and a six-state joint quotient. -/
set_option autoImplicit false
namespace Komorebi.LSM.Block3Examples
open scoped BigOperators
open FiniteBayes FinitePartitions

def coarse3 (i : Fin 3) : Bool := decide (i.val = 2)
noncomputable def prior3 (i : Fin 3) : ℝ := if i.val = 0 then 1/2 else 1/4
def likelihood3 (i : Fin 3) : ℝ := if i.val = 0 then 1 else if i.val = 1 then 3 else 2

theorem prior3_valid : IsPrior prior3 := by
  constructor
  · intro i; fin_cases i <;> norm_num [prior3]
  · norm_num [prior3, Fin.sum_univ_succ]

theorem likelihood3_positive : ∀ i, 0 < likelihood3 i := by
  intro i; fin_cases i <;> norm_num [likelihood3]

theorem prior3_coarse_masses :
    aggregate coarse3 prior3 false = 3/4 ∧ aggregate coarse3 prior3 true = 1/4 := by
  norm_num [aggregate, coarse3, prior3, Fin.sum_univ_succ]

theorem prior3_effective_likelihood :
    effectiveLikelihood coarse3 prior3 likelihood3 false = 5/3 ∧
    effectiveLikelihood coarse3 prior3 likelihood3 true = 2 := by
  norm_num [effectiveLikelihood, aggregate, coarse3, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_evidence : evidence prior3 likelihood3 = 7/4 := by
  norm_num [evidence, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_updated_masses :
    aggregate coarse3 (posterior prior3 likelihood3) false = 5/7 ∧
    aggregate coarse3 (posterior prior3 likelihood3) true = 2/7 := by
  norm_num [aggregate, posterior, evidence, coarse3, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_exact_defect :
    aggregate coarse3 (posterior prior3 likelihood3) false -
      posterior (aggregate coarse3 prior3) (fun _ => 1) false = -1/28 ∧
    aggregate coarse3 (posterior prior3 likelihood3) true -
      posterior (aggregate coarse3 prior3) (fun _ => 1) true = 1/28 := by
  norm_num [aggregate, posterior, evidence, coarse3, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_updates_do_not_commute :
    ¬ BayesCommutes coarse3 likelihood3 (fun _ => 1) := by
  intro h
  have he := congrFun (h prior3 prior3_valid) false
  have hd := prior3_exact_defect.1
  rw [he, sub_self] at hd
  norm_num at hd

noncomputable def balanced3 (i : Fin 3) : ℝ := if i.val = 2 then 1/2 else 1/4

theorem one_prior_can_hide_a_defect :
    aggregate coarse3 (posterior balanced3 likelihood3) =
      posterior (aggregate coarse3 balanced3) (fun _ => 1) := by
  funext a
  cases a <;> norm_num [aggregate, posterior, evidence, coarse3, balanced3, likelihood3,
    Fin.sum_univ_succ]

theorem empty_mass_block_is_harmless :
    effectiveLikelihood coarse3 (pointMass 0) likelihood3 true = 0 ∧
    aggregate coarse3 (posterior (pointMass 0) likelihood3) true = 0 := by
  norm_num [show (2 : Fin 3) ≠ 0 by decide, effectiveLikelihood, aggregate, posterior, evidence, coarse3, pointMass,
    likelihood3, Fin.sum_univ_succ]

def unequal2 (i : Fin 2) : ℝ := if i.val = 0 then 1 else 2

theorem unequal2_positive : ∀ i, 0 < unequal2 i := by
  intro i; fin_cases i <;> norm_num [unequal2]

theorem one_block_commutes_with_unequal_likelihoods :
    BayesCommutes (fun _ : Fin 2 => ()) unequal2 (fun _ => 1) :=
  one_block_commutes unequal2 (fun _ => 1) unequal2_positive (fun _ => by norm_num)

theorem one_block_global_scale_is_not_necessary :
    ¬ ∃ s : ℝ, 0 < s ∧ ∀ i : Fin 2, unequal2 i = s * (1 : ℝ) := by
  rintro ⟨s, _, h⟩
  have h0 := h 0
  have h1 := h 1
  norm_num [unequal2] at h0 h1
  linarith

theorem zero_evidence_is_not_an_update :
    ¬ IsPrior (posterior prior3 (fun _ => 0)) := by
  intro h
  have hs := h.2
  norm_num [posterior, evidence] at hs


/-- One deterministic transition. States zero and one remain equivalent. -/
def next6 (i : Fin 6) : Fin 6 :=
  if i.val = 0 then 3 else if i.val = 1 then 3 else if i.val = 2 then 5 else
    if i.val = 3 then 0 else if i.val = 4 then 2 else 5

def kernel6 (_ : Unit) (i : Fin 6) : Fin 6 → ℝ := pointMass (next6 i)
def likelihood6 (_ : Unit) (i : Fin 6) : ℝ := if i.val = 5 then 2 else 1

def label0 (i : Fin 6) : Fin 2 := if i.val < 3 then 0 else 1
def label1 (i : Fin 6) : Fin 3 := if i.val < 3 then 0 else if i.val < 5 then 1 else 2
def label2 (i : Fin 6) : Fin 4 :=
  if i.val < 2 then 0 else if i.val = 2 then 1 else if i.val < 5 then 2 else 3
def label3 (i : Fin 6) : Fin 5 :=
  if i.val < 2 then 0 else if i.val = 2 then 1 else if i.val = 3 then 2 else if i.val = 4 then 3 else 4

def partition0 : Setoid (Fin 6) := Setoid.ker label0
def partition1 : Setoid (Fin 6) := Setoid.ker label1
def partition2 : Setoid (Fin 6) := Setoid.ker label2
def partition3 : Setoid (Fin 6) := Setoid.ker label3

@[simp] theorem partition0_rel (i j : Fin 6) : partition0 i j ↔ label0 i = label0 j := Iff.rfl

@[simp] theorem partition1_rel (i j : Fin 6) : partition1 i j ↔ label1 i = label1 j := Iff.rfl

@[simp] theorem partition2_rel (i j : Fin 6) : partition2 i j ↔ label2 i = label2 j := Iff.rfl

@[simp] theorem partition3_rel (i j : Fin 6) : partition3 i j ↔ label3 i = label3 j := Iff.rfl

theorem kernel6_stochastic : ∀ u, IsStochastic (kernel6 u) := by
  intro u i
  exact pointMass_isPrior (next6 i)

theorem likelihood6_positive : ∀ y i, 0 < likelihood6 y i := by
  intro y i
  unfold likelihood6
  split_ifs <;> norm_num

theorem likelihood_split_six : likelihoodSplit partition0 likelihood6 = partition1 := by
  apply Setoid.ext
  intro i j
  fin_cases i <;> fin_cases j <;>
    norm_num [likelihoodSplit_rel, partition0_rel, partition1_rel, Setoid.ker_def, label0, label1, likelihood6]
  all_goals decide

theorem first_transition_split_six : transitionSplit kernel6 partition1 = partition2 := by
  apply Setoid.ext
  intro i j
  change transitionSplit (fun (_ : Unit) x => pointMass (next6 x)) partition1 i j ↔ partition2 i j
  rw [transitionSplit_deterministic]
  fin_cases i <;> fin_cases j <;>
    norm_num [partition1_rel, partition2_rel, Setoid.ker_def, label1, label2, next6]
  all_goals decide

theorem second_transition_split_six : transitionSplit kernel6 partition2 = partition3 := by
  apply Setoid.ext
  intro i j
  change transitionSplit (fun (_ : Unit) x => pointMass (next6 x)) partition2 i j ↔ partition3 i j
  rw [transitionSplit_deterministic]
  fin_cases i <;> fin_cases j <;>
    norm_num [partition2_rel, partition3_rel, Setoid.ker_def, label2, label3, next6]
  all_goals decide

theorem final_transition_split_six : transitionSplit kernel6 partition3 = partition3 := by
  apply Setoid.ext
  intro i j
  change transitionSplit (fun (_ : Unit) x => pointMass (next6 x)) partition3 i j ↔ partition3 i j
  rw [transitionSplit_deterministic]
  fin_cases i <;> fin_cases j <;>
    norm_num [partition3_rel, Setoid.ker_def, label3, next6]
  all_goals decide

theorem label0_surjective : Function.Surjective label0 := by
  intro a
  fin_cases a
  · exact ⟨0, rfl⟩
  · exact ⟨3, rfl⟩

theorem label1_surjective : Function.Surjective label1 := by
  intro a
  fin_cases a
  · exact ⟨0, rfl⟩
  · exact ⟨3, rfl⟩
  · exact ⟨5, rfl⟩

theorem label2_surjective : Function.Surjective label2 := by
  intro a
  fin_cases a
  · exact ⟨0, rfl⟩
  · exact ⟨2, rfl⟩
  · exact ⟨3, rfl⟩
  · exact ⟨5, rfl⟩

theorem label3_surjective : Function.Surjective label3 := by
  intro a
  fin_cases a
  · exact ⟨0, rfl⟩
  · exact ⟨2, rfl⟩
  · exact ⟨3, rfl⟩
  · exact ⟨4, rfl⟩
  · exact ⟨5, rfl⟩

theorem six_state_block_counts :
    blockCount partition0 = 2 ∧ blockCount partition1 = 3 ∧
    blockCount partition2 = 4 ∧ blockCount partition3 = 5 := by
  exact ⟨blockCount_kernel label0 label0_surjective,
    blockCount_kernel label1 label1_surjective,
    blockCount_kernel label2 label2_surjective,
    blockCount_kernel label3 label3_surjective⟩

theorem six_state_actual_completion : jointRefinement kernel6 likelihood6 partition0 = partition3 := by
  unfold jointRefinement
  rw [likelihood_split_six]
  unfold stableRefinement
  rw [six_state_block_counts.2.1]
  change refinementIter kernel6 partition1 3 = partition3
  simp only [refinementIter_succ, refinementIter_zero, first_transition_split_six,
    second_transition_split_six, final_transition_split_six]

theorem six_state_joint_closure : JointlyClosed kernel6 likelihood6 partition3 := by
  rw [← six_state_actual_completion]
  exact jointRefinement_closed kernel6 likelihood6 partition0 kernel6_stochastic likelihood6_positive

theorem two_states_remain_equivalent : partition3 0 1 := by
  change label3 0 = label3 1
  rfl

theorem transition_distinction_is_retained : ¬ partition3 3 4 := by
  change ¬ label3 3 = label3 4
  decide

theorem likelihood_split_is_not_prediction_closed : ¬ Lumpable kernel6 partition1 := by
  intro h
  have he := (transitionSplit_fixed_iff kernel6 partition1).mpr h
  rw [first_transition_split_six] at he
  have h02 : partition1 0 2 := by change label1 0 = label1 2; rfl
  rw [← he] at h02
  change label2 0 = label2 2 at h02
  norm_num [label2] at h02

theorem second_split_is_still_required : ¬ Lumpable kernel6 partition2 := by
  intro h
  have he := (transitionSplit_fixed_iff kernel6 partition2).mpr h
  rw [second_transition_split_six] at he
  have h34 : partition2 3 4 := by change label2 3 = label2 4; rfl
  rw [← he] at h34
  exact transition_distinction_is_retained h34

theorem initial_partition_has_two_blocks : Nontrivial (Quotient partition0) := by
  refine ⟨⟨Quotient.mk partition0 0, Quotient.mk partition0 5, ?_⟩⟩
  intro he
  have hr := Quotient.exact he
  change label0 0 = label0 5 at hr
  norm_num [label0] at hr

theorem six_state_semantic_minimality (r : Setoid (Fin 6))
    (hr : r ≤ partition0) (hc : JointlyClosed kernel6 likelihood6 r) : r ≤ partition3 := by
  let := initial_partition_has_two_blocks
  rw [← six_state_actual_completion]
  exact jointlyClosed_refines_completion kernel6 likelihood6 partition0 r
    kernel6_stochastic likelihood6_positive hr hc

end Komorebi.LSM.Block3Examples

