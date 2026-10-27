import PaperXI.DyadicCoordinates

/-! Transfer to arbitrary vector spaces with supplied symplectic coordinates.
The existence of those coordinates is explicitly separate. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicBasis
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates

variable {V ι : Type*} [AddCommGroup V] [Module F2 V] [Fintype ι]
variable {b : V →ₗ[F2] V →ₗ[F2] F2}

def toCoordinates (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement b) : Refinement (symplectic (ι := ι)) where
  value x := q.value (e.symm x)
  polar x y := by
    rw [map_add, q.polar, hb]
    simp

def fromCoordinates (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement (symplectic (ι := ι))) : Refinement b where
  value x := q.value (e x)
  polar x y := by rw [map_add, q.polar, hb]

/-- Every refinement transfers in both directions through supplied symplectic
coordinates. No formula for the refinement is assumed. -/
def refinementEquiv (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) :
    Refinement b ≃ Refinement (symplectic (ι := ι)) where
  toFun := toCoordinates e hb
  invFun := fromCoordinates e hb
  left_inv q := by
    ext x
    simp [toCoordinates, fromCoordinates]
  right_inv q := by
    ext x
    simp [toCoordinates, fromCoordinates]

@[simp] theorem toCoordinates_apply (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement b) (x : ι → F2 × F2) :
    (toCoordinates e hb q).value x = q.value (e.symm x) := rfl

@[simp] theorem fromCoordinates_apply (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y))
    (q : Refinement (symplectic (ι := ι))) (x : V) :
    (fromCoordinates e hb q).value x = q.value (e x) := rfl

/-- Arf's basis-value formula on the transported paired basis. -/
def basisArf (e : V ≃ₗ[F2] (ι → F2 × F2)) (q : Refinement b) : F2 :=
  ∑ i, q.value (e.symm (firstAxis i)) * q.value (e.symm (secondAxis i))

theorem basisArf_eq_coordinate_arf (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) (q : Refinement b) :
    basisArf e q = arf (refinementCoefficients (toCoordinates e hb q)) := by
  rw [refinement_arf_basis_formula]
  rfl

theorem gauss_sum [Fintype V] (e : V ≃ₗ[F2] (ι → F2 × F2))
    (hb : ∀ x y, b x y = symplectic (e x) (e y)) (q : Refinement b) :
    (∑ x : V, sign (q.value x)) = sign (basisArf e q) * 2 ^ Fintype.card ι := by
  calc
    (∑ x : V, sign (q.value x)) =
        ∑ x : ι → F2 × F2, sign (q.value (e.symm x)) :=
      (e.symm.toEquiv.sum_comp (fun x => sign (q.value x))).symm
    _ = sign (basisArf e q) * 2 ^ Fintype.card ι :=
      refinement_gauss_sum (toCoordinates e hb q)

/-- Changing a supplied symplectic coordinate map leaves the Arf value
unchanged, because both maps evaluate the same intrinsic Gauss sum. -/
theorem basisArf_independent [Fintype V]
    (e f : V ≃ₗ[F2] (ι → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y))
    (hf : ∀ x y, b x y = symplectic (f x) (f y)) (q : Refinement b) :
    basisArf e q = basisArf f q := by
  apply sign_injective
  have h := (gauss_sum e he q).symm.trans (gauss_sum f hf q)
  exact mul_right_cancel₀ (pow_ne_zero _ (by norm_num : (2 : ℤ) ≠ 0)) h

end PaperXI.DyadicBasis
