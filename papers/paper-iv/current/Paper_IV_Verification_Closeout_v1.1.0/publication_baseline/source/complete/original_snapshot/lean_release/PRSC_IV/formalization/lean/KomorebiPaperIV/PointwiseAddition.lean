/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.PointwiseFilters

namespace Komorebi.PaperIV
noncomputable section

theorem pointwiseRootAverage_scaled_exp (N j : ℕ) (omega lambda z : ℂ) :
    pointwiseRootAverage N j omega (fun t => Complex.exp (lambda * z * t)) 1 =
      entireTransfer N j omega lambda z := by
  unfold pointwiseRootAverage entireTransfer
  congr 1
  apply Finset.sum_congr rfl
  intro l _
  congr 2
  ring

theorem entireTransfer_addition {N k : ℕ} (hN : 0 < N) (hk : k < N)
    {omega : ℂ} (ho : IsPrimitiveRoot omega N) (lambda z w : ℂ) :
    entireTransfer N k omega lambda (z + w) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k then
          entireTransfer N i omega lambda z * entireTransfer N j omega lambda w
        else 0 := by
  have h := pointwiseRootAverage_product hN ho k
    (fun t => Complex.exp (lambda * z * t)) (fun t => Complex.exp (lambda * w * t)) 1
  have he : (fun t => Complex.exp (lambda * z * t) * Complex.exp (lambda * w * t)) =
      (fun t => Complex.exp (lambda * (z + w) * t)) := by
    funext t
    rw [← Complex.exp_add]
    congr 1
    ring
  rw [he, pointwiseRootAverage_scaled_exp] at h
  simpa only [pointwiseRootAverage_scaled_exp, Nat.mod_eq_of_lt hk] using h

theorem signed_addition_weight {N : ℕ} (hN : 0 < N) {rho : ℂ}
    (hr : rho ^ N = -1) (i j : ℕ) :
    (rho ^ ((i + j) % N))⁻¹ =
      (-1 : ℂ) ^ ((i + j) / N) * (rho ^ i)⁻¹ * (rho ^ j)⁻¹ := by
  have hr0 : rho ≠ 0 := by intro h; simp [h, hN.ne'] at hr
  have hp : rho ^ i * rho ^ j =
      (-1 : ℂ) ^ ((i + j) / N) * rho ^ ((i + j) % N) := by
    rw [← pow_add, ← hr, ← pow_mul, ← pow_add, Nat.div_add_mod]
  field_simp
  exact hp.trans (mul_comm _ _)

theorem entireSigned_addition {N k : ℕ} (hN : 0 < N) (hk : k < N)
    {omega rho : ℂ} (ho : IsPrimitiveRoot omega N) (hr : rho ^ N = -1)
    (z w : ℂ) :
    entireSigned N k omega rho (z + w) =
      ∑ i ∈ Finset.range N, ∑ j ∈ Finset.range N,
        if (i + j) % N = k then
          (-1 : ℂ) ^ ((i + j) / N) * entireSigned N i omega rho z *
            entireSigned N j omega rho w
        else 0 := by
  rw [entireSigned, entireTransfer_addition hN hk ho]
  simp_rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  split_ifs with h
  · rw [← h, signed_addition_weight hN hr]
    unfold entireSigned
    ring
  · simp

end
end Komorebi.PaperIV
