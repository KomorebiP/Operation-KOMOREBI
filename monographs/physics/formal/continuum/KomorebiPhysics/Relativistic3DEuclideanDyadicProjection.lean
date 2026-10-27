module

public import KomorebiPhysics.Relativistic3DBinaryLebesgue
public import Mathlib.Analysis.InnerProductSpace.Projection.Basic

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped ENNReal NNReal MeasureTheory InnerProductSpace Topology
open MeasureTheory

namespace KomorebiPhysics
namespace Relativistic3DEuclideanDyadicProjection

universe uE

variable {E : Type uE}
variable [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]

/-- Euclidean-cube continuum spinors. -/
abbrev CubeState := Lp E 2 Relativistic3DBinaryLebesgue.Cube.cubeVolume

/-- Symbolic octree continuum spinors. -/
abbrev OctreeState := Lp E 2 Relativistic3DWeightedDyadicReconstruction.Octree.octreeMeasure

/-- The checked measure-preserving pullback from Euclidean cube fields to octree fields. -/
noncomputable def cubePullback : CubeState (E := E) →ₗᵢ[ℂ] OctreeState (E := E) :=
  Relativistic3DBinaryLebesgue.Cube.pullbackCubeL2

/-- Hilbert adjoint of Euclidean-to-octree pullback. -/
noncomputable def cubeAdjoint : OctreeState (E := E) →L[ℂ] CubeState (E := E) :=
  ContinuousLinearMap.adjoint (cubePullback (E := E)).toContinuousLinearMap

/-- Pullback followed by its adjoint is the identity on Euclidean `L²`. -/
@[simp] theorem cubeAdjoint_pullback (f : CubeState (E := E)) :
    cubeAdjoint (E := E) (cubePullback (E := E) f) = f := by
  change ((ContinuousLinearMap.adjoint
    (cubePullback (E := E)).toContinuousLinearMap) ∘L
      (cubePullback (E := E)).toContinuousLinearMap) f = f
  rw [(cubePullback (E := E)).adjoint_comp_self]
  rfl

/-- The adjoint pushforward is contractive. -/
theorem norm_cubeAdjoint_le (g : OctreeState (E := E)) :
    ‖cubeAdjoint (E := E) g‖ ≤ ‖g‖ := by
  calc
    ‖cubeAdjoint (E := E) g‖ ≤ ‖cubeAdjoint (E := E)‖ * ‖g‖ :=
      (cubeAdjoint (E := E)).le_opNorm g
    _ = ‖(cubePullback (E := E)).toContinuousLinearMap‖ * ‖g‖ := by
      rw [show ‖cubeAdjoint (E := E)‖ =
          ‖(cubePullback (E := E)).toContinuousLinearMap‖ by
        exact LinearIsometryEquiv.norm_map ContinuousLinearMap.adjoint
          (cubePullback (E := E)).toContinuousLinearMap]
    _ ≤ 1 * ‖g‖ := by
      exact mul_le_mul_of_nonneg_right
        (cubePullback (E := E)).norm_toContinuousLinearMap_le (norm_nonneg g)
    _ = ‖g‖ := one_mul _

/-- The depth-`a` Euclidean approximation space obtained by adjoint transport of
finite-prefix octree states. -/
noncomputable def euclideanLevelRaw (a : ℕ) : Submodule ℂ (CubeState (E := E)) :=
  (Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule (E := E) a).map
    (cubeAdjoint (E := E)).toLinearMap

/-- Closed Euclidean depth-`a` reconstruction space. -/
noncomputable def euclideanLevel (a : ℕ) : Submodule ℂ (CubeState (E := E)) :=
  (euclideanLevelRaw (E := E) a).topologicalClosure

/-- The transported Euclidean reconstruction spaces are nested. -/
theorem euclideanLevel_mono {a b : ℕ} (hab : a ≤ b) :
    euclideanLevel (E := E) a ≤ euclideanLevel (E := E) b := by
  apply Submodule.topologicalClosure_mono
  exact Submodule.map_mono (Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule_mono (E := E) hab)

