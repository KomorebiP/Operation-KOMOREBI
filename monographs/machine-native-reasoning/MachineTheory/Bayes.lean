import MachineTheory.Instrument
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith

/-!
Core 3.4: reporting sufficiency for the actual joint experiment.
All posterior equalities below are guarded by positive event mass. Impossible retained
reports receive an arbitrary normalized reconstruction row, not a posterior belief.
The common reporting channel has no model argument.
-/
namespace Komorebi.MachineTheory
namespace Bayes
open scoped BigOperators
open Instrument
noncomputable section
variable {M O Z : Type*} [Fintype M]

/-- Unnormalized Bayesian weights. -/
def weights (p l : M → ℝ) : M → ℝ := fun m => l m * p m

def evidence (p l : M → ℝ) : ℝ := mass (weights p l)

def update (p l : M → ℝ) : M → ℝ := normalize (weights p l)

theorem evidence_nonneg (p l : M → ℝ) (hp : ∀ m, 0 ≤ p m) (hl : ∀ m, 0 ≤ l m) :
    0 ≤ evidence p l :=
  Finset.sum_nonneg (fun m _ => mul_nonneg (hl m) (hp m))

theorem evidence_scale (p l : M → ℝ) (c : ℝ) :
    evidence p (fun m => c * l m) = c * evidence p l := by
  simp only [evidence, weights, mass, mul_assoc, ← Finset.mul_sum]

theorem update_scale (p l : M → ℝ) (c : ℝ) (hc : c ≠ 0) :
    update p (fun m => c * l m) = update p l := by
  funext m
  change (c * l m * p m) / evidence p (fun m => c * l m) =
    (l m * p m) / evidence p l
  rw [evidence_scale, mul_assoc, mul_div_mul_left _ _ hc]

/-- Positive prior support makes an impossible event impossible in every model. -/
theorem likelihood_zero_of_evidence_zero (p l : M → ℝ)
    (hp : ∀ m, 0 < p m) (hl : ∀ m, 0 ≤ l m) (he : evidence p l = 0) :
    ∀ m, l m = 0 := by
  have h := zero_of_zero_mass (weights p l)
    (fun m => mul_nonneg (hl m) (le_of_lt (hp m))) he
  intro m
  have hz : l m * p m = 0 := congrFun h m
  exact (mul_eq_zero.mp hz).resolve_right (ne_of_gt (hp m))

theorem uniform_dist [Nonempty M] : IsDist (fun _ : M => (Fintype.card M : ℝ)⁻¹) := by
  have hc : (0 : ℝ) < Fintype.card M := by exact_mod_cast Fintype.card_pos
  constructor
  · intro _; positivity
  · simp only [mass, Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
    exact mul_inv_cancel₀ (ne_of_gt hc)

theorem uniform_pos [Nonempty M] : 0 < (Fintype.card M : ℝ)⁻¹ := by
  have hc : (0 : ℝ) < Fintype.card M := by exact_mod_cast Fintype.card_pos
  positivity

variable [Fintype O] [Fintype Z]

structure ReportingModel (M O Z : Type*) [Fintype O] [Fintype Z] where
  likelihood : M → O → ℝ
  likelihood_nonneg : ∀ m o, 0 ≤ likelihood m o
  likelihood_sum : ∀ m, ∑ o, likelihood m o = 1
  channel : O → Z → ℝ
  channel_nonneg : ∀ o z, 0 ≤ channel o z
  channel_sum : ∀ o, ∑ z, channel o z = 1

namespace ReportingModel
variable (E : ReportingModel M O Z)

def raw (o : O) : M → ℝ := fun m => E.likelihood m o

def joint (o : O) (z : Z) : M → ℝ := fun m => E.likelihood m o * E.channel o z

def report (z : Z) : M → ℝ := fun m => ∑ o, E.joint o z m

omit [Fintype M] in
theorem joint_nonneg (o : O) (z : Z) (m : M) : 0 ≤ E.joint o z m :=
  mul_nonneg (E.likelihood_nonneg m o) (E.channel_nonneg o z)

omit [Fintype M] in
theorem report_nonneg (z : Z) (m : M) : 0 ≤ E.report z m :=
  Finset.sum_nonneg (fun o _ => E.joint_nonneg o z m)

omit [Fintype M] in
theorem report_sum (m : M) : ∑ z, E.report z m = 1 := by
  unfold report joint
  rw [Finset.sum_comm]
  simp_rw [← Finset.mul_sum, E.channel_sum, mul_one]
  exact E.likelihood_sum m

theorem joint_mass (p : M → ℝ) (o : O) (z : Z) :
    evidence p (E.joint o z) = E.channel o z * evidence p (E.raw o) := by
  have hf : E.joint o z = fun m => E.channel o z * E.raw o m := by
    funext m; exact mul_comm _ _
  rw [hf, evidence_scale]

theorem report_mass (p : M → ℝ) (z : Z) :
    evidence p (E.report z) = ∑ o, evidence p (E.joint o z) := by
  simp only [evidence, mass, weights, report, Finset.sum_mul]
  exact Finset.sum_comm

theorem joint_le_report (p : M → ℝ) (hp : ∀ m, 0 ≤ p m) (o : O) (z : Z) :
    evidence p (E.joint o z) ≤ evidence p (E.report z) := by
  rw [E.report_mass]
  exact Finset.single_le_sum
    (fun o' _ => evidence_nonneg p _ hp (E.joint_nonneg o' z)) (Finset.mem_univ o)

