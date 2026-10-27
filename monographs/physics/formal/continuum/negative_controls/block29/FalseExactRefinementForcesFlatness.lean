import KomorebiPhysics.Relativistic3DEdgeCompatibility

open KomorebiPhysics
open Relativistic3DCliffordTransportU1
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DFullWalkRefinement
open Relativistic3DEdgeCompatibility

/-- Deliberately false: exact fixed-order refinement alone does not force the
coarse `xy` plaquette to be trivial. -/
example {Site : Type} {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (r : PhaseFrame Site) (p : FineSite3 Site) (ψ : State (Site := Site))
    (hcomm : ∀ s, τy (τx s) = τx (τy s))
    (hexact : refinedSevenFactorWalk D τx τy τz ux uy uz r (frameEmbed r ψ) =
      frameEmbed r (sevenFactorWalk M τx τy τz ux uy uz ψ)) :
    Relativistic3DGeometricEdgeRefinement.plaquette τx τy ux uy p.1 = 1 := by
  -- `hexact` is automatic for the canonical links, even when this plaquette
  -- is nontrivial.
