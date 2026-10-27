module

public import KomorebiPhysics.Relativistic3DGeometricEdgeRefinement
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.Group
public import Mathlib.Tactic.Ring

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Three-dimensional cubical refinement and curvature-controlled corner defects

This module replaces the one-edge geometry of Block 26 by an explicit cubical
cell with eight vertices and twelve oriented `U(1)` edges.  A reference-path
interpolation transports a coarse four-spinor from the origin to every child
vertex.  The interpolation is gauge covariant and Hilbert isometric after the
one-eighth cell measure is included.

The six paths from the origin to the opposite corner are compared exactly.
Adjacent path permutations differ by the corresponding face plaquette.  Hence
all six transports agree in the flat sector.  In the nonflat sector the spinor
defect is exactly a unitary transport of `(Omega - 1) * psi`, and its Hilbert
weight is exactly the curvature amplitude squared times the input weight.

This is a local cubical theorem.  It does not yet compare the complete coarse
and fine seven-factor walks or prove continuum convergence.
-/

namespace KomorebiPhysics
namespace Relativistic3DCubicalRefinement

open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DGeometricEdgeRefinement

universe u

/-- A vertex of the refined `2 x 2 x 2` child cell. -/
structure CubeVertex where
  x : Bool
  y : Bool
  z : Bool
deriving DecidableEq, Repr

/-- The coarse-cell origin and opposite corner. -/
def origin : CubeVertex := ⟨false, false, false⟩
def opposite : CubeVertex := ⟨true, true, true⟩

/-- Twelve positively oriented edge phases of one cubical cell.
`edgeX y z` runs from `(0,y,z)` to `(1,y,z)`, and cyclically. -/
structure CubeLinks where
  edgeX : Bool → Bool → Circle
  edgeY : Bool → Bool → Circle
  edgeZ : Bool → Bool → Circle

abbrev CubeGauge := CubeVertex → Circle
abbrev CubeState := CubeVertex → Spinor

namespace CubeLinks

/-- Gauge transformation of all twelve oriented cell edges. -/
def gaugeTransform (L : CubeLinks) (g : CubeGauge) : CubeLinks where
  edgeX := fun y z =>
    g ⟨true, y, z⟩ * L.edgeX y z * (g ⟨false, y, z⟩)⁻¹
  edgeY := fun x z =>
    g ⟨x, true, z⟩ * L.edgeY x z * (g ⟨x, false, z⟩)⁻¹
  edgeZ := fun x y =>
    g ⟨x, y, true⟩ * L.edgeZ x y * (g ⟨x, y, false⟩)⁻¹

/-! ## Face paths and plaquettes -/

/-- `x` then `y` on the face at fixed `z`. -/
def pathXY (L : CubeLinks) (z : Bool) : Circle :=
  L.edgeY true z * L.edgeX false z

/-- `y` then `x` on the face at fixed `z`. -/
def pathYX (L : CubeLinks) (z : Bool) : Circle :=
  L.edgeX true z * L.edgeY false z

/-- `x` then `z` on the face at fixed `y`. -/
def pathXZ (L : CubeLinks) (y : Bool) : Circle :=
  L.edgeZ true y * L.edgeX y false

/-- `z` then `x` on the face at fixed `y`. -/
def pathZX (L : CubeLinks) (y : Bool) : Circle :=
  L.edgeX y true * L.edgeZ false y

/-- `y` then `z` on the face at fixed `x`. -/
def pathYZ (L : CubeLinks) (x : Bool) : Circle :=
  L.edgeZ x true * L.edgeY x false

/-- `z` then `y` on the face at fixed `x`. -/
def pathZY (L : CubeLinks) (x : Bool) : Circle :=
  L.edgeY x true * L.edgeZ x false

/-- Oriented `xy` face holonomy. -/
def plaquetteXY (L : CubeLinks) (z : Bool) : Circle :=
  L.pathXY z / L.pathYX z

/-- Oriented `xz` face holonomy. -/
def plaquetteXZ (L : CubeLinks) (y : Bool) : Circle :=
  L.pathXZ y / L.pathZX y

/-- Oriented `yz` face holonomy. -/
def plaquetteYZ (L : CubeLinks) (x : Bool) : Circle :=
  L.pathYZ x / L.pathZY x

