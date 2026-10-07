import KomorebiPadic.PrunedMaskCertificate

/-! # A numerator bound using only surviving correction orders
Zero defect is assigned correction-order cap zero, not a fictitious finite valuation.
The initial numerator B is explicitly retained in the maximum defining the bound.
-/
namespace KomorebiPadic
open Polynomial

noncomputable def prunedMaskOrderCap (p r : ℕ) (B : ℤ[X]) : ℕ :=
  if frobeniusDefect p B = 0 then 0
  else coarseK r (polynomialPadicOrder p (frobeniusDefect p B))

@[simp] theorem prunedMaskOrderCap_zero_defect (p r : ℕ) (B : ℤ[X])
    (hE : frobeniusDefect p B = 0) : prunedMaskOrderCap p r B = 0 := by
  simp [prunedMaskOrderCap, hE]

theorem prunedMaskOrderCap_nonzero_defect (p r : ℕ) (B : ℤ[X])
    (hE : frobeniusDefect p B ≠ 0) :
    prunedMaskOrderCap p r B = coarseK r (polynomialPadicOrder p (frobeniusDefect p B)) := by
  simp [prunedMaskOrderCap, hE]

/-- All-natural bound, including zero precision. -/
theorem prunedMaskOrderCap_le_precision (p r : ℕ) (B : ℤ[X]) :
    prunedMaskOrderCap p r B ≤ r-1 := by
  unfold prunedMaskOrderCap
  split
  · exact Nat.zero_le _
  · exact Nat.div_le_self _ _

/-- Every admitted correction obeys the smaller cap, at every source layer. -/
theorem prunedCorrectionActive_le_orderCap {p r ell k : ℕ} (B : ℤ[X])
    (ha : prunedCorrectionActive p r ell k B) : k ≤ prunedMaskOrderCap p r B := by
  by_cases hE : frobeniusDefect p B = 0
  · simp only [prunedCorrectionActive, hE, ↓reduceIte] at ha
    simp [prunedMaskOrderCap, hE, ha]
  · simp only [prunedCorrectionActive, hE, ↓reduceIte] at ha
    rw [prunedMaskOrderCap_nonzero_defect p r B hE]
    exact activeAt_implies_le_coarseK ha

/-- A correction above the cap has zero residue kernel, before digit extraction. -/
theorem finiteMaskKernel_zero_above_orderCap {p r ell k : ℕ}
    (hp : p.Prime) (A B : ℤ[X]) (hk : prunedMaskOrderCap p r B < k) :
    finiteMaskKernel p r ell k A B = 0 := by
  apply finiteMaskKernel_zero_of_pruned_inactive hp A B
  intro ha
  have := prunedCorrectionActive_le_orderCap B ha
  omega

noncomputable def degreePrunedKernelCap (p r : ℕ) (A B : ℤ[X]) : ℕ :=
  A.natDegree + (p-1)*B.natDegree + prunedMaskOrderCap p r B * (frobeniusDefect p B).natDegree

noncomputable def degreePrunedNumeratorBound (p r : ℕ) (A B : ℤ[X]) : ℕ :=
  max B.natDegree (cartierCeilDiv (degreePrunedKernelCap p r A B) (p-1))

theorem degreePrunedNumeratorBound_initial (p r : ℕ) (A B : ℤ[X]) :
    B.natDegree ≤ degreePrunedNumeratorBound p r A B := Nat.le_max_left _ _

theorem degreePrunedKernelCap_le_original (p r : ℕ) (A B : ℤ[X]) :
    degreePrunedKernelCap p r A B ≤ cartierKernelDegreeCap p r A B := by
  exact Nat.add_le_add_left
    (Nat.mul_le_mul_right _ (prunedMaskOrderCap_le_precision p r B)) _

theorem cartierCeilDiv_mono_numerator {n m a : ℕ} (h : n ≤ m) :
    cartierCeilDiv n a ≤ cartierCeilDiv m a := by
  exact Nat.div_le_div_right (Nat.sub_le_sub_right (Nat.add_le_add_right h a) 1)

