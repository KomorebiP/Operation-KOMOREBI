import PaperXI.DyadicAbstract
import PaperXI.DyadicIsometry
import PaperXI.DyadicOrthogonal

/-! Intrinsic Arf and Gauss-sign laws for actual orthogonal sums.
Symplectic coordinates are constructed from alternation and nondegeneracy. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicAbstractOrthogonal
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates

variable {V W X : Type*} [AddCommGroup V] [Module F2 V]
  [AddCommGroup W] [Module F2 W] [AddCommGroup X] [Module F2 X]
variable (b : V →ₗ[F2] V →ₗ[F2] F2) (c : W →ₗ[F2] W →ₗ[F2] F2)

theorem form_alternating (ha : ∀ x, b x x = 0) (hc : ∀ x, c x x = 0)
    (x : V × W) : DyadicOrthogonal.form b c x x = 0 := by
  simp [DyadicOrthogonal.form_apply, ha, hc]

theorem form_nondegenerate
    (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
    (hm : ∀ x, (∀ y, c x y = 0) → x = 0)
    (x : V × W) (hx : ∀ y, DyadicOrthogonal.form b c x y = 0) : x = 0 := by
  apply Prod.ext
  · apply hn x.1
    intro y
    simpa using hx (y, 0)
  · apply hm x.2
    intro y
    simpa using hx (0, y)

variable [FiniteDimensional F2 V] [FiniteDimensional F2 W]
variable (ha : ∀ x, b x x = 0) (hn : ∀ x, (∀ y, b x y = 0) → x = 0)
  (hc : ∀ x, c x x = 0) (hm : ∀ x, (∀ y, c x y = 0) → x = 0)

/-- Intrinsic Arf is preserved by an actual form-preserving linear equivalence. -/
theorem arf_transport (f : V ≃ₗ[F2] W)
    (hf : ∀ x y, b x y = c (f x) (f y)) (q : Refinement b) :
    DyadicAbstract.arf c hc hm (DyadicIsometry.transportRefinement f hf q) =
      DyadicAbstract.arf b ha hn q := by
  rw [DyadicAbstract.arf_eq_basis c hc hm (DyadicAbstract.coordinates c hc hm)
    (DyadicAbstract.coordinates_form c hc hm),
    DyadicAbstract.arf_eq_basis b ha hn (DyadicAbstract.coordinates b ha hn)
    (DyadicAbstract.coordinates_form b ha hn)]
  exact DyadicIsometry.basisArf_transport f hf
    (DyadicAbstract.coordinates b ha hn) (DyadicAbstract.coordinates c hc hm)
    (DyadicAbstract.coordinates_form b ha hn) (DyadicAbstract.coordinates_form c hc hm) q

/-- Manuscript 13.6: Arf is additive on the actual product quadratic refinement,
without assuming any symplectic coordinate maps. -/
theorem arf_add (q : Refinement b) (r : Refinement c) :
    DyadicAbstract.arf (DyadicOrthogonal.form b c)
      (form_alternating b c ha hc) (form_nondegenerate b c hn hm)
      (DyadicOrthogonal.refinement b c q r) =
      DyadicAbstract.arf b ha hn q + DyadicAbstract.arf c hc hm r := by
  let e := DyadicAbstract.coordinates b ha hn
  let f := DyadicAbstract.coordinates c hc hm
  let : Fintype V := Fintype.ofEquiv _ e.symm.toEquiv
  let : Fintype W := Fintype.ofEquiv _ f.symm.toEquiv
  have he := DyadicAbstract.coordinates_form b ha hn
  have hf := DyadicAbstract.coordinates_form c hc hm
  rw [DyadicAbstract.arf_eq_basis (DyadicOrthogonal.form b c)
    (form_alternating b c ha hc) (form_nondegenerate b c hn hm)
    (DyadicOrthogonal.coordinates e f) (DyadicOrthogonal.coordinates_form e f he hf),
    DyadicAbstract.arf_eq_basis b ha hn e he,
    DyadicAbstract.arf_eq_basis c hc hm f hf]
  exact DyadicOrthogonal.arf_add e f he hf q r

/-- The normalized Gauss signs multiply on an orthogonal sum. -/
theorem arf_sign_product (q : Refinement b) (r : Refinement c) :
    sign (DyadicAbstract.arf (DyadicOrthogonal.form b c)
      (form_alternating b c ha hc) (form_nondegenerate b c hn hm)
      (DyadicOrthogonal.refinement b c q r)) =
      sign (DyadicAbstract.arf b ha hn q) * sign (DyadicAbstract.arf c hc hm r) := by
  rw [arf_add b c ha hn hc hm, sign_add]

variable [FiniteDimensional F2 X]
variable (d : X →ₗ[F2] X →ₗ[F2] F2)
  (hd : ∀ x, d x x = 0) (hk : ∀ x, (∀ y, d x y = 0) → x = 0)

/-- An arbitrary orthogonal decomposition is represented by its actual linear
equivalence, the form identity, and the equality of quadratic-refinement values. -/
theorem arf_of_decomposition (f : X ≃ₗ[F2] V × W)
    (hf : ∀ x y, d x y = DyadicOrthogonal.form b c (f x) (f y))
    (q : Refinement d) (qV : Refinement b) (qW : Refinement c)
    (hq : ∀ x, q.value x = qV.value (f x).1 + qW.value (f x).2) :
    DyadicAbstract.arf d hd hk q =
      DyadicAbstract.arf b ha hn qV + DyadicAbstract.arf c hc hm qW := by
  have hq' : DyadicIsometry.transportRefinement f hf q =
      DyadicOrthogonal.refinement b c qV qW := by
    ext x
    simp only [DyadicIsometry.transportRefinement_apply,
      DyadicOrthogonal.refinement]
    rw [hq]
    simp
  calc
    DyadicAbstract.arf d hd hk q = DyadicAbstract.arf (DyadicOrthogonal.form b c)
        (form_alternating b c ha hc) (form_nondegenerate b c hn hm)
        (DyadicIsometry.transportRefinement f hf q) :=
      (arf_transport d (DyadicOrthogonal.form b c) hd hk
        (form_alternating b c ha hc) (form_nondegenerate b c hn hm) f hf q).symm
    _ = DyadicAbstract.arf b ha hn qV + DyadicAbstract.arf c hc hm qW := by
      rw [hq']
      exact arf_add b c ha hn hc hm qV qW

theorem arf_sign_of_decomposition (f : X ≃ₗ[F2] V × W)
    (hf : ∀ x y, d x y = DyadicOrthogonal.form b c (f x) (f y))
    (q : Refinement d) (qV : Refinement b) (qW : Refinement c)
    (hq : ∀ x, q.value x = qV.value (f x).1 + qW.value (f x).2) :
    sign (DyadicAbstract.arf d hd hk q) =
      sign (DyadicAbstract.arf b ha hn qV) * sign (DyadicAbstract.arf c hc hm qW) := by
  rw [arf_of_decomposition b c ha hn hc hm d hd hk f hf q qV qW hq, sign_add]

/-- Multiplicativity of the actual Gauss sum divided by its positive power of two. -/
theorem normalized_sign_product (q : Refinement b) (r : Refinement c) :
    DyadicAbstract.normalizedGaussSign (DyadicOrthogonal.form b c)
      (form_alternating b c ha hc) (form_nondegenerate b c hn hm)
      (DyadicOrthogonal.refinement b c q r) =
      DyadicAbstract.normalizedGaussSign b ha hn q *
        DyadicAbstract.normalizedGaussSign c hc hm r := by
  rw [DyadicAbstract.normalizedGaussSign_eq_sign,
    DyadicAbstract.normalizedGaussSign_eq_sign,
    DyadicAbstract.normalizedGaussSign_eq_sign]
  exact_mod_cast arf_sign_product b c ha hn hc hm q r

/-- The actual normalized Gauss sum is multiplicative after any supplied
orthogonal decomposition of the quadratic space. -/
theorem normalized_sign_of_decomposition (f : X ≃ₗ[F2] V × W)
    (hf : ∀ x y, d x y = DyadicOrthogonal.form b c (f x) (f y))
    (q : Refinement d) (qV : Refinement b) (qW : Refinement c)
    (hq : ∀ x, q.value x = qV.value (f x).1 + qW.value (f x).2) :
    DyadicAbstract.normalizedGaussSign d hd hk q =
      DyadicAbstract.normalizedGaussSign b ha hn qV *
        DyadicAbstract.normalizedGaussSign c hc hm qW := by
  rw [DyadicAbstract.normalizedGaussSign_eq_sign,
    DyadicAbstract.normalizedGaussSign_eq_sign,
    DyadicAbstract.normalizedGaussSign_eq_sign]
  exact_mod_cast arf_sign_of_decomposition b c ha hn hc hm d hd hk f hf q qV qW hq

end PaperXI.DyadicAbstractOrthogonal
