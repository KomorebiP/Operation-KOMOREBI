module

public import KomorebiPhysics.Relativistic3DEdgeCompatibility
public import Mathlib.Analysis.Normed.Module.FiniteDimension

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Continuous operator refinement defects with independent edge and curvature budgets

This module packages the finite-volume Clifford shifts and phase-frame embedding
as continuous linear maps.  It identifies the exact local adjacent-scale
operator defect for arbitrary fine links, propagates those defects through the
full seven-factor walk, and keeps straight-edge reconstruction and cubical
path curvature as two independent budgets.

The final section connects summable edge and curvature budgets to the general
local-discrete/global-continuous reconstruction theorem.  No mesh decay law is
asserted: summability remains an explicit hypothesis.
-/

namespace KomorebiPhysics
namespace Relativistic3DCombinedDefect

open scoped BigOperators ComplexConjugate Topology
open Filter
open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DCubicalRefinement
open Relativistic3DFullWalkRefinement
open Relativistic3DEdgeCompatibility
open LocalDiscreteGlobalContinuum

universe u v

/-- Finite enumeration of the eight Boolean child vertices. -/
def cubeVertexEquiv : (Bool × (Bool × Bool)) ≃ CubeVertex where
  toFun q := ⟨q.1, q.2.1, q.2.2⟩
  invFun q := (q.x, (q.y, q.z))
  left_inv q := by rcases q with ⟨x, y, z⟩; rfl
  right_inv q := by rcases q with ⟨x, y, z⟩; rfl

@[instance_reducible] def cubeVertexFintype : Fintype CubeVertex :=
  Fintype.ofEquiv (Bool × (Bool × Bool)) cubeVertexEquiv

attribute [instance] cubeVertexFintype

/-! ## Continuous-linear packaging of the finite lattice operators -/

section LinearPackaging

variable {Site : Type u}

/-- A directional Clifford shift is additive. -/
theorem directionalShift_add (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ φ : State (Site := Site)) :
    directionalShift A τ u (ψ + φ) =
      directionalShift A τ u ψ + directionalShift A τ u φ := by
  funext x
  ext j
  simp [directionalShift, phaseMul]
  ring

/-- A directional Clifford shift is complex-linear. -/
theorem directionalShift_smul (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (c : ℂ) (ψ : State (Site := Site)) :
    directionalShift A τ u (c • ψ) = c • directionalShift A τ u ψ := by
  funext x
  ext j
  simp [directionalShift, phaseMul]
  ring

/-- Algebraic linear map underlying one directional shift. -/
def directionalShiftLinear (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    State (Site := Site) →ₗ[ℂ] State (Site := Site) where
  toFun := directionalShift A τ u
  map_add' := directionalShift_add A τ u
  map_smul' := directionalShift_smul A τ u

/-- Continuous-linear realization of one finite-lattice directional shift.
Continuity follows from finite dimensionality; no operator-norm claim is hidden
in this construction. -/
def directionalShiftCLM [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    State (Site := Site) →L[ℂ] State (Site := Site) :=
  { directionalShiftLinear A τ u with
    cont := (directionalShiftLinear A τ u).continuous_of_finiteDimensional }

@[simp] theorem directionalShiftCLM_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    directionalShiftCLM A τ u ψ = directionalShift A τ u ψ := rfl

/-- Phase-frame interpolation is additive. -/
theorem frameEmbed_add (r : PhaseFrame Site)
    (ψ φ : State (Site := Site)) :
    frameEmbed r (ψ + φ) = frameEmbed r ψ + frameEmbed r φ := by
  funext p
  simp [frameEmbed, phaseMul_add]

/-- Phase-frame interpolation is complex-linear. -/
theorem frameEmbed_smul (r : PhaseFrame Site)
    (c : ℂ) (ψ : State (Site := Site)) :
    frameEmbed r (c • ψ) = c • frameEmbed r ψ := by
  funext p
  ext j
  simp [frameEmbed, phaseMul]
  ring

/-- Algebraic linear map underlying the phase-frame embedding. -/
def frameEmbedLinear (r : PhaseFrame Site) :
    State (Site := Site) →ₗ[ℂ] State (Site := FineSite3 Site) where
  toFun := frameEmbed r
  map_add' := frameEmbed_add r
  map_smul' := frameEmbed_smul r

/-- Continuous-linear phase-frame embedding on a finite lattice. -/
def frameEmbedCLM [Fintype Site] (r : PhaseFrame Site) :
    State (Site := Site) →L[ℂ] State (Site := FineSite3 Site) :=
  { frameEmbedLinear r with
    cont := (frameEmbedLinear r).continuous_of_finiteDimensional }

@[simp] theorem frameEmbedCLM_apply [Fintype Site] (r : PhaseFrame Site)
    (ψ : State (Site := Site)) :
    frameEmbedCLM r ψ = frameEmbed r ψ := rfl

/-- Two consecutive fine `x` half-shifts as one continuous linear operator. -/
def twoHalfShiftXCLM [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site)) :
    State (Site := FineSite3 Site) →L[ℂ] State (Site := FineSite3 Site) :=
  (directionalShiftCLM A (halfShiftX τ) v).comp
    (directionalShiftCLM A (halfShiftX τ) v)

/-- Two consecutive fine `y` half-shifts. -/
def twoHalfShiftYCLM [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site)) :
    State (Site := FineSite3 Site) →L[ℂ] State (Site := FineSite3 Site) :=
  (directionalShiftCLM A (halfShiftY τ) v).comp
    (directionalShiftCLM A (halfShiftY τ) v)

/-- Two consecutive fine `z` half-shifts. -/
def twoHalfShiftZCLM [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site)) :
    State (Site := FineSite3 Site) →L[ℂ] State (Site := FineSite3 Site) :=
  (directionalShiftCLM A (halfShiftZ τ) v).comp
    (directionalShiftCLM A (halfShiftZ τ) v)