/-- An adjoint-transported finite-prefix state belongs to the corresponding closed level. -/
theorem cubeAdjoint_mem_euclideanLevel {a : ℕ} {g : OctreeState (E := E)}
    (hg : g ∈ Relativistic3DWeightedDyadicReconstruction.Octree.initialLevelSubmodule (E := E) a) :
    cubeAdjoint (E := E) g ∈ euclideanLevel (E := E) a := by
  apply Submodule.le_topologicalClosure
  exact ⟨g, hg, rfl⟩

/-- Every Euclidean `L²` field is approximable by one transported finite-prefix level. -/
theorem exists_euclideanLevel_approx (f : CubeState (E := E))
    {ε : ℝ} (hε : 0 < ε) :
    ∃ a : ℕ, ∃ g : CubeState (E := E),
      g ∈ euclideanLevel (E := E) a ∧ dist g f < ε := by
  obtain ⟨a, h, hh, hdist⟩ :=
    Relativistic3DWeightedDyadicReconstruction.Octree.exists_initialLevel_approx
      (E := E) (cubePullback (E := E) f) hε
  refine ⟨a, cubeAdjoint (E := E) h,
    cubeAdjoint_mem_euclideanLevel (E := E) hh, ?_⟩
  calc
    dist (cubeAdjoint (E := E) h) f =
        ‖cubeAdjoint (E := E) (h - cubePullback (E := E) f)‖ := by
      rw [dist_eq_norm, map_sub, cubeAdjoint_pullback]
    _ ≤ ‖h - cubePullback (E := E) f‖ :=
      norm_cubeAdjoint_le (E := E) _
    _ = dist h (cubePullback (E := E) f) := by rw [dist_eq_norm]
    _ < ε := hdist

/-- Algebraic union of the closed Euclidean finite-resolution spaces. -/
noncomputable def euclideanFiniteSubmodule : Submodule ℂ (CubeState (E := E)) :=
  ⨆ a : ℕ, euclideanLevel (E := E) a

/-- The transported finite-resolution Euclidean spaces are dense in cube `L²`. -/
theorem euclideanFiniteSubmodule_dense :
    Dense (euclideanFiniteSubmodule (E := E) : Set (CubeState (E := E))) := by
  rw [Metric.dense_iff]
  intro f ε hε
  obtain ⟨a, g, hg, hgf⟩ := exists_euclideanLevel_approx (E := E) f hε
  refine ⟨g, ?_⟩
  constructor
  · simpa [Metric.mem_ball, dist_comm] using hgf
  · exact (le_iSup (fun n : ℕ => euclideanLevel (E := E) n) a) hg

/-- Orthogonal projection onto the closed transported depth-`a` Euclidean space. -/
noncomputable def euclideanProjection (a : ℕ) :
    CubeState (E := E) →L[ℂ] CubeState (E := E) := by
  let _ : CompleteSpace (euclideanLevel (E := E) a) :=
    (Submodule.isClosed_topologicalClosure
      (euclideanLevelRaw (E := E) a)).completeSpace_coe
  exact (euclideanLevel (E := E) a).starProjection

/-- The level projection fixes every state already in that level. -/
@[simp] theorem euclideanProjection_eq_self {a : ℕ} {f : CubeState (E := E)}
    (hf : f ∈ euclideanLevel (E := E) a) :
    euclideanProjection (E := E) a f = f := by
  let _ : CompleteSpace (euclideanLevel (E := E) a) :=
    (Submodule.isClosed_topologicalClosure
      (euclideanLevelRaw (E := E) a)).completeSpace_coe
  exact Submodule.starProjection_eq_self_iff.mpr hf


/-- Every projected vector belongs to its finite-resolution level. -/
theorem euclideanProjection_mem (a : ℕ) (f : CubeState (E := E)) :
    euclideanProjection (E := E) a f ∈ euclideanLevel (E := E) a := by
  let _ : CompleteSpace (euclideanLevel (E := E) a) :=
    (Submodule.isClosed_topologicalClosure
      (euclideanLevelRaw (E := E) a)).completeSpace_coe
  change (((euclideanLevel (E := E) a).orthogonalProjectionOnto f :
    euclideanLevel (E := E) a) : CubeState (E := E)) ∈
      euclideanLevel (E := E) a
  exact ((euclideanLevel (E := E) a).orthogonalProjectionOnto f).property

