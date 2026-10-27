import KomorebiSpace.OverlapPathRepair

set_option autoImplicit false

/-!
# Which independently supplied edge residuals are integrable?

The route operator projects edge data onto the image of the actual overlap
operator. It is not a right inverse on arbitrary residuals. An antisymmetric
triangle example violates loop consistency and has no primitive.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace OverlapTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H] [Fintype V]
variable (e : Frames (V := V) (H := H))
variable {graph : SimpleGraph V} {o : V}

/-- Actual overlap defects have zero normalized circulation on every closed walk. -/
theorem actual_closed_walk (x : V → H) (i : V) (p : graph.Walk i i) :
    pathIntegral e graph (edgeDifferential e graph x) p = 0 := by
  rw [pathIntegral_differential, sub_self]

namespace Routing
variable (routing : Routing graph o)

def residualProjection : (Edges graph → H) →L[ℝ] (Edges graph → H) :=
  (edgeDifferential e graph).comp (routing.correction e)

@[simp] theorem residualProjection_apply (r : Edges graph → H) :
    routing.residualProjection e r = edgeDifferential e graph (routing.correction e r) := rfl

@[simp] theorem residualProjection_actual (x : V → H) :
    routing.residualProjection e (edgeDifferential e graph x) = edgeDifferential e graph x :=
  routing.differential_correction_differential e x

theorem residualProjection_idempotent (r : Edges graph → H) :
    routing.residualProjection e (routing.residualProjection e r) = routing.residualProjection e r := by
  exact routing.differential_correction_differential e (routing.correction e r)

def routeObstruction : (Edges graph → H) →L[ℝ] (Edges graph → H) :=
  ContinuousLinearMap.id ℝ _ - routing.residualProjection e

@[simp] theorem routeObstruction_apply (r : Edges graph → H) :
    routing.routeObstruction e r = r - routing.residualProjection e r := rfl

/-- The diagnostic vanishes exactly for the actual image, not for every edge family. -/
theorem routeObstruction_zero_iff (r : Edges graph → H) :
    routing.routeObstruction e r = 0 ↔ ∃ x : V → H, edgeDifferential e graph x = r := by
  constructor
  · intro h
    refine ⟨routing.correction e r, ?_⟩
    exact (sub_eq_zero.mp h).symm
  · rintro ⟨x,rfl⟩
    rw [routeObstruction_apply, residualProjection_apply,
      routing.differential_correction_differential e x, sub_self]

theorem routeObstruction_idempotent (r : Edges graph → H) :
    routing.routeObstruction e (routing.routeObstruction e r) = routing.routeObstruction e r := by
  simp only [routeObstruction_apply, map_sub, routing.residualProjection_idempotent e,
    sub_self, sub_zero]

theorem repair_correction (r : Edges graph → H) :
    repair e o (routing.correction e r) = 0 := by
  funext i
  simp [repair, routing.correction_anchor e]

/-- The nonintegrable remainder contributes nothing to the selected route primitive. -/
theorem correction_obstruction_zero (r : Edges graph → H) :
    routing.correction e (routing.routeObstruction e r) = 0 := by
  rw [routeObstruction_apply, map_sub, residualProjection_apply,
    routing.correction_differential e, routing.repair_correction e, sub_zero, sub_self]

theorem routeObstruction_bound (r : Edges graph → H) :
    ‖routing.routeObstruction e r‖ ≤ (1 + 2 * (routing.radius : ℝ)) * ‖r‖ := by
  have hd := differentialLinear_bound e graph (routing.correction e r)
  have ha := routing.correction_bound e r
  calc
    _ ≤ ‖r‖ + ‖routing.residualProjection e r‖ := norm_sub_le _ _
    _ ≤ ‖r‖ + 2 * (routing.radius : ℝ) * ‖r‖ := by
      change ‖r‖ + ‖differentialLinear e graph (routing.correction e r)‖ ≤ _
      nlinarith
    _ = _ := by ring

end Routing

namespace CycleBoundary

def triangleFrames : Frames (V := Fin 3) (H := ℝ) := fun _ => LinearIsometryEquiv.refl ℝ ℝ

def triangleResidual : Edges (⊤ : SimpleGraph (Fin 3)) → ℝ := fun a =>
  if (a.val.1 = 0 ∧ a.val.2 = 1) ∨ (a.val.1 = 1 ∧ a.val.2 = 2) then 1
  else if (a.val.1 = 1 ∧ a.val.2 = 0) ∨ (a.val.1 = 2 ∧ a.val.2 = 1) then -1 else 0

/-- Even an antisymmetric edge assignment need not be the disagreement of vertex data. -/
theorem triangle_no_primitive :
    ¬ ∃ x : Fin 3 → ℝ, edgeDifferential triangleFrames ⊤ x = triangleResidual := by
  rintro ⟨x,hx⟩
  let a01 : Edges (⊤ : SimpleGraph (Fin 3)) := ⟨(0,1), by simp⟩
  let a12 : Edges (⊤ : SimpleGraph (Fin 3)) := ⟨(1,2), by simp⟩
  let a02 : Edges (⊤ : SimpleGraph (Fin 3)) := ⟨(0,2), by simp⟩
  have h01 := congrFun hx a01
  have h12 := congrFun hx a12
  have h02 := congrFun hx a02
  change x 1 - x 0 = 1 at h01
  change x 2 - x 1 = 1 at h12
  change x 2 - x 0 = 0 at h02
  linarith

end CycleBoundary
end OverlapTransport
end KomorebiSpace
end