@[simp] theorem plaquetteXY_eq_one_iff (L : CubeLinks) (z : Bool) :
    L.plaquetteXY z = 1 ↔ L.pathXY z = L.pathYX z := by
  unfold plaquetteXY
  rw [div_eq_one]

@[simp] theorem plaquetteXZ_eq_one_iff (L : CubeLinks) (y : Bool) :
    L.plaquetteXZ y = 1 ↔ L.pathXZ y = L.pathZX y := by
  unfold plaquetteXZ
  rw [div_eq_one]

@[simp] theorem plaquetteYZ_eq_one_iff (L : CubeLinks) (x : Bool) :
    L.plaquetteYZ x = 1 ↔ L.pathYZ x = L.pathZY x := by
  unfold plaquetteYZ
  rw [div_eq_one]

/-- Gauge transformation of the two lower-to-upper paths on an `xy` face. -/
theorem pathXY_gauge (L : CubeLinks) (g : CubeGauge) (z : Bool) :
    (L.gaugeTransform g).pathXY z =
      g ⟨true, true, z⟩ * L.pathXY z * (g ⟨false, false, z⟩)⁻¹ := by
  simp only [pathXY, gaugeTransform]
  group

theorem pathYX_gauge (L : CubeLinks) (g : CubeGauge) (z : Bool) :
    (L.gaugeTransform g).pathYX z =
      g ⟨true, true, z⟩ * L.pathYX z * (g ⟨false, false, z⟩)⁻¹ := by
  simp only [pathYX, gaugeTransform]
  group

theorem pathXZ_gauge (L : CubeLinks) (g : CubeGauge) (y : Bool) :
    (L.gaugeTransform g).pathXZ y =
      g ⟨true, y, true⟩ * L.pathXZ y * (g ⟨false, y, false⟩)⁻¹ := by
  simp only [pathXZ, gaugeTransform]
  group

theorem pathZX_gauge (L : CubeLinks) (g : CubeGauge) (y : Bool) :
    (L.gaugeTransform g).pathZX y =
      g ⟨true, y, true⟩ * L.pathZX y * (g ⟨false, y, false⟩)⁻¹ := by
  simp only [pathZX, gaugeTransform]
  group

theorem pathYZ_gauge (L : CubeLinks) (g : CubeGauge) (x : Bool) :
    (L.gaugeTransform g).pathYZ x =
      g ⟨x, true, true⟩ * L.pathYZ x * (g ⟨x, false, false⟩)⁻¹ := by
  simp only [pathYZ, gaugeTransform]
  group

theorem pathZY_gauge (L : CubeLinks) (g : CubeGauge) (x : Bool) :
    (L.gaugeTransform g).pathZY x =
      g ⟨x, true, true⟩ * L.pathZY x * (g ⟨x, false, false⟩)⁻¹ := by
  simp only [pathZY, gaugeTransform]
  group

/-- Face plaquettes are exactly gauge invariant. -/
@[simp] theorem plaquetteXY_gauge_invariant
    (L : CubeLinks) (g : CubeGauge) (z : Bool) :
    (L.gaugeTransform g).plaquetteXY z = L.plaquetteXY z := by
  unfold plaquetteXY
  rw [pathXY_gauge, pathYX_gauge]
  exact common_endpoint_ratio_cancel
    (g ⟨true, true, z⟩) (g ⟨false, false, z⟩)
    (L.pathXY z) (L.pathYX z)

@[simp] theorem plaquetteXZ_gauge_invariant
    (L : CubeLinks) (g : CubeGauge) (y : Bool) :
    (L.gaugeTransform g).plaquetteXZ y = L.plaquetteXZ y := by
  unfold plaquetteXZ
  rw [pathXZ_gauge, pathZX_gauge]
  exact common_endpoint_ratio_cancel
    (g ⟨true, y, true⟩) (g ⟨false, y, false⟩)
    (L.pathXZ y) (L.pathZX y)

@[simp] theorem plaquetteYZ_gauge_invariant
    (L : CubeLinks) (g : CubeGauge) (x : Bool) :
    (L.gaugeTransform g).plaquetteYZ x = L.plaquetteYZ x := by
  unfold plaquetteYZ
  rw [pathYZ_gauge, pathZY_gauge]
  exact common_endpoint_ratio_cancel
    (g ⟨x, true, true⟩) (g ⟨x, false, false⟩)
    (L.pathYZ x) (L.pathZY x)

/-! ## Six origin-to-opposite-corner paths -/

