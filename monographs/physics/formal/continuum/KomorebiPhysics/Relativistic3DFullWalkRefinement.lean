module

public import KomorebiPhysics.Relativistic3DCubicalRefinement
public import Mathlib.Analysis.Normed.Operator.Basic

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Full three-axis geometric refinement of the Clifford walk

This block introduces a globally glued half-grid `Site × {0,1}³`.  Each
coordinate half shift toggles its local half-cell bit and carries to the next
coarse site on the second half step.  A phase frame defines the canonical
cellwise-flat fine links.  Two fine directional Clifford shifts then exactly
intertwine with one coarse shift in every axis, and the complete
`M-X-Y-Z-Y-X-M` walk intertwines after every coarse factor is replaced by two
fine factors.

The second half of the file develops a general continuous-linear telescoping
calculus.  It isolates the full-walk refinement defect into transported local
factor defects and supplies an operator-norm bound.  Cubical phase defects are
then identified with the norm of `Omega - 1`.
-/

namespace KomorebiPhysics
namespace Relativistic3DFullWalkRefinement

open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DCubicalRefinement

universe u v

/-- Globally glued half-grid: the Boolean coordinate records the local
half-cell position, while a carry changes the coarse site. -/
abbrev FineSite3 (Site : Type u) := Site × CubeVertex

/-- Coarse translation lifted without changing the local half-cell address. -/
def coarseLift {Site : Type u} (τ : Site ≃ Site) :
    FineSite3 Site ≃ FineSite3 Site :=
  Equiv.prodCongr τ (Equiv.refl CubeVertex)

/-- Half translation in the `x` direction. -/
def halfShiftX {Site : Type u} (τ : Site ≃ Site) :
    FineSite3 Site ≃ FineSite3 Site where
  toFun p :=
    if p.2.x then
      (τ p.1, ⟨false, p.2.y, p.2.z⟩)
    else
      (p.1, ⟨true, p.2.y, p.2.z⟩)
  invFun p :=
    if p.2.x then
      (p.1, ⟨false, p.2.y, p.2.z⟩)
    else
      (τ.symm p.1, ⟨true, p.2.y, p.2.z⟩)
  left_inv := by
    rintro ⟨s, ⟨bx, cy, bz⟩⟩
    cases bx
    · simp
    · simp
  right_inv := by
    rintro ⟨s, ⟨bx, cy, bz⟩⟩
    cases bx
    · simp
    · simp

/-- Half translation in the `y` direction. -/
def halfShiftY {Site : Type u} (τ : Site ≃ Site) :
    FineSite3 Site ≃ FineSite3 Site where
  toFun p :=
    if p.2.y then
      (τ p.1, ⟨p.2.x, false, p.2.z⟩)
    else
      (p.1, ⟨p.2.x, true, p.2.z⟩)
  invFun p :=
    if p.2.y then
      (p.1, ⟨p.2.x, false, p.2.z⟩)
    else
      (τ.symm p.1, ⟨p.2.x, true, p.2.z⟩)
  left_inv := by
    rintro ⟨s, ⟨bx, cy, bz⟩⟩
    cases cy
    · simp
    · simp
  right_inv := by
    rintro ⟨s, ⟨bx, cy, bz⟩⟩
    cases cy
    · simp
    · simp

/-- Half translation in the `z` direction. -/
def halfShiftZ {Site : Type u} (τ : Site ≃ Site) :
    FineSite3 Site ≃ FineSite3 Site where
  toFun p :=
    if p.2.z then
      (τ p.1, ⟨p.2.x, p.2.y, false⟩)
    else
      (p.1, ⟨p.2.x, p.2.y, true⟩)
  invFun p :=
    if p.2.z then
      (p.1, ⟨p.2.x, p.2.y, false⟩)
    else
      (τ.symm p.1, ⟨p.2.x, p.2.y, true⟩)
  left_inv := by
    rintro ⟨s, ⟨bx, cy, bz⟩⟩
    cases bz
    · simp
    · simp
  right_inv := by
    rintro ⟨s, ⟨bx, cy, bz⟩⟩
    cases bz
    · simp
    · simp

@[simp] theorem halfShiftX_sq {Site : Type u} (τ : Site ≃ Site)
    (p : FineSite3 Site) :
    halfShiftX τ (halfShiftX τ p) = coarseLift τ p := by
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bx
  · rfl
  · rfl

@[simp] theorem halfShiftY_sq {Site : Type u} (τ : Site ≃ Site)
    (p : FineSite3 Site) :
    halfShiftY τ (halfShiftY τ p) = coarseLift τ p := by
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases cy
  · rfl
  · rfl

@[simp] theorem halfShiftZ_sq {Site : Type u} (τ : Site ≃ Site)
    (p : FineSite3 Site) :
    halfShiftZ τ (halfShiftZ τ p) = coarseLift τ p := by
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bz
  · rfl
  · rfl

/-- A local `U(1)` frame on the glued half-grid. -/
abbrev PhaseFrame (Site : Type u) := FineSite3 Site → Circle

/-- Covariant interpolation in a chosen phase frame. -/
def frameEmbed {Site : Type u} (r : PhaseFrame Site)
    (ψ : State (Site := Site)) : State (Site := FineSite3 Site) :=
  fun p => phaseMul (r p) (ψ p.1)

/-- A coarse link is inserted only on the carrying half step. -/
def carryPhaseX {Site : Type u} (u : Link (Site := Site))
    (p : FineSite3 Site) : Circle := if p.2.x then u p.1 else 1

def carryPhaseY {Site : Type u} (u : Link (Site := Site))
    (p : FineSite3 Site) : Circle := if p.2.y then u p.1 else 1

def carryPhaseZ {Site : Type u} (u : Link (Site := Site))
    (p : FineSite3 Site) : Circle := if p.2.z then u p.1 else 1

/-- Canonical cellwise-flat fine link in the `x` direction. -/
def frameLinkX {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site) :
    Link (Site := FineSite3 Site) := fun p =>
  r (halfShiftX τ p) * carryPhaseX u p * (r p)⁻¹