@[simp] theorem twoHalfShiftXCLM_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site))
    (Ψ : State (Site := FineSite3 Site)) :
    twoHalfShiftXCLM A τ v Ψ =
      directionalShift A (halfShiftX τ) v
        (directionalShift A (halfShiftX τ) v Ψ) := by
  simp [twoHalfShiftXCLM]

@[simp] theorem twoHalfShiftYCLM_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site))
    (Ψ : State (Site := FineSite3 Site)) :
    twoHalfShiftYCLM A τ v Ψ =
      directionalShift A (halfShiftY τ) v
        (directionalShift A (halfShiftY τ) v Ψ) := by
  simp [twoHalfShiftYCLM]

@[simp] theorem twoHalfShiftZCLM_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v : Link (Site := FineSite3 Site))
    (Ψ : State (Site := FineSite3 Site)) :
    twoHalfShiftZCLM A τ v Ψ =
      directionalShift A (halfShiftZ τ) v
        (directionalShift A (halfShiftZ τ) v Ψ) := by
  simp [twoHalfShiftZCLM]

/-- Actual adjacent-scale operator defect in the `x` direction. -/
def straightDefectOpX [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) :
    State (Site := Site) →L[ℂ] State (Site := FineSite3 Site) :=
  intertwiningDefectOp (twoHalfShiftXCLM A τ v)
    (frameEmbedCLM r) (directionalShiftCLM A τ u)

/-- Actual adjacent-scale operator defect in the `y` direction. -/
def straightDefectOpY [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) :
    State (Site := Site) →L[ℂ] State (Site := FineSite3 Site) :=
  intertwiningDefectOp (twoHalfShiftYCLM A τ v)
    (frameEmbedCLM r) (directionalShiftCLM A τ u)

/-- Actual adjacent-scale operator defect in the `z` direction. -/
def straightDefectOpZ [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) :
    State (Site := Site) →L[ℂ] State (Site := FineSite3 Site) :=
  intertwiningDefectOp (twoHalfShiftZCLM A τ v)
    (frameEmbedCLM r) (directionalShiftCLM A τ u)

@[simp] theorem straightDefectOpX_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) (ψ : State (Site := Site)) :
    straightDefectOpX A τ u r v ψ =
      directionalShift A (halfShiftX τ) v
        (directionalShift A (halfShiftX τ) v (frameEmbed r ψ)) -
      frameEmbed r (directionalShift A τ u ψ) := by
  simp [straightDefectOpX, intertwiningDefectOp, twoHalfShiftXCLM]

@[simp] theorem straightDefectOpY_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) (ψ : State (Site := Site)) :
    straightDefectOpY A τ u r v ψ =
      directionalShift A (halfShiftY τ) v
        (directionalShift A (halfShiftY τ) v (frameEmbed r ψ)) -
      frameEmbed r (directionalShift A τ u ψ) := by
  simp [straightDefectOpY, intertwiningDefectOp, twoHalfShiftYCLM]

@[simp] theorem straightDefectOpZ_apply [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) (ψ : State (Site := Site)) :
    straightDefectOpZ A τ u r v ψ =
      directionalShift A (halfShiftZ τ) v
        (directionalShift A (halfShiftZ τ) v (frameEmbed r ψ)) -
      frameEmbed r (directionalShift A τ u ψ) := by
  simp [straightDefectOpZ, intertwiningDefectOp, twoHalfShiftZCLM]

/-- Exact straight reconstruction annihilates the `x` operator defect,
independently of all plaquette data. -/
theorem straightDefectOpX_eq_zero [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleX τ u r v) :
    straightDefectOpX A τ u r v = 0 := by
  ext ψ p j
  rw [straightDefectOpX_apply]
  rw [two_halfShiftX_frameEmbed_of_straightCompatible A τ u r v hv]
  simp

/-- Exact straight reconstruction annihilates the `y` operator defect. -/
theorem straightDefectOpY_eq_zero [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleY τ u r v) :
    straightDefectOpY A τ u r v = 0 := by
  ext ψ p j
  rw [straightDefectOpY_apply]
  rw [two_halfShiftY_frameEmbed_of_straightCompatible A τ u r v hv]
  simp