/-- Coordinate order `x-y-z`. -/
def pathXYZ (L : CubeLinks) : Circle :=
  L.edgeZ true true * L.edgeY true false * L.edgeX false false

/-- Coordinate order `x-z-y`. -/
def pathXZY (L : CubeLinks) : Circle :=
  L.edgeY true true * L.edgeZ true false * L.edgeX false false

/-- Coordinate order `y-x-z`. -/
def pathYXZ (L : CubeLinks) : Circle :=
  L.edgeZ true true * L.edgeX true false * L.edgeY false false

/-- Coordinate order `y-z-x`. -/
def pathYZX (L : CubeLinks) : Circle :=
  L.edgeX true true * L.edgeZ false true * L.edgeY false false

/-- Coordinate order `z-x-y`. -/
def pathZXY (L : CubeLinks) : Circle :=
  L.edgeY true true * L.edgeX false true * L.edgeZ false false

/-- Coordinate order `z-y-x`. -/
def pathZYX (L : CubeLinks) : Circle :=
  L.edgeX true true * L.edgeY false true * L.edgeZ false false

/-- Each face holonomy converts the reverse face path to the reference path. -/
@[simp] theorem plaquetteXY_mul_pathYX (L : CubeLinks) (z : Bool) :
    L.plaquetteXY z * L.pathYX z = L.pathXY z := by
  simp [plaquetteXY]

@[simp] theorem plaquetteXZ_mul_pathZX (L : CubeLinks) (y : Bool) :
    L.plaquetteXZ y * L.pathZX y = L.pathXZ y := by
  simp [plaquetteXZ]

@[simp] theorem plaquetteYZ_mul_pathZY (L : CubeLinks) (x : Bool) :
    L.plaquetteYZ x * L.pathZY x = L.pathYZ x := by
  simp [plaquetteYZ]

/-- Each adjacent path transposition is multiplication by one face holonomy. -/
theorem pathXYZ_eq_xy0_mul_pathYXZ (L : CubeLinks) :
    L.pathXYZ = L.plaquetteXY false * L.pathYXZ := by
  calc
    L.pathXYZ = L.edgeZ true true * L.pathXY false := by
      simp [pathXYZ, pathXY, mul_assoc]
    _ = L.edgeZ true true * (L.plaquetteXY false * L.pathYX false) := by simp
    _ = L.plaquetteXY false * L.pathYXZ := by
      simp [pathYXZ, pathYX]
      ac_rfl

theorem pathXYZ_eq_yz1_mul_pathXZY (L : CubeLinks) :
    L.pathXYZ = L.plaquetteYZ true * L.pathXZY := by
  calc
    L.pathXYZ = L.pathYZ true * L.edgeX false false := by
      simp [pathXYZ, pathYZ]
    _ = (L.plaquetteYZ true * L.pathZY true) * L.edgeX false false := by simp
    _ = L.plaquetteYZ true * L.pathXZY := by
      simp [pathXZY, pathZY]
      ac_rfl

theorem pathXZY_eq_edgeY_mul_pathXZ (L : CubeLinks) :
    L.pathXZY = L.edgeY true true * L.pathXZ false := by
  simp [pathXZY, pathXZ]
  ac_rfl

/-- Expanded lower-`xz` adjacent transposition. -/
theorem pathXZY_eq_xz0_mul_pathZXY (L : CubeLinks) :
    L.pathXZY = L.plaquetteXZ false * L.pathZXY := by
  calc
    L.pathXZY = L.edgeY true true * L.pathXZ false := by
      exact L.pathXZY_eq_edgeY_mul_pathXZ
    _ = L.edgeY true true * (L.plaquetteXZ false * L.pathZX false) := by simp
    _ = L.plaquetteXZ false * L.pathZXY := by
      simp [pathZXY, pathZX]
      ac_rfl

theorem pathYXZ_eq_xz1_mul_pathYZX (L : CubeLinks) :
    L.pathYXZ = L.plaquetteXZ true * L.pathYZX := by
  calc
    L.pathYXZ = L.pathXZ true * L.edgeY false false := by
      simp [pathYXZ, pathXZ]
    _ = (L.plaquetteXZ true * L.pathZX true) * L.edgeY false false := by simp
    _ = L.plaquetteXZ true * L.pathYZX := by
      simp [pathYZX, pathZX]
      ac_rfl