/-- Canonical cellwise-flat fine link in the `y` direction. -/
def frameLinkY {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site) :
    Link (Site := FineSite3 Site) := fun p =>
  r (halfShiftY τ p) * carryPhaseY u p * (r p)⁻¹

/-- Canonical cellwise-flat fine link in the `z` direction. -/
def frameLinkZ {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site) :
    Link (Site := FineSite3 Site) := fun p =>
  r (halfShiftZ τ p) * carryPhaseZ u p * (r p)⁻¹

/-- Two canonical `x` half links reconstruct the framed coarse link. -/
theorem frameLinkX_two_step {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site) (p : FineSite3 Site) :
    frameLinkX τ u r (halfShiftX τ p) * frameLinkX τ u r p =
      r (coarseLift τ p) * u p.1 * (r p)⁻¹ := by
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bx
  · simp [frameLinkX, carryPhaseX, halfShiftX, coarseLift]
  · simp [frameLinkX, carryPhaseX, halfShiftX, coarseLift]
    group

/-- Two canonical `y` half links reconstruct the framed coarse link. -/
theorem frameLinkY_two_step {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site) (p : FineSite3 Site) :
    frameLinkY τ u r (halfShiftY τ p) * frameLinkY τ u r p =
      r (coarseLift τ p) * u p.1 * (r p)⁻¹ := by
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases cy
  · simp [frameLinkY, carryPhaseY, halfShiftY, coarseLift]
  · simp [frameLinkY, carryPhaseY, halfShiftY, coarseLift]
    group

/-- Two canonical `z` half links reconstruct the framed coarse link. -/
theorem frameLinkZ_two_step {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site) (p : FineSite3 Site) :
    frameLinkZ τ u r (halfShiftZ τ p) * frameLinkZ τ u r p =
      r (coarseLift τ p) * u p.1 * (r p)⁻¹ := by
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bz
  · simp [frameLinkZ, carryPhaseZ, halfShiftZ, coarseLift]
  · simp [frameLinkZ, carryPhaseZ, halfShiftZ, coarseLift]
    group


