import KomorebiSpace.OverlapPathRepair
import Mathlib.Combinatorics.SimpleGraph.Walk.Operations

set_option autoImplicit false

/-!
# Isometric edge transports without a global trivialization

Reverse edges are inverse isometries. No triangle composition law is assumed.
Transport along a walk is constructed from its edges. Its discrepancy is
bounded by the sum of the actual edge discrepancies.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace HolonomyTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]

structure Connection (V : Type u) (H : Type v)
    [NormedAddCommGroup H] [NormedSpace ℝ H] where
  transport : V → V → H ≃ₗᵢ[ℝ] H
  self_apply : ∀ i z, transport i i z = z
  reverse_apply : ∀ i j z, transport i j (transport j i z) = z

namespace Connection
variable (T : Connection V H) {graph : SimpleGraph V}

def ofFrames (e : OverlapTransport.Frames (V := V) (H := H)) : Connection V H where
  transport := OverlapTransport.transport e
  self_apply := OverlapTransport.transport_self e
  reverse_apply := by
    intro i j z
    rw [OverlapTransport.transport_comp, OverlapTransport.transport_self]

def defect (x : V → H) (i j : V) : H := T.transport i j (x j) - x i

def Parallel (graph : SimpleGraph V) (x : V → H) : Prop :=
  ∀ i j, graph.Adj i j → T.transport i j (x j) = x i

def walkTransport : {i j : V} → graph.Walk i j → H ≃ₗᵢ[ℝ] H
  | _, _, .nil => LinearIsometryEquiv.refl ℝ H
  | i, _, @SimpleGraph.Walk.cons _ _ _ j _ _ p =>
      (walkTransport p).trans (T.transport i j)

@[simp] theorem walkTransport_nil (i : V) (z : H) :
    T.walkTransport (SimpleGraph.Walk.nil (G := graph) (u := i)) z = z := rfl

@[simp] theorem walkTransport_cons {i j k : V} (h : graph.Adj i j)
    (p : graph.Walk j k) (z : H) :
    T.walkTransport (.cons h p) z = T.transport i j (T.walkTransport p z) := rfl

theorem walkTransport_append {i j k : V} (p : graph.Walk i j)
    (q : graph.Walk j k) (z : H) :
    T.walkTransport (p.append q) z = T.walkTransport p (T.walkTransport q z) := by
  induction p with
  | nil => rfl
  | @cons i j k h p ih =>
    simpa only [SimpleGraph.Walk.cons_append, walkTransport_cons] using
      congrArg (T.transport i j) (ih q)

/-- Reverse edge consistency supplies inverse transport along every reversed walk. -/
theorem walkTransport_reverse {i j : V} (p : graph.Walk i j) (z : H) :
    T.walkTransport p.reverse (T.walkTransport p z) = z := by
  induction p with
  | nil => rfl
  | @cons i k j h p ih =>
    rw [SimpleGraph.Walk.reverse_cons,
      walkTransport_append, walkTransport_cons, walkTransport_nil, walkTransport_cons,
      T.reverse_apply]
    exact ih

theorem walkTransport_reverse_eq_symm {i j : V} (p : graph.Walk i j) (z : H) :
    T.walkTransport p.reverse z = (T.walkTransport p).symm z := by
  have he := T.walkTransport_reverse p ((T.walkTransport p).symm z)
  simpa only [LinearIsometryEquiv.apply_symm_apply] using he

theorem parallel_walk (x : V → H) (hx : T.Parallel graph x)
    {i j : V} (p : graph.Walk i j) : T.walkTransport p (x j) = x i := by
  induction p with
  | nil => rfl
  | cons h p ih => rw [walkTransport_cons, ih, hx _ _ h]

theorem parallel_iff_all_walks (x : V → H) :
    T.Parallel graph x ↔ ∀ i j (p : graph.Walk i j), T.walkTransport p (x j) = x i := by
  constructor
  · intro hx i j p; exact T.parallel_walk x hx p
  · intro hx i j h
    exact hx i j (.cons h .nil)

