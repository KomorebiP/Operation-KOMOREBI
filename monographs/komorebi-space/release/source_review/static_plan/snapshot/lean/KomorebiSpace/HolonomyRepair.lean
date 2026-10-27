import KomorebiSpace.HolonomyCoordinates
import KomorebiSpace.Correction

set_option autoImplicit false

/-!
# Holonomy-sensitive quantitative repair with protected observations

A feasible anchor has a unique parallel extension and a graph-derived bound.
The feasibility test is identified with the existing correction quotient.
For arbitrary anchors, a separate anchor correction estimate is necessary.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H] [Fintype V]
namespace Rooted
variable (T : Connection V H) {graph : SimpleGraph V} {o : V}
variable (p : OverlapTransport.Routing graph o)

def rootResidual (z : H) (a : OverlapTransport.Edges graph) : H := holonomy T p a z - z

omit [Fintype V] in
@[simp] theorem rootResidual_zero_iff (z : H) :
    rootResidual T p z = 0 ↔ z ∈ fixedSpace T p := by
  constructor
  · intro hz a; exact sub_eq_zero.mp (congrFun hz a)
  · intro hz; funext a; exact sub_eq_zero.mpr (hz a)

theorem rootResidual_coordinate_norm (z : H) (a : OverlapTransport.Edges graph) :
    ‖rootResidual T p z a‖ = ‖T.differential graph (reconstruct T p z) a‖ := by
  change ‖holonomy T p a z - z‖ = ‖T.defect (reconstruct T p z) a.val.1 a.val.2‖
  rw [← normalized_reconstruction_defect]
  exact (frame T p a.val.1).symm.norm_map _

theorem rootResidual_norm (z : H) :
    ‖rootResidual T p z‖ = ‖T.differential graph (reconstruct T p z)‖ := by
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg (norm_nonneg _)).mpr
    intro a
    rw [rootResidual_coordinate_norm]
    exact norm_le_pi_norm _ a
  · apply (pi_norm_le_iff_of_nonneg (norm_nonneg _)).mpr
    intro a
    rw [← rootResidual_coordinate_norm]
    exact norm_le_pi_norm _ a

theorem reconstruct_difference_norm (z w : H) :
    ‖reconstruct T p z - reconstruct T p w‖ = ‖z-w‖ := by
  have he : reconstruct T p z - reconstruct T p w = reconstruct T p (z-w) := by
    funext i
    exact (map_sub (frame T p i) z w).symm
  rw [he, reconstruct_norm]

/-- Small edge residual controls the loop inconsistency of the observed anchor. -/
theorem rootResidual_anchor_bound (x : V → H) :
    ‖rootResidual T p (x o)‖ ≤ (2 * (p.radius : ℝ) + 1) * ‖T.differential graph x‖ := by
  rw [rootResidual_norm]
  have ht : ‖T.differential graph (reconstruct T p (x o))‖ ≤
      ‖T.differential graph (reconstruct T p (x o) - x)‖ + ‖T.differential graph x‖ := by
    calc
      _ = ‖T.differential graph (reconstruct T p (x o) - x) + T.differential graph x‖ := by
        rw [map_sub, sub_add_cancel]
      _ ≤ _ := norm_add_le _ _
  have hd := T.differentialLinear_bound graph (reconstruct T p (x o)-x)
  have he := anchored_approximation_bound T p x
  change ‖T.differential graph (reconstruct T p (x o)-x)‖ ≤ 2 * ‖reconstruct T p (x o)-x‖ at hd
  rw [norm_sub_rev] at hd
  calc
    _ ≤ 2 * ‖x-reconstruct T p (x o)‖ + ‖T.differential graph x‖ :=
      by linarith
    _ ≤ 2 * ((p.radius : ℝ) * ‖T.differential graph x‖) + ‖T.differential graph x‖ :=
      by linarith
    _ = _ := by ring

theorem changed_anchor_error (x : V → H) (z : H) :
    ‖x-reconstruct T p z‖ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ + ‖x o-z‖ := by
  calc
    _ ≤ ‖x-reconstruct T p (x o)‖ +
      ‖reconstruct T p (x o)-reconstruct T p z‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ + ‖x o-z‖ :=
      add_le_add (anchored_approximation_bound T p x) (le_of_eq (reconstruct_difference_norm T p _ _))

