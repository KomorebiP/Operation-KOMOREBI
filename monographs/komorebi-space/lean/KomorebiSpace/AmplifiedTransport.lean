import KomorebiSpace.HolonomyTransport
import Mathlib.Combinatorics.SimpleGraph.Walk.Operations

set_option autoImplicit false

/-!
# Bounded invertible transports and actual path amplification

Each edge is a continuous linear equivalence, not assumed isometric or flat.
Walk products retain their order. The error estimate is derived from the
transported residual sum and recursive operator-norm gain.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace AmplifiedTransport
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]

structure Connection (V : Type u) (H : Type v)
    [NormedAddCommGroup H] [NormedSpace ℝ H] where
  transport : V → V → H ≃L[ℝ] H
  self_apply : ∀ i z, transport i i z = z
  reverse_apply : ∀ i j z, transport i j (transport j i z) = z

namespace Connection
variable (T : Connection V H) {graph : SimpleGraph V}

/-- The older isometric connection is embedded without changing its edge maps. -/
def ofIsometric (T : HolonomyTransport.Connection V H) : Connection V H where
  transport i j := (T.transport i j).toContinuousLinearEquiv
  self_apply := T.self_apply
  reverse_apply := T.reverse_apply

/-- A flat subclass with arbitrary bounded invertible local frames. -/
def ofFrames (e : V → H ≃L[ℝ] H) : Connection V H where
  transport i j := (e j).symm.trans (e i)
  self_apply := by intro i z; exact (e i).apply_symm_apply z
  reverse_apply := by
    intro i j z
    change e i ((e j).symm (e j ((e i).symm z))) = z
    rw [ContinuousLinearEquiv.symm_apply_apply, ContinuousLinearEquiv.apply_symm_apply]

def defect (x : V → H) (i j : V) : H := T.transport i j (x j) - x i

def Parallel (graph : SimpleGraph V) (x : V → H) : Prop :=
  ∀ i j, graph.Adj i j → T.transport i j (x j) = x i

def walkTransport : {i j : V} → graph.Walk i j → H ≃L[ℝ] H
  | _, _, .nil => ContinuousLinearEquiv.refl ℝ H
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
  simpa only [ContinuousLinearEquiv.apply_symm_apply] using he

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

/-- A path gain: one direct edge defect plus amplified later defects. -/
def walkGain : {i j : V} → graph.Walk i j → ℝ
  | _, _, .nil => 0
  | i, _, @SimpleGraph.Walk.cons _ _ _ j _ _ p =>
      1 + ‖(T.transport i j).toContinuousLinearMap‖ * walkGain p

@[simp] theorem walkGain_nil (i : V) :
    T.walkGain (SimpleGraph.Walk.nil (G := graph) (u := i)) = 0 := rfl

@[simp] theorem walkGain_cons {i j k : V} (h : graph.Adj i j)
    (p : graph.Walk j k) : T.walkGain (.cons h p) =
      1 + ‖(T.transport i j).toContinuousLinearMap‖ * T.walkGain p := rfl

theorem walkGain_nonneg {i j : V} (p : graph.Walk i j) : 0 ≤ T.walkGain p := by
  induction p with
  | nil => exact le_rfl
  | cons h p ih =>
    rw [walkGain_cons]
    exact add_nonneg zero_le_one (mul_nonneg (norm_nonneg _) ih)

/-- Product of the edge norm bounds in their original path order. -/
def walkProduct : {i j : V} → graph.Walk i j → ℝ
  | _, _, .nil => 1
  | i, _, @SimpleGraph.Walk.cons _ _ _ j _ _ p =>
      ‖(T.transport i j).toContinuousLinearMap‖ * walkProduct p

theorem walkGain_append {i j k : V} (p : graph.Walk i j) (q : graph.Walk j k) :
    T.walkGain (p.append q) = T.walkGain p + T.walkProduct p * T.walkGain q := by
  induction p with
  | nil => simp [walkGain, walkProduct]
  | @cons i j k h p ih =>
    simp only [SimpleGraph.Walk.cons_append, walkGain_cons, walkProduct, ih]
    ring

theorem walkGain_le_length (hc : ∀ i j, graph.Adj i j →
    ‖(T.transport i j).toContinuousLinearMap‖ ≤ 1)
    {i j : V} (p : graph.Walk i j) : T.walkGain p ≤ (p.length : ℝ) := by
  induction p with
  | nil => simp
  | @cons i k j h p ih =>
    rw [walkGain_cons, SimpleGraph.Walk.length_cons, Nat.cast_add, Nat.cast_one]
    have hm := mul_le_mul_of_nonneg_right (hc i k h) (T.walkGain_nonneg p)
    rw [one_mul] at hm
    linarith

/-- A quantitative residual sum, with each term expressed in the starting fiber. -/
def walkSum (r : OverlapTransport.Edges graph → H) :
    {i j : V} → graph.Walk i j → H
  | _, _, .nil => 0
  | i, _, @SimpleGraph.Walk.cons _ _ _ j _ h p =>
      r ⟨(i,j),h⟩ + T.transport i j (walkSum r p)