/-- Two canonical fine `x` shifts exactly realize one coarse `x` shift on the
framed subspace. -/
@[simp] theorem two_halfShiftX_frameEmbed {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShiftX τ) (frameLinkX τ u r)
      (directionalShift A (halfShiftX τ) (frameLinkX τ u r)
        (frameEmbed r ψ)) =
    frameEmbed r (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bx
  · simp [directionalShift, frameEmbed, frameLinkX, carryPhaseX,
      halfShiftX, phaseMul_mul]
    congr 1
    group
  · simp [directionalShift, frameEmbed, frameLinkX, carryPhaseX,
      halfShiftX, phaseMul_mul]
    congr 1
    group


/-- Two canonical fine `y` shifts exactly realize one coarse `y` shift on the
framed subspace. -/
@[simp] theorem two_halfShiftY_frameEmbed {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShiftY τ) (frameLinkY τ u r)
      (directionalShift A (halfShiftY τ) (frameLinkY τ u r)
        (frameEmbed r ψ)) =
    frameEmbed r (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases cy
  · simp [directionalShift, frameEmbed, frameLinkY, carryPhaseY,
      halfShiftY, phaseMul_mul]
    congr 1
    group
  · simp [directionalShift, frameEmbed, frameLinkY, carryPhaseY,
      halfShiftY, phaseMul_mul]
    congr 1
    group

/-- Two canonical fine `z` shifts exactly realize one coarse `z` shift on the
framed subspace. -/
@[simp] theorem two_halfShiftZ_frameEmbed {Site : Type u}
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShiftZ τ) (frameLinkZ τ u r)
      (directionalShift A (halfShiftZ τ) (frameLinkZ τ u r)
        (frameEmbed r ψ)) =
    frameEmbed r (directionalShift A τ u ψ) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bz
  · simp [directionalShift, frameEmbed, frameLinkZ, carryPhaseZ,
      halfShiftZ, phaseMul_mul]
    congr 1
    group
  · simp [directionalShift, frameEmbed, frameLinkZ, carryPhaseZ,
      halfShiftZ, phaseMul_mul]
    congr 1
    group

/-- Local spin steps commute with the phase-frame embedding. -/
@[simp] theorem localStep_frameEmbed {Site : Type u} (M : LocalStep)
    (r : PhaseFrame Site) (ψ : State (Site := Site)) :
    M.apply (frameEmbed r ψ) = frameEmbed r (M.apply ψ) := by
  funext p
  exact M.phase_commutes _ _


/-- Two local half steps agree pointwise with their coarse local step. -/
@[simp] theorem two_halfLocal_apply {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (ψ : State (Site := Site)) :
    D.half.apply (D.half.apply ψ) = M.apply ψ := by
  funext x
  exact D.square (ψ x)

/-- Two local half steps reproduce the coarse local step under the common
three-dimensional frame embedding. -/
@[simp] theorem two_halfLocal_frameEmbed {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (r : PhaseFrame Site) (ψ : State (Site := Site)) :
    D.half.apply (D.half.apply (frameEmbed r ψ)) =
      frameEmbed r (M.apply ψ) := by
  rw [localStep_frameEmbed, localStep_frameEmbed]
  funext p
  change phaseMul (r p) (D.half.toFun (D.half.toFun (ψ p.1))) =
    phaseMul (r p) (M.toFun (ψ p.1))
  rw [D.square]

/-- The complete geometrically refined walk.  Every coarse factor is replaced
by two half-time or half-edge factors in the same palindromic order. -/
def refinedSevenFactorWalk {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (r : PhaseFrame Site)
    (Ψ : State (Site := FineSite3 Site)) : State (Site := FineSite3 Site) :=
  let M2 := fun Φ => D.half.apply (D.half.apply Φ)
  let X2 := fun Φ =>
    directionalShift cliffordX (halfShiftX τx) (frameLinkX τx ux r)
      (directionalShift cliffordX (halfShiftX τx) (frameLinkX τx ux r) Φ)
  let Y2 := fun Φ =>
    directionalShift cliffordY (halfShiftY τy) (frameLinkY τy uy r)
      (directionalShift cliffordY (halfShiftY τy) (frameLinkY τy uy r) Φ)
  let Z2 := fun Φ =>
    directionalShift cliffordZ (halfShiftZ τz) (frameLinkZ τz uz r)
      (directionalShift cliffordZ (halfShiftZ τz) (frameLinkZ τz uz r) Φ)
  M2 (X2 (Y2 (Z2 (Y2 (X2 (M2 Ψ))))))

/-- Exact full three-axis intertwining on the canonical cellwise-flat fine
connection. -/
@[simp] theorem refinedSevenFactorWalk_frameEmbed {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (r : PhaseFrame Site) (ψ : State (Site := Site)) :
    refinedSevenFactorWalk D τx τy τz ux uy uz r (frameEmbed r ψ) =
      frameEmbed r (sevenFactorWalk M τx τy τz ux uy uz ψ) := by
  simp [refinedSevenFactorWalk, sevenFactorWalk]




/-! ## Gauge covariance of the multiresolution frame -/

/-- Simultaneous coarse/fine gauge transformation of a refinement frame. -/
def gaugeFrame {Site : Type u} (r : PhaseFrame Site)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    PhaseFrame Site := fun p => G p * r p * (g p.1)⁻¹

/-- The frame embedding intertwines the coarse and fine site-gauge actions. -/
@[simp] theorem frameEmbed_gauge_covariant {Site : Type u}
    (r : PhaseFrame Site) (g : Gauge (Site := Site))
    (G : Gauge (Site := FineSite3 Site)) (ψ : State (Site := Site)) :
    frameEmbed (gaugeFrame r g G) (gaugeState g ψ) =
      gaugeState G (frameEmbed r ψ) := by
  funext p
  simp [frameEmbed, gaugeFrame, gaugeState, phaseMul_mul]

/-- Canonical `x` half-links transform as genuine fine-lattice links. -/
@[simp] theorem frameLinkX_gauge_covariant {Site : Type u}
    (τ : Site ≃ Site) (u : Link (Site := Site)) (r : PhaseFrame Site)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    frameLinkX τ (gaugeLink τ g u) (gaugeFrame r g G) =
      gaugeLink (halfShiftX τ) G (frameLinkX τ u r) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bx
  · simp [frameLinkX, carryPhaseX, halfShiftX, gaugeFrame, gaugeLink]
    group
  · simp [frameLinkX, carryPhaseX, halfShiftX, gaugeFrame, gaugeLink]
    group

/-- Canonical `y` half-links transform as genuine fine-lattice links. -/
@[simp] theorem frameLinkY_gauge_covariant {Site : Type u}
    (τ : Site ≃ Site) (u : Link (Site := Site)) (r : PhaseFrame Site)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    frameLinkY τ (gaugeLink τ g u) (gaugeFrame r g G) =
      gaugeLink (halfShiftY τ) G (frameLinkY τ u r) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases cy
  · simp [frameLinkY, carryPhaseY, halfShiftY, gaugeFrame, gaugeLink]
    group
  · simp [frameLinkY, carryPhaseY, halfShiftY, gaugeFrame, gaugeLink]
    group

/-- Canonical `z` half-links transform as genuine fine-lattice links. -/
@[simp] theorem frameLinkZ_gauge_covariant {Site : Type u}
    (τ : Site ≃ Site) (u : Link (Site := Site)) (r : PhaseFrame Site)
    (g : Gauge (Site := Site)) (G : Gauge (Site := FineSite3 Site)) :
    frameLinkZ τ (gaugeLink τ g u) (gaugeFrame r g G) =
      gaugeLink (halfShiftZ τ) G (frameLinkZ τ u r) := by
  funext p
  rcases p with ⟨s, ⟨bx, cy, bz⟩⟩
  cases bz
  · simp [frameLinkZ, carryPhaseZ, halfShiftZ, gaugeFrame, gaugeLink]
    group
  · simp [frameLinkZ, carryPhaseZ, halfShiftZ, gaugeFrame, gaugeLink]
    group


/-- The complete refined walk is covariant under simultaneous coarse and fine
gauge transformations of the frame and links. -/
theorem refinedSevenFactorWalk_gauge_covariant {Site : Type u}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (τx τy τz : Site ≃ Site) (ux uy uz : Link (Site := Site))
    (r : PhaseFrame Site) (g : Gauge (Site := Site))
    (G : Gauge (Site := FineSite3 Site))
    (Ψ : State (Site := FineSite3 Site)) :
    refinedSevenFactorWalk D τx τy τz
      (gaugeLink τx g ux) (gaugeLink τy g uy) (gaugeLink τz g uz)
      (gaugeFrame r g G) (gaugeState G Ψ) =
    gaugeState G (refinedSevenFactorWalk D τx τy τz ux uy uz r Ψ) := by
  simp only [refinedSevenFactorWalk, frameLinkX_gauge_covariant,
    frameLinkY_gauge_covariant, frameLinkZ_gauge_covariant]
  rw [D.half.apply_gauge, D.half.apply_gauge]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant, directionalShift_gauge_covariant]
  rw [D.half.apply_gauge, D.half.apply_gauge]

/-! ## One-eighth Hilbert normalization on the glued half-grid -/

/-- The child-cell Hilbert product, summed over a finite coarse lattice.  Each
of the eight local child vertices carries one eighth of the parent-cell
measure. -/
def fineGridIP {Site : Type u} [Fintype Site]
    (Ψ Φ : State (Site := FineSite3 Site)) : ℂ :=
  ∑ s, CubeLinks.cubeIP (fun v => Ψ (s, v)) (fun v => Φ (s, v))

/-- Arbitrary unit-circle phase frames give Hilbert-isometric interpolation
from the coarse lattice into the glued half-grid. -/
@[simp] theorem frameEmbed_fineGridIP_isometry {Site : Type u} [Fintype Site]
    (r : PhaseFrame Site) (ψ φ : State (Site := Site)) :
    fineGridIP (frameEmbed r ψ) (frameEmbed r φ) = stateIP ψ φ := by
  simp [fineGridIP, CubeLinks.cubeIP, frameEmbed, stateIP]
  ring_nf


/-! ## The canonical fine connection is flat inside every child cube -/

/-- Internal half-edge links induced by a frame in one coarse cell. -/
def frameCubeLinks {Site : Type u} (r : PhaseFrame Site) (s : Site) : CubeLinks where
  edgeX := fun cy bz =>
    r (s, ⟨true, cy, bz⟩) * (r (s, ⟨false, cy, bz⟩))⁻¹
  edgeY := fun bx bz =>
    r (s, ⟨bx, true, bz⟩) * (r (s, ⟨bx, false, bz⟩))⁻¹
  edgeZ := fun bx cy =>
    r (s, ⟨bx, cy, true⟩) * (r (s, ⟨bx, cy, false⟩))⁻¹

/-- The internal `x` links of the global construction are exactly the
frame-generated cube links. -/
@[simp] theorem frameLinkX_internal {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (s : Site) (cy bz : Bool) :
    frameLinkX τ u r (s, ⟨false, cy, bz⟩) =
      (frameCubeLinks r s).edgeX cy bz := by
  simp [frameLinkX, carryPhaseX, halfShiftX, frameCubeLinks]

@[simp] theorem frameLinkY_internal {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (s : Site) (bx bz : Bool) :
    frameLinkY τ u r (s, ⟨bx, false, bz⟩) =
      (frameCubeLinks r s).edgeY bx bz := by
  simp [frameLinkY, carryPhaseY, halfShiftY, frameCubeLinks]

@[simp] theorem frameLinkZ_internal {Site : Type u} (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (s : Site) (bx cy : Bool) :
    frameLinkZ τ u r (s, ⟨bx, cy, false⟩) =
      (frameCubeLinks r s).edgeZ bx cy := by
  simp [frameLinkZ, carryPhaseZ, halfShiftZ, frameCubeLinks]

/-- Every canonical child cube has trivial face holonomy. -/
theorem frameCubeLinks_flat {Site : Type u} (r : PhaseFrame Site) (s : Site) :
    (frameCubeLinks r s).Flat where
  xy := by
    intro z
    simp [CubeLinks.plaquetteXY, CubeLinks.pathXY, CubeLinks.pathYX,
      frameCubeLinks]
  xz := by
    intro y
    simp [CubeLinks.plaquetteXZ, CubeLinks.pathXZ, CubeLinks.pathZX,
      frameCubeLinks]
  yz := by
    intro x
    simp [CubeLinks.plaquetteYZ, CubeLinks.pathYZ, CubeLinks.pathZY,
      frameCubeLinks]

/-- Consequently all six internal corner paths agree in every canonical child
cube. -/
theorem frameCubeLinks_all_corner_paths {Site : Type u}
    (r : PhaseFrame Site) (s : Site) :
    let L := frameCubeLinks r s
    L.pathXYZ = L.pathXZY ∧
    L.pathXYZ = L.pathYXZ ∧
    L.pathXYZ = L.pathYZX ∧
    L.pathXYZ = L.pathZXY ∧
    L.pathXYZ = L.pathZYX := by
  exact CubeLinks.Flat.all_corner_paths _ (frameCubeLinks_flat r s)



/-! ## Abstract telescoping calculus for curved refinement defects -/

section OperatorDefect

variable {X : Type u} {Y : Type v}
variable [NormedAddCommGroup X] [NormedSpace ℂ X]
variable [NormedAddCommGroup Y] [NormedSpace ℂ Y]

/-- Failure of one fine factor to intertwine with one coarse factor. -/
def intertwiningDefectOp (F : Y →L[ℂ] Y) (I : X →L[ℂ] Y)
    (C : X →L[ℂ] X) : X →L[ℂ] Y :=
  F.comp I - I.comp C

/-- Exact two-factor telescoping identity. -/
theorem intertwiningDefectOp_comp
    (F₁ F₂ : Y →L[ℂ] Y) (I : X →L[ℂ] Y)
    (C₁ C₂ : X →L[ℂ] X) :
    intertwiningDefectOp (F₂.comp F₁) I (C₂.comp C₁) =
      F₂.comp (intertwiningDefectOp F₁ I C₁) +
        (intertwiningDefectOp F₂ I C₂).comp C₁ := by
  ext x
  simp [intertwiningDefectOp]

/-- Operator-norm version of the two-factor telescoping identity. -/
theorem norm_intertwiningDefectOp_comp_le
    (F₁ F₂ : Y →L[ℂ] Y) (I : X →L[ℂ] Y)
    (C₁ C₂ : X →L[ℂ] X) :
    ‖intertwiningDefectOp (F₂.comp F₁) I (C₂.comp C₁)‖ ≤
      ‖F₂‖ * ‖intertwiningDefectOp F₁ I C₁‖ +
        ‖intertwiningDefectOp F₂ I C₂‖ * ‖C₁‖ := by
  rw [intertwiningDefectOp_comp]
  calc
    ‖F₂.comp (intertwiningDefectOp F₁ I C₁) +
        (intertwiningDefectOp F₂ I C₂).comp C₁‖
        ≤ ‖F₂.comp (intertwiningDefectOp F₁ I C₁)‖ +
          ‖(intertwiningDefectOp F₂ I C₂).comp C₁‖ := norm_add_le _ _
    _ ≤ ‖F₂‖ * ‖intertwiningDefectOp F₁ I C₁‖ +
          ‖intertwiningDefectOp F₂ I C₂‖ * ‖C₁‖ :=
      add_le_add (ContinuousLinearMap.opNorm_comp_le _ _)
        (ContinuousLinearMap.opNorm_comp_le _ _)

/-- Composition in execution order: the head factor acts first. -/
def composeOps {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E] :
    List (E →L[ℂ] E) → E →L[ℂ] E
  | [] => ContinuousLinearMap.id ℂ E
  | F :: Fs => (composeOps Fs).comp F

@[simp] theorem composeOps_nil {E : Type*}
    [NormedAddCommGroup E] [NormedSpace ℂ E] :
    composeOps ([] : List (E →L[ℂ] E)) = ContinuousLinearMap.id ℂ E := rfl

@[simp] theorem composeOps_cons {E : Type*}
    [NormedAddCommGroup E] [NormedSpace ℂ E]
    (F : E →L[ℂ] E) (Fs : List (E →L[ℂ] E)) :
    composeOps (F :: Fs) = (composeOps Fs).comp F := rfl

/-- A composition of contractions is a contraction. -/
theorem norm_composeOps_le_one {E : Type*}
    [NormedAddCommGroup E] [NormedSpace ℂ E]
    (Fs : List (E →L[ℂ] E))
    (h : ∀ F ∈ Fs, ‖F‖ ≤ 1) : ‖composeOps Fs‖ ≤ 1 := by
  induction Fs with
  | nil =>
      simpa [composeOps] using (ContinuousLinearMap.norm_id_le (𝕜 := ℂ) (E := E))
  | cons F Fs ih =>
      have hF : ‖F‖ ≤ 1 := h F (by simp)
      have hFs : ∀ G ∈ Fs, ‖G‖ ≤ 1 := by
        intro G hG
        exact h G (by simp [hG])
      calc
        ‖composeOps (F :: Fs)‖ = ‖(composeOps Fs).comp F‖ := rfl
        _ ≤ ‖composeOps Fs‖ * ‖F‖ := ContinuousLinearMap.opNorm_comp_le _ _
        _ ≤ 1 * 1 := mul_le_mul (ih hFs) hF (norm_nonneg _) (by norm_num)
        _ = 1 := by norm_num

/-- Fine-factor projection from a list of fine/coarse pairs. -/
def fineComposite
    (pairs : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) : Y →L[ℂ] Y :=
  composeOps (pairs.map Prod.fst)

/-- Coarse-factor projection from a list of fine/coarse pairs. -/
def coarseComposite
    (pairs : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) : X →L[ℂ] X :=
  composeOps (pairs.map Prod.snd)

/-- Sum of the local adjacent-scale operator defects. -/
def defectBudget (I : X →L[ℂ] Y)
    (pairs : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) : ℝ :=
  (pairs.map fun p => ‖intertwiningDefectOp p.1 I p.2‖).sum

@[simp] theorem fineComposite_nil :
    fineComposite ([] : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) =
      ContinuousLinearMap.id ℂ Y := rfl

@[simp] theorem coarseComposite_nil :
    coarseComposite ([] : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) =
      ContinuousLinearMap.id ℂ X := rfl

@[simp] theorem defectBudget_nil (I : X →L[ℂ] Y) :
    defectBudget I [] = 0 := rfl

@[simp] theorem fineComposite_cons
    (p : (Y →L[ℂ] Y) × (X →L[ℂ] X))
    (ps : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) :
    fineComposite (p :: ps) = (fineComposite ps).comp p.1 := rfl

@[simp] theorem coarseComposite_cons
    (p : (Y →L[ℂ] Y) × (X →L[ℂ] X))
    (ps : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) :
    coarseComposite (p :: ps) = (coarseComposite ps).comp p.2 := rfl

@[simp] theorem defectBudget_cons (I : X →L[ℂ] Y)
    (p : (Y →L[ℂ] Y) × (X →L[ℂ] X))
    (ps : List ((Y →L[ℂ] Y) × (X →L[ℂ] X))) :
    defectBudget I (p :: ps) =
      ‖intertwiningDefectOp p.1 I p.2‖ + defectBudget I ps := rfl

/-- Full finite-product curvature estimate: for contractive factors, the
operator norm of the complete refinement defect is at most the sum of the
local factor defects. -/
theorem norm_fullDefect_le_budget
    (I : X →L[ℂ] Y)
    (pairs : List ((Y →L[ℂ] Y) × (X →L[ℂ] X)))
    (hFine : ∀ p ∈ pairs, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ pairs, ‖p.2‖ ≤ 1) :
    ‖intertwiningDefectOp (fineComposite pairs) I (coarseComposite pairs)‖ ≤
      defectBudget I pairs := by
  induction pairs with
  | nil =>
      simp [intertwiningDefectOp]
  | cons p ps ih =>
      have hFineHead : ‖p.1‖ ≤ 1 := hFine p (by simp)
      have hCoarseHead : ‖p.2‖ ≤ 1 := hCoarse p (by simp)
      have hFineTail : ∀ q ∈ ps, ‖q.1‖ ≤ 1 := by
        intro q hq
        exact hFine q (by simp [hq])
      have hCoarseTail : ∀ q ∈ ps, ‖q.2‖ ≤ 1 := by
        intro q hq
        exact hCoarse q (by simp [hq])
      have hFineComp : ‖fineComposite ps‖ ≤ 1 := by
        exact norm_composeOps_le_one (ps.map Prod.fst) (by
          intro F hF
          rcases List.mem_map.mp hF with ⟨q, hq, rfl⟩
          exact hFineTail q hq)
      have hTail := ih hFineTail hCoarseTail
      have hBudgetNonneg : 0 ≤ defectBudget I ps := by
        unfold defectBudget
        exact List.sum_nonneg (by
          intro (x : ℝ) hx
          rcases List.mem_map.mp hx with ⟨q, hq, rfl⟩
          exact norm_nonneg _)
      calc
        ‖intertwiningDefectOp (fineComposite (p :: ps)) I
            (coarseComposite (p :: ps))‖
            ≤ ‖fineComposite ps‖ * ‖intertwiningDefectOp p.1 I p.2‖ +
              ‖intertwiningDefectOp (fineComposite ps) I
                (coarseComposite ps)‖ * ‖p.2‖ := by
              simpa using norm_intertwiningDefectOp_comp_le
                p.1 (fineComposite ps) I p.2 (coarseComposite ps)
        _ ≤ 1 * ‖intertwiningDefectOp p.1 I p.2‖ +
              defectBudget I ps * 1 := by
              gcongr
        _ = defectBudget I (p :: ps) := by simp

/-- Vanishing local defects imply exact intertwining of the complete product. -/
theorem fullDefect_eq_zero_of_local
    (I : X →L[ℂ] Y)
    (pairs : List ((Y →L[ℂ] Y) × (X →L[ℂ] X)))
    (h : ∀ p ∈ pairs, intertwiningDefectOp p.1 I p.2 = 0) :
    intertwiningDefectOp (fineComposite pairs) I (coarseComposite pairs) = 0 := by
  induction pairs with
  | nil => simp [intertwiningDefectOp]
  | cons p ps ih =>
      rw [fineComposite_cons, coarseComposite_cons, intertwiningDefectOp_comp]
      rw [h p (by simp), ih (by
        intro q hq
        exact h q (by simp [hq]))]
      simp



/-! ### Seven-factor specialization -/

/-- Ordered fine/coarse factor pairs for a seven-factor walk. -/
def sevenFactorPairs
    (m₀ x₀ y₀ z y₁ x₁ m₁ : (Y →L[ℂ] Y) × (X →L[ℂ] X)) :
    List ((Y →L[ℂ] Y) × (X →L[ℂ] X)) :=
  [m₀, x₀, y₀, z, y₁, x₁, m₁]

/-- Explicit seven-factor defect bound. -/
theorem norm_sevenFactorDefect_le
    (I : X →L[ℂ] Y)
    (m₀ x₀ y₀ z y₁ x₁ m₁ : (Y →L[ℂ] Y) × (X →L[ℂ] X))
    (hFine : ∀ p ∈ sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁, ‖p.2‖ ≤ 1) :
    ‖intertwiningDefectOp
        (fineComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁)) I
        (coarseComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁))‖ ≤
      ‖intertwiningDefectOp m₀.1 I m₀.2‖ +
      ‖intertwiningDefectOp x₀.1 I x₀.2‖ +
      ‖intertwiningDefectOp y₀.1 I y₀.2‖ +
      ‖intertwiningDefectOp z.1 I z.2‖ +
      ‖intertwiningDefectOp y₁.1 I y₁.2‖ +
      ‖intertwiningDefectOp x₁.1 I x₁.2‖ +
      ‖intertwiningDefectOp m₁.1 I m₁.2‖ := by
  simpa [sevenFactorPairs, defectBudget, add_assoc] using
    norm_fullDefect_le_budget I
      (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁) hFine hCoarse

/-- If the two mass factors intertwine exactly, the full seven-factor defect is
controlled by the five spatial defects. -/
theorem norm_sevenFactorDefect_le_five
    (I : X →L[ℂ] Y)
    (m₀ x₀ y₀ z y₁ x₁ m₁ : (Y →L[ℂ] Y) × (X →L[ℂ] X))
    (hFine : ∀ p ∈ sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁, ‖p.2‖ ≤ 1)
    (hm₀ : intertwiningDefectOp m₀.1 I m₀.2 = 0)
    (hm₁ : intertwiningDefectOp m₁.1 I m₁.2 = 0) :
    ‖intertwiningDefectOp
        (fineComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁)) I
        (coarseComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁))‖ ≤
      ‖intertwiningDefectOp x₀.1 I x₀.2‖ +
      ‖intertwiningDefectOp y₀.1 I y₀.2‖ +
      ‖intertwiningDefectOp z.1 I z.2‖ +
      ‖intertwiningDefectOp y₁.1 I y₁.2‖ +
      ‖intertwiningDefectOp x₁.1 I x₁.2‖ := by
  have h := norm_sevenFactorDefect_le I m₀ x₀ y₀ z y₁ x₁ m₁ hFine hCoarse
  rw [hm₀, hm₁] at h
  simpa using h

/-- Conditional curvature budget for the complete seven-factor composition. -/
theorem norm_sevenFactorDefect_le_curvatureBudget
    (I : X →L[ℂ] Y)
    (m₀ x₀ y₀ z y₁ x₁ m₁ : (Y →L[ℂ] Y) × (X →L[ℂ] X))
    (κx₀ κy₀ κz κy₁ κx₁ : ℝ)
    (hFine : ∀ p ∈ sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁, ‖p.2‖ ≤ 1)
    (hm₀ : intertwiningDefectOp m₀.1 I m₀.2 = 0)
    (hm₁ : intertwiningDefectOp m₁.1 I m₁.2 = 0)
    (hx₀ : ‖intertwiningDefectOp x₀.1 I x₀.2‖ ≤ κx₀)
    (hy₀ : ‖intertwiningDefectOp y₀.1 I y₀.2‖ ≤ κy₀)
    (hz : ‖intertwiningDefectOp z.1 I z.2‖ ≤ κz)
    (hy₁ : ‖intertwiningDefectOp y₁.1 I y₁.2‖ ≤ κy₁)
    (hx₁ : ‖intertwiningDefectOp x₁.1 I x₁.2‖ ≤ κx₁) :
    ‖intertwiningDefectOp
        (fineComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁)) I
        (coarseComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁))‖ ≤
      κx₀ + κy₀ + κz + κy₁ + κx₁ := by
  calc
    ‖intertwiningDefectOp
        (fineComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁)) I
        (coarseComposite (sevenFactorPairs m₀ x₀ y₀ z y₁ x₁ m₁))‖
      ≤ ‖intertwiningDefectOp x₀.1 I x₀.2‖ +
        ‖intertwiningDefectOp y₀.1 I y₀.2‖ +
        ‖intertwiningDefectOp z.1 I z.2‖ +
        ‖intertwiningDefectOp y₁.1 I y₁.2‖ +
        ‖intertwiningDefectOp x₁.1 I x₁.2‖ :=
          norm_sevenFactorDefect_le_five I m₀ x₀ y₀ z y₁ x₁ m₁
            hFine hCoarse hm₀ hm₁
    _ ≤ κx₀ + κy₀ + κz + κy₁ + κx₁ := by gcongr


