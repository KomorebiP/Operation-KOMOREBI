/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ReducedZeroCounting
import Mathlib.Topology.Algebra.InfiniteSum.Real

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Asymptotics

/-- Reciprocal-power convergence over all distinct zeros, weighted by their
actual analytic multiplicity. -/
def ZeroPowerSummable (f : ℂ → ℂ) (s : ℝ) : Prop :=
  Summable (fun z : {z : ℂ // f z = 0} =>
    (analyticOrderNatAt f z : ℝ) / ‖(z : ℂ)‖ ^ s)

theorem summable_iff_comp_of_finite_complement {α β : Type*} (i : α → β)
    (hi : Function.Injective i) (hc : (range i)ᶜ.Finite) (f : β → ℝ) :
    Summable f ↔ Summable (f ∘ i) := by
  have h : Summable (fun x : range i => f x) ↔ Summable f := by
    have h := hc.summable_compl_iff (f := f)
    rw [compl_compl] at h
    exact h
  rw [← h]
  exact exists_congr (fun _ => hi.hasSum_range_iff)

theorem SignedZeroEnumeration.root_equivalent_lattice {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) :
    e.root ~[atTop] (fun m : ℕ => (Real.pi / Real.sin (Real.pi / N)) * m) := by
  let A := Real.pi / Real.sin (Real.pi / N)
  have hA : 0 < A := div_pos Real.pi_pos (signed_sine_pos hN)
  have hb : (fun m : ℕ => e.root m - A * m) =O[atTop] (fun _ => (1 : ℝ)) := by
    apply isBigO_iff.mpr
    refine ⟨A * e.shift, ?_⟩
    filter_upwards [] with m
    have hw := e.windows m
    rw [norm_one, mul_one, Real.norm_eq_abs, abs_le]
    dsimp [A] at *
    constructor <;> nlinarith
  have ht : Tendsto (fun m : ℕ => ‖A * (m : ℝ)‖) atTop atTop := by
    simpa only [Real.norm_eq_abs, abs_of_nonneg (mul_nonneg hA.le (Nat.cast_nonneg _))] using
      (tendsto_natCast_atTop_atTop (R := ℝ)).const_mul_atTop hA
  exact hb.trans_isLittleO (isLittleO_const_left.mpr (Or.inr ht))

theorem SignedZeroEnumeration.root_reciprocal_rpow_summable_iff {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) (s : ℝ) :
    Summable (fun m => 1 / e.root m ^ s) ↔ 1 < s := by
  let A := Real.pi / Real.sin (Real.pi / N)
  have hA : 0 < A := div_pos Real.pi_pos (signed_sine_pos hN)
  have hp : 0 ≤ (fun m : ℕ => A * m) := fun m => mul_nonneg hA.le (Nat.cast_nonneg m)
  have he := (IsEquivalent.rpow hp (e.root_equivalent_lattice hN) (r := s)).inv
  have heq : (fun m => 1 / e.root m ^ s) ~[atTop]
      (fun m : ℕ => 1 / (A * m) ^ s) := by simpa only [one_div] using! he
  rw [heq.summable_iff_nat]
  have hf : (fun m : ℕ => 1 / (A * m) ^ s) =
      (fun m : ℕ => (1 / A ^ s) * (1 / (m : ℝ) ^ s)) := by
    funext m
    rw [Real.mul_rpow hA.le (Nat.cast_nonneg m)]
    ring
  rw [hf, summable_mul_left_iff (one_div_ne_zero (ne_of_gt (Real.rpow_pos_of_pos hA s)))]
  exact Real.summable_one_div_nat_rpow

theorem SignedZeroEnumeration.reducedRoot_reciprocal_rpow_summable_iff {N : ℕ} (hN : 2 ≤ N)
    (e : SignedZeroEnumeration N) (s : ℝ) :
    Summable (fun m => 1 / ‖e.reducedRoot m‖ ^ s) ↔ 1 < (N : ℝ) * s := by
  have he : (fun m => 1 / ‖e.reducedRoot m‖ ^ s) =
      (fun m => 1 / e.root m ^ ((N : ℝ) * s)) := by
    funext m
    rw [e.reducedRoot_norm, ← Real.rpow_natCast_mul (e.positive m).le]
  rw [he]
  exact e.root_reciprocal_rpow_summable_iff hN _

def SignedZeroEnumeration.orbitZero {N : ℕ} (hN : 0 < N) (e : SignedZeroEnumeration N)
    (p : Fin N × ℕ) : {z : ℂ // canonicalSignedDenominator N z = 0} :=
  ⟨e.orbit p, (e.orbit_zero_simple hN p).1⟩

theorem SignedZeroEnumeration.orbitZero_injective {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) : Function.Injective (e.orbitZero hN) := by
  intro p q h
  exact e.orbit_injective hN (congrArg Subtype.val h)

theorem SignedZeroEnumeration.orbitZero_finite_complement {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) : (range (e.orbitZero hN))ᶜ.Finite := by
  have hf : (Subtype.val ⁻¹' e.exceptions : Set {z : ℂ // canonicalSignedDenominator N z = 0}).Finite :=
    (e.exceptions_finite hN).preimage Subtype.val_injective.injOn
  apply hf.subset
  intro z hz
  have hd : (z : ℂ) ∈ zeroDisk (canonicalSignedDenominator N) ‖(z : ℂ)‖ := ⟨le_rfl, z.property⟩
  rcases e.zeroDisk_subset_union hN _ hd with ht | he
  · obtain ⟨p, _, hp⟩ := ht
    exact False.elim (hz ⟨p, Subtype.ext hp⟩)
  · exact he

def SignedZeroEnumeration.reducedZero {N : ℕ} (hN : 0 < N) (e : SignedZeroEnumeration N)
    (m : ℕ) : {z : ℂ // entireReducedDenominator N z = 0} :=
  ⟨e.reducedRoot m, (e.reducedRoot_zero_simple hN m).1⟩

theorem SignedZeroEnumeration.reducedZero_injective {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) : Function.Injective (e.reducedZero hN) := by
  intro m n h
  exact e.reducedRoot_injective hN (congrArg Subtype.val h)

theorem SignedZeroEnumeration.reducedZero_finite_complement {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) : (range (e.reducedZero hN))ᶜ.Finite := by
  have hf : (Subtype.val ⁻¹' e.reducedExceptions : Set {z : ℂ // entireReducedDenominator N z = 0}).Finite :=
    (e.reducedExceptions_finite hN).preimage Subtype.val_injective.injOn
  apply hf.subset
  intro z hz
  let r := ‖(z : ℂ)‖ ^ (1 / (N : ℝ))
  have hr : 0 ≤ r := Real.rpow_nonneg (norm_nonneg (z : ℂ)) _
  have hp : r ^ N = ‖(z : ℂ)‖ := by
    simpa only [r, one_div] using Real.rpow_inv_natCast_pow (norm_nonneg (z : ℂ)) hN.ne'
  have hd : (z : ℂ) ∈ zeroDisk (entireReducedDenominator N) (r ^ N) :=
    ⟨hp.ge, z.property⟩
  rcases e.reducedZeroDisk_subset_union hN hr hd with ht | he
  · obtain ⟨m, _, hm⟩ := ht
    exact False.elim (hz ⟨m, Subtype.ext hm⟩)
  · exact he

/-- The convergence exponent of the full denominator zero multiset is exactly one. -/
theorem canonicalSignedDenominator_zero_power_summable_iff {N : ℕ} (hN : 2 ≤ N) (s : ℝ) :
    ZeroPowerSummable (canonicalSignedDenominator N) s ↔ 1 < s := by
  let e := canonicalZeroEnumeration hN
  have hn : 0 < N := by omega
  unfold ZeroPowerSummable
  rw [summable_iff_comp_of_finite_complement (e.orbitZero hn) (e.orbitZero_injective hn)
    (e.orbitZero_finite_complement hn)]
  have he : ((fun z : {z : ℂ // canonicalSignedDenominator N z = 0} =>
      (analyticOrderNatAt (canonicalSignedDenominator N) z : ℝ) / ‖(z : ℂ)‖ ^ s) ∘ e.orbitZero hn) =
      (fun p : Fin N × ℕ => 1 / e.root p.2 ^ s) := by
    funext p
    simp only [Function.comp_apply, SignedZeroEnumeration.orbitZero,
      (e.orbit_zero_simple hn p).2, Nat.cast_one, e.orbit_norm hn]
  rw [he]
  have hp : Summable (fun p : Fin N × ℕ => 1 / e.root p.2 ^ s) ↔
      Summable (fun m => 1 / e.root m ^ s) := by
    constructor
    · intro h
      exact h.prod_factor ⟨0, hn⟩
    · intro h
      exact (summable_prod_of_nonneg (f := fun p : Fin N × ℕ => 1 / e.root p.2 ^ s) (fun p => (one_div_pos.mpr (Real.rpow_pos_of_pos (e.positive p.2) s)).le)).mpr
        ⟨fun _ => h, (hasSum_fintype _).summable⟩
  rw [hp]
  exact e.root_reciprocal_rpow_summable_iff hN s

/-- The convergence exponent of the full reduced zero multiset is exactly 1/N. -/
theorem entireReducedDenominator_zero_power_summable_iff {N : ℕ} (hN : 2 ≤ N) (s : ℝ) :
    ZeroPowerSummable (entireReducedDenominator N) s ↔ 1 / (N : ℝ) < s := by
  let e := canonicalZeroEnumeration hN
  have hn : 0 < N := by omega
  unfold ZeroPowerSummable
  rw [summable_iff_comp_of_finite_complement (e.reducedZero hn) (e.reducedZero_injective hn)
    (e.reducedZero_finite_complement hn)]
  have he : ((fun z : {z : ℂ // entireReducedDenominator N z = 0} =>
      (analyticOrderNatAt (entireReducedDenominator N) z : ℝ) / ‖(z : ℂ)‖ ^ s) ∘ e.reducedZero hn) =
      (fun m => 1 / ‖e.reducedRoot m‖ ^ s) := by
    funext m
    simp only [Function.comp_apply, SignedZeroEnumeration.reducedZero,
      (e.reducedRoot_zero_simple hn m).2, Nat.cast_one]
  rw [he, e.reducedRoot_reciprocal_rpow_summable_iff hN]
  rw [div_lt_iff₀ (by exact_mod_cast hn : (0 : ℝ) < N), mul_comm s]

theorem entireReducedDenominator_reciprocal_zeros_summable {N : ℕ} (hN : 2 ≤ N) :
    ZeroPowerSummable (entireReducedDenominator N) 1 := by
  apply (entireReducedDenominator_zero_power_summable_iff hN 1).mpr
  rw [div_lt_one (by exact_mod_cast (show 0 < N by omega) : (0 : ℝ) < N)]
  exact_mod_cast (show 1 < N by omega)

end
end Komorebi.PaperIV