/-- Exact straight reconstruction annihilates the `z` operator defect. -/
theorem straightDefectOpZ_eq_zero [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site))
    (hv : StraightCompatibleZ τ u r v) :
    straightDefectOpZ A τ u r v = 0 := by
  ext ψ p j
  rw [straightDefectOpZ_apply]
  rw [two_halfShiftZ_frameEmbed_of_straightCompatible A τ u r v hv]
  simp

end LinearPackaging

/-! ## The one-axis Hilbert defect as a continuous operator -/

section FineEdgeDefectOperator

variable {Site : Type u}

@[simp] theorem fineEdgeEmbed_add (P : FineEdgePair Site)
    (ψ φ : State (Site := Site)) :
    P.embed (ψ + φ) = P.embed ψ + P.embed φ := by
  funext y
  cases y <;> simp [FineEdgePair.embed, EdgeSubdivision.embed, phaseMul_add]

@[simp] theorem fineEdgeEmbed_smul (P : FineEdgePair Site)
    (c : ℂ) (ψ : State (Site := Site)) :
    P.embed (c • ψ) = c • P.embed ψ := by
  funext y
  cases y
  · rfl
  · ext j
    simp [FineEdgePair.embed, EdgeSubdivision.embed, phaseMul]
    ring

@[simp] theorem fineEdgeCoarseLinkDefect_add (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ φ : State (Site := Site)) :
    P.coarseLinkDefect A τ u (ψ + φ) =
      P.coarseLinkDefect A τ u ψ + P.coarseLinkDefect A τ u φ := by
  funext x
  ext j
  simp [FineEdgePair.coarseLinkDefect, directionalShift, phaseMul]
  ring