section Finite
variable [Fintype V]
abbrev Edges (graph : SimpleGraph V) := OverlapTransport.Edges graph

def differentialLinear (graph : SimpleGraph V) : (V → H) →ₗ[ℝ] (Edges graph → H) where
  toFun x a := T.defect x a.val.1 a.val.2
  map_add' := by
    intro x y
    funext a
    simp only [defect, Pi.add_apply, map_add]
    abel
  map_smul' := by
    intro c x
    funext a
    simp [defect, map_smul, smul_sub]

theorem differentialLinear_bound (graph : SimpleGraph V) (x : V → H) :
    ‖T.differentialLinear graph x‖ ≤ 2 * ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (mul_nonneg (by norm_num) (norm_nonneg x))).mpr
  intro a
  change ‖T.transport a.val.1 a.val.2 (x a.val.2) - x a.val.1‖ ≤ _
  calc
    _ ≤ ‖T.transport a.val.1 a.val.2 (x a.val.2)‖ + ‖x a.val.1‖ := norm_sub_le _ _
    _ = ‖x a.val.2‖ + ‖x a.val.1‖ := by rw [LinearIsometryEquiv.norm_map]
    _ ≤ 2 * ‖x‖ := by
      have hi := norm_le_pi_norm x a.val.1
      have hj := norm_le_pi_norm x a.val.2
      linarith

def differential (graph : SimpleGraph V) : (V → H) →L[ℝ] (Edges graph → H) :=
  (T.differentialLinear graph).mkContinuous 2 (T.differentialLinear_bound graph)

@[simp] theorem differential_apply (x : V → H) (a : Edges graph) :
    T.differential graph x a = T.defect x a.val.1 a.val.2 := rfl

theorem differential_opNorm (graph : SimpleGraph V) : ‖T.differential graph‖ ≤ 2 := by
  apply (T.differential graph).opNorm_le_bound (by norm_num)
  exact T.differentialLinear_bound graph

theorem parallel_iff_differential_zero (x : V → H) :
    T.Parallel graph x ↔ T.differential graph x = 0 := by
  constructor
  · intro hx; funext a; exact sub_eq_zero.mpr (hx _ _ a.property)
  · intro hx i j h
    exact sub_eq_zero.mp (congrFun hx (⟨(i,j),h⟩ : Edges graph))

theorem walk_error (x : V → H) {i j : V} (p : graph.Walk i j) :
    ‖T.walkTransport p (x j) - x i‖ ≤ (p.length : ℝ) * ‖T.differential graph x‖ := by
  induction p with
  | nil => simp
  | @cons i k j h p ih =>
    have he : ‖T.transport i k (x k) - x i‖ ≤ ‖T.differential graph x‖ :=
      norm_le_pi_norm (T.differential graph x) ⟨(i,k),h⟩
    calc
      _ = ‖T.transport i k (T.walkTransport p (x j) - x k) +
          (T.transport i k (x k) - x i)‖ := by
            rw [walkTransport_cons, map_sub]
            congr 1
            abel
      _ ≤ ‖T.transport i k (T.walkTransport p (x j) - x k)‖ +
          ‖T.transport i k (x k) - x i‖ := norm_add_le _ _
      _ = ‖T.walkTransport p (x j) - x k‖ +
          ‖T.transport i k (x k) - x i‖ := by rw [LinearIsometryEquiv.norm_map]
      _ ≤ (p.length : ℝ) * ‖T.differential graph x‖ + ‖T.differential graph x‖ :=
        add_le_add ih he
      _ = ((SimpleGraph.Walk.cons h p).length : ℝ) * ‖T.differential graph x‖ := by
        simp only [SimpleGraph.Walk.length_cons, Nat.cast_add, Nat.cast_one]
        ring

@[simp] theorem ofFrames_differential
    (e : OverlapTransport.Frames (V := V) (H := H)) (x : V → H) :
    (ofFrames e).differential graph x = OverlapTransport.edgeDifferential e graph x := rfl

end Finite
end Connection
end HolonomyTransport
end KomorebiSpace
end
