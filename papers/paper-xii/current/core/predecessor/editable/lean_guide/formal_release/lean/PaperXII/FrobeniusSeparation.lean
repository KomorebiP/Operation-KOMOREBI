import PaperXII.ReuseFiniteSeparation

/-! Paper XII 10.9. Samples lie in the actual domain of the supplied functions.
The existence proof is reused from Paper X; the inverse formula and natural
multiplicity recovery are proved here. Natural multiplicities require characteristic zero. -/
namespace PaperXII.FrobeniusSeparation

open scoped BigOperators
open PaperX.FiniteSeparation

variable {K I Ω : Type*} [Field K] [Fintype I] [DecidableEq I]

/-- The trace function of a carrier with coefficients c. -/
def combination (t : I → Ω → K) (c : I → K) : Ω → K :=
  fun v ↦ ∑ i, c i * t i v

/-- Values at the selected points, in row order. -/
def samples (t : I → Ω → K) (s : I → Ω) (c : I → K) : I → K :=
  fun j ↦ combination t c (s j)

omit [DecidableEq I] in
/-- The measurement map is multiplication by the actual evaluation matrix. -/
theorem samples_eq_mulVec (t : I → Ω → K) (s : I → Ω) (c : I → K) :
    samples t s c = (sampleMatrix t s).mulVec c := by
  funext j
  simp only [samples, combination, sampleMatrix, Matrix.mulVec, dotProduct, mul_comm]

/-- Recover coefficients using the inverse evaluation matrix. -/
noncomputable def recover (t : I → Ω → K) (s : I → Ω) (values : I → K) : I → K :=
  (sampleMatrix t s)⁻¹.mulVec values

/-- The inverse formula recovers every coefficient vector from its measured values. -/
theorem recover_samples (t : I → Ω → K) (s : I → Ω)
    (h : (sampleMatrix t s).det ≠ 0) (c : I → K) :
    recover t s (samples t s c) = c := by
  rw [recover, samples_eq_mulVec, Matrix.mulVec_mulVec,
    Matrix.nonsing_inv_mul _ (isUnit_iff_ne_zero.mpr h), Matrix.one_mulVec]

/-- Nonsingular samples determine coefficients uniquely. -/
theorem samples_injective (t : I → Ω → K) (s : I → Ω)
    (h : (sampleMatrix t s).det ≠ 0) : Function.Injective (samples t s) := by
  intro c d hcd
  have heq := congrArg (recover t s) hcd
  simpa only [recover_samples t s h] using heq

/-- Claim 10.9, including the actual inverse formula for recovery. -/
theorem exists_separator_and_recovery (t : I → Ω → K) (hi : LinearIndependent K t) :
    ∃ s : I → Ω, Function.Injective s ∧ (sampleMatrix t s).det ≠ 0 ∧
      (∀ c, recover t s (samples t s c) = c) ∧ Function.Injective (samples t s) := by
  obtain ⟨s, hs, hdet⟩ := exists_nonsingular_samples t hi
  exact ⟨s, hs, hdet, recover_samples t s hdet, samples_injective t s hdet⟩

/-- The selected measurements recover natural multiplicities in characteristic zero. -/
theorem natural_multiplicities_unique [CharZero K] (t : I → Ω → K) (s : I → Ω)
    (h : (sampleMatrix t s).det ≠ 0) (m n : I → ℕ)
    (heq : samples t s (fun i ↦ (m i : K)) = samples t s (fun i ↦ (n i : K))) : m = n := by
  have hc := samples_injective t s h heq
  funext i
  exact Nat.cast_injective (congrFun hc i)

/-- The multiplicity separator exists; invertibility is derived from functional independence. -/
theorem exists_multiplicity_separator [CharZero K] (t : I → Ω → K)
    (hi : LinearIndependent K t) :
    ∃ s : I → Ω, Function.Injective s ∧ (sampleMatrix t s).det ≠ 0 ∧
      ∀ m n : I → ℕ,
        samples t s (fun i ↦ (m i : K)) = samples t s (fun i ↦ (n i : K)) → m = n := by
  obtain ⟨s, hs, hdet⟩ := exists_nonsingular_samples t hi
  exact ⟨s, hs, hdet, natural_multiplicities_unique t s hdet⟩

/-- Without functional independence, no square evaluation matrix can be invertible. -/
theorem dependent_has_no_separator (t : I → Ω → K) (h : ¬ LinearIndependent K t)
    (s : I → Ω) : (sampleMatrix t s).det = 0 := by
  by_contra hdet
  exact h (independent_of_separator t s hdet)

end PaperXII.FrobeniusSeparation
