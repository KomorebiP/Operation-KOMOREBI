import Komorebi.SufficientResolution.MemoryClosure
import Mathlib.LinearAlgebra.Charpoly.Basic

/-!
# A finite, dimension-controlled certificate for all-depth closure

Cayley-Hamilton is supplied by Mathlib.  Only the hidden space must be finite
 dimensional.  The zero-dimensional hidden space is included, not excluded.
-/

set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.BlockDynamics

universe uR uV uH
variable {R : Type uR} [Field R]
variable {V : Type uV} [AddCommGroup V] [Module R V]
variable {H : Type uH} [AddCommGroup H] [Module R H]
variable (b : BlockDynamics R V H)
open Polynomial

/-- A monic annihilating polynomial supplies a finite feedback certificate. -/
 theorem memory_zero_of_annihilator (p : R[X]) (hp : p.Monic)
    (hroot : aeval b.D p = 0) (h : ∀ k < p.natDegree, b.memory k = 0) :
    ∀ n, b.memory n = 0 := by
  intro n
  let q : R[X] := X^n %ₘ p
  have hpow : b.D^n = aeval b.D q := by
    have hr : aeval b.D (X^n %ₘ p) = aeval b.D (X^n) :=
      aeval_modByMonic_eq_self_of_root hroot
    simpa only [q, map_pow, aeval_X] using hr.symm
  have hd : q.degree < (p.natDegree : WithBot ℕ) := by
    have ht := degree_modByMonic_lt (X^n) hp
    rwa [degree_eq_natDegree hp.ne_zero] at ht
  ext y
  change b.B ((b.D^n) (b.G y)) = 0
  rw [hpow, aeval_eq_sum_range]
  simp only [LinearMap.sum_apply, LinearMap.smul_apply, map_sum, map_smul]
  apply Finset.sum_eq_zero
  intro k _
  by_cases hk : k < p.natDegree
  · have hz : b.B ((b.D^k) (b.G y)) = 0 := LinearMap.congr_fun (h k hk) y
    rw [hz, smul_zero]
  · have hle : (p.natDegree : WithBot ℕ) ≤ (k : WithBot ℕ) := by
      exact_mod_cast (Nat.le_of_not_gt hk)
    have hc : q.coeff k = 0 := coeff_eq_zero_of_degree_lt (hd.trans_le hle)
    rw [hc, zero_smul]

/-- A finite prefix is sufficient because the hidden characteristic polynomial annihilates D. -/
 theorem memory_zero_of_finrank_prefix [FiniteDimensional R H]
    (h : ∀ k < Module.finrank R H, b.memory k = 0) :
    ∀ n, b.memory n = 0 := by
  apply b.memory_zero_of_annihilator b.D.charpoly b.D.charpoly_monic b.D.aeval_self_charpoly
  simpa only [b.D.charpoly_natDegree] using h

 theorem memory_zero_iff_finrank_prefix [FiniteDimensional R H] :
    (∀ n, b.memory n = 0) ↔ (∀ k < Module.finrank R H, b.memory k = 0) :=
  ⟨fun h k _ => h k, b.memory_zero_of_finrank_prefix⟩

/-- Exact prepared closure reduces to d explicit hidden-return maps. -/
 theorem prepared_powers_iff_finrank_memory [FiniteDimensional R H] :
    (∀ n, b.prepared n = b.A^n) ↔
      (∀ k < Module.finrank R H, b.memory k = 0) := by
  rw [b.prepared_powers_iff_memory_zero, b.memory_zero_iff_finrank_prefix]

/-- With hidden dimension d known, checking full maps through depth d+1 is sufficient. -/
 theorem prepared_powers_iff_finite_horizon [FiniteDimensional R H] :
    (∀ n, b.prepared n = b.A^n) ↔
      (∀ n ≤ Module.finrank R H + 1, b.prepared n = b.A^n) := by
  rw [b.prepared_prefix_iff_memory_prefix, b.prepared_powers_iff_finrank_memory]

/-- Any failure of exact prepared closure has a feedback witness below hidden dimension. -/
 theorem nonclosure_has_finite_feedback_witness [FiniteDimensional R H]
    (h : ¬ ∀ n, b.prepared n = b.A^n) :
    ∃ k < Module.finrank R H, b.memory k ≠ 0 := by
  classical
  by_contra hn
  apply h
  rw [b.prepared_powers_iff_finrank_memory]
  intro k hk
  by_contra hm
  exact hn ⟨k, hk, hm⟩

end Komorebi.SufficientResolution.BlockDynamics
