import MachineTheory.Transfer
import MachineTheory.Correction
import MachineTheory.Feedback
import Mathlib.Tactic.NormNum
import Mathlib.Data.Fintype.BigOperators

/-! Kernel-checked witnesses and counterexamples, not sampled agent behavior. -/
namespace Komorebi.MachineTheory.Examples
open scoped BigOperators
open Instrument
noncomputable section

abbrev Sensor := Bool × Bool × Bool

def physical (x : Sensor) : Bool := x.1
def display (x : Sensor) : Bool := Bool.xor x.1 x.2.1
def calibrated (x : Sensor) : Bool × Bool := (display x, x.2.1)
def flip (_ : Unit) (x : Sensor) : Sensor := (!x.1, x.2.1, x.2.2)
def displayStep (_ : Unit) (y : Bool) : Bool := !y

theorem sensor_local_transport (a : Unit) (x : Sensor) :
    display (flip a x) = displayStep a (display x) := by
  rcases x with ⟨b, s, n⟩
  cases b <;> cases s <;> rfl

/-- The display is reusable for arbitrarily many flips despite unidentified physical state. -/
theorem sensor_all_words (word : List Unit) (x : Sensor) :
    display (run flip word x) = run displayStep word (display x) := by
  simpa using forward_transport flip displayStep display id sensor_local_transport word x

theorem no_physical_decoder_from_display :
    ¬ ∃ d : Attained display → Bool, ∀ x, d (record display x) = physical x := by
  exact no_decoder_of_collision (false, false, false) (true, true, false) rfl (by decide)

theorem calibrated_recovers_physical (x : Sensor) :
    Bool.xor (calibrated x).1 (calibrated x).2 = physical x := by
  rcases x with ⟨b, s, n⟩
  cases b <;> cases s <;> rfl

theorem calibrated_decoder_exists :
    ∃ d : Attained calibrated → Bool, ∀ x, d (record calibrated x) = physical x := by
  exact ⟨fun h => Bool.xor h.val.1 h.val.2, calibrated_recovers_physical⟩

/-- The order convention is executable: successor then doubling differs from the reverse. -/
def noncommuting (a : Bool) (n : Nat) : Nat := if a then 2 * n else n + 1

theorem action_order_matters :
    run noncommuting [false, true] 1 = 4 ∧ run noncommuting [true, false] 1 = 3 := by
  decide

/-- Exact version of Core counterexample 2.2. -/
def compress (x : ℚ × ℚ) : ℚ := x.1
def reconstruct (z : ℚ) : ℚ × ℚ := (z, 0)
def swap (x : ℚ × ℚ) : ℚ × ℚ := (x.2, x.1)

theorem hidden_return_counterexample :
    compress (swap (reconstruct 1)) = 0 ∧
    compress (swap (swap (reconstruct 1))) = 1 ∧
    compress (swap (reconstruct (compress (swap (reconstruct 1))))) = 0 := by
  norm_num [compress, reconstruct, swap]

/-- Local agreement at zero is not enough when an action leaves that domain. -/
def partialRead (n : Nat) : Nat := if n ≤ 1 then 0 else 1

theorem invariant_domain_is_necessary :
    partialRead (Nat.succ 0) = 0 ∧ partialRead (Nat.succ (Nat.succ 0)) ≠ 0 := by
  decide

def candidatesV : Set Sensor := {x | x.1 = x.2.1}
def candidatesW : Set Sensor := {x | x.1 ≠ x.2.1}
def conventionZero : Set Sensor := {x | x.2.1 = false}

theorem same_present_target : physical '' candidatesV = physical '' candidatesW := by
  ext b
  have hv : b ∈ physical '' candidatesV := ⟨(b, b, false), rfl, rfl⟩
  have hw : b ∈ physical '' candidatesW := by
    refine ⟨(b, !b, false), ?_, rfl⟩
    change b ≠ !b
    cases b <;> decide
  exact ⟨fun _ => hw, fun _ => hv⟩

theorem corrected_target_V : physical '' (candidatesV ∩ conventionZero) = {false} := by
  ext b
  constructor
  · rintro ⟨⟨b', s, n⟩, ⟨hv, he⟩, hb⟩
    change b' = s at hv
    change s = false at he
    change b' = b at hb
    exact hb.symm.trans (hv.trans he)
  · intro hb
    have hb' : b = false := hb
    subst b
    exact ⟨(false, false, false), ⟨rfl, rfl⟩, rfl⟩

theorem corrected_target_W : physical '' (candidatesW ∩ conventionZero) = {true} := by
  ext b
  constructor
  · rintro ⟨⟨b', s, n⟩, ⟨hw, he⟩, hb⟩
    change b' ≠ s at hw
    change s = false at he
    change b' = b at hb
    subst s
    subst b
    cases b' <;> simp_all
  · intro hb
    have hb' : b = true := hb
    subst b
    exact ⟨(true, false, false), ⟨by change true ≠ false; decide, rfl⟩, rfl⟩

/-- Correct target marginals are insufficient memory for a later calibration. -/
theorem present_target_does_not_preserve_correction :
    physical '' candidatesV = physical '' candidatesW ∧
    physical '' (candidatesV ∩ conventionZero) ≠ physical '' (candidatesW ∩ conventionZero) := by
  refine ⟨same_present_target, ?_⟩
  rw [corrected_target_V, corrected_target_W]
  intro h
  have : false ∈ ({true} : Set Bool) := h ▸ (by simp : false ∈ ({false} : Set Bool))
  simp at this