/-- A conditional anchor estimate is kept separate from graph propagation. -/
theorem repair_from_anchor_estimate (q : H → H) (K : ℝ) (hK : 0 ≤ K)
    (hq : ∀ z, q z ∈ fixedSpace T p)
    (hb : ∀ z, ‖z-q z‖ ≤ K * ‖rootResidual T p z‖) (x : V → H) :
    T.Parallel graph (reconstruct T p (q (x o))) ∧
      ‖x-reconstruct T p (q (x o))‖ ≤
        ((p.radius : ℝ) + K * (2 * (p.radius : ℝ)+1)) * ‖T.differential graph x‖ := by
  constructor
  · exact (reconstruct_parallel_iff T p _).mpr (hq _)
  · calc
      _ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ + ‖x o-q (x o)‖ :=
        changed_anchor_error T p x _
      _ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ + K * ‖rootResidual T p (x o)‖ :=
        by linarith [hb (x o)]
      _ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ +
          K * ((2 * (p.radius : ℝ)+1) * ‖T.differential graph x‖) :=
        by
          have hm := mul_le_mul_of_nonneg_left (rootResidual_anchor_bound T p x) hK
          linarith
      _ = _ := by ring

/-- Prescribed vertex values, not only their norms. -/
def observation (U : Set V) : (V → H) →+ (U → H) where
  toFun x i := x i.val
  map_zero' := rfl
  map_add' := by intros; rfl

def problem (U : Set V) :
    CorrectionProblem (V → H) (OverlapTransport.Edges graph → H) (U → H) where
  residual := (T.differential graph).toLinearMap.toAddMonoidHom
  semantics := observation U

/-- The independently defined quotient detects both loop feasibility and prescribed values. -/
theorem obstruction_criterion (U : Set V) (ho : o ∈ U) (x : V → H) :
    (problem T (graph := graph) U).obstruction x = 0 ↔
      x o ∈ fixedSpace T p ∧ ∀ i : U, reconstruct T p (x o) i.val = x i.val := by
  rw [CorrectionProblem.flatten_iff]
  change (∃ y : V → H, T.differential graph y = 0 ∧ observation U y = observation U x) ↔ _
  constructor
  · rintro ⟨y,hy,hobs⟩
    have hp := (T.parallel_iff_differential_zero y).mpr hy
    have ha : y o = x o := congrFun hobs ⟨o,ho⟩
    have hr : reconstruct T p (x o) = y := by rw [← ha]; exact parallel_reconstruction T p y hp
    constructor
    · rw [← ha]; exact parallel_anchor_fixed T p y hp
    · intro i; rw [hr]; exact congrFun hobs i
  · rintro ⟨hx,hU⟩
    exact ⟨reconstruct T p (x o),
      (T.parallel_iff_differential_zero _).mp ((reconstruct_parallel_iff T p _).mpr hx),
      funext hU⟩

/-- A nonflat protected reconstruction theorem using the original correction quotient. -/
theorem quantitative_prescribed_repair (U : Set V) (ho : o ∈ U) (x : V → H)
    (hx : (problem T (graph := graph) U).obstruction x = 0) :
    ∃! y : V → H, T.Parallel graph y ∧ (∀ i : U, y i.val = x i.val) ∧
      ‖x-y‖ ≤ (p.radius : ℝ) * ‖T.differential graph x‖ := by
  obtain ⟨hfix,hU⟩ := (obstruction_criterion T p U ho x).mp hx
  refine ⟨reconstruct T p (x o), ⟨(reconstruct_parallel_iff T p _).mpr hfix,
    hU, anchored_approximation_bound T p x⟩, ?_⟩
  intro y hy
  exact parallel_unique T p hy.1 ((reconstruct_parallel_iff T p _).mpr hfix)
    ((hy.2.1 ⟨o,ho⟩).trans (reconstruct_anchor T p _).symm)

end Rooted
end HolonomyTransport
end KomorebiSpace
end
