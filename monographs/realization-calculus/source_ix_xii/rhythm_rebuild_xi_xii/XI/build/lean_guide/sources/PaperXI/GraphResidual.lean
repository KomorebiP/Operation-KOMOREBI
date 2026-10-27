import PaperXI.ContinuousHolonomyResidual
import PaperXI.GraphTransport
import PaperXI.GraphTree
import Mathlib.Analysis.Normed.Module.FiniteDimension

/-! Paper XI, 14.6 and 14.7 on the actual rooted graph paths. Finite dimensionality
makes the given edge equivalences and their actual inverses continuous for the
specified norms. Parallel edges and self-loops keep their identities. -/
set_option autoImplicit false
noncomputable section

namespace PaperXI.GraphResidual

open Quiver GraphTree

variable {α : Type*} [Quiver α]
variable {V W : α → Type*}
variable [∀ u, NormedAddCommGroup (V u)] [∀ u, NormedSpace ℂ (V u)]
variable [∀ u, FiniteDimensional ℂ (V u)]
variable [∀ u, NormedAddCommGroup (W u)] [∀ u, NormedSpace ℂ (W u)]
variable [∀ u, FiniteDimensional ℂ (W u)]

/-- The bounded transport is exactly the algebraic transport on the given walk. -/
def pathL (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    {u v : α} (p : GraphTransport.Walk u v) : V u ≃L[ℂ] V v :=
  (GraphTransport.path A p).toContinuousLinearEquiv

@[simp] theorem pathL_toLinearEquiv
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    {u v : α} (p : GraphTransport.Walk u v) :
    (pathL A p).toLinearEquiv = GraphTransport.path A p := rfl

@[simp] theorem pathL_apply
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    {u v : α} (p : GraphTransport.Walk u v) (x : V u) :
    pathL A p x = GraphTransport.path A p x := rfl

@[simp] theorem pathL_symm_apply
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    {u v : α} (p : GraphTransport.Walk u v) (x : V v) :
    (pathL A p).symm x = (GraphTransport.path A p).symm x := rfl

@[simp] theorem pathL_reverse
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    {u v : α} (p : GraphTransport.Walk u v) :
    pathL A p.reverse = (pathL A p).symm := by
  ext x
  exact LinearEquiv.congr_fun (GraphTransport.reverse A p) x

@[simp] theorem pathL_comp
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    {u v w : α} (p : GraphTransport.Walk u v) (q : GraphTransport.Walk v w) :
    pathL A (p.comp q) = (pathL A p).trans (pathL A q) := by
  ext x
  exact LinearEquiv.congr_fun (GraphTransport.comp A p q) x

variable {r : α}

/-- The continuous vertex gauge is constructed from the actual tree paths. -/
def gauge (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (v : α) : V v ≃L[ℂ] W v :=
  ContinuousHolonomyResidual.transported U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T v)) (pathL B (GraphTree.rootPath T v))