theorem pathYZX_eq_yz0_mul_pathZYX (L : CubeLinks) :
    L.pathYZX = L.plaquetteYZ false * L.pathZYX := by
  calc
    L.pathYZX = L.edgeX true true * L.pathYZ false := by
      simp [pathYZX, pathYZ]
      ac_rfl
    _ = L.edgeX true true * (L.plaquetteYZ false * L.pathZY false) := by simp
    _ = L.plaquetteYZ false * L.pathZYX := by
      simp [pathZYX, pathZY]
      ac_rfl

theorem pathZXY_eq_xy1_mul_pathZYX (L : CubeLinks) :
    L.pathZXY = L.plaquetteXY true * L.pathZYX := by
  calc
    L.pathZXY = L.pathXY true * L.edgeZ false false := by
      simp [pathZXY, pathXY]
    _ = (L.plaquetteXY true * L.pathYX true) * L.edgeZ false false := by simp
    _ = L.plaquetteXY true * L.pathZYX := by
      simp [pathZYX, pathYX]
      ac_rfl

/-- Abelian cube Bianchi identity: the two adjacent-transposition routes from
`XYZ` to `ZYX` carry the same total face holonomy. -/
theorem cube_bianchi (L : CubeLinks) :
    L.plaquetteYZ true * L.plaquetteXZ false * L.plaquetteXY true =
      L.plaquetteXY false * L.plaquetteXZ true * L.plaquetteYZ false := by
  have hA : L.pathXYZ =
      (L.plaquetteYZ true * L.plaquetteXZ false * L.plaquetteXY true) *
        L.pathZYX := by
    rw [L.pathXYZ_eq_yz1_mul_pathXZY]
    rw [L.pathXZY_eq_xz0_mul_pathZXY]
    rw [L.pathZXY_eq_xy1_mul_pathZYX]
    ac_rfl
  have hB : L.pathXYZ =
      (L.plaquetteXY false * L.plaquetteXZ true * L.plaquetteYZ false) *
        L.pathZYX := by
    rw [L.pathXYZ_eq_xy0_mul_pathYXZ]
    rw [L.pathYXZ_eq_xz1_mul_pathYZX]
    rw [L.pathYZX_eq_yz0_mul_pathZYX]
    ac_rfl
  exact mul_right_cancel (hA.symm.trans hB)

/-- Flatness of all six oriented faces. -/
structure Flat (L : CubeLinks) : Prop where
  xy : ∀ z, L.plaquetteXY z = 1
  xz : ∀ y, L.plaquetteXZ y = 1
  yz : ∀ x, L.plaquetteYZ x = 1

namespace Flat

/-- In the flat sector all six corner paths coincide. -/
theorem all_corner_paths (L : CubeLinks) (h : L.Flat) :
    L.pathXYZ = L.pathXZY ∧
    L.pathXYZ = L.pathYXZ ∧
    L.pathXYZ = L.pathYZX ∧
    L.pathXYZ = L.pathZXY ∧
    L.pathXYZ = L.pathZYX := by
  have hXYZ_XZY : L.pathXYZ = L.pathXZY := by
    rw [L.pathXYZ_eq_yz1_mul_pathXZY, h.yz true, one_mul]
  have hXYZ_YXZ : L.pathXYZ = L.pathYXZ := by
    rw [L.pathXYZ_eq_xy0_mul_pathYXZ, h.xy false, one_mul]
  have hXZY_ZXY : L.pathXZY = L.pathZXY := by
    rw [L.pathXZY_eq_xz0_mul_pathZXY, h.xz false, one_mul]
  have hYXZ_YZX : L.pathYXZ = L.pathYZX := by
    rw [L.pathYXZ_eq_xz1_mul_pathYZX, h.xz true, one_mul]
  have hYZX_ZYX : L.pathYZX = L.pathZYX := by
    rw [L.pathYZX_eq_yz0_mul_pathZYX, h.yz false, one_mul]
  exact ⟨hXYZ_XZY, hXYZ_YXZ,
    hXYZ_YXZ.trans hYXZ_YZX,
    hXYZ_XZY.trans hXZY_ZXY,
    hXYZ_YXZ.trans (hYXZ_YZX.trans hYZX_ZYX)⟩

