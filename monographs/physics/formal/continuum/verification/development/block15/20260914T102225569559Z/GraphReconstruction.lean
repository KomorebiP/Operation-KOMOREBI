module
public import KomorebiPhysics.AtlasReconstruction
public import KomorebiPhysics.SpectralGraph

/-! Graph-domain reconstruction. Every application of the unbounded operator
has a domain-valued input. The output limit is in the ambient Hilbert norm. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace GraphReconstruction
open Filter
open scoped Topology BigOperators
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H} (P : DomainAtlas T I)

/-- Apply T to the actual domain-valued finite sum, then apply the bounded cutoff. -/
def reconstructed (s : Finset I) (x : T.domain) : H :=
  AtlasReconstruction.cutoff P.atlas s (T (P.partialSum s x))

/-- The exact source identity (6.66), before any convergence argument. -/
theorem error_identity (s : Finset I) (x : T.domain) :
    reconstructed P s x - T x =
      AtlasReconstruction.cutoff P.atlas s (T (P.partialSum s x)-T x) +
      (AtlasReconstruction.cutoff P.atlas s (T x)-T x) := by
  simp only [reconstructed, map_sub]
  abel

theorem error_bound (s : Finset I) (x : T.domain) :
    ‖reconstructed P s x-T x‖ ≤ ‖T (P.partialSum s x)-T x‖ +
      ‖AtlasReconstruction.cutoff P.atlas s (T x)-T x‖ := by
  rw [error_identity]
  exact (norm_add_le _ _).trans (add_le_add
    (StrongReconstruction.contraction_apply _ (AtlasReconstruction.cutoff_norm_le P.atlas s) _) le_rfl)

/-- Graph-norm input error controls the first contribution; the ordinary
cutoff tail of T x remains explicitly present. -/
theorem graph_error_bound (s : Finset I) (x : T.domain) :
    ‖reconstructed P s x-T x‖ ≤ GraphDomain.graphNorm T (P.partialSum s x-x) +
      ‖AtlasReconstruction.cutoff P.atlas s (T x)-T x‖ := by
  apply (error_bound P s x).trans
  apply add_le_add _ le_rfl
  simpa only [map_sub] using GraphDomain.action_norm_le_graphNorm T (P.partialSum s x-x)

/-- Convergence follows from graph compatibility, not from state convergence alone. -/
theorem tendsto (hg : P.GraphCompatible) (x : T.domain) :
    Tendsto (fun s : Finset I => reconstructed P s x) atTop (𝓝 (T x)) :=
  StrongReconstruction.varying_vector (AtlasReconstruction.cutoff P.atlas)
    (AtlasReconstruction.cutoff_norm_le P.atlas) (AtlasReconstruction.cutoff_strong P.atlas)
    (P.graph_components hg x).2

theorem norm_error_tendsto (hg : P.GraphCompatible) (x : T.domain) :
    Tendsto (fun s : Finset I => ‖reconstructed P s x-T x‖) atTop (𝓝 0) := by
  simpa using ((tendsto P hg x).sub_const (T x)).norm

/-- The same limit along any cofinal family of finite subsets. -/
theorem cofinal_reconstruction {α : Type*} {l : Filter α}
    (s : α → Finset I) (hs : Tendsto s l atTop)
    (hg : P.GraphCompatible) (x : T.domain) :
    Tendsto (fun a => reconstructed P (s a) x) l (𝓝 (T x)) :=
  (tendsto P hg x).comp hs

end GraphReconstruction
end KomorebiPhysics
