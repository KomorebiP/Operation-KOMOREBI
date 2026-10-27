import Mathlib.MeasureTheory.Function.L2Space
import Mathlib.MeasureTheory.SpecificCodomains.Pi
import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic
import Mathlib.Probability.ConditionalProbability
import Mathlib.Analysis.Matrix.Normed

/-! The covariance correction for averaging a quadratic matrix action. -/
set_option autoImplicit false

open MeasureTheory Matrix
open scoped BigOperators ENNReal MeasureTheory

namespace Komorebi.LSM.AveragedCongruence

variable {Ω : Type*} {mΩ : MeasurableSpace Ω} {ν : Measure Ω}
  [IsProbabilityMeasure ν]

theorem product_covariance {f g : Ω → ℝ} (hf : MemLp f 2 ν) (hg : MemLp g 2 ν) :
    (∫ ω, f ω * g ω ∂ν) = (∫ ω, f ω ∂ν) * (∫ ω, g ω ∂ν) +
      ∫ ω, (f ω - ∫ y, f y ∂ν) * (g ω - ∫ y, g y ∂ν) ∂ν := by
  have hfi : Integrable f ν := hf.integrable (by norm_num)
  have hgi : Integrable g ν := hg.integrable (by norm_num)
  have hfg : Integrable (fun ω => f ω * g ω) ν := hf.integrable_mul hg
  have heq : (fun ω => (f ω - ∫ y, f y ∂ν) * (g ω - ∫ y, g y ∂ν)) =
      (fun ω => f ω * g ω - f ω * (∫ y, g y ∂ν) -
        (∫ y, f y ∂ν) * g ω + (∫ y, f y ∂ν) * (∫ y, g y ∂ν)) := by
    funext ω
    ring
  rw [heq, integral_add
    (f := fun ω => f ω * g ω - f ω * (∫ y, g y ∂ν) - (∫ y, f y ∂ν) * g ω)
    (g := fun _ => (∫ y, f y ∂ν) * (∫ y, g y ∂ν))
    ((hfg.sub (hfi.mul_const _)).sub (hgi.const_mul _)) (integrable_const _),
    integral_sub
      (f := fun ω => f ω * g ω - f ω * (∫ y, g y ∂ν))
      (g := fun ω => (∫ y, f y ∂ν) * g ω)
      (hfg.sub (hfi.mul_const _)) (hgi.const_mul _),
    integral_sub (f := fun ω => f ω * g ω)
      (g := fun ω => f ω * (∫ y, g y ∂ν)) hfg (hfi.mul_const _),
    integral_mul_const, integral_const_mul]
  simp only [integral_const, probReal_univ, one_smul]
  ring

variable {M N : Type*} [Fintype M] [Fintype N]

/-- Matrix integration is taken in its finite coordinate space. -/
noncomputable def matrixMean (K : Ω → Matrix M N ℝ) : Matrix M N ℝ :=
  fun i j => ∫ ω, K ω i j ∂ν