@[simp] theorem fineEdgeCoarseLinkDefect_smul (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (c : ℂ) (ψ : State (Site := Site)) :
    P.coarseLinkDefect A τ u (c • ψ) =
      c • P.coarseLinkDefect A τ u ψ := by
  funext x
  ext j
  simp [FineEdgePair.coarseLinkDefect, directionalShift, phaseMul]
  ring

@[simp] theorem fineEdgeIntertwiningDefect_add
    (P : FineEdgePair Site) (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ φ : State (Site := Site)) :
    P.fineIntertwiningDefect A τ u (ψ + φ) =
      P.fineIntertwiningDefect A τ u ψ +
        P.fineIntertwiningDefect A τ u φ := by
  simp only [P.fineIntertwiningDefect_eq_embed,
    fineEdgeCoarseLinkDefect_add P, fineEdgeEmbed_add P]

@[simp] theorem fineEdgeIntertwiningDefect_smul
    (P : FineEdgePair Site) (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (c : ℂ) (ψ : State (Site := Site)) :
    P.fineIntertwiningDefect A τ u (c • ψ) =
      c • P.fineIntertwiningDefect A τ u ψ := by
  simp only [P.fineIntertwiningDefect_eq_embed,
    fineEdgeCoarseLinkDefect_smul P, fineEdgeEmbed_smul P]

/-- Linear map whose values are exactly the arbitrary half-link refinement
defects proved in Block 29. -/
def fineEdgeDefectLinear (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    State (Site := Site) →ₗ[ℂ] State (Site := HalfSite Site) where
  toFun := P.fineIntertwiningDefect A τ u
  map_add' := fineEdgeIntertwiningDefect_add P A τ u
  map_smul' := fineEdgeIntertwiningDefect_smul P A τ u

/-- Continuous-linear operator realization of the one-axis arbitrary-link
defect on a finite lattice. -/
def fineEdgeDefectCLM [Fintype Site] (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    State (Site := Site) →L[ℂ] State (Site := HalfSite Site) :=
  { fineEdgeDefectLinear P A τ u with
    cont := (fineEdgeDefectLinear P A τ u).continuous_of_finiteDimensional }

@[simp] theorem fineEdgeDefectCLM_apply [Fintype Site]
    (P : FineEdgePair Site) (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    fineEdgeDefectCLM P A τ u ψ = P.fineIntertwiningDefect A τ u ψ := rfl

/-- The continuous defect operator retains the exact half-cell Hilbert-energy
identity from Block 29. -/
theorem fineEdgeDefectCLM_halfCellIP [Fintype Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    halfCellIP (fineEdgeDefectCLM P H.toClifford τ u ψ)
      (fineEdgeDefectCLM P H.toClifford τ u ψ) =
    stateIP (P.coarseLinkDefect H.toClifford τ u ψ)
      (P.coarseLinkDefect H.toClifford τ u ψ) := by
  exact P.fineIntertwiningDefect_halfCellIP H τ u ψ

/-- Fully explicit energy formula for the continuous one-axis defect operator. -/
theorem fineEdgeDefectCLM_energy [Fintype Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : State (Site := Site)) :
    halfCellIP (fineEdgeDefectCLM P H.toClifford τ u ψ)
      (fineEdgeDefectCLM P H.toClifford τ u ψ) =
    ∑ x,
      (phaseErrorWeight (P.productLink (τ.symm x)) (u (τ.symm x)) *
        ip (H.toClifford.plus (ψ (τ.symm x)))
          (H.toClifford.plus (ψ (τ.symm x))) +
      phaseErrorWeight (P.productLink x)⁻¹ (u x)⁻¹ *
        ip (H.toClifford.minus (ψ (τ x)))
          (H.toClifford.minus (ψ (τ x)))) := by
  exact P.fineIntertwiningDefect_energy H τ u ψ

@[simp] theorem fineEdgeDefectCLM_eq_zero_of_product
    [Fintype Site] (P : FineEdgePair Site)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (h : P.productLink = u) :
    fineEdgeDefectCLM P A τ u = 0 := by
  apply ContinuousLinearMap.ext
  intro ψ
  rw [fineEdgeDefectCLM_apply]
  exact P.fineIntertwiningDefect_eq_zero_of_product A τ u h ψ

end FineEdgeDefectOperator

/-! ## Seven-factor straight-edge operator budget -/

section StraightSevenFactor

variable {Site : Type u} [Fintype Site]

/-- The actual seven factor pairs for geometric refinement.  The two mass
pairs are supplied as continuous linear maps; the five spatial pairs are the
concrete two-half-step and one-coarse-step Clifford operators. -/
def straightSevenFactorPairs
    (mFine₀ mFine₁ : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (mCoarse₀ mCoarse₁ : State (Site := Site) →L[ℂ]
      State (Site := Site))
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site))
    (vx vy vz : Link (Site := FineSite3 Site)) :
    List ((State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site)) ×
      (State (Site := Site) →L[ℂ] State (Site := Site))) :=
  sevenFactorPairs
    (mFine₀, mCoarse₀)
    (twoHalfShiftXCLM cliffordX τx vx,
      directionalShiftCLM cliffordX τx ux)
    (twoHalfShiftYCLM cliffordY τy vy,
      directionalShiftCLM cliffordY τy uy)
    (twoHalfShiftZCLM cliffordZ τz vz,
      directionalShiftCLM cliffordZ τz uz)
    (twoHalfShiftYCLM cliffordY τy vy,
      directionalShiftCLM cliffordY τy uy)
    (twoHalfShiftXCLM cliffordX τx vx,
      directionalShiftCLM cliffordX τx ux)
    (mFine₁, mCoarse₁)

/-- The five spatial local operator defects, retaining both repeated `x` and
`y` factors of the palindromic walk. -/
def straightSpatialBudget
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) (r : PhaseFrame Site)
    (vx vy vz : Link (Site := FineSite3 Site)) : ℝ :=
  ‖straightDefectOpX cliffordX τx ux r vx‖ +
  ‖straightDefectOpY cliffordY τy uy r vy‖ +
  ‖straightDefectOpZ cliffordZ τz uz r vz‖ +
  ‖straightDefectOpY cliffordY τy uy r vy‖ +
  ‖straightDefectOpX cliffordX τx ux r vx‖

/-- The complete seven-factor straight-refinement defect is bounded by the five
actual spatial operator defects when the two mass factors intertwine exactly. -/
theorem norm_straightSevenFactorDefect_le
    (mFine₀ mFine₁ : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (mCoarse₀ mCoarse₁ : State (Site := Site) →L[ℂ]
      State (Site := Site))
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) (r : PhaseFrame Site)
    (vx vy vz : Link (Site := FineSite3 Site))
    (hFine : ∀ p ∈ straightSevenFactorPairs mFine₀ mFine₁
      mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ straightSevenFactorPairs mFine₀ mFine₁
      mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz, ‖p.2‖ ≤ 1)
    (hm₀ : intertwiningDefectOp mFine₀ (frameEmbedCLM r) mCoarse₀ = 0)
    (hm₁ : intertwiningDefectOp mFine₁ (frameEmbedCLM r) mCoarse₁ = 0) :
    ‖intertwiningDefectOp
        (fineComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz))
        (frameEmbedCLM r)
        (coarseComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz))‖ ≤
      straightSpatialBudget τx τy τz ux uy uz r vx vy vz := by
  simpa [straightSevenFactorPairs, straightSpatialBudget,
    straightDefectOpX, straightDefectOpY, straightDefectOpZ] using
    norm_sevenFactorDefect_le_five
      (frameEmbedCLM r)
      (mFine₀, mCoarse₀)
      (twoHalfShiftXCLM cliffordX τx vx,
        directionalShiftCLM cliffordX τx ux)
      (twoHalfShiftYCLM cliffordY τy vy,
        directionalShiftCLM cliffordY τy uy)
      (twoHalfShiftZCLM cliffordZ τz vz,
        directionalShiftCLM cliffordZ τz uz)
      (twoHalfShiftYCLM cliffordY τy vy,
        directionalShiftCLM cliffordY τy uy)
      (twoHalfShiftXCLM cliffordX τx vx,
        directionalShiftCLM cliffordX τx ux)
      (mFine₁, mCoarse₁) hFine hCoarse hm₀ hm₁

/-- Exact straight reconstruction of all three directions makes the complete
seven-factor operator defect vanish, without any flatness hypothesis. -/
theorem straightSevenFactorDefect_eq_zero
    (mFine₀ mFine₁ : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (mCoarse₀ mCoarse₁ : State (Site := Site) →L[ℂ]
      State (Site := Site))
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) (r : PhaseFrame Site)
    (vx vy vz : Link (Site := FineSite3 Site))
    (hm₀ : intertwiningDefectOp mFine₀ (frameEmbedCLM r) mCoarse₀ = 0)
    (hm₁ : intertwiningDefectOp mFine₁ (frameEmbedCLM r) mCoarse₁ = 0)
    (hx : StraightCompatibleX τx ux r vx)
    (hy : StraightCompatibleY τy uy r vy)
    (hz : StraightCompatibleZ τz uz r vz) :
    intertwiningDefectOp
        (fineComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz))
        (frameEmbedCLM r)
        (coarseComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz)) = 0 := by
  apply fullDefect_eq_zero_of_local
  intro p hp
  simp [straightSevenFactorPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact hm₀
  · simpa [straightDefectOpX] using
      straightDefectOpX_eq_zero cliffordX τx ux r vx hx
  · simpa [straightDefectOpY] using
      straightDefectOpY_eq_zero cliffordY τy uy r vy hy
  · simpa [straightDefectOpZ] using
      straightDefectOpZ_eq_zero cliffordZ τz uz r vz hz
  · simpa [straightDefectOpY] using
      straightDefectOpY_eq_zero cliffordY τy uy r vy hy
  · simpa [straightDefectOpX] using
      straightDefectOpX_eq_zero cliffordX τx ux r vx hx
  · exact hm₁

end StraightSevenFactor

/-! ## Explicit straight-edge reconstruction ratios -/

section ReconstructionRatios

variable {Site : Type u}

/-- Multiplicative `x` reconstruction error.  It is one exactly when the two
ordered fine half-links reconstruct the framed coarse link. -/
def edgeRatioX (τ : Site ≃ Site) (u : Link (Site := Site))
    (r : PhaseFrame Site) (v : Link (Site := FineSite3 Site))
    (p : FineSite3 Site) : Circle :=
  v (halfShiftX τ p) * v p * (targetProductX τ u r p)⁻¹

/-- Multiplicative `y` reconstruction error. -/
def edgeRatioY (τ : Site ≃ Site) (u : Link (Site := Site))
    (r : PhaseFrame Site) (v : Link (Site := FineSite3 Site))
    (p : FineSite3 Site) : Circle :=
  v (halfShiftY τ p) * v p * (targetProductY τ u r p)⁻¹

/-- Multiplicative `z` reconstruction error. -/
def edgeRatioZ (τ : Site ≃ Site) (u : Link (Site := Site))
    (r : PhaseFrame Site) (v : Link (Site := FineSite3 Site))
    (p : FineSite3 Site) : Circle :=
  v (halfShiftZ τ p) * v p * (targetProductZ τ u r p)⁻¹

@[simp] theorem edgeRatioX_eq_one_iff (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) (p : FineSite3 Site) :
    edgeRatioX τ u r v p = 1 ↔
      v (halfShiftX τ p) * v p = targetProductX τ u r p := by
  simpa [edgeRatioX] using
    (mul_inv_eq_one :
      (v (halfShiftX τ p) * v p) * (targetProductX τ u r p)⁻¹ = 1 ↔
        v (halfShiftX τ p) * v p = targetProductX τ u r p)

@[simp] theorem edgeRatioY_eq_one_iff (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) (p : FineSite3 Site) :
    edgeRatioY τ u r v p = 1 ↔
      v (halfShiftY τ p) * v p = targetProductY τ u r p := by
  simpa [edgeRatioY] using
    (mul_inv_eq_one :
      (v (halfShiftY τ p) * v p) * (targetProductY τ u r p)⁻¹ = 1 ↔
        v (halfShiftY τ p) * v p = targetProductY τ u r p)

@[simp] theorem edgeRatioZ_eq_one_iff (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) (p : FineSite3 Site) :
    edgeRatioZ τ u r v p = 1 ↔
      v (halfShiftZ τ p) * v p = targetProductZ τ u r p := by
  simpa [edgeRatioZ] using
    (mul_inv_eq_one :
      (v (halfShiftZ τ p) * v p) * (targetProductZ τ u r p)⁻¹ = 1 ↔
        v (halfShiftZ τ p) * v p = targetProductZ τ u r p)

theorem straightCompatibleX_iff_ratios_one (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) :
    StraightCompatibleX τ u r v ↔ ∀ p, edgeRatioX τ u r v p = 1 := by
  constructor
  · intro h p
    exact (edgeRatioX_eq_one_iff τ u r v p).2 (h p)
  · intro h p
    exact (edgeRatioX_eq_one_iff τ u r v p).1 (h p)

theorem straightCompatibleY_iff_ratios_one (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) :
    StraightCompatibleY τ u r v ↔ ∀ p, edgeRatioY τ u r v p = 1 := by
  constructor
  · intro h p
    exact (edgeRatioY_eq_one_iff τ u r v p).2 (h p)
  · intro h p
    exact (edgeRatioY_eq_one_iff τ u r v p).1 (h p)

theorem straightCompatibleZ_iff_ratios_one (τ : Site ≃ Site)
    (u : Link (Site := Site)) (r : PhaseFrame Site)
    (v : Link (Site := FineSite3 Site)) :
    StraightCompatibleZ τ u r v ↔ ∀ p, edgeRatioZ τ u r v p = 1 := by
  constructor
  · intro h p
    exact (edgeRatioZ_eq_one_iff τ u r v p).2 (h p)
  · intro h p
    exact (edgeRatioZ_eq_one_iff τ u r v p).1 (h p)

end ReconstructionRatios

/-! ## Independent straight and curvature budgets -/

section TwoBudgetOperatorCalculus

variable {X : Type u} {Y : Type v}
variable [NormedAddCommGroup X] [NormedSpace ℂ X]
variable [NormedAddCommGroup Y] [NormedSpace ℂ Y]

/-- Two-stage defect estimate.  The first stage may represent straight-edge
reconstruction; the second may represent path reordering or cubical gluing. -/
theorem norm_twoStageDefect_le
    (Fedge Fglue : Y →L[ℂ] Y) (I : X →L[ℂ] Y)
    (Cedge Cglue : X →L[ℂ] X)
    (hFglue : ‖Fglue‖ ≤ 1) (hCedge : ‖Cedge‖ ≤ 1)
    {εedge εcurv : ℝ}
    (hedge : ‖intertwiningDefectOp Fedge I Cedge‖ ≤ εedge)
    (hcurv : ‖intertwiningDefectOp Fglue I Cglue‖ ≤ εcurv) :
    ‖intertwiningDefectOp (Fglue.comp Fedge) I
        (Cglue.comp Cedge)‖ ≤ εedge + εcurv := by
  have hεedge : 0 ≤ εedge := le_trans (norm_nonneg _) hedge
  have hεcurv : 0 ≤ εcurv := le_trans (norm_nonneg _) hcurv
  calc
    ‖intertwiningDefectOp (Fglue.comp Fedge) I
        (Cglue.comp Cedge)‖
      ≤ ‖Fglue‖ * ‖intertwiningDefectOp Fedge I Cedge‖ +
          ‖intertwiningDefectOp Fglue I Cglue‖ * ‖Cedge‖ :=
        norm_intertwiningDefectOp_comp_le Fedge Fglue I Cedge Cglue
    _ ≤ 1 * εedge + εcurv * 1 := by gcongr
    _ = εedge + εcurv := by ring

/-- Exact independence statement: if both stages intertwine exactly, their
composition intertwines exactly. -/
theorem twoStageDefect_eq_zero
    (Fedge Fglue : Y →L[ℂ] Y) (I : X →L[ℂ] Y)
    (Cedge Cglue : X →L[ℂ] X)
    (hedge : intertwiningDefectOp Fedge I Cedge = 0)
    (hcurv : intertwiningDefectOp Fglue I Cglue = 0) :
    intertwiningDefectOp (Fglue.comp Fedge) I
      (Cglue.comp Cedge) = 0 := by
  rw [intertwiningDefectOp_comp, hedge, hcurv]
  simp

/-- The five independent plaquette amplitudes used by the cubical swap
comparison. -/
def curvatureBudget (L : CubeLinks) : ℝ :=
  ‖(L.plaquetteXY false : ℂ) - 1‖ +
  ‖(L.plaquetteXZ true : ℂ) - 1‖ +
  ‖(L.plaquetteYZ false : ℂ) - 1‖ +
  ‖(L.plaquetteYZ true : ℂ) - 1‖ +
  ‖(L.plaquetteXZ false : ℂ) - 1‖

/-- The checked cubical path-swap operator is controlled by the explicitly
separate curvature budget. -/
theorem norm_cubeSwapDefect_le_curvatureBudget (L : CubeLinks) :
    ‖intertwiningDefectOp
        (fineComposite (cubeSwapSevenPairs L))
        (ContinuousLinearMap.id ℂ Spinor)
        (coarseComposite (cubeSwapSevenPairs L))‖ ≤ curvatureBudget L := by
  simpa [curvatureBudget] using norm_cubeSwapSevenDefect_le_curvatureBudget L

/-- The full state-space seven-factor straight stage followed by an
arbitrary gluing stage is controlled by the sum of the straight spatial budget
and the independently supplied cubical curvature budget. -/
theorem norm_straightSeven_then_gluing_le
    {Site : Type u} [Fintype Site]
    (mFine₀ mFine₁ : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (mCoarse₀ mCoarse₁ : State (Site := Site) →L[ℂ]
      State (Site := Site))
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) (r : PhaseFrame Site)
    (vx vy vz : Link (Site := FineSite3 Site))
    (Fglue : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (Cglue : State (Site := Site) →L[ℂ] State (Site := Site))
    (L : CubeLinks)
    (hFine : ∀ p ∈ straightSevenFactorPairs mFine₀ mFine₁
      mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ straightSevenFactorPairs mFine₀ mFine₁
      mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz, ‖p.2‖ ≤ 1)
    (hm₀ : intertwiningDefectOp mFine₀ (frameEmbedCLM r) mCoarse₀ = 0)
    (hm₁ : intertwiningDefectOp mFine₁ (frameEmbedCLM r) mCoarse₁ = 0)
    (hFglue : ‖Fglue‖ ≤ 1)
    (hGlue : ‖intertwiningDefectOp Fglue (frameEmbedCLM r) Cglue‖ ≤
      curvatureBudget L) :
    ‖intertwiningDefectOp
        (Fglue.comp (fineComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz)))
        (frameEmbedCLM r)
        (Cglue.comp (coarseComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz)))‖ ≤
      straightSpatialBudget τx τy τz ux uy uz r vx vy vz +
        curvatureBudget L := by
  have hEdge := norm_straightSevenFactorDefect_le
    mFine₀ mFine₁ mCoarse₀ mCoarse₁ τx τy τz ux uy uz r vx vy vz
    hFine hCoarse hm₀ hm₁
  have hCoarseComposite :
      ‖coarseComposite (straightSevenFactorPairs mFine₀ mFine₁
        mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz)‖ ≤ 1 := by
    apply norm_composeOps_le_one
    intro C hC
    rcases List.mem_map.mp hC with ⟨p, hp, rfl⟩
    exact hCoarse p hp
  exact norm_twoStageDefect_le
    (fineComposite (straightSevenFactorPairs mFine₀ mFine₁
      mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz))
    Fglue (frameEmbedCLM r)
    (coarseComposite (straightSevenFactorPairs mFine₀ mFine₁
      mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz))
    Cglue hFglue hCoarseComposite hEdge hGlue

