import Komorebi.SufficientResolution.DiscreteMemory

/-!
# Exact closure iff every hidden feedback coefficient vanishes

The converse is essential: this module does not only prove sufficient invariance.
Prepared hidden state and arbitrary hidden state have different exact criteria.
-/

set_option autoImplicit false
namespace Komorebi.SufficientResolution.BlockDynamics

universe uR uV uH
variable {R : Type uR} [CommRing R]
variable {V : Type uV} [AddCommGroup V] [Module R V]
variable {H : Type uH} [AddCommGroup H] [Module R H]
variable (b : BlockDynamics R V H)

/-- Zero feedback at every delay gives exact prepared dynamics at every depth. -/
 theorem prepared_powers_of_memory_zero (h : ∀ k, b.memory k = 0) (n : ℕ) :
    b.prepared n = b.A^n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [b.prepared_recurrence]
    simp only [h, zero_mul, Finset.sum_const_zero, add_zero, ih]
    exact (pow_succ' b.A n).symm

/-- Conversely, exact prepared dynamics force every feedback coefficient to vanish. -/
 theorem memory_zero_of_prepared_powers (h : ∀ n, b.prepared n = b.A^n) :
    ∀ k, b.memory k = 0 := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    have he := b.prepared_first_return k ih
    rw [h (k+2), h (k+1)] at he
    have hp : b.A * b.A^(k+1) = b.A^(k+2) := (pow_succ' b.A (k+1)).symm
    rw [hp] at he
    exact add_left_cancel (he.symm.trans (add_zero _).symm)

 theorem prepared_powers_iff_memory_zero :
    (∀ n, b.prepared n = b.A^n) ↔ (∀ k, b.memory k = 0) :=
  ⟨b.memory_zero_of_prepared_powers, b.prepared_powers_of_memory_zero⟩

/-- Exact semigroup composition of prepared evolution has the same criterion. -/
 theorem prepared_semigroup_iff_memory_zero :
    (∀ m n, b.prepared (m+n) = b.prepared m * b.prepared n) ↔
      (∀ k, b.memory k = 0) := by
  constructor
  · intro h
    apply b.memory_zero_of_prepared_powers
    intro n
    induction n with
    | zero => simp
    | succ n ih => rw [h n 1, ih, b.prepared_one, pow_succ]
  · intro h m n
    simp only [b.prepared_powers_of_memory_zero h, pow_add]

/-- The existing split-compression defect is the same obstruction at all depths. -/
 theorem power_defects_zero_iff_memory_zero :
    (∀ m n, b.compression.defect (b.step^m) (b.step^n) = 0) ↔
      (∀ k, b.memory k = 0) := by
  rw [← b.prepared_semigroup_iff_memory_zero]
  simp only [SplitCompression.defect, sub_eq_zero, ← pow_add, prepared]

/-- All-state closure requires independence from arbitrary hidden initial states. -/
 theorem visible_powers_of_B_zero (hB : b.B = 0) (n : ℕ) (y : V) (z : H) :
    b.visible n y z = (b.A^n) y := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [b.visible_succ, hB, LinearMap.zero_apply, add_zero, ih]
    rw [pow_succ', Module.End.mul_apply]

 theorem all_state_closure_iff_B_zero :
    (∀ n y z, b.visible n y z = (b.A^n) y) ↔ b.B = 0 := by
  constructor
  · intro h
    ext z
    have hh := h 1 0 z
    simpa [visible, step] using hh
  · exact b.visible_powers_of_B_zero

/-- No return coupling implies prepared closure, with no condition on entry coupling. -/
 theorem memory_zero_of_B_zero (hB : b.B = 0) (k : ℕ) : b.memory k = 0 := by
  ext y
  simp only [memory_apply, hB, LinearMap.zero_apply]

/-- No entry coupling implies prepared closure even if hidden initial states are observable. -/
 theorem memory_zero_of_G_zero (hG : b.G = 0) (k : ℕ) : b.memory k = 0 := by
  ext y
  simp only [memory_apply, hG, LinearMap.zero_apply, map_zero]

/-- Finite-horizon agreement identifies each feedback coefficient tested by that horizon. -/
 theorem memory_prefix_zero_of_prepared_prefix (N : ℕ)
    (h : ∀ n ≤ N+1, b.prepared n = b.A^n) :
    ∀ k < N, b.memory k = 0 := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro hk
    have he := b.prepared_first_return k (fun j hj => ih j hj (by omega))
    rw [h (k+2) (by omega), h (k+1) (by omega)] at he
    have hp : b.A * b.A^(k+1) = b.A^(k+2) := (pow_succ' b.A (k+1)).symm
    rw [hp] at he
    exact add_left_cancel (he.symm.trans (add_zero _).symm)

/-- Vanishing of a feedback prefix gives exactly the corresponding prepared horizon. -/
 theorem prepared_prefix_of_memory_prefix (N : ℕ) (h : ∀ k < N, b.memory k = 0) :
    ∀ n ≤ N+1, b.prepared n = b.A^n := by
  intro n
  induction n with
  | zero => intro _; simp
  | succ n ih =>
    intro hn
    rw [b.prepared_recurrence, ih (by omega)]
    have hs : ∑ j ∈ Finset.range n, b.memory (n-1-j) * b.prepared j = 0 := by
      apply Finset.sum_eq_zero
      intro j hj
      have hjn := Finset.mem_range.mp hj
      rw [h (n-1-j) (by omega), zero_mul]
    rw [hs, add_zero]
    exact (pow_succ' b.A n).symm

 theorem prepared_prefix_iff_memory_prefix (N : ℕ) :
    (∀ n ≤ N+1, b.prepared n = b.A^n) ↔ (∀ k < N, b.memory k = 0) :=
  ⟨b.memory_prefix_zero_of_prepared_prefix N, b.prepared_prefix_of_memory_prefix N⟩

/-- A first nonzero hidden return is detected exactly two transitions later. -/
 theorem first_return_discrepancy (k : ℕ) (h : ∀ j < k, b.memory j = 0) :
    b.prepared (k+2) - b.A^(k+2) = b.memory k := by
  rw [b.prepared_first_return k h,
    b.prepared_prefix_of_memory_prefix k h (k+1) (by omega)]
  have hp : b.A * b.A^(k+1) = b.A^(k+2) := (pow_succ' b.A (k+1)).symm
  rw [hp]
  abel

 theorem first_return_detected (k : ℕ) (h : ∀ j < k, b.memory j = 0)
    (hk : b.memory k ≠ 0) : b.prepared (k+2) ≠ b.A^(k+2) := by
  intro he
  apply hk
  rw [← b.first_return_discrepancy k h, he, sub_self]

end Komorebi.SufficientResolution.BlockDynamics
