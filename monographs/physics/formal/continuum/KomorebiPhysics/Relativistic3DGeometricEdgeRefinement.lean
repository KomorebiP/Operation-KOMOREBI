module

public import KomorebiPhysics.Relativistic3DCliffordHilbertRefinement

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Geometric edge subdivision for the Clifford walk

This module replaces spectator-child replication by an actual subdivision of
one oriented lattice edge.  A coarse edge `x -> τ x` is split into

`inl x -> inr x -> inl (τ x)`.

The midpoint value is obtained by parallel transport along the first half-link.
With a coarse link reconstructed as the product of the second and first
half-links, two fine Clifford transports exactly intertwine with one coarse
transport.  The embedding is gauge covariant and Hilbert isometric after the
half-cell measure is included.

The result is deliberately one-axis.  Simultaneous exact interpolation in
three directions requires compatibility around fine plaquettes; that curvature
condition is not assumed here.
-/

namespace KomorebiPhysics
namespace Relativistic3DGeometricEdgeRefinement

open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement

universe u

/-- The two geometric half-cells attached to every coarse site. -/
abbrev HalfSite (Site : Type u) := Sum Site Site

/-- Lift a coarse translation to both endpoint copies. -/
def coarseLift {Site : Type u} (τ : Site ≃ Site) :
    HalfSite Site ≃ HalfSite Site :=
  Equiv.sumCongr τ τ

/-- A genuine half-edge translation:
`inl x -> inr x -> inl (τ x)`. -/
def halfShift {Site : Type u} (τ : Site ≃ Site) :
    HalfSite Site ≃ HalfSite Site where
  toFun
    | Sum.inl x => Sum.inr x
    | Sum.inr x => Sum.inl (τ x)
  invFun
    | Sum.inl x => Sum.inr (τ.symm x)
    | Sum.inr x => Sum.inl x
  left_inv := by
    intro y
    cases y <;> simp
  right_inv := by
    intro y
    cases y <;> simp

@[simp] theorem halfShift_inl {Site : Type u} (τ : Site ≃ Site) (x : Site) :
    halfShift τ (Sum.inl x) = Sum.inr x := rfl

@[simp] theorem halfShift_inr {Site : Type u} (τ : Site ≃ Site) (x : Site) :
    halfShift τ (Sum.inr x) = Sum.inl (τ x) := rfl

@[simp] theorem halfShift_symm_inl {Site : Type u} (τ : Site ≃ Site) (x : Site) :
    (halfShift τ).symm (Sum.inl x) = Sum.inr (τ.symm x) := rfl

@[simp] theorem halfShift_symm_inr {Site : Type u} (τ : Site ≃ Site) (x : Site) :
    (halfShift τ).symm (Sum.inr x) = Sum.inl x := rfl

/-- Two half translations are exactly one coarse translation on each copy. -/
@[simp] theorem halfShift_sq {Site : Type u} (τ : Site ≃ Site)
    (y : HalfSite Site) :
    halfShift τ (halfShift τ y) = coarseLift τ y := by
  cases y <;> rfl

/-- The graph-theoretic mesh scale.  The fine edge length is half the coarse
edge length; no continuum coordinate chart is inferred from this metadata. -/
structure MeshScale where
  spacing : ℝ
  spacing_pos : 0 < spacing

namespace MeshScale

/-- Halving the geometric edge scale. -/
def half (a : MeshScale) : MeshScale where
  spacing := a.spacing / 2
  spacing_pos := div_pos a.spacing_pos (by norm_num)

@[simp] theorem half_spacing (a : MeshScale) :
    a.half.spacing = a.spacing / 2 := rfl

@[simp] theorem two_mul_half_spacing (a : MeshScale) :
    2 * a.half.spacing = a.spacing := by
  dsimp [half]
  ring

end MeshScale

variable {Site : Type u}

/-- A factorization of one coarse `U(1)` link into two oriented half-links. -/
structure EdgeSubdivision (u : Link (Site := Site)) where
  first : Link (Site := Site)
  second : Link (Site := Site)
  reconstruct : ∀ x, second x * first x = u x

namespace EdgeSubdivision

