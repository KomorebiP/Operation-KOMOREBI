import PaperX.DenseTraceSeparation

/-! Exact trace recovery and scalar-field descent. The finite matrix comes from
actual trace values. Nonnegative capacity constraints are separate from solving
the linear equations. No compatible arithmetic system is constructed here. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.TraceRecovery

open scoped BigOperators Matrix
open PaperX.FiniteSeparation PaperX.DenseTraceSeparation
universe u v w z
variable {E : Type u} [Field E] {I : Type v} [Fintype I] [DecidableEq I]

/-- Exact recovery by the inverse of a certified square separator. -/
def recover (C : Matrix I I E) (t : I → E) : I → E := C⁻¹ *ᵥ t

theorem recover_trace (C : Matrix I I E) (h : C.det ≠ 0) (m : I → E) :
    recover C (C *ᵥ m) = m := by
  rw [recover, Matrix.mulVec_mulVec, C.nonsing_inv_mul (isUnit_iff_ne_zero.mpr h),
    Matrix.one_mulVec]

theorem recover_solves (C : Matrix I I E) (h : C.det ≠ 0) (t : I → E) :
    C *ᵥ recover C t = t := by
  rw [recover, Matrix.mulVec_mulVec, C.mul_nonsing_inv (isUnit_iff_ne_zero.mpr h),
    Matrix.one_mulVec]

theorem unique_recovery (C : Matrix I I E) (h : C.det ≠ 0) (m n : I → E)
    (ht : C *ᵥ m = C *ᵥ n) : m = n := by
  simpa [recover_trace C h] using congrArg (recover C) ht

/-- Multiplicities are natural numbers, with upper bounds from a given carrier. -/
def Admissible (capacity m : I → ℕ) : Prop := ∀ i, m i ≤ capacity i

theorem natural_multiplicity_unique [CharZero E] (C : Matrix I I E) (h : C.det ≠ 0)
    (m n : I → ℕ)
    (ht : C *ᵥ (fun i => (m i : E)) = C *ᵥ (fun i => (n i : E))) : m = n := by
  have hh := unique_recovery C h _ _ ht
  funext i
  exact Nat.cast_injective (congrFun hh i)

/-- Linear solvability does not enforce integrality, positivity, or capacities.
This equivalence keeps the carrier membership test explicit. -/
theorem admissible_trace_iff [CharZero E] (C : Matrix I I E) (h : C.det ≠ 0)
    (capacity : I → ℕ) (t : I → E) :
    (∃ m : I → ℕ, Admissible capacity m ∧ C *ᵥ (fun i => (m i : E)) = t) ↔
    ∃ m : I → ℕ, Admissible capacity m ∧ recover C t = (fun i => (m i : E)) := by
  constructor
  · rintro ⟨m, hm, rfl⟩
    exact ⟨m, hm, recover_trace C h _⟩
  · rintro ⟨m, hm, ht⟩
    exact ⟨m, hm, by rw [← ht, recover_solves C h]⟩

/-- A field embedding preserves and reflects the separator determinant. -/
theorem determinant_transport {K : Type w} [Field K] (σ : E →+* K)
    (C : Matrix I I E) : (σ.mapMatrix C).det ≠ 0 ↔ C.det ≠ 0 := by
  rw [← σ.map_det C]
  exact not_congr (by constructor
                      · intro h; exact σ.injective (by simpa using h)
                      · intro h; simp [h])

theorem mapped_trace {K : Type w} [Field K] (σ : E →+* K)
    (C : Matrix I I E) (m : I → E) :
    (σ.mapMatrix C) *ᵥ (fun i => σ (m i)) = fun j => σ ((C *ᵥ m) j) := by
  funext j
  simp [Matrix.mulVec, dotProduct]

theorem recovery_transport {K : Type w} [Field K] (σ : E →+* K)
    (C : Matrix I I E) (h : C.det ≠ 0) (t : I → E) :
    recover (σ.mapMatrix C) (fun j => σ (t j)) = fun i => σ (recover C t i) := by
  apply unique_recovery (σ.mapMatrix C) ((determinant_transport σ C).2 h)
  rw [recover_solves _ ((determinant_transport σ C).2 h), mapped_trace,
    recover_solves C h]

/-- The common algebraic trace matrix is certified over E using one coefficient
field, then stays invertible at every field embedding. No unramifiedness is inferred
for the places excluded by the arithmetic compatibility convention. -/
theorem common_trace_separator {K : Type w} [Field K] [TopologicalSpace K]
    [IsTopologicalRing K] [T2Space K]
    {G : Type z} [Group G] [TopologicalSpace G] {X : Type*}
    (σ : E →+* K) (τ : I → X → E) (f : I → G → K)
    (hc : ∀ i, Continuous (f i)) (hi : LinearIndependent K f) (s : X → G)
    (hd : DenseRange (fun p : X × G => p.2 * s p.1 * p.2⁻¹))
    (hconj : ∀ i g x, f i (g * s x * g⁻¹) = f i (s x))
    (hτ : ∀ i x, σ (τ i x) = f i (s x)) :
    ∃ v : I → X, Function.Injective v ∧ (sampleMatrix τ v).det ≠ 0 := by
  obtain ⟨v, hv, hdet⟩ := finite_conjugacy_separator f hc hi s hd hconj
  refine ⟨v, hv, (determinant_transport σ _).1 ?_⟩
  have hmat : σ.mapMatrix (sampleMatrix τ v) =
      sampleMatrix (fun i x => f i (s x)) v := by
    ext j i
    exact hτ i (v j)
  rw [hmat]
  exact hdet

end PaperX.TraceRecovery
