module

public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Topology.Algebra.Monoid
public import Mathlib.Topology.Order.OrderClosed
public import Mathlib.NumberTheory.NumberField.DedekindZeta

/-!
# Residue domination for a finite factorization

This module proves a nonvanishing assembly lemma, not Chebotarev's theorem.
No occurrence, density, or Artin analytic-extension theorem is assumed by the
abstract comparison. The number-field specialization uses the actual Dedekind
zeta functions and Mathlib's positive residues. Factorization, domination, and
the finite limits of the other factors remain explicit hypotheses.
-/

@[expose] public section

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology BigOperators

namespace PaperX.ResidueDomination

section Abstract
variable {α I : Type*} [Fintype I] {l : Filter α} [l.NeBot]
variable {w Z T U R : α → ℂ} {F : I → α → ℂ}
variable {a b r : ℂ} {v : I → ℂ}

/-- A nonzero normalized product cannot disappear when its potentially singular
factor is dominated by another normalized function with a finite limit. -/
theorem normalized_product_bound
    (hZ : Tendsto (fun x => w x * Z x) l (𝓝 a))
    (hU : Tendsto U l (𝓝 b))
    (hR : Tendsto R l (𝓝 r))
    (hF : ∀ i, Tendsto (F i) l (𝓝 (v i)))
    (hfactor : ∀ᶠ x in l, Z x = T x * (R x * ∏ i, F i x))
    (hdom : ∀ᶠ x in l, ‖w x * T x‖ ≤ ‖U x‖) :
    ‖a‖ ≤ ‖b‖ * ‖r * ∏ i, v i‖ := by
  have hp : Tendsto (fun x => ∏ i, F i x) l (𝓝 (∏ i, v i)) :=
    tendsto_finsetProd Finset.univ (fun i _ => hF i)
  apply le_of_tendsto_of_tendsto hZ.norm (hU.norm.mul (hR.mul hp).norm)
  filter_upwards [hfactor, hdom] with x hx hd
  calc
    ‖w x * Z x‖ = ‖w x * T x‖ * ‖R x * ∏ i, F i x‖ := by
      rw [hx, ← mul_assoc, norm_mul]
    _ ≤ ‖U x‖ * ‖R x * ∏ i, F i x‖ :=
      mul_le_mul_of_nonneg_right hd (norm_nonneg _)

/-- A nonzero residue forces the limiting correction and every limiting factor
to be nonzero. No limit of the singular factor `w * T` is required. -/
theorem factors_nonzero
    (hZ : Tendsto (fun x => w x * Z x) l (𝓝 a))
    (hU : Tendsto U l (𝓝 b))
    (hR : Tendsto R l (𝓝 r))
    (hF : ∀ i, Tendsto (F i) l (𝓝 (v i)))
    (hfactor : ∀ᶠ x in l, Z x = T x * (R x * ∏ i, F i x))
    (hdom : ∀ᶠ x in l, ‖w x * T x‖ ≤ ‖U x‖)
    (ha : a ≠ 0) :
    r ≠ 0 ∧ ∀ i, v i ≠ 0 := by
  classical
  have hb := normalized_product_bound hZ hU hR hF hfactor hdom
  have hp : r * ∏ i, v i ≠ 0 := by
    intro hz
    have hz' : ‖a‖ ≤ 0 := by simpa only [hz, norm_zero, mul_zero] using hb
    exact (not_le_of_gt (norm_pos_iff.mpr ha)) hz'
  refine ⟨(mul_ne_zero_iff.mp hp).1, ?_⟩
  exact fun i => Finset.prod_ne_zero_iff.mp (mul_ne_zero_iff.mp hp).2 i (Finset.mem_univ i)

/-- The quantitative lower bound on the entire regular factor. -/
theorem normalized_product_ratio_bound
    (hZ : Tendsto (fun x => w x * Z x) l (𝓝 a))
    (hU : Tendsto U l (𝓝 b))
    (hR : Tendsto R l (𝓝 r))
    (hF : ∀ i, Tendsto (F i) l (𝓝 (v i)))
    (hfactor : ∀ᶠ x in l, Z x = T x * (R x * ∏ i, F i x))
    (hdom : ∀ᶠ x in l, ‖w x * T x‖ ≤ ‖U x‖)
    (hb : b ≠ 0) :
    ‖a‖ / ‖b‖ ≤ ‖r * ∏ i, v i‖ := by
  apply (div_le_iff₀ (norm_pos_iff.mpr hb)).mpr
  simpa only [mul_comm] using normalized_product_bound hZ hU hR hF hfactor hdom
