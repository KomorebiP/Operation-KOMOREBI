import MachineTheory.Refinement
import Mathlib.Tactic.FinCases
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Algebra.BigOperators.Fin

/-! Kernel-checked finite witnesses for Block 02. All numerical probabilities are
exact rationals interpreted in the reals. There is no sampling or external evaluator. -/
namespace Komorebi.MachineTheory.Block02Examples
open scoped BigOperators
open Instrument Bayes Bayes.ReportingModel BayesianLumping Refinement
noncomputable section

/-- The sensor reveals the model bit, then the channel deletes the entire reading. -/
def erased : ReportingModel Bool Bool Unit where
  likelihood m o := if o = m then 1 else 0
  likelihood_nonneg m o := by split_ifs <;> norm_num
  likelihood_sum m := by cases m <;> norm_num
  channel _ _ := 1
  channel_nonneg _ _ := by norm_num
  channel_sum _ := by simp

def fair : Bool → ℝ := fun _ => 1/2

theorem fair_is_dist : IsDist fair := by norm_num [IsDist, fair, mass]

/-- A prior concentrated on one model cannot reveal the lost distinction. -/
theorem supported_prior_misses_loss : erased.PreservesAt (basis false) := by
  intro o z h
  cases z
  cases o
  · funext m; cases m <;>
      norm_num [update, normalize, mass, weights, raw, report, joint, erased, basis]
  · norm_num [evidence, mass, weights, joint, erased, basis] at h

/-- The same channel fails for a full-support prior, so it fails the all-prior contract. -/
theorem erased_not_preserves_all : ¬ erased.PreservesAll := by
  intro h
  have he := h fair fair_is_dist false () (by
    norm_num [evidence, mass, weights, joint, erased, fair])
  have h0 := congrFun he false
  norm_num [update, normalize, mass, weights, raw, report, joint, erased, fair] at h0

theorem erased_has_no_actual_reconstruction : ¬ ∃ ρ, erased.Reconstructs ρ := by
  intro h
  exact erased_not_preserves_all (erased.all_iff_reconstruction.mpr h)

/-- A noisy bit accompanied by an independent fair flag. -/
def flagged : ReportingModel Bool (Bool × Bool) Bool where
  likelihood m o := if o.1 = m then 3/8 else 1/8
  likelihood_nonneg m o := by split_ifs <;> norm_num
  likelihood_sum m := by cases m <;> norm_num [Fintype.sum_prod_type]
  channel o z := if o.1 = z then 1 else 0
  channel_nonneg o z := by split_ifs <;> norm_num
  channel_sum o := by rcases o with ⟨b,f⟩; cases b <;> norm_num

def flagReconstruction (z : Bool) (o : Bool × Bool) : ℝ :=
  if o.1 = z then 1/2 else 0

theorem flagged_reconstructs : flagged.Reconstructs flagReconstruction := by
  refine ⟨?_, ?_, ?_⟩
  · intro z o; unfold flagReconstruction; split_ifs <;> norm_num
  · intro z; cases z <;> norm_num [flagReconstruction, Fintype.sum_prod_type]
  · intro m o z; rcases o with ⟨b,f⟩
    cases m <;> cases b <;> cases f <;> cases z <;>
      norm_num [joint, report, flagged, flagReconstruction, Fintype.sum_prod_type]

theorem flag_can_be_discarded_for_every_prior : flagged.PreservesAll :=
  flagged.preservesAll_of_reconstructs flagged_reconstructs

/-- A retained report that is impossible under every model still gets a normalized
reconstruction row. It does not get an invented posterior. -/
def unusedReport : ReportingModel Bool Unit Bool where
  likelihood _ _ := 1
  likelihood_nonneg _ _ := by norm_num
  likelihood_sum _ := by simp
  channel _ z := if z then 0 else 1
  channel_nonneg _ z := by cases z <;> norm_num
  channel_sum _ := by norm_num

theorem impossible_report_reconstruction_row :
    unusedReport.Reconstructs (fun _ _ => 1) := by
  refine ⟨by intros; norm_num, by intros; simp, ?_⟩
  intro m o z; cases o; cases z <;> norm_num [joint, report, unusedReport]

theorem impossible_report_has_no_posterior :
    posterior? (weights fair (unusedReport.report true)) = none := by
  norm_num [posterior?, mass, weights, report, joint, unusedReport, fair]

/-- Nonconstant likelihoods can commute with a one-block probability record.
This is why Core 3.5 protects at least two blocks. -/
def nonconstantLikelihood (b : Bool) : ℝ := if b then 3 else 1

