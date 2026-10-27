import EffectivePadicHensel

namespace Komorebi.StrongArtin.EffectiveResonance

open Polynomial

variable {p : ℕ} [Fact p.Prime]

theorem nat_degree_norm (d : ℕ) (hd : d ≠ 0) :
    ‖(d : PadicInt p)‖ = (p : ℝ) ^ (-(padicValNat p d : ℤ)) := by
  rw [PadicInt.norm_def, PadicInt.coe_natCast,
    Padic.norm_eq_zpow_neg_valuation (by exact_mod_cast hd), Padic.valuation_natCast]

theorem power_derivative_norm (d : ℕ) (hd : d ≠ 0)
    (u a : PadicInt p) (ha : IsUnit a) :
    ‖(X ^ d - C u : Polynomial (PadicInt p)).derivative.eval a‖ =
      (p : ℝ) ^ (-(padicValNat p d : ℤ)) := by
  simpa [Polynomial.derivative_X_pow, norm_mul, norm_pow, PadicInt.isUnit_iff.mp ha] using nat_degree_norm (p := p) d hd

theorem reduction_mono {m n : ℕ} (hmn : m ≤ n) {x y : PadicInt p}
    (h : PadicInt.toZModPow n x = PadicInt.toZModPow n y) :
    PadicInt.toZModPow m x = PadicInt.toZModPow m y := by
  have hh := congrArg (fun b : ZMod (p ^ n) => (ZMod.cast b : ZMod (p ^ m))) h
  simpa only [PadicInt.cast_toZModPow m n hmn] using hh

theorem unit_of_same_positive_prefix {m : ℕ} (hm : 0 < m)
    {a b : PadicInt p} (ha : IsUnit a)
    (hba : PadicInt.toZModPow m b = PadicInt.toZModPow m a) : IsUnit b := by
  have hp : (1 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).one_lt
  have hn := (reduction_eq_iff_norm m b a).mp hba
  have hlt : (p : ℝ) ^ (-(m : ℤ)) < 1 := by
    rw [← zpow_zero (p : ℝ)]
    apply (zpow_lt_zpow_iff_right₀ hp).2
    omega
  have hsmall : ‖b + -a‖ < ‖-a‖ := by
    simpa [← sub_eq_add_neg, PadicInt.isUnit_iff.mp ha] using lt_of_le_of_lt hn hlt
  apply PadicInt.isUnit_iff.mpr
  simpa [PadicInt.isUnit_iff.mp ha] using PadicInt.norm_eq_of_norm_add_lt_right hsmall

/-- Exact scalar power image on a prefix deeper than the degree valuation. -/
theorem scalar_deep_prefix_root_iff (d : ℕ) (hd : d ≠ 0)
    (u a : PadicInt p) (ha : IsUnit a) (m : ℕ) (hm : padicValNat p d < m) :
    (∃! z : PadicInt p, z ^ d = u ∧
      PadicInt.toZModPow m z = PadicInt.toZModPow m a) ↔
      PadicInt.toZModPow (m + padicValNat p d) (a ^ d) =
        PadicInt.toZModPow (m + padicValNat p d) u := by
  simpa [sub_eq_zero] using polynomial_prefix_root_iff
    (X ^ d - C u) a m (padicValNat p d) hm (power_derivative_norm d hd u a ha)

/-- A computable sufficient horizon, not asserted optimal. -/
def scalarHorizon (p d m : ℕ) : ℕ := max m (padicValNat p d + 1) + padicValNat p d

omit [Fact p.Prime] in
theorem le_scalarHorizon (d m : ℕ) : m ≤ scalarHorizon p d m := by
  unfold scalarHorizon
  omega

/-- A finite modular root above a fixed positive unit prefix suffices at this horizon.
    No compatibility or all-depth solvability premise is used. -/
theorem scalar_root_iff_finite_horizon (d : ℕ) (hd : d ≠ 0)
    (u a : PadicInt p) (ha : IsUnit a) (m : ℕ) (hm : 0 < m) :
    (∃ z : PadicInt p, z ^ d = u ∧
      PadicInt.toZModPow m z = PadicInt.toZModPow m a) ↔
    ∃ b : ZMod (p ^ scalarHorizon p d m),
      b ^ d = PadicInt.toZModPow (scalarHorizon p d m) u ∧
      (ZMod.cast b : ZMod (p ^ m)) = PadicInt.toZModPow m a := by
  constructor
  · rintro ⟨z, hz, hza⟩
    refine ⟨PadicInt.toZModPow (scalarHorizon p d m) z, ?_, ?_⟩
    · simpa only [map_pow] using congrArg (PadicInt.toZModPow (scalarHorizon p d m)) hz
    · simpa only [PadicInt.cast_toZModPow m _ (le_scalarHorizon d m)] using hza
  · rintro ⟨b, hb, hba⟩
    let B : PadicInt p := b.val
    have hB : PadicInt.toZModPow (scalarHorizon p d m) B = b := by simp [B]
    have hBm : PadicInt.toZModPow m B = PadicInt.toZModPow m a := by
      rw [← hB, PadicInt.cast_toZModPow m _ (le_scalarHorizon d m)] at hba
      exact hba
    have hBu : IsUnit B := unit_of_same_positive_prefix hm ha hBm
    let k := max m (padicValNat p d + 1)
    have hk : padicValNat p d < k := by dsimp [k]; omega
    have hpower : PadicInt.toZModPow (k + padicValNat p d) (B ^ d) =
        PadicInt.toZModPow (k + padicValNat p d) u := by
      change PadicInt.toZModPow (scalarHorizon p d m) (B ^ d) = _
      rw [map_pow, hB]
      exact hb
    obtain ⟨z, hz, _⟩ := (scalar_deep_prefix_root_iff d hd u B hBu k hk).mpr hpower
    refine ⟨z, hz.1, ?_⟩
    exact (reduction_mono (show m ≤ k by dsimp [k]; omega) hz.2).trans hBm

