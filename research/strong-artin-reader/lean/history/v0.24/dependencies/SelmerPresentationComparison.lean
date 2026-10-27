import PresentationIntrinsicObstructionCapstone

/-!
# Selmer-to-presentation comparison interface

A global arithmetic comparison should identify the intrinsic cotangent H1 of a
presentation with the relevant Selmer obstruction space.  Once such an
identification is supplied, the raw transpose-Jacobian kernel maps onto the
Selmer space, and its kernel is exactly relation redundancy.  Under conormal
independence this becomes a linear equivalence.
-/

namespace Komorebi.StrongArtin.SelmerPresentationComparison

open Module
open Komorebi.StrongArtin.PresentationObstructionExactSequence
open Komorebi.StrongArtin.PresentationIntrinsicObstructionCapstone

noncomputable section

universe u v w t z

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [CommRing S] [Algebra R S]

/-- Arithmetic comparison datum between intrinsic cotangent H1 and a declared
Selmer obstruction space.  The existence of this datum is the domain-specific
local-global input; all presentation consequences below are formal. -/
structure Datum (P : Algebra.Presentation R S ι σ)
    (H : Type z) [AddCommGroup H] [Module S H] where
  intrinsicEquiv : P.toExtension.H1Cotangent ≃ₗ[S] H

variable {H : Type z} [AddCommGroup H] [Module S H]

/-- Canonical map from the presentation-dependent transpose-Jacobian kernel to
the arithmetic Selmer obstruction space. -/
def Datum.presentationToSelmer
    {P : Algebra.Presentation R S ι σ} (D : Datum P H) :
    presentationObstructionDual P →ₗ[S] H :=
  D.intrinsicEquiv.toLinearMap.comp (toH1Cotangent P)

@[simp]
theorem Datum.presentationToSelmer_apply
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (x : presentationObstructionDual P) :
    D.presentationToSelmer x = D.intrinsicEquiv (toH1Cotangent P x) := rfl

/-- Every arithmetic Selmer obstruction has a presentation-kernel
representative. -/
theorem Datum.presentationToSelmer_surjective
    {P : Algebra.Presentation R S ι σ} (D : Datum P H) :
    Function.Surjective D.presentationToSelmer :=
  D.intrinsicEquiv.surjective.comp (toH1Cotangent_surjective P)

set_option backward.defeqAttrib.useBackward true in
set_option backward.isDefEq.respectTransparency false in
/-- The kernel of the map to arithmetic Selmer obstructions is exactly the
relation-syzygy submodule. -/
theorem Datum.ker_presentationToSelmer
    {P : Algebra.Presentation R S ι σ} (D : Datum P H) :
    LinearMap.ker D.presentationToSelmer = relationSyzygies P := by
  ext x
  change D.intrinsicEquiv (toH1Cotangent P x) = 0 ↔
    toH1Cotangent P x = 0
  constructor
  · intro hx
    exact D.intrinsicEquiv.injective (by simpa using hx)
  · intro hx
    simp [hx]

/-- Exactness of relation syzygies, the raw presentation kernel, and the
arithmetic Selmer obstruction space. -/
theorem Datum.exact_syzygy_to_presentation_to_selmer
    {P : Algebra.Presentation R S ι σ} (D : Datum P H) :
    Function.Exact (Submodule.subtype (relationSyzygies P))
      D.presentationToSelmer := by
  rw [LinearMap.exact_iff]
  exact D.ker_presentationToSelmer.trans
    (Submodule.range_subtype (relationSyzygies P)).symm

/-- The raw presentation kernel identifies injectively with the Selmer space
exactly when the chosen relation generators are conormally independent. -/
theorem Datum.presentationToSelmer_injective_iff_relationIndependent
    {P : Algebra.Presentation R S ι σ} (D : Datum P H) :
    Function.Injective D.presentationToSelmer ↔
      Function.Injective (Algebra.Presentation.differentials.hom₁ P) := by
  constructor
  · intro hinj
    have hto : Function.Injective (toH1Cotangent P) := by
      intro x y hxy
      apply hinj
      simp [hxy]
    exact relationIndependent_of_toH1Cotangent_injective P hto
  · intro hrel
    exact D.intrinsicEquiv.injective.comp
      (toH1Cotangent_injective_of_relationIndependent P hrel)

/-- Under conormal independence, the displayed transpose-Jacobian kernel is
linearly equivalent to the arithmetic Selmer obstruction space. -/
def Datum.presentationObstructionEquivSelmer
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (hrel : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P)) :
    presentationObstructionDual P ≃ₗ[S] H :=
  (obstructionDualEquivH1_of_relationIndependent P hrel).trans
    D.intrinsicEquiv

@[simp]
theorem Datum.presentationObstructionEquivSelmer_apply
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (hrel : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P))
    (x : presentationObstructionDual P) :
    D.presentationObstructionEquivSelmer hrel x =
      D.presentationToSelmer x := rfl

/-- Any arithmetic functional pulled back from the intrinsic Selmer space
annihilates every relation syzygy.  Presentation redundancy therefore cannot
be removed by genuine arithmetic obstruction functionals; it must be quotiented
out or excluded by an independent-relation presentation. -/
theorem Datum.functional_vanishes_on_relationSyzygies
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (φ : H →ₗ[S] S) {x : presentationObstructionDual P}
    (hx : x ∈ relationSyzygies P) :
    φ (D.presentationToSelmer x) = 0 := by
  have hxker : x ∈ LinearMap.ker D.presentationToSelmer := by
    rw [D.ker_presentationToSelmer]
    exact hx
  change φ (D.presentationToSelmer x) = 0
  rw [LinearMap.mem_ker.mp hxker, map_zero]


/-- If relation syzygies are nonzero, no family consisting only of genuine
Selmer functionals can detect every nonzero vector in the raw presentation
kernel.  This is the formal obstruction to running auxiliary selection on a
redundant Jacobian presentation. -/
theorem Datum.no_complete_arithmetic_detection_of_nonzero_syzygies
    [Nontrivial S]
    {P : Algebra.Presentation R S ι σ} (D : Datum P H)
    (hsyz : relationSyzygies P ≠ ⊥) :
    ¬ (∀ x : presentationObstructionDual P, x ≠ 0 →
      ∃ φ : H →ₗ[S] S, φ (D.presentationToSelmer x) ≠ 0) := by
  intro hdetect
  obtain ⟨x, hxsyz, hxne⟩ :=
    (Submodule.ne_bot_iff (relationSyzygies P)).mp hsyz
  obtain ⟨φ, hφ⟩ := hdetect x hxne
  exact hφ (D.functional_vanishes_on_relationSyzygies φ hxsyz)

end

end Komorebi.StrongArtin.SelmerPresentationComparison

#print axioms Komorebi.StrongArtin.SelmerPresentationComparison.Datum.ker_presentationToSelmer
#print axioms Komorebi.StrongArtin.SelmerPresentationComparison.Datum.presentationToSelmer_injective_iff_relationIndependent
#print axioms Komorebi.StrongArtin.SelmerPresentationComparison.Datum.functional_vanishes_on_relationSyzygies
#print axioms Komorebi.StrongArtin.SelmerPresentationComparison.Datum.no_complete_arithmetic_detection_of_nonzero_syzygies