/-- Smaller degree never increases the old ambient numerator dimension. -/
theorem degreePrunedNumeratorBound_le_original (p r : ℕ) (A B : ℤ[X]) :
    degreePrunedNumeratorBound p r A B ≤ cartierNumeratorBound p r A B := by
  exact max_le_max le_rfl (cartierCeilDiv_mono_numerator (degreePrunedKernelCap_le_original p r A B))

theorem degreePrunedNumeratorBound_kernel {p r : ℕ} (hp : 1 < p) (A B : ℤ[X]) :
    degreePrunedKernelCap p r A B ≤ (p-1)*degreePrunedNumeratorBound p r A B := by
  exact (le_mul_cartierCeilDiv _ (by omega : 0 < p-1)).trans
    (Nat.mul_le_mul_left (p-1) (Nat.le_max_right _ _))

/-- All kernels, including inactive zero kernels, obey the reduced degree bound.
No k<r assumption is required: the activity test already enforces the cap. -/
theorem finiteMaskKernel_degree_pruned {p r ell k : ℕ} (hp : p.Prime) (A B : ℤ[X]) :
    (finiteMaskKernel p r ell k A B).natDegree ≤ (p-1)*degreePrunedNumeratorBound p r A B := by
  by_cases ha : prunedCorrectionActive p r ell k B
  · have ht : maskPadding p ell ≤ p-1 := by
      have := (maskPadding_spec (ell := ell) hp.pos).2
      omega
    have hb := Polynomial.natDegree_pow_le (p := B) (n := maskPadding p ell)
    have hw := cartierBranchWeight_degree p (quotientOfLayer p ell) k (frobeniusDefect p B)
    have hprod := Polynomial.natDegree_mul_le
      (p := A*B^maskPadding p ell)
      (q := cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B))
    have hab := Polynomial.natDegree_mul_le (p := A) (q := B^maskPadding p ell)
    have ht' := Nat.mul_le_mul_right B.natDegree ht
    have hk' := Nat.mul_le_mul_right (frobeniusDefect p B).natDegree
      (prunedCorrectionActive_le_orderCap B ha)
    have hcap : (A*B^maskPadding p ell*
        cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)).natDegree ≤
        degreePrunedKernelCap p r A B := by
      unfold degreePrunedKernelCap
      omega
    exact Polynomial.natDegree_map_le.trans
      (hcap.trans (degreePrunedNumeratorBound_kernel hp.one_lt A B))
  · rw [finiteMaskKernel_zero_of_pruned_inactive hp A B ha]
    simp

/-- Polynomial extraction after a retained kernel remains within the smaller D. -/
theorem finiteMaskBranch_degree_pruned {p r ell k : ℕ} (hp : p.Prime)
    (d : ℕ) (A B : ℤ[X]) (P : (ZMod (p^r))[X])
    (hP : P.natDegree ≤ degreePrunedNumeratorBound p r A B) :
    (polynomialCartier p d (P*finiteMaskKernel p r ell k A B)).natDegree ≤
      degreePrunedNumeratorBound p r A B :=
  polynomialCartier_mul_degree_le hp.pos d P _ hP (finiteMaskKernel_degree_pruned hp A B)

/-- Zero defect does not by itself improve the old global D: its old defect term was zero. -/
theorem degreePrunedNumeratorBound_zero_defect (p r : ℕ) (A B : ℤ[X])
    (hE : frobeniusDefect p B = 0) :
    degreePrunedNumeratorBound p r A B = cartierNumeratorBound p r A B := by
  simp [degreePrunedNumeratorBound, cartierNumeratorBound, degreePrunedKernelCap,
    cartierKernelDegreeCap, hE]

/-- Generic defect valuation zero also leaves the previous degree bound unchanged. -/
theorem degreePrunedNumeratorBound_order_zero (p r : ℕ) (A B : ℤ[X])
    (hE : frobeniusDefect p B ≠ 0) (hh : polynomialPadicOrder p (frobeniusDefect p B) = 0) :
    degreePrunedNumeratorBound p r A B = cartierNumeratorBound p r A B := by
  simp [degreePrunedNumeratorBound, cartierNumeratorBound, degreePrunedKernelCap,
    cartierKernelDegreeCap, prunedMaskOrderCap, hE, hh, coarseK]

end KomorebiPadic
