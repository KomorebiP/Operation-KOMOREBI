import Mathlib.CategoryTheory.Groupoid.FreeGroupoid
import Mathlib.CategoryTheory.Endomorphism
import Mathlib.GroupTheory.Abelianization.Defs

/-!
# Reduced graph loops and their abelianization

Edges belong to the original quiver. A path in its symmetrification can traverse
an edge in either direction. The free groupoid identifies paths under insertion
and deletion of an edge followed by its reverse. Based endomorphisms therefore
give the combinatorial fundamental group, with multiplication ordered as function
composition: `x * y` traverses `y` before `x`.

`H1` is the abelianization of this actual path quotient. No comparison with a
topological realization or singular homology is asserted here.
-/

namespace PaperXI.GraphLoop

open CategoryTheory

universe u v w

variable {α : Type u} [Quiver.{v} α]

/-- The object of the free groupoid represented by a graph vertex. -/
abbrev vertex (r : α) : Quiver.FreeGroupoid α :=
  (Quiver.FreeGroupoid.of α).obj r

/-- The quotient class of an actual oriented path. -/
def pathClass {u v : α} (p : @Quiver.Path (Quiver.Symmetrify α) _ u v) :
    vertex u ⟶ vertex v :=
  (CategoryTheory.Quotient.functor Quiver.FreeGroupoid.redStep).map p

@[simp] theorem pathClass_nil (r : α) :
    pathClass (@Quiver.Path.nil (Quiver.Symmetrify α) _ r) = 𝟙 (vertex r) := rfl

@[simp] theorem pathClass_comp {u v w : α}
    (p : @Quiver.Path (Quiver.Symmetrify α) _ u v)
    (q : @Quiver.Path (Quiver.Symmetrify α) _ v w) :
    pathClass (p.comp q) = pathClass p ≫ pathClass q := rfl

@[simp] theorem pathClass_reverse {u v : α}
    (p : @Quiver.Path (Quiver.Symmetrify α) _ u v) :
    pathClass p.reverse = Groupoid.inv (pathClass p) := rfl

/-- Every morphism of the graph groupoid is represented by an actual path. -/
theorem pathClass_surjective (u v : α) :
    Function.Surjective (@pathClass α _ u v) :=
  (CategoryTheory.Quotient.functor Quiver.FreeGroupoid.redStep).map_surjective

/-- The group of actual reduced loops based at `r`. -/
abbrev Loop (r : α) := CategoryTheory.End (vertex r)

/-- A based path as an element of the reduced loop group. -/
def loopClass {r : α} (p : @Quiver.Path (Quiver.Symmetrify α) _ r r) : Loop r :=
  pathClass p

@[simp] theorem loopClass_nil (r : α) :
    loopClass (@Quiver.Path.nil (Quiver.Symmetrify α) _ r) = 1 := rfl

/-- Multiplication follows function composition, so path concatenation reverses its order. -/
@[simp] theorem loopClass_comp {r : α}
    (p q : @Quiver.Path (Quiver.Symmetrify α) _ r r) :
    loopClass (p.comp q) = loopClass q * loopClass p := rfl

@[simp] theorem loopClass_reverse {r : α}
    (p : @Quiver.Path (Quiver.Symmetrify α) _ r r) :
    loopClass p.reverse = (loopClass p)⁻¹ := rfl

theorem loopClass_surjective (r : α) :
    Function.Surjective (@loopClass α _ r) := pathClass_surjective r r

/-- The first combinatorial homology group, defined as the abelianization of reduced loops. -/
abbrev H1 (r : α) := Abelianization (Loop r)

/-- The canonical homomorphism from reduced loops to their abelianization. -/
def homologyClass (r : α) : Loop r →* H1 r := Abelianization.of

@[simp] theorem homologyClass_mul (r : α) (x y : Loop r) :
    homologyClass r (x * y) = homologyClass r x * homologyClass r y := rfl

/-- Abelian characters of reduced loops are exactly characters of `H1`. -/
def factorCharacter (r : α) (C : Type w) [CommGroup C] :
    (Loop r →* C) ≃ (H1 r →* C) := Abelianization.lift

@[simp] theorem factorCharacter_apply_class {r : α} {C : Type w} [CommGroup C]
    (χ : Loop r →* C) (x : Loop r) :
    factorCharacter r C χ (homologyClass r x) = χ x := rfl

/-- The character factorization is unique, including its values away from chosen loops. -/
theorem factorCharacter_unique {r : α} {C : Type w} [CommGroup C]
    (χ : Loop r →* C) (ψ : H1 r →* C)
    (h : ∀ x, ψ (homologyClass r x) = χ x) : ψ = factorCharacter r C χ := by
  ext x
  exact Abelianization.lift_unique χ ψ h

/-- Equality on represented paths suffices for equality of loop homomorphisms. -/
theorem character_ext_paths {r : α} {C : Type w} [Monoid C]
    (χ ψ : Loop r →* C)
    (h : ∀ p, χ (loopClass p) = ψ (loopClass p)) : χ = ψ := by
  ext x
  obtain ⟨p, rfl⟩ := loopClass_surjective r x
  exact h p

end PaperXI.GraphLoop