/-! ### Exact cubical phase-defect operator norms -/

/-- Unit-circle phase transport as a continuous linear operator on spinors. -/
def phaseOp (z : Circle) : Spinor →L[ℂ] Spinor :=
  (z : ℂ) • ContinuousLinearMap.id ℂ Spinor

@[simp] theorem phaseOp_apply (z : Circle) (ψ : Spinor) :
    phaseOp z ψ = phaseMul z ψ := by
  rfl

/-- Every unit-circle phase operator has operator norm one. -/
@[simp] theorem norm_phaseOp (z : Circle) : ‖phaseOp z‖ = 1 := by
  rw [phaseOp, norm_smul, ContinuousLinearMap.norm_id, Circle.norm_coe]
  norm_num

/-- Operator difference between two parallel-transport paths. -/
def phaseDefectOp (p q : Circle) : Spinor →L[ℂ] Spinor :=
  phaseOp p - phaseOp q

/-- With the identity embedding, the adjacent-scale phase defect is exactly the
path-defect operator. -/
@[simp] theorem intertwiningDefectOp_phase_id (p q : Circle) :
    intertwiningDefectOp (phaseOp p) (ContinuousLinearMap.id ℂ Spinor)
      (phaseOp q) = phaseDefectOp p q := by
  ext ψ j
  simp [intertwiningDefectOp, phaseDefectOp, phaseOp]

