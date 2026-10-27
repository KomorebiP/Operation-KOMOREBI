import AVOC.BayesianEvidence
import AVOC.ApproximateStochastic
import Mathlib.Tactic.FieldSimp
import Mathlib.Algebra.Order.Field.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace Komorebi.AVOC

universe u

/-- L1 distance between two finite rational beliefs. -/
def beliefL1Distance
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω) : ℚ :=
  ∑ ω, |b.prob ω - c.prob ω|

/-- Belief L1 distance is nonnegative. -/
theorem beliefL1Distance_nonneg
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω) : 0 ≤ beliefL1Distance b c := by
  unfold beliefL1Distance
  apply Finset.sum_nonneg
  intro ω hω
  exact abs_nonneg _

/-- Total-mass difference is bounded by L1 row difference. -/
theorem abs_sum_sub_sum_le_sum_abs_sub
    {Ω : Type u} [Fintype Ω]
    (p q : Ω → ℚ) :
    |(∑ ω, p ω) - ∑ ω, q ω| ≤ ∑ ω, |p ω - q ω| := by
  rw [← Finset.sum_sub_distrib]
  simpa using Finset.abs_sum_le_sum_abs (fun ω => p ω - q ω) Finset.univ

/-- Normalizing two nonnegative finite rows is stable away from zero mass.
The asymmetric denominator `Z` is enough; both rows must have positive mass. -/
theorem normalized_l1_le_two_over_mass
    {Ω : Type u} [Fintype Ω]
    (p q : Ω → ℚ)
    (_hp : ∀ ω, 0 ≤ p ω) (hq : ∀ ω, 0 ≤ q ω)
    (Z W D ζ : ℚ)
    (hZ : Z = ∑ ω, p ω) (hW : W = ∑ ω, q ω)
    (hZpos : 0 < Z) (hWpos : 0 < W)
    (hD : ∑ ω, |p ω - q ω| ≤ D)
    (hDnonneg : 0 ≤ D)
    (hζ : 0 < ζ) (hζZ : ζ ≤ Z) :
    (∑ ω, |p ω / Z - q ω / W|) ≤ 2 * D / ζ := by
  have hZW : |W - Z| ≤ D := by
    calc
      |W - Z| = |Z - W| := by rw [abs_sub_comm]
      _ = |(∑ ω, p ω) - ∑ ω, q ω| := by rw [← hZ, ← hW]
      _ ≤ ∑ ω, |p ω - q ω| := abs_sum_sub_sum_le_sum_abs_sub p q
      _ ≤ D := hD
  have hpoint : ∀ ω,
      |p ω / Z - q ω / W| ≤
        |p ω - q ω| / Z + q ω * |W - Z| / (Z * W) := by
    intro ω
    have hZne : Z ≠ 0 := ne_of_gt hZpos
    have hWne : W ≠ 0 := ne_of_gt hWpos
    have hZWpos : 0 < Z * W := mul_pos hZpos hWpos
    have hdecomp :
        p ω / Z - q ω / W =
          (p ω - q ω) / Z + q ω * (W - Z) / (Z * W) := by
      field_simp [hZne, hWne]
      ring
    rw [hdecomp]
    calc
      |(p ω - q ω) / Z + q ω * (W - Z) / (Z * W)|
          ≤ |(p ω - q ω) / Z| + |q ω * (W - Z) / (Z * W)| := abs_add_le _ _
      _ = |p ω - q ω| / Z + q ω * |W - Z| / (Z * W) := by
        rw [abs_div, abs_div, abs_mul]
        rw [abs_of_pos hZpos, abs_of_pos hZWpos, abs_of_nonneg (hq ω)]
  calc
    (∑ ω, |p ω / Z - q ω / W|)
        ≤ ∑ ω, (|p ω - q ω| / Z + q ω * |W - Z| / (Z * W)) := by
          exact Finset.sum_le_sum (fun ω _ => hpoint ω)
    _ = (∑ ω, |p ω - q ω|) / Z +
        (∑ ω, q ω) * |W - Z| / (Z * W) := by
          rw [Finset.sum_add_distrib]
          have h1 : (∑ x : Ω, |p x - q x| / Z) =
              (∑ x : Ω, |p x - q x|) / Z := by
            change (∑ x : Ω, |p x - q x| * Z⁻¹) =
              (∑ x : Ω, |p x - q x|) * Z⁻¹
            exact (Finset.sum_mul Finset.univ (fun x : Ω => |p x - q x|) Z⁻¹).symm
          have h2 : (∑ x : Ω, q x * |W - Z| / (Z * W)) =
              (∑ x : Ω, q x) * |W - Z| / (Z * W) := by
            have hterm : ∀ x : Ω,
                q x * |W - Z| / (Z * W) = q x * (|W - Z| / (Z * W)) := by
              intro x
              ring
            simp_rw [hterm]
            rw [← Finset.sum_mul]
            ring
          rw [h1, h2]
    _ = (∑ ω, |p ω - q ω|) / Z + |W - Z| / Z := by
          rw [← hW]
          field_simp [ne_of_gt hWpos]
    _ ≤ D / Z + D / Z := by
          apply add_le_add
          · exact div_le_div_of_nonneg_right hD (le_of_lt hZpos)
          · exact div_le_div_of_nonneg_right hZW (le_of_lt hZpos)
    _ = 2 * D / Z := by ring
    _ ≤ 2 * D / ζ := by
          have h2D : 0 ≤ 2 * D := by positivity
          exact div_le_div_of_nonneg_left h2D hζ hζZ