/-- Five flat faces force the sixth through the cube Bianchi identity. -/
theorem xy1_of_other_five (L : CubeLinks)
    (hyz1 : L.plaquetteYZ true = 1)
    (hxz0 : L.plaquetteXZ false = 1)
    (hxy0 : L.plaquetteXY false = 1)
    (hxz1 : L.plaquetteXZ true = 1)
    (hyz0 : L.plaquetteYZ false = 1) :
    L.plaquetteXY true = 1 := by
  have h := L.cube_bianchi
  rw [hyz1, hxz0, hxy0, hxz1, hyz0] at h
  simpa using h

end Flat


/-- Flatness is preserved by arbitrary vertex gauges. -/
theorem Flat.gaugeTransform (L : CubeLinks) (h : L.Flat) (g : CubeGauge) :
    (L.gaugeTransform g).Flat where
  xy := by intro z; simpa using h.xy z
  xz := by intro y; simpa using h.xz y
  yz := by intro x; simpa using h.yz x

/-! ## Gauge-covariant reference-path interpolation -/

/-- Reference path phase from the origin to each child vertex.  On faces and
at the opposite corner the reference order is `x`, then `y`, then `z`. -/
def referencePhase (L : CubeLinks) : CubeVertex → Circle
  | ⟨false, false, false⟩ => 1
  | ⟨true,  false, false⟩ => L.edgeX false false
  | ⟨false, true,  false⟩ => L.edgeY false false
  | ⟨false, false, true ⟩ => L.edgeZ false false
  | ⟨true,  true,  false⟩ => L.pathXY false
  | ⟨true,  false, true ⟩ => L.pathXZ false
  | ⟨false, true,  true ⟩ => L.pathYZ false
  | ⟨true,  true,  true ⟩ => L.pathXYZ

/-- Every reference transport acquires only the target and origin gauge factors. -/
@[simp] theorem referencePhase_gauge (L : CubeLinks) (g : CubeGauge)
    (v : CubeVertex) :
    (L.gaugeTransform g).referencePhase v =
      g v * L.referencePhase v * (g origin)⁻¹ := by
  rcases v with ⟨x, y, z⟩
  cases x <;> cases y <;> cases z <;>
    simp [referencePhase, origin, gaugeTransform, pathXY, pathXZ, pathYZ,
      pathXYZ] <;> group

/-- Reference-path interpolation of one coarse spinor into the eight children. -/
def embed (L : CubeLinks) (ψ : Spinor) : CubeState :=
  fun v => phaseMul (L.referencePhase v) ψ

/-- Sitewise gauge action on the eight child spinors. -/
def gaugeState (g : CubeGauge) (Ψ : CubeState) : CubeState :=
  fun v => phaseMul (g v) (Ψ v)

/-- The cubical reference-path interpolation is exactly gauge covariant. -/
@[simp] theorem embed_gauge_covariant (L : CubeLinks) (g : CubeGauge)
    (ψ : Spinor) :
    (L.gaugeTransform g).embed (phaseMul (g origin) ψ) =
      gaugeState g (L.embed ψ) := by
  funext v
  simp [embed, gaugeState, phaseMul_mul, referencePhase_gauge]

/-! ## One-eighth Hilbert normalization -/

/-- Explicit Hilbert product of the eight child vertices. -/
def cubeIP (Ψ Φ : CubeState) : ℂ :=
  (8 : ℂ)⁻¹ * (
    ip (Ψ ⟨false,false,false⟩) (Φ ⟨false,false,false⟩) +
    ip (Ψ ⟨true, false,false⟩) (Φ ⟨true, false,false⟩) +
    ip (Ψ ⟨false,true, false⟩) (Φ ⟨false,true, false⟩) +
    ip (Ψ ⟨false,false,true ⟩) (Φ ⟨false,false,true ⟩) +
    ip (Ψ ⟨true, true, false⟩) (Φ ⟨true, true, false⟩) +
    ip (Ψ ⟨true, false,true ⟩) (Φ ⟨true, false,true ⟩) +
    ip (Ψ ⟨false,true, true ⟩) (Φ ⟨false,true, true ⟩) +
    ip (Ψ ⟨true, true, true ⟩) (Φ ⟨true, true, true ⟩))

/-- The one-eighth child-cell measure makes reference interpolation isometric. -/
@[simp] theorem embed_cubeIP_isometry (L : CubeLinks) (ψ φ : Spinor) :
    cubeIP (L.embed ψ) (L.embed φ) = ip ψ φ := by
  simp [cubeIP, embed]
  ring

