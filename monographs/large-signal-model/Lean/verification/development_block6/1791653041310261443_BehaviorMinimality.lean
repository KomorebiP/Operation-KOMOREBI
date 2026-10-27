import KomorebiLSM.BehaviorSpace
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-! Canonical reachability, observability and the uniqueness of minimal models.
Similarity transports operators, initial state and mass together. -/
set_option autoImplicit false
namespace Komorebi.LSM.Behavior
open FiniteInstruments
variable {S : Type*} (f : List S → ℝ)

theorem history_span : Submodule.span ℝ (Set.range (history f)) = ⊤ := by
  exact (Submodule.span_range_subtype_eq_top_iff (space f)
    (fun h => Submodule.subset_span ⟨h,rfl⟩)).mpr rfl

theorem canonical_reachable : (canonical f).IsReachable := by
  have hs : (canonical f).state = history f := by
    funext h
    simpa [Realization.state,canonical] using word_history f h []
  change Submodule.span ℝ (Set.range (canonical f).state) = ⊤
  rw [hs,history_span]

theorem canonical_observable : (canonical f).IsObservable := by
  intro x y h
  apply Subtype.ext
  funext t
  have ht := congrFun h t
  simpa only [Realization.observe_apply,canonical,test_evaluation] using ht

namespace Realization
variable {f}
variable {E F : Type*} [AddCommGroup E] [Module ℝ E] [AddCommGroup F] [Module ℝ F]

/-- Any finite model implies finite-dimensional behavior; this is not inferred
from a finite sampled table without a rank hypothesis. -/
theorem behavior_finite [FiniteDimensional ℝ E] (r : Realization f E) :
    FiniteDimensional ℝ (space f) :=
  Module.Finite.of_surjective r.toBehavior r.toBehavior_surjective

noncomputable def similarity (r : Realization f E) (q : Realization f F)
    (hr : r.IsReachable) (ho : r.IsObservable)
    (hq : q.IsReachable) (hp : q.IsObservable) : E ≃ₗ[ℝ] F :=
  (r.equiv hr ho).trans (q.equiv hq hp).symm

theorem similarity_initial (r : Realization f E) (q : Realization f F)
    (hr : r.IsReachable) (ho : r.IsObservable)
    (hq : q.IsReachable) (hp : q.IsObservable) :
    similarity r q hr ho hq hp r.initial = q.initial := by
  apply (q.equiv hq hp).injective
  change q.equiv hq hp ((q.equiv hq hp).symm (r.equiv hr ho r.initial)) = _
  rw [LinearEquiv.apply_symm_apply,r.equiv_initial hr ho,q.equiv_initial hq hp]

theorem similarity_operator (r : Realization f E) (q : Realization f F)
    (hr : r.IsReachable) (ho : r.IsObservable)
    (hq : q.IsReachable) (hp : q.IsObservable) (s : S) (x : E) :
    similarity r q hr ho hq hp (r.operator s x) =
      q.operator s (similarity r q hr ho hq hp x) := by
  apply (q.equiv hq hp).injective
  change q.equiv hq hp ((q.equiv hq hp).symm (r.equiv hr ho (r.operator s x))) = _
  rw [LinearEquiv.apply_symm_apply,r.equiv_operator hr ho,q.equiv_operator hq hp]
  congr 1
  exact (q.equiv hq hp).apply_symm_apply _ |>.symm

theorem similarity_mass (r : Realization f E) (q : Realization f F)
    (hr : r.IsReachable) (ho : r.IsObservable)
    (hq : q.IsReachable) (hp : q.IsObservable) (x : E) :
    q.readout (similarity r q hr ho hq hp x) = r.readout x := by
  rw [← q.equiv_mass hq hp,← r.equiv_mass hr ho]
  change mass f (q.equiv hq hp ((q.equiv hq hp).symm (r.equiv hr ho x))) = _
  rw [LinearEquiv.apply_symm_apply]

/-- Reachability makes an initial-state/operator intertwiner unique. -/
theorem intertwiner_unique (r : Realization f E) (q : Realization f F)
    (hr : r.IsReachable) (T U : E →ₗ[ℝ] F)
    (hT0 : T r.initial = q.initial) (hU0 : U r.initial = q.initial)
    (hT : ∀ s, T.comp (r.operator s) = (q.operator s).comp T)
    (hU : ∀ s, U.comp (r.operator s) = (q.operator s).comp U) : T = U := by
  apply LinearMap.ext
  intro x
  have hx : x ∈ r.reachable := by rw [hr]; trivial
  induction hx using Submodule.span_induction with
  | mem x hx =>
    obtain ⟨w,rfl⟩ := hx
    have htw := word_intertwining r.operator q.operator T (fun s => (hT s).symm) w
    have huw := word_intertwining r.operator q.operator U (fun s => (hU s).symm) w
    have ht := congrArg (fun L : E →ₗ[ℝ] F => L r.initial) htw
    have hu := congrArg (fun L : E →ₗ[ℝ] F => L r.initial) huw
    change T (wordAction r.operator w r.initial) = U (wordAction r.operator w r.initial)
    simp only [LinearMap.comp_apply,hT0] at ht
    simp only [LinearMap.comp_apply,hU0] at hu
    exact ht.symm.trans hu
  | zero => simp
  | add x y hx hy ihx ihy => simp only [map_add,ihx,ihy]
  | smul c x hx ih => simp only [map_smul,ih]

/-- The dimension of any reachable observable finite realization is the full
behavior dimension, not just the rank of a selected sample. -/
theorem minimal_dimension [FiniteDimensional ℝ E] (r : Realization f E)
    (hr : r.IsReachable) (ho : r.IsObservable) :
    Module.finrank ℝ E = Module.finrank ℝ (space f) :=
  (r.equiv hr ho).finrank_eq

/-- P27 uniqueness includes the two boundary vectors, not only matrix conjugacy. -/
theorem minimal_realizations_similar (r : Realization f E) (q : Realization f F)
    (hr : r.IsReachable) (ho : r.IsObservable)
    (hq : q.IsReachable) (hp : q.IsObservable) :
    ∃ T : E ≃ₗ[ℝ] F,
      T r.initial = q.initial ∧
      (∀ s x, T (r.operator s x) = q.operator s (T x)) ∧
      (∀ x, q.readout (T x) = r.readout x) :=
  ⟨similarity r q hr ho hq hp, similarity_initial r q hr ho hq hp,
    similarity_operator r q hr ho hq hp, similarity_mass r q hr ho hq hp⟩

end Realization
end Komorebi.LSM.Behavior
