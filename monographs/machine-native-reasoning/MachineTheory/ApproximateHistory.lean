import MachineTheory.Variation
import MachineTheory.Feedback

/-!
Core 3.8, whole-history approximation.
A path retains every hidden state for mathematical comparison. The policy sees only its
previous actions and reports. Projection retains every coarse state, not just the final one.
Instruments may vary with time, with a separate uniform joint-row defect at each step.
-/
namespace Komorebi.MachineTheory.ApproximateHistory
open scoped BigOperators
open Instrument Variation
noncomputable section
universe u
variable {X Z A O : Type u}

/-- Chronological trace: initial state, followed by action/report/successor triples. -/
@[reducible] def Path (X A O : Type u) : Nat → Type u
  | 0 => X
  | n+1 => Path X A O n × (A × O × X)

instance pathFintype [Fintype X] [Fintype A] [Fintype O] (n : Nat) : Fintype (Path X A O n) := by
  induction n with
  | zero => exact inferInstanceAs (Fintype X)
  | succ n ih =>
    letI := ih
    exact inferInstanceAs (Fintype (Path X A O n × (A × O × X)))

instance pathDecidableEq [DecidableEq X] [DecidableEq A] [DecidableEq O] (n : Nat) :
    DecidableEq (Path X A O n) := by
  induction n with
  | zero => exact inferInstanceAs (DecidableEq X)
  | succ n ih =>
    letI := ih
    exact inferInstanceAs (DecidableEq (Path X A O n × (A × O × X)))

def last : (n : Nat) → Path X A O n → X
  | 0, x => x
  | _+1, h => h.2.2.2

/-- No state coordinate is exposed to this history interface. -/
def observed : (n : Nat) → Path X A O n → History A O
  | 0, _ => []
  | n+1, h => observed n h.1 ++ [(h.2.1,h.2.2.1)]

def reportMap (π : X → Z) (u : O × X) : O × Z := (u.1,π u.2)

def stepMap (π : X → Z) (u : A × O × X) : A × O × Z := (u.1,reportMap π u.2)

def project (π : X → Z) : (n : Nat) → Path X A O n → Path Z A O n
  | 0, x => π x
  | n+1, h => (project π n h.1,stepMap π h.2)

theorem project_last (π : X → Z) (n : Nat) (h : Path X A O n) :
    last n (project π n h) = π (last n h) := by
  cases n <;> rfl

theorem project_observed (π : X → Z) (n : Nat) (h : Path X A O n) :
    observed n (project π n h) = observed n h := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [observed, project, stepMap, reportMap, ih]

def jointRow [Fintype X] [Fintype O] (K : Law X A O) (a : A) (x : X) : O × X → ℝ :=
  fun u => K.kernel a u.1 u.2 x

theorem jointRow_dist [Fintype X] [Fintype O] (K : Law X A O) (a : A) (x : X) :
    IsDist (jointRow K a x) := by
  refine ⟨fun u => K.nonnegative a u.1 u.2 x, ?_⟩
  simpa only [mass, jointRow, Fintype.sum_prod_type] using K.normalized a x

def stepRow [Fintype X] [Fintype A] [Fintype O]
    (K : Law X A O) (g : Policy A O) (past : History A O) (x : X) : A × O × X → ℝ :=
  fun u => g.probability past u.1 * jointRow K u.1 x u.2

theorem stepRow_dist [Fintype X] [Fintype A] [Fintype O]
    (K : Law X A O) (g : Policy A O) (past : History A O) (x : X) :
    IsDist (stepRow K g past x) := by
  constructor
  · intro u
    exact mul_nonneg (g.nonnegative past u.1) (K.nonnegative u.1 u.2.1 u.2.2 x)
  · simp only [mass, stepRow, jointRow, Fintype.sum_prod_type]
    simp_rw [← Finset.mul_sum, K.normalized, mul_one]
    exact g.normalized past

/-- Append an observed step and its true successor to the complete path. -/
def pathKernel [Fintype X] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq A] [DecidableEq O]
    (K : Law X A O) (g : Policy A O) (n : Nat) : Kernel (Path X A O n) (Path X A O (n+1)) where
  entry t h := push (fun u : A × O × X => (h,u)) (stepRow K g (observed n h) (last n h)) t
  nonnegative t h := push_nonnegative _ _ (stepRow_dist K g (observed n h) (last n h)).1 t
  normalized h := (mass_push _ _).trans (stepRow_dist K g (observed n h) (last n h)).2

/-- The actual fine path law is evolved before any state coordinate is forgotten. -/
def law [Fintype X] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq A] [DecidableEq O]
    (K : Nat → Law X A O) (g : Policy A O) (p : X → ℝ) : (n : Nat) → Path X A O n → ℝ
  | 0 => p
  | n+1 => applyKernel (pathKernel (K n) g n).entry (law K g p n)

