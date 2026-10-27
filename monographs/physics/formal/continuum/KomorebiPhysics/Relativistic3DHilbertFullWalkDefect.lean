module

public import KomorebiPhysics.Relativistic3DHilbertScalarDefect

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ComplexConjugate Topology
open WithLp Filter

namespace KomorebiPhysics
namespace Relativistic3DHilbertFullWalkDefect

open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DCubicalRefinement
open Relativistic3DFullWalkRefinement
open Relativistic3DEdgeCompatibility
open Relativistic3DCombinedDefect
open Relativistic3DHilbertScalarDefect

universe u

/-! ## Hilbert realization of a single directional Clifford shift -/

/-- A link-coupled Clifford shift acting on the genuine finite Euclidean
`ℓ²` realization. -/
def directionalShiftHilbertLinear {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    HilbertState Site →ₗ[ℂ] HilbertState Site :=
  stateHilbertEquiv.toLinearMap.comp
    ((directionalShiftCLM A τ u).toLinearMap.comp
      stateHilbertEquiv.symm.toLinearMap)

/-- Continuous Hilbert-space realization of a directional Clifford shift. -/
def directionalShiftHilbertCLM {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  LinearMap.toContinuousLinearMap (directionalShiftHilbertLinear A τ u)

@[simp] theorem directionalShiftHilbertCLM_apply
    {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : HilbertState Site) :
    directionalShiftHilbertCLM A τ u ψ =
      stateToHilbert (directionalShift A τ u (hilbertToState ψ)) := by
  rfl

/-- Every unit-circle Clifford shift is an exact Hilbert isometry. -/
theorem directionalShiftHilbertCLM_norm_eq
    {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : HilbertState Site) :
    ‖directionalShiftHilbertCLM H.toClifford τ u ψ‖ = ‖ψ‖ := by
  apply (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  rw [directionalShiftHilbertCLM_apply, stateToHilbert_norm_sq]
  rw [directionalShift_stateIP]
  exact hilbertToState_stateIP_re ψ

/-- Directional Clifford shifts are contractive in operator norm. -/
theorem directionalShiftHilbertCLM_opNorm_le_one
    {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    ‖directionalShiftHilbertCLM H.toClifford τ u‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ (by norm_num)
  intro ψ
  rw [directionalShiftHilbertCLM_norm_eq H τ u]
  simp

/-- With the identity embedding, the local intertwining defect is exactly the
Hilbert shift-difference operator from Block 31. -/
@[simp] theorem intertwiningDefectOp_directionalShiftHilbert_id
    {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) :
    intertwiningDefectOp
      (directionalShiftHilbertCLM A τ v)
      (ContinuousLinearMap.id ℂ (HilbertState Site))
      (directionalShiftHilbertCLM A τ u) =
    directionalShiftDefectHilbertCLM A τ v u := by
  apply ContinuousLinearMap.ext
  intro ψ
  rfl

/-- Ratio form of the sharp one-direction Hilbert operator estimate. -/
theorem directionalShiftHilbertDefect_opNorm_le_ratioSup
    {Site : Type u} [Fintype Site] [Nonempty Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) :
    ‖intertwiningDefectOp
      (directionalShiftHilbertCLM H.toClifford τ v)
      (ContinuousLinearMap.id ℂ (HilbertState Site))
      (directionalShiftHilbertCLM H.toClifford τ u)‖ ≤
      edgeRatioSup v u := by
  rw [intertwiningDefectOp_directionalShiftHilbert_id]
  rw [← edgeMismatchSup_eq_edgeRatioSup]
  exact directionalShiftDefectHilbertCLM_opNorm_le_sup H τ v u


/-! ## Complete palindromic Hilbert walk -/

section HilbertSevenFactor

variable {Site : Type u} [Fintype Site] [Nonempty Site]

/-- Fine/coarse Hilbert factor pairs for the physical order
`M-X-Y-Z-Y-X-M`.  The same two mass operators occur on both sides; only the
three link fields may differ. -/
def hilbertSevenFactorPairs
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site)) :
    List ((HilbertState Site →L[ℂ] HilbertState Site) ×
      (HilbertState Site →L[ℂ] HilbertState Site)) :=
  sevenFactorPairs
    (m₀, m₀)
    (directionalShiftHilbertCLM cliffordX τx vx,
      directionalShiftHilbertCLM cliffordX τx ux)
    (directionalShiftHilbertCLM cliffordY τy vy,
      directionalShiftHilbertCLM cliffordY τy uy)
    (directionalShiftHilbertCLM cliffordZ τz vz,
      directionalShiftHilbertCLM cliffordZ τz uz)
    (directionalShiftHilbertCLM cliffordY τy vy,
      directionalShiftHilbertCLM cliffordY τy uy)
    (directionalShiftHilbertCLM cliffordX τx vx,
      directionalShiftHilbertCLM cliffordX τx ux)
    (m₁, m₁)

/-- Scalar straight-edge budget with the multiplicities forced by the
palindromic factor order. -/
def hilbertEdgeBudget
    (vx vy vz ux uy uz : Link (Site := Site)) : ℝ :=
  2 * edgeRatioSup vx ux + 2 * edgeRatioSup vy uy + edgeRatioSup vz uz

/-- The complete effective fine Hilbert walk. -/
def fineHilbertWalk
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz : Link (Site := Site)) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  fineComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
    vx vy vz vx vy vz)

