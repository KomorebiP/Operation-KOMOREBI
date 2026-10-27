import Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree
import Mathlib.LinearAlgebra.Isomorphisms

/-!
# First-order representation deformations and one-cocycles

For a group representation `rho`, the derivative of the multiplicativity equations
is normalized by right multiplication with `rho(g⁻¹)`.  This identifies the
representation tangent space with the ordinary one-cocycles of the adjoint
representation.
-/

namespace Komorebi.StrongArtin.RepresentationTangentCocycles

open Representation
open groupCohomology

noncomputable section

universe u w

variable {k G : Type u} {V : Type w} [CommRing k] [Group G]
  [AddCommGroup V] [Module k V]

/-- The adjoint representation on endomorphisms. -/
abbrev AdRep (rho : Representation k G V) : Rep.{w} k G :=
  Rep.of (Representation.linHom rho rho)

/-- The derivative of the representation multiplication equations at `rho`.
A tangent `delta` satisfies the Leibniz rule
`delta(gh) = delta(g) rho(h) + rho(g) delta(h)`. -/
def representationTangents (rho : Representation k G V) :
    Submodule k (G → Module.End k V) where
  carrier := {delta | ∀ g h : G,
    delta (g * h) = delta g * rho h + rho g * delta h}
  zero_mem' := by
    intro g h
    simp
  add_mem' := by
    intro a b ha hb g h
    rw [Pi.add_apply, Pi.add_apply, Pi.add_apply, ha g h, hb g h]
    simp only [add_mul, mul_add]
    abel
  smul_mem' := by
    intro c a ha g h
    rw [Pi.smul_apply, Pi.smul_apply, Pi.smul_apply, ha g h]
    simp only [smul_add, smul_mul_assoc, mul_smul_comm]

@[simp] theorem mem_representationTangents_iff
    (rho : Representation k G V) (delta : G → Module.End k V) :
    delta ∈ representationTangents rho ↔
      ∀ g h : G, delta (g * h) = delta g * rho h + rho g * delta h :=
  Iff.rfl

/-- Normalize an unnormalized representation tangent by right multiplication
with the inverse representation matrix. -/
def normalizeTangent (rho : Representation k G V)
    (delta : representationTangents rho) : G → Module.End k V :=
  fun g => delta.1 g * rho g⁻¹

/-- Denormalize an adjoint cocycle by right multiplication with `rho(g)`. -/
def denormalizeCocycle (rho : Representation k G V)
    (f : cocycles₁ (AdRep rho)) : G → Module.End k V :=
  fun g => f g * rho g

/-- A normalized representation tangent satisfies the adjoint cocycle law. -/
theorem normalizeTangent_isCocycle
    (rho : Representation k G V)
    (delta : representationTangents rho) :
    normalizeTangent rho delta ∈ cocycles₁ (AdRep rho) := by
  rw [mem_cocycles₁_iff]
  intro g h
  change delta.1 (g * h) * rho (g * h)⁻¹ =
    (rho g ∘ₗ (delta.1 h * rho h⁻¹) ∘ₗ rho g⁻¹) +
      delta.1 g * rho g⁻¹
  rw [delta.2 g h]
  simp only [Module.End.mul_eq_comp]
  ext x
  simp [LinearMap.add_apply, LinearMap.comp_apply]
  abel

/-- An adjoint cocycle denormalizes to a tangent of the representation equations. -/
theorem denormalizeCocycle_isTangent
    (rho : Representation k G V)
    (f : cocycles₁ (AdRep rho)) :
    denormalizeCocycle rho f ∈ representationTangents rho := by
  rw [mem_representationTangents_iff]
  intro g h
  have hf := (mem_cocycles₁_iff f).1 f.2 g h
  change f (g * h) * rho (g * h) =
    (f g * rho g) * rho h + rho g * (f h * rho h)
  rw [hf]
  simp only [Representation.linHom_apply, map_mul, Module.End.mul_eq_comp]
  ext x
  simp [LinearMap.add_apply, LinearMap.comp_apply]
  abel

/-- Normalization as a linear map from representation tangents to adjoint cocycles. -/
def tangentToCocycle (rho : Representation k G V) :
    representationTangents rho →ₗ[k] cocycles₁ (AdRep rho) where
  toFun delta := ⟨normalizeTangent rho delta,
    normalizeTangent_isCocycle rho delta⟩
  map_add' a b := by
    apply Subtype.ext
    funext g
    change (a.1 g + b.1 g) * rho g⁻¹ =
      a.1 g * rho g⁻¹ + b.1 g * rho g⁻¹
    exact add_mul _ _ _
  map_smul' c a := by
    apply Subtype.ext
    funext g
    change (c • a.1 g) * rho g⁻¹ = c • (a.1 g * rho g⁻¹)
    exact smul_mul_assoc c (a.1 g) (rho g⁻¹)

/-- Denormalization as a linear map from adjoint cocycles to representation tangents. -/
def cocycleToTangent (rho : Representation k G V) :
    cocycles₁ (AdRep rho) →ₗ[k] representationTangents rho where
  toFun f := ⟨denormalizeCocycle rho f,
    denormalizeCocycle_isTangent rho f⟩
  map_add' a b := by
    apply Subtype.ext
    funext g
    change (a.1 g + b.1 g) * rho g =
      a.1 g * rho g + b.1 g * rho g
    exact add_mul _ _ _
  map_smul' c a := by
    apply Subtype.ext
    funext g
    change (c • a.1 g) * rho g = c • (a.1 g * rho g)
    exact smul_mul_assoc c (a.1 g) (rho g)

/-- Representation-equation tangents are exactly adjoint one-cocycles. -/
def tangentEquivCocycles (rho : Representation k G V) :
    representationTangents rho ≃ₗ[k] cocycles₁ (AdRep rho) where
  toLinearMap := tangentToCocycle rho
  invFun := cocycleToTangent rho
  left_inv delta := by
    apply Subtype.ext
    funext g
    change (delta.1 g * rho g⁻¹) * rho g = delta.1 g
    simp only [Module.End.mul_eq_comp]
    ext x
    simp [LinearMap.comp_apply]
  right_inv f := by
    apply Subtype.ext
    funext g
    change (f g * rho g) * rho g⁻¹ = f g
    simp only [Module.End.mul_eq_comp]
    ext x
    simp [LinearMap.comp_apply]

@[simp] theorem tangentEquivCocycles_apply
    (rho : Representation k G V) (delta : representationTangents rho) (g : G) :
    tangentEquivCocycles rho delta g = delta.1 g * rho g⁻¹ := rfl

@[simp] theorem tangentEquivCocycles_symm_apply
    (rho : Representation k G V) (f : cocycles₁ (AdRep rho)) (g : G) :
    ((tangentEquivCocycles rho).symm f).1 g = f g * rho g := rfl

end

end Komorebi.StrongArtin.RepresentationTangentCocycles

#print axioms Komorebi.StrongArtin.RepresentationTangentCocycles.tangentEquivCocycles
