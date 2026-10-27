import MachineTheory.ApproximateHistory
import MachineTheory.Planning

/-!
Core 5.6: a uniform same-policy law bound controls selection of a different policy.
The loss for each policy is the same bounded function in the two models. The finite
policy catalogue is shared. Admissibility, absorbing-stop encoding and model truth
are separate premises, not consequences of an expected-loss bound.
-/
namespace Komorebi.MachineTheory.ApproximateDecision
open scoped BigOperators
open Instrument Variation ApproximateHistory
noncomputable section
variable {X I : Type*}

def risk [Fintype X] (p f : X → ℝ) : ℝ := ∑ x, f x * p x

theorem risk_range [Fintype X] (p f : X → ℝ) (hp : IsDist p) (B : ℝ)
    (hf : ∀ x, 0 ≤ f x ∧ f x ≤ B) : 0 ≤ risk p f ∧ risk p f ≤ B := by
  constructor
  · exact Finset.sum_nonneg (fun x _ => mul_nonneg (hf x).1 (hp.1 x))
  · calc
      risk p f ≤ ∑ x, B*p x := Finset.sum_le_sum
        (fun x _ => mul_le_mul_of_nonneg_right (hf x).2 (hp.1 x))
      _ = B := by rw [← Finset.mul_sum]; change B*mass p=B; rw [hp.2, mul_one]

/-- The fixed-policy comparison is established before policy selection is used. -/
theorem same_policy_error [Fintype X] (p q f : X → ℝ)
    (hp : IsDist p) (hq : IsDist q) (B d : ℝ) (hB : 0 ≤ B)
    (hf : ∀ x, 0 ≤ f x ∧ f x ≤ B) (hd : tv p q ≤ d) :
    |risk p f-risk q f| ≤ B*d :=
  (expectation_bound p q f (hp.2.trans hq.2.symm) B hB hf).trans
    (mul_le_mul_of_nonneg_left hd hB)

/-- An explicit lower/upper error interval on each of the same fixed alternatives. -/
theorem regret_from_uniform_error (J Q : I → ℝ) (S : Finset I) (B e : ℝ)
    (hJ : ∀ i ∈ S, 0 ≤ J i ∧ J i ≤ B)
    (he : ∀ i ∈ S, |J i-Q i| ≤ e)
    (chosen comparator : I) (hc : chosen ∈ S) (hr : comparator ∈ S)
    (hopt : ∀ i ∈ S, Q chosen ≤ Q i) :
    J chosen-J comparator ≤ min B (2*e) := by
  apply le_min
  · linarith [(hJ chosen hc).2, (hJ comparator hr).1]
  · have h1 := (abs_le.mp (he chosen hc)).2
    have h2 := (abs_le.mp (he comparator hr)).1
    have h3 := hopt comparator hr
    linarith

/-- Core 5.6, including its range cap, for any declared common finite class. -/
theorem uniform_policy_regret [Fintype X]
    (P Q : I → X → ℝ) (loss : I → X → ℝ) (S : Finset I) (B d : ℝ) (hB : 0 ≤ B)
    (hP : ∀ i ∈ S, IsDist (P i)) (hQ : ∀ i ∈ S, IsDist (Q i))
    (hL : ∀ i ∈ S, ∀ x, 0 ≤ loss i x ∧ loss i x ≤ B)
    (hD : ∀ i ∈ S, tv (P i) (Q i) ≤ d)
    (chosen comparator : I) (hc : chosen ∈ S) (hr : comparator ∈ S)
    (hopt : ∀ i ∈ S, risk (Q chosen) (loss chosen) ≤ risk (Q i) (loss i)) :
    risk (P chosen) (loss chosen)-risk (P comparator) (loss comparator) ≤ min B (2*B*d) := by
  have h := regret_from_uniform_error
    (fun i => risk (P i) (loss i)) (fun i => risk (Q i) (loss i)) S B (B*d)
    (fun i hi => risk_range (P i) (loss i) (hP i hi) B (hL i hi))
    (fun i hi => same_policy_error (P i) (Q i) (loss i) (hP i hi) (hQ i hi) B d hB (hL i hi) (hD i hi))
    chosen comparator hc hr hopt
  simpa only [mul_assoc] using h