theorem positive_pair (p : M → ℝ) (hp : ∀ m, 0 ≤ p m) (o : O) (z : Z)
    (h : 0 < evidence p (E.joint o z)) :
    0 < E.channel o z ∧ 0 < evidence p (E.raw o) ∧ 0 < evidence p (E.report z) := by
  have he := h
  rw [E.joint_mass] at he
  have hn := evidence_nonneg p (E.raw o) hp (fun m => E.likelihood_nonneg m o)
  have hc := E.channel_nonneg o z
  constructor
  · exact lt_of_le_of_ne hc (fun hz => by rw [← hz, zero_mul] at he; exact (lt_irrefl 0) he)
  constructor
  · exact lt_of_le_of_ne hn (fun hz => by rw [← hz, mul_zero] at he; exact (lt_irrefl 0) he)
  · exact lt_of_lt_of_le h (E.joint_le_report p hp o z)

theorem joint_update_eq_raw (p : M → ℝ) (o : O) (z : Z)
    (hb : E.channel o z ≠ 0) : update p (E.joint o z) = update p (E.raw o) := by
  have hf : E.joint o z = fun m => E.channel o z * E.raw o m := by
    funext m; exact mul_comm _ _
  rw [hf, update_scale p (E.raw o) _ hb]

/-- Equality on every positive-probability pair in the actual coupling. -/
def PreservesAt (p : M → ℝ) : Prop :=
  ∀ o z, 0 < evidence p (E.joint o z) → update p (E.raw o) = update p (E.report z)

def PreservesAll : Prop := ∀ p, IsDist p → E.PreservesAt p

/-- This is an explicit reconstruction kernel, not an existence assumption. -/
def reconstruction [Nonempty O] (p : M → ℝ) (z : Z) (o : O) : ℝ :=
  if 0 < evidence p (E.report z) then
    evidence p (E.joint o z) / evidence p (E.report z)
  else (Fintype.card O : ℝ)⁻¹

def Reconstructs (ρ : Z → O → ℝ) : Prop :=
  (∀ z o, 0 ≤ ρ z o) ∧ (∀ z, ∑ o, ρ z o = 1) ∧
    ∀ m o z, E.joint o z m = E.report z m * ρ z o

theorem reconstruction_nonneg [Nonempty O] (p : M → ℝ) (hp : ∀ m, 0 ≤ p m)
    (z : Z) (o : O) : 0 ≤ E.reconstruction p z o := by
  unfold reconstruction
  split_ifs with hz
  · exact div_nonneg (evidence_nonneg p _ hp (E.joint_nonneg o z)) (le_of_lt hz)
  · positivity