/-- Two normalized joint kernels with the same separate marginals. -/
def correlated : Unit → Bool → Bool → Bool → ℝ :=
  fun _ o y _ => if y = o then 1 / 2 else 0

def anticorrelated : Unit → Bool → Bool → Bool → ℝ :=
  fun _ o y _ => if y = !o then 1 / 2 else 0

def correlatedLaw : Law Bool Unit Bool where
  kernel := correlated
  nonnegative _ o y _ := by unfold correlated; split_ifs <;> norm_num
  normalized _ _ := by norm_num [correlated, Fintype.sum_bool]

def anticorrelatedLaw : Law Bool Unit Bool where
  kernel := anticorrelated
  nonnegative _ o y _ := by unfold anticorrelated; split_ifs <;> norm_num
  normalized _ _ := by norm_num [anticorrelated, Fintype.sum_bool]

theorem equal_transition_marginals (y x : Bool) :
    (∑ o, correlated () o y x) = ∑ o, anticorrelated () o y x := by
  cases y <;> norm_num [correlated, anticorrelated, Fintype.sum_bool]

theorem equal_report_marginals (o x : Bool) :
    (∑ y, correlated () o y x) = ∑ y, anticorrelated () o y x := by
  cases o <;> norm_num [correlated, anticorrelated, Fintype.sum_bool]

/-- Same transition/report marginals, but opposite positive-report posteriors. -/
theorem joint_marginal_counterexample :
    mass (applyKernel (correlated () true) (basis false)) = 1 / 2 ∧
    mass (applyKernel (anticorrelated () true) (basis false)) = 1 / 2 ∧
    normalize (applyKernel (correlated () true) (basis false)) true = 1 ∧
    normalize (applyKernel (anticorrelated () true) (basis false)) true = 0 := by
  norm_num [mass, applyKernel, normalize, basis, correlated, anticorrelated, Fintype.sum_bool]

theorem no_posterior_for_zero_mass : posterior? (fun _ : Bool => (0 : ℝ)) = none := by
  simp [posterior?, mass]

/-- Within one instrument, a hidden bit changes the report/successor association. -/
abbrev PairState := Bool × Bool

def mixedKernel : Unit → Bool → PairState → PairState → ℝ :=
  fun _ o y x => if y.2 = false ∧ y.1 = Bool.xor o x.2 then 1 / 2 else 0

def mixedLaw : Law PairState Unit Bool where
  kernel := mixedKernel
  nonnegative _ o y x := by unfold mixedKernel; split_ifs <;> norm_num
  normalized _ x := by
    rcases x with ⟨v, h⟩
    cases h <;> norm_num [mixedKernel, Fintype.sum_prod_type, Fintype.sum_bool]

def visible (x : PairState) : Bool := x.1

theorem visible_surjective : Function.Surjective visible := fun b => ⟨(b, false), rfl⟩

/-- Exact obstruction to a quotient despite separately correct marginals. -/
theorem mixed_fiber_failure : ¬ FiberCriterion visible mixedLaw.kernel := by
  intro h
  have he := h () true true (false, false) (false, true) rfl
  norm_num [mixedLaw, mixedKernel, visible, Fintype.sum_prod_type, Fintype.sum_bool] at he

theorem no_joint_quotient_for_lost_association :
    ¬ ∃ L : Law Bool Unit Bool,
      ∀ a o, Intertwines visible (mixedLaw.kernel a o) (L.kernel a o) := by
  intro h
  exact mixed_fiber_failure ((quotient_exists_iff visible visible_surjective mixedLaw).mp h)

/-- A nontrivial many-to-one positive example: hidden input does not affect the instrument. -/
def insensitiveKernel : Unit → Bool → PairState → PairState → ℝ :=
  fun _ o y x => if y.2 = x.2 ∧ y.1 = !x.1 ∧ o = y.1 then 1 else 0

def insensitiveLaw : Law PairState Unit Bool where
  kernel := insensitiveKernel
  nonnegative _ o y x := by unfold insensitiveKernel; split_ifs <;> norm_num
  normalized _ x := by
    rcases x with ⟨v, h⟩
    cases v <;> cases h <;>
      norm_num [insensitiveKernel, Fintype.sum_prod_type, Fintype.sum_bool] <;> decide

theorem insensitive_fiber_closed : FiberCriterion visible insensitiveLaw.kernel := by
  intro a o z x y h
  rcases x with ⟨v, n⟩
  rcases y with ⟨v', n'⟩
  change v = v' at h
  subst v'
  cases v <;> cases n <;> cases n' <;> cases z <;> cases o <;>
    norm_num [insensitiveLaw, insensitiveKernel, visible,
      Fintype.sum_prod_type, Fintype.sum_bool] <;> decide

/-- Its hidden coordinate is discarded without imposing a horizon on feedback. -/
theorem insensitive_feedback (g : Policy Unit Bool) (p : PairState → ℝ)
    (events : History Unit Bool) :
    let L := coarseLaw visible visible_surjective insensitiveLaw
    mass (evolve insensitiveLaw.kernel g.probability [] events p) =
      mass (evolve L.kernel g.probability [] events (push visible p)) ∧
    Option.map (push visible) (posterior? (evolve insensitiveLaw.kernel g.probability [] events p)) =
      posterior? (evolve L.kernel g.probability [] events (push visible p)) :=
  quotient_feedback_law visible visible_surjective insensitiveLaw insensitive_fiber_closed g p events

end
end Komorebi.MachineTheory.Examples