@[simp] theorem law_zero [Fintype X] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq A] [DecidableEq O]
    (K : Nat → Law X A O) (g : Policy A O) (p : X → ℝ) : law K g p 0 = p := rfl

theorem law_dist [Fintype X] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq A] [DecidableEq O]
    (K : Nat → Law X A O) (g : Policy A O) (p : X → ℝ) (hp : IsDist p) (n : Nat) :
    IsDist (law K g p n) := by
  induction n with
  | zero => exact hp
  | succ n ih => exact kernel_dist (pathKernel (K n) g n) _ ih

/-- The path construction is the literal chronological product, not an assumed history law. -/
theorem law_succ [Fintype X] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq A] [DecidableEq O]
    (K : Nat → Law X A O) (g : Policy A O) (p : X → ℝ) (n : Nat)
    (h : Path X A O n) (u : A × O × X) :
    law K g p (n+1) (h,u) =
      g.probability (observed n h) u.1 * (K n).kernel u.1 u.2.1 u.2.2 (last n h) * law K g p n h := by
  simp [law, pathKernel, applyKernel, push, Prod.mk.injEq, ite_and, stepRow, jointRow]

/-- Aggregation retains the complete report/successor association. -/
theorem push_stepRow [Fintype X] [Fintype A] [Fintype O]
    [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (K : Law X A O) (g : Policy A O) (past : History A O) (x : X) :
    push (stepMap π) (stepRow K g past x) =
      fun u => g.probability past u.1 * push (reportMap π) (jointRow K u.1 x) u.2 := by
  funext u
  rcases u with ⟨a,v⟩
  change push (fun u : A × O × X => (u.1, reportMap π u.2))
    (fun u => g.probability past u.1*jointRow K u.1 x u.2) (a,v) = _
  rw [push_pair_right (reportMap π) (fun a v => g.probability past a * jointRow K a x v) a v]
  change push (reportMap π) (scale (g.probability past a) (jointRow K a x)) v = _
  rw [push_scale]
  rfl

/-- The policy has the same observed-history input and the same action probabilities. -/
theorem stepRow_error [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (K : Law X A O) (L : Law Z A O) (g : Policy A O)
    (past : History A O) (x : X) (ε : ℝ)
    (hε : ∀ a x, tv (push (reportMap π) (jointRow K a x)) (jointRow L a (π x)) ≤ ε) :
    tv (push (stepMap π) (stepRow K g past x)) (stepRow L g past (π x)) ≤ ε := by
  rw [push_stepRow]
  exact tv_weighted_rows_le (g.probability past) ⟨g.nonnegative past,g.normalized past⟩
    (fun a => push (reportMap π) (jointRow K a x)) (fun a => jointRow L a (π x)) ε (fun a => hε a x)

/-- Appending the old path adds no error: it is the same recorded prefix on both sides. -/
theorem project_append [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (n : Nat) (h : Path X A O n) (p : A × O × X → ℝ) :
    push (project π (n+1)) (push (fun u => (h,u)) p) =
      push (fun u : A × O × Z => (project π n h,u)) (push (stepMap π) p) := by
  rw [push_comp, push_comp]
  rfl

theorem pathKernel_error [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (K : Law X A O) (L : Law Z A O) (g : Policy A O)
    (n : Nat) (ε : ℝ)
    (hε : ∀ a x, tv (push (reportMap π) (jointRow K a x)) (jointRow L a (π x)) ≤ ε)
    (h : Path X A O n) :
    tv (push (project π (n+1)) (fun t => (pathKernel K g n).entry t h))
      (fun t => (pathKernel L g n).entry t (project π n h)) ≤ ε := by
  change tv (push (project π (n+1)) (push (fun u => (h,u)) _)) (push _ _) ≤ ε
  rw [project_append]
  simp only [project_observed, project_last]
  exact (tv_push_le (fun u : A × O × Z => (project π n h,u)) _ _).trans
    (stepRow_error π K L g (observed n h) (last n h) ε hε)

/-- Core 3.8: accumulated error for the entire coarse-state and action/report path. -/
theorem whole_history_bound [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (K : Nat → Law X A O) (L : Nat → Law Z A O) (g : Policy A O)
    (p : X → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
    (δ : ℝ) (ε : Nat → ℝ)
    (h0 : tv (push π p) q ≤ δ)
    (hε : ∀ n a x, tv (push (reportMap π) (jointRow (K n) a x)) (jointRow (L n) a (π x)) ≤ ε n)
    (H : Nat) :
    tv (push (project π H) (law K g p H)) (law L g q H) ≤
      min 1 (δ + ∑ n ∈ Finset.range H, ε n) := by
  apply le_min
  · exact tv_le_one _ _ (push_dist _ _ (law_dist K g p hp H)) (law_dist L g q hq H)
  · induction H with
    | zero =>
      change tv (push π p) q ≤ δ + 0
      simpa only [add_zero] using h0
    | succ n ih =>
      have hstep := push_kernel_step (project π n) (project π (n+1))
        (pathKernel (K n) g n) (pathKernel (L n) g n)
        (law K g p n) (law L g q n) (law_dist K g p hp n) (ε n)
        (pathKernel_error π (K n) (L n) g n (ε n) (hε n))
      change tv (push (project π (n+1)) (law K g p (n+1))) (law L g q (n+1)) ≤ _ at hstep
      rw [Finset.sum_range_succ]
      linarith

/-- Any further observable projection inherits the full-history bound. -/
theorem observed_history_bound [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    {Y : Type*} [Fintype Y] [DecidableEq Y]
    (π : X → Z) (K : Nat → Law X A O) (L : Nat → Law Z A O) (g : Policy A O)
    (p : X → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
    (δ : ℝ) (ε : Nat → ℝ) (h0 : tv (push π p) q ≤ δ)
    (hε : ∀ n a x, tv (push (reportMap π) (jointRow (K n) a x)) (jointRow (L n) a (π x)) ≤ ε n)
    (H : Nat) (f : Path Z A O H → Y) :
    tv (push f (push (project π H) (law K g p H))) (push f (law L g q H)) ≤
      min 1 (δ + ∑ n ∈ Finset.range H, ε n) :=
  (tv_push_le f _ _).trans (whole_history_bound π K L g p q hp hq δ ε h0 hε H)

/-- Core 3.8's posterior conclusion is derived from the same constructed full path laws. -/
theorem conditional_final_bound [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (K : Nat → Law X A O) (L : Nat → Law Z A O) (g : Policy A O)
    (p : X → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
    (δ : ℝ) (ε : Nat → ℝ) (h0 : tv (push π p) q ≤ δ)
    (hε : ∀ n a x, tv (push (reportMap π) (jointRow (K n) a x)) (jointRow (L n) a (π x)) ≤ ε n)
    (H : Nat) (E : Finset (Path Z A O H))
    (hEp : 0 < mass (restrict E (push (project π H) (law K g p H))))
    (hEq : 0 < mass (restrict E (law L g q H))) :
    tv (push (last H) (normalize (restrict E (push (project π H) (law K g p H)))))
      (push (last H) (normalize (restrict E (law L g q H)))) ≤
      min 1 ((min 1 (δ + ∑ n ∈ Finset.range H, ε n)) /
        max (mass (restrict E (push (project π H) (law K g p H)))) (mass (restrict E (law L g q H)))) :=
  conditional_output_bound (last H) E _ _ (push_dist _ _ (law_dist K g p hp H))
    (law_dist L g q hq H) hEp hEq _ (whole_history_bound π K L g p q hp hq δ ε h0 hε H)

/-- If either observed-event mass exceeds the common error budget, both posteriors are defined. -/
theorem history_event_positive [Fintype X] [Fintype Z] [Fintype A] [Fintype O]
    [DecidableEq X] [DecidableEq Z] [DecidableEq A] [DecidableEq O]
    (π : X → Z) (K : Nat → Law X A O) (L : Nat → Law Z A O) (g : Policy A O)
    (p : X → ℝ) (q : Z → ℝ) (hp : IsDist p) (hq : IsDist q)
    (δ : ℝ) (ε : Nat → ℝ) (h0 : tv (push π p) q ≤ δ)
    (hε : ∀ n a x, tv (push (reportMap π) (jointRow (K n) a x)) (jointRow (L n) a (π x)) ≤ ε n)
    (H : Nat) (E : Finset (Path Z A O H))
    (he : min 1 (δ + ∑ n ∈ Finset.range H, ε n) < mass (restrict E (push (project π H) (law K g p H))) ∨
      min 1 (δ + ∑ n ∈ Finset.range H, ε n) < mass (restrict E (law L g q H))) :
    0 < mass (restrict E (push (project π H) (law K g p H))) ∧
    0 < mass (restrict E (law L g q H)) := by
  have h := whole_history_bound π K L g p q hp hq δ ε h0 hε H
  have hP := push_dist (project π H) _ (law_dist K g p hp H)
  have hQ := law_dist L g q hq H
  have hd := (tv_nonneg _ _).trans h
  rcases he with hleft | hright
  · exact ⟨hd.trans_lt hleft, event_positive E _ _ hP hQ _ h hleft⟩
  · rw [tv_symm] at h
    exact ⟨event_positive E _ _ hQ hP _ h hright, hd.trans_lt hright⟩

end
end Komorebi.MachineTheory.ApproximateHistory
