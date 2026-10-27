module

public import KomorebiPhysics.Relativistic3DFullWalkRefinement

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Arbitrary-link refinement: edge compatibility and curvature transport

For a fixed factorwise refinement of the Clifford walk, the exact local
obstruction is not face curvature by itself.  It is failure of the two ordered
half-links to reconstruct the framed coarse link.  This module proves the
arbitrary-link two-half-step theorem in all three directions, composes it
through the complete `M-X-Y-Z-Y-X-M` walk, and transports a nontrivial coarse
plaquette exactly to the corresponding two-by-two fine Wilson loop.

It also develops an exact one-axis Hilbert defect formula for arbitrary
half-link pairs and gives a flat-but-edge-mismatched counterexample.  Therefore
an unconditional curvature-only bound for arbitrary fine links is false:
straight-edge reconstruction data and path curvature are distinct quantities.
-/

namespace KomorebiPhysics
namespace Relativistic3DEdgeCompatibility

open scoped BigOperators ComplexConjugate
open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DCubicalRefinement
open Relativistic3DFullWalkRefinement

universe u

/-! ## Straight two-half-edge compatibility -/

/-- Target framed product for two `x` half-links. -/
def targetProductX {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (p : FineSite3 Site) : Circle :=
  r (Relativistic3DFullWalkRefinement.coarseLift τ p) * u p.1 * (r p)⁻¹

/-- Target framed product for two `y` half-links. -/
def targetProductY {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (p : FineSite3 Site) : Circle :=
  r (Relativistic3DFullWalkRefinement.coarseLift τ p) * u p.1 * (r p)⁻¹

/-- Target framed product for two `z` half-links. -/
def targetProductZ {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (p : FineSite3 Site) : Circle :=
  r (Relativistic3DFullWalkRefinement.coarseLift τ p) * u p.1 * (r p)⁻¹

/-- An arbitrary fine `x` link reconstructs the framed coarse link after two
ordered half steps. -/
def StraightCompatibleX {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) : Prop :=
  ∀ p, v (halfShiftX τ p) * v p = targetProductX τ u r p

/-- `y`-direction straight-edge compatibility. -/
def StraightCompatibleY {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) : Prop :=
  ∀ p, v (halfShiftY τ p) * v p = targetProductY τ u r p

/-- `z`-direction straight-edge compatibility. -/
def StraightCompatibleZ {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) : Prop :=
  ∀ p, v (halfShiftZ τ p) * v p = targetProductZ τ u r p

/-- Canonical frame links satisfy the arbitrary-link compatibility contract. -/
@[simp] theorem frameLinkX_straightCompatible {Site : Type u}
    (τ : Site ≃ Site) (u : Link (Site := Site)) (r : PhaseFrame Site) :
    StraightCompatibleX τ u r (frameLinkX τ u r) := by
  intro p
  exact frameLinkX_two_step τ u r p

@[simp] theorem frameLinkY_straightCompatible {Site : Type u}
    (τ : Site ≃ Site) (u : Link (Site := Site)) (r : PhaseFrame Site) :
    StraightCompatibleY τ u r (frameLinkY τ u r) := by
  intro p
  exact frameLinkY_two_step τ u r p

@[simp] theorem frameLinkZ_straightCompatible {Site : Type u}
    (τ : Site ≃ Site) (u : Link (Site := Site)) (r : PhaseFrame Site) :
    StraightCompatibleZ τ u r (frameLinkZ τ u r) := by
  intro p
  exact frameLinkZ_two_step τ u r p

/-- Straight `x` reconstruction is invariant under simultaneous coarse and
fine site-gauge transformations. -/
theorem StraightCompatibleX.gauge {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleX τ u r v)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    StraightCompatibleX τ (gaugeLink τ g u) (gaugeFrame r g G)
      (gaugeLink (halfShiftX τ) G v) := by
  intro p
  simp only [gaugeLink]
  rw [halfShiftX_sq]
  calc
    (G (Relativistic3DFullWalkRefinement.coarseLift τ p) * v (halfShiftX τ p) * (G (halfShiftX τ p))⁻¹) *
        (G (halfShiftX τ p) * v p * (G p)⁻¹) =
      G (Relativistic3DFullWalkRefinement.coarseLift τ p) * (v (halfShiftX τ p) * v p) * (G p)⁻¹ := by group
    _ = G (Relativistic3DFullWalkRefinement.coarseLift τ p) * targetProductX τ u r p * (G p)⁻¹ := by rw [hv p]
    _ = targetProductX τ (gaugeLink τ g u) (gaugeFrame r g G) p := by
      simp [targetProductX, gaugeFrame, gaugeLink, Relativistic3DFullWalkRefinement.coarseLift]
      group

/-- Gauge invariance of straight `y` reconstruction. -/
theorem StraightCompatibleY.gauge {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleY τ u r v)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    StraightCompatibleY τ (gaugeLink τ g u) (gaugeFrame r g G)
      (gaugeLink (halfShiftY τ) G v) := by
  intro p
  simp only [gaugeLink]
  rw [halfShiftY_sq]
  calc
    (G (Relativistic3DFullWalkRefinement.coarseLift τ p) * v (halfShiftY τ p) * (G (halfShiftY τ p))⁻¹) *
        (G (halfShiftY τ p) * v p * (G p)⁻¹) =
      G (Relativistic3DFullWalkRefinement.coarseLift τ p) * (v (halfShiftY τ p) * v p) * (G p)⁻¹ := by group
    _ = G (Relativistic3DFullWalkRefinement.coarseLift τ p) * targetProductY τ u r p * (G p)⁻¹ := by rw [hv p]
    _ = targetProductY τ (gaugeLink τ g u) (gaugeFrame r g G) p := by
      simp [targetProductY, gaugeFrame, gaugeLink, Relativistic3DFullWalkRefinement.coarseLift]
      group

/-- Gauge invariance of straight `z` reconstruction. -/
theorem StraightCompatibleZ.gauge {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleZ τ u r v)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    StraightCompatibleZ τ (gaugeLink τ g u) (gaugeFrame r g G)
      (gaugeLink (halfShiftZ τ) G v) := by
  intro p
  simp only [gaugeLink]
  rw [halfShiftZ_sq]
  calc
    (G (Relativistic3DFullWalkRefinement.coarseLift τ p) * v (halfShiftZ τ p) * (G (halfShiftZ τ p))⁻¹) *
        (G (halfShiftZ τ p) * v p * (G p)⁻¹) =
      G (Relativistic3DFullWalkRefinement.coarseLift τ p) * (v (halfShiftZ τ p) * v p) * (G p)⁻¹ := by group
    _ = G (Relativistic3DFullWalkRefinement.coarseLift τ p) * targetProductZ τ u r p * (G p)⁻¹ := by rw [hv p]
    _ = targetProductZ τ (gaugeLink τ g u) (gaugeFrame r g G) p := by
      simp [targetProductZ, gaugeFrame, gaugeLink, Relativistic3DFullWalkRefinement.coarseLift]
      group

/-- Cancel the source frame from a compatible two-edge product. -/
theorem product_mul_source_cancel (a b target u source : Circle)
    (h : a * b = target * u * source⁻¹) :
    a * (b * source) = target * u := by
  calc
    a * (b * source) = (a * b) * source := by group
    _ = (target * u * source⁻¹) * source := by rw [h]
    _ = target * u := by group

/-- Inverting the same compatible product gives the backward-channel phase. -/
theorem inverse_product_mul_target_cancel (a b target u source : Circle)
    (h : a * b = target * u * source⁻¹) :
    b⁻¹ * (a⁻¹ * target) = source * u⁻¹ := by
  calc
    b⁻¹ * (a⁻¹ * target) = (a * b)⁻¹ * target := by group
    _ = (target * u * source⁻¹)⁻¹ * target := by rw [h]
    _ = source * u⁻¹ := by group

/-- Two arbitrary compatible `x` half-links exactly realize the coarse
Clifford shift on the framed subspace. -/
theorem two_halfShiftX_frameEmbed_of_straightCompatible {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleX τ u r v)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShiftX τ) v
      (directionalShift A (halfShiftX τ) v (frameEmbed r ψ)) =
      frameEmbed r (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bx
  · have hprev := hv (τ.symm s, ⟨false, cy, bz⟩)
    have hhere := hv (s, ⟨false, cy, bz⟩)
    simp [targetProductX, halfShiftX,
      Relativistic3DFullWalkRefinement.coarseLift] at hprev hhere
    have hp := product_mul_source_cancel
      _ _ _ _ _ hprev
    have hm := inverse_product_mul_target_cancel
      _ _ _ _ _ hhere
    simp [directionalShift, frameEmbed, halfShiftX, phaseMul_mul, hp, hm]
  · have hprev := hv (τ.symm s, ⟨true, cy, bz⟩)
    have hhere := hv (s, ⟨true, cy, bz⟩)
    simp [targetProductX, halfShiftX,
      Relativistic3DFullWalkRefinement.coarseLift] at hprev hhere
    have hp := product_mul_source_cancel
      _ _ _ _ _ hprev
    have hm := inverse_product_mul_target_cancel
      _ _ _ _ _ hhere
    simp [directionalShift, frameEmbed, halfShiftX, phaseMul_mul, hp, hm]

/-- Two arbitrary compatible `y` half-links exactly realize the coarse
Clifford shift on the framed subspace. -/
theorem two_halfShiftY_frameEmbed_of_straightCompatible {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleY τ u r v)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShiftY τ) v
      (directionalShift A (halfShiftY τ) v (frameEmbed r ψ)) =
      frameEmbed r (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases cy
  · have hprev := hv (τ.symm s, ⟨bx, false, bz⟩)
    have hhere := hv (s, ⟨bx, false, bz⟩)
    simp [targetProductY, halfShiftY,
      Relativistic3DFullWalkRefinement.coarseLift] at hprev hhere
    have hp := product_mul_source_cancel
      _ _ _ _ _ hprev
    have hm := inverse_product_mul_target_cancel
      _ _ _ _ _ hhere
    simp [directionalShift, frameEmbed, halfShiftY, phaseMul_mul, hp, hm]
  · have hprev := hv (τ.symm s, ⟨bx, true, bz⟩)
    have hhere := hv (s, ⟨bx, true, bz⟩)
    simp [targetProductY, halfShiftY,
      Relativistic3DFullWalkRefinement.coarseLift] at hprev hhere
    have hp := product_mul_source_cancel
      _ _ _ _ _ hprev
    have hm := inverse_product_mul_target_cancel
      _ _ _ _ _ hhere
    simp [directionalShift, frameEmbed, halfShiftY, phaseMul_mul, hp, hm]

/-- Two arbitrary compatible `z` half-links exactly realize the coarse
Clifford shift on the framed subspace. -/
theorem two_halfShiftZ_frameEmbed_of_straightCompatible {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleZ τ u r v)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShiftZ τ) v
      (directionalShift A (halfShiftZ τ) v (frameEmbed r ψ)) =
      frameEmbed r (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bz
  · have hprev := hv (τ.symm s, ⟨bx, cy, false⟩)
    have hhere := hv (s, ⟨bx, cy, false⟩)
    simp [targetProductZ, halfShiftZ,
      Relativistic3DFullWalkRefinement.coarseLift] at hprev hhere
    have hp := product_mul_source_cancel
      _ _ _ _ _ hprev
    have hm := inverse_product_mul_target_cancel
      _ _ _ _ _ hhere
    simp [directionalShift, frameEmbed, halfShiftZ, phaseMul_mul, hp, hm]
  · have hprev := hv (τ.symm s, ⟨bx, cy, true⟩)
    have hhere := hv (s, ⟨bx, cy, true⟩)
    simp [targetProductZ, halfShiftZ,
      Relativistic3DFullWalkRefinement.coarseLift] at hprev hhere
    have hp := product_mul_source_cancel
      _ _ _ _ _ hprev
    have hm := inverse_product_mul_target_cancel
      _ _ _ _ _ hhere
    simp [directionalShift, frameEmbed, halfShiftZ, phaseMul_mul, hp, hm]

/-- Complete factorwise refined walk using arbitrary fine links. -/
def arbitraryRefinedSevenFactorWalk {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (vx vy vz : Link (Site := FineSite3 Site))
    (Ψ : State (Site := FineSite3 Site)) : State (Site := FineSite3 Site) :=
  let M2 := fun Φ => D.half.apply (D.half.apply Φ)
  let X2 := fun Φ =>
    directionalShift cliffordX (halfShiftX τx) vx
      (directionalShift cliffordX (halfShiftX τx) vx Φ)
  let Y2 := fun Φ =>
    directionalShift cliffordY (halfShiftY τy) vy
      (directionalShift cliffordY (halfShiftY τy) vy Φ)
  let Z2 := fun Φ =>
    directionalShift cliffordZ (halfShiftZ τz) vz
      (directionalShift cliffordZ (halfShiftZ τz) vz Φ)
  M2 (X2 (Y2 (Z2 (Y2 (X2 (M2 Ψ))))))

/-- The arbitrary-link refined walk is itself exactly gauge covariant. -/
theorem arbitraryRefinedSevenFactorWalk_gauge_covariant {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site)
    (vx vy vz : Link (Site := FineSite3 Site))
    (G : Gauge (Site := FineSite3 Site))
    (Ψ : State (Site := FineSite3 Site)) :
    arbitraryRefinedSevenFactorWalk D τx τy τz
      (gaugeLink (halfShiftX τx) G vx)
      (gaugeLink (halfShiftY τy) G vy)
      (gaugeLink (halfShiftZ τz) G vz)
      (gaugeState G Ψ) =
    gaugeState G (arbitraryRefinedSevenFactorWalk D τx τy τz vx vy vz Ψ) := by
  simp only [arbitraryRefinedSevenFactorWalk]
  rw [D.half.apply_gauge, D.half.apply_gauge]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [D.half.apply_gauge, D.half.apply_gauge]

/-- Straight-edge compatibility in the three directions is sufficient for
exact full-walk refinement.  No plaquette-flatness hypothesis is used. -/
theorem arbitraryRefinedSevenFactorWalk_frameEmbed {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (r : PhaseFrame Site)
    (vx vy vz : Link (Site := FineSite3 Site))
    (hx : StraightCompatibleX τx ux r vx)
    (hy : StraightCompatibleY τy uy r vy)
    (hz : StraightCompatibleZ τz uz r vz)
    (ψ : State (Site := Site)) :
    arbitraryRefinedSevenFactorWalk D τx τy τz vx vy vz
      (frameEmbed r ψ) =
    frameEmbed r (sevenFactorWalk M τx τy τz ux uy uz ψ) := by
  simp only [arbitraryRefinedSevenFactorWalk, sevenFactorWalk]
  rw [two_halfLocal_frameEmbed D r]
  rw [two_halfShiftX_frameEmbed_of_straightCompatible
    cliffordX τx ux r vx hx]
  rw [two_halfShiftY_frameEmbed_of_straightCompatible
    cliffordY τy uy r vy hy]
  rw [two_halfShiftZ_frameEmbed_of_straightCompatible
    cliffordZ τz uz r vz hz]
  rw [two_halfShiftY_frameEmbed_of_straightCompatible
    cliffordY τy uy r vy hy]
  rw [two_halfShiftX_frameEmbed_of_straightCompatible
    cliffordX τx ux r vx hx]
  rw [two_halfLocal_frameEmbed D r]


/-! ## Exact transport of coarse plaquette holonomy -/

/-- Ordered product along two fine `x` half-edges. -/
def twoStepProductX {Site : Type u} (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site)) (p : FineSite3 Site) : Circle :=
  v (halfShiftX τ p) * v p

/-- Ordered product along two fine `y` half-edges. -/
def twoStepProductY {Site : Type u} (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site)) (p : FineSite3 Site) : Circle :=
  v (halfShiftY τ p) * v p

/-- Fine path consisting of two `x` half-edges followed by two `y` half-edges. -/
def finePathXXYY {Site : Type u} (τx τy : Site ≃ Site)
    (vx vy : Link (Site := FineSite3 Site)) (p : FineSite3 Site) : Circle :=
  twoStepProductY τy vy
      (Relativistic3DFullWalkRefinement.coarseLift τx p) *
    twoStepProductX τx vx p

/-- Fine path consisting of two `y` half-edges followed by two `x` half-edges. -/
def finePathYYXX {Site : Type u} (τx τy : Site ≃ Site)
    (vx vy : Link (Site := FineSite3 Site)) (p : FineSite3 Site) : Circle :=
  twoStepProductX τx vx
      (Relativistic3DFullWalkRefinement.coarseLift τy p) *
    twoStepProductY τy vy p

/-- The two-by-two fine Wilson-loop ratio. -/
def fineLargePlaquetteXY {Site : Type u} (τx τy : Site ≃ Site)
    (vx vy : Link (Site := FineSite3 Site)) (p : FineSite3 Site) : Circle :=
  finePathXXYY τx τy vx vy p / finePathYYXX τx τy vx vy p

/-- Canonical frame links transport the coarse `x`-then-`y` path exactly. -/
theorem finePathXXYY_frame {Site : Type u} (τx τy : Site ≃ Site)
    (ux uy : Link (Site := Site)) (r : PhaseFrame Site)
    (p : FineSite3 Site) :
    finePathXXYY τx τy (frameLinkX τx ux r) (frameLinkY τy uy r) p =
      r (Relativistic3DFullWalkRefinement.coarseLift τy
          (Relativistic3DFullWalkRefinement.coarseLift τx p)) *
        Relativistic3DGeometricEdgeRefinement.pathXY τx ux uy p.1 *
        (r p)⁻¹ := by
  unfold finePathXXYY twoStepProductX twoStepProductY
  rw [frameLinkY_two_step, frameLinkX_two_step]
  simp [Relativistic3DGeometricEdgeRefinement.pathXY,
    Relativistic3DFullWalkRefinement.coarseLift]
  group

/-- Canonical frame links transport the coarse `y`-then-`x` path exactly. -/
theorem finePathYYXX_frame {Site : Type u} (τx τy : Site ≃ Site)
    (ux uy : Link (Site := Site)) (r : PhaseFrame Site)
    (p : FineSite3 Site) :
    finePathYYXX τx τy (frameLinkX τx ux r) (frameLinkY τy uy r) p =
      r (Relativistic3DFullWalkRefinement.coarseLift τx
          (Relativistic3DFullWalkRefinement.coarseLift τy p)) *
        Relativistic3DGeometricEdgeRefinement.pathYX τy ux uy p.1 *
        (r p)⁻¹ := by
  unfold finePathYYXX twoStepProductX twoStepProductY
  rw [frameLinkX_two_step, frameLinkY_two_step]
  simp [Relativistic3DGeometricEdgeRefinement.pathYX,
    Relativistic3DFullWalkRefinement.coarseLift]
  group

/-- Commuting coarse translations have the same four-half-edge endpoint. -/
theorem coarseLift_comm {Site : Type u} (τx τy : Site ≃ Site)
    (hcomm : ∀ s, τy (τx s) = τx (τy s)) (p : FineSite3 Site) :
    Relativistic3DFullWalkRefinement.coarseLift τy
        (Relativistic3DFullWalkRefinement.coarseLift τx p) =
      Relativistic3DFullWalkRefinement.coarseLift τx
        (Relativistic3DFullWalkRefinement.coarseLift τy p) := by
  rcases p with ⟨s, v⟩
  simp [Relativistic3DFullWalkRefinement.coarseLift, hcomm s]

/-- Exact curvature transport: the large fine Wilson loop of the canonical
refinement is the original coarse plaquette.  Curvature is preserved, not
forced to vanish. -/
@[simp] theorem fineLargePlaquetteXY_frame {Site : Type u}
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site))
    (r : PhaseFrame Site)
    (hcomm : ∀ s, τy (τx s) = τx (τy s)) (p : FineSite3 Site) :
    fineLargePlaquetteXY τx τy
      (frameLinkX τx ux r) (frameLinkY τy uy r) p =
    Relativistic3DGeometricEdgeRefinement.plaquette τx τy ux uy p.1 := by
  unfold fineLargePlaquetteXY
  rw [finePathXXYY_frame, finePathYYXX_frame]
  rw [coarseLift_comm τx τy hcomm p]
  exact Relativistic3DGeometricEdgeRefinement.common_endpoint_ratio_cancel
    (r (Relativistic3DFullWalkRefinement.coarseLift τx
      (Relativistic3DFullWalkRefinement.coarseLift τy p)))
    (r p)
    (Relativistic3DGeometricEdgeRefinement.pathXY τx ux uy p.1)
    (Relativistic3DGeometricEdgeRefinement.pathYX τy ux uy p.1)

/-- Nontrivial coarse curvature survives exact canonical walk refinement. -/
theorem exact_refinement_can_preserve_nonflat_plaquette {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (r : PhaseFrame Site)
    (hcomm : ∀ s, τy (τx s) = τx (τy s))
    (p : FineSite3 Site)
    (hcurv : Relativistic3DGeometricEdgeRefinement.plaquette
      τx τy ux uy p.1 ≠ 1)
    (ψ : State (Site := Site)) :
    refinedSevenFactorWalk D τx τy τz ux uy uz r (frameEmbed r ψ) =
        frameEmbed r (sevenFactorWalk M τx τy τz ux uy uz ψ) ∧
      fineLargePlaquetteXY τx τy
        (frameLinkX τx ux r) (frameLinkY τy uy r) p ≠ 1 := by
  constructor
  · exact refinedSevenFactorWalk_frameEmbed D τx τy τz ux uy uz r ψ
  · simpa [fineLargePlaquetteXY_frame τx τy ux uy r hcomm p] using hcurv


/-! ## Exact arbitrary half-link mismatch energy -/

/-- An arbitrary ordered pair of half-links.  Its reconstructed coarse link is
`second * first`; no relation to a separately prescribed coarse link is assumed. -/
structure FineEdgePair (Site : Type u) where
  first : Link (Site := Site)
  second : Link (Site := Site)

namespace FineEdgePair

variable {Site : Type u}

/-- Coarse link actually reconstructed by the two supplied half-links. -/
def productLink (P : FineEdgePair Site) : Link (Site := Site) :=
  fun x => P.second x * P.first x

/-- Every arbitrary pair is an exact subdivision of its own product link. -/
def toSubdivision (P : FineEdgePair Site) :
    EdgeSubdivision P.productLink where
  first := P.first
  second := P.second
  reconstruct := by intro x; rfl

/-- Fine half-grid link assembled from the arbitrary pair. -/
def fineLink (P : FineEdgePair Site) : Link (Site := HalfSite Site) :=
  P.toSubdivision.fineLink

/-- Midpoint interpolation determined by the first half-link. -/
def embed (P : FineEdgePair Site) (ψ : State (Site := Site)) :
    State (Site := HalfSite Site) :=
  P.toSubdivision.embed ψ

@[simp] theorem fineLink_inl (P : FineEdgePair Site) (x : Site) :
    P.fineLink (Sum.inl x) = P.first x := rfl

@[simp] theorem fineLink_inr (P : FineEdgePair Site) (x : Site) :
    P.fineLink (Sum.inr x) = P.second x := rfl

@[simp] theorem embed_inl (P : FineEdgePair Site)
    (ψ : State (Site := Site)) (x : Site) :
    P.embed ψ (Sum.inl x) = ψ x := rfl

@[simp] theorem embed_inr (P : FineEdgePair Site)
    (ψ : State (Site := Site)) (x : Site) :
    P.embed ψ (Sum.inr x) = phaseMul (P.first x) (ψ x) := rfl

/-- Two arbitrary half steps exactly produce the Clifford shift associated to
their product link. -/
@[simp] theorem two_halfSteps_embed_product (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShift τ) P.fineLink
      (directionalShift A (halfShift τ) P.fineLink (P.embed ψ)) =
    P.embed (directionalShift A τ P.productLink ψ) := by
  exact P.toSubdivision.two_halfSteps_embed A τ ψ

/-- The midpoint interpolation is complex linear under subtraction. -/
@[simp] theorem embed_sub (P : FineEdgePair Site)
    (ψ φ : State (Site := Site)) :
    P.embed (ψ - φ) = P.embed ψ - P.embed φ := by
  funext y
  cases y <;> simp [embed, EdgeSubdivision.embed, phaseMul, smul_sub]

/-- Coarse directional defect caused by comparing the reconstructed product
link with a prescribed coarse link. -/
def coarseLinkDefect (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    State (Site := Site) :=
  directionalShift A τ P.productLink ψ - directionalShift A τ u ψ

/-- Fine adjacent-scale defect for the arbitrary half-link pair. -/
def fineIntertwiningDefect (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    State (Site := HalfSite Site) :=
  directionalShift A (halfShift τ) P.fineLink
      (directionalShift A (halfShift τ) P.fineLink (P.embed ψ)) -
    P.embed (directionalShift A τ u ψ)

/-- The complete fine defect is exactly the interpolation of the coarse link
mismatch defect. -/
@[simp] theorem fineIntertwiningDefect_eq_embed (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    P.fineIntertwiningDefect A τ u ψ = P.embed (P.coarseLinkDefect A τ u ψ) := by
  simp [fineIntertwiningDefect, coarseLinkDefect]

/-- The fine adjacent-scale defect vanishes exactly when the corresponding
coarse reconstructed-link defect vanishes.  The endpoint component makes the
interpolation injective. -/
@[simp] theorem fineIntertwiningDefect_eq_zero_iff (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    P.fineIntertwiningDefect A τ u ψ = 0 ↔
      P.coarseLinkDefect A τ u ψ = 0 := by
  rw [P.fineIntertwiningDefect_eq_embed]
  constructor
  · intro h
    funext x
    have hx := congrFun h (Sum.inl x)
    simpa using hx
  · intro h
    rw [h]
    funext y
    cases y <;> simp [FineEdgePair.embed, EdgeSubdivision.embed]

end FineEdgePair

/-- Complex squared amplitude of a phase difference. -/
def phaseErrorWeight (z w : Circle) : ℂ :=
  (starRingEnd ℂ) ((z : ℂ) - (w : ℂ)) * ((z : ℂ) - (w : ℂ))

/-- Difference between two link-coupled Clifford shifts, displayed as the sum
of its positive and negative projector-channel errors. -/
theorem directionalShift_sub_apply {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (ψ : State (Site := Site)) (x : Site) :
    (directionalShift A τ v ψ - directionalShift A τ u ψ) x =
      (((v (τ.symm x) : ℂ) - (u (τ.symm x) : ℂ)) •
        A.plus (ψ (τ.symm x))) +
      ((((v x)⁻¹ : Circle) : ℂ) - (((u x)⁻¹ : Circle) : ℂ)) •
        A.minus (ψ (τ x)) := by
  ext j
  simp [directionalShift, phaseMul]
  ring

/-- Exact pointwise Hilbert energy of an arbitrary link mismatch.  The two
Clifford channels remain orthogonal, so no cross term survives. -/
theorem directionalShift_sub_ip {Site : Type u}
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (ψ : State (Site := Site)) (x : Site) :
    ip ((directionalShift H.toClifford τ v ψ -
          directionalShift H.toClifford τ u ψ) x)
       ((directionalShift H.toClifford τ v ψ -
          directionalShift H.toClifford τ u ψ) x) =
      phaseErrorWeight (v (τ.symm x)) (u (τ.symm x)) *
        ip (H.toClifford.plus (ψ (τ.symm x)))
          (H.toClifford.plus (ψ (τ.symm x))) +
      phaseErrorWeight (v x)⁻¹ (u x)⁻¹ *
        ip (H.toClifford.minus (ψ (τ x)))
          (H.toClifford.minus (ψ (τ x))) := by
  rw [directionalShift_sub_apply]
  rw [ip_add_left, ip_add_right, ip_add_right]
  simp only [ip_smul_left, ip_smul_right,
    H.ip_plus_minus, H.ip_minus_plus]
  unfold phaseErrorWeight
  ring

/-- Exact global finite-volume mismatch energy. -/
theorem directionalShift_sub_stateIP {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (ψ : State (Site := Site)) :
    stateIP
      (directionalShift H.toClifford τ v ψ -
        directionalShift H.toClifford τ u ψ)
      (directionalShift H.toClifford τ v ψ -
        directionalShift H.toClifford τ u ψ) =
    ∑ x,
      (phaseErrorWeight (v (τ.symm x)) (u (τ.symm x)) *
        ip (H.toClifford.plus (ψ (τ.symm x)))
          (H.toClifford.plus (ψ (τ.symm x))) +
      phaseErrorWeight (v x)⁻¹ (u x)⁻¹ *
        ip (H.toClifford.minus (ψ (τ x)))
          (H.toClifford.minus (ψ (τ x)))) := by
  unfold stateIP
  apply Finset.sum_congr rfl
  intro x hx
  exact directionalShift_sub_ip H τ v u ψ x

/-- The half-cell Hilbert energy of the fine adjacent-scale defect equals the
coarse link-product mismatch energy exactly. -/
theorem FineEdgePair.fineIntertwiningDefect_halfCellIP {Site : Type u}
    [Fintype Site] (P : FineEdgePair Site)
    (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    halfCellIP (P.fineIntertwiningDefect H.toClifford τ u ψ)
      (P.fineIntertwiningDefect H.toClifford τ u ψ) =
    stateIP (P.coarseLinkDefect H.toClifford τ u ψ)
      (P.coarseLinkDefect H.toClifford τ u ψ) := by
  rw [P.fineIntertwiningDefect_eq_embed]
  exact embed_halfCellIP_isometry P.toSubdivision _ _

/-- Fully explicit adjacent-scale mismatch energy: only the discrepancy between
the ordered half-link product and the prescribed coarse link enters. -/
theorem FineEdgePair.fineIntertwiningDefect_energy {Site : Type u}
    [Fintype Site] (P : FineEdgePair Site)
    (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    halfCellIP (P.fineIntertwiningDefect H.toClifford τ u ψ)
      (P.fineIntertwiningDefect H.toClifford τ u ψ) =
    ∑ x,
      (phaseErrorWeight (P.productLink (τ.symm x)) (u (τ.symm x)) *
        ip (H.toClifford.plus (ψ (τ.symm x)))
          (H.toClifford.plus (ψ (τ.symm x))) +
      phaseErrorWeight (P.productLink x)⁻¹ (u x)⁻¹ *
        ip (H.toClifford.minus (ψ (τ x)))
          (H.toClifford.minus (ψ (τ x)))) := by
  rw [P.fineIntertwiningDefect_halfCellIP]
  unfold FineEdgePair.coarseLinkDefect
  exact directionalShift_sub_stateIP H τ P.productLink u ψ

/-- Exact straight-edge reconstruction makes the arbitrary-pair defect vanish. -/
@[simp] theorem FineEdgePair.fineIntertwiningDefect_eq_zero_of_product
    {Site : Type u} (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site))
    (h : P.productLink = u) (ψ : State (Site := Site)) :
    P.fineIntertwiningDefect A τ u ψ = 0 := by
  subst u
  simp [FineEdgePair.fineIntertwiningDefect]


/-! ## Separation counterexamples -/

/-- A quarter-turn unit-circle phase. -/
def quarterTurn : Circle :=
  ⟨Complex.I, by simp [Submonoid.unitSphere]⟩

@[simp] theorem quarterTurn_coe : (quarterTurn : ℂ) = Complex.I := rfl

@[simp] theorem quarterTurn_sq : quarterTurn * quarterTurn = -1 := by
  apply Circle.ext
  change Complex.I * Complex.I = (-1 : ℂ)
  exact Complex.I_mul_I

/-- Constant quarter-turn links have trivial plaquettes: every parallel
length-two path has the same phase `-1`. -/
def flatQuarterCube : CubeLinks where
  edgeX := fun _ _ => quarterTurn
  edgeY := fun _ _ => quarterTurn
  edgeZ := fun _ _ => quarterTurn

@[simp] theorem flatQuarterCube_flat : flatQuarterCube.Flat where
  xy := by
    intro z
    simp [CubeLinks.plaquetteXY, CubeLinks.pathXY,
      CubeLinks.pathYX, flatQuarterCube]
  xz := by
    intro y
    simp [CubeLinks.plaquetteXZ, CubeLinks.pathXZ,
      CubeLinks.pathZX, flatQuarterCube]
  yz := by
    intro x
    simp [CubeLinks.plaquetteYZ, CubeLinks.pathYZ,
      CubeLinks.pathZY, flatQuarterCube]

/-- The same quarter-turn on both half edges reconstructs `-1`. -/
def quarterPair (Site : Type) : FineEdgePair Site where
  first := fun _ => quarterTurn
  second := fun _ => quarterTurn

@[simp] theorem quarterPair_productLink {Site : Type} (x : Site) :
    (quarterPair Site).productLink x = -1 := by
  simp [quarterPair, FineEdgePair.productLink]

@[simp] theorem quarterPair_not_reconstruct_one {Site : Type}
    [Nonempty Site] :
    (quarterPair Site).productLink ≠ (fun _ => 1) := by
  intro h
  let x : Site := Classical.choice inferInstance
  have hx := congrFun h x
  have hc := congrArg (fun z : Circle => (z : ℂ)) hx
  norm_num at hc

/-- Flat plaquettes do not imply straight-edge reconstruction of a separately
prescribed coarse link. -/
theorem flat_curvature_does_not_force_edge_reconstruction :
    flatQuarterCube.Flat ∧
      (quarterPair PUnit).productLink ≠ (fun _ => 1) := by
  exact ⟨flatQuarterCube_flat, quarterPair_not_reconstruct_one⟩

/-- The flat quarter-turn mismatch acts nontrivially on the first Clifford
basis spinor. -/
theorem quarterPair_coarseDefect_nonzero :
    (quarterPair PUnit).coarseLinkDefect cliffordX (Equiv.refl PUnit)
      (fun _ => 1) (fun _ => basisSpinor0) ≠ 0 := by
  intro h
  have hs := congrFun h PUnit.unit
  have h0 := congrFun hs 0
  simp [FineEdgePair.coarseLinkDefect, directionalShift,
    quarterPair_productLink, phaseMul, cliffordX,
    CliffordInvolution.plus, CliffordInvolution.minus,
    alphaX, basisSpinor0] at h0
  norm_num at h0

/-- Consequently its two-half-step adjacent-scale defect is nonzero. -/
theorem quarterPair_fineDefect_nonzero :
    (quarterPair PUnit).fineIntertwiningDefect cliffordX (Equiv.refl PUnit)
      (fun _ => 1) (fun _ => basisSpinor0) ≠ 0 := by
  intro h
  apply quarterPair_coarseDefect_nonzero
  exact ((quarterPair PUnit).fineIntertwiningDefect_eq_zero_iff
    cliffordX (Equiv.refl PUnit) (fun _ => 1)
      (fun _ => basisSpinor0)).mp h

/-- Vanishing plaquette curvature alone cannot force arbitrary-link
intertwining, even for a concrete nonzero spinor. -/
theorem flat_curvature_with_nonzero_refinement_defect :
    flatQuarterCube.Flat ∧
      (quarterPair PUnit).fineIntertwiningDefect cliffordX (Equiv.refl PUnit)
        (fun _ => 1) (fun _ => basisSpinor0) ≠ 0 := by
  exact ⟨flatQuarterCube_flat, quarterPair_fineDefect_nonzero⟩

/-- Formal rejection of a universal curvature-only zero-defect rule. -/
theorem no_universal_flatness_implies_refinement :
    ¬ (∀ (L : CubeLinks), L.Flat →
      (quarterPair PUnit).fineIntertwiningDefect cliffordX (Equiv.refl PUnit)
        (fun _ => 1) (fun _ => basisSpinor0) = 0) := by
  intro h
  exact quarterPair_fineDefect_nonzero
    (h flatQuarterCube flatQuarterCube_flat)

end Relativistic3DEdgeCompatibility
end KomorebiPhysics