omit [Fintype M] in
theorem congruence_entry (K : Matrix M N ℝ) (X : Matrix N N ℝ) (i j : M) :
    (K * X * K.transpose) i j = ∑ a, ∑ b, X a b * (K i a * K j b) := by
  simp only [Matrix.mul_apply, Matrix.transpose_apply, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro a _
  apply Finset.sum_congr rfl
  intro b _
  ring

omit [IsProbabilityMeasure ν] [Fintype M] in
theorem congruence_entry_integrable {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν) (X : Matrix N N ℝ) (i j : M) :
    Integrable (fun ω => (K ω * X * (K ω).transpose) i j) ν := by
  simp_rw [congruence_entry]
  apply integrable_finsetSum
  intro a _
  apply integrable_finsetSum
  intro b _
  exact ((hK i a).integrable_mul (hK j b)).const_mul (X a b)

omit [IsProbabilityMeasure ν] [Fintype M] in
theorem mean_congruence_entry {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν) (X : Matrix N N ℝ) (i j : M) :
    matrixMean (ν := ν) (fun ω => K ω * X * (K ω).transpose) i j =
      ∑ a, ∑ b, X a b * ∫ ω, K ω i a * K ω j b ∂ν := by
  unfold matrixMean
  simp_rw [congruence_entry]
  rw [integral_finsetSum]
  · apply Finset.sum_congr rfl
    intro a _
    rw [integral_finsetSum]
    · apply Finset.sum_congr rfl
      intro b _
      exact integral_const_mul _ _
    · intro b _
      exact ((hK i a).integrable_mul (hK j b)).const_mul (X a b)
  · intro a _
    exact integrable_finsetSum _ fun b _ =>
      ((hK i a).integrable_mul (hK j b)).const_mul (X a b)

omit [Fintype M] in
/-- P57 covariance identity. Matrix integrals are evaluated entry by entry,
the canonical finite-dimensional matrix integral. Symmetry of `X` is not
needed for the identity itself. -/
theorem averaged_congruence {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν) (X : Matrix N N ℝ) :
    matrixMean (ν := ν) (fun ω => K ω * X * (K ω).transpose) =
      matrixMean (ν := ν) K * X * (matrixMean (ν := ν) K).transpose +
      matrixMean (ν := ν) (fun ω => (K ω - matrixMean (ν := ν) K) * X *
        (K ω - matrixMean (ν := ν) K).transpose) := by
  have hc : ∀ i j, MemLp (fun ω => (K ω - matrixMean (ν := ν) K) i j) 2 ν := by
    intro i j
    exact (hK i j).sub (memLp_const _)
  ext i j
  rw [Matrix.add_apply, mean_congruence_entry hK X i j,
    congruence_entry, mean_congruence_entry hc X i j]
  change (∑ a, ∑ b, X a b * ∫ ω, K ω i a * K ω j b ∂ν) =
    (∑ a, ∑ b, X a b * ((∫ ω, K ω i a ∂ν) * (∫ ω, K ω j b ∂ν))) +
      ∑ a, ∑ b, X a b *
        ∫ ω, (K ω i a - ∫ y, K y i a ∂ν) * (K ω j b - ∫ y, K y j b ∂ν) ∂ν
  calc
    _ = ∑ a, ∑ b,
        (X a b * ((∫ ω, K ω i a ∂ν) * (∫ ω, K ω j b ∂ν)) +
          X a b * ∫ ω, (K ω i a - ∫ y, K y i a ∂ν) *
            (K ω j b - ∫ y, K y j b ∂ν) ∂ν) := by
      apply Finset.sum_congr rfl
      intro a _
      apply Finset.sum_congr rfl
      intro b _
      rw [product_covariance (hK i a) (hK j b), mul_add]
    _ = _ := by simp only [Finset.sum_add_distrib]

omit [IsProbabilityMeasure ν] [Fintype N] in
theorem mean_quadratic {A : Ω → Matrix M M ℝ}
    (hA : ∀ i j, Integrable (fun ω => A ω i j) ν) (x : M → ℝ) :
    star x ⬝ᵥ (matrixMean (ν := ν) A *ᵥ x) =
      ∫ ω, star x ⬝ᵥ (A ω *ᵥ x) ∂ν := by
  simp only [dotProduct, Matrix.mulVec, matrixMean, Finset.mul_sum]
  rw [integral_finsetSum]
  · apply Finset.sum_congr rfl
    intro i _
    rw [integral_finsetSum]
    · apply Finset.sum_congr rfl
      intro j _
      rw [integral_const_mul, integral_mul_const]
    · intro j _
      exact ((hA i j).mul_const (x j)).const_mul (star (x i))
  · intro i _
    exact integrable_finsetSum _ fun j _ =>
      ((hA i j).mul_const (x j)).const_mul (star (x i))

omit [IsProbabilityMeasure ν] [Fintype N] in
/-- Integrating a finite real positive-semidefinite matrix family preserves
positive semidefiniteness. -/
theorem matrixMean_posSemidef {A : Ω → Matrix M M ℝ}
    (hAi : ∀ i j, Integrable (fun ω => A ω i j) ν)
    (hA : ∀ ω, (A ω).PosSemidef) : (matrixMean (ν := ν) A).PosSemidef := by
  apply Matrix.PosSemidef.of_dotProduct_mulVec_nonneg
  · ext i j
    change (∫ ω, A ω j i ∂ν) = ∫ ω, A ω i j ∂ν
    apply integral_congr_ae
    filter_upwards with ω
    have hs := congrArg (fun B : Matrix M M ℝ => B i j) (hA ω).isHermitian
    simpa only [Matrix.conjTranspose_apply, star_trivial] using hs
  · intro x
    rw [mean_quadratic hAi x]
    exact integral_nonneg fun ω => (hA ω).dotProduct_mulVec_nonneg x

/-- The P57 covariance correction is positive semidefinite whenever `X` is. -/
theorem covariance_correction_posSemidef {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν)
    {X : Matrix N N ℝ} (hX : X.PosSemidef) :
    (matrixMean (ν := ν) (fun ω => (K ω - matrixMean (ν := ν) K) * X *
      (K ω - matrixMean (ν := ν) K).transpose)).PosSemidef := by
  have hc : ∀ i j, MemLp (fun ω => (K ω - matrixMean (ν := ν) K) i j) 2 ν := by
    intro i j
    exact (hK i j).sub (memLp_const _)
  refine matrixMean_posSemidef (fun i j => congruence_entry_integrable hc X i j) ?_
  intro ω
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    hX.mul_mul_conjTranspose_same (K ω - matrixMean (ν := ν) K)

omit [Fintype M] [Fintype N] in
theorem mean_affine_matrix {u : Ω → ℝ} (hu : MemLp u 2 ν)
    (K₀ K₁ : Matrix M N ℝ) :
    matrixMean (ν := ν) (fun ω => K₀ + u ω • K₁) =
      K₀ + (∫ ω, u ω ∂ν) • K₁ := by
  ext i j
  change (∫ ω, K₀ i j + u ω * K₁ i j ∂ν) = K₀ i j + (∫ ω, u ω ∂ν) * K₁ i j
  rw [integral_add (integrable_const _) ((hu.integrable (by norm_num)).mul_const _),
    integral_mul_const]
  simp

omit [Fintype M] [Fintype N] in
theorem affine_entries_memLp {u : Ω → ℝ} (hu : MemLp u 2 ν)
    (K₀ K₁ : Matrix M N ℝ) (i : M) (j : N) :
    MemLp (fun ω => (K₀ + u ω • K₁) i j) 2 ν :=
  (memLp_const (K₀ i j)).add (hu.mul_const (K₁ i j))

omit [Fintype M] in
/-- For an affine transformation family the correction is its scalar
variance times one fixed positive congruence. -/
theorem affine_covariance_correction {u : Ω → ℝ} (hu : MemLp u 2 ν)
    (K₀ K₁ : Matrix M N ℝ) (X : Matrix N N ℝ) :
    matrixMean (ν := ν) (fun ω =>
      ((K₀ + u ω • K₁) - matrixMean (ν := ν) (fun y => K₀ + u y • K₁)) * X *
      ((K₀ + u ω • K₁) - matrixMean (ν := ν) (fun y => K₀ + u y • K₁)).transpose) =
      (∫ ω, (u ω - ∫ y, u y ∂ν) ^ 2 ∂ν) • (K₁ * X * K₁.transpose) := by
  have hc (ω : Ω) : (K₀ + u ω • K₁) -
      matrixMean (ν := ν) (fun y => K₀ + u y • K₁) =
      (u ω - ∫ y, u y ∂ν) • K₁ := by
    rw [mean_affine_matrix hu K₀ K₁]
    ext i j
    simp only [Matrix.sub_apply, Matrix.add_apply, Matrix.smul_apply, smul_eq_mul]
    ring
  simp_rw [hc, Matrix.transpose_smul, Matrix.smul_mul, Matrix.mul_smul, smul_smul,
    ← pow_two]
  ext i j
  exact integral_mul_const _ _

/-- The uniform probability measure on a nondegenerate real interval. -/
noncomputable def uniformInterval (a b : ℝ) : Measure ℝ :=
  ProbabilityTheory.cond volume (Set.Ioc a b)

theorem uniformInterval_isProbability {a b : ℝ} (hab : a < b) :
    IsProbabilityMeasure (uniformInterval a b) := by
  apply ProbabilityTheory.cond_isProbabilityMeasure_of_finite
  · rw [Real.volume_Ioc]
    exact ne_of_gt (ENNReal.ofReal_pos.mpr (sub_pos.mpr hab))
  · rw [Real.volume_Ioc]
    exact ENNReal.ofReal_ne_top

theorem integral_uniformInterval {a b : ℝ} (hab : a < b) (f : ℝ → ℝ) :
    (∫ x, f x ∂uniformInterval a b) = (b - a)⁻¹ * ∫ x in a..b, f x := by
  rw [uniformInterval, ProbabilityTheory.cond, integral_smul_measure, Real.volume_Ioc,
    ENNReal.toReal_inv, ENNReal.toReal_ofReal (sub_nonneg.mpr hab.le),
    ← intervalIntegral.integral_of_le hab.le]
  rfl

theorem uniformInterval_mean {a b : ℝ} (hab : a < b) :
    (∫ x, x ∂uniformInterval a b) = (a + b) / 2 := by
  rw [integral_uniformInterval hab, integral_id]
  field_simp [ne_of_gt (sub_pos.mpr hab)]
  ring

/-- The exact variance of an interval-uniform random variable is width
squared divided by twelve. -/
theorem uniformInterval_variance {a b : ℝ} (hab : a < b) :
    (∫ x, (x - ∫ y, y ∂uniformInterval a b) ^ 2 ∂uniformInterval a b) =
      (b - a) ^ 2 / 12 := by
  rw [uniformInterval_mean hab, integral_uniformInterval hab]
  have hpoly : (fun x : ℝ => (x - (a + b) / 2) ^ 2) =
      (fun x => x ^ 2 - (a + b) * x + ((a + b) / 2) ^ 2) := by
    funext x
    ring
  have hsq : IntervalIntegrable (fun x : ℝ => x ^ 2) volume a b :=
    (continuous_id.pow 2).intervalIntegrable a b
  have hlin : IntervalIntegrable (fun x : ℝ => (a + b) * x) volume a b :=
    (continuous_const.mul continuous_id).intervalIntegrable a b
  rw [hpoly, intervalIntegral.integral_add (f := fun x : ℝ => x ^ 2 - (a + b) * x)
    (g := fun _ : ℝ => ((a + b) / 2) ^ 2) (hsq.sub hlin) intervalIntegrable_const,
    intervalIntegral.integral_sub hsq hlin, integral_pow,
    intervalIntegral.integral_const_mul, integral_id, intervalIntegral.integral_const]
  simp only [smul_eq_mul]
  field_simp [ne_of_gt (sub_pos.mpr hab)]
  ring

theorem uniformInterval_id_memLp {a b : ℝ} (hab : a < b) :
    MemLp (fun x : ℝ => x) 2 (uniformInterval a b) := by
  have hs : Integrable (fun x : ℝ => x ^ 2) (volume.restrict (Set.Ioc a b)) :=
    ((continuous_id.pow 2).intervalIntegrable a b).1
  have hi : MemLp (fun x : ℝ => x) 2 (volume.restrict (Set.Ioc a b)) :=
    (memLp_two_iff_integrable_sq continuous_id.aestronglyMeasurable).mpr hs
  apply hi.smul_measure
  rw [ENNReal.inv_ne_top, Real.volume_Ioc]
  exact ne_of_gt (ENNReal.ofReal_pos.mpr (sub_pos.mpr hab))

omit [IsProbabilityMeasure ν] [Fintype M] in
/-- The interval-uniform specialization includes the derived `h²/12`
coefficient, with `h = b-a`, rather than assuming a variance oracle. -/
theorem uniformInterval_affine_correction {a b : ℝ} (hab : a < b)
    (K₀ K₁ : Matrix M N ℝ) (X : Matrix N N ℝ) :
    matrixMean (ν := uniformInterval a b) (fun u =>
      ((K₀ + u • K₁) - matrixMean (ν := uniformInterval a b) (fun v => K₀ + v • K₁)) * X *
      ((K₀ + u • K₁) - matrixMean (ν := uniformInterval a b) (fun v => K₀ + v • K₁)).transpose) =
      ((b - a) ^ 2 / 12) • (K₁ * X * K₁.transpose) := by
  let := uniformInterval_isProbability hab
  rw [affine_covariance_correction (uniformInterval_id_memLp hab), uniformInterval_variance hab]

section BochnerBridge

open scoped Matrix.Norms.Elementwise

set_option backward.isDefEq.respectTransparency false in
omit [IsProbabilityMeasure ν] in
/-- Entrywise integrability gives integrability in the actual finite matrix
space with its standard product topology and elementwise norm. -/
theorem matrix_integrable_of_entries {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, Integrable (fun ω => K ω i j) ν) : Integrable K ν := by
  change Integrable (fun ω i j => K ω i j) ν
  exact Integrable.of_eval (fun i => Integrable.of_eval (hK i))

set_option backward.isDefEq.respectTransparency false in
omit [IsProbabilityMeasure ν] in
/-- The coordinate matrix integral is exactly the Bochner matrix integral. -/
theorem matrixMean_eq_integral {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, Integrable (fun ω => K ω i j) ν) :
    matrixMean (ν := ν) K = ∫ ω, K ω ∂ν := by
  ext i j
  change (∫ ω, K ω i j ∂ν) = (∫ ω, K ω ∂ν) i j
  rw [eval_integral (fun i => Integrable.of_eval (hK i)) i]
  exact (eval_integral (hK i) j).symm

set_option backward.isDefEq.respectTransparency false in
/-- The manuscript's L2-entry hypothesis supplies matrix integrability; it
is not an extra input to the covariance theorem. -/
theorem matrix_integrable_of_memLp_entries {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν) : Integrable K ν :=
  matrix_integrable_of_entries (fun i j => (hK i j).integrable (by norm_num))

set_option backward.isDefEq.respectTransparency false in
/-- P57 written directly with Bochner matrix integrals. -/
theorem averaged_congruence_integral {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν) (X : Matrix N N ℝ) :
    (∫ ω, K ω * X * (K ω).transpose ∂ν) =
      (∫ ω, K ω ∂ν) * X * (∫ ω, K ω ∂ν).transpose +
      ∫ ω, (K ω - ∫ y, K y ∂ν) * X * (K ω - ∫ y, K y ∂ν).transpose ∂ν := by
  have hKi : ∀ i j, Integrable (fun ω => K ω i j) ν :=
    fun i j => (hK i j).integrable (by norm_num)
  have hc : ∀ i j, MemLp (fun ω => (K ω - matrixMean (ν := ν) K) i j) 2 ν := by
    intro i j
    exact (hK i j).sub (memLp_const _)
  have h := averaged_congruence hK X
  rw [matrixMean_eq_integral (fun i j => congruence_entry_integrable hK X i j),
    matrixMean_eq_integral (fun i j => congruence_entry_integrable hc X i j),
    matrixMean_eq_integral hKi] at h
  exact h

set_option backward.isDefEq.respectTransparency false in
/-- The positive covariance correction in the same Bochner-integral
dictionary as the manuscript. -/
theorem covariance_integral_posSemidef {K : Ω → Matrix M N ℝ}
    (hK : ∀ i j, MemLp (fun ω => K ω i j) 2 ν)
    {X : Matrix N N ℝ} (hX : X.PosSemidef) :
    (∫ ω, (K ω - ∫ y, K y ∂ν) * X *
      (K ω - ∫ y, K y ∂ν).transpose ∂ν).PosSemidef := by
  have hc : ∀ i j, MemLp (fun ω => (K ω - matrixMean (ν := ν) K) i j) 2 ν := by
    intro i j
    exact (hK i j).sub (memLp_const _)
  have h := covariance_correction_posSemidef hK hX
  rw [matrixMean_eq_integral (fun i j => congruence_entry_integrable hc X i j),
    matrixMean_eq_integral (fun i j => (hK i j).integrable (by norm_num))] at h
  exact h

end BochnerBridge

end Komorebi.LSM.AveragedCongruence
