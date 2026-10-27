import AVOC.AffineFactorChoice

namespace Komorebi.AVOC.Affine.Reuse

open Factorization
variable {R : Type} [Field R] {n m : Nat}

/-- Untrusted persisted data. Validation is repeated on every imported record. -/
structure Record (R : Type) (n m : Nat) where
  signature : Signature R n m
  candidate : Candidate R n m

/-- A change of affine offset does not require a new rank factorization.
The first offset is retained, not silently assumed zero. -/
def retarget (f : Signature R n m) (c : Candidate R n m) : Candidate R n m where
  width := c.width
  first := c.first
  second := ⟨c.second.linear, f.offset - c.second.linear.mulVec c.first.offset⟩
  left := c.left
  right := c.right

@[simp] theorem retarget_width (f : Signature R n m) (c : Candidate R n m) :
    (retarget f c).width = c.width := rfl

@[simp] theorem retarget_first (f : Signature R n m) (c : Candidate R n m) :
    (retarget f c).first = c.first := rfl

@[simp] theorem retarget_linear (f : Signature R n m) (c : Candidate R n m) :
    (compose (retarget f c).second (retarget f c).first).linear =
      (compose c.second c.first).linear := rfl

@[simp] theorem retarget_offset (f : Signature R n m) (c : Candidate R n m) :
    (compose (retarget f c).second (retarget f c).first).offset = f.offset := by
  change c.second.linear.mulVec c.first.offset +
    (f.offset - c.second.linear.mulVec c.first.offset) = f.offset
  abel

/-- The stored full certificate is validated, then transported by exact linear equality. -/
theorem retarget_valid {f g : Signature R n m} {c : Candidate R n m}
    (hc : Valid f c) (hlinear : g.linear = f.linear) : Valid g (retarget g c) := by
  constructor
  · apply Signature.ext
    · simpa only [retarget_linear, hlinear] using congrArg Signature.linear hc.1
    · exact retarget_offset g c
  · change c.left * g.linear * c.right = 1
    rw [hlinear]
    exact hc.2

/-- A later offset change replaces the former offset rather than accumulating it. -/
theorem retarget_overwrite (f g : Signature R n m) (c : Candidate R n m) :
    retarget g (retarget f c) = retarget g c := rfl

@[simp] theorem retarget_plan_cost (f : Signature R n m) (c : Candidate R n m) :
    executionCost (plan (retarget f c)) = factorCost n m c.width := rfl

/-- Import only after rechecking the saved certificate and its linear semantic key. -/
def importFor [DecidableEq R] (f : Signature R n m) (r : Record R n m) :
    Option (Checked f) :=
  if hc : Factorization.check r.signature r.candidate = true then
    if hl : f.linear = r.signature.linear then
      some ⟨retarget f r.candidate, retarget_valid ((Factorization.check_iff _ _).1 hc) hl⟩
    else none
  else none

theorem importFor_iff [DecidableEq R] (f : Signature R n m) (r : Record R n m) :
    (∃ c, importFor f r = some c) ↔
      Valid r.signature r.candidate ∧ f.linear = r.signature.linear := by
  unfold importFor
  split
  next hc =>
    split
    next hl => simp only [Option.some.injEq, exists_eq', true_iff]
               exact ⟨(Factorization.check_iff _ _).1 hc, hl⟩
    next hl => simp only [reduceCtorEq, exists_false, false_iff]
               exact fun h => hl h.2
  next hc =>
    simp only [reduceCtorEq, exists_false, false_iff]
    exact fun h => hc ((Factorization.check_iff _ _).2 h.1)

theorem import_invalid_rejected [DecidableEq R] (f : Signature R n m) (r : Record R n m)
    (h : ¬ Valid r.signature r.candidate) : importFor f r = none := by
  have hc : ¬ Factorization.check r.signature r.candidate = true :=
    fun hc => h ((Factorization.check_iff _ _).1 hc)
  simp [importFor, hc]

theorem import_wrong_linear_rejected [DecidableEq R] (f : Signature R n m) (r : Record R n m)
    (h : f.linear ≠ r.signature.linear) : importFor f r = none := by
  simp [importFor, h]

theorem imported_valid [DecidableEq R] (f : Signature R n m) (r : Record R n m)
    (c : Checked f) (_h : importFor f r = some c) : Valid f c.candidate := c.certified

theorem imported_width [DecidableEq R] (f : Signature R n m) (r : Record R n m)
    (c : Checked f) (h : importFor f r = some c) : c.candidate.width = r.candidate.width := by
  unfold importFor at h
  split at h
  · split at h
    · cases h; rfl
    · cases h
  · cases h

/-- A reused certificate is compared with the CURRENT implementation, not a cached choice. -/
theorem reused_choice_correct [DecidableEq R] (p : DenseProgram R n m) (r : Record R n m)
    (c : Checked (coefficients p)) (_h : importFor (coefficients p) r = some c) :
    (∀ x, execute (choose p c) x = execute p x) ∧
      executionCost (choose p c) ≤ executionCost p :=
  ⟨choose_correct p c, choose_le_original p c⟩

theorem reused_minimal_width [DecidableEq R] (p : DenseProgram R n m) (r : Record R n m)
    (c : Checked (coefficients p)) (_h : importFor (coefficients p) r = some c)
    {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : ∀ x, eval b (eval a x) = execute p x) : c.candidate.width ≤ k :=
  width_minimal c.certified a b (fun x => (he x).trans (coefficients_correct p x).symm)

/-- Different valid witnesses need not be byte identical, but minimum width agrees. -/
theorem checked_width_unique (f : Signature R n m) (c d : Checked f) :
    c.candidate.width = d.candidate.width :=
  (valid_rank_exact c.certified).symm.trans (valid_rank_exact d.certified)

omit [Field R] in
/-- An exact simple menu formula makes clear which restricted optimum is retained. -/
theorem cheaper_cost (p q : DenseProgram R n m) :
    executionCost (cheaper p q) = min (executionCost p) (executionCost q) := by
  unfold cheaper
  split
  next h => exact (Nat.min_eq_right (Nat.le_of_lt h)).symm
  next h => exact (Nat.min_eq_left (Nat.le_of_not_gt h)).symm

theorem choose_cost_exact (p : DenseProgram R n m) (c : Checked (coefficients p)) :
    executionCost (choose p c) =
      min (min (executionCost p) (denseCost n m)) (factorCost n m c.candidate.width) := by
  simp only [choose, cheaper_cost, fused_execution_cost, plan_cost]

/-- A complete valid cached certificate leaves no two-dense-stage tariff improvement
for another factor search, although other implementation classes remain open. -/
theorem same_signature_search_cannot_lower_factor_cost
    (f : Signature R n m) (c d : Checked f) :
    factorCost n m c.candidate.width = factorCost n m d.candidate.width := by
  rw [checked_width_unique f c d]

end Komorebi.AVOC.Affine.Reuse