/-- The complete prescribed coarse Hilbert walk. -/
def coarseHilbertWalk
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  coarseComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
    ux uy uz ux uy uz)

/-- The actual two-walk comparison using reconstructed links on the fine side
and prescribed links on the coarse side. -/
def hilbertSevenFactorDefect
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site)) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  intertwiningDefectOp
    (fineComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz))
    (ContinuousLinearMap.id ℂ (HilbertState Site))
    (coarseComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz))

omit [Nonempty Site] in
/-- Every factor on the effective fine side is contractive when the two mass
operators are contractive. -/
theorem hilbertSevenFactorPairs_fine_contractive
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (hm₀ : ‖m₀‖ ≤ 1) (hm₁ : ‖m₁‖ ≤ 1) :
    ∀ p ∈ hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz, ‖p.1‖ ≤ 1 := by
  intro p hp
  simp [hilbertSevenFactorPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact hm₀
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianX τx vx
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianY τy vy
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianZ τz vz
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianY τy vy
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianX τx vx
  · exact hm₁

omit [Nonempty Site] in
/-- Every prescribed coarse factor is contractive under the same mass
hypotheses. -/
theorem hilbertSevenFactorPairs_coarse_contractive
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (hm₀ : ‖m₀‖ ≤ 1) (hm₁ : ‖m₁‖ ≤ 1) :
    ∀ p ∈ hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz, ‖p.2‖ ≤ 1 := by
  intro p hp
  simp [hilbertSevenFactorPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · exact hm₀
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianX τx ux
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianY τy uy
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianZ τz uz
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianY τy uy
  · exact directionalShiftHilbertCLM_opNorm_le_one hermitianX τx ux
  · exact hm₁

omit [Nonempty Site] in
@[simp] theorem mass_intertwiningDefect_id
    (m : HilbertState Site →L[ℂ] HilbertState Site) :
    intertwiningDefectOp m
      (ContinuousLinearMap.id ℂ (HilbertState Site)) m = 0 := by
  ext ψ
  simp [intertwiningDefectOp]

/-- Main Block 32 straight-edge theorem: the full palindromic walk has the
sharp repeated-factor scalar budget `2δx + 2δy + δz`. -/
theorem norm_hilbertSevenFactorDefect_le_edgeBudget
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (hm₀ : ‖m₀‖ ≤ 1) (hm₁ : ‖m₁‖ ≤ 1) :
    ‖hilbertSevenFactorDefect m₀ m₁ τx τy τz
      vx vy vz ux uy uz‖ ≤
      hilbertEdgeBudget vx vy vz ux uy uz := by
  have h := norm_sevenFactorDefect_le_curvatureBudget
    (ContinuousLinearMap.id ℂ (HilbertState Site))
    (m₀, m₀)
    (directionalShiftHilbertCLM cliffordX τx vx,
      directionalShiftHilbertCLM cliffordX τx ux)
    (directionalShiftHilbertCLM cliffordY τy vy,
      directionalShiftHilbertCLM cliffordY τy uy)
    (directionalShiftHilbertCLM cliffordZ τz vz,
      directionalShiftHilbertCLM cliffordZ τz uz)
    (directionalShiftHilbertCLM cliffordY τy vy,
      directionalShiftHilbertCLM cliffordY τy uy)
    (directionalShiftHilbertCLM cliffordX τx vx,
      directionalShiftHilbertCLM cliffordX τx ux)
    (m₁, m₁)
    (edgeRatioSup vx ux) (edgeRatioSup vy uy) (edgeRatioSup vz uz)
    (edgeRatioSup vy uy) (edgeRatioSup vx ux)
    (hilbertSevenFactorPairs_fine_contractive m₀ m₁ τx τy τz
      vx vy vz ux uy uz hm₀ hm₁)
    (hilbertSevenFactorPairs_coarse_contractive m₀ m₁ τx τy τz
      vx vy vz ux uy uz hm₀ hm₁)
    (mass_intertwiningDefect_id m₀)
    (mass_intertwiningDefect_id m₁)
    (directionalShiftHilbertDefect_opNorm_le_ratioSup hermitianX τx vx ux)
    (directionalShiftHilbertDefect_opNorm_le_ratioSup hermitianY τy vy uy)
    (directionalShiftHilbertDefect_opNorm_le_ratioSup hermitianZ τz vz uz)
    (directionalShiftHilbertDefect_opNorm_le_ratioSup hermitianY τy vy uy)
    (directionalShiftHilbertDefect_opNorm_le_ratioSup hermitianX τx vx ux)
  change ‖hilbertSevenFactorDefect m₀ m₁ τx τy τz
      vx vy vz ux uy uz‖ ≤ _ at h
  calc
    ‖hilbertSevenFactorDefect m₀ m₁ τx τy τz
      vx vy vz ux uy uz‖ ≤
        edgeRatioSup vx ux + edgeRatioSup vy uy + edgeRatioSup vz uz +
          edgeRatioSup vy uy + edgeRatioSup vx ux := h
    _ = hilbertEdgeBudget vx vy vz ux uy uz := by
      simp [hilbertEdgeBudget]
      ring

/-- A mismatch of size two in the repeated `x` factor contributes four to the
full palindromic edge budget. -/
@[simp] theorem quarterX_hilbertEdgeBudget :
    hilbertEdgeBudget
      (quarterPair PUnit).productLink (fun _ => 1) (fun _ => 1)
      (fun _ => 1) (fun _ => 1) (fun _ => 1) = 4 := by
  rw [hilbertEdgeBudget, quarterPair_edgeRatioSup]
  simp [edgeRatioSup, edgeRatio]
  norm_num

omit [Nonempty Site] in
/-- Exact equality of all reconstructed and prescribed links annihilates the
full Hilbert walk defect. -/
theorem hilbertSevenFactorDefect_eq_zero_of_links
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site)) :
    hilbertSevenFactorDefect m₀ m₁ τx τy τz
      ux uy uz ux uy uz = 0 := by
  apply fullDefect_eq_zero_of_local
  intro p hp
  simp [hilbertSevenFactorPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals simp [intertwiningDefectOp]

end HilbertSevenFactor


/-! ## Cubical gluing on the finite Hilbert state space -/

section HilbertCurvature

variable {Site : Type u} [Fintype Site] [Nonempty Site]

/-- Uniform unit-circle phase transport on the full finite Hilbert state. -/
def hilbertPhaseOp (z : Circle) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  (z : ℂ) • ContinuousLinearMap.id ℂ (HilbertState Site)

omit [Nonempty Site] in
@[simp] theorem hilbertPhaseOp_apply (z : Circle) (ψ : HilbertState Site) :
    hilbertPhaseOp (Site := Site) z ψ = (z : ℂ) • ψ := by
  rfl

/-- Uniform phase transport is unitary. -/
@[simp] theorem norm_hilbertPhaseOp (z : Circle) :
    ‖hilbertPhaseOp (Site := Site) z‖ = 1 := by
  rw [hilbertPhaseOp, norm_smul, ContinuousLinearMap.norm_id, Circle.norm_coe]
  norm_num

/-- Hilbert operator difference between two parallel cubical paths. -/
def hilbertPhaseDefectOp (p q : Circle) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  hilbertPhaseOp (Site := Site) p - hilbertPhaseOp (Site := Site) q

omit [Nonempty Site] in
@[simp] theorem intertwiningDefectOp_hilbertPhase_id (p q : Circle) :
    intertwiningDefectOp
      (hilbertPhaseOp (Site := Site) p)
      (ContinuousLinearMap.id ℂ (HilbertState Site))
      (hilbertPhaseOp (Site := Site) q) =
    hilbertPhaseDefectOp (Site := Site) p q := by
  ext ψ
  simp [intertwiningDefectOp, hilbertPhaseDefectOp, hilbertPhaseOp]

omit [Nonempty Site] in
/-- The Hilbert path defect is scalar multiplication by the phase difference. -/
theorem hilbertPhaseDefectOp_eq_smul_id (p q : Circle) :
    hilbertPhaseDefectOp (Site := Site) p q =
      ((p : ℂ) - (q : ℂ)) •
        ContinuousLinearMap.id ℂ (HilbertState Site) := by
  ext ψ
  simp [hilbertPhaseDefectOp, hilbertPhaseOp, sub_smul]

/-- Exact Hilbert operator norm of a curvature-controlled path defect. -/
theorem norm_hilbertPhaseDefectOp_eq_curvature
    (p q Ω : Circle) (h : p = Ω * q) :
    ‖hilbertPhaseDefectOp (Site := Site) p q‖ =
      ‖(Ω : ℂ) - 1‖ := by
  subst p
  rw [hilbertPhaseDefectOp_eq_smul_id]
  rw [norm_smul, ContinuousLinearMap.norm_id]
  have hfactor : ((↑(Ω * q) : ℂ) - (q : ℂ)) =
      (q : ℂ) * ((Ω : ℂ) - 1) := by
    push_cast
    ring
  rw [hfactor, norm_mul, Circle.norm_coe, one_mul, mul_one]

@[simp] theorem norm_hilbertDefect_XYZ_YXZ (L : CubeLinks) :
    ‖hilbertPhaseDefectOp (Site := Site) L.pathXYZ L.pathYXZ‖ =
      ‖(L.plaquetteXY false : ℂ) - 1‖ := by
  exact norm_hilbertPhaseDefectOp_eq_curvature _ _ _
    L.pathXYZ_eq_xy0_mul_pathYXZ

@[simp] theorem norm_hilbertDefect_XYZ_XZY (L : CubeLinks) :
    ‖hilbertPhaseDefectOp (Site := Site) L.pathXYZ L.pathXZY‖ =
      ‖(L.plaquetteYZ true : ℂ) - 1‖ := by
  exact norm_hilbertPhaseDefectOp_eq_curvature _ _ _
    L.pathXYZ_eq_yz1_mul_pathXZY

@[simp] theorem norm_hilbertDefect_XZY_ZXY (L : CubeLinks) :
    ‖hilbertPhaseDefectOp (Site := Site) L.pathXZY L.pathZXY‖ =
      ‖(L.plaquetteXZ false : ℂ) - 1‖ := by
  exact norm_hilbertPhaseDefectOp_eq_curvature _ _ _
    L.pathXZY_eq_xz0_mul_pathZXY

@[simp] theorem norm_hilbertDefect_YXZ_YZX (L : CubeLinks) :
    ‖hilbertPhaseDefectOp (Site := Site) L.pathYXZ L.pathYZX‖ =
      ‖(L.plaquetteXZ true : ℂ) - 1‖ := by
  exact norm_hilbertPhaseDefectOp_eq_curvature _ _ _
    L.pathYXZ_eq_xz1_mul_pathYZX

@[simp] theorem norm_hilbertDefect_YZX_ZYX (L : CubeLinks) :
    ‖hilbertPhaseDefectOp (Site := Site) L.pathYZX L.pathZYX‖ =
      ‖(L.plaquetteYZ false : ℂ) - 1‖ := by
  exact norm_hilbertPhaseDefectOp_eq_curvature _ _ _
    L.pathYZX_eq_yz0_mul_pathZYX

/-- Seven Hilbert factor pairs implementing the five independent cubical path
swaps; the first and last factors are identities. -/
def hilbertCubeSwapSevenPairs (L : CubeLinks) :
    List ((HilbertState Site →L[ℂ] HilbertState Site) ×
      (HilbertState Site →L[ℂ] HilbertState Site)) :=
  sevenFactorPairs
    (ContinuousLinearMap.id ℂ (HilbertState Site),
      ContinuousLinearMap.id ℂ (HilbertState Site))
    (hilbertPhaseOp (Site := Site) L.pathXYZ,
      hilbertPhaseOp (Site := Site) L.pathYXZ)
    (hilbertPhaseOp (Site := Site) L.pathYXZ,
      hilbertPhaseOp (Site := Site) L.pathYZX)
    (hilbertPhaseOp (Site := Site) L.pathYZX,
      hilbertPhaseOp (Site := Site) L.pathZYX)
    (hilbertPhaseOp (Site := Site) L.pathXYZ,
      hilbertPhaseOp (Site := Site) L.pathXZY)
    (hilbertPhaseOp (Site := Site) L.pathXZY,
      hilbertPhaseOp (Site := Site) L.pathZXY)
    (ContinuousLinearMap.id ℂ (HilbertState Site),
      ContinuousLinearMap.id ℂ (HilbertState Site))

/-- The cubical gluing defect has the same five-face curvature budget on the
full finite Hilbert state as on a single spinor fiber. -/
theorem norm_hilbertCubeSwapDefect_le_curvatureBudget (L : CubeLinks) :
    ‖intertwiningDefectOp
      (fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
      (ContinuousLinearMap.id ℂ (HilbertState Site))
      (coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L))‖ ≤
      curvatureBudget L := by
  have hFine : ∀ p ∈ hilbertCubeSwapSevenPairs (Site := Site) L,
      ‖p.1‖ ≤ 1 := by
    simp [hilbertCubeSwapSevenPairs, sevenFactorPairs]
  have hCoarse : ∀ p ∈ hilbertCubeSwapSevenPairs (Site := Site) L,
      ‖p.2‖ ≤ 1 := by
    simp [hilbertCubeSwapSevenPairs, sevenFactorPairs]
  have h := norm_fullDefect_le_budget
    (ContinuousLinearMap.id ℂ (HilbertState Site))
    (hilbertCubeSwapSevenPairs (Site := Site) L) hFine hCoarse
  calc
    ‖intertwiningDefectOp
      (fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
      (ContinuousLinearMap.id ℂ (HilbertState Site))
      (coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L))‖ ≤
      ‖hilbertPhaseDefectOp (Site := Site) L.pathXYZ L.pathYXZ‖ +
      ‖hilbertPhaseDefectOp (Site := Site) L.pathYXZ L.pathYZX‖ +
      ‖hilbertPhaseDefectOp (Site := Site) L.pathYZX L.pathZYX‖ +
      ‖hilbertPhaseDefectOp (Site := Site) L.pathXYZ L.pathXZY‖ +
      ‖hilbertPhaseDefectOp (Site := Site) L.pathXZY L.pathZXY‖ := by
        simpa [hilbertCubeSwapSevenPairs, sevenFactorPairs, defectBudget,
          hilbertPhaseDefectOp, intertwiningDefectOp, add_assoc] using h
    _ = curvatureBudget L := by
      rw [norm_hilbertDefect_XYZ_YXZ,
        norm_hilbertDefect_YXZ_YZX,
        norm_hilbertDefect_YZX_ZYX,
        norm_hilbertDefect_XYZ_XZY,
        norm_hilbertDefect_XZY_ZXY]
      rfl

omit [Nonempty Site] in
/-- Flat cubical data gives an exactly vanishing Hilbert gluing defect. -/
theorem hilbertCubeSwapDefect_eq_zero_of_flat
    (L : CubeLinks) (h : L.Flat) :
    intertwiningDefectOp
      (fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
      (ContinuousLinearMap.id ℂ (HilbertState Site))
      (coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L)) = 0 := by
  rcases CubeLinks.Flat.all_corner_paths L h with
    ⟨hXZY, hYXZ, hYZX, hZXY, hZYX⟩
  apply fullDefect_eq_zero_of_local
  intro p hp
  simp [hilbertCubeSwapSevenPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  · simp [intertwiningDefectOp]
  · simp [intertwiningDefectOp, hilbertPhaseOp, hYXZ]
  · simp [intertwiningDefectOp, hilbertPhaseOp,
      hYXZ.symm.trans hYZX]
  · simp [intertwiningDefectOp, hilbertPhaseOp,
      hYZX.symm.trans hZYX]
  · simp [intertwiningDefectOp, hilbertPhaseOp, hXZY]
  · simp [intertwiningDefectOp, hilbertPhaseOp,
      hXZY.symm.trans hZXY]
  · simp [intertwiningDefectOp]

end HilbertCurvature


/-! ## Combined edge-plus-curvature Hilbert theorem -/

section CombinedHilbertBudget

variable {Site : Type u} [Fintype Site] [Nonempty Site]

omit [Nonempty Site] in
/-- The effective fine seven-factor walk is contractive. -/
theorem norm_fineHilbertSevenFactorComposite_le_one
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (hm₀ : ‖m₀‖ ≤ 1) (hm₁ : ‖m₁‖ ≤ 1) :
    ‖fineComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz)‖ ≤ 1 := by
  apply norm_composeOps_le_one
  intro F hF
  rcases List.mem_map.mp hF with ⟨p, hp, rfl⟩
  exact hilbertSevenFactorPairs_fine_contractive
    m₀ m₁ τx τy τz vx vy vz ux uy uz hm₀ hm₁ p hp

omit [Nonempty Site] in
/-- The prescribed coarse seven-factor walk is contractive. -/
theorem norm_coarseHilbertSevenFactorComposite_le_one
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (hm₀ : ‖m₀‖ ≤ 1) (hm₁ : ‖m₁‖ ≤ 1) :
    ‖coarseComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz)‖ ≤ 1 := by
  apply norm_composeOps_le_one
  intro F hF
  rcases List.mem_map.mp hF with ⟨p, hp, rfl⟩
  exact hilbertSevenFactorPairs_coarse_contractive
    m₀ m₁ τx τy τz vx vy vz ux uy uz hm₀ hm₁ p hp