/-- Exact state-space composition: straight compatibility and an exact gluing
stage together give exact full intertwining. -/
theorem straightSeven_then_gluing_eq_zero
    {Site : Type u} [Fintype Site]
    (mFine₀ mFine₁ : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (mCoarse₀ mCoarse₁ : State (Site := Site) →L[ℂ]
      State (Site := Site))
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) (r : PhaseFrame Site)
    (vx vy vz : Link (Site := FineSite3 Site))
    (Fglue : State (Site := FineSite3 Site) →L[ℂ]
      State (Site := FineSite3 Site))
    (Cglue : State (Site := Site) →L[ℂ] State (Site := Site))
    (hm₀ : intertwiningDefectOp mFine₀ (frameEmbedCLM r) mCoarse₀ = 0)
    (hm₁ : intertwiningDefectOp mFine₁ (frameEmbedCLM r) mCoarse₁ = 0)
    (hx : StraightCompatibleX τx ux r vx)
    (hy : StraightCompatibleY τy uy r vy)
    (hz : StraightCompatibleZ τz uz r vz)
    (hGlue : intertwiningDefectOp Fglue (frameEmbedCLM r) Cglue = 0) :
    intertwiningDefectOp
        (Fglue.comp (fineComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz)))
        (frameEmbedCLM r)
        (Cglue.comp (coarseComposite (straightSevenFactorPairs mFine₀ mFine₁
          mCoarse₀ mCoarse₁ τx τy τz ux uy uz vx vy vz))) = 0 := by
  apply twoStageDefect_eq_zero
  · exact straightSevenFactorDefect_eq_zero
      mFine₀ mFine₁ mCoarse₀ mCoarse₁ τx τy τz ux uy uz r vx vy vz
      hm₀ hm₁ hx hy hz
  · exact hGlue