/-! ## Exact curvature-controlled spinor defects -/

/-- Difference between two phase transports of the same spinor. -/
def pathDefect (p q : Circle) (ψ : Spinor) : Spinor :=
  phaseMul p ψ - phaseMul q ψ

/-- A path ratio `Omega` controls the transport defect exactly. -/
theorem pathDefect_eq_curvature_transport
    (p q Ω : Circle) (ψ : Spinor) (h : p = Ω * q) :
    pathDefect p q ψ =
      phaseMul q ((((Ω : ℂ) - 1) : ℂ) • ψ) := by
  subst p
  ext j
  simp [pathDefect, phaseMul]
  ring

/-- Exact Hilbert weight of a curvature-controlled path defect. -/
theorem pathDefect_ip_eq_curvature_weight
    (p q Ω : Circle) (ψ : Spinor) (h : p = Ω * q) :
    ip (pathDefect p q ψ) (pathDefect p q ψ) =
      (starRingEnd ℂ) ((Ω : ℂ) - 1) * ((Ω : ℂ) - 1) * ip ψ ψ := by
  rw [pathDefect_eq_curvature_transport p q Ω ψ h]
  rw [ip_phase_same]
  rw [ip_smul_left, ip_smul_right]
  ring

/-- Lower `xy` face curvature controls the `XYZ` versus `YXZ` corner defect. -/
theorem defect_XYZ_YXZ (L : CubeLinks) (ψ : Spinor) :
    pathDefect L.pathXYZ L.pathYXZ ψ =
      phaseMul L.pathYXZ
        ((((L.plaquetteXY false : Circle) : ℂ) - 1) • ψ) := by
  exact pathDefect_eq_curvature_transport _ _ _ _ L.pathXYZ_eq_xy0_mul_pathYXZ

/-- Upper `yz` face curvature controls the `XYZ` versus `XZY` defect. -/
theorem defect_XYZ_XZY (L : CubeLinks) (ψ : Spinor) :
    pathDefect L.pathXYZ L.pathXZY ψ =
      phaseMul L.pathXZY
        ((((L.plaquetteYZ true : Circle) : ℂ) - 1) • ψ) := by
  exact pathDefect_eq_curvature_transport _ _ _ _ L.pathXYZ_eq_yz1_mul_pathXZY

/-- Lower `xz` face curvature controls the `XZY` versus `ZXY` defect. -/
theorem defect_XZY_ZXY (L : CubeLinks) (ψ : Spinor) :
    pathDefect L.pathXZY L.pathZXY ψ =
      phaseMul L.pathZXY
        ((((L.plaquetteXZ false : Circle) : ℂ) - 1) • ψ) := by
  exact pathDefect_eq_curvature_transport _ _ _ _ L.pathXZY_eq_xz0_mul_pathZXY

/-- Upper `xz` face curvature controls the `YXZ` versus `YZX` defect. -/
theorem defect_YXZ_YZX (L : CubeLinks) (ψ : Spinor) :
    pathDefect L.pathYXZ L.pathYZX ψ =
      phaseMul L.pathYZX
        ((((L.plaquetteXZ true : Circle) : ℂ) - 1) • ψ) := by
  exact pathDefect_eq_curvature_transport _ _ _ _ L.pathYXZ_eq_xz1_mul_pathYZX

/-- Lower `yz` face curvature controls the `YZX` versus `ZYX` defect. -/
theorem defect_YZX_ZYX (L : CubeLinks) (ψ : Spinor) :
    pathDefect L.pathYZX L.pathZYX ψ =
      phaseMul L.pathZYX
        ((((L.plaquetteYZ false : Circle) : ℂ) - 1) • ψ) := by
  exact pathDefect_eq_curvature_transport _ _ _ _ L.pathYZX_eq_yz0_mul_pathZYX

/-- Upper `xy` face curvature controls the `ZXY` versus `ZYX` defect. -/
theorem defect_ZXY_ZYX (L : CubeLinks) (ψ : Spinor) :
    pathDefect L.pathZXY L.pathZYX ψ =
      phaseMul L.pathZYX
        ((((L.plaquetteXY true : Circle) : ℂ) - 1) • ψ) := by
  exact pathDefect_eq_curvature_transport _ _ _ _ L.pathZXY_eq_xy1_mul_pathZYX


