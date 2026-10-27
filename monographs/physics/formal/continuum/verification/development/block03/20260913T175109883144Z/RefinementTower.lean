module

public import KomorebiPhysics.Refinement
public import Mathlib.LinearAlgebra.Matrix.ToLin
import all TensorRefinement

/-!
Chapter 4.3 (4.16)--(4.22). Associative finite coarsening.
Address maps enforce exactly one target cell per source sector. Arbitrary
zero-one arrays alone do not imply the partition property. Weighted matrix
identities are proved separately and never used to invent orthogonal atlases.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators Matrix
namespace RefinementTower

section Push
variable {I J K V : Type*} [Fintype I] [Fintype J] [DecidableEq J]
  [DecidableEq K] [AddCommMonoid V]

/-- Push a finite family through an address map. Empty cells have value zero. -/
def push (f : I → J) (x : I → V) (a : J) : V :=
  ∑ i, if f i = a then x i else 0

/-- Fiber formula for a finite additive push. -/
omit [Fintype J] in
theorem push_eq_fiber (f : I → J) (x : I → V) (a : J) :
    push f x a = ∑ i ∈ Atlas.fiber f a, x i := by
  simp only [push, Atlas.fiber, Finset.sum_filter]

/-- The exact associativity law works in every additive commutative monoid. -/
theorem push_comp (f : I → J) (g : J → K) (x : I → V) :
    push g (push f x) = push (g ∘ f) x := by
  funext c
  unfold push
  have distribute (b : J) :
      (if g b = c then ∑ i, if f i = b then x i else 0 else 0) =
        ∑ i, if g b = c then (if f i = b then x i else 0) else 0 := by
    by_cases h : g b = c <;> simp [h]
  simp_rw [distribute]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  rw [Finset.sum_eq_single (f i)]
  · simp
  · intro b _ hb
    simp [Ne.symm hb]
  · simp

/-- Reconstruction is not changed by empty coarse cells. -/
theorem sum_push (f : I → J) (x : I → V) : (∑ a, push f x a) = ∑ i, x i := by
  unfold push
  rw [Finset.sum_comm]
  simp

end Push

section Identity
variable {I V : Type*} [Fintype I] [DecidableEq I] [AddCommMonoid V]

/-- Identity addresses do not change the family. -/
theorem push_id (x : I → V) : push id x = x := by
  funext i
  simp [push]

/-- Iterate any finite sequence of same-label-space coarsenings. -/
def pushList : List (I → I) → (I → V) → (I → V)
  | [], x => x
  | f :: fs, x => pushList fs (push f x)

/-- Compose addresses in the same order as pushList. -/
def composeList : List (I → I) → (I → I)
  | [] => id
  | f :: fs => composeList fs ∘ f

/-- All finite depths, including the zero-step tower. -/
theorem pushList_eq (fs : List (I → I)) (x : I → V) :
    pushList fs x = push (composeList fs) x := by
  induction fs generalizing x with
  | nil => exact (push_id x).symm
  | cons f fs ih =>
      simp only [pushList, composeList, ih, push_comp]

end Identity

section Incidence
variable {I J K : Type*} [Fintype I] [Fintype J] [Fintype K]
  [DecidableEq I] [DecidableEq J] [DecidableEq K]

/-- One-hot column incidence matrix of an actual partition address. -/
def incidence (f : I → J) : Matrix J I ℝ := fun a i => if f i = a then 1 else 0

/-- Each fine sector occurs in exactly one coarse cell. -/
omit [Fintype I] [DecidableEq I] in
theorem incidence_column_sum (f : I → J) (i : I) : (∑ a, incidence f a i) = 1 := by
  simp [incidence]

/-- Composition of one-hot incidence matrices remains one-hot. -/
omit [Fintype I] [Fintype K] [DecidableEq I] in
theorem incidence_comp (f : I → J) (g : J → K) :
    incidence (g ∘ f) = incidence g * incidence f := by
  ext c i
  symm
  rw [Matrix.mul_apply, Finset.sum_eq_single (f i)]
  · simp [incidence]
  · intro b _ hb
    simp [incidence, Ne.symm hb]
  · simp

/-- The additive push is the literal matrix-vector multiplication in (4.20). -/
omit [Fintype J] [DecidableEq I] in
theorem push_eq_mulVec (f : I → J) (x : I → ℝ) :
    push f x = incidence f *ᵥ x := by
  funext a
  simp [push, incidence, Matrix.mulVec, dotProduct, ite_mul]

/-- Ordered two-sided current aggregation. -/
def aggregateCurrent (R : Matrix J I ℝ) (F : Matrix I I ℝ) : Matrix J J ℝ :=
  R * F * R.transpose

/-- The matrix version of (4.21), valid even for arbitrary real weights. -/
omit [Fintype K] [DecidableEq I] [DecidableEq J] [DecidableEq K] in
theorem aggregateCurrent_comp (R : Matrix J I ℝ) (S : Matrix K J ℝ)
    (F : Matrix I I ℝ) :
    aggregateCurrent S (aggregateCurrent R F) = aggregateCurrent (S * R) F := by
  simp only [aggregateCurrent, Matrix.transpose_mul, Matrix.mul_assoc]

/-- Literal incidence form of the two-step current tower. -/
omit [Fintype K] [DecidableEq I] in
theorem aggregateCurrent_incidence_comp (f : I → J) (g : J → K)
    (F : Matrix I I ℝ) :
    aggregateCurrent (incidence g) (aggregateCurrent (incidence f) F) =
      aggregateCurrent (incidence (g ∘ f)) F := by
  rw [aggregateCurrent_comp, incidence_comp]

