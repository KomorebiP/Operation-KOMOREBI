module

public import KomorebiPhysics.InfiniteCells
public import KomorebiPhysics.CountableContinuity

/-!
Closed-graph construction of domain-valued infinite cell projectors. Ambient
strong convergence alone is never used to infer membership in an unbounded
operator's domain. Both components of the graph limit are constructed.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DomainAtlas
open Filter
open scoped BigOperators Topology
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable [CompleteSpace H] {T : H →ₗ.[ℂ] H} (P : DomainAtlas T I)

/-- Partial cell sums live in the genuine domain by finite linear closure. -/
def cellPartial (C : Set I) (s : Finset C) (x : T.domain) : T.domain :=
  ∑ i ∈ s, P.project i x

theorem cellPartial_coe (C : Set I) (s : Finset C) (x : T.domain) :
    (P.cellPartial C s x : H) = ∑ i ∈ s, P.atlas.proj i x := by
  simp only [cellPartial, Submodule.coe_sum, project_coe]

theorem action_cellPartial (C : Set I) (s : Finset C) (x : T.domain) :
    T (P.cellPartial C s x) = ∑ i ∈ s, T (P.project i x) := map_sum T.toFun _ s

/-- The limiting pair belongs to the closed graph, before any domain-valued
coarse projector is defined. -/
theorem cell_pair_mem_graph (hT : T.IsClosed) (hG : P.GraphCompatible)
    (C : Set I) (x : T.domain) :
    (P.atlas.cell C x, ∑' i : C, T (P.project i x)) ∈ T.graph := by
  have hx : Tendsto (fun s : Finset C => (P.cellPartial C s x : H)) atTop
      (𝓝 (P.atlas.cell C x)) := by
    simpa only [cellPartial_coe] using P.atlas.cell_sum C (x : H)
  have hTx : Tendsto (fun s : Finset C => T (P.cellPartial C s x)) atTop
      (𝓝 (∑' i : C, T (P.project i x))) := by
    simpa only [action_cellPartial] using ((P.action_hasSum hG x).summable.subtype C).hasSum
  exact hT.mem_of_tendsto (hx.prodMk_nhds hTx)
    (Filter.Eventually.of_forall (fun s => T.mem_graph (P.cellPartial C s x)))

theorem cell_mem_domain (hT : T.IsClosed) (hG : P.GraphCompatible)
    (C : Set I) (x : T.domain) : P.atlas.cell C x ∈ T.domain :=
  LinearPMap.mem_domain_of_mem_graph (P.cell_pair_mem_graph hT hG C x)

/-- Actual bounded ambient cell, restricted using the proved domain membership. -/
def cellProject (hT : T.IsClosed) (hG : P.GraphCompatible) (C : Set I) :
    T.domain →ₗ[ℂ] T.domain where
  toFun x := ⟨P.atlas.cell C x, P.cell_mem_domain hT hG C x⟩
  map_add' x y := Subtype.ext (map_add (P.atlas.cell C) (x : H) (y : H))
  map_smul' c x := Subtype.ext (map_smul (P.atlas.cell C) c (x : H))

theorem cellProject_coe (hT : T.IsClosed) (hG : P.GraphCompatible) (C : Set I)
    (x : T.domain) : (P.cellProject hT hG C x : H) = P.atlas.cell C x := rfl

theorem cell_action_tsum (hT : T.IsClosed) (hG : P.GraphCompatible) (C : Set I)
    (x : T.domain) : T (P.cellProject hT hG C x) = ∑' i : C, T (P.project i x) := by
  exact T.mem_graph_snd_inj (T.mem_graph (P.cellProject hT hG C x))
    (P.cell_pair_mem_graph hT hG C x) rfl

theorem cell_action_hasSum (hT : T.IsClosed) (hG : P.GraphCompatible) (C : Set I)
    (x : T.domain) : HasSum (fun i : C => T (P.project i x)) (T (P.cellProject hT hG C x)) := by
  rw [P.cell_action_tsum]
  exact ((P.action_hasSum hG x).summable.subtype C).hasSum

theorem cell_graph_tendsto (hT : T.IsClosed) (hG : P.GraphCompatible) (C : Set I)
    (x : T.domain) :
    Tendsto (fun s : Finset C => GraphDomain.graphNorm T
      (P.cellPartial C s x - P.cellProject hT hG C x)) atTop (𝓝 0) := by
  apply (GraphDomain.graph_convergence_iff T _ _).mpr
  constructor
  · simpa only [cellPartial_coe, cellProject_coe] using P.atlas.cell_sum C (x : H)
  · simpa only [action_cellPartial] using P.cell_action_hasSum hT hG C x

/-- Also expose an interface for independently established coarse-domain
preservation; closedness/graph compatibility are sufficient, not necessary. -/
def coarsenOfPreserves (f : I → J)
    (hp : ∀ (a : J) (x : T.domain), P.atlas.cell (f ⁻¹' {a}) x ∈ T.domain) :
    DomainAtlas T J where
  atlas := P.atlas.coarsenInfinite f
  preserves := hp

/-- Constructed domain atlas for arbitrary infinite address fibers. -/
def coarsenClosed (hT : T.IsClosed) (hG : P.GraphCompatible) (f : I → J) :
    DomainAtlas T J :=
  P.coarsenOfPreserves f (fun a x => P.cell_mem_domain hT hG (f ⁻¹' {a}) x)

theorem coarsenClosed_project (hT : T.IsClosed) (hG : P.GraphCompatible)
    (f : I → J) (a : J) (x : T.domain) :
    (P.coarsenClosed hT hG f).project a x = P.cellProject hT hG (f ⁻¹' {a}) x := rfl

theorem coarsenClosed_action (hT : T.IsClosed) (hG : P.GraphCompatible)
    (f : I → J) (a : J) (x : T.domain) :
    T ((P.coarsenClosed hT hG f).project a x) =
      ∑' i : f ⁻¹' {a}, T (P.project i x) := P.cell_action_tsum hT hG _ x

/-- Graph compatibility survives regrouping, not just state completeness. -/
theorem coarsenClosed_graph (hT : T.IsClosed) (hG : P.GraphCompatible) (f : I → J) :
    (P.coarsenClosed hT hG f).GraphCompatible := by
  apply DomainAtlas.graph_iff_action.mpr
  intro x
  have h := (P.action_hasSum hG x).tsum_fiberwise f
  exact h.congr_fun (fun a => P.coarsenClosed_action hT hG f a x)

end DomainAtlas
end KomorebiPhysics
