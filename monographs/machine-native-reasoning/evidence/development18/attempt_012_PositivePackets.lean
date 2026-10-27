import Mathlib.Geometry.Convex.Cone.Basic
import Mathlib.Basic.Real.Basic
import Mathlib.LinearAlgebra.Pi
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
# Positive packet mixtures

Core 2.5, general cone sector. Probability meaning belongs to a declared convex
cone and a strictly positive linear mass, not to the visible signs of coordinates.
Only positive-mass packets are normalized. Idempotence is not needed here.
-/
namespace Komorebi.MachineTheory.PositivePackets

noncomputable section

open scoped BigOperators

universe uV uI
variable {V : Type uV} {I : Type uI}
variable [AddCommGroup V] [Module ℝ V]

/-- A mass functional detects every nonzero member of the declared cone. -/
def StrictMass (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ) : Prop :=
  ∀ v ∈ C, v ≠ 0 → 0 < mass v

/-- Actual cone preservation of each packet operator. -/
def Preserves (C : ConvexCone ℝ V) (P : V →ₗ[ℝ] V) : Prop :=
  ∀ v ∈ C, P v ∈ C

/-- A normalized state is cone membership together with unit mass. -/
def IsState (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ) (v : V) : Prop :=
  v ∈ C ∧ mass v = 1

/-- The weight of a packet is its declared mass. -/
def weight (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V) (v : V) (i : I) : ℝ :=
  mass (P i v)

