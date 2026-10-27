import Mathlib.NumberTheory.NumberField.CanonicalEmbedding.Basic

/-!
The signed field norm in mixed embedding coordinates.

The embedding-fiber argument follows the proof of
`NumberField.InfinitePlace.prod_eq_abs_norm` in Mathlib, with the factors retained
before taking absolute values. That source carries the following notice:
Copyright (c) 2022 Xavier Roblot. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Xavier Roblot
-/
set_option autoImplicit false
noncomputable section

namespace PaperX.NormSignArithmetic
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open scoped Classical
variable (K : Type*) [Field K] [NumberField K]

theorem embedding_fiber_eq_pair (w : InfinitePlace K) :
    ({φ : K →+* ℂ | mk φ = w} : Finset _) =
      {embedding w, ComplexEmbedding.conjugate (embedding w)} := by
  ext φ
  simp only [Finset.mem_filter, Finset.mem_univ, true_and,
    Finset.mem_insert, Finset.mem_singleton]
  conv_lhs => rw [← mk_embedding w, mk_eq_iff]
  exact or_congr Iff.rfl ⟨fun h => by
    simpa only [ComplexEmbedding.conjugate, star_star] using congrArg star h,
    fun h => by
      simpa only [ComplexEmbedding.conjugate, star_star] using congrArg star h⟩

theorem embedding_fiber_product_real (x : K) (w : InfinitePlace K) (hw : IsReal w) :
    (∏ φ ∈ ({φ : K →+* ℂ | mk φ = w} : Finset _), φ x) =
      (embedding_of_isReal hw x : ℂ) := by
  rw [embedding_fiber_eq_pair, conjugate_embedding_eq_of_isReal hw]
  simp

theorem embedding_fiber_product_complex (x : K) (w : InfinitePlace K)
    (hw : IsComplex w) :
    (∏ φ ∈ ({φ : K →+* ℂ | mk φ = w} : Finset _), φ x) =
      ((‖embedding w x‖ ^ 2 : ℝ) : ℂ) := by
  rw [embedding_fiber_eq_pair]
  have hne : embedding w ≠ ComplexEmbedding.conjugate (embedding w) := by
    intro h
    exact (isComplex_iff.mp hw) (ComplexEmbedding.isReal_iff.mpr h.symm)
  rw [Finset.prod_pair hne]
  simp only [ComplexEmbedding.conjugate_coe_eq]
  rw [Complex.mul_conj, Complex.normSq_eq_norm_sq]

/-- The signed rational field norm, before taking absolute values. -/
theorem field_norm_eq_real_mul_complex (x : K) :
    (Algebra.norm ℚ x : ℝ) =
      (∏ w : {w : InfinitePlace K // IsReal w}, (mixedEmbedding K x).1 w) *
        ∏ w : {w : InfinitePlace K // IsComplex w}, ‖(mixedEmbedding K x).2 w‖ ^ 2 := by
  apply Complex.ofReal_injective
  rw [Complex.ofReal_ratCast, Complex.ofReal_mul, Complex.ofReal_prod, Complex.ofReal_prod]
  calc
    (Algebra.norm ℚ x : ℂ) = ∏ φ : K →+* ℂ, φ x := by
      simpa only [eq_ratCast] using (Algebra.norm_eq_prod_embeddings ℚ ℂ x).trans
        (Fintype.prod_equiv (RingHom.equivRatAlgHom K ℂ).symm _ _ (fun _ => rfl))
    _ = (∏ w : {w : InfinitePlace K // IsReal w}, ((mixedEmbedding K x).1 w : ℂ)) *
        ∏ w : {w : InfinitePlace K // IsComplex w}, ((‖(mixedEmbedding K x).2 w‖ ^ 2 : ℝ) : ℂ) := by
      rw [← Finset.prod_fiberwise Finset.univ mk (fun φ => φ x), prod_eq_prod_mul_prod]
      congr 1
      · apply Finset.prod_congr rfl
        intro w _
        exact embedding_fiber_product_real K x w.1 w.2
      · apply Finset.prod_congr rfl
        intro w _
        exact embedding_fiber_product_complex K x w.1 w.2

theorem complex_factor_pos {x : K} (hx : x ≠ 0) :
    0 < ∏ w : {w : InfinitePlace K // IsComplex w}, ‖(mixedEmbedding K x).2 w‖ ^ 2 := by
  apply Finset.prod_pos
  intro w _
  apply pow_pos
  rw [norm_pos_iff, mixedEmbedding_apply_isComplex]
  exact fun h => hx ((embedding w.1).injective (by simpa using h))

end PaperX.NormSignArithmetic
