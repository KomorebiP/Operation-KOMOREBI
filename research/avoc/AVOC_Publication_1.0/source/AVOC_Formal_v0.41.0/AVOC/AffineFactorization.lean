import AVOC.AffineFusion
import Mathlib.LinearAlgebra.Matrix.Rank

namespace Komorebi.AVOC.Affine.Factorization

/-- Untrusted candidate data, including independently checked lower-bound witnesses.
The map goes input -> width -> output. Dimensions are exact types. -/
structure Candidate (R : Type) (n m : Nat) where
  width : Nat
  first : Signature R n width
  second : Signature R width m
  left : Matrix (Fin width) (Fin m) R
  right : Matrix (Fin n) (Fin width) R

variable {R : Type} [Field R] {n m : Nat}

def plan (c : Candidate R n m) : DenseProgram R n m :=
  .seq (.atom c.first) (.atom c.second)

def factorCost (n m k : Nat) : Nat := denseCost n k + denseCost k m

omit [Field R] in
@[simp] theorem plan_cost (c : Candidate R n m) :
    executionCost (plan c) = factorCost n m c.width := rfl

@[simp] theorem plan_coefficients (c : Candidate R n m) :
    coefficients (plan c) = compose c.second c.first := rfl

/-- Upper witness: the factorization is exact, including both affine offsets.
Lower witness: left * reference.linear * right is the width-dimensional identity. -/
def Valid (f : Signature R n m) (c : Candidate R n m) : Prop :=
  compose c.second c.first = f ∧ c.left * f.linear * c.right = 1

def check [DecidableEq R] (f : Signature R n m) (c : Candidate R n m) : Bool :=
  Affine.check (compose c.second c.first) f &&
    decide (c.left * f.linear * c.right = 1)

theorem check_iff [DecidableEq R] (f : Signature R n m) (c : Candidate R n m) :
    check f c = true ↔ Valid f c := by
  simp only [check, Bool.and_eq_true, Affine.check_iff, decide_eq_true_eq,
    Valid, ← eq_iff_eval]

theorem valid_execution {f : Signature R n m} {c : Candidate R n m}
    (h : Valid f c) (x : Fin n → R) : execute (plan c) x = eval f x := by
  rw [← coefficients_correct, plan_coefficients, h.1]

theorem lower_witness_rank {f : Signature R n m} {c : Candidate R n m}
    (h : c.left * f.linear * c.right = 1) : c.width ≤ f.linear.rank := by
  have ha := Matrix.rank_mul_le_left (c.left * f.linear) c.right
  have hb := Matrix.rank_mul_le_right c.left f.linear
  rw [h, Matrix.rank_one, Fintype.card_fin] at ha
  exact ha.trans hb

theorem any_factor_rank_upper {k : Nat} (a : Signature R n k) (b : Signature R k m) :
    (compose b a).linear.rank ≤ k :=
  (Matrix.rank_mul_le_left b.linear a.linear).trans (Matrix.rank_le_width b.linear)

theorem valid_rank_exact {f : Signature R n m} {c : Candidate R n m}
    (h : Valid f c) : f.linear.rank = c.width := by
  apply Nat.le_antisymm
  · rw [← h.1]
    exact any_factor_rank_upper c.first c.second
  · exact lower_witness_rank h.2

/-- Minimality is among *all* exact two-stage affine factorizations, not a supplied list. -/
theorem width_minimal {f : Signature R n m} {c : Candidate R n m}
    (h : Valid f c) {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : ∀ x, eval b (eval a x) = eval f x) : c.width ≤ k := by
  have eqf : compose b a = f := (eq_iff_eval _ _).2 (by simpa using he)
  have hu := any_factor_rank_upper a b
  rw [eqf, valid_rank_exact h] at hu
  exact hu

theorem factorCost_mono {k l : Nat} (h : k ≤ l) :
    factorCost n m k ≤ factorCost n m l := by
  unfold factorCost denseCost
  apply Nat.add_le_add
  · exact Nat.mul_le_mul_right (2*n+1) h
  · exact Nat.mul_le_mul_left m (Nat.add_le_add_right (Nat.mul_le_mul_left 2 h) 1)

theorem factorCost_strict {k l : Nat} (h : k < l) :
    factorCost n m k < factorCost n m l := by
  have h1 : k * (2*n+1) < l * (2*n+1) :=
    Nat.mul_lt_mul_of_pos_right h (by omega)
  have h2 : m * (2*k+1) ≤ m * (2*l+1) :=
    Nat.mul_le_mul_left m (by omega)
  unfold factorCost denseCost
  omega

theorem two_stage_cost_minimal {f : Signature R n m} {c : Candidate R n m}
    (h : Valid f c) {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : ∀ x, eval b (eval a x) = eval f x) :
    executionCost (plan c) ≤ executionCost (.seq (.atom a) (.atom b)) :=
  factorCost_mono (width_minimal h a b he)

theorem checked_optimal [DecidableEq R] {f : Signature R n m} {c : Candidate R n m}
    (h : check f c = true) :
    (∀ x, execute (plan c) x = eval f x) ∧
    f.linear.rank = c.width ∧
    ∀ (k : Nat) (a : Signature R n k) (b : Signature R k m),
      (∀ x, eval b (eval a x) = eval f x) →
      c.width ≤ k ∧ factorCost n m c.width ≤ factorCost n m k := by
  have hv := (check_iff f c).1 h
  refine ⟨valid_execution hv, valid_rank_exact hv, ?_⟩
  intro k a b he
  exact ⟨width_minimal hv a b he, factorCost_mono (width_minimal hv a b he)⟩

/-- No runtime rank calculation is trusted: the executable gate tests polynomial identities. -/
structure Checked (f : Signature R n m) where
  candidate : Candidate R n m
  certified : Valid f candidate

def validate [DecidableEq R] (f : Signature R n m) (c : Candidate R n m) :
    Option (Checked f) :=
  if h : check f c = true then some ⟨c, (check_iff f c).1 h⟩ else none

theorem validation_sound [DecidableEq R] {f : Signature R n m} {c : Candidate R n m}
    {v : Checked f} (_h : validate f c = some v) : Valid f v.candidate := v.certified

theorem validation_complete [DecidableEq R] {f : Signature R n m} {c : Candidate R n m}
    (h : Valid f c) : ∃ v, validate f c = some v := by
  simp [validate, (check_iff f c).2 h]

theorem altered_semantics_rejected [DecidableEq R] {f : Signature R n m}
    {c : Candidate R n m} (h : compose c.second c.first ≠ f) : check f c = false := by
  cases hc : check f c with
  | false => rfl
  | true => exact False.elim (h ((check_iff f c).1 hc).1)

theorem false_lower_witness_rejected [DecidableEq R] {f : Signature R n m}
    {c : Candidate R n m} (h : c.left * f.linear * c.right ≠ 1) : check f c = false := by
  cases hc : check f c with
  | false => rfl
  | true => exact False.elim (h ((check_iff f c).1 hc).2)

end Komorebi.AVOC.Affine.Factorization
