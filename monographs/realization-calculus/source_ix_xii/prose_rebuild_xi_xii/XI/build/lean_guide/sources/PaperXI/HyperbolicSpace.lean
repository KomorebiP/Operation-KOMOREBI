import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.BilinearForm.Properties
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic

/-! The actual hyperbolic space U × U*, its evaluation form, and its
contragredient action. No bilinear form or action identities are assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HyperbolicSpace

variable (k U : Type*) [Field k] [AddCommGroup U] [Module k U]

/-- The actual hyperbolic carrier. -/
abbrev Space := U × Module.Dual k U

/-- The evaluation form with the convention k(u) - l(v). -/
def form : LinearMap.BilinForm k (Space k U) where
  toFun x :=
    { toFun := fun y => y.2 x.1 - x.2 y.1
      map_add' := by intro y z; simp; ring
      map_smul' := by intro r y; simp; ring }
  map_add' := by
    intro x y
    apply LinearMap.ext
    intro z
    change z.2 (x.1 + y.1) - (x.2 + y.2) z.1 =
      (z.2 x.1 - x.2 z.1) + (z.2 y.1 - y.2 z.1)
    simp only [map_add, LinearMap.add_apply]
    ring
  map_smul' := by
    intro r x
    apply LinearMap.ext
    intro y
    change y.2 (r • x.1) - (r • x.2) y.1 = r • (y.2 x.1 - x.2 y.1)
    simp only [map_smul, LinearMap.smul_apply, smul_sub]

@[simp] theorem form_apply (x y : Space k U) :
    form k U x y = y.2 x.1 - x.2 y.1 := rfl

/-- Alternation holds in every characteristic. -/
theorem form_isAlt : (form k U).IsAlt := by
  intro x
  simp

/-- Evaluation separates vectors and functionals, giving actual nondegeneracy. -/
theorem form_nondegenerate : (form k U).Nondegenerate := by
  constructor
  · intro x hx
    apply Prod.ext
    · apply (Module.forall_dual_apply_eq_zero_iff k x.1).1
      intro l
      simpa using hx (0, l)
    · apply LinearMap.ext
      intro u
      have h := hx (u, 0)
      simpa using h
  · intro x hx
    apply Prod.ext
    · apply (Module.forall_dual_apply_eq_zero_iff k x.1).1
      intro l
      have h := hx (0, l)
      simpa using h
    · apply LinearMap.ext
      intro u
      simpa using hx (u, 0)

variable {k U}

/-- The original action on U paired with its inverse dual action on U*. -/
def action (a : U ≃ₗ[k] U) : Space k U ≃ₗ[k] Space k U :=
  a.prodCongr a.symm.dualMap

@[simp] theorem action_apply (a : U ≃ₗ[k] U) (x : Space k U) :
    action a x = (a x.1, a.symm.dualMap x.2) := rfl

/-- The inverse dual is forced by preservation of the evaluation pairing. -/
theorem action_form (a : U ≃ₗ[k] U) (x y : Space k U) :
    form k U (action a x) (action a y) = form k U x y := by
  simp [form_apply, LinearEquiv.dualMap_apply]

/-- No nonzero fixed vector on U implies no nonzero fixed functional for
its inverse dual action. -/
theorem dual_fixedPointFree [FiniteDimensional k U] (a : U ≃ₗ[k] U)
    (ha : ∀ u, a u = u → u = 0) (l : Module.Dual k U)
    (hl : a.symm.dualMap l = l) : l = 0 := by
  have hsurj : Function.Surjective (a.toLinearMap - 1 : Module.End k U) := by
    apply LinearMap.surjective_of_injective
    apply LinearMap.ker_eq_bot.mp
    apply le_antisymm _ bot_le
    intro u hu
    change u = 0
    change a u - u = 0 at hu
    exact ha u (sub_eq_zero.mp hu)
  apply LinearMap.ext
  intro v
  obtain ⟨u, hu⟩ := hsurj v
  have hi := congrArg (fun f : Module.Dual k U => f (a u)) hl
  change l (a.symm (a u)) = l (a u) at hi
  rw [a.symm_apply_apply] at hi
  rw [← hu]
  change l (a u - u) = 0
  rw [map_sub, ← hi, sub_self]

/-- The actual hyperbolic action has no nonzero fixed vectors. -/
theorem action_fixedPointFree [FiniteDimensional k U] (a : U ≃ₗ[k] U)
    (ha : ∀ u, a u = u → u = 0) (x : Space k U)
    (hx : action a x = x) : x = 0 := by
  apply Prod.ext
  · exact ha x.1 (congrArg Prod.fst hx)
  · exact dual_fixedPointFree a ha x.2 (congrArg Prod.snd hx)

/-- The hyperbolic dimension is twice the original dimension, including U=0. -/
theorem finrank [FiniteDimensional k U] :
    Module.finrank k (Space k U) = 2 * Module.finrank k U := by
  rw [Module.finrank_prod, Subspace.dual_finrank_eq]
  omega

end PaperXI.HyperbolicSpace