theorem one_block_still_corrects (p : Bool → ℝ) (hp : IsDist p) :
    push (fun _ : Bool => ()) (update p nonconstantLikelihood) =
      update (push (fun _ : Bool => ()) p) (fun _ : Unit => 1) := by
  have he : p false + p true = 1 := by simpa [mass, add_comm] using hp.2
  have hn0 := hp.1 false
  have hn1 := hp.1 true
  have hz : p false + 3 * p true ≠ 0 := by nlinarith
  funext z; cases z
  have hz' : 3 * p true + p false ≠ 0 := by nlinarith
  have hs : p true + p false = 1 := by linarith
  simp [update, normalize, weights, push, mass, nonconstantLikelihood, ← add_div, hz', hs]

theorem one_block_likelihood_not_constant : nonconstantLikelihood false ≠ nonconstantLikelihood true := by
  norm_num [nonconstantLikelihood]

/-- Four states encoded 00,01,10,11, with successors 00,10,11,11.
A future distinction propagates backwards through two refinement rounds. -/
abbrev Four := Bool × Bool

def successor : Four → Four
  | (false,false) => (false,false)
  | (false,true) => (true,false)
  | (true,_) => (true,true)

def fourKernel (_ : Unit) (y x : Four) : ℝ := if y = successor x then 1 else 0

def mandatory : Setoid Four := Setoid.ker (fun x => x.1 && x.2)

def afterOne : Setoid Four := Setoid.ker (fun x : Four => if x.1 then x else (false,false))

@[simp] theorem mandatory_rel (x y : Four) :
    mandatory x y ↔ (x.1 && x.2) = (y.1 && y.2) := Iff.rfl

@[simp] theorem afterOne_rel (x y : Four) :
    afterOne x y ↔ (if x.1 then x else (false,false)) =
      (if y.1 then y else (false,false)) := Iff.rfl

theorem refinement_first_round : step fourKernel mandatory = afterOne := by
  apply Setoid.ext
  rintro ⟨x₁,x₂⟩ ⟨y₁,y₂⟩
  rw [step_rel_iff]
  cases x₁ <;> cases x₂ <;> cases y₁ <;> cases y₂ <;>
    norm_num [fourKernel, successor, Fintype.sum_prod_type, Prod.forall]

theorem refinement_second_round : step fourKernel afterOne = ⊥ := by
  apply Setoid.ext
  rintro ⟨x₁,x₂⟩ ⟨y₁,y₂⟩
  rw [step_rel_iff]
  cases x₁ <;> cases x₂ <;> cases y₁ <;> cases y₂ <;>
    norm_num [fourKernel, successor, Fintype.sum_prod_type, Prod.forall]

theorem discrete_is_stable : Stable fourKernel (⊥ : Setoid Four) := by
  apply (stable_iff fourKernel ⊥).mpr
  intro x y h
  have he : x = y := h
  subst y; rfl

theorem two_strict_rounds :
    Refinement.sequence fourKernel mandatory 1 ≠ mandatory ∧
    Refinement.sequence fourKernel mandatory 2 ≠ Refinement.sequence fourKernel mandatory 1 ∧
    Stable fourKernel (Refinement.sequence fourKernel mandatory 2) := by
  have hfirst : afterOne ≠ mandatory := by
    intro he
    have h : mandatory (false,false) (true,false) := by change false = false; rfl
    rw [← he] at h
    norm_num at h
  have hsecond : (⊥ : Setoid Four) ≠ afterOne := by
    intro he
    have h : afterOne (false,false) (false,true) := by
      change (false,false) = (false,false); rfl
    rw [← he] at h
    exact (by decide : ((false,false) : Four) ≠ (false,true)) h
  simpa only [Refinement.sequence, refinement_first_round, refinement_second_round] using
    And.intro hfirst (And.intro hsecond discrete_is_stable)

/-- Stable dynamics alone do not establish Bayesian closure for a nontrivial partition. -/
theorem likelihood_split_cannot_be_omitted :
    ¬ ∃ g : Bool → ℝ, (∀ b, 0 < g b) ∧
      ∀ p : Four → ℝ, IsDist p →
        push Prod.fst (update p (fun x => nonconstantLikelihood x.2)) =
          update (push Prod.fst p) g := by
  intro h
  have hs : Function.Surjective (Prod.fst : Four → Bool) := fun b => ⟨(b,false),rfl⟩
  have hl : ∀ x : Four, 0 < nonconstantLikelihood x.2 := by
    rintro ⟨b,c⟩; cases c <;> norm_num [nonconstantLikelihood]
  have hn : ∃ u v : Four, u.1 ≠ v.1 := ⟨(false,false),(true,false),by decide⟩
  have he := (fixed_positive_coarse_iff Prod.fst hs
    (fun x : Four => nonconstantLikelihood x.2) hl hn).mp h
      (false,false) (false,true) rfl
  norm_num [nonconstantLikelihood] at he

def fourLaw : Law Four Unit Unit where
  kernel a _ := fourKernel a
  nonnegative a o y x := by unfold fourKernel; split_ifs <;> norm_num
  normalized a x := by
    rcases x with ⟨b,c⟩
    cases b <;> cases c <;> norm_num [fourKernel, successor, Fintype.sum_prod_type] <;> decide

theorem mandatory_nontrivial : ∃ x y : Four, ¬ mandatory x y :=
  ⟨(false,false),(true,true),by simp⟩

/-- The concrete two-round chain has the same operational contract as Core 3.5. -/
theorem discrete_is_only_admissible (P : Setoid Four)
    (hp : Admissible fourLaw (fun _ : Unit => fun _ : Four => (1 : ℝ)) mandatory P) :
    P = ⊥ := by
  have he := (admissible_iff fourLaw (fun _ : Unit => fun _ : Four => (1 : ℝ))
    mandatory P (by intros; norm_num) mandatory_nontrivial).mp hp
  have hI : initial mandatory (fun _ : Unit => fun _ : Four => (1 : ℝ)) = mandatory := by
    apply Setoid.ext; intro x y
    change (mandatory x y ∧ (fun _ : Unit => (1 : ℝ)) = fun _ : Unit => (1 : ℝ)) ↔ _
    simp
  rw [hI] at he
  have h2 := stable_refines_sequence (transition fourLaw) he.1 he.2 2
  have hK : transition fourLaw = fourKernel := rfl
  rw [hK] at h2
  simp only [Refinement.sequence, refinement_first_round, refinement_second_round] at h2
  exact le_antisymm h2 bot_le

end
end Komorebi.MachineTheory.Block02Examples
