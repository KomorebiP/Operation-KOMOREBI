module
public import KomorebiPhysics.LindbladJumps

/-!
Off-diagonal consequences of the actual distinct-jump generator. No diagonal
input restriction is imposed. Self-jumps remain excluded as in equation (4.46).
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.LindbladCoherence
open scoped BigOperators Matrix
open LindbladJumps
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- Sum of rates leaving a source label, excluding self-jumps. -/
def escapeRate (γ : n → n → ℝ) (b : n) : ℝ :=
  ∑ a, if a = b then 0 else γ a b

theorem escapeRate_nonneg (γ : n → n → ℝ) (hγ : ∀ a b, 0 ≤ γ a b) (b : n) :
    0 ≤ escapeRate γ b := by
  apply Finset.sum_nonneg
  intro a _
  by_cases hab : a = b <;> simp [hab, hγ a b]

theorem escapeRate_cast (γ : n → n → ℝ) (b : n) :
    (escapeRate γ b : ℂ) = ∑ a, if a = b then 0 else (γ a b : ℂ) := by
  simp [escapeRate]

/-- A rank-one jump creates only diagonal gain, while its two loss terms
both act on coherences touching the source. -/
theorem dissipator_offdiag (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (a b i j : n) (hγ : 0 ≤ γ a b) (hij : i ≠ j) :
    dissipator (jump γ a b) ρ i j = -(1/2 : ℂ) *
      ((if b = i then (γ a b : ℂ) else 0) + (if b = j then (γ a b : ℂ) else 0)) * ρ i j := by
  rw [dissipator_jump_entry γ ρ a b i j hγ]
  have hgain : ¬ (a = i ∧ a = j) := fun h => hij (h.1.symm.trans h.2)
  simp only [hgain, ite_false, zero_sub]
  by_cases hbi : b = i
  · subst i
    have hbj : b ≠ j := hij
    simp only [ite_true, hbj, ite_false, add_zero]
    ring
  · by_cases hbj : b = j
    · subst j
      simp only [hbi, ite_false, ite_true, zero_add]
      ring
    · simp [hbi, hbj]

/-- Exact off-diagonal reduction of the actual distinct-jump matrix sum. -/
theorem generator_offdiag (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hγ : ∀ a b, 0 ≤ γ a b) (i j : n) (hij : i ≠ j) :
    generator γ ρ i j = -(1/2 : ℂ) *
      ((escapeRate γ i : ℂ) + (escapeRate γ j : ℂ)) * ρ i j := by
  let r (a b : n) : ℂ := if a = b then 0 else (γ a b : ℂ)
  have ht (a b : n) :
      (if a = b then (0 : Matrix n n ℂ) else dissipator (jump γ a b) ρ) i j =
        -(1/2 : ℂ) * ((if b = i then r a b else 0) + (if b = j then r a b else 0)) * ρ i j := by
    by_cases hab : a = b
    · simp [hab, r]
    · simp only [hab, ite_false, dissipator_offdiag γ ρ a b i j (hγ a b) hij]
      simp only [r, hab, ite_false]
  simp only [generator, Matrix.sum_apply, ht]
  simp only [← Finset.sum_mul, ← Finset.mul_sum, Finset.sum_add_distrib]
  simp only [Finset.sum_ite_eq', Finset.mem_univ, ite_true]
  rw [escapeRate_cast, escapeRate_cast]

/-- Actual complex coherence derivative, derived from the original matrix flow. -/
theorem hasDerivAt_coherence {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (generator γ (ρ t)) t)
    (i j : n) (hij : i ≠ j) :
    HasDerivAt (fun s => ρ s i j)
      (-(1/2 : ℂ) * ((escapeRate γ i : ℂ) + (escapeRate γ j : ℂ)) * ρ t i j) t := by
  simpa only [generator_offdiag γ (ρ t) hγ i j hij] using MixedTransfer.hasDerivAt_entry hρ i j

end KomorebiPhysics.LindbladCoherence
