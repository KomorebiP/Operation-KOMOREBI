/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.QuarticExactZeros

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- Construction used only after all zeros and their simplicity have been proved. -/
def exactLatticeEnumeration {N : ℕ} (hN : 2 ≤ N)
    (hz : ∀ m, canonicalSignedDenominator N (signedZeroCenter N m : ℂ) = 0)
    (hs : ∀ m, analyticOrderAt (canonicalSignedDenominator N) (signedZeroCenter N m : ℂ) = 1)
    (he : ∀ z, canonicalSignedDenominator N z = 0 → ∃ k : Fin N, ∃ m,
      z = canonicalPrimitiveRoot N ^ k.val * (signedZeroCenter N m : ℂ)) : SignedZeroEnumeration N where
  root := signedZeroCenter N
  positive := signedZeroCenter_positive hN
  zero := hz
  simple := hs
  injective := by
    intro m n h
    have hA := ne_of_gt (div_pos Real.pi_pos (signed_sine_pos hN))
    exact_mod_cast add_right_cancel (mul_left_cancel₀ hA h)
  shift := 1
  windows := by
    intro m
    have hA := div_pos Real.pi_pos (signed_sine_pos hN)
    unfold signedZeroCenter
    norm_num only [Nat.cast_one]
    constructor <;> nlinarith
  offset := 0
  displacement := ⟨1, by norm_num, 1, by norm_num, fun m => by
    simp only [Nat.add_zero, sub_self, abs_zero, one_mul]
    exact (Real.exp_pos _).le⟩
  radius := 1
  radius_pos := by norm_num
  exhaustive := fun z _ hz0 => he z hz0

theorem SignedZeroEnumeration.reducedZero_surjective_of_orbitZero {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) (he : Function.Surjective (e.orbitZero hn)) :
    Function.Surjective (e.reducedZero hn) := by
  intro w
  obtain ⟨z, hz⟩ := exists_complex_nth_root hn (w : ℂ)
  have hd : canonicalSignedDenominator N z = 0 := by
    rw [canonicalSignedDenominator_eq_reduced_power hn, hz]
    exact w.property
  obtain ⟨p, hp⟩ := he ⟨z, hd⟩
  refine ⟨p.2, Subtype.ext ?_⟩
  have heq : e.orbit p = z := congrArg Subtype.val hp
  have hu : (canonicalPrimitiveRoot N ^ p.1.val) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive hn).pow_eq_one, one_pow]
  rw [← hz, ← heq, SignedZeroEnumeration.orbit, mul_pow, hu, one_mul]
  rfl

theorem SignedZeroEnumeration.exceptions_zero_of_surjective {N : ℕ} (hn : 0 < N)
    (e : SignedZeroEnumeration N) (he : Function.Surjective (e.orbitZero hn)) (s : ℂ) :
    e.absoluteExceptionZeta hn s = 0 ∧ e.reducedExceptionZeta hn s = 0 := by
  have hr := e.reducedZero_surjective_of_orbitZero hn he
  have : IsEmpty ↥((range (e.orbitZero hn))ᶜ) := ⟨fun z => z.property (he z.val)⟩
  have : IsEmpty ↥((range (e.reducedZero hn))ᶜ) := ⟨fun z => z.property (hr z.val)⟩
  simp [SignedZeroEnumeration.absoluteExceptionZeta, SignedZeroEnumeration.reducedExceptionZeta]