/-- The chosen nonzero basis spinor detects equality of phase transports. -/
@[simp] theorem pathDefect_basis_eq_zero_iff (p q : Circle) :
    pathDefect p q basisSpinor0 = 0 ↔ p = q := by
  constructor
  · intro h
    apply phaseMul_basisSpinor0_injective
    exact sub_eq_zero.mp h
  · rintro rfl
    simp [pathDefect]

/-- Under a known path-ratio factorization, zero basis-spinor defect is
exactly trivial curvature. -/
theorem pathDefect_basis_eq_zero_iff_curvature_one
    (p q Ω : Circle) (h : p = Ω * q) :
    pathDefect p q basisSpinor0 = 0 ↔ Ω = 1 := by
  rw [pathDefect_basis_eq_zero_iff]
  constructor
  · intro hpq
    have hm : Ω * q = 1 * q := by
      simpa using h.symm.trans hpq
    exact mul_right_cancel hm
  · intro hΩ
    simpa [hΩ] using h

@[simp] theorem defect_XYZ_YXZ_basis_eq_zero_iff (L : CubeLinks) :
    pathDefect L.pathXYZ L.pathYXZ basisSpinor0 = 0 ↔
      L.plaquetteXY false = 1 :=
  pathDefect_basis_eq_zero_iff_curvature_one _ _ _
    L.pathXYZ_eq_xy0_mul_pathYXZ

@[simp] theorem defect_XYZ_XZY_basis_eq_zero_iff (L : CubeLinks) :
    pathDefect L.pathXYZ L.pathXZY basisSpinor0 = 0 ↔
      L.plaquetteYZ true = 1 :=
  pathDefect_basis_eq_zero_iff_curvature_one _ _ _
    L.pathXYZ_eq_yz1_mul_pathXZY

@[simp] theorem defect_XZY_ZXY_basis_eq_zero_iff (L : CubeLinks) :
    pathDefect L.pathXZY L.pathZXY basisSpinor0 = 0 ↔
      L.plaquetteXZ false = 1 :=
  pathDefect_basis_eq_zero_iff_curvature_one _ _ _
    L.pathXZY_eq_xz0_mul_pathZXY

@[simp] theorem defect_YXZ_YZX_basis_eq_zero_iff (L : CubeLinks) :
    pathDefect L.pathYXZ L.pathYZX basisSpinor0 = 0 ↔
      L.plaquetteXZ true = 1 :=
  pathDefect_basis_eq_zero_iff_curvature_one _ _ _
    L.pathYXZ_eq_xz1_mul_pathYZX

@[simp] theorem defect_YZX_ZYX_basis_eq_zero_iff (L : CubeLinks) :
    pathDefect L.pathYZX L.pathZYX basisSpinor0 = 0 ↔
      L.plaquetteYZ false = 1 :=
  pathDefect_basis_eq_zero_iff_curvature_one _ _ _
    L.pathYZX_eq_yz0_mul_pathZYX

@[simp] theorem defect_ZXY_ZYX_basis_eq_zero_iff (L : CubeLinks) :
    pathDefect L.pathZXY L.pathZYX basisSpinor0 = 0 ↔
      L.plaquetteXY true = 1 :=
  pathDefect_basis_eq_zero_iff_curvature_one _ _ _
    L.pathZXY_eq_xy1_mul_pathZYX

/-- Flat cells have zero defect for every adjacent path transposition. -/
theorem all_adjacent_defects_zero (L : CubeLinks) (h : L.Flat) (ψ : Spinor) :
    pathDefect L.pathXYZ L.pathYXZ ψ = 0 ∧
    pathDefect L.pathXYZ L.pathXZY ψ = 0 ∧
    pathDefect L.pathXZY L.pathZXY ψ = 0 ∧
    pathDefect L.pathYXZ L.pathYZX ψ = 0 ∧
    pathDefect L.pathYZX L.pathZYX ψ = 0 ∧
    pathDefect L.pathZXY L.pathZYX ψ = 0 := by
  rcases Flat.all_corner_paths L h with ⟨hXZY, hYXZ, hYZX, hZXY, hZYX⟩
  have hXZY_ZXY : L.pathXZY = L.pathZXY := hXZY.symm.trans hZXY
  have hYXZ_YZX : L.pathYXZ = L.pathYZX := hYXZ.symm.trans hYZX
  have hYZX_ZYX : L.pathYZX = L.pathZYX := hYZX.symm.trans hZYX
  have hZXY_ZYX : L.pathZXY = L.pathZYX := hZXY.symm.trans hZYX
  constructor
  · rw [hYXZ]
    simp [pathDefect]
  constructor
  · rw [hXZY]
    simp [pathDefect]
  constructor
  · rw [hXZY_ZXY]
    simp [pathDefect]
  constructor
  · rw [hYXZ_YZX]
    simp [pathDefect]
  constructor
  · rw [hYZX_ZYX]
    simp [pathDefect]
  · rw [hZXY_ZYX]
    simp [pathDefect]

