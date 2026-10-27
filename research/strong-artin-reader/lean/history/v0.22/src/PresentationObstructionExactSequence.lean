import Mathlib.Algebra.Module.Presentation.Differentials
import Mathlib.LinearAlgebra.Isomorphisms

/-!
# Presentation obstruction exact sequence

For a polynomial presentation, the kernel of the displayed Jacobian-transpose
relation map surjects onto the intrinsic first homology of the naive cotangent
complex.  The kernel of this surjection is exactly the redundancy among the
chosen relation generators.  Thus the presentation-dependent dual obstruction
agrees with intrinsic cotangent H1 precisely when the relation generators are
independent in the conormal module.
-/

namespace Komorebi.StrongArtin.PresentationObstructionExactSequence

open Module

noncomputable section

universe u v w t

variable {R : Type u} {S : Type v} {ι : Type w} {σ : Type t}
  [CommRing R] [CommRing S] [Algebra R S]

set_option backward.isDefEq.respectTransparency false in
/-- The relation differential map with the presentation index types exposed.
In bases this is the transpose Jacobian of the chosen relations. -/
def relationDifferentialMap (P : Algebra.Presentation R S ι σ) :
    (σ →₀ S) →ₗ[S] (ι →₀ S) :=
  P.differentialsRelations.map

/-- The kernel of the relation differential map in a chosen presentation.  In
coordinates this is the kernel of the transpose Jacobian. -/
abbrev presentationObstructionDual (P : Algebra.Presentation R S ι σ) : Type _ :=
  LinearMap.ker (relationDifferentialMap P)

set_option backward.isDefEq.respectTransparency false in
theorem cotangentComplex_comp_hom₁ (P : Algebra.Presentation R S ι σ) :
    P.toExtension.cotangentComplex.comp
        (Algebra.Presentation.differentials.hom₁ P) =
      P.cotangentSpaceBasis.repr.symm.toLinearMap.comp
        (relationDifferentialMap P) := by
  simpa [relationDifferentialMap] using
    Algebra.Presentation.differentials.comm₁₂ P

/-- The canonical map from the presentation-dependent kernel of relation
differentials to the intrinsic first homology of the naive cotangent complex. -/
def toH1Cotangent (P : Algebra.Presentation R S ι σ) :
    presentationObstructionDual P →ₗ[S] P.toExtension.H1Cotangent := by
  refine (Algebra.Presentation.differentials.hom₁ P).restrict
    (p := LinearMap.ker (relationDifferentialMap P))
    (q := LinearMap.ker P.toExtension.cotangentComplex) ?_
  intro x hx
  change relationDifferentialMap P x = 0 at hx
  change P.toExtension.cotangentComplex
      (Algebra.Presentation.differentials.hom₁ P x) = 0
  have hcomm := DFunLike.congr_fun (cotangentComplex_comp_hom₁ P) x
  simpa [hx] using hcomm

@[simp]
theorem toH1Cotangent_apply_val (P : Algebra.Presentation R S ι σ)
    (x : presentationObstructionDual P) :
    (toH1Cotangent P x).1 =
      Algebra.Presentation.differentials.hom₁ P x.1 := rfl

/-- Every intrinsic cotangent-H1 class is represented by a relation vector in
the kernel of the displayed Jacobian transpose. -/
theorem toH1Cotangent_surjective (P : Algebra.Presentation R S ι σ) :
    Function.Surjective (toH1Cotangent P) := by
  intro h
  obtain ⟨x, hx⟩ :=
    Algebra.Presentation.differentials.surjective_hom₁ P h.1
  have hxker : x ∈ LinearMap.ker (relationDifferentialMap P) := by
    change relationDifferentialMap P x = 0
    apply P.cotangentSpaceBasis.repr.symm.injective
    calc
      P.cotangentSpaceBasis.repr.symm (relationDifferentialMap P x) =
          P.toExtension.cotangentComplex
            (Algebra.Presentation.differentials.hom₁ P x) := by
              symm
              exact DFunLike.congr_fun
                (cotangentComplex_comp_hom₁ P) x
      _ = 0 := by simpa [hx] using h.2
      _ = P.cotangentSpaceBasis.repr.symm 0 := by simp
  refine ⟨⟨x, hxker⟩, ?_⟩
  apply Subtype.ext
  exact hx

/-- Relation syzygies: presentation-obstruction vectors whose conormal class is
already zero. -/
def relationSyzygies (P : Algebra.Presentation R S ι σ) :
    Submodule S (presentationObstructionDual P) :=
  LinearMap.ker (toH1Cotangent P)

/-- Membership in the syzygy kernel can be tested before restriction: it means
that the chosen linear combination of relation generators is zero in the
conormal module. -/
theorem mem_relationSyzygies_iff_hom₁_eq_zero
    (P : Algebra.Presentation R S ι σ)
    (x : presentationObstructionDual P) :
    x ∈ relationSyzygies P ↔
      Algebra.Presentation.differentials.hom₁ P x.1 = 0 := by
  rw [relationSyzygies, LinearMap.mem_ker]
  constructor
  · intro h
    exact congrArg Subtype.val h
  · intro h
    apply Subtype.ext
    exact h

/-- If the chosen relation generators are independent in the conormal module,
the displayed Jacobian-transpose kernel is already the intrinsic cotangent H1. -/
theorem toH1Cotangent_injective_of_relationIndependent
    (P : Algebra.Presentation R S ι σ)
    (hrel : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P)) :
    Function.Injective (toH1Cotangent P) := by
  intro x y hxy
  apply Subtype.ext
  apply hrel
  exact congrArg Subtype.val hxy

/-- Under conormal independence of the chosen relations, presentation dual
obstructions and intrinsic cotangent H1 are linearly equivalent. -/
def obstructionDualEquivH1_of_relationIndependent
    (P : Algebra.Presentation R S ι σ)
    (hrel : Function.Injective
      (Algebra.Presentation.differentials.hom₁ P)) :
    presentationObstructionDual P ≃ₗ[S] P.toExtension.H1Cotangent :=
  LinearEquiv.ofBijective (toH1Cotangent P)
    ⟨toH1Cotangent_injective_of_relationIndependent P hrel,
      toH1Cotangent_surjective P⟩

/-- Exactness of the syzygy inclusion followed by the intrinsic obstruction map. -/
theorem exact_syzygy_to_obstruction_to_h1
    (P : Algebra.Presentation R S ι σ) :
    Function.Exact (Submodule.subtype (relationSyzygies P))
      (toH1Cotangent P) := by
  rw [LinearMap.exact_iff]
  exact (Submodule.range_subtype (relationSyzygies P)).symm

end

end Komorebi.StrongArtin.PresentationObstructionExactSequence

#print axioms Komorebi.StrongArtin.PresentationObstructionExactSequence.toH1Cotangent_surjective
#print axioms Komorebi.StrongArtin.PresentationObstructionExactSequence.obstructionDualEquivH1_of_relationIndependent
#print axioms Komorebi.StrongArtin.PresentationObstructionExactSequence.exact_syzygy_to_obstruction_to_h1
