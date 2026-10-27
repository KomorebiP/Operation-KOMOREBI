import MachineTheory

/-! Independently restated source-facing types, checked against the delivered endpoints. -/
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision
open scoped BigOperators
noncomputable section

section Conditioning
variable {X Z : Type*} [Fintype X] [Fintype Z] [DecidableEq X] [DecidableEq Z]
variable (p q : X → ℝ) (hp : IsDist p) (hq : IsDist q) (E : Finset X)
example (hEp : 0 < mass (restrict E p)) (hEq : 0 < mass (restrict E q)) :
    (∑ x, |normalize (restrict E p) x-normalize (restrict E q) x|)/2 ≤
      min 1 (tv p q/max (mass (restrict E p)) (mass (restrict E q))) :=
  condition_bound E p q hp hq hEp hEq
example (d : ℝ) (hd : tv p q ≤ d) (he : d < mass (restrict E p)) :
    0 < mass (restrict E q) := event_positive E p q hp hq d hd he
example (f : X → Z) (hEp : 0 < mass (restrict E p)) (hEq : 0 < mass (restrict E q)) :
    tv (push f (normalize (restrict E p))) (push f (normalize (restrict E q))) ≤
      min 1 (tv p q/max (mass (restrict E p)) (mass (restrict E q))) :=
  conditional_output_bound f E p q hp hq hEp hEq _ le_rfl
end Conditioning

section History
universe u
variable {X Z A O : Type u} [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
  [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
variable (π : X → Z) (K : Nat → Law X A O) (L : Nat → Law Z A O) (g : Policy A O)
  (p : X → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
  (δ : ℝ) (ε : Nat → ℝ) (h0 : tv (push π p) q ≤ δ)
  (hε : ∀ n a x, tv (push (fun t : O × X => (t.1,π t.2)) (fun t => (K n).kernel a t.1 t.2 x))
    (fun t : O × Z => (L n).kernel a t.1 t.2 (π x)) ≤ ε n)
example (H : Nat) :
    (∑ t, |push (project π H) (law K g p H) t-law L g q H t|)/2 ≤
      min 1 (δ+∑ n ∈ Finset.range H, ε n) :=
  whole_history_bound π K L g p q hp hq δ ε h0 hε H
example (H : Nat) : IsDist (push (project π H) (law K g p H)) :=
  push_dist _ _ (law_dist K g p hp H)
end History

section Selection
variable {I X : Type*} [Fintype X]
variable (P Q : I → X → ℝ) (loss : I → X → ℝ) (S : Finset I) (B d : ℝ) (hB : 0 ≤ B)
  (hP : ∀ i ∈ S, IsDist (P i)) (hQ : ∀ i ∈ S, IsDist (Q i))
  (hL : ∀ i ∈ S, ∀ x, 0 ≤ loss i x ∧ loss i x ≤ B)
  (hD : ∀ i ∈ S, tv (P i) (Q i) ≤ d)
example (chosen best : I) (hc : chosen ∈ S) (hb : best ∈ S)
    (hopt : ∀ i ∈ S, (∑ x, loss chosen x*Q chosen x) ≤ ∑ x, loss i x*Q i x) :
    (∑ x, loss chosen x*P chosen x)-(∑ x, loss best x*P best x) ≤ min B (2*B*d) :=
  uniform_policy_regret P Q loss S B d hB hP hQ hL hD chosen best hc hb hopt
end Selection

#check ApproximationExamples.sensor_all_history_error
#check ApproximationExamples.checked_selected_regret
#check ApproximationExamples.unequal_mass_sharp
#check ApproximationExamples.reset_full_history_distance
#check ApproximationExamples.reset_final_states_agree
end
