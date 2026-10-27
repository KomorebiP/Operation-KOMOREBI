import PaperXI.DyadicAffine
import Mathlib.Algebra.Torsor.Defs

/-! The canonical affine-space structure on a nonempty family of refinements.
The action and subtraction are the actual addition and difference of functions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicTorsor
open PaperXI.DyadicAffine

variable {V : Type*} [AddCommGroup V] [Module (ZMod 2) V]
variable {b : V →ₗ[ZMod 2] V →ₗ[ZMod 2] ZMod 2}

@[simp] theorem addLinear_zero (q : Refinement b) : addLinear q 0 = q := by
  ext x
  simp

theorem addLinear_add (q : Refinement b) (l m : V →ₗ[ZMod 2] ZMod 2) :
    addLinear q (l + m) = addLinear (addLinear q m) l := by
  ext x
  simp only [addLinear_apply, LinearMap.add_apply]
  abel

theorem addLinear_injective (q : Refinement b) :
    Function.Injective (addLinear q) := by
  intro l m h
  have h' := congrArg (fun r => linearDifference r q) h
  simpa only [linearDifference_addLinear] using h'

theorem addLinear_free (q : Refinement b) (l : V →ₗ[ZMod 2] ZMod 2) :
    addLinear q l = q ↔ l = 0 := by
  constructor
  · intro h
    apply addLinear_injective q
    simpa only [addLinear_zero] using h
  · intro h
    rw [h, addLinear_zero]

theorem addLinear_transitive (q r : Refinement b) :
    ∃ l : V →ₗ[ZMod 2] ZMod 2, addLinear q l = r :=
  ⟨linearDifference r q, addLinear_linearDifference r q⟩

/-- The canonical action exists even when the family of refinements is empty. -/
instance instAddAction : AddAction (V →ₗ[ZMod 2] ZMod 2) (Refinement b) where
  vadd l q := addLinear q l
  add_vadd l m q := addLinear_add q l m
  zero_vadd := addLinear_zero

instance instVSub : VSub (V →ₗ[ZMod 2] ZMod 2) (Refinement b) where
  vsub := linearDifference

/-- A nonempty family of refinements is an affine space over the dual vector
space, with no choice of origin used to define either operation. -/
instance instAddTorsor [Nonempty (Refinement b)] :
    AddTorsor (V →ₗ[ZMod 2] ZMod 2) (Refinement b) where
  vsub_vadd' := addLinear_linearDifference
  vadd_vsub' l q := linearDifference_addLinear q l

/-- A named reference exposes the entire bundled structure to declaration
audits, including the canonical action and subtraction instances. -/
abbrev canonicalTorsor [Nonempty (Refinement b)] :
    AddTorsor (V →ₗ[ZMod 2] ZMod 2) (Refinement b) := inferInstance

@[simp] theorem vadd_apply (l : V →ₗ[ZMod 2] ZMod 2) (q : Refinement b) (x : V) :
    (l +ᵥ q).value x = q.value x + l x := rfl

@[simp] theorem vsub_apply (q r : Refinement b) (x : V) :
    (q -ᵥ r : V →ₗ[ZMod 2] ZMod 2) x = q.value x - r.value x := rfl

end PaperXI.DyadicTorsor
