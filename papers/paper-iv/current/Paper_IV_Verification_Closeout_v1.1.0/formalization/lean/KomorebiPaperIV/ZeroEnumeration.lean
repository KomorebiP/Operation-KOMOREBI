/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.WeightedZeroCounts

namespace Komorebi.PaperIV
noncomputable section
open Metric

/-- A positive simple tail, proved below to exist, with all large complex zeros
accounted for by its finite root-of-unity orbits. -/
structure SignedZeroEnumeration (N : ℕ) where
  root : ℕ → ℝ
  positive : ∀ m, 0 < root m
  zero : ∀ m, canonicalSignedDenominator N (root m : ℂ) = 0
  simple : ∀ m, analyticOrderAt (canonicalSignedDenominator N) (root m : ℂ) = 1
  injective : Function.Injective root
  shift : ℕ
  windows : ∀ m, (Real.pi / Real.sin (Real.pi / N)) * m ≤ root m ∧
    root m ≤ (Real.pi / Real.sin (Real.pi / N)) * ((m : ℝ) + shift)
  offset : ℕ
  displacement : ∃ C : ℝ, 0 < C ∧ ∃ γ : ℝ, 0 < γ ∧ ∀ m,
    |root m - signedZeroCenter N (m + offset)| ≤ C * Real.exp (-γ * signedZeroCenter N (m + offset))
  radius : ℝ
  radius_pos : 0 < radius
  exhaustive : ∀ z : ℂ, radius ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
    ∃ k : Fin N, ∃ m : ℕ, z = canonicalPrimitiveRoot N ^ k.val * (root m : ℂ)