/-- An incidence current entry equals the double fine-sector fiber sum. -/
theorem aggregateCurrent_entry (f : I → J) (F : Matrix I I ℝ) (a b : J) :
    aggregateCurrent (incidence f) F a b =
      ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, F i j := by
  change (∑ j, (∑ i, (if f i = a then 1 else 0) * F i j) *
      (if f j = b then 1 else 0)) = _
  simp only [ite_mul, one_mul, zero_mul, mul_ite, mul_one, mul_zero]
  have distribute (j : I) :
      (if f j = b then ∑ i, if f i = a then F i j else 0 else 0) =
        ∑ i, if f j = b then (if f i = a then F i j else 0) else 0 := by
    by_cases h : f j = b <;> simp [h]
  simp_rw [distribute]
  rw [Finset.sum_comm]
  simp only [Atlas.fiber, Finset.sum_filter]
  apply Finset.sum_congr rfl
  intro i _
  by_cases hi : f i = a <;> simp [hi]

/-- Weighted aggregation preserves antisymmetry independently of atlas axioms. -/
omit [Fintype J] [DecidableEq I] [DecidableEq J] in
theorem aggregateCurrent_antisymm (R : Matrix J I ℝ) (F : Matrix I I ℝ)
    (hF : F.transpose = -F) :
    (aggregateCurrent R F).transpose = -aggregateCurrent R F := by
  simp only [aggregateCurrent, Matrix.transpose_mul, Matrix.transpose_transpose,
    hF, Matrix.mul_neg, Matrix.neg_mul, Matrix.mul_assoc]

end Incidence
end RefinementTower

namespace Atlas
variable {H I J K : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
  [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]
  [Fintype K] [DecidableEq K]
variable (P : Atlas H I)

/-- At the operator level, sequential coarsening equals composed addressing. -/
theorem coarsen_coarsen_proj (f : I → J) (g : J → K) (c : K) :
    ((P.coarsen f).coarsen g).proj c = (P.coarsen (g ∘ f)).proj c := by
  exact congrFun (RefinementTower.push_comp f g P.proj) c

/-- The actual state packets agree, not merely bookkeeping arrays. -/
theorem coarsen_coarsen_packet (f : I → J) (g : J → K) (ψ : H) (c : K) :
    ((P.coarsen f).coarsen g).packet ψ c = (P.coarsen (g ∘ f)).packet ψ c := by
  simp only [packet, P.coarsen_coarsen_proj]

/-- The actual operator corners agree, with no commutative reorderings. -/
theorem coarsen_coarsen_corner (f : I → J) (g : J → K) (X : H →L[ℂ] H) (c d : K) :
    ((P.coarsen f).coarsen g).proj c * X * ((P.coarsen f).coarsen g).proj d =
      (P.coarsen (g ∘ f)).proj c * X * (P.coarsen (g ∘ f)).proj d := by
  rw [P.coarsen_coarsen_proj, P.coarsen_coarsen_proj]

/-- Actual squared norms are independent of the intermediate resolution. -/
theorem coarsen_coarsen_energy (f : I → J) (g : J → K) (ψ : H) (c : K) :
    ((P.coarsen f).coarsen g).energy ψ c = (P.coarsen (g ∘ f)).energy ψ c := by
  simp only [energy, P.coarsen_coarsen_packet]

/-- Actual inner-product currents are independent of intermediate resolution. -/
theorem coarsen_coarsen_current (f : I → J) (g : J → K)
    (A : H →L[ℂ] H) (ψ : H) (c d : K) :
    ((P.coarsen f).coarsen g).current A ψ c d =
      (P.coarsen (g ∘ f)).current A ψ c d := by
  simp only [current, P.coarsen_coarsen_packet]

/-- The physical coarse energy equals the incidence matrix applied to fine energies. -/
theorem coarsen_energy_incidence (f : I → J) (ψ : H) :
    (P.coarsen f).energy ψ = RefinementTower.incidence f *ᵥ P.energy ψ := by
  rw [← RefinementTower.push_eq_mulVec]
  funext a
  rw [P.coarsen_energy, RefinementTower.push_eq_fiber]

/-- The physical coarse current equals R J R-transpose. -/
theorem coarsen_current_incidence (f : I → J) (A : H →L[ℂ] H) (ψ : H) :
    Matrix.of ((P.coarsen f).current A ψ) =
      RefinementTower.aggregateCurrent (RefinementTower.incidence f) (Matrix.of (P.current A ψ)) := by
  ext a b
  change (P.coarsen f).current A ψ a b = _
  rw [P.coarsen_current, RefinementTower.aggregateCurrent_entry]
  rfl

/-- An actual derivative at the top of the tower equals its direct fine-resolution flux. -/
theorem hasDerivAt_tower_energy (f : I → J) (g : J → K) (A : H →L[ℂ] H)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t) (c : K) :
    HasDerivAt (fun s => ((P.coarsen f).coarsen g).energy (ψ s) c)
      (∑ d, (P.coarsen (g ∘ f)).current A (ψ t) c d) t := by
  simpa only [P.coarsen_coarsen_energy] using
    (P.coarsen (g ∘ f)).hasDerivAt_packet_energy A hψ c

end Atlas
end KomorebiPhysics
