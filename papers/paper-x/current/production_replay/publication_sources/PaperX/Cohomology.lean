import Mathlib.LinearAlgebra.Quotient.Basic
import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.DirectSum.Module
import Mathlib.Tactic

/-!
Paper X, Block 04. Actual three-term cohomology ker(d_out)/im(d_in),
with functorial maps induced by cochain maps. No decomposition is assumed.
A three-term window at any degree is enough to compute that degree's cohomology.
-/
set_option autoImplicit false
namespace PaperX.Cohomology

universe u v

/-- Three consecutive terms of a cochain complex, including d_out d_in = 0. -/
structure Triple (R : Type u) [CommRing R] where
  X₀ : Type v
  X₁ : Type v
  X₂ : Type v
  [add₀ : AddCommGroup X₀]
  [add₁ : AddCommGroup X₁]
  [add₂ : AddCommGroup X₂]
  [mod₀ : Module R X₀]
  [mod₁ : Module R X₁]
  [mod₂ : Module R X₂]
  d₀ : X₀ →ₗ[R] X₁
  d₁ : X₁ →ₗ[R] X₂
  square : d₁.comp d₀ = 0

attribute [instance] Triple.add₀ Triple.add₁ Triple.add₂ Triple.mod₀ Triple.mod₁ Triple.mod₂

variable {R : Type u} [CommRing R]

/-- A genuine cochain map on the three-term window. -/
structure ChainMap (C D : Triple.{u,v} R) where
  left : C.X₀ →ₗ[R] D.X₀
  middle : C.X₁ →ₗ[R] D.X₁
  right : C.X₂ →ₗ[R] D.X₂
  comm₀ : D.d₀.comp left = middle.comp C.d₀
  comm₁ : D.d₁.comp middle = right.comp C.d₁

variable (C : Triple.{u,v} R)

abbrev Cycles := LinearMap.ker C.d₁

def incomingCycles : C.X₀ →ₗ[R] Cycles C :=
  C.d₀.codRestrict (Cycles C) (fun x => by
    change C.d₁ (C.d₀ x) = 0
    exact LinearMap.congr_fun C.square x)

def boundaries : Submodule R (Cycles C) := LinearMap.range (incomingCycles C)

/-- Cohomology is an actual quotient module, not a dimension or named placeholder. -/
abbrev H := (Cycles C) ⧸ boundaries C

def classOf : Cycles C →ₗ[R] H C := (boundaries C).mkQ

theorem classOf_surjective : Function.Surjective (classOf C) :=
  Submodule.mkQ_surjective _

theorem classOf_eq_zero_iff (x : Cycles C) :
    classOf C x = 0 ↔ ∃ y : C.X₀, C.d₀ y = x.1 := by
  change (Submodule.Quotient.mk x : H C) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  change (∃ y, incomingCycles C y = x) ↔ _
  constructor
  · rintro ⟨y, h⟩
    exact ⟨y, congrArg Subtype.val h⟩
  · rintro ⟨y, h⟩
    exact ⟨y, Subtype.ext h⟩

variable {C} {D E : Triple.{u,v} R}

def cyclesMap (f : ChainMap C D) : Cycles C →ₗ[R] Cycles D :=
  (f.middle.comp (Cycles C).subtype).codRestrict (Cycles D) (fun x => by
    change D.d₁ (f.middle x.1) = 0
    calc
      _ = f.right (C.d₁ x.1) := LinearMap.congr_fun f.comm₁ x.1
      _ = 0 := by rw [x.property, map_zero])

@[simp] theorem cyclesMap_val (f : ChainMap C D) (x : Cycles C) :
    (cyclesMap f x).val = f.middle x.val := rfl

theorem cyclesMap_incoming (f : ChainMap C D) (x : C.X₀) :
    cyclesMap f (incomingCycles C x) = incomingCycles D (f.left x) := by
  apply Subtype.ext
  exact (LinearMap.congr_fun f.comm₀ x).symm

def hmap (f : ChainMap C D) : H C →ₗ[R] H D :=
  (boundaries C).liftQ ((classOf D).comp (cyclesMap f)) (by
    rintro x ⟨y, rfl⟩
    change classOf D (cyclesMap f (incomingCycles C y)) = 0
    rw [cyclesMap_incoming, classOf_eq_zero_iff]
    exact ⟨f.left y, rfl⟩)

@[simp] theorem hmap_classOf (f : ChainMap C D) (x : Cycles C) :
    hmap f (classOf C x) = classOf D (cyclesMap f x) := rfl

/-- Equality of induced maps needs equality on cocycles, not arbitrary choices of representatives. -/
theorem hmap_ext (f g : ChainMap C D)
    (h : ∀ x : Cycles C, f.middle x.1 = g.middle x.1) : hmap f = hmap g := by
  apply LinearMap.ext
  intro z
  obtain ⟨x, rfl⟩ := classOf_surjective C z
  rw [hmap_classOf, hmap_classOf]
  congr 1
  exact Subtype.ext (h x)

def identityMap (C : Triple.{u,v} R) : ChainMap C C where
  left := LinearMap.id
  middle := LinearMap.id
  right := LinearMap.id
  comm₀ := by simp
  comm₁ := by simp

def compose (g : ChainMap D E) (f : ChainMap C D) : ChainMap C E where
  left := g.left.comp f.left
  middle := g.middle.comp f.middle
  right := g.right.comp f.right
  comm₀ := by rw [← LinearMap.comp_assoc, g.comm₀, LinearMap.comp_assoc,
    f.comm₀, ← LinearMap.comp_assoc]
  comm₁ := by rw [← LinearMap.comp_assoc, g.comm₁, LinearMap.comp_assoc,
    f.comm₁, ← LinearMap.comp_assoc]

@[simp] theorem hmap_identity : hmap (identityMap C) = LinearMap.id := by
  apply LinearMap.ext
  intro z
  obtain ⟨x, rfl⟩ := classOf_surjective C z
  rfl

@[simp] theorem hmap_compose (g : ChainMap D E) (f : ChainMap C D) :
    hmap (compose g f) = (hmap g).comp (hmap f) := by
  apply LinearMap.ext
  intro z
  obtain ⟨x, rfl⟩ := classOf_surjective C z
  rfl

end PaperX.Cohomology
