import PaperXI.MonomialAction
import Mathlib.LinearAlgebra.Dual.Basis

/-! The contragredient of a genuine monomial representation on the dual basis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonomialDual
open scoped Classical
variable {G X V : Type*} [Group G] [Fintype X]
variable [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ G V) (b : Module.Basis X ℂ V)
variable (p : G →* Equiv.Perm X) (c : G → X → ℂˣ)
variable (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x))

include hρ in
omit [Fintype X] in
/-- Inverse-step coefficients are consequences of the original representation law. -/
theorem inverse_weight (g : G) (j : X) :
    c g⁻¹ (p g j) = (c g j)⁻¹ := by
  apply eq_inv_iff_mul_eq_one.mpr
  rw [← MonomialAction.weight_mul b p c ρ hρ, inv_mul_cancel,
    MonomialAction.weight_one b p c ρ hρ]

include hρ in
/-- This identity uses the actual contragredient action, not merely inverse labels. -/
theorem dual_basis_action (g : G) (j : X) :
    ρ.dual g (b.dualBasis j) = ((c g j)⁻¹ : ℂˣ) • b.dualBasis (p g j) := by
  apply b.ext
  intro k
  change b.dualBasis j (ρ g⁻¹ (b k)) =
    (((c g j)⁻¹ : ℂˣ) : ℂ) * b.dualBasis (p g j) (b k)
  rw [hρ, map_smul, b.dualBasis_apply_self, b.dualBasis_apply_self]
  by_cases hk : k = p g j
  · subst k
    have hp : p g⁻¹ (p g j) = j := by simp
    rw [hp, inverse_weight ρ b p c hρ]
    simp
  · have hn : p g⁻¹ k ≠ j := by
      intro h
      apply hk
      have hh := congrArg (p g) h
      simpa using hh
    rw [ite_eq_right hn, ite_eq_right hk]
    simp

end PaperXI.MonomialDual