@[simp] theorem gauge_toLinearEquiv (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (v : α) :
    (gauge T A B U v).toLinearEquiv = HolonomyResidual.transported U
      (GraphTransport.path A (GraphTree.rootPath T v)) (GraphTransport.path B (GraphTree.rootPath T v)) := rfl

@[simp] theorem gauge_apply (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (v : α) (x : V v) :
    gauge T A B U v x = GraphTransport.path B (GraphTree.rootPath T v)
      (U ((GraphTransport.path A (GraphTree.rootPath T v)).symm x)) := rfl

@[simp] theorem gauge_root (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) : gauge T A B U r = U.toContinuousLinearEquiv := by
  ext x
  simp only [gauge_apply, GraphTree.rootPath_root]
  rfl

/-- The constructed gauge satisfies the selected tree-edge equation. -/
theorem gauge_parent (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (a : {a : α // a ≠ r}) (x : V (T.parent a)) :
    gauge T A B U a.val (GraphTransport.edge A (T.parentEdge a) x) =
      GraphTransport.edge B (T.parentEdge a) (gauge T A B U (T.parent a) x) := by
  simp only [gauge_apply]
  rw [← GraphTree.rootPath_parent T a]
  change GraphTransport.edge B (T.parentEdge a)
    (GraphTransport.path B (GraphTree.rootPath T (T.parent a))
      (U ((GraphTransport.path A (GraphTree.rootPath T (T.parent a))).symm
        ((GraphTransport.edge A (T.parentEdge a)).symm
          (GraphTransport.edge A (T.parentEdge a) x))))) = _
  rw [LinearEquiv.symm_apply_apply]

/-- The literal residual of the constructed gauges and original edge maps. -/
def edgeResidual (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) : V u →L[ℂ] W v :=
  (gauge T A B U v).toContinuousLinearMap.comp
      (A e).toContinuousLinearEquiv.toContinuousLinearMap -
    (B e).toContinuousLinearEquiv.toContinuousLinearMap.comp
      (gauge T A B U u).toContinuousLinearMap

/-- The defect uses the actual tree transports and the actual edge. -/
def cycleDefect (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) : V r →L[ℂ] W r :=
  ContinuousHolonomyResidual.cycleDefect U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T u)) (pathL A (GraphTree.rootPath T v))
    (pathL B (GraphTree.rootPath T u)) (pathL B (GraphTree.rootPath T v))
    (A e).toContinuousLinearEquiv (B e).toContinuousLinearEquiv

theorem cycleDefect_toLinearMap (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    (cycleDefect T A B U e).toLinearMap = HolonomyResidual.cycleDefect U
      (GraphTransport.path A (GraphTree.rootPath T u)) (GraphTransport.path A (GraphTree.rootPath T v))
      (GraphTransport.path B (GraphTree.rootPath T u)) (GraphTransport.path B (GraphTree.rootPath T v))
      (A e) (B e) := rfl

theorem edgeResidual_toLinearMap (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    (edgeResidual T A B U e).toLinearMap = HolonomyResidual.edgeResidual U
      (GraphTransport.path A (GraphTree.rootPath T u)) (GraphTransport.path A (GraphTree.rootPath T v))
      (GraphTransport.path B (GraphTree.rootPath T u)) (GraphTransport.path B (GraphTree.rootPath T v))
      (A e) (B e) := rfl

/-- The defect compares the transports on the literal based fundamental loop. -/
theorem cycleDefect_loop (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    (cycleDefect T A B U e).toLinearMap =
      U.toLinearMap.comp (GraphTransport.path A
        (((GraphTree.rootPath T u).cons (Sum.inl e)).comp (GraphTree.rootPath T v).reverse)).toLinearMap -
      (GraphTransport.path B
        (((GraphTree.rootPath T u).cons (Sum.inl e)).comp (GraphTree.rootPath T v).reverse)).toLinearMap.comp
          U.toLinearMap := by
  rw (config := { transparency := .all })
    [GraphTransport.comp A, GraphTransport.comp B,
      GraphTransport.reverse A, GraphTransport.reverse B,
      GraphTransport.cons A, GraphTransport.cons B]
  ext x
  simp [cycleDefect, ContinuousHolonomyResidual.cycleDefect]

/-- Exact graph identity, in particular valid for every non-tree edge. -/
theorem residual_factorization (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    edgeResidual T A B U e = (pathL B (GraphTree.rootPath T v)).toContinuousLinearMap.comp
      ((cycleDefect T A B U e).comp (pathL A (GraphTree.rootPath T u)).symm.toContinuousLinearMap) :=
  ContinuousHolonomyResidual.residual_factorization U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T u)) (pathL A (GraphTree.rootPath T v))
    (pathL B (GraphTree.rootPath T u)) (pathL B (GraphTree.rootPath T v))
    (A e).toContinuousLinearEquiv (B e).toContinuousLinearEquiv

theorem residual_zero_iff (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    edgeResidual T A B U e = 0 ↔ cycleDefect T A B U e = 0 :=
  ContinuousHolonomyResidual.residual_zero_iff U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T u)) (pathL A (GraphTree.rootPath T v))
    (pathL B (GraphTree.rootPath T u)) (pathL B (GraphTree.rootPath T v))
    (A e).toContinuousLinearEquiv (B e).toContinuousLinearEquiv

/-- The precise bound has only the two path conditioning factors. -/
theorem residual_norm_bound (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    ‖edgeResidual T A B U e‖ ≤
      ‖(pathL B (GraphTree.rootPath T v)).toContinuousLinearMap‖ * ‖cycleDefect T A B U e‖ *
        ‖(pathL A (GraphTree.rootPath T u)).symm.toContinuousLinearMap‖ :=
  ContinuousHolonomyResidual.residual_norm_bound U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T u)) (pathL A (GraphTree.rootPath T v))
    (pathL B (GraphTree.rootPath T u)) (pathL B (GraphTree.rootPath T v))
    (A e).toContinuousLinearEquiv (B e).toContinuousLinearEquiv

theorem uniform_bound (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (C_B ε C_A : ℝ)
    (hB : ∀ v, ‖(pathL B (GraphTree.rootPath T v)).toContinuousLinearMap‖ ≤ C_B)
    (hD : ∀ {u v : α} (e : u ⟶ v), ‖cycleDefect T A B U e‖ ≤ ε)
    (hA : ∀ u, ‖(pathL A (GraphTree.rootPath T u)).symm.toContinuousLinearMap‖ ≤ C_A)
    {u v : α} (e : u ⟶ v) :
    ‖edgeResidual T A B U e‖ ≤ C_B * ε * C_A :=
  ContinuousHolonomyResidual.uniform_bound U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T u)) (pathL A (GraphTree.rootPath T v))
    (pathL B (GraphTree.rootPath T u)) (pathL B (GraphTree.rootPath T v))
    (A e).toContinuousLinearEquiv (B e).toContinuousLinearEquiv
    C_B ε C_A (hB v) (hD e) (hA u)

/-- Uniform control is a bound on the mixed factor, with both actual norms. -/
theorem uniform_product_bound (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (C ε : ℝ)
    (hC : ∀ {u v : α} (_e : u ⟶ v),
      ‖(pathL B (GraphTree.rootPath T v)).toContinuousLinearMap‖ *
        ‖(pathL A (GraphTree.rootPath T u)).symm.toContinuousLinearMap‖ ≤ C)
    (hD : ∀ {u v : α} (e : u ⟶ v), ‖cycleDefect T A B U e‖ ≤ ε)
    {u v : α} (e : u ⟶ v) : ‖edgeResidual T A B U e‖ ≤ C * ε :=
  ContinuousHolonomyResidual.product_conditioning_bound U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T u)) (pathL A (GraphTree.rootPath T v))
    (pathL B (GraphTree.rootPath T u)) (pathL B (GraphTree.rootPath T v))
    (A e).toContinuousLinearEquiv (B e).toContinuousLinearEquiv C ε (hC e) (hD e)

/-- Only the tested chords require defect bounds. Tree-edge errors are not
included as hypotheses. -/
theorem uniform_chord_bound (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (C_B ε C_A : ℝ)
    (hB : ∀ v, ‖(pathL B (GraphTree.rootPath T v)).toContinuousLinearMap‖ ≤ C_B)
    (hD : ∀ e : GraphTree.Chord T, ‖cycleDefect T A B U e.val.2.2‖ ≤ ε)
    (hA : ∀ u, ‖(pathL A (GraphTree.rootPath T u)).symm.toContinuousLinearMap‖ ≤ C_A)
    (e : GraphTree.Chord T) :
    ‖edgeResidual T A B U e.val.2.2‖ ≤ C_B * ε * C_A :=
  ContinuousHolonomyResidual.uniform_bound U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T e.val.1))
    (pathL A (GraphTree.rootPath T e.val.2.1))
    (pathL B (GraphTree.rootPath T e.val.1))
    (pathL B (GraphTree.rootPath T e.val.2.1))
    (A e.val.2.2).toContinuousLinearEquiv (B e.val.2.2).toContinuousLinearEquiv
    C_B ε C_A (hB e.val.2.1) (hD e) (hA e.val.1)

