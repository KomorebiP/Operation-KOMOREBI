module
public import PolynomialPadicUnique

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Topology

namespace Komorebi.PolynomialParameterPath
open Komorebi.PolynomialPadicUnique

variable {k : ℕ}

/-- Truncate a prescribed p-adic parameter while retaining the exact initial
integer representative, rather than replacing it by its canonical residue. -/
def parameterPath (p L : ℕ) [Fact (Nat.Prime p)] (x : Fin k → ℤ)
    (τ : Fin k → ℤ_[p]) : ℕ → Fin k → ℤ
  | 0 => x
  | n + 1 => truncInt p (L + n + 1) τ

@[simp] theorem parameterPath_zero (p L : ℕ) [Fact (Nat.Prime p)]
    (x : Fin k → ℤ) (τ : Fin k → ℤ_[p]) :
    parameterPath p L x τ 0 = x := rfl

/-- Every stage retains its full requested precision relative to the target. -/
theorem parameterPath_precision (p L : ℕ) [Fact (Nat.Prime p)]
    (x : Fin k → ℤ) (τ : Fin k → ℤ_[p])
    (hτ : ∀ i, (p : ℤ_[p])^L ∣ τ i - (x i : ℤ_[p])) (n : ℕ) (i : Fin k) :
    (p : ℤ_[p])^(L+n) ∣ τ i - (parameterPath p L x τ n i : ℤ_[p]) := by
  cases n with
  | zero => simpa only [Nat.add_zero, parameterPath] using hτ i
  | succ n =>
      simpa only [parameterPath, Nat.add_assoc] using
        truncInt_precision p (L+n+1) τ i

/-- Successive parameter representatives are compatible over the integers. -/
theorem parameterPath_compatible (p L : ℕ) [Fact (Nat.Prime p)]
    (x : Fin k → ℤ) (τ : Fin k → ℤ_[p])
    (hτ : ∀ i, (p : ℤ_[p])^L ∣ τ i - (x i : ℤ_[p])) :
    ∀ n i, (p : ℤ)^(L+n) ∣
      (parameterPath p L x τ (n+1) - parameterPath p L x τ n) i := by
  intro n i
  apply (int_pow_dvd_iff p (L+n) _).mpr
  have hnext := dvd_trans (pow_dvd_pow (p : ℤ_[p]) (by omega : L+n ≤ L+(n+1)))
    (parameterPath_precision p L x τ hτ (n+1) i)
  simpa only [Pi.sub_apply, Int.cast_sub, sub_sub_sub_cancel_left] using
    dvd_sub (parameterPath_precision p L x τ hτ n i) hnext

/-- The constructed parameter path converges to the prescribed target itself. -/
theorem parameterPath_tendsto (p L : ℕ) [Fact (Nat.Prime p)]
    (x : Fin k → ℤ) (τ : Fin k → ℤ_[p])
    (hτ : ∀ i, (p : ℤ_[p])^L ∣ τ i - (x i : ℤ_[p])) :
    Tendsto (fun n i => (parameterPath p L x τ n i : ℤ_[p])) atTop (𝓝 τ) := by
  apply tendsto_pi_nhds.mpr
  intro i
  rw [Metric.tendsto_atTop]
  intro ε hε
  obtain ⟨N, hN⟩ := PadicInt.exists_pow_neg_lt p hε
  refine ⟨N, ?_⟩
  intro n hn
  have hd : (p : ℤ_[p])^N ∣ τ i - (parameterPath p L x τ n i : ℤ_[p]) :=
    dvd_trans (pow_dvd_pow (p : ℤ_[p]) (by omega))
      (parameterPath_precision p L x τ hτ n i)
  have hb := (PadicInt.norm_le_pow_iff_mem_span_pow
    (τ i - (parameterPath p L x τ n i : ℤ_[p])) N).mpr
    (Ideal.mem_span_singleton.mpr hd)
  rw [dist_comm, dist_eq_norm]
  exact lt_of_le_of_lt hb hN

/-- Every p-adic parameter in the base residue ball supplies an actual compatible
integer path, with exact initial representative and all retained precisions. -/
theorem exists_parameter_path (p L : ℕ) [Fact (Nat.Prime p)]
    (x : Fin k → ℤ) (τ : Fin k → ℤ_[p])
    (hτ : ∀ i, (p : ℤ_[p])^L ∣ τ i - (x i : ℤ_[p])) :
    ∃ t : ℕ → Fin k → ℤ,
      t 0 = x ∧
      (∀ n i, (p : ℤ)^(L+n) ∣ (t (n+1) - t n) i) ∧
      (∀ n i, (p : ℤ_[p])^(L+n) ∣ τ i - (t n i : ℤ_[p])) ∧
      Tendsto (fun n i => (t n i : ℤ_[p])) atTop (𝓝 τ) := by
  exact ⟨parameterPath p L x τ, rfl,
    parameterPath_compatible p L x τ hτ, parameterPath_precision p L x τ hτ,
    parameterPath_tendsto p L x τ hτ⟩

#print axioms parameterPath
#print axioms parameterPath_zero
#print axioms parameterPath_precision
#print axioms parameterPath_compatible
#print axioms parameterPath_tendsto
#print axioms exists_parameter_path

end Komorebi.PolynomialParameterPath