/-- Flat cubical data has zero curvature budget. -/
@[simp] theorem curvatureBudget_eq_zero_of_flat (L : CubeLinks) (h : L.Flat) :
    curvatureBudget L = 0 := by
  rcases h with ⟨hxy, hxz, hyz⟩
  simp [curvatureBudget, hxy, hxz, hyz]

/-- A concrete local-fiber model combining arbitrary straight-factor pairs with
the checked cubical path-swap stage. -/
def combinedFiberFine
    (edgePairs : List ((Spinor →L[ℂ] Spinor) × (Spinor →L[ℂ] Spinor)))
    (L : CubeLinks) : Spinor →L[ℂ] Spinor :=
  (fineComposite (cubeSwapSevenPairs L)).comp (fineComposite edgePairs)

/-- Coarse comparison operator for the two-stage local-fiber model. -/
def combinedFiberCoarse
    (edgePairs : List ((Spinor →L[ℂ] Spinor) × (Spinor →L[ℂ] Spinor)))
    (L : CubeLinks) : Spinor →L[ℂ] Spinor :=
  (coarseComposite (cubeSwapSevenPairs L)).comp (coarseComposite edgePairs)

/-- Concrete two-budget estimate: arbitrary straight-factor defects and
plaquette path defects enter additively and remain logically independent. -/
theorem norm_combinedFiberDefect_le
    (edgePairs : List ((Spinor →L[ℂ] Spinor) × (Spinor →L[ℂ] Spinor)))
    (L : CubeLinks)
    (hFine : ∀ p ∈ edgePairs, ‖p.1‖ ≤ 1)
    (hCoarse : ∀ p ∈ edgePairs, ‖p.2‖ ≤ 1) :
    ‖intertwiningDefectOp (combinedFiberFine edgePairs L)
        (ContinuousLinearMap.id ℂ Spinor)
        (combinedFiberCoarse edgePairs L)‖ ≤
      defectBudget (ContinuousLinearMap.id ℂ Spinor) edgePairs +
        curvatureBudget L := by
  have hEdge := norm_fullDefect_le_budget
    (ContinuousLinearMap.id ℂ Spinor) edgePairs hFine hCoarse
  have hGlue := norm_cubeSwapDefect_le_curvatureBudget L
  have hGlueFine : ‖fineComposite (cubeSwapSevenPairs L)‖ ≤ 1 := by
    apply norm_composeOps_le_one
    intro F hF
    rcases List.mem_map.mp hF with ⟨p, hp, rfl⟩
    simp [cubeSwapSevenPairs, sevenFactorPairs] at hp
    rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> simp
  have hEdgeCoarse : ‖coarseComposite edgePairs‖ ≤ 1 := by
    apply norm_composeOps_le_one
    intro C hC
    rcases List.mem_map.mp hC with ⟨p, hp, rfl⟩
    exact hCoarse p hp
  exact norm_twoStageDefect_le
    (fineComposite edgePairs) (fineComposite (cubeSwapSevenPairs L))
    (ContinuousLinearMap.id ℂ Spinor)
    (coarseComposite edgePairs) (coarseComposite (cubeSwapSevenPairs L))
    hGlueFine hEdgeCoarse hEdge hGlue

