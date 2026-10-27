import KomorebiLSM.InvariantCompletion
import Mathlib.LinearAlgebra.Dual.Lemmas

/-! P8: apply the finite invariant-space construction to observable rows.
The observation map and reduced transitions are constructed, then connected
to arbitrary finite bases and to the row spaces of competing summaries. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM
open Module
universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w}

/-- Evaluation of all observables in a declared row space. -/
def observableState (W : Submodule K (Dual K X)) : X →ₗ[K] Dual K W :=
  W.subtype.dualMap.comp (Dual.eval K X)

@[simp] theorem observableState_apply (W : Submodule K (Dual K X)) (x : X) (w : W) :
    observableState W x w = (w : Dual K X) x := rfl

/-- The row pullback restricted to an invariant observable space. -/
def restrictedPullback (L : I → X →ₗ[K] X) (W : Submodule K (Dual K X))
    (hW : CommonInvariant (fun i => (L i).dualMap) W) (i : I) : W →ₗ[K] W :=
  (L i).dualMap.restrict (fun w hw => hW i (Submodule.mem_map.mpr ⟨w, hw, rfl⟩))

/-- The dual of the row pullback evolves the evaluated state. -/
def observableTransition (L : I → X →ₗ[K] X) (W : Submodule K (Dual K X))
    (hW : CommonInvariant (fun i => (L i).dualMap) W) (i : I) :
    Dual K W →ₗ[K] Dual K W := (restrictedPullback L W hW i).dualMap

/-- Exact current-state closure follows from row invariance. -/
theorem observableState_closed (L : I → X →ₗ[K] X) (W : Submodule K (Dual K X))
    (hW : CommonInvariant (fun i => (L i).dualMap) W) (i : I) :
    (observableTransition L W hW i).comp (observableState W) =
      (observableState W).comp (L i) := by
  ext x w
  rfl

/-- Restricting the completed state recovers the initial observable state. -/
theorem observableState_retains (W₀ W : Submodule K (Dual K X)) (h : W₀ ≤ W) :
    (Submodule.inclusion h).dualMap.comp (observableState W) = observableState W₀ := by
  ext x w
  rfl

/-- In finite dimension this state space is exactly realizable, not padded. -/
theorem observableState_surjective [FiniteDimensional K X]
    (W : Submodule K (Dual K X)) : Function.Surjective (observableState W) := by
  intro z
  obtain ⟨f, hf⟩ := (Subspace.dualRestrict_surjective (W := W)) z
  refine ⟨(Module.evalEquiv K X).symm f, ?_⟩
  ext w
  change (w : Dual K X) ((Module.evalEquiv K X).symm f) = z w
  rw [Module.apply_evalEquiv_symm_apply]
  exact congrArg (fun g : Dual K W => g w) hf

/-- The state dimension equals the completed row dimension. -/
theorem observableState_dimension (W : Submodule K (Dual K X)) :
    finrank K (Dual K W) = finrank K W := by
  simpa using (Subspace.dual_finrank_eq (K := K) (V := W))

/-- Basis-independent completion of the initial observation rows. -/
noncomputable def predictiveCompletion (L : I → X →ₗ[K] X)
    (W₀ : Submodule K (Dual K X)) : Submodule K (Dual K X) :=
  invariantCompletion (fun i => (L i).dualMap) W₀

theorem predictiveCompletion_isLeast [FiniteDimensional K X]
    (L : I → X →ₗ[K] X) (W₀ : Submodule K (Dual K X)) :
    IsLeast {W : Submodule K (Dual K X) |
      W₀ ≤ W ∧ CommonInvariant (fun i => (L i).dualMap) W}
      (predictiveCompletion L W₀) := invariantCompletion_isLeast _ _

/-- The stopping bound is the original signal dimension deficit. -/
theorem predictiveCompletion_stopping_bound [FiniteDimensional K X]
    (L : I → X →ₗ[K] X) (W₀ : Submodule K (Dual K X)) :
    ∃ n ≤ finrank K X - finrank K W₀,
      invariantSequence (fun i => (L i).dualMap) W₀ (n+1) =
        invariantSequence (fun i => (L i).dualMap) W₀ n := by
  simpa only [Subspace.dual_finrank_eq] using
    invariantSequence_exists_stable (fun i => (L i).dualMap) W₀

section Coordinates
variable {J : Type*} [Fintype J]
variable {W : Submodule K (Dual K X)}

/-- The rows of an arbitrary basis are the matrix R in the manuscript. -/
noncomputable def basisObservation (b : Basis J K W) : X →ₗ[K] (J → K) :=
  LinearMap.pi (fun j => (b j : Dual K X))

/-- Reading out any row using its finite basis coefficients. -/
noncomputable def basisRowReadout (b : Basis J K W) (w : W) : (J → K) →ₗ[K] K :=
  ∑ j, (b.repr w j) • (LinearMap.proj j : (J → K) →ₗ[K] K)

theorem basisRowReadout_correct (b : Basis J K W) (w : W) (x : X) :
    basisRowReadout b w (basisObservation b x) = (w : Dual K X) x := by
  have h := congrArg (fun z : W => (z : Dual K X) x) (b.sum_repr w)
  simp only [Submodule.coe_sum, Submodule.coe_smul, LinearMap.sum_apply,
    LinearMap.smul_apply, smul_eq_mul] at h
  simpa only [basisRowReadout, basisObservation, LinearMap.sum_apply,
    LinearMap.smul_apply, LinearMap.proj_apply, LinearMap.pi_apply, smul_eq_mul] using h

/-- A finite matrix acting on the basis-evaluation state. -/
noncomputable def basisTransition (L : I → X →ₗ[K] X)
    (hW : CommonInvariant (fun i => (L i).dualMap) W)
    (b : Basis J K W) (i : I) : (J → K) →ₗ[K] (J → K) :=
  LinearMap.pi (fun j => basisRowReadout b (restrictedPullback L W hW i (b j)))

