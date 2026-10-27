module
public import Mathlib.Order.Interval.Finset.Fin
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Algebra.BigOperators.Group.Finset.Piecewise
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII item 4.1.
Counts actual finite addresses, not a recurrence assumed to describe them.
One scalar multiplication and one accumulation are two modeled operations.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators Classical

abbrev BandedAddress (p w : ℕ) :=
  {e : Fin p × Fin p // e.1.val ≤ e.2.val+w ∧ e.2.val ≤ e.1.val+w}

noncomputable def bandCount (p w : ℕ) : ℕ :=
  ∑ i : Fin p, ∑ j : Fin p,
    if i.val ≤ j.val+w ∧ j.val ≤ i.val+w then 1 else 0

theorem bandCount_card (p w : ℕ) : Fintype.card (BandedAddress p w) = bandCount p w := by
  simp only [BandedAddress,Fintype.card_subtype,Finset.card_filter,Fintype.sum_prod_type,bandCount]

theorem finite_prefix_count (p w : ℕ) (hw : w ≤ p) :
    (∑ i : Fin p, if i.val < w then 1 else 0) = w := by
  by_cases he : w = p
  · subst w
    simp
  · let a : Fin p := ⟨w,by omega⟩
    have hf : Finset.univ.filter (fun i : Fin p => i.val < w) = Finset.Iio a := by
      ext i
      simp [a,Fin.lt_def]
    rw [←Finset.card_filter,hf,Fin.card_Iio]

theorem bandCount_succ (p w : ℕ) (hw : w ≤ p) :
    bandCount (p+1) w = bandCount p w + 2*w+1 := by
  have hc : (∑ i : Fin p, if i.val+1 ≤ w then 1 else 0) = w := by
    simpa only [Nat.succ_le_iff] using finite_prefix_count p w hw
  have hpred (i j : Fin p) :
      (i.val+1 ≤ j.val+1+w ∧ j.val+1 ≤ i.val+1+w) ↔
      (i.val ≤ j.val+w ∧ j.val ≤ i.val+w) := by omega
  simp only [bandCount,Fin.sum_univ_succ,Fin.val_zero,Fin.val_succ,
    Nat.zero_add,Nat.zero_le,true_and,and_true,hpred,Finset.sum_add_distrib]
  simp only [hc,ite_true]
  omega

theorem bandCount_full (p : ℕ) : bandCount (p+1) p = (p+1)^2 := by
  have hpred (i j : Fin (p+1)) : i.val ≤ j.val+p ∧ j.val ≤ i.val+p := by
    have hi := i.isLt
    have hj := j.isLt
    omega
  simp [bandCount,hpred,pow_two]

/-- Subtraction-free count identity, avoiding truncated-natural ambiguity. -/
theorem bandCount_balance (p w : ℕ) (hw : w < p) :
    bandCount p w + w*(w+1) = p*(2*w+1) := by
  induction p with
  | zero => omega
  | succ p ih =>
    by_cases he : w = p
    · subst w
      rw [bandCount_full]
      ring
    · have hwp : w < p := by omega
      have hi := ih hwp
      rw [bandCount_succ p w (by omega)]
      nlinarith

/-- Item 4.1: exact cardinality of the active block address set. -/
theorem banded_block_count (p w : ℕ) (hw : w < p) :
    Fintype.card (BandedAddress p w) = p*(2*w+1)-w*(w+1) := by
  rw [bandCount_card]
  have he := bandCount_balance p w hw
  omega

/-- Scalar entries in an explicitly stored banded block representation. -/
abbrev BandedStorage (p w b : ℕ) := BandedAddress p w × Fin b × Fin b

/-- One event for each multiply or accumulation, RHS, address and local scalar. -/
abbrev BandedOperation (p w b q : ℕ) := Fin 2 × Fin q × BandedStorage p w b

theorem banded_storage_count (p w b : ℕ) (hw : w < p) :
    Fintype.card (BandedStorage p w b) = b^2*(p*(2*w+1)-w*(w+1)) := by
  simp only [BandedStorage,Fintype.card_prod,Fintype.card_fin,banded_block_count p w hw]
  ring

theorem banded_operation_count (p w b q : ℕ) (hw : w < p) :
    Fintype.card (BandedOperation p w b q) = 2*q*b^2*(p*(2*w+1)-w*(w+1)) := by
  simp only [BandedOperation,Fintype.card_prod,Fintype.card_fin,
    banded_storage_count p w b hw]
  ring

theorem banded_diagonal_case (p : ℕ) (hp : 0 < p) :
    Fintype.card (BandedAddress p 0) = p := by
  simpa using banded_block_count p 0 hp

end KomorebiPaperVIII

-- FIFTH BLOCK AXIOM AUDIT
#print axioms KomorebiPaperVIII.bandCount_card
#print axioms KomorebiPaperVIII.finite_prefix_count
#print axioms KomorebiPaperVIII.bandCount_succ
#print axioms KomorebiPaperVIII.bandCount_full
#print axioms KomorebiPaperVIII.bandCount_balance
#print axioms KomorebiPaperVIII.banded_block_count
#print axioms KomorebiPaperVIII.banded_storage_count
#print axioms KomorebiPaperVIII.banded_operation_count
#print axioms KomorebiPaperVIII.banded_diagonal_case
#print axioms KomorebiPaperVIII.BandedAddress
#print axioms KomorebiPaperVIII.BandedStorage
#print axioms KomorebiPaperVIII.BandedOperation
#print axioms KomorebiPaperVIII.bandCount