/-- Fine link on the two half-edges. -/
def fineLink {u : Link (Site := Site)} (S : EdgeSubdivision u) :
    Link (Site := HalfSite Site)
  | Sum.inl x => S.first x
  | Sum.inr x => S.second x

/-- Gauge-covariant midpoint interpolation.  The midpoint is obtained by
parallel transport along the first half-link. -/
def embed {u : Link (Site := Site)} (S : EdgeSubdivision u)
    (ψ : State (Site := Site)) : State (Site := HalfSite Site)
  | Sum.inl x => ψ x
  | Sum.inr x => phaseMul (S.first x) (ψ x)

/-- Restrict a fine state to the coarse endpoints. -/
def endpointRestrict (Ψ : State (Site := HalfSite Site)) :
    State (Site := Site) := fun x => Ψ (Sum.inl x)

@[simp] theorem endpointRestrict_embed {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (ψ : State (Site := Site)) :
    endpointRestrict (S.embed ψ) = ψ := by
  rfl

/-- Reconstruct a coarse state by averaging the endpoint value with the
back-transported midpoint value.  This is the Hilbert adjoint of `embed` for
the half-cell weighted inner product proved below. -/
def restrict {u : Link (Site := Site)} (S : EdgeSubdivision u)
    (Ψ : State (Site := HalfSite Site)) : State (Site := Site) :=
  fun x => (2 : ℂ)⁻¹ •
    (Ψ (Sum.inl x) + phaseMul (S.first x)⁻¹ (Ψ (Sum.inr x)))

@[simp] theorem restrict_embed {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (ψ : State (Site := Site)) :
    S.restrict (S.embed ψ) = ψ := by
  funext x
  ext j
  simp [restrict, embed, phaseMul]
  ring

/-- Fine gauge values at endpoints and midpoints. -/
def fineGauge (g midpointGauge : Gauge (Site := Site)) :
    Gauge (Site := HalfSite Site)
  | Sum.inl x => g x
  | Sum.inr x => midpointGauge x

/-- Gauge transform the two half-links independently. -/
def gaugeTransform {u : Link (Site := Site)} (S : EdgeSubdivision u)
    (τ : Site ≃ Site) (g midpointGauge : Gauge (Site := Site)) :
    EdgeSubdivision (gaugeLink τ g u) where
  first := fun x => midpointGauge x * S.first x * (g x)⁻¹
  second := fun x => g (τ x) * S.second x * (midpointGauge x)⁻¹
  reconstruct := by
    intro x
    rw [gaugeLink]
    rw [← S.reconstruct x]
    group

@[simp] theorem gaugeTransform_first {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (τ : Site ≃ Site)
    (g midpointGauge : Gauge (Site := Site)) (x : Site) :
    (S.gaugeTransform τ g midpointGauge).first x =
      midpointGauge x * S.first x * (g x)⁻¹ := rfl

@[simp] theorem gaugeTransform_second {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (τ : Site ≃ Site)
    (g midpointGauge : Gauge (Site := Site)) (x : Site) :
    (S.gaugeTransform τ g midpointGauge).second x =
      g (τ x) * S.second x * (midpointGauge x)⁻¹ := rfl

/-- Gauge transformation commutes with assembling the fine link. -/
@[simp] theorem fineLink_gaugeTransform {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (τ : Site ≃ Site)
    (g midpointGauge : Gauge (Site := Site)) :
    (S.gaugeTransform τ g midpointGauge).fineLink =
      gaugeLink (halfShift τ) (fineGauge g midpointGauge) S.fineLink := by
  funext y
  cases y <;> simp [fineLink, gaugeLink, fineGauge, gaugeTransform]

/-- The midpoint interpolation itself is exactly gauge covariant. -/
@[simp] theorem embed_gauge_covariant {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (τ : Site ≃ Site)
    (g midpointGauge : Gauge (Site := Site))
    (ψ : State (Site := Site)) :
    (S.gaugeTransform τ g midpointGauge).embed (gaugeState g ψ) =
      gaugeState (fineGauge g midpointGauge) (S.embed ψ) := by
  funext y
  cases y <;> simp [embed, gaugeState, fineGauge, gaugeTransform,
    phaseMul_mul]

/-- Two fine half-edge Clifford transports exactly equal one coarse transport
on the gauge-covariant interpolated subspace. -/
@[simp] theorem first_inv_mul_second_inv {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (x : Site) :
    (S.first x)⁻¹ * (S.second x)⁻¹ = (u x)⁻¹ := by
  rw [← S.reconstruct x]
  group

@[simp] theorem second_inv_eq_first_mul_coarse_inv {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (x : Site) :
    (S.second x)⁻¹ = S.first x * (u x)⁻¹ := by
  rw [← S.reconstruct x]
  group

@[simp] theorem two_halfSteps_embed {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (A : CliffordInvolution) (τ : Site ≃ Site)
    (ψ : State (Site := Site)) :
    directionalShift A (halfShift τ) S.fineLink
      (directionalShift A (halfShift τ) S.fineLink (S.embed ψ)) =
    S.embed (directionalShift A τ u ψ) := by
  funext y
  cases y with
  | inl x =>
      simp [directionalShift, fineLink, embed, S.reconstruct]
  | inr x =>
      simp [directionalShift, fineLink, embed, S.reconstruct]


/-- The adjacent-scale directional intertwining defect. -/
def intertwiningDefect {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (A : CliffordInvolution) (τ : Site ≃ Site)
    (ψ : State (Site := Site)) : State (Site := HalfSite Site) :=
  directionalShift A (halfShift τ) S.fineLink
      (directionalShift A (halfShift τ) S.fineLink (S.embed ψ)) -
    S.embed (directionalShift A τ u ψ)

/-- Geometric edge subdivision has exactly zero directional defect. -/
@[simp] theorem intertwiningDefect_eq_zero {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (A : CliffordInvolution) (τ : Site ≃ Site)
    (ψ : State (Site := Site)) :
    intertwiningDefect S A τ ψ = 0 := by
  simp [intertwiningDefect]

end EdgeSubdivision

/-! ## Hilbert normalization and adjoint reconstruction -/

section Hilbert

variable [Fintype Site]

/-- Half-cell weighted Hilbert product on a geometrically subdivided edge. -/
def halfCellIP (Ψ Φ : State (Site := HalfSite Site)) : ℂ :=
  (2 : ℂ)⁻¹ * stateIP Ψ Φ

/-- Unweighted interpolation duplicates the coarse Hilbert weight. -/
@[simp] theorem embed_stateIP {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (ψ φ : State (Site := Site)) :
    stateIP (S.embed ψ) (S.embed φ) = 2 * stateIP ψ φ := by
  simp [stateIP, EdgeSubdivision.embed, Fintype.sum_sum_type,
    ip_phase_same]
  ring

/-- The half-cell measure makes geometric interpolation exactly isometric. -/
@[simp] theorem embed_halfCellIP_isometry {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (ψ φ : State (Site := Site)) :
    halfCellIP (S.embed ψ) (S.embed φ) = stateIP ψ φ := by
  simp [halfCellIP]

/-- Move a unit-circle phase from the first slot to the second slot. -/
@[simp] theorem ip_phase_left_eq_ip_inv_right (z : Circle) (ψ φ : Spinor) :
    ip (phaseMul z ψ) φ = ip ψ (phaseMul z⁻¹ φ) := by
  calc
    ip (phaseMul z ψ) φ =
        ip (phaseMul z ψ) (phaseMul z (phaseMul z⁻¹ φ)) := by simp
    _ = ip ψ (phaseMul z⁻¹ φ) := ip_phase_same z ψ (phaseMul z⁻¹ φ)

/-- The averaging restriction is the Hilbert adjoint of interpolation. -/
@[simp] theorem embed_restrict_adjoint {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (ψ : State (Site := Site))
    (Ψ : State (Site := HalfSite Site)) :
    halfCellIP (S.embed ψ) Ψ = stateIP ψ (S.restrict Ψ) := by
  simp [halfCellIP, stateIP, EdgeSubdivision.embed, EdgeSubdivision.restrict,
    Fintype.sum_sum_type, ip_phase_left_eq_ip_inv_right, ip_add_right,
    ip_smul_right]
  rw [mul_add, Finset.mul_sum, Finset.mul_sum, ← Finset.sum_add_distrib]

/-- Fine Clifford transport is unitary for the half-cell measure. -/
@[simp] theorem directionalShift_halfCellIP
    (H : HermitianClifford) (τ : HalfSite Site ≃ HalfSite Site)
    (u : Link (Site := HalfSite Site))
    (Ψ Φ : State (Site := HalfSite Site)) :
    halfCellIP
      (directionalShift H.toClifford τ u Ψ)
      (directionalShift H.toClifford τ u Φ) = halfCellIP Ψ Φ := by
  unfold halfCellIP
  rw [directionalShift_stateIP]

end Hilbert

/-! ## One-axis factorwise refined evolution -/

/-- A local coarse step supplied together with an exact half-step square root. -/
structure LocalStepSubdivision (coarse : LocalStep) where
  half : LocalStep
  square : ∀ ψ, half.toFun (half.toFun ψ) = coarse.toFun ψ

namespace LocalStepSubdivision

/-- Local steps commute with the covariant edge interpolation. -/
@[simp] theorem half_apply_embed {u : Link (Site := Site)}
    {M : LocalStep} (D : LocalStepSubdivision M) (S : EdgeSubdivision u)
    (ψ : State (Site := Site)) :
    D.half.apply (S.embed ψ) = S.embed (D.half.apply ψ) := by
  funext y
  cases y <;> simp [LocalStep.apply, EdgeSubdivision.embed, D.half.phase_commutes]

/-- Two local half steps exactly realize the coarse local step under embedding. -/
@[simp] theorem two_half_apply_embed {u : Link (Site := Site)}
    {M : LocalStep} (D : LocalStepSubdivision M) (S : EdgeSubdivision u)
    (ψ : State (Site := Site)) :
    D.half.apply (D.half.apply (S.embed ψ)) = S.embed (M.apply ψ) := by
  rw [D.half_apply_embed, D.half_apply_embed]
  funext y
  cases y <;> simp [LocalStep.apply, EdgeSubdivision.embed, D.square]

end LocalStepSubdivision

/-- A one-axis symmetric local walk `M-S-M`. -/
def oneAxisWalk (M : LocalStep) (A : CliffordInvolution)
    (τ : Site ≃ Site) (u : Link (Site := Site))
    (ψ : State (Site := Site)) : State (Site := Site) :=
  M.apply (directionalShift A τ u (M.apply ψ))

/-- Factorwise geometric refinement of `M-S-M`: each coarse factor is replaced
by its two half-edge or half-time factors. -/
def refinedOneAxisWalk {u : Link (Site := Site)}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (S : EdgeSubdivision u) (A : CliffordInvolution) (τ : Site ≃ Site)
    (Ψ : State (Site := HalfSite Site)) : State (Site := HalfSite Site) :=
  D.half.apply (D.half.apply
    (directionalShift A (halfShift τ) S.fineLink
      (directionalShift A (halfShift τ) S.fineLink
        (D.half.apply (D.half.apply Ψ)))))

/-- Exact one-axis geometric refinement of the symmetric local walk. -/
@[simp] theorem refinedOneAxisWalk_embed {u : Link (Site := Site)}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (S : EdgeSubdivision u) (A : CliffordInvolution) (τ : Site ≃ Site)
    (ψ : State (Site := Site)) :
    refinedOneAxisWalk D S A τ (S.embed ψ) =
      S.embed (oneAxisWalk M A τ u ψ) := by
  unfold refinedOneAxisWalk oneAxisWalk
  rw [D.two_half_apply_embed]
  rw [S.two_halfSteps_embed]
  rw [D.two_half_apply_embed]

/-! ## Concrete spectral-phase square roots -/

/-- Two identical spectral half-phases multiply to the corresponding squared
coarse phases. -/
def spectralPhaseSubdivision (H : HermitianClifford) (zp zm : Circle) :
    LocalStepSubdivision (spectralPhaseLocalStep H (zp * zp) (zm * zm)) where
  half := spectralPhaseLocalStep H zp zm
  square := by
    intro ψ
    simp [spectralPhaseLocalStep, spectralPhase, phaseMul_mul]

/-- Concrete beta-mass version of the exact one-axis refinement theorem. -/
@[simp] theorem refinedOneAxisWalk_beta_embed {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (zp zm : Circle)
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (ψ : State (Site := Site)) :
    refinedOneAxisWalk (spectralPhaseSubdivision hermitianBeta zp zm)
      S A τ (S.embed ψ) =
    S.embed
      (oneAxisWalk (spectralPhaseLocalStep hermitianBeta (zp * zp) (zm * zm))
        A τ u ψ) := by
  exact refinedOneAxisWalk_embed
    (spectralPhaseSubdivision hermitianBeta zp zm) S A τ ψ



/-! ## Canonical subdivisions and covariant projection -/

namespace EdgeSubdivision

/-- Every coarse link admits a subdivision after choosing the first half-link. -/
def fromFirst (u first : Link (Site := Site)) : EdgeSubdivision u where
  first := first
  second := fun x => u x * (first x)⁻¹
  reconstruct := by
    intro x
    group

@[simp] theorem fromFirst_first (u first : Link (Site := Site)) (x : Site) :
    (fromFirst u first).first x = first x := rfl

@[simp] theorem fromFirst_second (u first : Link (Site := Site)) (x : Site) :
    (fromFirst u first).second x = u x * (first x)⁻¹ := rfl

/-- Canonical endpoint-midpoint subdivision with trivial first half-link. -/
def boundarySubdivision (u : Link (Site := Site)) : EdgeSubdivision u :=
  fromFirst u (fun _ => 1)

@[simp] theorem boundarySubdivision_first (u : Link (Site := Site)) (x : Site) :
    (boundarySubdivision u).first x = 1 := rfl

@[simp] theorem boundarySubdivision_second (u : Link (Site := Site)) (x : Site) :
    (boundarySubdivision u).second x = u x := by
  simp [boundarySubdivision, fromFirst]

/-- Orthogonal reconstruction candidate onto the covariantly interpolated
subspace. -/
def project {u : Link (Site := Site)} (S : EdgeSubdivision u)
    (Ψ : State (Site := HalfSite Site)) : State (Site := HalfSite Site) :=
  S.embed (S.restrict Ψ)

@[simp] theorem restrict_project {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (Ψ : State (Site := HalfSite Site)) :
    S.restrict (S.project Ψ) = S.restrict Ψ := by
  simp [project]

@[simp] theorem project_idempotent {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (Ψ : State (Site := HalfSite Site)) :
    S.project (S.project Ψ) = S.project Ψ := by
  simp [project]

@[simp] theorem project_embed {u : Link (Site := Site)}
    (S : EdgeSubdivision u) (ψ : State (Site := Site)) :
    S.project (S.embed ψ) = S.embed ψ := by
  simp [project]

end EdgeSubdivision

/-! ## Gauge covariance of the refined one-axis walk -/

@[simp] theorem refinedOneAxisWalk_gauge_covariant {u : Link (Site := Site)}
    {M : LocalStep} (D : LocalStepSubdivision M)
    (S : EdgeSubdivision u) (A : CliffordInvolution) (τ : Site ≃ Site)
    (g midpointGauge : Gauge (Site := Site))
    (Ψ : State (Site := HalfSite Site)) :
    refinedOneAxisWalk D (S.gaugeTransform τ g midpointGauge) A τ
      (gaugeState (EdgeSubdivision.fineGauge g midpointGauge) Ψ) =
    gaugeState (EdgeSubdivision.fineGauge g midpointGauge)
      (refinedOneAxisWalk D S A τ Ψ) := by
  unfold refinedOneAxisWalk
  rw [EdgeSubdivision.fineLink_gaugeTransform]
  rw [D.half.apply_gauge]
  rw [D.half.apply_gauge]
  rw [directionalShift_gauge_covariant]
  rw [directionalShift_gauge_covariant]
  rw [D.half.apply_gauge]
  rw [D.half.apply_gauge]

/-! ## Hilbert-preserving factorwise refinement -/

/-- A Hilbert-preserving local coarse step with an exact Hilbert-preserving
square root. -/
structure HilbertLocalStepSubdivision (coarse : HilbertLocalStep) where
  half : HilbertLocalStep
  square : ∀ ψ, half.toLocalStep.toFun (half.toLocalStep.toFun ψ) =
    coarse.toLocalStep.toFun ψ

namespace HilbertLocalStepSubdivision

/-- Forget only the Hilbert certificate. -/
def toLocalSubdivision {M : HilbertLocalStep}
    (D : HilbertLocalStepSubdivision M) :
    LocalStepSubdivision M.toLocalStep where
  half := D.half.toLocalStep
  square := D.square

end HilbertLocalStepSubdivision

/-- Every Hermitian spectral phase split carries its Hilbert certificate. -/
def spectralPhaseHilbertStep (H : HermitianClifford) (zp zm : Circle) :
    HilbertLocalStep where
  toLocalStep := spectralPhaseLocalStep H zp zm
  preserves_ip := spectralPhase_ip H zp zm

/-- Spectral phases admit exact Hilbert-preserving half steps. -/
def spectralPhaseHilbertSubdivision (H : HermitianClifford) (zp zm : Circle) :
    HilbertLocalStepSubdivision
      (spectralPhaseHilbertStep H (zp * zp) (zm * zm)) where
  half := spectralPhaseHilbertStep H zp zm
  square := by
    intro ψ
    simp [spectralPhaseHilbertStep, spectralPhaseLocalStep, spectralPhase,
      phaseMul_mul]

section RefinedHilbert

variable [Fintype Site]

/-- The complete factorwise fine walk preserves the half-cell Hilbert product. -/
@[simp] theorem refinedOneAxisWalk_halfCellIP
    {u : Link (Site := Site)} {M : HilbertLocalStep}
    (D : HilbertLocalStepSubdivision M)
    (S : EdgeSubdivision u)
    (H : HermitianClifford) (τ : Site ≃ Site)
    (Ψ Φ : State (Site := HalfSite Site)) :
    halfCellIP
      (refinedOneAxisWalk D.toLocalSubdivision S H.toClifford τ Ψ)
      (refinedOneAxisWalk D.toLocalSubdivision S H.toClifford τ Φ) =
    halfCellIP Ψ Φ := by
  unfold refinedOneAxisWalk halfCellIP
  simp only [HilbertLocalStepSubdivision.toLocalSubdivision]
  rw [D.half.apply_stateIP]
  rw [D.half.apply_stateIP]
  rw [directionalShift_stateIP]
  rw [directionalShift_stateIP]
  rw [D.half.apply_stateIP]
  rw [D.half.apply_stateIP]

end RefinedHilbert

/-! ## Plaquette holonomy: the obstruction to path-independent multi-axis interpolation -/

section Plaquette

/-- Parallel transport around the `x`-then-`y` path. -/
def pathXY (τx : Site ≃ Site)
    (ux uy : Link (Site := Site)) (x : Site) : Circle :=
  uy (τx x) * ux x

/-- Parallel transport around the `y`-then-`x` path. -/
def pathYX (τy : Site ≃ Site)
    (ux uy : Link (Site := Site)) (x : Site) : Circle :=
  ux (τy x) * uy x

/-- Abelian plaquette holonomy comparing the two corner paths. -/
def plaquette (τx τy : Site ≃ Site)
    (ux uy : Link (Site := Site)) (x : Site) : Circle :=
  pathXY τx ux uy x / pathYX τy ux uy x

@[simp] theorem plaquette_eq_one_iff_path_independent
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site)) (x : Site) :
    plaquette τx τy ux uy x = 1 ↔
      pathXY τx ux uy x = pathYX τy ux uy x := by
  unfold plaquette
  rw [div_eq_one]

/-- Gauge transformation of the `x`-then-`y` path. -/
theorem pathXY_gauge
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site))
    (g : Gauge (Site := Site)) (x : Site) :
    pathXY τx (gaugeLink τx g ux) (gaugeLink τy g uy) x =
      g (τy (τx x)) * pathXY τx ux uy x * (g x)⁻¹ := by
  simp only [pathXY, gaugeLink]
  group

/-- Gauge transformation of the `y`-then-`x` path. -/
theorem pathYX_gauge
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site))
    (g : Gauge (Site := Site)) (x : Site) :
    pathYX τy (gaugeLink τx g ux) (gaugeLink τy g uy) x =
      g (τx (τy x)) * pathYX τy ux uy x * (g x)⁻¹ := by
  simp only [pathYX, gaugeLink]
  group

/-- Common endpoint gauge factors cancel from a ratio of abelian transports. -/
theorem common_endpoint_ratio_cancel (a b p q : Circle) :
    (a * p * b⁻¹) / (a * q * b⁻¹) = p / q := by
  simp only [div_eq_mul_inv, mul_inv_rev, inv_inv]
  calc
    a * p * b⁻¹ * (b * (q⁻¹ * a⁻¹)) =
        (a * a⁻¹) * (b⁻¹ * b) * (p * q⁻¹) := by ac_rfl
    _ = p * q⁻¹ := by simp

/-- Under commuting lattice translations, the plaquette is gauge invariant. -/
@[simp] theorem plaquette_gauge_invariant
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site))
    (g : Gauge (Site := Site))
    (hcomm : ∀ x, τy (τx x) = τx (τy x)) (x : Site) :
    plaquette τx τy (gaugeLink τx g ux) (gaugeLink τy g uy) x =
      plaquette τx τy ux uy x := by
  unfold plaquette
  rw [pathXY_gauge, pathYX_gauge, hcomm x]
  exact common_endpoint_ratio_cancel (g (τx (τy x))) (g x)
    (pathXY τx ux uy x) (pathYX τy ux uy x)

/-- A nontrivial plaquette forces the two transported corner phases to differ. -/
theorem path_ne_of_plaquette_ne_one
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site)) (x : Site)
    (h : plaquette τx τy ux uy x ≠ 1) :
    pathXY τx ux uy x ≠ pathYX τy ux uy x := by
  intro hp
  apply h
  exact (plaquette_eq_one_iff_path_independent τx τy ux uy x).2 hp

/-- A fixed nonzero spinor witnessing the path dependence. -/
def basisSpinor0 : Spinor := ![1, 0, 0, 0]

/-- Unit-circle phases act faithfully on the chosen nonzero spinor. -/
theorem phaseMul_basisSpinor0_injective :
    Function.Injective (fun z : Circle => phaseMul z basisSpinor0) := by
  intro z w h
  apply Subtype.ext
  have h0 := congrFun h 0
  simpa [phaseMul, basisSpinor0] using h0

/-- Flat plaquette holonomy is equivalent to path-independent transport of a
nonzero spinor around the refined corner. -/
@[simp] theorem corner_transport_eq_iff_flat
    (τx τy : Site ≃ Site) (ux uy : Link (Site := Site)) (x : Site) :
    phaseMul (pathXY τx ux uy x) basisSpinor0 =
      phaseMul (pathYX τy ux uy x) basisSpinor0 ↔
    plaquette τx τy ux uy x = 1 := by
  constructor
  · intro h
    apply (plaquette_eq_one_iff_path_independent τx τy ux uy x).2
    exact phaseMul_basisSpinor0_injective h
  · intro h
    have hp := (plaquette_eq_one_iff_path_independent τx τy ux uy x).1 h
    rw [hp]



/-! ### Concrete nonflat witness -/

/-- Swap the two sites of a Boolean periodic edge. -/
def boolSwap : Bool ≃ Bool := Equiv.swap false true

/-- A unit-circle link with opposite phases on the two Boolean sites. -/
def alternatingBoolLink : Link (Site := Bool)
  | false => 1
  | true => -1

/-- The Boolean periodic cell has an explicit nontrivial plaquette. -/
@[simp] theorem bool_plaquette_witness :
    plaquette boolSwap (Equiv.refl Bool) (fun _ => 1) alternatingBoolLink false = -1 := by
  simp [plaquette, pathXY, pathYX, boolSwap, alternatingBoolLink]

/-- Hence exact path-independent corner interpolation fails in this witness. -/
theorem bool_plaquette_nonflat :
    plaquette boolSwap (Equiv.refl Bool) (fun _ => 1) alternatingBoolLink false ≠ 1 := by
  rw [bool_plaquette_witness]
  intro h
  have hc := congrArg (fun z : Circle => (z : ℂ)) h
  norm_num at hc

end Plaquette

end Relativistic3DGeometricEdgeRefinement
end KomorebiPhysics