/-- R L_i = B_i R, for any chosen basis of the invariant row space. -/
theorem basisTransition_correct (L : I → X →ₗ[K] X)
    (hW : CommonInvariant (fun i => (L i).dualMap) W)
    (b : Basis J K W) (i : I) :
    (basisTransition L hW b i).comp (basisObservation b) =
      (basisObservation b).comp (L i) := by
  ext x j
  exact basisRowReadout_correct b (restrictedPullback L W hW i (b j)) x

/-- H R recovers every specified initial row, not only a fitted sample. -/
theorem basisReadout_correct {O : Type*} (b : Basis J K W) (rows : O → W) :
    (LinearMap.pi (fun o => basisRowReadout b (rows o))).comp (basisObservation b) =
      LinearMap.pi (fun o => (rows o : Dual K X)) := by
  ext x o
  exact basisRowReadout_correct b (rows o) x

omit [Fintype J] in
/-- The matrix rows are independent because they are an actual subspace basis. -/
theorem basisObservation_independent (b : Basis J K W) :
    LinearIndependent K (fun j => (LinearMap.proj j : (J → K) →ₗ[K] K).comp
      (basisObservation b)) := by
  change LinearIndependent K (fun j => (b j : Dual K X))
  intro a c h
  apply b.linearIndependent
  apply Subtype.ext
  simpa only [Finsupp.linearCombination_apply, Finsupp.sum,
    Submodule.coe_sum, Submodule.coe_smul] using h

end Coordinates

/-- Every summary closed under the dynamics has an invariant row space. -/
theorem closed_summary_row_invariant
    {Z : Type*} [AddCommGroup Z] [Module K Z]
    (L : I → X →ₗ[K] X) (R : X →ₗ[K] Z) (B : I → Z →ₗ[K] Z)
    (h : ∀ i, R.comp (L i) = (B i).comp R) :
    CommonInvariant (fun i => (L i).dualMap) (LinearMap.range R.dualMap) := by
  intro i w hw
  obtain ⟨v, hv, rfl⟩ := Submodule.mem_map.mp hw
  obtain ⟨f, rfl⟩ := hv
  refine ⟨(B i).dualMap f, ?_⟩
  ext x
  exact congrArg f (congrArg (fun g : X →ₗ[K] Z => g x) (h i)).symm

/-- Retaining an output by a linear readout contains its entire row space. -/
theorem retained_summary_row_le
    {Y Z : Type*} [AddCommGroup Y] [Module K Y] [AddCommGroup Z] [Module K Z]
    (C₀ : X →ₗ[K] Y) (R : X →ₗ[K] Z) (H : Z →ₗ[K] Y)
    (h : C₀ = H.comp R) :
    LinearMap.range C₀.dualMap ≤ LinearMap.range R.dualMap := by
  rintro w ⟨f, rfl⟩
  refine ⟨H.dualMap f, ?_⟩
  ext x
  exact congrArg f (congrArg (fun g : X →ₗ[K] Y => g x) h).symm

/-- Minimality applies to any linear summary with exact readout and closure. -/
theorem predictiveCompletion_le_competing_summary [FiniteDimensional K X]
    {Y Z : Type*} [AddCommGroup Y] [Module K Y] [AddCommGroup Z] [Module K Z]
    (L : I → X →ₗ[K] X) (C₀ : X →ₗ[K] Y)
    (R : X →ₗ[K] Z) (H : Z →ₗ[K] Y) (B : I → Z →ₗ[K] Z)
    (retains : C₀ = H.comp R) (closes : ∀ i, R.comp (L i) = (B i).comp R) :
    predictiveCompletion L (LinearMap.range C₀.dualMap) ≤ LinearMap.range R.dualMap :=
  invariantCompletion_minimal _ _ _ (retained_summary_row_le C₀ R H retains)
    (closed_summary_row_invariant L R B closes)

/-- P8 coordinate realization, with full-row-rank R, exact readout H,
and action transitions B constructed from the completed row space. -/
theorem predictiveCompletion_coordinate_realization [FiniteDimensional K X]
    {O : Type*} (L : I → X →ₗ[K] X) (rows : O → Dual K X) :
    let W₀ := Submodule.span K (Set.range rows)
    let W := predictiveCompletion L W₀
    ∃ (R : X →ₗ[K] (Fin (finrank K W) → K))
      (H : (Fin (finrank K W) → K) →ₗ[K] (O → K))
      (B : I → (Fin (finrank K W) → K) →ₗ[K] (Fin (finrank K W) → K)),
      LinearIndependent K (fun j => (LinearMap.proj j).comp R) ∧
      H.comp R = LinearMap.pi rows ∧ ∀ i, (B i).comp R = R.comp (L i) := by
  classical
  let W₀ := Submodule.span K (Set.range rows)
  let W := predictiveCompletion L W₀
  let : Module.Free K W := Module.Free.of_divisionRing K W
  let b := Module.finBasis K W
  have hi : W₀ ≤ W := (predictiveCompletion_isLeast L W₀).1.1
  have hc : CommonInvariant (fun i => (L i).dualMap) W :=
    (predictiveCompletion_isLeast L W₀).1.2
  let rw₀ : O → W := fun o => ⟨rows o, hi (Submodule.subset_span ⟨o, rfl⟩)⟩
  refine ⟨basisObservation b, LinearMap.pi (fun o => basisRowReadout b (rw₀ o)),
    basisTransition L hc b, basisObservation_independent b, ?_, ?_⟩
  · exact basisReadout_correct b rw₀
  · exact basisTransition_correct L hc b

end Komorebi.LSM