theorem signedZeroEnumeration_exists_ge_three {N : ℕ} (hN : 3 ≤ N) :
    Nonempty (SignedZeroEnumeration N) := by
  let : NeZero N := ⟨by omega⟩
  have hn : 0 < N := by omega
  have homega := canonicalPrimitiveRoot_isPrimitive hn
  obtain ⟨C, hC, M, hM⟩ := signedPositiveZero_local_strings hN
  obtain ⟨R, hR, hex⟩ := canonicalSignedDenominator_large_zero_orbits hN M
  refine ⟨{ root := fun m => signedPositiveZero N (m + M)
            positive := fun m => (hM (m + M) (by omega)).1.1
            zero := fun m => (hM (m + M) (by omega)).1.2.1
            simple := fun m => (hM (m + M) (by omega)).2.1
            injective := ?_
            shift := M + 1
            windows := ?_
            offset := M
            displacement := ⟨C, hC, signedPolygonGap N, signedPolygonGap_pos hN,
              fun m => (hM (m + M) (by omega)).2.2.1⟩
            radius := R
            radius_pos := hR
            exhaustive := ?_ }⟩
  · intro m n h
    change signedPositiveZero N (m + M) = signedPositiveZero N (n + M) at h
    have he : m + M = n + M := by
      apply signedZeroCenter_disk_index_unique (by omega : 2 ≤ N) (hM (m + M) (by omega)).1.2.2
      rw [h]
      exact (hM (n + M) (by omega)).1.2.2
    omega
  · intro m
    have hb := (hM (m + M) (by omega)).1.2.2
    have he : |signedPositiveZero N (m + M) - signedZeroCenter N (m + M)| ≤
        1 / ‖signedZeroFrequency N‖ := by
      simpa only [mem_closedBall, dist_eq_norm, ← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs] using hb
    have hr := signedZeroCenter_ge_radius (by omega : 2 ≤ N) 0
    have hA : 0 < Real.pi / Real.sin (Real.pi / N) := div_pos Real.pi_pos (signed_sine_pos (by omega))
    have hM0 : (0 : ℝ) ≤ M := Nat.cast_nonneg M
    rw [abs_le] at he
    simp only [signedZeroCenter, Nat.cast_zero, zero_add] at hr
    simp only [signedZeroCenter, Nat.cast_add, Nat.cast_one] at he ⊢
    constructor <;> nlinarith
  · intro z hz hz0
    obtain ⟨k, _, m, hm, hb, _, _, _⟩ := hex z hz hz0
    have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
      rw [← pow_mul, Nat.mul_comm, pow_mul, homega.pow_eq_one, one_pow]
    have he := (hM m hm).2.2.2 (canonicalPrimitiveRoot N ^ k * z)
      ⟨hb, by rw [canonicalSignedDenominator_rotation hn hu]; exact hz0⟩
    have hui : ((canonicalPrimitiveRoot N ^ k)⁻¹) ^ N = 1 := by rw [inv_pow, hu, inv_one]
    obtain ⟨j, hj, hjinv⟩ := homega.eq_pow_of_pow_eq_one hui
    have hu0 : canonicalPrimitiveRoot N ^ k ≠ 0 := by intro h; simp [h, hn.ne'] at hu
    refine ⟨⟨j, hj⟩, m - M, ?_⟩
    rw [Nat.sub_add_cancel hm, ← he, hjinv, ← mul_assoc, inv_mul_cancel₀ hu0, one_mul]

theorem signedZeroEnumeration_exists_two : Nonempty (SignedZeroEnumeration 2) := by
  have homega := canonicalPrimitiveRoot_isPrimitive (by norm_num : 0 < 2)
  have hrho := canonicalSignedRoot_pow (by norm_num : 0 < 2)
  have hz : ∀ m : ℕ, canonicalSignedDenominator 2 ((Real.pi * ((m : ℝ) + 1 / 2) : ℝ) : ℂ) = 0 := by
    intro m
    apply (entireSigned_two_zero_iff_nat homega hrho).mpr
    refine ⟨m, Or.inl ?_⟩
    push_cast
    ring
  refine ⟨{ root := fun m => Real.pi * ((m : ℝ) + 1 / 2)
            positive := fun m => by positivity
            zero := hz
            simple := fun m => entireSigned_two_zero_order_one homega hrho (hz m)
            injective := ?_
            shift := 1
            windows := ?_
            offset := 0
            displacement := ⟨1, by norm_num, 1, by norm_num, fun m => by
              simp only [Nat.add_zero, signedZeroCenter, Nat.cast_ofNat, Real.sin_pi_div_two,
                div_one, sub_self, abs_zero, neg_mul, one_mul]
              exact (Real.exp_pos _).le⟩
            radius := 1
            radius_pos := by norm_num
            exhaustive := ?_ }⟩
  · intro m n h
    have he := mul_left_cancel₀ Real.pi_ne_zero h
    exact_mod_cast (add_right_cancel he)
  · intro m
    simp only [Nat.cast_ofNat, Real.sin_pi_div_two, div_one, Nat.cast_one]
    constructor <;> nlinarith [Real.pi_pos]
  · intro z _ hz0
    obtain ⟨m, hm | hm⟩ := (entireSigned_two_zero_iff_nat homega hrho).mp hz0
    · refine ⟨⟨0, by omega⟩, m, ?_⟩
      simp only [pow_zero, one_mul]
      rw [hm]; push_cast; ring
    · refine ⟨⟨1, by omega⟩, m, ?_⟩
      simp only [pow_one, homega.eq_neg_one_of_two_right]
      rw [hm]; push_cast; ring

/-- No enumeration or zero-counting certificate is assumed. -/
theorem signedZeroEnumeration_exists {N : ℕ} (hN : 2 ≤ N) :
    Nonempty (SignedZeroEnumeration N) := by
  rcases eq_or_lt_of_le hN with h | h
  · subst N; exact signedZeroEnumeration_exists_two
  · exact signedZeroEnumeration_exists_ge_three (by omega)

def canonicalZeroEnumeration {N : ℕ} (hN : 2 ≤ N) : SignedZeroEnumeration N :=
  Classical.choice (signedZeroEnumeration_exists hN)

def SignedZeroEnumeration.orbit {N : ℕ} (e : SignedZeroEnumeration N) (p : Fin N × ℕ) : ℂ :=
  canonicalPrimitiveRoot N ^ p.1.val * (e.root p.2 : ℂ)

theorem SignedZeroEnumeration.orbit_norm {N : ℕ} (hN : 0 < N) (e : SignedZeroEnumeration N)
    (p : Fin N × ℕ) : ‖e.orbit p‖ = e.root p.2 := by
  rw [SignedZeroEnumeration.orbit, norm_mul, norm_pow,
    (canonicalPrimitiveRoot_isPrimitive hN).norm'_eq_one hN.ne', one_pow, one_mul,
    Complex.norm_real, Real.norm_eq_abs, abs_of_pos (e.positive _)]

theorem SignedZeroEnumeration.orbit_injective {N : ℕ} (hN : 0 < N) (e : SignedZeroEnumeration N) :
    Function.Injective e.orbit := by
  intro p q hpq
  have hm : p.2 = q.2 := e.injective (by
    have hh := congrArg norm hpq
    rwa [e.orbit_norm hN, e.orbit_norm hN] at hh)
  have hp : p.1 = q.1 := by
    apply Fin.ext
    apply (canonicalPrimitiveRoot_isPrimitive hN).pow_inj p.1.isLt q.1.isLt
    unfold SignedZeroEnumeration.orbit at hpq
    rw [hm] at hpq
    exact mul_right_cancel₀ (Complex.ofReal_ne_zero.mpr (ne_of_gt (e.positive _))) hpq
  exact Prod.ext hp hm

theorem SignedZeroEnumeration.orbit_zero_simple {N : ℕ} (hN : 0 < N)
    (e : SignedZeroEnumeration N) (p : Fin N × ℕ) :
    canonicalSignedDenominator N (e.orbit p) = 0 ∧
      analyticOrderNatAt (canonicalSignedDenominator N) (e.orbit p) = 1 := by
  have hu : (canonicalPrimitiveRoot N ^ p.1.val) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive hN).pow_eq_one, one_pow]
  constructor
  · rw [SignedZeroEnumeration.orbit, canonicalSignedDenominator_rotation hN hu]; exact e.zero _
  · rw [analyticOrderNatAt, SignedZeroEnumeration.orbit,
      ← canonicalSignedDenominator_order_rotation hN hu, e.simple]
    rfl

end
end Komorebi.PaperIV
