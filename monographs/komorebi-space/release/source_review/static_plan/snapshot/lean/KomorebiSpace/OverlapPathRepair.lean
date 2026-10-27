import KomorebiSpace.OverlapTransport
import Mathlib.Combinatorics.SimpleGraph.Walk.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

set_option autoImplicit false

/-!
# A correction from measured overlap paths

All edges carry the actual source-frame residual. The correction is a finite
sum along specified root paths. Its norm follows from path length, rather
than being a right-inverse or spectral-gap assumption.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace OverlapTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]
abbrev Edges (graph : SimpleGraph V) := {p : V × V // graph.Adj p.1 p.2}
noncomputable instance edgesFintype [Fintype V] (graph : SimpleGraph V) :
    Fintype (Edges graph) := Fintype.ofFinite _
structure Routing (graph : SimpleGraph V) (o : V) where
  path : ∀ i, graph.Walk o i
  at_anchor : path o = .nil
variable (e : Frames (V := V) (H := H)) (graph : SimpleGraph V)
def pathIntegral (r : Edges graph → H) : {i j : V} → graph.Walk i j → H
  | _, _, .nil => 0
  | i, _, .cons h p => (e i).symm (r ⟨(_, _), h⟩) + pathIntegral r p
@[simp] theorem pathIntegral_nil (r : Edges graph → H) (i : V) :
    pathIntegral e graph r (SimpleGraph.Walk.nil (u := i)) = 0 := rfl
theorem pathIntegral_add (r s : Edges graph → H) {i j : V} (p : graph.Walk i j) :
    pathIntegral e graph (r+s) p = pathIntegral e graph r p + pathIntegral e graph s p := by
  induction p with
  | nil => simp [pathIntegral]
  | cons h p ih => simp only [pathIntegral, Pi.add_apply, map_add, ih]; abel
theorem pathIntegral_smul (c : ℝ) (r : Edges graph → H) {i j : V}
    (p : graph.Walk i j) :
    pathIntegral e graph (c • r) p = c • pathIntegral e graph r p := by
  induction p with
  | nil => simp [pathIntegral]
  | cons h p ih => simp [pathIntegral, ih, smul_add]
variable [Fintype V]
def differentialLinear : (V → H) →ₗ[ℝ] (Edges graph → H) where
  toFun x a := defect e x a.val.1 a.val.2
  map_add' := by
    intro x y
    funext a
    simp only [defect, Pi.add_apply, map_add]
    abel
  map_smul' := by intro c x; funext a; simp [defect, map_smul, smul_sub]
theorem differentialLinear_bound (x : V → H) :
    ‖differentialLinear e graph x‖ ≤ 2 * ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (mul_nonneg (by norm_num) (norm_nonneg x))).mpr
  intro a
  change ‖transport e a.val.1 a.val.2 (x a.val.2) - x a.val.1‖ ≤ _
  calc
    _ ≤ ‖transport e a.val.1 a.val.2 (x a.val.2)‖ + ‖x a.val.1‖ := norm_sub_le _ _
    _ = ‖x a.val.2‖ + ‖x a.val.1‖ := by rw [(transport e _ _).norm_map]
    _ ≤ 2 * ‖x‖ := by
      have h1 := norm_le_pi_norm x a.val.1
      have h2 := norm_le_pi_norm x a.val.2
      linarith
def edgeDifferential : (V → H) →L[ℝ] (Edges graph → H) :=
  (differentialLinear e graph).mkContinuous 2 (differentialLinear_bound e graph)
@[simp] theorem edgeDifferential_apply (x : V → H) (a : Edges graph) :
    edgeDifferential e graph x a = defect e x a.val.1 a.val.2 := rfl
theorem edgeDifferential_opNorm : ‖edgeDifferential e graph‖ ≤ 2 := by
  apply (edgeDifferential e graph).opNorm_le_bound (by norm_num)
  exact differentialLinear_bound e graph
theorem pathIntegral_bound (r : Edges graph → H) {i j : V} (p : graph.Walk i j) :
    ‖pathIntegral e graph r p‖ ≤ (p.length : ℝ) * ‖r‖ := by
  induction p with
  | nil => simp [pathIntegral]
  | @cons i k j h p ih =>
    have he : ‖(e i).symm (r ⟨(i,k),h⟩)‖ ≤ ‖r‖ := by
      simpa only [LinearIsometryEquiv.norm_map] using norm_le_pi_norm r ⟨(i,k),h⟩
    calc
      _ ≤ ‖(e i).symm (r ⟨(i,k),h⟩)‖ + ‖pathIntegral e graph r p‖ := norm_add_le _ _
      _ ≤ ‖r‖ + (p.length : ℝ) * ‖r‖ := add_le_add he ih
      _ = ((SimpleGraph.Walk.cons h p).length : ℝ) * ‖r‖ := by
        simp only [SimpleGraph.Walk.length_cons, Nat.cast_add, Nat.cast_one]
        ring