theorem walkSum_defect (x : V → H) {i j : V} (p : graph.Walk i j) :
    T.walkSum (fun a => T.defect x a.val.1 a.val.2) p =
      T.walkTransport p (x j) - x i := by
  induction p with
  | nil => simp [walkSum]
  | @cons i k j h p ih =>
    change T.defect x i k + T.transport i k (T.walkSum _ p) = _
    rw [ih, map_sub, walkTransport_cons]
    unfold defect
    abel

section Finite
variable [Fintype V]
abbrev Edges (graph : SimpleGraph V) := OverlapTransport.Edges graph

/-- Only measured edges determine this finite bound. -/
def edgeBound (graph : SimpleGraph V) : ℝ :=
  ‖fun a : Edges graph => (T.transport a.val.1 a.val.2).toContinuousLinearMap‖

theorem edgeBound_nonneg (graph : SimpleGraph V) : 0 ≤ T.edgeBound graph := norm_nonneg _

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
    ‖T.differentialLinear graph x‖ ≤ (T.edgeBound graph + 1) * ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg
    (mul_nonneg (add_nonneg (T.edgeBound_nonneg graph) zero_le_one) (norm_nonneg _))).mpr
  intro a
  change ‖T.transport a.val.1 a.val.2 (x a.val.2) - x a.val.1‖ ≤ _
  have hm : ‖(T.transport a.val.1 a.val.2).toContinuousLinearMap‖ ≤ T.edgeBound graph :=
    norm_le_pi_norm (fun a : Edges graph => (T.transport a.val.1 a.val.2).toContinuousLinearMap) a
  calc
    _ ≤ ‖T.transport a.val.1 a.val.2 (x a.val.2)‖ + ‖x a.val.1‖ := norm_sub_le _ _
    _ ≤ ‖(T.transport a.val.1 a.val.2).toContinuousLinearMap‖ * ‖x a.val.2‖ + ‖x a.val.1‖ :=
      add_le_add ((T.transport a.val.1 a.val.2).toContinuousLinearMap.le_opNorm _) le_rfl
    _ ≤ T.edgeBound graph * ‖x‖ + ‖x‖ :=
      add_le_add (mul_le_mul hm (norm_le_pi_norm x a.val.2) (norm_nonneg _)
        (T.edgeBound_nonneg graph)) (norm_le_pi_norm x a.val.1)
    _ = _ := by ring

def differential (graph : SimpleGraph V) : (V → H) →L[ℝ] (Edges graph → H) :=
  (T.differentialLinear graph).mkContinuous (T.edgeBound graph + 1)
    (T.differentialLinear_bound graph)

@[simp] theorem differential_apply (x : V → H) (a : Edges graph) :
    T.differential graph x a = T.defect x a.val.1 a.val.2 := rfl

theorem differential_bound (graph : SimpleGraph V) (x : V → H) :
    ‖T.differential graph x‖ ≤ (T.edgeBound graph + 1) * ‖x‖ :=
  T.differentialLinear_bound graph x

theorem differential_opNorm (graph : SimpleGraph V) :
    ‖T.differential graph‖ ≤ T.edgeBound graph + 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ (add_nonneg (T.edgeBound_nonneg graph) zero_le_one)
  exact T.differential_bound graph

theorem parallel_iff_differential_zero (x : V → H) :
    T.Parallel graph x ↔ T.differential graph x = 0 := by
  constructor
  · intro hx; funext a; exact sub_eq_zero.mpr (hx _ _ a.property)
  · intro hx i j h
    exact sub_eq_zero.mp (congrFun hx (⟨(i,j),h⟩ : Edges graph))

theorem walkSum_bound (r : Edges graph → H) {i j : V} (p : graph.Walk i j) :
    ‖T.walkSum r p‖ ≤ T.walkGain p * ‖r‖ := by
  induction p with
  | nil => simp [walkSum]
  | @cons i k j h p ih =>
    change ‖r ⟨(i,k),h⟩ + T.transport i k (T.walkSum r p)‖ ≤ _
    calc
      _ ≤ ‖r ⟨(i,k),h⟩‖ + ‖T.transport i k (T.walkSum r p)‖ := norm_add_le _ _
      _ ≤ ‖r‖ + ‖(T.transport i k).toContinuousLinearMap‖ * ‖T.walkSum r p‖ :=
        add_le_add (norm_le_pi_norm r ⟨(i,k),h⟩)
          ((T.transport i k).toContinuousLinearMap.le_opNorm _)
      _ ≤ ‖r‖ + ‖(T.transport i k).toContinuousLinearMap‖ * (T.walkGain p * ‖r‖) :=
        add_le_add le_rfl (mul_le_mul_of_nonneg_left ih (norm_nonneg _))
      _ = _ := by rw [walkGain_cons]; ring

theorem walk_error (x : V → H) {i j : V} (p : graph.Walk i j) :
    ‖T.walkTransport p (x j) - x i‖ ≤ T.walkGain p * ‖T.differential graph x‖ := by
  rw [← T.walkSum_defect x p]
  exact T.walkSum_bound (T.differential graph x) p

@[simp] theorem ofIsometric_differential (S : HolonomyTransport.Connection V H)
    (x : V → H) : (ofIsometric S).differential graph x = S.differential graph x := rfl

end Finite
end Connection
end AmplifiedTransport
end KomorebiSpace
end