/-- The fine cubical path-swap composition is contractive. -/
theorem norm_fineHilbertCubeSwapComposite_le_one (L : CubeLinks) :
    ‖fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L)‖ ≤ 1 := by
  apply norm_composeOps_le_one
  intro F hF
  rcases List.mem_map.mp hF with ⟨p, hp, rfl⟩
  simp [hilbertCubeSwapSevenPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals simp

/-- The coarse cubical path-swap composition is contractive. -/
theorem norm_coarseHilbertCubeSwapComposite_le_one (L : CubeLinks) :
    ‖coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L)‖ ≤ 1 := by
  apply norm_composeOps_le_one
  intro F hF
  rcases List.mem_map.mp hF with ⟨p, hp, rfl⟩
  simp [hilbertCubeSwapSevenPairs, sevenFactorPairs] at hp
  rcases hp with rfl | rfl | rfl | rfl | rfl | rfl | rfl
  all_goals simp

/-- Complete two-stage Hilbert defect: first the straight-edge walk comparison,
then the cubical path-reordering/gluing comparison. -/
def combinedHilbertDefect
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (L : CubeLinks) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  intertwiningDefectOp
    ((fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L)).comp
      (fineComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
        vx vy vz ux uy uz)))
    (ContinuousLinearMap.id ℂ (HilbertState Site))
    ((coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L)).comp
      (coarseComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
        vx vy vz ux uy uz)))

