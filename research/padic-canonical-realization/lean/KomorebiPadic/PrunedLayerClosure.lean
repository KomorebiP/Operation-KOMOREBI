import KomorebiPadic.CanonicalMaskAutomaton

/-! # Valuation-pruned denominator closure for the actual polynomial mask
Zero defect has a separate one-layer definition. Otherwise the layer cap is the
existing exact correction-graph maximum, not a new optimization surrogate.
-/
namespace KomorebiPadic
open Polynomial

/-- Every active successor of a layer below the exact maximum stays below it. -/
theorem exactMaximumLayer_active_closed {p r h ell k : ℕ} (hp : p.Prime)
    (hell : ell ≤ exactMaximumLayer p r h)
    (ha : ActiveAt r h k (padicValNat p ((quotientOfLayer p ell+k-1).choose k))) :
    quotientOfLayer p ell + k ≤ exactMaximumLayer p r h := by
  have hq : quotientOfLayer p ell ≤ stableQuotient p r h := by
    rw [← quotientOf_exactMaximumLayer hp]
    exact Nat.add_le_add_right (Nat.div_le_div_right hell) 1
  apply isTarget_le_exactMaximumLayer hp
  exact ⟨quotientOfLayer p ell, k, Nat.succ_le_iff.mpr (Nat.succ_pos _), hq, ha, rfl⟩

/-- The graph maximum does not exceed the old sufficient all-branch layer cap. -/
theorem exactMaximumLayer_le_cartierLayerBound {p r h : ℕ}
    (hp : p.Prime) (hr : 0 < r) :
    exactMaximumLayer p r h ≤ cartierLayerBound p r := by
  have hceil := le_mul_cartierCeilDiv r (by have := hp.one_lt; omega : 0 < p-1)
  have hK : coarseK r h ≤ r-1 := Nat.div_le_self _ _
  have hdiv : coarseK r h / (p-1) < cartierCeilDiv r (p-1) := by
    apply (Nat.div_lt_iff_lt_mul (by have := hp.one_lt; omega : 0 < p-1)).mpr
    rw [Nat.mul_comm]
    omega
  have hQ := firstNoncrossingQuotient_le_bound (p := p) (r := r) (h := h) hp
  rcases exactMaximumLayer_isTarget (r := r) (h := h) hp hr with
    ⟨q, k, _, hq, he, hm⟩
  have hk : k ≤ coarseK r h := activeAt_implies_le_coarseK he
  change q ≤ firstNoncrossingQuotient p r h at hq
  change firstNoncrossingQuotient p r h ≤ coarseK r h / (p-1)+1 at hQ
  unfold cartierLayerBound
  omega

/-- Zero defect is genuinely one-layer, rather than assigned a fictitious finite valuation. -/
noncomputable def prunedMaskLayerBound (p r : ℕ) (B : ℤ[X]) : ℕ :=
  if frobeniusDefect p B = 0 then 1
  else exactMaximumLayer p r (polynomialPadicOrder p (frobeniusDefect p B))

/-- The formal branch gate agrees with actual nonzero weight at positive quotient. -/
noncomputable def prunedCorrectionActive (p r ell k : ℕ) (B : ℤ[X]) : Prop :=
  if frobeniusDefect p B = 0 then k = 0
  else ActiveAt r (polynomialPadicOrder p (frobeniusDefect p B)) k
    (padicValNat p ((quotientOfLayer p ell+k-1).choose k))

@[simp] theorem prunedMaskLayerBound_zero_defect (p r : ℕ) (B : ℤ[X])
    (hE : frobeniusDefect p B = 0) : prunedMaskLayerBound p r B = 1 := by
  simp [prunedMaskLayerBound, hE]

theorem prunedMaskLayerBound_nonzero_defect (p r : ℕ) (B : ℤ[X])
    (hE : frobeniusDefect p B ≠ 0) :
    prunedMaskLayerBound p r B =
      exactMaximumLayer p r (polynomialPadicOrder p (frobeniusDefect p B)) := by
  simp [prunedMaskLayerBound, hE]

