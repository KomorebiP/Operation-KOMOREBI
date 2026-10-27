module
public import PadicTowerLimit

@[expose] public section
noncomputable section
set_option autoImplicit false
open Filter Topology

example (p L : ℕ) [Fact p.Prime] (z : ℕ → ℤ)
    (hstep : ∀ n, (p : ℤ) ^ (L + n) ∣ z (n + 1) - z n) :
    ∃ a : ℤ_[p],
      Tendsto (fun n => (z n : ℤ_[p])) atTop (𝓝 a) ∧
      ∀ n, (p : ℤ_[p]) ^ (L + n) ∣ a - (z n : ℤ_[p]) :=
  Komorebi.PadicTowerLimit.compatible_int_tower_limit p L z hstep

example {ι : Type*} (p L : ℕ) [Fact p.Prime] (z : ℕ → ι → ℤ)
    (hstep : ∀ n i, (p : ℤ) ^ (L + n) ∣ z (n + 1) i - z n i) :
    ∃ a : ι → ℤ_[p],
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 a) ∧
      ∀ n i, (p : ℤ_[p]) ^ (L + n) ∣ a i - (z n i : ℤ_[p]) :=
  Komorebi.PadicTowerLimit.compatible_vector_tower_limit p L z hstep

example (p L : ℕ) [Fact p.Prime] (z : ℕ → ℤ)
    (hz : ∀ n, (p : ℤ) ^ (L + n) ∣ z n) :
    Tendsto (fun n => (z n : ℤ_[p])) atTop (𝓝 0) :=
  Komorebi.PadicTowerLimit.divisible_int_tendsto_zero p L z hz

#print axioms Komorebi.PadicTowerLimit.tower_pair_dvd
#print axioms Komorebi.PadicTowerLimit.compatible_int_tower_cauchy
#print axioms Komorebi.PadicTowerLimit.compatible_int_tower_limit
#print axioms Komorebi.PadicTowerLimit.compatible_vector_tower_limit
#print axioms Komorebi.PadicTowerLimit.divisible_int_tendsto_zero
#print axioms Komorebi.PadicTowerLimit.compatible_int_tower_unique_limit
