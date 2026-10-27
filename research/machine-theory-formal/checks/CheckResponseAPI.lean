import MachineTheory

/-! Independent source-facing restatements. The risk sums, bound and finite minimum
are explicitly named here instead of trusting a theorem's printed title. -/
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory
open scoped BigOperators
noncomputable section
variable {X A V : Type*} [Fintype X] [PseudoMetricSpace V]
variable (p q : X → ℝ) (v w : X → V) (loss : A → V → ℝ)
    (hp : IsDist p) (hq : IsDist q) (e K d : ℝ) (hK : 0 ≤ K)
    (he : tv p q ≤ e) (hd : ∀ x, dist (v x) (w x) ≤ d)
    (hlip : ∀ a y z, |loss a y-loss a z| ≤ K*dist y z)
    (hl : ∀ a y, 0 ≤ loss a y ∧ loss a y ≤ 1)

example (a : A) :
    |(∑ x, loss a (v x)*p x)-(∑ x, loss a (w x)*q x)| ≤ min 1 (e+K*d) :=
  decision_error_global p q v w loss hp hq e K d hK he hd hlip hl a

example (S : Finset A) (hS : S.Nonempty) :
    ∃ a ∈ S, ∃ b ∈ S,
      (∀ c ∈ S, (∑ x, loss a (w x)*q x) ≤ ∑ x, loss c (w x)*q x) ∧
      (∀ c ∈ S, (∑ x, loss b (v x)*p x) ≤ ∑ x, loss c (v x)*p x) ∧
      (∑ x, loss a (v x)*p x)-(∑ x, loss b (v x)*p x) ≤ min 1 (2*min 1 (e+K*d)) :=
  metric_minimizers_exist p q v w loss S hS hp hq e K d hK he hd
    (fun a _ x => hlip a (v x) (w x)) (fun a _ x => hl a (v x)) (fun a _ x => hl a (w x))

example (S : Finset A) (hS : S.Nonempty) (chosen : A) (hc : chosen ∈ S)
    (hopt : ∀ a ∈ S, (∑ x, loss chosen (w x)*q x) ≤ ∑ x, loss a (w x)*q x) :
    (∑ x, loss chosen (v x)*p x)-Planning.finiteMin S hS (fun a => ∑ x, loss a (v x)*p x) ≤
      min 1 (2*min 1 (e+K*d)) :=
  regret_to_minimum p q v w loss S hS hp (allowance e K d)
    (fun a _ x => hl a (v x))
    (fun a _ => decision_error_global p q v w loss hp hq e K d hK he hd hlip hl a) chosen hc hopt

example (S : Finset A) (chosen : A) (hc : chosen ∈ S)
    (gap : ∀ a ∈ S, a ≠ chosen →
      (∑ x, loss chosen (w x)*q x)+2*min 1 (e+K*d) < ∑ x, loss a (w x)*q x) :
    (∀ a ∈ S, a ≠ chosen → (∑ x, loss chosen (v x)*p x) < ∑ x, loss a (v x)*p x) ∧
    (∀ a ∈ S, (∀ b ∈ S, (∑ x, loss a (v x)*p x) ≤ ∑ x, loss b (v x)*p x) → a=chosen) :=
  unique_minimizer_transfer p q v w loss S (allowance e K d) chosen hc
    (fun a _ => decision_error_global p q v w loss hp hq e K d hK he hd hlip hl a) gap

example (chosen : A) (τ : ℝ)
    (bound : (∑ x, loss chosen (w x)*q x)+min 1 (e+K*d) ≤ τ) :
    (∑ x, loss chosen (v x)*p x) ≤ τ :=
  risk_threshold p q v w loss chosen (allowance e K d) τ
    (decision_error_global p q v w loss hp hq e K d hK he hd hlip hl chosen) bound

section Conditioning
variable {H Y : Type*} [Fintype H] [Fintype Y] [DecidableEq H] [DecidableEq Y]
variable (P Q : H → ℝ) (r : Y → ℝ) (hP : IsDist P) (hQ : IsDist Q) (hr : IsDist r)
variable (f : H → Y) (E : Finset H) (hE : 0 < mass (restrict E P)) (hE' : 0 < mass (restrict E Q))
variable (δ s : ℝ) (hδ : tv P Q ≤ δ) (hs : tv (push f (normalize (restrict E Q))) r ≤ s)
example : tv (push f (normalize (restrict E P))) r ≤
    min 1 (min 1 (δ/max (mass (restrict E P)) (mass (restrict E Q)))+s) :=
  conditioning_and_storage f E P Q r hP hQ hr hE hE' δ s hδ hs
end Conditioning

example : responseRisk ResponseExamples.truePosterior ResponseExamples.targetResponse
    ResponseExamples.scalarLoss true ≤ 713/2500 := ResponseExamples.sensor_risk_upper_certificate
example : ∀ a : Bool, a ≠ true →
    responseRisk ResponseExamples.truePosterior ResponseExamples.targetResponse ResponseExamples.scalarLoss true <
    responseRisk ResponseExamples.truePosterior ResponseExamples.targetResponse ResponseExamples.scalarLoss a :=
  ResponseExamples.sensor_true_unique_from_certificate
#check DecisionHistory.history_conditioned_response_error
#check DecisionHistory.history_response_error
#check ResponseDecision.expected_response_error
#check ResponseDecision.approximate_optimizer_regret
end
