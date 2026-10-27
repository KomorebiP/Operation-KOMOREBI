import AVOC.AffineFactorization

namespace Komorebi.AVOC.Affine.Factorization

variable {R : Type} [Field R] {n m : Nat}

/-- Prefer the incumbent on ties. Only tariff is compared here; semantic premises
are provided separately by the certified menu construction. -/
def cheaper (p q : DenseProgram R n m) : DenseProgram R n m :=
  if executionCost q < executionCost p then q else p

omit [Field R] in
theorem cheaper_left (p q : DenseProgram R n m) :
    executionCost (cheaper p q) ≤ executionCost p := by
  unfold cheaper; split <;> omega

omit [Field R] in
theorem cheaper_right (p q : DenseProgram R n m) :
    executionCost (cheaper p q) ≤ executionCost q := by
  unfold cheaper; split <;> omega

omit [Field R] in
theorem cheaper_member (p q : DenseProgram R n m) : cheaper p q = p ∨ cheaper p q = q := by
  unfold cheaper; split <;> simp

theorem cheaper_correct (p q : DenseProgram R n m)
    (h : ∀ x, execute q x = execute p x) :
    ∀ x, execute (cheaper p q) x = execute p x := by
  intro x; unfold cheaper; split
  · exact h x
  · rfl

/-- The original implementation remains in the menu. A dense normal form is not
silently assumed cheaper than the input or the minimum-width factorization. -/
def choose (p : DenseProgram R n m) (c : Checked (coefficients p)) : DenseProgram R n m :=
  cheaper (cheaper p (fuse p)) (plan c.candidate)

theorem choose_correct (p : DenseProgram R n m) (c : Checked (coefficients p)) :
    ∀ x, execute (choose p c) x = execute p x := by
  intro x
  have hf := cheaper_correct p (fuse p) (fuse_correct p)
  have hc : ∀ x, execute (plan c.candidate) x = execute p x :=
    fun x => (valid_execution c.certified x).trans (coefficients_correct p x)
  exact (cheaper_correct _ _ (fun x => (hc x).trans (hf x).symm) x).trans (hf x)

theorem choose_le_original (p : DenseProgram R n m) (c : Checked (coefficients p)) :
    executionCost (choose p c) ≤ executionCost p :=
  (cheaper_left _ _).trans (cheaper_left _ _)

theorem choose_le_dense (p : DenseProgram R n m) (c : Checked (coefficients p)) :
    executionCost (choose p c) ≤ denseCost n m :=
  (cheaper_left _ _).trans (cheaper_right p (fuse p))

theorem choose_le_factor (p : DenseProgram R n m) (c : Checked (coefficients p)) :
    executionCost (choose p c) ≤ factorCost n m c.candidate.width :=
  cheaper_right _ _

theorem choose_le_any_two_stage (p : DenseProgram R n m) (c : Checked (coefficients p))
    {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : ∀ x, eval b (eval a x) = execute p x) :
    executionCost (choose p c) ≤ executionCost (.seq (.atom a) (.atom b)) := by
  apply (choose_le_factor p c).trans
  exact two_stage_cost_minimal c.certified a b
    (fun x => (he x).trans (coefficients_correct p x).symm)

theorem choose_menu_member (p : DenseProgram R n m) (c : Checked (coefficients p)) :
    choose p c = p ∨ choose p c = fuse p ∨ choose p c = plan c.candidate := by
  rcases cheaper_member (cheaper p (fuse p)) (plan c.candidate) with h | h
  · rcases cheaper_member p (fuse p) with hp | hp
    · exact Or.inl (h.trans hp)
    · exact Or.inr (Or.inl (h.trans hp))
  · exact Or.inr (Or.inr h)

/-- Cost of the two candidate-certificate polynomial identities and comparisons.
This is a conservative declared dense-arithmetic tariff, not CPU or allocation cost. -/
def checkingCharge (n m r : Nat) : Nat :=
  composeCost n r m + 2*r*m*n + 2*r*n*r + m*(n+1) + r*r

/-- Work already spent on exploration is paid regardless of the selected plan. -/
def upfront {n m : Nat} (p : DenseProgram R n m) (r generation : Nat) : Nat :=
  normalizationCost p + generation + checkingCharge n m r

def campaignCost (p : DenseProgram R n m) (c : Checked (coefficients p))
    (calls generation : Nat) : Nat :=
  upfront p c.candidate.width generation + calls * executionCost (choose p c)

def costSaving (p : DenseProgram R n m) (c : Checked (coefficients p)) : Nat :=
  executionCost p - executionCost (choose p c)

theorem amortization_iff (p : DenseProgram R n m) (c : Checked (coefficients p))
    (calls generation : Nat) :
    campaignCost p c calls generation ≤ calls * executionCost p ↔
      upfront p c.candidate.width generation ≤ calls * costSaving p c := by
  have hc := choose_le_original p c
  have hi : executionCost p = executionCost (choose p c) + costSaving p c := by
    unfold costSaving; omega
  unfold campaignCost
  rw [hi, Nat.mul_add]
  omega

theorem campaign_never_refunds (p : DenseProgram R n m) (c : Checked (coefficients p))
    (calls generation : Nat) :
    upfront p c.candidate.width generation ≤ campaignCost p c calls generation := by
  unfold campaignCost; omega

theorem no_savings_no_positive_net (p : DenseProgram R n m) (c : Checked (coefficients p))
    (calls generation : Nat) (h : executionCost (choose p c) = executionCost p) :
    calls * executionCost p ≤ campaignCost p c calls generation := by
  unfold campaignCost; rw [h]; omega

/-- Check resources before evaluating the expensive candidate certificate. The
supplied generation charge is an external meter input, not authenticated by this gate. -/
def admit [DecidableEq R] (p : DenseProgram R n m) (c : Candidate R n m)
    (generation budget : Nat) : Option (Checked (coefficients p)) :=
  if upfront p c.width generation ≤ budget then validate (coefficients p) c else none

theorem admission_iff [DecidableEq R] (p : DenseProgram R n m)
    (c : Candidate R n m) (generation budget : Nat) :
    (∃ v, admit p c generation budget = some v) ↔
      upfront p c.width generation ≤ budget ∧ Valid (coefficients p) c := by
  unfold admit validate
  split
  next hb =>
    split
    next hv => exact ⟨fun _ => ⟨hb, (check_iff _ _).1 hv⟩,
      fun _ => ⟨_, rfl⟩⟩
    next hv => simp only [reduceCtorEq, exists_false, false_iff]
               intro h; exact hv ((check_iff _ _).2 h.2)
  next hb => simp [hb]

theorem admitted_budget_and_semantics [DecidableEq R] (p : DenseProgram R n m)
    (c : Candidate R n m) (generation budget : Nat) (v : Checked (coefficients p))
    (h : admit p c generation budget = some v) :
    upfront p c.width generation ≤ budget ∧
    ∀ x, execute (choose p v) x = execute p x :=
  ⟨((admission_iff p c generation budget).1 ⟨v,h⟩).1, choose_correct p v⟩

theorem insufficient_credit [DecidableEq R] (p : DenseProgram R n m)
    (c : Candidate R n m) (generation budget : Nat)
    (h : budget < upfront p c.width generation) :
    admit p c generation budget = none := by
  simp [admit, Nat.not_le.mpr h]

end Komorebi.AVOC.Affine.Factorization
