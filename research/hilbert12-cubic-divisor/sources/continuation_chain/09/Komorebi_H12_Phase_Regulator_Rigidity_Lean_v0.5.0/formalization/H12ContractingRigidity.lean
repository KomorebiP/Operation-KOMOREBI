module
public import Mathlib.Analysis.SpecificLimits.Normed
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.Ring
@[expose] public section
open Filter Topology
namespace H12.ContractingRigidity

/-- Invariance is propagated to every iterate, not only to sampled returns. -/
theorem invariant_all_powers (d : ℂ → ℂ) (rho : ℂ)
    (hi : ∀ z, d (rho*z) = d z) :
    ∀ (n : ℕ) (z : ℂ), d (rho^n*z) = d z := by
  intro n
  induction n with
  | zero => intro z; simp
  | succ n ih =>
    intro z
    calc
      d (rho^(n+1)*z) = d (rho*(rho^n*z)) := by congr 1; ring
      _ = d (rho^n*z) := hi _
      _ = d z := ih z

/-- A continuous normalized phase invariant under a genuine contraction
cannot carry a free phase. No gamma properties are assumed here. -/
theorem continuous_contraction_invariant_constant
    (d : ℂ → ℂ) (rho : ℂ) (hr : ‖rho‖ < 1)
    (hc : ContinuousAt d 0) (hi : ∀ z, d (rho*z) = d z) :
    ∀ z, d z = d 0 := by
  intro z
  have hp : Tendsto (fun n : ℕ => rho^n*z) atTop (𝓝 0) := by
    simpa using (tendsto_pow_atTop_nhds_zero_of_norm_lt_one hr).mul_const z
  have hl : Tendsto (fun n : ℕ => d (rho^n*z)) atTop (𝓝 (d 0)) := hc.tendsto.comp hp
  have he : (fun n : ℕ => d (rho^n*z)) = (fun _ : ℕ => d z) :=
    funext (fun n => invariant_all_powers d rho hi n z)
  rw [he] at hl
  exact tendsto_nhds_unique tendsto_const_nhds hl

theorem normalized_contraction_phase_trivial
    (d : ℂ → ℂ) (rho : ℂ) (hr : ‖rho‖ < 1)
    (hc : ContinuousAt d 0) (hi : ∀ z, d (rho*z) = d z)
    (h0 : d 0 = 1) : ∀ z, d z = 1 := by
  intro z
  rw [continuous_contraction_invariant_constant d rho hr hc hi z, h0]

end H12.ContractingRigidity