/-- The operator defect is scalar multiplication by the path-phase difference. -/
theorem phaseDefectOp_eq_smul_id (p q : Circle) :
    phaseDefectOp p q =
      (((p : ℂ) - (q : ℂ)) : ℂ) • ContinuousLinearMap.id ℂ Spinor := by
  ext ψ j
  simp [phaseDefectOp, phaseOp]
  ring

/-- If `p = Omega q`, curvature factors the complete path operator defect. -/
theorem phaseDefectOp_eq_curvature
    (p q Ω : Circle) (h : p = Ω * q) :
    phaseDefectOp p q =
      ((q : ℂ) * ((Ω : ℂ) - 1)) • ContinuousLinearMap.id ℂ Spinor := by
  subst p
  ext ψ j
  simp [phaseDefectOp, phaseOp]
  ring

/-- Exact operator norm of a curvature-controlled path defect. -/
theorem norm_phaseDefectOp_eq_curvature
    (p q Ω : Circle) (h : p = Ω * q) :
    ‖phaseDefectOp p q‖ = ‖(Ω : ℂ) - 1‖ := by
  rw [phaseDefectOp_eq_curvature p q Ω h]
  rw [norm_smul, ContinuousLinearMap.norm_id]
  rw [norm_mul, Circle.norm_coe, one_mul, mul_one]

