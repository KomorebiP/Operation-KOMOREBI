import KomorebiSpace.DyadicInfiniteReconstruction
import Mathlib.NumberTheory.Padics.PadicVal.Basic

set_option autoImplicit false

/-!
# KS55: congruence support of the actual dyadic residual remainder

These statements use the original varying operator fibers, coarseners, target
sections and residual remainder. No fixed scalar replacement is introduced.
-/
universe u v
noncomputable section
namespace KomorebiSpace.DyadicResidual.System
open BanachTower
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (T : System.{u,v} 𝕜)

theorem finite_details_zero_coordinate_of_not_dvd (r : Residuals T.source T.target)
    (N j k : ℕ)
    (hd : ∀ i < N, T.cascade.detail r (j+i) = 0)
    (hk : ¬ 2^N ∣ k+1) : T.residualLevel r j k = 0 := by
  induction N generalizing j k with
  | zero => exact (hk (by simp)).elim
  | succ N ih =>
    let U := T.stage j
    have hh : hidden U.source U.target U.source_contractive U.target_contractive
        U.target_splitting (T.residualLevel r j) = 0 := by
      have h := hd 0 (Nat.zero_lt_succ N)
      rw [Nat.add_zero] at h
      exact h
    have hpar : k = 2*(k/2) ∨ k = 2*(k/2)+1 := by omega
    rcases hpar with he | ho
    · have hv := congrArg (fun f : Residuals U.source U.target => f (2*(k/2))) hh
      rw [hidden_even] at hv
      rw [he]
      exact hv
    · have hv := congrArg (fun f : Residuals U.source U.target => f (2*(k/2)+1)) hh
      rw [hidden_odd] at hv
      have hk' : ¬ 2^N ∣ k/2+1 := by
        rintro ⟨t, ht⟩
        apply hk
        refine ⟨t, ?_⟩
        calc
          k+1 = 2*(k/2+1) := by omega
          _ = 2*(2^N*t) := by rw [ht]
          _ = 2^(N+1)*t := by rw [pow_succ]; ring
      have hd' : ∀ i < N, T.cascade.detail r ((j+1)+i) = 0 := by
        intro i hi
        rw [show j+1+i = j+(i+1) by omega]
        exact hd (i+1) (by omega)
      have hc : coarsen U.source U.target U.source_contractive U.target_contractive
          (T.residualLevel r j) (k/2) = 0 := ih (j+1) (k/2) hd' hk'
      change T.residualLevel r j (2*(k/2)+1) -
        (U.target_splitting.up (2*(k/2))).comp
          (coarsen U.source U.target U.source_contractive U.target_contractive
            (T.residualLevel r j) (k/2)) = 0 at hv
      rw [hc, ContinuousLinearMap.comp_zero, sub_zero] at hv
      rw [ho]
      exact hv

theorem remainder_coordinate_zero_of_not_dvd
    (r : Residuals T.source T.target) (N k : ℕ) (hk : ¬ 2^N ∣ k+1) :
    T.residualRemainder N r k = 0 := by
  have hd : ∀ i < N, T.cascade.detail (T.residualRemainder N r) (0+i) = 0 := by
    intro i hi
    rw [Nat.zero_add]
    exact T.cascade.remainder_details_below r N i hi
  exact T.finite_details_zero_coordinate_of_not_dvd (T.residualRemainder N r) N 0 k hd hk

theorem reconstruction_coordinate_of_not_dvd
    (r : Residuals T.source T.target) (N k : ℕ) (hk : ¬ 2^N ∣ k+1) :
    T.reconstructedResidual N r k = r k := by
  change r k - T.residualRemainder N r k = r k
  rw [T.remainder_coordinate_zero_of_not_dvd r N k hk, sub_zero]

/-- Nonzero remainder coordinates must belong to the indicated congruence class. -/
theorem nonzero_remainder_requires_divisibility
    (r : Residuals T.source T.target) (N k : ℕ)
    (hk : T.residualRemainder N r k ≠ 0) : 2^N ∣ k+1 := by
  by_contra h
  exact hk (T.remainder_coordinate_zero_of_not_dvd r N k h)

/-- The precise sufficient coordinate threshold is the dyadic valuation, not the index. -/
theorem reconstruction_after_valuation
    (r : Residuals T.source T.target) (N k : ℕ)
    (hk : padicValNat 2 (k+1) < N) : T.reconstructedResidual N r k = r k := by
  apply T.reconstruction_coordinate_of_not_dvd r N k
  rw [padicValNat_dvd_iff_le_of_ne_one (by decide : (2:ℕ) ≠ 1) (by omega : k+1 ≠ 0)]
  exact Nat.not_le_of_lt hk

end KomorebiSpace.DyadicResidual.System
end