/-- Chord-only uniform control using the exact mixed path factor. -/
theorem uniform_chord_product_bound (T : GraphTree.Rooted α r)
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) (C ε : ℝ)
    (hC : ∀ e : GraphTree.Chord T,
      ‖(pathL B (GraphTree.rootPath T e.val.2.1)).toContinuousLinearMap‖ *
        ‖(pathL A (GraphTree.rootPath T e.val.1)).symm.toContinuousLinearMap‖ ≤ C)
    (hD : ∀ e : GraphTree.Chord T, ‖cycleDefect T A B U e.val.2.2‖ ≤ ε)
    (e : GraphTree.Chord T) : ‖edgeResidual T A B U e.val.2.2‖ ≤ C * ε :=
  ContinuousHolonomyResidual.product_conditioning_bound U.toContinuousLinearEquiv
    (pathL A (GraphTree.rootPath T e.val.1))
    (pathL A (GraphTree.rootPath T e.val.2.1))
    (pathL B (GraphTree.rootPath T e.val.1))
    (pathL B (GraphTree.rootPath T e.val.2.1))
    (A e.val.2.2).toContinuousLinearEquiv (B e.val.2.2).toContinuousLinearEquiv
    C ε (hC e) (hD e)

/-- Connectedness supplies the tree used in the quantitative statement. -/
theorem connected_residual_bound (hc : GraphTree.Connected (α := α))
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[ℂ] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[ℂ] W v))
    (U : V r ≃ₗ[ℂ] W r) {u v : α} (e : u ⟶ v) :
    let T := GraphTree.ofConnected r hc
    ‖edgeResidual T A B U e‖ ≤
      ‖(pathL B (GraphTree.rootPath T v)).toContinuousLinearMap‖ * ‖cycleDefect T A B U e‖ *
        ‖(pathL A (GraphTree.rootPath T u)).symm.toContinuousLinearMap‖ :=
  residual_norm_bound (GraphTree.ofConnected r hc) A B U e

end PaperXI.GraphResidual