theorem scalar_no_root_iff_horizon_obstruction (d : ℕ) (hd : d ≠ 0)
    (u a : PadicInt p) (ha : IsUnit a) (m : ℕ) (hm : 0 < m) :
    (¬ ∃ z : PadicInt p, z ^ d = u ∧
      PadicInt.toZModPow m z = PadicInt.toZModPow m a) ↔
    ¬ ∃ b : ZMod (p ^ scalarHorizon p d m),
      b ^ d = PadicInt.toZModPow (scalarHorizon p d m) u ∧
      (ZMod.cast b : ZMod (p ^ m)) = PadicInt.toZModPow m a :=
  not_congr (scalar_root_iff_finite_horizon d hd u a ha m hm)

/-- A single finite horizon supplies the full finite-solvability premise used
    by the preceding compactness block, for scalar unit prefixes. -/
theorem scalar_horizon_iff_all_deeper_levels (d : ℕ) (hd : d ≠ 0)
    (u a : PadicInt p) (ha : IsUnit a) (m : ℕ) (hm : 0 < m) :
    (∃ b : ZMod (p ^ scalarHorizon p d m),
      b ^ d = PadicInt.toZModPow (scalarHorizon p d m) u ∧
      (ZMod.cast b : ZMod (p ^ m)) = PadicInt.toZModPow m a) ↔
    ∀ r : ℕ, m ≤ r → ∃ b : ZMod (p ^ r),
      b ^ d = PadicInt.toZModPow r u ∧
      (ZMod.cast b : ZMod (p ^ m)) = PadicInt.toZModPow m a := by
  constructor
  · intro h r hmr
    obtain ⟨z, hz, hza⟩ := (scalar_root_iff_finite_horizon d hd u a ha m hm).mpr h
    refine ⟨PadicInt.toZModPow r z, ?_, ?_⟩
    · simpa only [map_pow] using congrArg (PadicInt.toZModPow r) hz
    · simpa only [PadicInt.cast_toZModPow m r hmr] using hza
  · intro h
    exact h (scalarHorizon p d m) (le_scalarHorizon d m)

/-- Existence alone has the same deep-prefix criterion. -/
theorem scalar_deep_prefix_exists_iff (d : ℕ) (hd : d ≠ 0)
    (u a : PadicInt p) (ha : IsUnit a) (m : ℕ) (hm : padicValNat p d < m) :
    (∃ z : PadicInt p, z ^ d = u ∧
      PadicInt.toZModPow m z = PadicInt.toZModPow m a) ↔
      PadicInt.toZModPow (m + padicValNat p d) (a ^ d) =
        PadicInt.toZModPow (m + padicValNat p d) u := by
  constructor
  · rintro ⟨z, hz, hza⟩
    let P : Polynomial (PadicInt p) := Polynomial.X ^ d - Polynomial.C u
    have hp : (1 : ℝ) < p := by exact_mod_cast (Fact.out : p.Prime).one_lt
    have hsmall : ‖z - a‖ < ‖P.derivative.eval a‖ := by
      rw [power_derivative_norm d hd u a ha]
      apply lt_of_le_of_lt ((reduction_eq_iff_norm m z a).mp hza)
      apply (zpow_lt_zpow_iff_right₀ hp).2
      omega
    have he := polynomial_norm_difference P a z hsmall
    have hh : ‖P.eval a‖ ≤ ‖P.derivative.eval a‖ * (p : ℝ) ^ (-(m : ℤ)) := by
      have hzero : P.eval z = 0 := by simp [P, hz]
      simp only [hzero, zero_sub, norm_neg] at he
      rw [he]
      exact mul_le_mul_of_nonneg_left ((reduction_eq_iff_norm m z a).mp hza) (norm_nonneg _)
    have hrad : (p : ℝ) ^ (-(m : ℤ)) < ‖P.derivative.eval a‖ := by
      rw [power_derivative_norm d hd u a ha]
      apply (zpow_lt_zpow_iff_right₀ hp).2
      omega
    have huniq := (polynomial_ball_root_iff P a _ (zpow_nonneg (by positivity) _) hrad).mpr hh
    have huniq' : ∃! w : PadicInt p, w ^ d = u ∧
        PadicInt.toZModPow m w = PadicInt.toZModPow m a := by
      simpa only [P, Polynomial.eval_sub, Polynomial.eval_pow, Polynomial.eval_X,
        Polynomial.eval_C, sub_eq_zero, ← reduction_eq_iff_norm] using huniq
    exact (scalar_deep_prefix_root_iff d hd u a ha m hm).mp huniq'
  · intro h
    exact ((scalar_deep_prefix_root_iff d hd u a ha m hm).mpr h).exists

end Komorebi.StrongArtin.EffectiveResonance