/-- The type of indices for which normalization is permitted. -/
abbrev PositiveIndex (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V) (v : V) :=
  {i : I // 0 < weight mass P v i}

/-- Normalization is defined only on a positive-weight index. -/
def normalized (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V) (v : V)
    (i : PositiveIndex mass P v) : V :=
  (weight mass P v i.val)⁻¹ • P i.val v

/-- Strict mass entails nonnegative mass, also at zero. -/
theorem mass_nonneg (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) {v : V} (hv : v ∈ C) : 0 ≤ mass v := by
  by_cases h : v = 0
  · simp [h]
  · exact le_of_lt (hm v hv h)

/-- A cone member has zero mass exactly when it is the zero vector. -/
theorem mass_zero_iff (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) {v : V} (hv : v ∈ C) : mass v = 0 ↔ v = 0 := by
  constructor
  · intro hz
    by_contra hn
    exact (ne_of_gt (hm v hv hn)) hz
  · intro hz
    simp [hz]

/-- A cone member has positive mass exactly when it is nonzero. -/
theorem mass_pos_iff (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) {v : V} (hv : v ∈ C) : 0 < mass v ↔ v ≠ 0 := by
  constructor
  · intro h hz
    simp [hz] at h
  · exact hm v hv

/-- Every actual packet has nonnegative weight. -/
theorem weight_nonneg (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) {v : V} (hv : v ∈ C) (i : I) :
    0 ≤ weight mass P v i := mass_nonneg C mass hm (hp i v hv)

/-- Zero-weight packets are zero, rather than additional normalized states. -/
theorem weight_zero_iff (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) {v : V} (hv : v ∈ C) (i : I) :
    weight mass P v i = 0 ↔ P i v = 0 := mass_zero_iff C mass hm (hp i v hv)

/-- Exactly the nonzero packets can be normalized. -/
theorem weight_pos_iff (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) {v : V} (hv : v ∈ C) (i : I) :
    0 < weight mass P v i ↔ P i v ≠ 0 := mass_pos_iff C mass hm (hp i v hv)

/-- The normalized positive packet belongs to the same cone. -/
theorem normalized_mem (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (P : I → V →ₗ[ℝ] V) (hp : ∀ i, Preserves C (P i))
    {v : V} (hv : v ∈ C) (i : PositiveIndex mass P v) :
    normalized mass P v i ∈ C :=
  C.smul_mem (inv_pos.mpr i.property) (hp i.val v hv)

/-- Its mass is one because its weight is genuinely positive. -/
theorem normalized_mass (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V)
    (v : V) (i : PositiveIndex mass P v) : mass (normalized mass P v i) = 1 := by
  rw [normalized, map_smul]
  change (weight mass P v i.val)⁻¹ * weight mass P v i.val = 1
  exact inv_mul_cancel₀ (ne_of_gt i.property)

/-- The normalized packet is an actual state, not an arbitrary division by zero. -/
theorem normalized_isState (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (P : I → V →ₗ[ℝ] V) (hp : ∀ i, Preserves C (P i))
    {v : V} (hv : v ∈ C) (i : PositiveIndex mass P v) :
    IsState C mass (normalized mass P v i) :=
  ⟨normalized_mem C mass P hp hv i, normalized_mass mass P v i⟩

/-- Multiplying a normalized positive packet by its weight recovers the packet. -/
theorem weighted_normalized (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V)
    (v : V) (i : PositiveIndex mass P v) :
    weight mass P v i.val • normalized mass P v i = P i.val v := by
  simp [normalized, smul_smul, ne_of_gt i.property]

variable [Fintype I]

/-- The active index type is finite, with no nonempty-index premise. -/
instance positiveIndexFintype (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V) (v : V) :
    Fintype (PositiveIndex mass P v) := Fintype.ofFinite _

/-- Completeness is an identity of the supplied linear operators. -/
def Complete (P : I → V →ₗ[ℝ] V) : Prop := ∑ i, P i = LinearMap.id

/-- Complete operators reconstruct every vector, not just normalized inputs. -/
theorem sum_packets (P : I → V →ₗ[ℝ] V) (hc : Complete P) (v : V) :
    ∑ i, P i v = v := by
  simpa only [LinearMap.sum_apply, LinearMap.id_apply] using LinearMap.congr_fun hc v

/-- The complete family retains the original mass. -/
theorem sum_weights (mass : V →ₗ[ℝ] ℝ) (P : I → V →ₗ[ℝ] V)
    (hc : Complete P) (v : V) : ∑ i, weight mass P v i = mass v := by
  unfold weight
  rw [← map_sum, sum_packets P hc]

/-- A normalized input has weights summing exactly to one. -/
theorem sum_weights_one (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (P : I → V →ₗ[ℝ] V) (hc : Complete P) {v : V} (hv : IsState C mass v) :
    ∑ i, weight mass P v i = 1 := (sum_weights mass P hc v).trans hv.2

/-- Removing the zero packets loses nothing in the reconstruction. -/
theorem sum_positive_packets (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) (hc : Complete P) {v : V} (hv : v ∈ C) :
    ∑ i : PositiveIndex mass P v, P i.val v = v := by
  classical
  let s : Finset I := Finset.univ.filter (fun i => 0 < weight mass P v i)
  have hs : ∀ i, i ∈ s ↔ 0 < weight mass P v i := by simp [s]
  calc
    (∑ i : PositiveIndex mass P v, P i.val v) = ∑ i ∈ s, P i v :=
      (Finset.sum_subtype s hs (fun i => P i v)).symm
    _ = ∑ i, P i v := by
      apply Finset.sum_subset (Finset.filter_subset _ _)
      intro i _ hi
      apply (weight_zero_iff C mass hm P hp hv i).mp
      have hn : ¬ 0 < weight mass P v i := by simpa [s] using hi
      exact le_antisymm (le_of_not_gt hn) (weight_nonneg C mass hm P hp hv i)
    _ = v := sum_packets P hc v

/-- The active weights retain the complete mass after all zero packets are removed. -/
theorem sum_positive_weights (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) (hc : Complete P) {v : V} (hv : v ∈ C) :
    (∑ i : PositiveIndex mass P v, weight mass P v i.val) = mass v := by
  unfold weight
  rw [← map_sum, sum_positive_packets C mass hm P hp hc hv]

/-- In a normalized mixture the active weights, not only all weights, sum to one. -/
theorem sum_positive_weights_one (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) (hc : Complete P) {v : V} (hv : IsState C mass v) :
    (∑ i : PositiveIndex mass P v, weight mass P v i.val) = 1 :=
  (sum_positive_weights C mass hm P hp hc hv.1).trans hv.2

/-- Exact convex-mixture reconstruction, indexed only by positive weights. -/
theorem mixture_reconstruction (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) (hc : Complete P) {v : V} (hv : v ∈ C) :
    (∑ i : PositiveIndex mass P v, weight mass P v i.val • normalized mass P v i) = v := by
  simp_rw [weighted_normalized]
  exact sum_positive_packets C mass hm P hp hc hv

/-- Source-facing Core 2.5 mixture theorem with all zero-weight and normalization clauses. -/
theorem source_core25 (C : ConvexCone ℝ V) (mass : V →ₗ[ℝ] ℝ)
    (hm : StrictMass C mass) (P : I → V →ₗ[ℝ] V)
    (hp : ∀ i, Preserves C (P i)) (hc : Complete P) {v : V} (hv : IsState C mass v) :
    (∀ i, 0 ≤ weight mass P v i) ∧
    (∑ i, weight mass P v i) = 1 ∧
    (∀ i, weight mass P v i = 0 ↔ P i v = 0) ∧
    (∀ i : PositiveIndex mass P v, IsState C mass (normalized mass P v i)) ∧
    (∑ i : PositiveIndex mass P v, weight mass P v i.val • normalized mass P v i) = v :=
  ⟨weight_nonneg C mass hm P hp hv.1, sum_weights_one C mass P hc hv,
    weight_zero_iff C mass hm P hp hv.1, normalized_isState C mass P hp hv.1,
    mixture_reconstruction C mass hm P hp hc hv.1⟩

end
end Komorebi.MachineTheory.PositivePackets