end Abstract

section NumberField
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
variable {I : Type*} [Fintype I]
variable {T R : ℝ → ℂ} {F : I → ℝ → ℂ} {r : ℂ} {v : I → ℂ}

/-- Actual number-field residues replace both abstract residue premises.
This does not construct the supplied factors or prove their limits. -/
theorem dedekind_product_bound
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1,
      NumberField.dedekindZeta L (s : ℂ) = T s * (R s * ∏ i, F i s))
    (hdom : ∀ᶠ s : ℝ in 𝓝[>] 1, ‖T s‖ ≤ ‖NumberField.dedekindZeta K (s : ℂ)‖)
    (hR : Tendsto R (𝓝[>] (1 : ℝ)) (𝓝 r))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    NumberField.dedekindZeta_residue L ≤
      NumberField.dedekindZeta_residue K * ‖r * ∏ i, v i‖ := by
  have hz : Tendsto (fun s : ℝ => ((s : ℂ) - 1) * NumberField.dedekindZeta L (s : ℂ))
      (𝓝[>] (1 : ℝ)) (𝓝 (NumberField.dedekindZeta_residue L : ℂ)) := by
    simpa using NumberField.tendsto_sub_one_mul_dedekindZeta_nhdsGT L
  have hu : Tendsto (fun s : ℝ => ((s : ℂ) - 1) * NumberField.dedekindZeta K (s : ℂ))
      (𝓝[>] (1 : ℝ)) (𝓝 (NumberField.dedekindZeta_residue K : ℂ)) := by
    simpa using NumberField.tendsto_sub_one_mul_dedekindZeta_nhdsGT K
  have hd : ∀ᶠ s : ℝ in 𝓝[>] 1,
      ‖((s : ℂ) - 1) * T s‖ ≤ ‖((s : ℂ) - 1) * NumberField.dedekindZeta K (s : ℂ)‖ := by
    filter_upwards [hdom] with s hs
    simpa only [norm_mul] using mul_le_mul_of_nonneg_left hs (norm_nonneg ((s : ℂ) - 1))
  have h := normalized_product_bound hz hu hR hF hfactor hd
  simpa only [Complex.norm_real, Real.norm_eq_abs,
    abs_of_pos (NumberField.dedekindZeta_residue_pos L),
    abs_of_pos (NumberField.dedekindZeta_residue_pos K)] using h

/-- Nonvanishing for an actual Dedekind-zeta factorization under only domination
of the distinguished factor and convergence of the remaining finite factors. -/
theorem dedekind_factors_nonzero
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1,
      NumberField.dedekindZeta L (s : ℂ) = T s * (R s * ∏ i, F i s))
    (hdom : ∀ᶠ s : ℝ in 𝓝[>] 1, ‖T s‖ ≤ ‖NumberField.dedekindZeta K (s : ℂ)‖)
    (hR : Tendsto R (𝓝[>] (1 : ℝ)) (𝓝 r))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    r ≠ 0 ∧ ∀ i, v i ≠ 0 := by
  classical
  have hb := dedekind_product_bound K L hfactor hdom hR hF
  have hp : r * ∏ i, v i ≠ 0 := by
    intro hz
    have hz' : NumberField.dedekindZeta_residue L ≤ 0 := by
      simpa only [hz, norm_zero, mul_zero] using hb
    exact (not_le_of_gt (NumberField.dedekindZeta_residue_pos L)) hz'
  exact ⟨(mul_ne_zero_iff.mp hp).1,
    fun i => Finset.prod_ne_zero_iff.mp (mul_ne_zero_iff.mp hp).2 i (Finset.mem_univ i)⟩

/-- The explicit residue-ratio lower bound for the regular factor. -/
theorem dedekind_product_ratio_bound
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1,
      NumberField.dedekindZeta L (s : ℂ) = T s * (R s * ∏ i, F i s))
    (hdom : ∀ᶠ s : ℝ in 𝓝[>] 1, ‖T s‖ ≤ ‖NumberField.dedekindZeta K (s : ℂ)‖)
    (hR : Tendsto R (𝓝[>] (1 : ℝ)) (𝓝 r))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    NumberField.dedekindZeta_residue L / NumberField.dedekindZeta_residue K ≤
      ‖r * ∏ i, v i‖ := by
  apply (div_le_iff₀ (NumberField.dedekindZeta_residue_pos K)).mpr
  simpa only [mul_comm] using dedekind_product_bound K L hfactor hdom hR hF
end NumberField
end PaperX.ResidueDomination