@[simp] theorem norm_defect_XYZ_YXZ (L : CubeLinks) :
    ‖phaseDefectOp L.pathXYZ L.pathYXZ‖ =
      ‖(L.plaquetteXY false : ℂ) - 1‖ := by
  exact norm_phaseDefectOp_eq_curvature _ _ _ L.pathXYZ_eq_xy0_mul_pathYXZ

@[simp] theorem norm_defect_XYZ_XZY (L : CubeLinks) :
    ‖phaseDefectOp L.pathXYZ L.pathXZY‖ =
      ‖(L.plaquetteYZ true : ℂ) - 1‖ := by
  exact norm_phaseDefectOp_eq_curvature _ _ _ L.pathXYZ_eq_yz1_mul_pathXZY

@[simp] theorem norm_defect_XZY_ZXY (L : CubeLinks) :
    ‖phaseDefectOp L.pathXZY L.pathZXY‖ =
      ‖(L.plaquetteXZ false : ℂ) - 1‖ := by
  exact norm_phaseDefectOp_eq_curvature _ _ _ L.pathXZY_eq_xz0_mul_pathZXY

@[simp] theorem norm_defect_YXZ_YZX (L : CubeLinks) :
    ‖phaseDefectOp L.pathYXZ L.pathYZX‖ =
      ‖(L.plaquetteXZ true : ℂ) - 1‖ := by
  exact norm_phaseDefectOp_eq_curvature _ _ _ L.pathYXZ_eq_xz1_mul_pathYZX

