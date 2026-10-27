import PaperXII.DeterminantalStabilization
import Mathlib.Data.Fintype.Option

noncomputable section
namespace PaperXII.DeterminantalIdeals
open Matrix
variable {R : Type*} [CommRing R] {m n m' n' : Type*}

theorem presentationIdeal_submatrix_equiv [Fintype m] [Fintype m']
    (A : Matrix m n R) (e : m' ≃ m) (f : n' ≃ n) (j : ℕ) :
    presentationIdeal (A.submatrix e f) j = presentationIdeal A j := by
  simp only [presentationIdeal, Fintype.card_congr e, minorIdeal_submatrix_equiv]

/-- Stabilization by an arbitrary finite identity block. -/
def stabilizeBlock (A : Matrix m n R) (q : Type*) : Matrix (m ⊕ q) (n ⊕ q) R := by
  classical
  exact Matrix.fromBlocks A 0 0 1

@[simp] theorem stabilizeBlock_inl_inl (A : Matrix m n R) (q : Type*) (i : m) (j : n) :
    stabilizeBlock A q (.inl i) (.inl j) = A i j := rfl
@[simp] theorem stabilizeBlock_inl_inr (A : Matrix m n R) (q : Type*) (i : m) (j : q) :
    stabilizeBlock A q (.inl i) (.inr j) = 0 := rfl
@[simp] theorem stabilizeBlock_inr_inl (A : Matrix m n R) (q : Type*) (i : q) (j : n) :
    stabilizeBlock A q (.inr i) (.inl j) = 0 := rfl
@[simp] theorem stabilizeBlock_inr_inr (A : Matrix m n R) (q : Type*) [DecidableEq q] (i j : q) :
    stabilizeBlock A q (.inr i) (.inr j) = if i = j then 1 else 0 := by
  classical
  simp [stabilizeBlock, Matrix.one_apply]

def optionSumEquiv (α β : Type*) : α ⊕ Option β ≃ Option (α ⊕ β) where
  toFun := fun x => match x with
    | .inl a => some (.inl a)
    | .inr none => none
    | .inr (some b) => some (.inr b)
  invFun := fun x => match x with
    | none => .inr none
    | some (.inl a) => .inl a
    | some (.inr b) => .inr (some b)
  left_inv := by intro x; rcases x with a | (_ | b) <;> rfl
  right_inv := by intro x; rcases x with _ | (a | b) <;> rfl

theorem stabilizeBlock_option (A : Matrix m n R) (q : Type*) :
    stabilizeBlock A (Option q) =
      (stabilize (stabilizeBlock A q)).submatrix (optionSumEquiv m q) (optionSumEquiv n q) := by
  classical
  ext i j
  rcases i with a | (_ | b) <;> rcases j with c | (_ | d) <;>
    simp [Matrix.submatrix_apply, optionSumEquiv, stabilize]

theorem stabilizeBlock_equiv (A : Matrix m n R) {q q' : Type*} (e : q ≃ q') :
    (stabilizeBlock A q').submatrix (Equiv.sumCongr (Equiv.refl m) e)
      (Equiv.sumCongr (Equiv.refl n) e) = stabilizeBlock A q := by
  classical
  ext i j
  rcases i with i | i <;> rcases j with j | j <;>
    simp [Matrix.submatrix_apply]

theorem presentationIdeal_stabilizeBlock [Fintype m] (A : Matrix m n R)
    (q : Type*) [Fintype q] (j : ℕ) :
    presentationIdeal (stabilizeBlock A q) j = presentationIdeal A j := by
  classical
  refine Fintype.induction_empty_option (P := fun q _ =>
    presentationIdeal (stabilizeBlock A q) j = presentationIdeal A j) ?_ ?_ ?_ q
  · intro α β _ e h
    let : Fintype α := Fintype.ofEquiv β e.symm
    rw [← presentationIdeal_submatrix_equiv (stabilizeBlock A β)
      (Equiv.sumCongr (Equiv.refl m) e) (Equiv.sumCongr (Equiv.refl n) e) j,
      stabilizeBlock_equiv]
    exact h
  · have h : stabilizeBlock A PEmpty = A.submatrix (Equiv.sumEmpty m PEmpty)
        (Equiv.sumEmpty n PEmpty) := by
      ext i k
      rcases i with i | i
      · rcases k with k | k
        · rfl
        · exact isEmptyElim k
      · exact isEmptyElim i
    rw [h, presentationIdeal_submatrix_equiv]
  · intro α _ h
    rw [stabilizeBlock_option, presentationIdeal_submatrix_equiv,
      presentationIdeal_stabilize, h]

end PaperXII.DeterminantalIdeals