/-- A pointwise likelihood perturbation of size `β` changes the unnormalized
Bayes numerator row by L1 at most `β` under a normalized prior. -/
theorem bayes_numerator_l1_le
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (L M : Ω → ℚ) (β : ℚ)
    (hβ : ∀ ω, |L ω - M ω| ≤ β) :
    (∑ ω, |b.prob ω * L ω - b.prob ω * M ω|) ≤ β := by
  calc
    (∑ ω, |b.prob ω * L ω - b.prob ω * M ω|)
        = ∑ ω, b.prob ω * |L ω - M ω| := by
            apply Finset.sum_congr rfl
            intro ω hω
            rw [← mul_sub, abs_mul, abs_of_nonneg (b.nonneg ω)]
    _ ≤ ∑ ω, b.prob ω * β := by
          apply Finset.sum_le_sum
          intro ω hω
          exact mul_le_mul_of_nonneg_left (hβ ω) (b.nonneg ω)
    _ = β := by
          rw [← Finset.sum_mul, b.sum_one]
          simp

/-- Posterior stability under likelihood perturbation away from zero evidence. -/
theorem conditionByWeight_l1_stability_likelihood
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (L M : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω) (hM : ∀ ω, 0 ≤ M ω)
    (β ζ : ℚ)
    (hβnonneg : 0 ≤ β)
    (hβ : ∀ ω, |L ω - M ω| ≤ β)
    (hζ : 0 < ζ)
    (hLmass : ζ ≤ evidenceMass b L)
    (hMmass : ζ ≤ evidenceMass b M) :
    beliefL1Distance
        (conditionByWeight b L hL (lt_of_lt_of_le hζ hLmass))
        (conditionByWeight b M hM (lt_of_lt_of_le hζ hMmass))
      ≤ 2 * β / ζ := by
  let p : Ω → ℚ := fun ω => b.prob ω * L ω
  let q : Ω → ℚ := fun ω => b.prob ω * M ω
  have hp : ∀ ω, 0 ≤ p ω := fun ω => mul_nonneg (b.nonneg ω) (hL ω)
  have hq : ∀ ω, 0 ≤ q ω := fun ω => mul_nonneg (b.nonneg ω) (hM ω)
  have hrow : (∑ ω, |p ω - q ω|) ≤ β := by
    simpa [p, q] using bayes_numerator_l1_le b L M β hβ
  unfold beliefL1Distance
  change (∑ ω,
    |p ω / evidenceMass b L - q ω / evidenceMass b M|) ≤ 2 * β / ζ
  exact normalized_l1_le_two_over_mass p q hp hq
    (evidenceMass b L) (evidenceMass b M) β ζ
    (by simp [p, evidenceMass]) (by simp [q, evidenceMass])
    (lt_of_lt_of_le hζ hLmass) (lt_of_lt_of_le hζ hMmass)
    hrow hβnonneg hζ hLmass

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u

/-- A bounded nonnegative likelihood converts prior L1 error into numerator L1 error. -/
theorem bayes_numerator_l1_le_of_prior_error
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω) (L : Ω → ℚ)
    (K α : ℚ)
    (hL : ∀ ω, 0 ≤ L ω)
    (hK : 0 ≤ K)
    (hLK : ∀ ω, L ω ≤ K)
    (hprior : beliefL1Distance b c ≤ α) :
    (∑ ω, |b.prob ω * L ω - c.prob ω * L ω|) ≤ K * α := by
  calc
    (∑ ω, |b.prob ω * L ω - c.prob ω * L ω|)
        = ∑ ω, |b.prob ω - c.prob ω| * L ω := by
            apply Finset.sum_congr rfl
            intro ω hω
            rw [← sub_mul, abs_mul, abs_of_nonneg (hL ω)]
    _ ≤ ∑ ω, |b.prob ω - c.prob ω| * K := by
          apply Finset.sum_le_sum
          intro ω hω
          exact mul_le_mul_of_nonneg_left (hLK ω) (abs_nonneg _)
    _ = beliefL1Distance b c * K := by
          unfold beliefL1Distance
          rw [Finset.sum_mul]
    _ ≤ α * K := by
          exact mul_le_mul_of_nonneg_right hprior hK
    _ = K * α := by ring