@[simp] theorem norm_defect_YZX_ZYX (L : CubeLinks) :
    ‖phaseDefectOp L.pathYZX L.pathZYX‖ =
      ‖(L.plaquetteYZ false : ℂ) - 1‖ := by
  exact norm_phaseDefectOp_eq_curvature _ _ _ L.pathYZX_eq_yz0_mul_pathZYX

@[simp] theorem norm_defect_ZXY_ZYX (L : CubeLinks) :
    ‖phaseDefectOp L.pathZXY L.pathZYX‖ =
      ‖(L.plaquetteXY true : ℂ) - 1‖ := by
  exact norm_phaseDefectOp_eq_curvature _ _ _ L.pathZXY_eq_xy1_mul_pathZYX


/-- Seven factor pairs built from five adjacent corner-path swaps.  These five
faces form a convenient independent cubical curvature budget; the sixth face
is constrained by the cubical Bianchi identity. -/
def cubeSwapSevenPairs (L : CubeLinks) :
    List ((Spinor →L[ℂ] Spinor) × (Spinor →L[ℂ] Spinor)) :=
  sevenFactorPairs
    (ContinuousLinearMap.id ℂ Spinor, ContinuousLinearMap.id ℂ Spinor)
    (phaseOp L.pathXYZ, phaseOp L.pathYXZ)
    (phaseOp L.pathYXZ, phaseOp L.pathYZX)
    (phaseOp L.pathYZX, phaseOp L.pathZYX)
    (phaseOp L.pathXYZ, phaseOp L.pathXZY)
    (phaseOp L.pathXZY, phaseOp L.pathZXY)
    (ContinuousLinearMap.id ℂ Spinor, ContinuousLinearMap.id ℂ Spinor)

