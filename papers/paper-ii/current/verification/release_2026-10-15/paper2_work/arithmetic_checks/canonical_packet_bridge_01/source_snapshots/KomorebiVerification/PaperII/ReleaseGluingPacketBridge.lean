import KomorebiVerification.PaperII.ReleaseGluingDVR
import KomorebiVerification.PaperII.NestedRefinement

/-! The genuine lattice quotient construction consumes the existing packet/refinement interface. -/

set_option autoImplicit false

namespace Komorebi.PaperII.ReleaseGluing

open Komorebi.Foundation

universe u v w
variable {O : Type u} {K : Type v} {V : Type w}
variable [CommRing O] [CommRing K] [Algebra O K]
variable [AddCommGroup V] [Module O V] [Module K V] [IsScalarTower O K V]
variable {I J : Type*} [Fintype I] [Fintype J]

def ofLinearProjectorFamily (P : LinearProjectorFamily K V I) : Projectors K V I where
  proj := P.proj
  idem i := by ext x; exact P.idempotent i x
  orthogonal i j hij := by ext x; exact P.orthogonal hij x
  complete := by
    ext x
    simpa only [LinearMap.sum_apply, Module.End.one_apply] using P.complete x

/-- Existing refinement, rather than an assumed range-containment conclusion, supplies the lattice inclusion. -/
theorem original_refinement_range_containment
    (P : LinearProjectorFamily K V I) (Q : LinearProjectorFamily K V J)
    (parent : J → I) (h : NestedRefinement.Refines P Q parent) (j : J) :
    LinearMap.range (((ofLinearProjectorFamily Q).restrictScalars (O := O)).proj j) ≤
      LinearMap.range (((ofLinearProjectorFamily P).restrictScalars (O := O)).proj (parent j)) := by
  rintro x ⟨y, rfl⟩
  refine ⟨Q.proj j y, ?_⟩
  exact h.coarse_fine_apply_eq_self j y

/-- The displayed quotient exact sequence under the original refinement relation. -/
theorem original_refinement_gluing_short_exact
    (P : LinearProjectorFamily K V I) (Q : LinearProjectorFamily K V J)
    (parent : J → I) (h : NestedRefinement.Refines P Q parent) (Λ : Submodule O V) :
    let P' := (ofLinearProjectorFamily P).restrictScalars (O := O)
    let Q' := (ofLinearProjectorFamily Q).restrictScalars (O := O)
    let incl := splitInside_le_of_refines P' Λ Q' parent
      (original_refinement_range_containment P Q parent h)
    Function.Injective (quotientInclusion (splitInside Q' Λ) (splitInside P' Λ)) ∧
    LinearMap.range (quotientInclusion (splitInside Q' Λ) (splitInside P' Λ)) =
      LinearMap.ker (Submodule.factor incl) ∧
    Function.Surjective (Submodule.factor incl) := by
  exact gluing_refinement_short_exact _ _ _ parent
    (original_refinement_range_containment P Q parent h)

/-- The original refinement relation gives monotonicity of the genuine least gluing weights. -/
theorem original_refinement_globalWeight_mono
    (P : LinearProjectorFamily K V I) (Q : LinearProjectorFamily K V J)
    (parent : J → I) (h : NestedRefinement.Refines P Q parent) (Λ : Submodule O V) (pi : O)
    (finiteP : ∀ i, ∃ s, ClearsPacket
      ((ofLinearProjectorFamily P).restrictScalars (O := O)) Λ pi i s)
    (finiteQ : ∀ j, ∃ s, ClearsPacket
      ((ofLinearProjectorFamily Q).restrictScalars (O := O)) Λ pi j s) :
    globalWeight ((ofLinearProjectorFamily P).restrictScalars (O := O)) Λ pi finiteP ≤
      globalWeight ((ofLinearProjectorFamily Q).restrictScalars (O := O)) Λ pi finiteQ := by
  exact globalWeight_mono_of_refines _ _ _ pi finiteP finiteQ parent
    (original_refinement_range_containment P Q parent h)

end Komorebi.PaperII.ReleaseGluing
