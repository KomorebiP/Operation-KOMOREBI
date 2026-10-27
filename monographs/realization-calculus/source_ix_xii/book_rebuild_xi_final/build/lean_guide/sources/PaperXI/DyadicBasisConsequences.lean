import PaperXI.DyadicBasis
import PaperXI.DyadicRefinement

/-! Translation and opposite Arf phases on arbitrary spaces with supplied
symplectic coordinates. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicBasisConsequences
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates
open PaperXI.DyadicBasis

variable {V ι : Type*} [AddCommGroup V] [Module F2 V] [Fintype ι]
variable {b : V →ₗ[F2] V →ₗ[F2] F2}

theorem toCoordinates_addLinear (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement b) (v : V) :
    toCoordinates e hb (addLinear q (b v)) =
      addLinear (toCoordinates e hb q) (symplectic (e v)) := by
  ext x
  simp [toCoordinates, addLinear, hb]

/-- Translation by the actual bilinear functional b(v,-) changes Arf by q(v). -/
theorem arf_translation (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement b) (v : V) :
    basisArf e (addLinear q (b v)) = basisArf e q + q.value v := by
  calc
    basisArf e (addLinear q (b v)) =
        PaperXI.DyadicRefinement.basisArf
          (toCoordinates e hb (addLinear q (b v))) := rfl
    _ = PaperXI.DyadicRefinement.basisArf
        (addLinear (toCoordinates e hb q) (symplectic (e v))) := by
      rw [toCoordinates_addLinear]
    _ = PaperXI.DyadicRefinement.basisArf (toCoordinates e hb q) +
        (toCoordinates e hb q).value (e v) :=
      PaperXI.DyadicRefinement.arf_translation _ _
    _ = basisArf e q + q.value v := by
      simp [PaperXI.DyadicRefinement.basisArf, basisArf, toCoordinates]

theorem basisArf_fromCoordinates (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement (symplectic (ι := ι))) :
    basisArf e (fromCoordinates e hb q) = PaperXI.DyadicRefinement.basisArf q := by
  simp [basisArf, fromCoordinates, PaperXI.DyadicRefinement.basisArf]

theorem gauss_fromCoordinates [Fintype V] (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement (symplectic (ι := ι))) :
    (∑ v : V, sign ((fromCoordinates e hb q).value v)) =
      ∑ x : ι → F2 × F2, sign (q.value x) :=
  e.toEquiv.sum_comp (fun x => sign (q.value x))

/-- A nonzero number of symplectic pairs gives actual refinements with
opposite Arf values and opposite nonzero Gauss phases. -/
theorem opposite_refinements [Fintype V] (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) (i : ι) :
    ∃ q r : Refinement b,
      basisArf e q = 0 ∧ basisArf e r = 1 ∧
      (∑ x : V, sign (r.value x)) = -(∑ x : V, sign (q.value x)) := by
  obtain ⟨q, r, hq, hr, hs⟩ := PaperXI.DyadicRefinement.opposite_refinements i
  refine ⟨fromCoordinates e hb q, fromCoordinates e hb r, ?_, ?_, ?_⟩
  · simpa only [basisArf_fromCoordinates] using hq
  · simpa only [basisArf_fromCoordinates] using hr
  · simpa only [gauss_fromCoordinates] using hs

end PaperXI.DyadicBasisConsequences