/-- Both exact models follow from a fully proved, simple, exhaustive lattice. -/
theorem zero_zeta_exact_of_lattice {N : ℕ} (hN : 2 ≤ N)
    (hz : ∀ m, canonicalSignedDenominator N (signedZeroCenter N m : ℂ) = 0)
    (hsimple : ∀ m, analyticOrderAt (canonicalSignedDenominator N) (signedZeroCenter N m : ℂ) = 1)
    (hex : ∀ z, canonicalSignedDenominator N z = 0 → ∃ k : Fin N, ∃ m,
      z = canonicalPrimitiveRoot N ^ k.val * (signedZeroCenter N m : ℂ)) :
    (∀ s : ℂ, 1 < s.re → absoluteZeroZeta (canonicalSignedDenominator N) s =
      (N : ℂ) * hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) 1 s) ∧
    (∀ s : ℂ, 1 / (N : ℝ) < s.re → absoluteZeroZeta (entireReducedDenominator N) s =
      hurwitzLatticeModel (Real.pi / Real.sin (Real.pi / N)) N s) := by
  let e := exactLatticeEnumeration hN hz hsimple hex
  have he : Function.Surjective (e.orbitZero (by omega)) := by
    intro z
    obtain ⟨k, m, hm⟩ := hex z z.property
    exact ⟨(k, m), Subtype.ext hm.symm⟩
  have hc : ∀ s, e.latticeCorrection s = 0 := by
    intro s
    simp only [SignedZeroEnumeration.latticeCorrection, exponentialZetaDifference, e,
      exactLatticeEnumeration, Nat.add_zero, sub_self, tsum_zero]
  have hp : ∀ s, e.latticePrefix s = 0 := by
    intro s
    simp only [SignedZeroEnumeration.latticePrefix, e, exactLatticeEnumeration, Finset.range_zero, Finset.sum_empty]
  constructor
  · intro s hs
    rw [e.absoluteZeta_decomposition hN hs, e.root_zeta_eq_model hN hs, hc, hp,
      (e.exceptions_zero_of_surjective (by omega) he s).1, add_zero, sub_zero, add_zero]
  · intro s hs
    have hsN : 1 < ((N : ℂ) * s).re := by
      simp only [Complex.mul_re, Complex.natCast_re, Complex.natCast_im, zero_mul, sub_zero]
      have hn : (0 : ℝ) < N := by exact_mod_cast (show 0 < N by omega)
      exact (div_lt_iff₀ hn).mp hs |>.trans_eq (mul_comm _ _)
    rw [e.reducedZeta_decomposition hN hs, e.root_zeta_eq_model hN hsN, hc, hp,
      (e.exceptions_zero_of_surjective (by omega) he s).2, add_zero, sub_zero, add_zero]
    simp only [hurwitzLatticeModel, Nat.cast_one, one_mul]

theorem signedZeroCenter_four (m : ℕ) : signedZeroCenter 4 m = quarticPositiveZero m := by
  have hq : (Real.sqrt 2) ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  have hq0 : Real.sqrt 2 ≠ 0 := by positivity
  unfold signedZeroCenter quarticPositiveZero
  simp only [Nat.cast_ofNat, Real.sin_pi_div_four]
  field_simp
  nlinarith

theorem orderTwo_full_lattice :
    (∀ m, canonicalSignedDenominator 2 (signedZeroCenter 2 m : ℂ) = 0) ∧
    (∀ m, analyticOrderAt (canonicalSignedDenominator 2) (signedZeroCenter 2 m : ℂ) = 1) ∧
    (∀ z, canonicalSignedDenominator 2 z = 0 → ∃ k : Fin 2, ∃ m,
      z = canonicalPrimitiveRoot 2 ^ k.val * (signedZeroCenter 2 m : ℂ)) := by
  have homega := canonicalPrimitiveRoot_isPrimitive (by norm_num : 0 < 2)
  have hrho := canonicalSignedRoot_pow (by norm_num : 0 < 2)
  have hc : ∀ m, (signedZeroCenter 2 m : ℂ) = ((m : ℂ) + 1 / 2) * (Real.pi : ℂ) := by
    intro m
    simp only [signedZeroCenter, Nat.cast_ofNat, Real.sin_pi_div_two, div_one]
    push_cast
    ring
  have hz : ∀ m, canonicalSignedDenominator 2 (signedZeroCenter 2 m : ℂ) = 0 := by
    intro m
    exact (entireSigned_two_zero_iff_nat homega hrho).mpr ⟨m, Or.inl (hc m)⟩
  refine ⟨hz, fun m => entireSigned_two_zero_order_one homega hrho (hz m), ?_⟩
  intro z hz0
  obtain ⟨m, hm | hm⟩ := (entireSigned_two_zero_iff_nat homega hrho).mp hz0
  · exact ⟨⟨0, by norm_num⟩, m, by simpa only [pow_zero, one_mul, hc m] using hm⟩
  · exact ⟨⟨1, by norm_num⟩, m, by simpa only [pow_one, homega.eq_neg_one_of_two_right, neg_one_mul, hc m] using hm⟩

