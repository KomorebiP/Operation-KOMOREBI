import PaperXI.BreakQuadratic

/-! Paper XI 15.3, characteristic two: finite-family products of actual
normalized Gauss sums, and transfer through the supplied quadratic decomposition. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakDyadicPhase
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.BreakQuadratic

variable {ι : Type*} [Fintype ι] {V : ι → Type*}
  [∀ i, AddCommGroup (V i)] [∀ i, Module F2 (V i)]
  [∀ i, FiniteDimensional F2 (V i)]
variable (b : ∀ i, V i →ₗ[F2] V i →ₗ[F2] F2)
  (ha : ∀ i x, b i x x = 0)
  (hn : ∀ i x, (∀ y, b i x y = 0) → x = 0)

/-- The intrinsic Gauss sums use the same literal finite product sum,
independently of the internally chosen finite enumerations. -/
theorem gaussSum_product (q : ∀ i, Refinement (b i)) :
    DyadicAbstract.gaussSum (form b) (form_alternating b ha)
      (form_nondegenerate b hn) (refinement b q) =
      ∏ i, DyadicAbstract.gaussSum (b i) (ha i) (hn i) (q i) := by
  let (i : ι) : Fintype (V i) := Fintype.ofEquiv _
    (DyadicAbstract.coordinates (b i) (ha i) (hn i)).symm.toEquiv
  simp_rw [DyadicAbstract.gaussSum_eq_sum]
  exact gauss_sum_product b q

/-- Source 15.3: the normalized Gauss sign of the actual finite orthogonal
refinement is the product of the component normalized Gauss signs. -/
theorem normalizedGaussSign_product (q : ∀ i, Refinement (b i)) :
    DyadicAbstract.normalizedGaussSign (form b) (form_alternating b ha)
      (form_nondegenerate b hn) (refinement b q) =
      ∏ i, DyadicAbstract.normalizedGaussSign (b i) (ha i) (hn i) (q i) := by
  simp only [DyadicAbstract.normalizedGaussSign]
  rw [half_finrank_product b ha hn, gaussSum_product b ha hn]
  push_cast
  rw [Finset.prod_div_distrib, Finset.prod_pow_eq_pow_sum]

/-- The corresponding intrinsic Arf invariant is additive over the actual
finite orthogonal family. -/
theorem arf_sum (q : ∀ i, Refinement (b i)) :
    DyadicAbstract.arf (form b) (form_alternating b ha)
      (form_nondegenerate b hn) (refinement b q) =
      ∑ i, DyadicAbstract.arf (b i) (ha i) (hn i) (q i) := by
  apply sign_injective
  have h := normalizedGaussSign_product b ha hn q
  simp_rw [DyadicAbstract.normalizedGaussSign_eq_sign] at h
  rw [sign_sum]
  exact_mod_cast h

/-- The empty family contributes the multiplicative unit. -/
theorem normalizedGaussSign_empty [IsEmpty ι] (q : ∀ i, Refinement (b i)) :
    DyadicAbstract.normalizedGaussSign (form b) (form_alternating b ha)
      (form_nondegenerate b hn) (refinement b q) = 1 := by
  rw [normalizedGaussSign_product b ha hn]
  simp

variable {X : Type*} [AddCommGroup X] [Module F2 X] [FiniteDimensional F2 X]
variable (d : X →ₗ[F2] X →ₗ[F2] F2)
  (hd : ∀ x, d x x = 0) (hk : ∀ x, (∀ y, d x y = 0) → x = 0)

omit [∀ i, FiniteDimensional F2 (V i)] [FiniteDimensional F2 X] in
/-- Exact refinement compatibility is the value equation on the supplied
decomposition; preserving only the polar form is insufficient. -/
theorem transport_refinement (f : X ≃ₗ[F2] (∀ i, V i))
    (hf : ∀ x y, d x y = form b (f x) (f y))
    (q : Refinement d) (qs : ∀ i, Refinement (b i))
    (hq : ∀ x, q.value x = ∑ i, (qs i).value (f x i)) :
    DyadicIsometry.transportRefinement f hf q = refinement b qs := by
  ext x
  rw [DyadicIsometry.transportRefinement_apply, hq]
  simp only [LinearEquiv.apply_symm_apply, refinement_apply]

/-- Finite-family Arf additivity after an actual form- and refinement-preserving
break decomposition. -/
theorem arf_of_decomposition (f : X ≃ₗ[F2] (∀ i, V i))
    (hf : ∀ x y, d x y = form b (f x) (f y))
    (q : Refinement d) (qs : ∀ i, Refinement (b i))
    (hq : ∀ x, q.value x = ∑ i, (qs i).value (f x i)) :
    DyadicAbstract.arf d hd hk q =
      ∑ i, DyadicAbstract.arf (b i) (ha i) (hn i) (qs i) := by
  calc
    DyadicAbstract.arf d hd hk q =
        DyadicAbstract.arf (form b) (form_alternating b ha) (form_nondegenerate b hn)
          (DyadicIsometry.transportRefinement f hf q) :=
      (DyadicAbstractOrthogonal.arf_transport d (form b) hd hk
        (form_alternating b ha) (form_nondegenerate b hn) f hf q).symm
    _ = _ := by
      rw [transport_refinement b d f hf q qs hq]
      exact arf_sum b ha hn qs

/-- Source 15.3 for supplied finite break data: the actual normalized total
Gauss sum factors into the actual normalized summand Gauss sums. -/
theorem normalizedGaussSign_of_decomposition (f : X ≃ₗ[F2] (∀ i, V i))
    (hf : ∀ x y, d x y = form b (f x) (f y))
    (q : Refinement d) (qs : ∀ i, Refinement (b i))
    (hq : ∀ x, q.value x = ∑ i, (qs i).value (f x i)) :
    DyadicAbstract.normalizedGaussSign d hd hk q =
      ∏ i, DyadicAbstract.normalizedGaussSign (b i) (ha i) (hn i) (qs i) := by
  simp_rw [DyadicAbstract.normalizedGaussSign_eq_sign]
  rw [arf_of_decomposition b ha hn d hd hk f hf q qs hq, sign_sum]
  push_cast
  rfl

include b ha hn in
omit [FiniteDimensional F2 X] in
/-- The displayed normalization exponent transports through the actual
decomposition, rather than being supplied as a numerical assumption. -/
theorem half_finrank_of_decomposition (f : X ≃ₗ[F2] (∀ i, V i)) :
    Module.finrank F2 X / 2 = ∑ i, Module.finrank F2 (V i) / 2 := by
  rw [f.finrank_eq]
  exact half_finrank_product b ha hn

end PaperXI.BreakDyadicPhase
