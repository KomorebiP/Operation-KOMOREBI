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

def coarse3 (i : Fin 3) : Bool := decide (i = 2)
noncomputable def prior3 (i : Fin 3) : ℝ := if i = 0 then 1/2 else 1/4
def likelihood3 (i : Fin 3) : ℝ := if i = 0 then 1 else if i = 1 then 3 else 2

theorem prior3_valid : IsPrior prior3 := by
  constructor
  · intro i; fin_cases i <;> norm_num [Fin.ext_iff, prior3]
  · norm_num [Fin.ext_iff, prior3, Fin.sum_univ_succ]

theorem likelihood3_positive : ∀ i, 0 < likelihood3 i := by
  intro i; fin_cases i <;> norm_num [Fin.ext_iff, likelihood3]

theorem prior3_coarse_masses :
    aggregate coarse3 prior3 false = 3/4 ∧ aggregate coarse3 prior3 true = 1/4 := by
  norm_num [Fin.ext_iff, aggregate, coarse3, prior3, Fin.sum_univ_succ]

theorem prior3_effective_likelihood :
    effectiveLikelihood coarse3 prior3 likelihood3 false = 5/3 ∧
    effectiveLikelihood coarse3 prior3 likelihood3 true = 2 := by
  norm_num [Fin.ext_iff, effectiveLikelihood, aggregate, coarse3, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_evidence : evidence prior3 likelihood3 = 7/4 := by
  norm_num [Fin.ext_iff, evidence, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_updated_masses :
    aggregate coarse3 (posterior prior3 likelihood3) false = 5/7 ∧
    aggregate coarse3 (posterior prior3 likelihood3) true = 2/7 := by
  norm_num [Fin.ext_iff, aggregate, posterior, evidence, coarse3, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_exact_defect :
    aggregate coarse3 (posterior prior3 likelihood3) false -
      posterior (aggregate coarse3 prior3) (fun _ => 1) false = -1/28 ∧
    aggregate coarse3 (posterior prior3 likelihood3) true -
      posterior (aggregate coarse3 prior3) (fun _ => 1) true = 1/28 := by
  norm_num [Fin.ext_iff, aggregate, posterior, evidence, coarse3, prior3, likelihood3, Fin.sum_univ_succ]

theorem prior3_updates_do_not_commute :
    ¬ BayesCommutes coarse3 likelihood3 (fun _ => 1) := by
  intro h
  have he := congrFun (h prior3 prior3_valid) false
  have hd := prior3_exact_defect.1
  rw [he, sub_self] at hd
  norm_num at hd

noncomputable def balanced3 (i : Fin 3) : ℝ := if i = 2 then 1/2 else 1/4

theorem one_prior_can_hide_a_defect :
    aggregate coarse3 (posterior balanced3 likelihood3) =
      posterior (aggregate coarse3 balanced3) (fun _ => 1) := by
  funext a
  cases a <;> norm_num [Fin.ext_iff, aggregate, posterior, evidence, coarse3, balanced3, likelihood3,
    Fin.sum_univ_succ]

theorem empty_mass_block_is_harmless :
    effectiveLikelihood coarse3 (pointMass 0) likelihood3 true = 0 ∧
    aggregate coarse3 (posterior (pointMass 0) likelihood3) true = 0 := by
  norm_num [Fin.ext_iff, effectiveLikelihood, aggregate, posterior, evidence, coarse3, pointMass,
    likelihood3, Fin.sum_univ_succ]

def unequal2 (i : Fin 2) : ℝ := if i = 0 then 1 else 2

theorem unequal2_positive : ∀ i, 0 < unequal2 i := by
  intro i; fin_cases i <;> norm_num [Fin.ext_iff, unequal2]

theorem one_block_commutes_with_unequal_likelihoods :
    BayesCommutes (fun _ : Fin 2 => ()) unequal2 (fun _ => 1) :=
  one_block_commutes unequal2 (fun _ => 1) unequal2_positive (fun _ => by norm_num)

theorem one_block_global_scale_is_not_necessary :
    ¬ ∃ s : ℝ, 0 < s ∧ ∀ i : Fin 2, unequal2 i = s * (1 : ℝ) := by
  rintro ⟨s, _, h⟩
  have h0 := h 0
  have h1 := h 1
  norm_num [Fin.ext_iff, unequal2] at h0 h1
  linarith

theorem zero_evidence_is_not_an_update :
    ¬ IsPrior (posterior prior3 (fun _ => 0)) := by
  intro h
  have hs := h.2
  norm_num [Fin.ext_iff, posterior, evidence] at hs


end Komorebi.LSM.Block3Examples