theorem pathIntegral_differential (x : V → H) {i j : V} (p : graph.Walk i j) :
    pathIntegral e graph (edgeDifferential e graph x) p =
      normalized e x j - normalized e x i := by
  induction p with
  | nil => simp [pathIntegral]
  | cons h p ih =>
    simp only [pathIntegral, edgeDifferential_apply, normalized_defect, ih]
    abel
namespace Routing
variable {graph} {o : V} (routing : Routing graph o)
def radius : ℕ := Finset.univ.sup (fun i => (routing.path i).length)
theorem length_le_radius (i : V) : (routing.path i).length ≤ routing.radius := by
  exact Finset.le_sup (f := fun i => (routing.path i).length) (Finset.mem_univ i)
def correctionLinear : (Edges graph → H) →ₗ[ℝ] (V → H) where
  toFun r i := e i (pathIntegral e graph r (routing.path i))
  map_add' := by intro r s; funext i; simp [pathIntegral_add, map_add]
  map_smul' := by intro c r; funext i; simp [pathIntegral_smul, map_smul]
theorem correctionLinear_bound (r : Edges graph → H) :
    ‖routing.correctionLinear e r‖ ≤ (routing.radius : ℝ) * ‖r‖ := by
  apply (pi_norm_le_iff_of_nonneg (mul_nonneg (Nat.cast_nonneg _) (norm_nonneg r))).mpr
  intro i
  change ‖e i (pathIntegral e graph r (routing.path i))‖ ≤ _
  rw [(e i).norm_map]
  exact (pathIntegral_bound e graph r (routing.path i)).trans
    (mul_le_mul_of_nonneg_right (by exact_mod_cast routing.length_le_radius i) (norm_nonneg r))
def correction : (Edges graph → H) →L[ℝ] (V → H) :=
  (routing.correctionLinear e).mkContinuous (routing.radius : ℝ)
    (routing.correctionLinear_bound e)
@[simp] theorem correction_apply (r : Edges graph → H) (i : V) :
    routing.correction e r i = e i (pathIntegral e graph r (routing.path i)) := rfl
theorem correction_bound (r : Edges graph → H) :
    ‖routing.correction e r‖ ≤ (routing.radius : ℝ) * ‖r‖ :=
  routing.correctionLinear_bound e r
theorem correction_opNorm : ‖routing.correction e‖ ≤ (routing.radius : ℝ) := by
  apply (routing.correction e).opNorm_le_bound (Nat.cast_nonneg _)
  exact routing.correction_bound e
@[simp] theorem correction_anchor (r : Edges graph → H) :
    routing.correction e r o = 0 := by
  simp [correction_apply, routing.at_anchor]
theorem correction_differential (x : V → H) :
    routing.correction e (edgeDifferential e graph x) = x - repair e o x := by
  funext i
  simp [correction_apply, pathIntegral_differential, normalized,
    repair, transport_apply, map_sub]
@[simp] theorem differential_repair (x : V → H) :
    edgeDifferential e graph (repair e o x) = 0 := by
  funext a
  exact repair_defect e o x a.val.1 a.val.2
/-- Right inversion only on residuals of actual candidates. -/
theorem differential_correction_differential (x : V → H) :
    edgeDifferential e graph (routing.correction e (edgeDifferential e graph x)) =
      edgeDifferential e graph x := by
  rw [routing.correction_differential e, map_sub, differential_repair (graph := graph) (o := o) e, sub_zero]
theorem repair_error (x : V → H) :
    ‖x - repair e o x‖ ≤ (routing.radius : ℝ) * ‖edgeDifferential e graph x‖ := by
  rw [← routing.correction_differential e x]
  exact routing.correction_bound e _
include routing in
theorem exact_iff_repair (x : V → H) :
    edgeDifferential e graph x = 0 ↔ repair e o x = x := by
  constructor
  · intro hx
    have he := routing.correction_differential e x
    rw [hx, map_zero] at he
    exact (sub_eq_zero.mp he.symm).symm
  · intro hx
    rw [← hx]
    exact differential_repair (graph := graph) (o := o) e x
include routing in
theorem unique_exact_repair (x : V → H) :
    ∃! y : V → H, edgeDifferential e graph y = 0 ∧ y o = x o := by
  refine ⟨repair e o x, ⟨differential_repair (graph := graph) (o := o) e x, repair_anchor e o x⟩, ?_⟩
  intro y hy
  calc
    y = repair e o y := ((routing.exact_iff_repair e y).mp hy.1).symm
    _ = repair e o x := by funext i; simp only [repair, hy.2]
theorem routes_agree_on_actual_residual (other : Routing graph o) (x : V → H) :
    routing.correction e (edgeDifferential e graph x) =
      other.correction e (edgeDifferential e graph x) := by
  rw [routing.correction_differential e, other.correction_differential e]
end Routing
end OverlapTransport
end KomorebiSpace
end