/-- Main combined Block 32 estimate.  Straight-edge reconstruction and cubical
curvature remain independent additive budgets. -/
theorem norm_combinedHilbertDefect_le
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (vx vy vz ux uy uz : Link (Site := Site))
    (L : CubeLinks)
    (hm₀ : ‖m₀‖ ≤ 1) (hm₁ : ‖m₁‖ ≤ 1) :
    ‖combinedHilbertDefect m₀ m₁ τx τy τz
      vx vy vz ux uy uz L‖ ≤
      hilbertEdgeBudget vx vy vz ux uy uz + curvatureBudget L := by
  exact norm_twoStageDefect_le
    (fineComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz))
    (fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
    (ContinuousLinearMap.id ℂ (HilbertState Site))
    (coarseComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      vx vy vz ux uy uz))
    (coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
    (norm_fineHilbertCubeSwapComposite_le_one L)
    (norm_coarseHilbertSevenFactorComposite_le_one
      m₀ m₁ τx τy τz vx vy vz ux uy uz hm₀ hm₁)
    (norm_hilbertSevenFactorDefect_le_edgeBudget
      m₀ m₁ τx τy τz vx vy vz ux uy uz hm₀ hm₁)
    (norm_hilbertCubeSwapDefect_le_curvatureBudget L)

omit [Nonempty Site] in
/-- Exact edge reconstruction together with flat cubical data annihilates the
complete two-stage Hilbert defect. -/
theorem combinedHilbertDefect_eq_zero_of_exact_flat
    (m₀ m₁ : HilbertState Site →L[ℂ] HilbertState Site)
    (τx τy τz : Site ≃ Site)
    (ux uy uz : Link (Site := Site))
    (L : CubeLinks) (hflat : L.Flat) :
    combinedHilbertDefect m₀ m₁ τx τy τz
      ux uy uz ux uy uz L = 0 := by
  exact twoStageDefect_eq_zero
    (fineComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      ux uy uz ux uy uz))
    (fineComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
    (ContinuousLinearMap.id ℂ (HilbertState Site))
    (coarseComposite (hilbertSevenFactorPairs m₀ m₁ τx τy τz
      ux uy uz ux uy uz))
    (coarseComposite (hilbertCubeSwapSevenPairs (Site := Site) L))
    (hilbertSevenFactorDefect_eq_zero_of_links m₀ m₁ τx τy τz ux uy uz)
    (hilbertCubeSwapDefect_eq_zero_of_flat L hflat)

end CombinedHilbertBudget

end Relativistic3DHilbertFullWalkDefect
end KomorebiPhysics
