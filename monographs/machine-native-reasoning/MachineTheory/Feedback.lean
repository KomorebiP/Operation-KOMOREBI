import MachineTheory.Instrument

/-! Core 3.6, arbitrary finite feedback histories and normalization.
The same history-dependent policy is used by both realizations. Its probabilities
may depend on all prior observed actions/reports, but not on the hidden state.
-/
namespace Komorebi.MachineTheory.Instrument
open scoped BigOperators
noncomputable section
variable {X Z A O : Type*} [Fintype X] [Fintype Z]

abbrev History (A O : Type*) := List (A × O)

structure Policy (A O : Type*) [Fintype A] where
  probability : History A O → A → ℝ
  nonnegative : ∀ h a, 0 ≤ probability h a
  normalized : ∀ h, ∑ a, probability h a = 1

/-- Unnormalized state of one named future history, from a specified observed past. -/
def evolve (K : A → O → X → X → ℝ) (g : History A O → A → ℝ) :
    History A O → History A O → (X → ℝ) → (X → ℝ)
  | _, [], p => p
  | past, (a, o) :: tail, p =>
      evolve K g (past ++ [(a, o)]) tail (scale (g past a) (applyKernel (K a o) p))

/-- The full joint instrument, not its separate marginals, propagates the same compressed history. -/
theorem feedback_unnormalized [DecidableEq Z] (π : X → Z)
    (K : A → O → X → X → ℝ) (L : A → O → Z → Z → ℝ)
    (g : History A O → A → ℝ) (h : ∀ a o, Intertwines π (K a o) (L a o))
    (past events : History A O) (p : X → ℝ) :
    push π (evolve K g past events p) = evolve L g past events (push π p) := by
  induction events generalizing past p with
  | nil => rfl
  | cons event events ih =>
    obtain ⟨a, o⟩ := event
    simp only [evolve]
    rw [ih, push_scale, h a o]

/-- Equality of the probabilities of every finite joint action/report history. -/
theorem feedback_history_mass [DecidableEq Z] (π : X → Z)
    (K : A → O → X → X → ℝ) (L : A → O → Z → Z → ℝ)
    (g : History A O → A → ℝ) (h : ∀ a o, Intertwines π (K a o) (L a o))
    (past events : History A O) (p : X → ℝ) :
    mass (evolve K g past events p) = mass (evolve L g past events (push π p)) := by
  rw [← mass_push π, feedback_unnormalized π K L g h]

/-- Impossible histories are `none` on both sides; positive histories have equal coarse posteriors. -/
theorem feedback_posterior [DecidableEq Z] (π : X → Z)
    (K : A → O → X → X → ℝ) (L : A → O → Z → Z → ℝ)
    (g : History A O → A → ℝ) (h : ∀ a o, Intertwines π (K a o) (L a o))
    (past events : History A O) (p : X → ℝ) :
    Option.map (push π) (posterior? (evolve K g past events p)) =
      posterior? (evolve L g past events (push π p)) := by
  unfold posterior?
  rw [feedback_history_mass π K L g h]
  split_ifs
  · simp only [Option.map_some]
    congr 1
    rw [push_normalize, feedback_unnormalized π K L g h]
  · rfl

variable [Fintype O]

/-- Summing over reports returns exactly the input mass of a normalized instrument. -/
theorem report_mass_total (K : Law X A O) (a : A) (p : X → ℝ) :
    (∑ o, mass (applyKernel (K.kernel a o) p)) = mass p := by
  unfold mass applyKernel
  calc
    (∑ o, ∑ y, ∑ x, K.kernel a o y x * p x) =
        ∑ o, ∑ x, ∑ y, K.kernel a o y x * p x := by
      apply Finset.sum_congr rfl
      intro o _
      exact Finset.sum_comm
    _ = ∑ x, ∑ o, ∑ y, K.kernel a o y x * p x := Finset.sum_comm
    _ = ∑ x, (∑ o, ∑ y, K.kernel a o y x) * p x := by
      simp only [Finset.sum_mul]
    _ = ∑ x, p x := by simp_rw [K.normalized, one_mul]

variable [Fintype A]

/-- Sum over all possible future action/report branches of the declared depth. -/
def totalHistoryMass (K : Law X A O) (g : Policy A O) :
    Nat → History A O → (X → ℝ) → ℝ
  | 0, _, p => mass p
  | n + 1, past, p => ∑ a, ∑ o,
      totalHistoryMass K g n (past ++ [(a, o)])
        (scale (g.probability past a) (applyKernel (K.kernel a o) p))

/-- The policy and instrument produce a normalized finite-history law, not just matching weights. -/
theorem totalHistoryMass_eq (K : Law X A O) (g : Policy A O)
    (n : Nat) (past : History A O) (p : X → ℝ) :
    totalHistoryMass K g n past p = mass p := by
  induction n generalizing past p with
  | zero => rfl
  | succ n ih =>
    simp only [totalHistoryMass, ih, mass_scale]
    simp_rw [← Finset.mul_sum, report_mass_total, ← Finset.sum_mul]
    rw [g.normalized, one_mul]