/-- Exact zero-defect sector: local straight factors intertwine and cubical
paths are flat.  Neither condition is used as a surrogate for the other. -/
theorem combinedFiberDefect_eq_zero
    (edgePairs : List ((Spinor →L[ℂ] Spinor) × (Spinor →L[ℂ] Spinor)))
    (L : CubeLinks)
    (hEdge : ∀ p ∈ edgePairs,
      intertwiningDefectOp p.1 (ContinuousLinearMap.id ℂ Spinor) p.2 = 0)
    (hFlat : L.Flat) :
    intertwiningDefectOp (combinedFiberFine edgePairs L)
      (ContinuousLinearMap.id ℂ Spinor)
      (combinedFiberCoarse edgePairs L) = 0 := by
  apply twoStageDefect_eq_zero
  · exact fullDefect_eq_zero_of_local
      (ContinuousLinearMap.id ℂ Spinor) edgePairs hEdge
  · exact cubeSwapSevenDefect_eq_zero_of_flat L hFlat

end TwoBudgetOperatorCalculus

/-! ## Summable two-budget bridge to the global continuum theorem -/

section SummableBudgets

/-- Adjacent-scale budget with independent straight-edge and curvature parts. -/
def combinedScaleBudget (edge curvature : ℕ → ℝ) (n : ℕ) : ℝ :=
  edge n + curvature n

