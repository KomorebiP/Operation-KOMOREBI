/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NormalizedGrowth

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical

/-- Every signed or unsigned residue weight leaves the dominant vertex term
unchanged on the positive real ray. -/
theorem entireTransfer_positive_ray {N : ℕ} (hN : 0 < N) (j : ℕ)
    {ω : ℂ} (hω : IsPrimitiveRoot ω N) :
    Tendsto (fun r : ℝ => (N : ℂ) * Complex.exp (-(r : ℂ)) * entireTransfer N j ω 1 r)
      atTop (𝓝 1) := by
  have hw : ‖ω‖ = 1 := Complex.norm_eq_one_of_pow_eq_one hω.pow_eq_one hN.ne'
  have hk (k : ℕ) (hk : k ∈ (Finset.range N).erase 0) : (ω ^ k - 1).re < 0 := by
    have hne : ω ^ k ≠ 1 := by
      intro he
      have := hω.pow_inj (Finset.mem_range.mp (Finset.mem_erase.mp hk).2) hN (he.trans (pow_zero ω).symm)
      exact (Finset.mem_erase.mp hk).1 this
    have := unit_complex_re_lt_one (by simp [norm_pow, hw]) hne
    simpa using sub_neg.mpr this
  have ht (k : ℕ) (hk' : k ∈ (Finset.range N).erase 0) :
      Tendsto (fun r : ℝ => ((ω ^ j)⁻¹) ^ k * Complex.exp ((ω ^ k - 1) * (r : ℂ))) atTop (𝓝 0) := by
    have he : Tendsto (fun r : ℝ => Complex.exp ((ω ^ k - 1) * (r : ℂ))) atTop (𝓝 0) := by
      apply tendsto_zero_iff_norm_tendsto_zero.mpr
      simp only [Complex.norm_exp, Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im, mul_zero, sub_zero]
      exact Real.tendsto_exp_atBot.comp (tendsto_id.const_mul_atTop_of_neg (hk k hk'))
    simpa using he.const_mul (((ω ^ j)⁻¹) ^ k)
  have htall := tendsto_finsetSum (s := (Finset.range N).erase 0) (fun k hk => ht k hk)
  have htotal : Tendsto (fun r : ℝ =>
      (∑ k ∈ (Finset.range N).erase 0, ((ω ^ j)⁻¹) ^ k * Complex.exp ((ω ^ k - 1) * (r : ℂ))) + 1)
      atTop (𝓝 1) := by simpa using htall.add_const 1
  apply htotal.congr
  intro r
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
  have he : (N : ℂ) * Complex.exp (-(r : ℂ)) * entireTransfer N j ω 1 r =
      ∑ k ∈ Finset.range N, ((ω ^ j)⁻¹) ^ k * Complex.exp ((ω ^ k - 1) * (r : ℂ)) := by
    calc
      _ = Complex.exp (-(r : ℂ)) *
          ∑ k ∈ Finset.range N, ((ω ^ j)⁻¹) ^ k * Complex.exp (ω ^ k * (r : ℂ)) := by
        unfold entireTransfer
        simp only [one_mul]
        field_simp
      _ = ∑ k ∈ Finset.range N, Complex.exp (-(r : ℂ)) *
          (((ω ^ j)⁻¹) ^ k * Complex.exp (ω ^ k * (r : ℂ))) := Finset.mul_sum ..
      _ = _ := by
        apply Finset.sum_congr rfl
        intro k _
        rw [mul_left_comm, ← Complex.exp_add]
        congr 2
        ring
  rw [he]
  simpa using (Finset.sum_erase_add (Finset.range N) (fun k => ((ω ^ j)⁻¹) ^ k *
    Complex.exp ((ω ^ k - 1) * (r : ℂ))) (Finset.mem_range.mpr hN))

end
end Komorebi.PaperIV