/-- A concrete seven-factor phase-transport composition is bounded by the sum
of five independent face-curvature amplitudes. -/
theorem norm_cubeSwapSevenDefect_le_curvatureBudget (L : CubeLinks) :
    ‖intertwiningDefectOp
        (fineComposite (cubeSwapSevenPairs L))
        (ContinuousLinearMap.id ℂ Spinor)
        (coarseComposite (cubeSwapSevenPairs L))‖ ≤
      ‖(L.plaquetteXY false : ℂ) - 1‖ +
      ‖(L.plaquetteXZ true : ℂ) - 1‖ +
      ‖(L.plaquetteYZ false : ℂ) - 1‖ +
      ‖(L.plaquetteYZ true : ℂ) - 1‖ +
      ‖(L.plaquetteXZ false : ℂ) - 1‖ := by
  have hFine : ∀ p ∈ cubeSwapSevenPairs L, ‖p.1‖ ≤ 1 := by
    simp [cubeSwapSevenPairs, sevenFactorPairs]
  have hCoarse : ∀ p ∈ cubeSwapSevenPairs L, ‖p.2‖ ≤ 1 := by
    simp [cubeSwapSevenPairs, sevenFactorPairs]
  have h := norm_fullDefect_le_budget
    (ContinuousLinearMap.id ℂ Spinor) (cubeSwapSevenPairs L) hFine hCoarse
  calc
    ‖intertwiningDefectOp
        (fineComposite (cubeSwapSevenPairs L))
        (ContinuousLinearMap.id ℂ Spinor)
        (coarseComposite (cubeSwapSevenPairs L))‖ ≤
      ‖phaseDefectOp L.pathXYZ L.pathYXZ‖ +
      ‖phaseDefectOp L.pathYXZ L.pathYZX‖ +
      ‖phaseDefectOp L.pathYZX L.pathZYX‖ +
      ‖phaseDefectOp L.pathXYZ L.pathXZY‖ +
      ‖phaseDefectOp L.pathXZY L.pathZXY‖ := by
        simpa [cubeSwapSevenPairs, sevenFactorPairs, defectBudget,
          intertwiningDefectOp, phaseDefectOp, add_assoc] using h
    _ = ‖(L.plaquetteXY false : ℂ) - 1‖ +
      ‖(L.plaquetteXZ true : ℂ) - 1‖ +
      ‖(L.plaquetteYZ false : ℂ) - 1‖ +
      ‖(L.plaquetteYZ true : ℂ) - 1‖ +
      ‖(L.plaquetteXZ false : ℂ) - 1‖ := by
        rw [norm_defect_XYZ_YXZ, norm_defect_YXZ_YZX,
          norm_defect_YZX_ZYX, norm_defect_XYZ_XZY,
          norm_defect_XZY_ZXY]

/-- In the flat sector the concrete seven-factor phase-transport defect
vanishes exactly. -/
theorem cubeSwapSevenDefect_eq_zero_of_flat (L : CubeLinks) (h : L.Flat) :
    intertwiningDefectOp
        (fineComposite (cubeSwapSevenPairs L))
        (ContinuousLinearMap.id ℂ Spinor)
        (coarseComposite (cubeSwapSevenPairs L)) = 0 := by
  rcases CubeLinks.Flat.all_corner_paths L h with
    ⟨hXZY, hYXZ, hYZX, hZXY, hZYX⟩
  apply fullDefect_eq_zero_of_local
  intro p hp
  simp [cubeSwapSevenPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · simp [intertwiningDefectOp]
  · rw [intertwiningDefectOp_phase_id]
    simp [phaseDefectOp, hYXZ]
  · rw [intertwiningDefectOp_phase_id]
    simp [phaseDefectOp, hYXZ.symm.trans hYZX]
  · rw [intertwiningDefectOp_phase_id]
    simp [phaseDefectOp, hYZX.symm.trans hZYX]
  · rw [intertwiningDefectOp_phase_id]
    simp [phaseDefectOp, hXZY]
  · rw [intertwiningDefectOp_phase_id]
    simp [phaseDefectOp, hXZY.symm.trans hZXY]
  · simp [intertwiningDefectOp]

/-- The explicit nonflat cube has a lower-`xy` phase-defect operator of norm
exactly two. -/
@[simp] theorem norm_nonflatCube_lowerXY_phaseDefect :
    ‖phaseDefectOp nonflatCube.pathXYZ nonflatCube.pathYXZ‖ = 2 := by
  rw [norm_defect_XYZ_YXZ]
  simp [nonflatCube_xy0]
  norm_num

/-- Flat plaquettes give zero path-defect operators. -/
theorem phaseDefectOp_eq_zero_of_flat (L : CubeLinks) (h : L.Flat) :
    phaseDefectOp L.pathXYZ L.pathYXZ = 0 ∧
    phaseDefectOp L.pathXYZ L.pathXZY = 0 ∧
    phaseDefectOp L.pathXZY L.pathZXY = 0 ∧
    phaseDefectOp L.pathYXZ L.pathYZX = 0 ∧
    phaseDefectOp L.pathYZX L.pathZYX = 0 ∧
    phaseDefectOp L.pathZXY L.pathZYX = 0 := by
  rcases CubeLinks.Flat.all_corner_paths L h with
    ⟨hXZY, hYXZ, hYZX, hZXY, hZYX⟩
  constructor
  · simp [phaseDefectOp, hYXZ]
  constructor
  · simp [phaseDefectOp, hXZY]
  constructor
  · simp [phaseDefectOp, hXZY.symm.trans hZXY]
  constructor
  · simp [phaseDefectOp, hYXZ.symm.trans hYZX]
  constructor
  · simp [phaseDefectOp, hYZX.symm.trans hZYX]
  · simp [phaseDefectOp, hZXY.symm.trans hZYX]


end OperatorDefect


end Relativistic3DFullWalkRefinement
end KomorebiPhysics
