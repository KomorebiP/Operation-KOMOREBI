/-
Finite-fibre summation tools for the Paper X fixed-field density block.
The constant-fibre argument follows the attributed AINTLIB fixed-field reduction.
-/
module
public import CebotarevDensity.FixedFieldFibres
public import Mathlib.RingTheory.RamificationInertia.Basic

@[expose] public section
noncomputable section
open Filter NumberField Topology Set
namespace Chebotarev.FixedFieldSumTools

/-- Exact summation through a map whose finite fibres have a constant cardinality. -/
theorem tsum_comp_eq_card_fibre_mul {β γ : Type*} (g : β → γ) (h : γ → ℝ) (c : ℝ)
    (hsumm : Summable fun b ↦ h (g b)) (hfin : ∀ y, Finite (g ⁻¹' {y} : Set β))
    (hcard : ∀ y, (Nat.card (g ⁻¹' {y} : Set β) : ℝ) = c) :
    ∑' b, h (g b) = c * ∑' y, h y := by
  rw [← (hsumm.hasSum.tsum_fiberwise g).tsum_eq, ← tsum_mul_left]
  refine tsum_congr fun y ↦ ?_
  have := hfin y
  let := Fintype.ofFinite (g ⁻¹' {y} : Set β)
  rw [tsum_congr fun b : (g ⁻¹' {y} : Set β) ↦ congrArg h b.2, tsum_fintype,
    Finset.sum_const, Finset.card_univ, ← Nat.card_eq_fintype_card, nsmul_eq_mul,
    hcard, mul_comm]

/-- A summable nonnegative majorant with uniformly bounded finite fibres controls the total. -/
theorem tsum_le_card_fibre_mul {β γ : Type*} (g : β → γ) (A : β → ℝ)
    (B : γ → ℝ) (d : ℕ) (hA : Summable A) (hB : Summable B)
    (hB0 : ∀ y, 0 ≤ B y) (hterm : ∀ b, A b ≤ B (g b))
    (hfin : ∀ y, Finite (g ⁻¹' {y} : Set β))
    (hcard : ∀ y, Nat.card (g ⁻¹' {y} : Set β) ≤ d) :
    ∑' b, A b ≤ (d : ℝ) * ∑' y, B y := by
  rw [← (hA.hasSum.tsum_fiberwise g).tsum_eq, ← tsum_mul_left]
  refine Summable.tsum_le_tsum (fun y ↦ ?_) (hA.hasSum.tsum_fiberwise g).summable
    (hB.mul_left (d : ℝ))
  have := hfin y
  let := Fintype.ofFinite (g ⁻¹' {y} : Set β)
  rw [tsum_fintype]
  calc ∑ b : (g ⁻¹' {y} : Set β), A b.1
      ≤ ∑ _b : (g ⁻¹' {y} : Set β), B y :=
        Finset.sum_le_sum fun b _ ↦ (hterm b.1).trans_eq (congrArg B b.2)
    _ = (Nat.card (g ⁻¹' {y} : Set β) : ℝ) * B y := by
        rw [Finset.sum_const, Finset.card_univ, nsmul_eq_mul, Nat.card_eq_fintype_card]
    _ ≤ (d : ℝ) * B y := mul_le_mul_of_nonneg_right (by exact_mod_cast hcard y) (hB0 y)

/-- The prime-sum normalizers of any two number fields have asymptotic ratio one. -/
theorem prime_normalizer_ratio (K M : Type*) [Field K] [NumberField K]
    [Field M] [NumberField M] :
    Tendsto (fun s : ℝ ↦ primeIdealZetaSum (univ : Set (Ideal (𝓞 M))) s /
      primeIdealZetaSum (univ : Set (Ideal (𝓞 K))) s) (𝓝[>] 1) (𝓝 1) := by
  have h := (primeIdealZetaSum_univ_tendsto_log M).div
    (primeIdealZetaSum_univ_tendsto_log K) one_ne_zero
  rw [one_div_one] at h
  refine h.congr' ?_
  filter_upwards [tendsto_log_one_div_sub_one_atTop.eventually_gt_atTop 0] with s hs
  simp only [Pi.div_apply]
  rw [div_div_div_cancel_right₀ hs.ne']

end Chebotarev.FixedFieldSumTools