theorem orderFour_full_lattice :
    (∀ m, canonicalSignedDenominator 4 (signedZeroCenter 4 m : ℂ) = 0) ∧
    (∀ m, analyticOrderAt (canonicalSignedDenominator 4) (signedZeroCenter 4 m : ℂ) = 1) ∧
    (∀ z, canonicalSignedDenominator 4 z = 0 → ∃ k : Fin 4, ∃ m,
      z = canonicalPrimitiveRoot 4 ^ k.val * (signedZeroCenter 4 m : ℂ)) := by
  refine ⟨fun m => ?_, fun m => ?_, ?_⟩
  · rw [signedZeroCenter_four]
    exact canonicalSignedDenominator_four_zero_iff.mpr ⟨m, Or.inl rfl⟩
  · rw [signedZeroCenter_four]
    exact quarticPositiveZero_simple m
  · intro z hz
    have homega := canonicalPrimitiveRoot_isPrimitive (by norm_num : 0 < 4)
    have hu : ∀ u : ℂ, u ^ 4 = 1 → ∀ m, ∃ k : Fin 4, ∃ j,
        u * (quarticPositiveZero m : ℂ) = canonicalPrimitiveRoot 4 ^ k.val * (signedZeroCenter 4 j : ℂ) := by
      intro u hu m
      obtain ⟨k, hk, he⟩ := homega.eq_pow_of_pow_eq_one hu
      exact ⟨⟨k, hk⟩, m, by rw [signedZeroCenter_four, he]⟩
    obtain ⟨m, hm | hm | hm | hm⟩ := canonicalSignedDenominator_four_zero_iff.mp hz
    · rw [hm]
      simpa only [one_mul] using hu 1 (by norm_num) m
    · rw [hm]
      simpa only [neg_one_mul] using hu (-1) (by norm_num) m
    · rw [hm]
      exact hu Complex.I Complex.isPrimitiveRoot_I.pow_eq_one m
    · rw [hm]
      simpa only [neg_mul] using hu (-Complex.I) Complex.isPrimitiveRoot_neg_I.pow_eq_one m

/-- Corollary 14.4, with no omitted zeros in either order. -/
theorem orderTwo_exact_zero_zeta_models :
    (∀ s : ℂ, 1 < s.re → absoluteZeroZeta (canonicalSignedDenominator 2) s =
      2 * hurwitzLatticeModel Real.pi 1 s) ∧
    (∀ s : ℂ, 1 / 2 < s.re → absoluteZeroZeta (entireReducedDenominator 2) s =
      hurwitzLatticeModel Real.pi 2 s) := by
  simpa only [Nat.cast_ofNat, Real.sin_pi_div_two, div_one] using
    zero_zeta_exact_of_lattice (by norm_num) orderTwo_full_lattice.1 orderTwo_full_lattice.2.1 orderTwo_full_lattice.2.2

