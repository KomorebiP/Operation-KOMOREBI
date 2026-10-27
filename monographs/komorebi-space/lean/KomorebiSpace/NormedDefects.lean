import Mathlib.Analysis.Normed.Ring.Basic
import Mathlib.Tactic.NoncommRing
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# Quantitative defects and transported finite telescopes

The noncommutative ring model includes bounded endomorphism algebras when those
are supplied. Arbitrary square defects cannot be added across distinct Hom
spaces without whiskering them into a common Hom space.
-/
universe u
namespace KomorebiSpace
namespace NormedDefects

variable {R : Type u}

def defect [Ring R] (v f f' u : R) : R := v*f - f'*u

section Ring
variable [Ring R]

theorem horizontal (u v w f g f' g' : R) :
    defect w (g*f) (g'*f') u = defect w g g' v * f + g' * defect v f f' u := by
  unfold defect
  noncomm_ring

/-- Algebraic compression-shell formula, with the projection identities explicit. -/
theorem compression_shell (P Q T : R) (hPP : P*P = P) (hQP : Q*P = P) :
    (Q*T*Q)*P - P*(P*T*P) = (Q-P)*T*P := by
  calc
    (Q*T*Q)*P - P*(P*T*P) = Q*T*(Q*P) - (P*P)*T*P := by noncomm_ring
    _ = Q*T*P - P*T*P := by rw [hQP, hPP]
    _ = (Q-P)*T*P := by noncomm_ring

/-- A finite transported Stokes identity for a certified sequence of path swaps. -/
theorem transported_telescope (T A Ω B : ℕ → R)
    (hswap : ∀ k, T (k+1) - T k = A k * Ω k * B k) (n : ℕ) :
    T n - T 0 = ∑ k ∈ Finset.range n, A k * Ω k * B k := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ, ← ih, ← hswap n]
    abel
end Ring

section Normed
variable [NormedRing R]

theorem horizontal_norm (u v w f g f' g' : R) :
    ‖defect w (g*f) (g'*f') u‖ ≤
      ‖defect w g g' v‖ * ‖f‖ + ‖g'‖ * ‖defect v f f' u‖ := by
  rw [horizontal]
  exact (norm_add_le _ _).trans (add_le_add (norm_mul_le _ _) (norm_mul_le _ _))

theorem horizontal_contractive (u v w f g f' g' : R)
    (hf : ‖f‖ ≤ 1) (hg : ‖g'‖ ≤ 1) :
    ‖defect w (g*f) (g'*f') u‖ ≤ ‖defect w g g' v‖ + ‖defect v f f' u‖ := by
  calc
    ‖defect w (g*f) (g'*f') u‖ ≤
        ‖defect w g g' v‖ * ‖f‖ + ‖g'‖ * ‖defect v f f' u‖ :=
      horizontal_norm u v w f g f' g'
    _ ≤ ‖defect w g g' v‖ * 1 + 1 * ‖defect v f f' u‖ :=
      add_le_add (mul_le_mul_of_nonneg_left hf (norm_nonneg _))
        (mul_le_mul_of_nonneg_right hg (norm_nonneg _))
    _ = _ := by rw [mul_one, one_mul]

theorem whiskered_norm (a e b : R) (ha : ‖a‖ ≤ 1) (hb : ‖b‖ ≤ 1) :
    ‖a*e*b‖ ≤ ‖e‖ := by
  calc
    ‖a*e*b‖ ≤ ‖a*e‖ * ‖b‖ := norm_mul_le _ _
    _ ≤ (‖a‖*‖e‖)*‖b‖ := mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _)
    _ ≤ (1*‖e‖)*1 := mul_le_mul
      (mul_le_mul_of_nonneg_right ha (norm_nonneg _)) hb
      (norm_nonneg _) (mul_nonneg (by norm_num) (norm_nonneg _))
    _ = ‖e‖ := by rw [one_mul, mul_one]

theorem transported_stokes_bound (T A Ω B : ℕ → R)
    (hswap : ∀ k, T (k+1) - T k = A k * Ω k * B k)
    (hA : ∀ k, ‖A k‖ ≤ 1) (hB : ∀ k, ‖B k‖ ≤ 1) (n : ℕ) :
    ‖T n - T 0‖ ≤ ∑ k ∈ Finset.range n, ‖Ω k‖ := by
  rw [transported_telescope T A Ω B hswap n]
  apply (norm_sum_le _ _).trans
  apply Finset.sum_le_sum
  intro k hk
  exact whiskered_norm _ _ _ (hA k) (hB k)

end Normed
end NormedDefects
end KomorebiSpace
