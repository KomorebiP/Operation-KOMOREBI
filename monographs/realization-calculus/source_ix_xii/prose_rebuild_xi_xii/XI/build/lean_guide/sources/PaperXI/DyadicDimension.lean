import PaperXI.DyadicBasis
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Defs

/-! Dimensions and Arf comparison for arbitrary finite symplectic index types.
All coordinate maps in this module are explicit inputs. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicDimension
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates PaperXI.DyadicBasis

variable {V ι κ : Type*} [AddCommGroup V] [Module F2 V] [Fintype ι] [Fintype κ]

theorem finrank_eq_twice_card (e : V ≃ₗ[F2] (ι → F2 × F2)) :
    Module.finrank F2 V = 2 * Fintype.card ι := by
  rw [e.finrank_eq, Module.finrank_pi_fintype]
  simp [Module.finrank_prod, Nat.mul_comm]

theorem card_eq_finrank_div_two (e : V ≃ₗ[F2] (ι → F2 × F2)) :
    Fintype.card ι = Module.finrank F2 V / 2 := by
  rw [finrank_eq_twice_card e]
  omega

theorem card_pos [Nontrivial V] (e : V ≃ₗ[F2] (ι → F2 × F2)) :
    0 < Fintype.card ι := by
  let : FiniteDimensional F2 V := e.symm.finiteDimensional
  have h := Module.finrank_pos (R := F2) (M := V)
  rw [finrank_eq_twice_card e] at h
  omega

theorem coordinate_card_eq (e : V ≃ₗ[F2] (ι → F2 × F2))
    (f : V ≃ₗ[F2] (κ → F2 × F2)) : Fintype.card ι = Fintype.card κ := by
  rw [card_eq_finrank_div_two e, card_eq_finrank_div_two f]

/-- Arf is independent of both the coordinate map and its finite index type.
The finite enumeration of the underlying space is derived from the map. -/
theorem basisArf_independent {b : V →ₗ[F2] V →ₗ[F2] F2}
    (e : V ≃ₗ[F2] (ι → F2 × F2)) (f : V ≃ₗ[F2] (κ → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y))
    (hf : ∀ x y, b x y = symplectic (f x) (f y)) (q : Refinement b) :
    basisArf e q = basisArf f q := by
  let : Fintype V := Fintype.ofEquiv (ι → F2 × F2) e.symm.toEquiv
  apply sign_injective
  have h := (gauss_sum e he q).symm.trans (gauss_sum f hf q)
  rw [coordinate_card_eq e f] at h
  exact mul_right_cancel₀ (pow_ne_zero _ (by norm_num : (2 : ℤ) ≠ 0)) h

end PaperXI.DyadicDimension