theorem orderFour_exact_zero_zeta_models :
    (∀ s : ℂ, 1 < s.re → absoluteZeroZeta (canonicalSignedDenominator 4) s =
      4 * hurwitzLatticeModel (Real.sqrt 2 * Real.pi) 1 s) ∧
    (∀ s : ℂ, 1 / 4 < s.re → absoluteZeroZeta (entireReducedDenominator 4) s =
      hurwitzLatticeModel (Real.sqrt 2 * Real.pi) 4 s) := by
  have hA : Real.pi / Real.sin (Real.pi / 4) = Real.sqrt 2 * Real.pi := by
    have h := signedZeroCenter_four 0
    simp only [signedZeroCenter, quarticPositiveZero, Nat.cast_zero, zero_add, Nat.cast_ofNat] at h
    linarith
  simpa only [Nat.cast_ofNat, hA] using
    zero_zeta_exact_of_lattice (by norm_num) orderFour_full_lattice.1 orderFour_full_lattice.2.1 orderFour_full_lattice.2.2

theorem entire_zero_of_halfplane {f : ℂ → ℂ} (hf : Differentiable ℂ f) (c : ℝ)
    (hz : ∀ s : ℂ, c < s.re → f s = 0) : f = 0 := by
  have he : f =ᶠ[𝓝 ((c + 1 : ℝ) : ℂ)] 0 := by
    have ho : IsOpen {s : ℂ | c < s.re} := isOpen_lt continuous_const Complex.continuous_re
    filter_upwards [ho.mem_nhds (show ((c + 1 : ℝ) : ℂ) ∈ {s : ℂ | c < s.re} by
      simp only [mem_ofPred_eq, Complex.ofReal_re]; linarith)] with s hs
    exact hz s hs
  exact (show AnalyticOnNhd ℂ f univ from fun s _ => hf.analyticAt s).eq_of_eventuallyEq
    (show AnalyticOnNhd ℂ (0 : ℂ → ℂ) univ from fun _ _ => analyticAt_const) he

/-- The corrections chosen in Theorem 14.3 themselves vanish in the exact cases. -/
theorem zero_zeta_corrections_of_lattice {N : ℕ} (hN : 2 ≤ N)
    (hz : ∀ m, canonicalSignedDenominator N (signedZeroCenter N m : ℂ) = 0)
    (hsimple : ∀ m, analyticOrderAt (canonicalSignedDenominator N) (signedZeroCenter N m : ℂ) = 1)
    (hex : ∀ z, canonicalSignedDenominator N z = 0 → ∃ k : Fin N, ∃ m,
      z = canonicalPrimitiveRoot N ^ k.val * (signedZeroCenter N m : ℂ)) :
    absoluteZetaCorrection hN = 0 ∧ reducedZetaCorrection hN = 0 := by
  have he := zero_zeta_exact_of_lattice hN hz hsimple hex
  constructor
  · apply entire_zero_of_halfplane (absoluteZetaCorrection_entire hN) 1
    intro s hs
    have h := canonicalSignedDenominator_zeta_eq_hurwitz hN hs
    rw [he.1 s hs] at h
    linear_combination -h
  · apply entire_zero_of_halfplane (reducedZetaCorrection_entire hN) (1 / (N : ℝ))
    intro s hs
    have h := entireReducedDenominator_zeta_eq_hurwitz hN hs
    rw [he.2 s hs] at h
    linear_combination -h

theorem orderTwo_zeta_corrections_zero :
    absoluteZetaCorrection (by norm_num : 2 ≤ 2) = 0 ∧
    reducedZetaCorrection (by norm_num : 2 ≤ 2) = 0 :=
  zero_zeta_corrections_of_lattice (by norm_num) orderTwo_full_lattice.1
    orderTwo_full_lattice.2.1 orderTwo_full_lattice.2.2

theorem orderFour_zeta_corrections_zero :
    absoluteZetaCorrection (by norm_num : 2 ≤ 4) = 0 ∧
    reducedZetaCorrection (by norm_num : 2 ≤ 4) = 0 :=
  zero_zeta_corrections_of_lattice (by norm_num) orderFour_full_lattice.1
    orderFour_full_lattice.2.1 orderFour_full_lattice.2.2

end
end Komorebi.PaperIV