theorem reconstruction_sum [Nonempty O] (p : M → ℝ) (z : Z) :
    ∑ o, E.reconstruction p z o = 1 := by
  unfold reconstruction
  by_cases hz : 0 < evidence p (E.report z)
  · simp only [hz, ↓reduceIte, ← Finset.sum_div, ← E.report_mass]
    exact div_self (ne_of_gt hz)
  · simp only [hz, ↓reduceIte, Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
    have hc : (Fintype.card O : ℝ) ≠ 0 := by exact_mod_cast Fintype.card_ne_zero
    exact mul_inv_cancel₀ hc

/-- Full support is used only to cancel the prior and resolve impossible events modelwise. -/
theorem reconstruction_factor [Nonempty O] (p : M → ℝ) (hp : ∀ m, 0 < p m)
    (hpres : E.PreservesAt p) :
    ∀ m o z, E.joint o z m = E.report z m * E.reconstruction p z o := by
  intro m o z
  have hpn : ∀ m, 0 ≤ p m := fun m => le_of_lt (hp m)
  have hjn := evidence_nonneg p (E.joint o z) hpn (E.joint_nonneg o z)
  have hrn := evidence_nonneg p (E.report z) hpn (E.report_nonneg z)
  by_cases hr : 0 < evidence p (E.report z)
  · simp only [reconstruction, hr, ↓reduceIte]
    by_cases hj : 0 < evidence p (E.joint o z)
    · have hb := (E.positive_pair p hpn o z hj).1
      have hpost : update p (E.joint o z) = update p (E.report z) :=
        (E.joint_update_eq_raw p o z (ne_of_gt hb)).trans (hpres o z hj)
      have he := congrFun hpost m
      change (E.joint o z m * p m) / evidence p (E.joint o z) =
        (E.report z m * p m) / evidence p (E.report z) at he
      have hc := (div_eq_div_iff (ne_of_gt hj) (ne_of_gt hr)).mp he
      have hc' : E.joint o z m * evidence p (E.report z) =
          E.report z m * evidence p (E.joint o z) := by
        apply (mul_right_cancel₀ (ne_of_gt (hp m)))
        nlinarith [hc]
      calc
        E.joint o z m = (E.report z m * evidence p (E.joint o z)) /
            evidence p (E.report z) := (eq_div_iff (ne_of_gt hr)).2 hc'
        _ = E.report z m * (evidence p (E.joint o z) /
            evidence p (E.report z)) := by rw [mul_div_assoc]
    · have hz : evidence p (E.joint o z) = 0 := le_antisymm (le_of_not_gt hj) hjn
      have h0 := likelihood_zero_of_evidence_zero p (E.joint o z) hp (E.joint_nonneg o z) hz
      rw [h0 m, hz, zero_div, mul_zero]
  · have hz : evidence p (E.report z) = 0 := le_antisymm (le_of_not_gt hr) hrn
    have h0 := likelihood_zero_of_evidence_zero p (E.report z) hp (E.report_nonneg z) hz
    have hjz : evidence p (E.joint o z) = 0 :=
      le_antisymm ((E.joint_le_report p hpn o z).trans_eq hz) hjn
    have hj0 := likelihood_zero_of_evidence_zero p (E.joint o z) hp (E.joint_nonneg o z) hjz
    rw [hj0 m, h0 m, zero_mul]

theorem reconstructs_of_full_support [Nonempty O] (p : M → ℝ)
    (hp : ∀ m, 0 < p m) (hpres : E.PreservesAt p) :
    E.Reconstructs (E.reconstruction p) :=
  ⟨E.reconstruction_nonneg p (fun m => le_of_lt (hp m)),
    E.reconstruction_sum p, E.reconstruction_factor p hp hpres⟩

theorem preservesAll_of_reconstructs {ρ : Z → O → ℝ} (hρ : E.Reconstructs ρ) :
    E.PreservesAll := by
  intro p hp o z hj
  have hp' := E.positive_pair p hp.1 o z hj
  have hf : E.joint o z = fun m => ρ z o * E.report z m := by
    funext m; rw [hρ.2.2 m o z, mul_comm]
  have hrho : ρ z o ≠ 0 := by
    intro hz
    have he := hj
    rw [hf, evidence_scale, hz, zero_mul] at he
    exact (lt_irrefl 0) he
  calc
    update p (E.raw o) = update p (E.joint o z) :=
      (E.joint_update_eq_raw p o z (ne_of_gt hp'.1)).symm
    _ = update p (E.report z) := by rw [hf, update_scale p (E.report z) _ hrho]

/-- Core 3.4: one specified full-support probability prior suffices for every prior. -/
theorem all_iff_full_support_prior [Nonempty O] (p : M → ℝ) (hp : IsDist p)
    (hfull : ∀ m, 0 < p m) : E.PreservesAll ↔ E.PreservesAt p := by
  constructor
  · intro h; exact h p hp
  · intro h; exact E.preservesAll_of_reconstructs (E.reconstructs_of_full_support p hfull h)

/-- Core 3.4: all-prior posterior preservation iff a stochastic reconstruction
of the actual joint experiment exists, including impossible retained reports. -/
theorem all_iff_reconstruction [Nonempty M] [Nonempty O] :
    E.PreservesAll ↔ ∃ ρ, E.Reconstructs ρ := by
  constructor
  · intro h
    let p : M → ℝ := fun _ => (Fintype.card M : ℝ)⁻¹
    exact ⟨E.reconstruction p, E.reconstructs_of_full_support p
      (fun _ => uniform_pos (M := M)) (h p uniform_dist)⟩
  · rintro ⟨ρ,hρ⟩; exact E.preservesAll_of_reconstructs hρ

theorem all_iff_exists_full_support [Nonempty M] [Nonempty O] :
    E.PreservesAll ↔ ∃ p, IsDist p ∧ (∀ m, 0 < p m) ∧ E.PreservesAt p := by
  constructor
  · intro h
    exact ⟨_, uniform_dist, (fun _ => uniform_pos (M := M)), h _ uniform_dist⟩
  · rintro ⟨p,hp,hfull,h⟩
    exact (E.all_iff_full_support_prior p hp hfull).mpr h

end ReportingModel
end
end Bayes
end Komorebi.MachineTheory