/-- Separate summability of the two physical defect channels implies
summability of their combined local refinement budget. -/
theorem summable_combinedScaleBudget {edge curvature : ℕ → ℝ}
    (hedge : Summable edge) (hcurvature : Summable curvature) :
    Summable (combinedScaleBudget edge curvature) := by
  exact hedge.add hcurvature

variable {Y : Type v} [MetricSpace Y]

/-- Build a global-limit defect certificate from separately summable edge and
curvature budgets. -/
def twoBudgetSummableDefect (f : ℕ → Y)
    (edge curvature : ℕ → ℝ)
    (hedge : Summable edge) (hcurvature : Summable curvature)
    (hstep : ∀ n, dist (f n) (f n.succ) ≤
      combinedScaleBudget edge curvature n) : SummableDefect f where
  bound := combinedScaleBudget edge curvature
  summable_bound := summable_combinedScaleBudget hedge hcurvature
  step_le := hstep

variable [CompleteSpace Y]

/-- The two-budget finite-resolution hierarchy converges to a single global
state whenever both defect channels are summable. -/
theorem tendsto_twoBudgetLimit (f : ℕ → Y)
    (edge curvature : ℕ → ℝ)
    (hedge : Summable edge) (hcurvature : Summable curvature)
    (hstep : ∀ n, dist (f n) (f n.succ) ≤
      combinedScaleBudget edge curvature n) :
    Tendsto f atTop
      (𝓝 ((twoBudgetSummableDefect f edge curvature
        hedge hcurvature hstep).limit)) :=
  (twoBudgetSummableDefect f edge curvature hedge hcurvature hstep).tendsto_limit

/-- Quantitative tail estimate for the global state obtained from the two
independent local budgets. -/
theorem dist_twoBudgetLimit_le_tail (f : ℕ → Y)
    (edge curvature : ℕ → ℝ)
    (hedge : Summable edge) (hcurvature : Summable curvature)
    (hstep : ∀ n, dist (f n) (f n.succ) ≤
      combinedScaleBudget edge curvature n) (n : ℕ) :
    dist (f n)
      ((twoBudgetSummableDefect f edge curvature
        hedge hcurvature hstep).limit) ≤
      ∑' m : ℕ, combinedScaleBudget edge curvature (n + m) :=
  (twoBudgetSummableDefect f edge curvature
    hedge hcurvature hstep).dist_limit_le_tail n

end SummableBudgets

end Relativistic3DCombinedDefect
end KomorebiPhysics
