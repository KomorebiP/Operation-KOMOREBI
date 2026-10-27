module
public import GraphSchedules
import all GraphSchedules
public import Mathlib.LinearAlgebra.Pi
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII item 6.5.
Constructs the actual forward-substitution solution in dependent block spaces.
Diagonal invertibility is represented by local linear equivalences. Transfers
are arbitrary linear maps on graph edges. No solution or solve equation is assumed.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
namespace DAG.Graph
open scoped BigOperators Classical
variable {V K : Type*} [Fintype V] [Field K]
variable (G : DAG.Graph V) (X : V → Type*)
variable [∀ v, AddCommGroup (X v)] [∀ v, Module K (X v)]
variable (D : ∀ v, X v ≃ₗ[K] X v) (T : ∀ b a, X a →ₗ[K] X b)

/-- Block diagonal plus the actual graph-edge transfers. -/
noncomputable def triangularAction (x : ∀ v, X v) (v : V) : X v :=
  D v (x v) + ∑ u : {u // G.edge u v}, T v u.val (x u.val)

/-- Well-founded forward substitution on the constructed acyclic graph. -/
noncomputable def solve (rhs : ∀ v, X v) : ∀ v, X v :=
  G.wellFounded.fix (fun v rec =>
    (D v).symm (rhs v - ∑ u : {u // G.edge u v}, T v u.val (rec u.val u.property)))

theorem solve_eq (rhs : ∀ v, X v) (v : V) :
    G.solve X D T rhs v = (D v).symm
      (rhs v - ∑ u : {u // G.edge u v}, T v u.val (G.solve X D T rhs u.val)) :=
  WellFounded.fix_eq G.wellFounded _ v

/-- The computed vector solves the actual block equations. -/
theorem solve_correct (rhs : ∀ v, X v) :
    G.triangularAction X D T (G.solve X D T rhs) = rhs := by
  funext v
  unfold triangularAction
  rw [G.solve_eq X D T rhs v, LinearEquiv.apply_symm_apply]
  exact sub_add_cancel _ _

/-- A competitor satisfying the equations must equal the constructed solution. -/
theorem solve_unique (rhs x : ∀ v, X v)
    (hx : G.triangularAction X D T x = rhs) : x = G.solve X D T rhs := by
  funext v
  induction v using G.wellFounded.induction with
  | h v ih =>
    have hv := congrFun hx v
    change D v (x v) + ∑ u : {u // G.edge u v}, T v u.val (x u.val) = rhs v at hv
    have hsum : (∑ u : {u // G.edge u v}, T v u.val (x u.val)) =
        ∑ u : {u // G.edge u v}, T v u.val (G.solve X D T rhs u.val) := by
      apply Finset.sum_congr rfl
      intro u _
      rw [ih u.val u.property]
    rw [hsum] at hv
    rw [G.solve_eq X D T rhs v]
    apply (D v).injective
    rw [LinearEquiv.apply_symm_apply]
    exact eq_sub_iff_add_eq.mpr hv

/-- In particular, the block triangular operator is bijective. -/
theorem triangular_bijective : Function.Bijective (G.triangularAction X D T) := by
  constructor
  · intro x y h
    have hx := G.solve_unique X D T (G.triangularAction X D T y) x h
    have hy := G.solve_unique X D T (G.triangularAction X D T y) y rfl
    exact hx.trans hy.symm
  · intro rhs
    exact ⟨G.solve X D T rhs, G.solve_correct X D T rhs⟩

/-- A single stage only reads strict predecessors. -/
theorem local_solve_independent (rhs : ∀ v, X v) (v : V) (x y : ∀ v, X v)
    (h : ∀ u, G.level u < G.level v → x u = y u) :
    (D v).symm (rhs v - ∑ u : {u // G.edge u v}, T v u.val (x u.val)) =
      (D v).symm (rhs v - ∑ u : {u // G.edge u v}, T v u.val (y u.val)) := by
  congr 2
  apply Finset.sum_congr rfl
  intro u _
  rw [h u.val (G.edge_level u.property)]

/-- Stage evaluator: update all tasks whose canonical level is the next stage. -/
noncomputable def stagedSolve (rhs : ∀ v, X v) : ℕ → ∀ v, X v
  | 0 => fun _ => 0
  | k+1 => fun v => if G.level v = k+1 then
      (D v).symm (rhs v - ∑ u : {u // G.edge u v}, T v u.val (stagedSolve rhs k u.val))
      else stagedSolve rhs k v

theorem stagedSolve_correct_through (rhs : ∀ v, X v) (k : ℕ) :
    ∀ v, G.level v ≤ k → G.stagedSolve X D T rhs k v = G.solve X D T rhs v := by
  induction k with
  | zero =>
    intro v hv
    have := G.level_positive v
    omega
  | succ k ih =>
    intro v hv
    by_cases he : G.level v = k+1
    · simp only [stagedSolve,he,ite_true]
      rw [G.solve_eq X D T rhs v]
      congr 2
      apply Finset.sum_congr rfl
      intro u _
      have hu := G.edge_level u.property
      rw [ih u.val (by omega)]
    · simp only [stagedSolve,he,ite_false]
      exact ih v (by omega)

/-- The concrete parallel-stage evaluator finishes at the optimal DAG depth. -/
theorem level_schedule_solves (rhs : ∀ v, X v) :
    G.triangularAction X D T (G.stagedSolve X D T rhs G.depth) = rhs := by
  have he : G.stagedSolve X D T rhs G.depth = G.solve X D T rhs := by
    funext v
    exact G.stagedSolve_correct_through X D T rhs G.depth v (G.level_le_depth v)
  rw [he]
  exact G.solve_correct X D T rhs

end DAG.Graph
end KomorebiPaperVIII

-- FIFTH BLOCK AXIOM AUDIT
#print axioms KomorebiPaperVIII.DAG.Graph.solve_eq
#print axioms KomorebiPaperVIII.DAG.Graph.solve_correct
#print axioms KomorebiPaperVIII.DAG.Graph.solve_unique
#print axioms KomorebiPaperVIII.DAG.Graph.triangular_bijective
#print axioms KomorebiPaperVIII.DAG.Graph.local_solve_independent
#print axioms KomorebiPaperVIII.DAG.Graph.stagedSolve_correct_through
#print axioms KomorebiPaperVIII.DAG.Graph.level_schedule_solves
#print axioms KomorebiPaperVIII.DAG.Graph.triangularAction
#print axioms KomorebiPaperVIII.DAG.Graph.solve
#print axioms KomorebiPaperVIII.DAG.Graph.stagedSolve
