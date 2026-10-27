import KomorebiVerification.TopologicalCompletion
import Mathlib.Topology.Algebra.Module.Basic
import Mathlib.LinearAlgebra.Isomorphisms

/-!
# Paper I: topological transport at the stated generality

The dense-realization result below uses topological modules, without a norm
or a metrizability assumption. Fibre aggregation is represented by actual
finite sums of the source projectors. The quotient equivalence uses an
explicit quotient-map hypothesis.
-/

noncomputable section
open scoped BigOperators
open Set Function Topology

namespace PaperIRelease.TopologyTransport

section General

variable {𝕜 X Y : Type*} [Ring 𝕜] [TopologicalSpace 𝕜]
variable [AddCommGroup X] [Module 𝕜 X] [TopologicalSpace X]
variable [AddCommGroup Y] [Module 𝕜 Y] [TopologicalSpace Y]
variable [ContinuousAdd X] [ContinuousSMul 𝕜 X]
variable [ContinuousAdd Y] [ContinuousSMul 𝕜 Y]

/-- The algebraic operator hull in a general topological module. -/
def operatorHull (A : Set (X →L[𝕜] X)) (S : Set X) : Submodule 𝕜 X :=
  Submodule.span 𝕜 {x | ∃ T ∈ A, ∃ s ∈ S, T s = x}

omit [TopologicalSpace 𝕜] [ContinuousAdd X] [ContinuousSMul 𝕜 X]
  [ContinuousAdd Y] [ContinuousSMul 𝕜 Y] in
/-- Intertwining transports the actual operator hull. -/
theorem map_operatorHull_le
    (f : X →L[𝕜] Y) (φ : (X →L[𝕜] X) → (Y →L[𝕜] Y))
    (A : Set (X →L[𝕜] X)) (B : Set (Y →L[𝕜] Y))
    (S : Set X) (hφ : ∀ T ∈ A, φ T ∈ B)
    (hintertwine : ∀ T ∈ A, f.comp T = (φ T).comp f) :
    (operatorHull A S).map f.toLinearMap ≤ operatorHull B (f '' S) := by
  rw [Submodule.map_le_iff_le_comap]
  apply Submodule.span_le.2
  rintro x ⟨T, hTA, s, hs, rfl⟩
  change f (T s) ∈ operatorHull B (f '' S)
  have hpoint : f (T s) = φ T (f s) := by
    simpa using congrArg (fun L : X →L[𝕜] Y ↦ L s) (hintertwine T hTA)
  rw [hpoint]
  exact Submodule.subset_span ⟨φ T, hφ T hTA, f s, ⟨s, hs, rfl⟩, rfl⟩

/-- Dense realization for arbitrary topological modules. In particular,
this covers Hausdorff topological vector spaces as printed in Paper I. -/
theorem dense_operatorHull_image
    (f : X →L[𝕜] Y) (hf : Surjective f)
    (φ : (X →L[𝕜] X) → (Y →L[𝕜] Y))
    (A : Set (X →L[𝕜] X)) (B : Set (Y →L[𝕜] Y))
    (S : Set X) (hφ : ∀ T ∈ A, φ T ∈ B)
    (hintertwine : ∀ T ∈ A, f.comp T = (φ T).comp f)
    (hgenerate : (operatorHull A S).topologicalClosure = ⊤) :
    (operatorHull B (f '' S)).topologicalClosure = ⊤ := by
  have himage : ((operatorHull A S).map f.toLinearMap).topologicalClosure = ⊤ :=
    hf.denseRange.topologicalClosure_map_submodule hgenerate
  apply top_unique
  rw [← himage]
  exact Submodule.topologicalClosure_mono
    (map_operatorHull_le f φ A B S hφ hintertwine)

omit [TopologicalSpace 𝕜] [ContinuousAdd X] [ContinuousSMul 𝕜 X]
  [ContinuousAdd Y] [ContinuousSMul 𝕜 Y] in
/-- A continuous surjective intertwiner maps the source range onto the
target range, with no norm assumption. -/
theorem map_packetRange_eq
    (f : X →L[𝕜] Y) (hf : Surjective f)
    (P : X →L[𝕜] X) (Q : Y →L[𝕜] Y)
    (hintertwine : f.comp P = Q.comp f) :
    P.range.map f.toLinearMap = Q.range := by
  have hi : ∀ a, f (P a) = Q (f a) := by
    intro a
    simpa using congrArg (fun L : X →L[𝕜] Y ↦ L a) hintertwine
  ext y
  constructor
  · rintro ⟨x, ⟨a, rfl⟩, rfl⟩
    exact ⟨f a, (hi a).symm⟩
  · rintro ⟨b, rfl⟩
    rcases hf b with ⟨a, rfl⟩
    exact ⟨P a, ⟨a, rfl⟩, hi a⟩

omit [TopologicalSpace 𝕜] [ContinuousSMul 𝕜 X] [ContinuousAdd Y] [ContinuousSMul 𝕜 Y] in
/-- The arbitrary fibre-aggregation clause of dense realization. Empty
fibres are included because their projector is the empty sum. -/
theorem map_aggregated_packetRange_eq
    {ι κ : Type*} [Fintype ι] [DecidableEq κ]
    (f : X →L[𝕜] Y) (hf : Surjective f) (σ : ι → κ)
    (P : ι → X →L[𝕜] X) (Q : κ → Y →L[𝕜] Y)
    (hintertwine : ∀ j, f.comp (∑ i with σ i = j, P i) = (Q j).comp f)
    (j : κ) :
    (∑ i with σ i = j, P i).range.map f.toLinearMap = (Q j).range :=
  map_packetRange_eq f hf _ _ (hintertwine j)

end General

section Quotient

variable {𝕜 X Y : Type*} [Ring 𝕜]
variable [AddCommGroup X] [Module 𝕜 X] [TopologicalSpace X]
variable [AddCommGroup Y] [Module 𝕜 Y] [TopologicalSpace Y]

/-- The algebraic first-isomorphism equivalence is a topological linear
equivalence precisely under the declared quotient-map hypothesis. -/
def quotientEquiv (f : X →L[𝕜] Y) (hf : IsQuotientMap f) :
    (X ⧸ f.ker) ≃L[𝕜] Y := by
  let e := f.toLinearMap.quotKerEquivOfSurjective hf.surjective
  have hcomp : (e : X ⧸ f.ker → Y) ∘ f.ker.mkQ = f := by
    funext x
    exact LinearMap.quotKerEquivOfSurjective_apply_mk _ _ x
  have he : IsQuotientMap e := by
    apply f.ker.isQuotientMap_mkQ.of_comp_isQuotientMap
    simpa only [hcomp] using hf
  refine { e with continuous_toFun := he.continuous, continuous_invFun := ?_ }
  apply he.continuous_iff.2
  convert (continuous_id : Continuous (id : X ⧸ f.ker → X ⧸ f.ker)) using 1
  funext x
  exact e.symm_apply_apply x

@[simp]
theorem quotientEquiv_apply_mk (f : X →L[𝕜] Y) (hf : IsQuotientMap f) (x : X) :
    quotientEquiv f hf (f.ker.mkQ x) = f x :=
  LinearMap.quotKerEquivOfSurjective_apply_mk f.toLinearMap hf.surjective x

end Quotient

end PaperIRelease.TopologyTransport