/-- Nonnegativity is maintained along every real observation history. -/
theorem evolve_nonnegative (K : Law X A O) (g : Policy A O)
    (past events : History A O) (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) :
    ∀ x, 0 ≤ evolve K.kernel g.probability past events p x := by
  induction events generalizing past p with
  | nil => exact hp
  | cons event events ih =>
    obtain ⟨a, o⟩ := event
    apply ih
    intro x
    exact mul_nonneg (g.nonnegative past a)
      (apply_nonnegative _ (K.nonnegative a o) p hp x)

/-- A positive history produces a genuine normalized posterior. -/
theorem positive_history_posterior_dist (K : Law X A O) (g : Policy A O)
    (past events : History A O) (p : X → ℝ) (hp : IsDist p)
    (hm : 0 < mass (evolve K.kernel g.probability past events p)) :
    IsDist (normalize (evolve K.kernel g.probability past events p)) :=
  normalize_dist _ (evolve_nonnegative K g past events p hp.1) hm

/-- The main Core 3.6 endpoint: constructed coarse instrument, one lawful feedback policy,
all finite histories, equal probabilities, and exactly matched optional posteriors. -/
theorem quotient_feedback_law [DecidableEq Z] (π : X → Z) (hπ : Function.Surjective π)
    (K : Law X A O) (hc : FiberCriterion π K.kernel) (g : Policy A O)
    (p : X → ℝ) (events : History A O) :
    let L := coarseLaw π hπ K
    mass (evolve K.kernel g.probability [] events p) =
      mass (evolve L.kernel g.probability [] events (push π p)) ∧
    Option.map (push π) (posterior? (evolve K.kernel g.probability [] events p)) =
      posterior? (evolve L.kernel g.probability [] events (push π p)) := by
  let L := coarseLaw π hπ K
  have h := coarseLaw_intertwines π hπ K hc
  exact ⟨feedback_history_mass π K.kernel L.kernel g.probability h [] events p,
    feedback_posterior π K.kernel L.kernel g.probability h [] events p⟩

/-- A common observed-history policy may instead issue one of finitely many terminal decisions. -/
structure StoppingPolicy (A O D : Type*) [Fintype A] [Fintype D] where
  continueProb : History A O → A → ℝ
  stopProb : History A O → D → ℝ
  continue_nonnegative : ∀ h a, 0 ≤ continueProb h a
  stop_nonnegative : ∀ h d, 0 ≤ stopProb h d
  normalized : ∀ h, (∑ a, continueProb h a) + (∑ d, stopProb h d) = 1

variable {D : Type*} [Fintype D]

/-- Joint unnormalized state of a complete finite history and its terminal decision. -/
def stoppedState (K : A → O → X → X → ℝ) (g : StoppingPolicy A O D)
    (events : History A O) (d : D) (p : X → ℝ) : X → ℝ :=
  scale (g.stopProb events d) (evolve K g.continueProb [] events p)

/-- Core 3.6's terminal-choice extension uses the same continuation and stopping probabilities. -/
theorem stopped_feedback [DecidableEq Z] (π : X → Z)
    (K : Law X A O) (L : Law Z A O)
    (h : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o))
    (g : StoppingPolicy A O D) (events : History A O) (d : D) (p : X → ℝ) :
    push π (stoppedState K.kernel g events d p) =
      stoppedState L.kernel g events d (push π p) := by
  unfold stoppedState
  rw [push_scale, feedback_unnormalized π K.kernel L.kernel g.continueProb h]

/-- Terminal decisions preserve the probabilities of complete finite records. -/
theorem stopped_history_mass [DecidableEq Z] (π : X → Z)
    (K : Law X A O) (L : Law Z A O)
    (h : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o))
    (g : StoppingPolicy A O D) (events : History A O) (d : D) (p : X → ℝ) :
    mass (stoppedState K.kernel g events d p) =
      mass (stoppedState L.kernel g events d (push π p)) := by
  rw [← mass_push π, stopped_feedback π K L h]

/-- Sum stopped branches and surviving active mass at a finite cutoff.
It deliberately does not assert eventual termination of an arbitrary policy. -/
def stoppedAndSurvivingMass (K : Law X A O) (g : StoppingPolicy A O D) :
    Nat → History A O → (X → ℝ) → ℝ
  | 0, _, p => mass p
  | n + 1, past, p => (∑ d, mass (scale (g.stopProb past d) p)) +
      ∑ a, ∑ o, stoppedAndSurvivingMass K g n (past ++ [(a, o)])
        (scale (g.continueProb past a) (applyKernel (K.kernel a o) p))

theorem stoppedAndSurvivingMass_eq (K : Law X A O) (g : StoppingPolicy A O D)
    (n : Nat) (past : History A O) (p : X → ℝ) :
    stoppedAndSurvivingMass K g n past p = mass p := by
  induction n generalizing past p with
  | zero => rfl
  | succ n ih =>
    simp only [stoppedAndSurvivingMass, ih, mass_scale]
    simp_rw [← Finset.mul_sum, report_mass_total, ← Finset.sum_mul]
    rw [← add_mul, add_comm (∑ d, g.stopProb past d), g.normalized, one_mul]

end
end Komorebi.MachineTheory.Instrument