/-- The finite common class actually has both minimizers. -/
theorem minimizing_policies_exist [Fintype X]
    (P Q : I → X → ℝ) (loss : I → X → ℝ) (S : Finset I) (hS : S.Nonempty)
    (B d : ℝ) (hB : 0 ≤ B)
    (hP : ∀ i ∈ S, IsDist (P i)) (hQ : ∀ i ∈ S, IsDist (Q i))
    (hL : ∀ i ∈ S, ∀ x, 0 ≤ loss i x ∧ loss i x ≤ B)
    (hD : ∀ i ∈ S, tv (P i) (Q i) ≤ d) :
    ∃ chosen ∈ S, ∃ best ∈ S,
      (∀ i ∈ S, risk (Q chosen) (loss chosen) ≤ risk (Q i) (loss i)) ∧
      (∀ i ∈ S, risk (P best) (loss best) ≤ risk (P i) (loss i)) ∧
      risk (P chosen) (loss chosen)-risk (P best) (loss best) ≤ min B (2*B*d) := by
  obtain ⟨chosen,hc,eqc⟩ := Planning.finiteMin_attained S hS (fun i => risk (Q i) (loss i))
  obtain ⟨best,hb,eqb⟩ := Planning.finiteMin_attained S hS (fun i => risk (P i) (loss i))
  have hmin : ∀ i ∈ S, risk (Q chosen) (loss chosen) ≤ risk (Q i) (loss i) := by
    intro i hi; rw [eqc]; exact Planning.finiteMin_le S hS _ i hi
  refine ⟨chosen,hc,best,hb,hmin,?_,uniform_policy_regret P Q loss S B d hB hP hQ hL hD chosen best hc hb hmin⟩
  intro i hi; rw [eqb]; exact Planning.finiteMin_le S hS _ i hi

/-- A strict approximate gap larger than twice the error preserves the true comparison. -/
theorem robust_gap (J Q : I → ℝ) (i j : I) (e : ℝ)
    (hi : |J i-Q i| ≤ e) (hj : |J j-Q j| ≤ e) (gap : Q i+2*e < Q j) : J i < J j := by
  have h1 := (abs_le.mp hi).2
  have h2 := (abs_le.mp hj).1
  linarith

universe u
variable {S Z A O : Type u}

/-- The first half of Core 5.6 is instantiated by the whole-history theorem, uniformly in the policy. -/
theorem history_policy_error [Fintype S] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq S] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : S → Z) (K : Nat → Law S A O) (L : Nat → Law Z A O)
    (g : Policy A O) (p : S → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
    (δ : ℝ) (ε : Nat → ℝ) (h0 : tv (push π p) q ≤ δ)
    (hε : ∀ n a x, tv (push (reportMap π) (jointRow (K n) a x)) (jointRow (L n) a (π x)) ≤ ε n)
    (H : Nat) (loss : Path Z A O H → ℝ) (B : ℝ) (hB : 0 ≤ B)
    (hL : ∀ h, 0 ≤ loss h ∧ loss h ≤ B) :
    |risk (push (project π H) (law K g p H)) loss-risk (law L g q H) loss| ≤
      B * min 1 (δ + ∑ n ∈ Finset.range H, ε n) :=
  same_policy_error _ _ _ (push_dist _ _ (law_dist K g p hp H)) (law_dist L g q hq H)
    B _ hB hL (whole_history_bound π K L g p q hp hq δ ε h0 hε H)

/-- Two separately chosen policies are compared only after every fixed policy has been transported. -/
theorem history_selected_policy_regret [Fintype S] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq S] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : S → Z) (K : Nat → Law S A O) (L : Nat → Law Z A O)
    (policies : I → Policy A O) (catalogue : Finset I)
    (p : S → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
    (δ : ℝ) (ε : Nat → ℝ) (h0 : tv (push π p) q ≤ δ)
    (hε : ∀ n a x, tv (push (reportMap π) (jointRow (K n) a x)) (jointRow (L n) a (π x)) ≤ ε n)
    (H : Nat) (loss : I → Path Z A O H → ℝ) (B : ℝ) (hB : 0 ≤ B)
    (hL : ∀ i ∈ catalogue, ∀ h, 0 ≤ loss i h ∧ loss i h ≤ B)
    (chosen best : I) (hc : chosen ∈ catalogue) (hb : best ∈ catalogue)
    (hopt : ∀ i ∈ catalogue, risk (law L (policies chosen) q H) (loss chosen) ≤ risk (law L (policies i) q H) (loss i)) :
    risk (push (project π H) (law K (policies chosen) p H)) (loss chosen) -
      risk (push (project π H) (law K (policies best) p H)) (loss best) ≤
      min B (2*B*min 1 (δ + ∑ n ∈ Finset.range H, ε n)) :=
  uniform_policy_regret
    (fun i => push (project π H) (law K (policies i) p H))
    (fun i => law L (policies i) q H) loss catalogue B _ hB
    (fun i _ => push_dist _ _ (law_dist K (policies i) p hp H))
    (fun i _ => law_dist L (policies i) q hq H) hL
    (fun i _ => whole_history_bound π K L (policies i) p q hp hq δ ε h0 hε H)
    chosen best hc hb hopt

end
end Komorebi.MachineTheory.ApproximateDecision