end CubeLinks

/-! ## Coarse-site family of cubical cells -/

abbrev CellLinks (Site : Type u) := Site → CubeLinks
abbrev CellState (Site : Type u) := Site → CubeState
abbrev CellGauge (Site : Type u) := Site → CubeGauge

/-- Embed every coarse-site spinor into its local eight-vertex child cell. -/
def cellEmbed {Site : Type u} (L : CellLinks Site)
    (ψ : State (Site := Site)) : CellState Site :=
  fun x => (L x).embed (ψ x)

/-- Gauge action on a family of child cells. -/
def cellGaugeState {Site : Type u} (g : CellGauge Site)
    (Ψ : CellState Site) : CellState Site :=
  fun x => CubeLinks.gaugeState (g x) (Ψ x)

/-- The induced gauge on coarse origin values. -/
def originGauge {Site : Type u} (g : CellGauge Site) : Gauge (Site := Site) :=
  fun x => g x origin

/-- Gauge-transform every local cubical link field. -/
def gaugeCellLinks {Site : Type u} (L : CellLinks Site)
    (g : CellGauge Site) : CellLinks Site :=
  fun x => (L x).gaugeTransform (g x)

/-- Global family version of cubical interpolation covariance. -/
@[simp] theorem cellEmbed_gauge_covariant {Site : Type u}
    (L : CellLinks Site) (g : CellGauge Site) (ψ : State (Site := Site)) :
    cellEmbed (gaugeCellLinks L g) (gaugeState (originGauge g) ψ) =
      cellGaugeState g (cellEmbed L ψ) := by
  funext x v
  exact congrFun (CubeLinks.embed_gauge_covariant (L x) (g x) (ψ x)) v

/-- One-eighth weighted Hilbert product for a finite family of refined cells. -/
def cellIP {Site : Type u} [Fintype Site]
    (Ψ Φ : CellState Site) : ℂ :=
  ∑ x, CubeLinks.cubeIP (Ψ x) (Φ x)

/-- Cubical interpolation is globally Hilbert isometric on a finite coarse lattice. -/
@[simp] theorem cellEmbed_isometry {Site : Type u} [Fintype Site]
    (L : CellLinks Site) (ψ φ : State (Site := Site)) :
    cellIP (cellEmbed L ψ) (cellEmbed L φ) = stateIP ψ φ := by
  simp [cellIP, cellEmbed, stateIP]

/-! ## Concrete nonflat cubical witness -/

/-- A cube with one nontrivial lower `xy` face. -/
def nonflatCube : CubeLinks where
  edgeX := fun _ _ => 1
  edgeY := fun x z => if x && !z then -1 else 1
  edgeZ := fun _ _ => 1

@[simp] theorem nonflatCube_xy0 : nonflatCube.plaquetteXY false = -1 := by
  simp [nonflatCube, CubeLinks.plaquetteXY, CubeLinks.pathXY,
    CubeLinks.pathYX]

@[simp] theorem nonflatCube_pathXYZ : nonflatCube.pathXYZ = -1 := by
  simp [nonflatCube, CubeLinks.pathXYZ]

@[simp] theorem nonflatCube_pathYXZ : nonflatCube.pathYXZ = 1 := by
  simp [nonflatCube, CubeLinks.pathYXZ]

/-- The concrete nonflat cube has a genuinely nonzero opposite-corner defect. -/
theorem nonflatCube_defect_nonzero :
    CubeLinks.pathDefect nonflatCube.pathXYZ nonflatCube.pathYXZ basisSpinor0 ≠ 0 := by
  intro h
  have h0 := congrFun h 0
  norm_num [CubeLinks.pathDefect, nonflatCube_pathXYZ,
    nonflatCube_pathYXZ, phaseMul, basisSpinor0] at h0

end Relativistic3DCubicalRefinement
end KomorebiPhysics