theorem prunedMaskLayerBound_pos (p r : ℕ) (B : ℤ[X]) :
    0 < prunedMaskLayerBound p r B := by
  unfold prunedMaskLayerBound
  split
  · omega
  · have hb := finalFiberLower_le_exactMaximumLayer p r
      (polynomialPadicOrder p (frobeniusDefect p B))
    unfold finalFiberLower stableFiberLower at hb
    omega

theorem prunedMaskLayerBound_le_unpruned {p r : ℕ} (hp : p.Prime)
    (hr : 0 < r) (B : ℤ[X]) : prunedMaskLayerBound p r B ≤ cartierLayerBound p r := by
  unfold prunedMaskLayerBound
  split
  · exact cartierLayerBound_pos hp.one_lt hr
  · exact exactMaximumLayer_le_cartierLayerBound hp hr

/-- Every admitted formal branch stays inside the smaller coordinate space. -/
theorem prunedMaskLayerBound_closed {p r ell k : ℕ} (hp : p.Prime)
    (B : ℤ[X]) (hell : ell ≤ prunedMaskLayerBound p r B)
    (ha : prunedCorrectionActive p r ell k B) :
    quotientOfLayer p ell + k ≤ prunedMaskLayerBound p r B := by
  by_cases hE : frobeniusDefect p B = 0
  · simp only [prunedCorrectionActive, hE, ↓reduceIte] at ha
    subst k
    rw [prunedMaskLayerBound_zero_defect p r B hE] at hell ⊢
    have hlt : ell < p := by have := hp.one_lt; omega
    simp [quotientOfLayer, Nat.div_eq_of_lt hlt]
  · simp only [prunedCorrectionActive, hE, ↓reduceIte] at ha
    rw [prunedMaskLayerBound_nonzero_defect p r B hE] at hell ⊢
    exact exactMaximumLayer_active_closed hp hell ha

/-- Disallowed branches are zero as residue polynomials, before any section. -/
theorem finiteMaskKernel_zero_of_pruned_inactive {p r ell k : ℕ}
    (hp : p.Prime) (A B : ℤ[X]) (ha : ¬ prunedCorrectionActive p r ell k B) :
    finiteMaskKernel p r ell k A B = 0 := by
  by_cases hE : frobeniusDefect p B = 0
  · have hk : 0 < k := by
      simp only [prunedCorrectionActive, hE, ↓reduceIte] at ha
      omega
    simp [finiteMaskKernel, hE, cartierBranchWeight_zero_defect p _ k hk]
  · have hna : ¬ ActiveAt r (polynomialPadicOrder p (frobeniusDefect p B)) k
        (padicValNat p ((quotientOfLayer p ell+k-1).choose k)) := by
      simpa only [prunedCorrectionActive, hE, ↓reduceIte] using ha
    have hw : (cartierBranchWeight p (quotientOfLayer p ell) k (frobeniusDefect p B)).map
        (Int.castRingHom (ZMod (p^r))) = 0 := by
      by_contra hn
      exact hna ((cartierBranchWeight_survives_iff_activeAt hp (Nat.succ_pos _) r k _ hE).mp hn)
    simp only [finiteMaskKernel, Polynomial.map_mul, hw, mul_zero]

/-- Nonzero actual polynomial kernels cannot be sent outside the pruned range. -/
theorem finiteMaskKernel_nonzero_target_closed {p r ell k : ℕ}
    (hp : p.Prime) (A B : ℤ[X]) (hell : ell ≤ prunedMaskLayerBound p r B)
    (hn : finiteMaskKernel p r ell k A B ≠ 0) :
    quotientOfLayer p ell+k ≤ prunedMaskLayerBound p r B := by
  apply prunedMaskLayerBound_closed hp B hell
  by_contra ha
  exact hn (finiteMaskKernel_zero_of_pruned_inactive hp A B ha)

end KomorebiPadic
