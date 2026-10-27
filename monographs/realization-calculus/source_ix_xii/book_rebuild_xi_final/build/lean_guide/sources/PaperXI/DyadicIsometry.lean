import PaperXI.DyadicDimension

/-! Quadratic refinements and their Arf values transport along actual isometries. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicIsometry
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates PaperXI.DyadicBasis

variable {V W ι κ : Type*} [AddCommGroup V] [Module F2 V]
  [AddCommGroup W] [Module F2 W] [Fintype ι] [Fintype κ]
variable {b : V →ₗ[F2] V →ₗ[F2] F2} {c : W →ₗ[F2] W →ₗ[F2] F2}

def transportRefinement (f : V ≃ₗ[F2] W)
    (hf : ∀ x y, b x y = c (f x) (f y)) (q : Refinement b) : Refinement c where
  value x := q.value (f.symm x)
  polar x y := by
    rw [map_add, q.polar, hf]
    simp

@[simp] theorem transportRefinement_apply (f : V ≃ₗ[F2] W)
    (hf : ∀ x y, b x y = c (f x) (f y)) (q : Refinement b) (x : W) :
    (transportRefinement f hf q).value x = q.value (f.symm x) := rfl

def transportRefinementEquiv (f : V ≃ₗ[F2] W)
    (hf : ∀ x y, b x y = c (f x) (f y)) : Refinement b ≃ Refinement c where
  toFun := transportRefinement f hf
  invFun := transportRefinement f.symm (fun x y => by simpa using (hf (f.symm x) (f.symm y)).symm)
  left_inv q := by ext x; simp [transportRefinement]
  right_inv q := by ext x; simp [transportRefinement]

/-- Transport preserves the intrinsic Gauss sum by bijectivity. -/
theorem gauss_sum_transport [Fintype V] [Fintype W] (f : V ≃ₗ[F2] W)
    (hf : ∀ x y, b x y = c (f x) (f y)) (q : Refinement b) :
    (∑ x : W, sign ((transportRefinement f hf q).value x)) =
      ∑ x : V, sign (q.value x) := by
  exact f.symm.toEquiv.sum_comp (fun x => sign (q.value x))

/-- An actual form-preserving linear equivalence preserves Arf, even when the
two supplied symplectic coordinate systems use different finite index types. -/
theorem basisArf_transport (f : V ≃ₗ[F2] W)
    (hf : ∀ x y, b x y = c (f x) (f y))
    (eV : V ≃ₗ[F2] (ι → F2 × F2)) (eW : W ≃ₗ[F2] (κ → F2 × F2))
    (heV : ∀ x y, b x y = symplectic (eV x) (eV y))
    (heW : ∀ x y, c x y = symplectic (eW x) (eW y)) (q : Refinement b) :
    basisArf eW (transportRefinement f hf q) = basisArf eV q := by
  change basisArf (f.trans eW) q = basisArf eV q
  apply DyadicDimension.basisArf_independent (f.trans eW) eV _ heV q
  intro x y
  exact (hf x y).trans (heW (f x) (f y))

end PaperXI.DyadicIsometry
