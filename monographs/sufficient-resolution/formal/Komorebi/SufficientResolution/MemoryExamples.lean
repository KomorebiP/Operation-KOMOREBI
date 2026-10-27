import Komorebi.SufficientResolution.SplitMemory
import Komorebi.SufficientResolution.Examples

/-!
# Exact controls for feedback delay and prepared-versus-all-state closure

These rational examples exercise the new general theorems. They are not used
as evidence replacing the all-depth proofs.
-/

set_option autoImplicit false
namespace Komorebi.SufficientResolution.MemoryExamples

/-- A two-dimensional hidden chain returns to the visible coordinate after three steps. -/
def delayedCycle : BlockDynamics ℚ ℚ (ℚ × ℚ) where
  A := 0
  B := LinearMap.fst ℚ ℚ ℚ
  G := LinearMap.inr ℚ ℚ ℚ
  D := (LinearMap.inl ℚ ℚ ℚ).comp (LinearMap.snd ℚ ℚ ℚ)

 theorem delayed_step_is_original : delayedCycle.step = Examples.rotate := by
  apply LinearMap.ext
  intro p
  simp [BlockDynamics.step, delayedCycle, Examples.rotate]

 theorem delayed_memory_zero : delayedCycle.memory 0 = 0 := by
  apply LinearMap.ext
  intro y
  rfl

 theorem delayed_memory_one : delayedCycle.memory 1 = 1 := by
  apply LinearMap.ext
  intro y
  rfl

 theorem delayed_hidden_square : delayedCycle.D^2 = 0 := by
  apply LinearMap.ext
  intro z
  rfl

 theorem delayed_memory_tail (n : ℕ) : delayedCycle.memory (n+2) = 0 := by
  apply LinearMap.ext
  intro y
  simp only [BlockDynamics.memory_apply, pow_add, delayed_hidden_square, mul_zero,
    LinearMap.zero_apply, map_zero]

 theorem delayed_correct_through_two (n : ℕ) (hn : n ≤ 2) :
    delayedCycle.prepared n = delayedCycle.A^n := by
  apply delayedCycle.prepared_prefix_of_memory_prefix 1 _ n hn
  intro k hk
  have h : k = 0 := by omega
  rw [h, delayed_memory_zero]

 theorem delayed_exact_error_at_three :
    delayedCycle.prepared 3 - delayedCycle.A^3 = 1 := by
  rw [delayedCycle.first_return_discrepancy 1]
  · exact delayed_memory_one
  · intro j hj
    have h : j = 0 := by omega
    rw [h, delayed_memory_zero]

/-- Nonzero entry and return maps need not form an active feedback path. -/
def invisibleExcursion : BlockDynamics ℚ ℚ (ℚ × ℚ) where
  A := 1
  B := LinearMap.fst ℚ ℚ ℚ
  G := LinearMap.inr ℚ ℚ ℚ
  D := 1

 theorem invisible_memory_zero (n : ℕ) : invisibleExcursion.memory n = 0 := by
  apply LinearMap.ext
  intro y
  simp [BlockDynamics.memory, invisibleExcursion]

 theorem invisible_prepared_exact (n : ℕ) :
    invisibleExcursion.prepared n = invisibleExcursion.A^n :=
  invisibleExcursion.prepared_powers_of_memory_zero invisible_memory_zero n

 theorem invisible_entry_nonzero : invisibleExcursion.G ≠ 0 := by
  intro h
  have hh := congrArg (fun f : ℚ →ₗ[ℚ] (ℚ × ℚ) => (f 1).2) h
  norm_num [invisibleExcursion] at hh

 theorem invisible_return_nonzero : invisibleExcursion.B ≠ 0 := by
  intro h
  have hh := LinearMap.congr_fun h (1,0)
  norm_num [invisibleExcursion] at hh

 theorem invisible_not_all_state_closed :
    ¬ ∀ n y z, invisibleExcursion.visible n y z = (invisibleExcursion.A^n) y := by
  rw [invisibleExcursion.all_state_closure_iff_B_zero]
  exact invisible_return_nonzero

end Komorebi.SufficientResolution.MemoryExamples