/-- Prior perturbation stability under a bounded likelihood and positive evidence. -/
theorem conditionByWeight_l1_stability_prior
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω)
    (L : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω)
    (K α ζ : ℚ)
    (hK : 0 ≤ K)
    (hLK : ∀ ω, L ω ≤ K)
    (hα : 0 ≤ α)
    (hprior : beliefL1Distance b c ≤ α)
    (hζ : 0 < ζ)
    (hbmass : ζ ≤ evidenceMass b L)
    (hcmass : ζ ≤ evidenceMass c L) :
    beliefL1Distance
        (conditionByWeight b L hL (lt_of_lt_of_le hζ hbmass))
        (conditionByWeight c L hL (lt_of_lt_of_le hζ hcmass))
      ≤ 2 * (K * α) / ζ := by
  let p : Ω → ℚ := fun ω => b.prob ω * L ω
  let q : Ω → ℚ := fun ω => c.prob ω * L ω
  have hp : ∀ ω, 0 ≤ p ω := fun ω => mul_nonneg (b.nonneg ω) (hL ω)
  have hq : ∀ ω, 0 ≤ q ω := fun ω => mul_nonneg (c.nonneg ω) (hL ω)
  have hrow : (∑ ω, |p ω - q ω|) ≤ K * α := by
    simpa [p, q] using bayes_numerator_l1_le_of_prior_error b c L K α hL hK hLK hprior
  unfold beliefL1Distance
  change (∑ ω,
    |p ω / evidenceMass b L - q ω / evidenceMass c L|) ≤ 2 * (K * α) / ζ
  exact normalized_l1_le_two_over_mass p q hp hq
    (evidenceMass b L) (evidenceMass c L) (K * α) ζ
    (by simp [p, evidenceMass]) (by simp [q, evidenceMass])
    (lt_of_lt_of_le hζ hbmass) (lt_of_lt_of_le hζ hcmass)
    hrow (mul_nonneg hK hα) hζ hbmass

/-- Combined prior-and-likelihood perturbation bound, routed through the
intermediate posterior using the perturbed likelihood under the original prior. -/
theorem conditionByWeight_l1_stability_combined
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω)
    (L M : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω) (hM : ∀ ω, 0 ≤ M ω)
    (K α β ζ : ℚ)
    (hK : 0 ≤ K) (hMK : ∀ ω, M ω ≤ K)
    (hα : 0 ≤ α) (hprior : beliefL1Distance b c ≤ α)
    (hβ : 0 ≤ β) (hlik : ∀ ω, |L ω - M ω| ≤ β)
    (hζ : 0 < ζ)
    (hbL : ζ ≤ evidenceMass b L)
    (hbM : ζ ≤ evidenceMass b M)
    (hcM : ζ ≤ evidenceMass c M) :
    beliefL1Distance
        (conditionByWeight b L hL (lt_of_lt_of_le hζ hbL))
        (conditionByWeight c M hM (lt_of_lt_of_le hζ hcM))
      ≤ 2 * β / ζ + 2 * (K * α) / ζ := by
  let pL := conditionByWeight b L hL (lt_of_lt_of_le hζ hbL)
  let pM := conditionByWeight b M hM (lt_of_lt_of_le hζ hbM)
  let qM := conditionByWeight c M hM (lt_of_lt_of_le hζ hcM)
  have h1 : beliefL1Distance pL pM ≤ 2 * β / ζ := by
    simpa [pL, pM] using conditionByWeight_l1_stability_likelihood
      b L M hL hM β ζ hβ hlik hζ hbL hbM
  have h2 : beliefL1Distance pM qM ≤ 2 * (K * α) / ζ := by
    simpa [pM, qM] using conditionByWeight_l1_stability_prior
      b c M hM K α ζ hK hMK hα hprior hζ hbM hcM
  unfold beliefL1Distance at h1 h2 ⊢
  calc
    (∑ ω, |pL.prob ω - qM.prob ω|)
        ≤ ∑ ω, (|pL.prob ω - pM.prob ω| + |pM.prob ω - qM.prob ω|) := by
          apply Finset.sum_le_sum
          intro ω hω
          have := abs_sub_le (pL.prob ω) (pM.prob ω) (qM.prob ω)
          simpa [sub_eq_add_neg, add_assoc] using this
    _ = (∑ ω, |pL.prob ω - pM.prob ω|) +
        (∑ ω, |pM.prob ω - qM.prob ω|) := by
          rw [Finset.sum_add_distrib]
    _ ≤ 2 * β / ζ + 2 * (K * α) / ζ := add_le_add h1 h2

end Komorebi.AVOC
