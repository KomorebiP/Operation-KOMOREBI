module
public import Mathlib.NumberTheory.Padics.PadicIntegers
public import Mathlib.Topology.MetricSpace.Cauchy

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Topology

namespace Komorebi.PadicTowerLimit

/-- Later integer approximations retain every earlier prescribed precision. -/
theorem tower_pair_dvd (p L : ℕ) (z : ℕ → ℤ)
    (hstep : ∀ n, (p : ℤ) ^ (L + n) ∣ z (n + 1) - z n)
    (n m : ℕ) (hnm : n ≤ m) :
    (p : ℤ) ^ (L + n) ∣ z m - z n := by
  induction m, hnm using Nat.le_induction with
  | base => simp
  | succ m hnm ih =>
      have hs : (p : ℤ) ^ (L + n) ∣ z (m + 1) - z m :=
        (pow_dvd_pow (p : ℤ) (Nat.add_le_add_left hnm L)).trans (hstep m)
      have he : (z (m + 1) - z m) + (z m - z n) = z (m + 1) - z n := by ring
      rw [← he]
      exact dvd_add hs ih

/-- Compatible integer approximations are Cauchy in the actual p-adic metric. -/
theorem compatible_int_tower_cauchy (p L : ℕ) [Fact p.Prime]
    (z : ℕ → ℤ)
    (hstep : ∀ n, (p : ℤ) ^ (L + n) ∣ z (n + 1) - z n) :
    CauchySeq (fun n => (z n : ℤ_[p])) := by
  rw [Metric.cauchySeq_iff]
  intro ε hε
  obtain ⟨N, hN⟩ := PadicInt.exists_pow_neg_lt p hε
  refine ⟨N, ?_⟩
  intro m hm n hn
  have hm' := tower_pair_dvd p L z hstep N m hm
  have hn' := tower_pair_dvd p L z hstep N n hn
  have hd : (p : ℤ) ^ (L + N) ∣ z m - z n := by
    have he : (z m - z N) - (z n - z N) = z m - z n := by ring
    rw [← he]
    exact dvd_sub hm' hn'
  have hd' : (p : ℤ) ^ N ∣ z m - z n :=
    (pow_dvd_pow (p : ℤ) (Nat.le_add_left N L)).trans hd
  have hb := (PadicInt.norm_int_le_pow_iff_dvd (p := p)).2 hd'
  rw [dist_eq_norm]
  simpa only [Int.cast_sub] using lt_of_le_of_lt hb hN

/-- A compatible integer tower has a p-adic limit retaining every finite residue. -/
theorem compatible_int_tower_limit (p L : ℕ) [Fact p.Prime]
    (z : ℕ → ℤ)
    (hstep : ∀ n, (p : ℤ) ^ (L + n) ∣ z (n + 1) - z n) :
    ∃ a : ℤ_[p],
      Tendsto (fun n => (z n : ℤ_[p])) atTop (𝓝 a) ∧
      ∀ n, (p : ℤ_[p]) ^ (L + n) ∣ a - (z n : ℤ_[p]) := by
  obtain ⟨a, ha⟩ := cauchySeq_tendsto_of_complete
    (compatible_int_tower_cauchy p L z hstep)
  refine ⟨a, ha, ?_⟩
  intro n
  rw [← Ideal.mem_span_singleton,
    ← PadicInt.norm_le_pow_iff_mem_span_pow]
  apply le_of_tendsto ((ha.sub tendsto_const_nhds).norm)
  filter_upwards [eventually_ge_atTop n] with m hm
  have hb := (PadicInt.norm_int_le_pow_iff_dvd (p := p)).2
    (tower_pair_dvd p L z hstep n m hm)
  simpa only [Int.cast_sub] using hb

/-- The same limit construction applies coordinatewise, with convergence in the product topology. -/
theorem compatible_vector_tower_limit {ι : Type*} (p L : ℕ) [Fact p.Prime]
    (z : ℕ → ι → ℤ)
    (hstep : ∀ n i, (p : ℤ) ^ (L + n) ∣ z (n + 1) i - z n i) :
    ∃ a : ι → ℤ_[p],
      Tendsto (fun n i => (z n i : ℤ_[p])) atTop (𝓝 a) ∧
      ∀ n i, (p : ℤ_[p]) ^ (L + n) ∣ a i - (z n i : ℤ_[p]) := by
  choose a ha using fun i => compatible_int_tower_limit p L (fun n => z n i)
    (fun n => hstep n i)
  exact ⟨a, tendsto_pi_nhds.2 (fun i => (ha i).1), fun n i => (ha i).2 n⟩

/-- Diverging divisibility precision forces the actual p-adic value to tend to zero. -/
theorem divisible_int_tendsto_zero (p L : ℕ) [Fact p.Prime]
    (z : ℕ → ℤ) (hz : ∀ n, (p : ℤ) ^ (L + n) ∣ z n) :
    Tendsto (fun n => (z n : ℤ_[p])) atTop (𝓝 0) := by
  rw [Metric.tendsto_atTop]
  intro ε hε
  obtain ⟨N, hN⟩ := PadicInt.exists_pow_neg_lt p hε
  refine ⟨N, ?_⟩
  intro n hn
  have hd : (p : ℤ) ^ N ∣ z n :=
    (pow_dvd_pow (p : ℤ) (hn.trans (Nat.le_add_left n L))).trans (hz n)
  have hb := (PadicInt.norm_int_le_pow_iff_dvd (p := p)).2 hd
  simpa only [dist_zero_right] using lt_of_le_of_lt hb hN

/-- The constructed limit is unique among all p-adic limits of the integer tower. -/
theorem compatible_int_tower_unique_limit (p L : ℕ) [Fact p.Prime]
    (z : ℕ → ℤ)
    (hstep : ∀ n, (p : ℤ) ^ (L + n) ∣ z (n + 1) - z n) :
    ∃! a : ℤ_[p],
      Tendsto (fun n => (z n : ℤ_[p])) atTop (𝓝 a) ∧
      ∀ n, (p : ℤ_[p]) ^ (L + n) ∣ a - (z n : ℤ_[p]) := by
  obtain ⟨a, ha, hp⟩ := compatible_int_tower_limit p L z hstep
  exact ⟨a, ⟨ha, hp⟩, fun b hb => tendsto_nhds_unique hb.1 ha⟩

end Komorebi.PadicTowerLimit