/-- Each level projection is idempotent. -/
@[simp] theorem euclideanProjection_idem (a : ℕ) (f : CubeState (E := E)) :
    euclideanProjection (E := E) a (euclideanProjection (E := E) a f) =
      euclideanProjection (E := E) a f := by
  exact euclideanProjection_eq_self (E := E)
    (euclideanProjection_mem (E := E) a f)

/-- Each level projection is norm-contracting. -/
theorem norm_euclideanProjection_le (a : ℕ) (f : CubeState (E := E)) :
    ‖euclideanProjection (E := E) a f‖ ≤ ‖f‖ := by
  let _ : CompleteSpace (euclideanLevel (E := E) a) :=
    (Submodule.isClosed_topologicalClosure
      (euclideanLevelRaw (E := E) a)).completeSpace_coe
  exact (euclideanLevel (E := E) a).norm_starProjection_apply_le f

/-- Orthogonal projection gives the best approximation from its level. -/
theorem norm_sub_euclideanProjection_le {a : ℕ} (f g : CubeState (E := E))
    (hg : g ∈ euclideanLevel (E := E) a) :
    ‖f - euclideanProjection (E := E) a f‖ ≤ ‖f - g‖ := by
  let V : Submodule ℂ (CubeState (E := E)) := euclideanLevel (E := E) a
  have hVclosed : IsClosed (V : Set (CubeState (E := E))) := by
    dsimp [V, euclideanLevel]
    exact Submodule.isClosed_topologicalClosure _
  let _ : CompleteSpace V := hVclosed.completeSpace_coe
  have hproj : euclideanProjection (E := E) a f = V.starProjection f := by rfl
  have hbound : BddBelow (Set.range (fun x : V => ‖f - (x : CubeState (E := E))‖)) := by
    refine ⟨0, ?_⟩
    rintro y ⟨x, rfl⟩
    exact norm_nonneg _
  calc
    ‖f - euclideanProjection (E := E) a f‖ = ‖f - V.starProjection f‖ := by
      rw [hproj]
    _ = ⨅ x : V, ‖f - (x : CubeState (E := E))‖ :=
      Submodule.starProjection_minimal f
    _ ≤ ‖f - (⟨g, hg⟩ : V)‖ := ciInf_le hbound ⟨g, hg⟩
    _ = ‖f - g‖ := rfl

/-- A finer projection fixes every coarser projected state. -/
theorem euclideanProjection_of_le {a b : ℕ} (hab : a ≤ b)
    (f : CubeState (E := E)) :
    euclideanProjection (E := E) b (euclideanProjection (E := E) a f) =
      euclideanProjection (E := E) a f := by
  apply euclideanProjection_eq_self (E := E)
  exact euclideanLevel_mono (E := E) hab
    (euclideanProjection_mem (E := E) a f)

/-- The orthogonal finite-resolution projections converge strongly to the identity. -/
theorem euclideanProjection_tendsto (f : CubeState (E := E)) :
    Filter.Tendsto (fun a : ℕ => euclideanProjection (E := E) a f)
      Filter.atTop (𝓝 f) := by
  rw [Metric.tendsto_atTop]
  intro ε hε
  obtain ⟨N, g, hg, hgf⟩ := exists_euclideanLevel_approx (E := E) f hε
  refine ⟨N, ?_⟩
  intro n hn
  have hgn : g ∈ euclideanLevel (E := E) n :=
    euclideanLevel_mono (E := E) hn hg
  have hminimal :
      ‖f - euclideanProjection (E := E) n f‖ ≤ ‖f - g‖ :=
    norm_sub_euclideanProjection_le (E := E) f g hgn
  calc
    dist (euclideanProjection (E := E) n f) f =
        ‖f - euclideanProjection (E := E) n f‖ := by
      rw [dist_eq_norm, norm_sub_rev]
    _ ≤ ‖f - g‖ := hminimal
    _ = dist g f := by rw [dist_eq_norm, norm_sub_rev]
    _ < ε := hgf


end Relativistic3DEuclideanDyadicProjection
end KomorebiPhysics
