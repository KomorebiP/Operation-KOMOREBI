import PaperX.IntegralCharts
import PaperX.Singular

/-! Digit expansions with a declared uniformizer and a chosen section of the
residue map. The section is not assumed to be a ring homomorphism. -/
set_option autoImplicit false
namespace PaperX.Digits
open IsLocalRing
open scoped BigOperators
variable {R : Type*} [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
variable {π : R} (hπ : Irreducible π)
variable (s : ResidueField R → R) (hs : Function.RightInverse s (residue R))

/-- An arbitrary residue section can always be chosen to send zero to zero. -/
theorem exists_normalized_section : ∃ s : ResidueField R → R,
    Function.RightInverse s (residue R) ∧ s 0 = 0 := by
  classical
  let s : ResidueField R → R := fun a => if a = 0 then 0 else
    Classical.choose (residue_surjective a)
  refine ⟨s, ?_, by simp [s]⟩
  intro a
  by_cases ha : a = 0
  · simp [s, ha]
  · simpa [s, ha] using Classical.choose_spec (residue_surjective a)

/-- The finite partial sum in the chosen digits. -/
noncomputable def partialSum (a : ℕ → ResidueField R) (n : ℕ) : R :=
  ∑ j ∈ Finset.range n, π^j * s (a j)

@[simp] theorem prefix_zero (a : ℕ → ResidueField R) : partialSum (π := π) s a 0 = 0 := by
  simp [partialSum]

theorem prefix_succ (a : ℕ → ResidueField R) (n : ℕ) :
    partialSum (π := π) s a (n+1) = partialSum (π := π) s a n + π^n*s (a n) := by
  exact Finset.sum_range_succ _ _

theorem prefix_congr (a b : ℕ → ResidueField R) (n : ℕ)
    (h : ∀ j < n, a j = b j) : partialSum (π := π) s a n = partialSum (π := π) s b n := by
  apply Finset.sum_congr rfl
  intro j hj
  rw [h j (Finset.mem_range.mp hj)]

/-- Each finite partial sum must agree with x through its stated precision. -/
def Encodes (a : ℕ → ResidueField R) (x : R) : Prop :=
  ∀ n, π^n ∣ x - partialSum (π := π) s a n

include hπ hs in
/-- Removing the selected first digit leaves an exactly divisible remainder. -/
theorem remainder_divisible (x : R) : π ∣ x - s (residue R x) := by
  rw [← Ideal.mem_span_singleton, ← hπ.maximalIdeal_eq, ← residue_eq_zero_iff]
  simp [hs (residue R x)]

noncomputable def tail (x : R) : R := Classical.choose (remainder_divisible hπ s hs x)

theorem tail_spec (x : R) : x = s (residue R x) + π * tail hπ s hs x := by
  have h := Classical.choose_spec (remainder_divisible hπ s hs x)
  change x - s (residue R x) = π * tail hπ s hs x at h
  linear_combination h

noncomputable def rest (x : R) : ℕ → R
  | 0 => x
  | n+1 => tail hπ s hs (rest x n)

noncomputable def digits (x : R) (n : ℕ) : ResidueField R := residue R (rest hπ s hs x n)

/-- Finite exact identity; no completeness assumption is needed to extract digits. -/
theorem remainder_identity (x : R) (n : ℕ) :
    x = partialSum (π := π) s (digits hπ s hs x) n + π^n * rest hπ s hs x n := by
  induction n with
  | zero => simp [rest]
  | succ n ih =>
    rw [prefix_succ, pow_succ]
    change x = partialSum s (digits hπ s hs x) n + π^n*s (residue R (rest hπ s hs x n)) +
      (π^n*π) * tail hπ s hs (rest hπ s hs x n)
    have h := tail_spec hπ s hs (rest hπ s hs x n)
    linear_combination ih + π^n * h

theorem digits_encode (x : R) : Encodes (π := π) s (digits hπ s hs x) x := by
  intro n
  refine ⟨rest hπ s hs x n, ?_⟩
  have h := remainder_identity hπ s hs x n
  linear_combination h

include hπ hs in
/-- Two streams representing the same element agree at every digit. -/
theorem encoding_unique (a b : ℕ → ResidueField R) (x : R)
    (ha : Encodes (π := π) s a x) (hb : Encodes (π := π) s b x) : a = b := by
  funext n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    have hpref := prefix_congr (π := π) s a b n ih
    have hdiff : π^(n+1) ∣ π^n * (s (a n) - s (b n)) := by
      have h := dvd_sub (hb (n+1)) (ha (n+1))
      convert h using 1
      rw [prefix_succ, prefix_succ, hpref]
      ring
    rw [pow_succ] at hdiff
    have hd := (mul_dvd_mul_iff_left (pow_ne_zero n hπ.ne_zero)).mp hdiff
    have hr : residue R (s (a n) - s (b n)) = 0 := by
      apply (residue_eq_zero_iff _).mpr
      rw [hπ.maximalIdeal_eq, Ideal.mem_span_singleton]
      exact hd
    simpa only [map_sub, hs _, sub_eq_zero] using hr

/-- Differences between successive partial sums have increasing precision. -/
theorem prefix_compatible (a : ℕ → ResidueField R) {m n : ℕ} (h : m ≤ n) :
    π^m ∣ partialSum (π := π) s a n - partialSum (π := π) s a m := by
  induction n, h using Nat.le_induction with
  | base => simp
  | succ n h ih =>
    rw [prefix_succ]
    have hd : π^m ∣ π^n * s (a n) := dvd_mul_of_dvd_left (pow_dvd_pow π h) _
    convert dvd_add ih hd using 1
    ring

variable [IsAdicComplete (maximalIdeal R) R]

include hπ in
/-- Every digit stream converges to a unique coefficient-ring element. -/
theorem stream_reconstructs (a : ℕ → ResidueField R) : ∃! x, Encodes (π := π) s a x := by
  have hc : ∀ {m n : ℕ}, m ≤ n →
      partialSum (π := π) s a m ≡ partialSum (π := π) s a n [SMOD maximalIdeal R ^ m • (⊤ : Submodule R R)] := by
    intro m n h
    rw [SModEq.sub_mem, Ideal.smul_eq_mul, Ideal.mul_top,
      hπ.maximalIdeal_eq, Ideal.span_singleton_pow, Ideal.mem_span_singleton]
    simpa only [neg_sub, dvd_neg] using dvd_neg.mpr (prefix_compatible s a h)
  obtain ⟨x, hx⟩ := IsPrecomplete.prec (inferInstance : IsPrecomplete (maximalIdeal R) R) hc
  have hex : Encodes (π := π) s a x := by
    intro n
    have h := hx n
    rw [SModEq.sub_mem, Ideal.smul_eq_mul, Ideal.mul_top,
      hπ.maximalIdeal_eq, Ideal.span_singleton_pow, Ideal.mem_span_singleton] at h
    simpa only [neg_sub, dvd_neg] using dvd_neg.mpr h
  refine ⟨x, hex, ?_⟩
  intro y hy
  apply (IsHausdorff.eq_iff_smodEq (I := maximalIdeal R)).mpr
  intro n
  rw [SModEq.sub_mem, Ideal.smul_eq_mul, Ideal.mul_top,
    hπ.maximalIdeal_eq, Ideal.span_singleton_pow, Ideal.mem_span_singleton]
  convert dvd_sub (hy n) (hex n) using 1
  ring

/-- Explicit coordinate change between the complete DVR and residue-digit streams. -/
noncomputable def digitEquiv : R ≃ (ℕ → ResidueField R) where
  toFun := digits hπ s hs
  invFun a := Classical.choose (stream_reconstructs hπ s a)
  left_inv x := by
    have h := Classical.choose_spec (stream_reconstructs hπ s (digits hπ s hs x))
    exact (h.2 x (digits_encode hπ s hs x)).symm
  right_inv a := by
    apply encoding_unique hπ s hs _ a
    · exact digits_encode hπ s hs _
    · exact (Classical.choose_spec (stream_reconstructs hπ s a)).1

omit [IsAdicComplete (maximalIdeal R) R] in
/-- Positive-depth values are precisely streams whose constant digit is zero. -/
theorem positive_depth_iff (x : R) :
    x ∈ maximalIdeal R ↔ digits hπ s hs x 0 = 0 := by
  exact (residue_eq_zero_iff x).symm


omit [IsAdicComplete (maximalIdeal R) R] in
include hπ in
/-- Membership in the maximal ideal supplies one uniformizer factor. -/
theorem maximal_divisible (x : R) (hx : x ∈ maximalIdeal R) : π ∣ x := by
  rw [hπ.maximalIdeal_eq, Ideal.mem_span_singleton] at hx
  exact hx

/-- Dividing a positive-depth value by the declared uniformizer is a bijection. -/
noncomputable def uniformizerEquiv : maximalIdeal R ≃ R where
  toFun x := Classical.choose (maximal_divisible hπ x.val x.property)
  invFun y := ⟨π*y, by rw [hπ.maximalIdeal_eq, Ideal.mem_span_singleton]; exact dvd_mul_right π y⟩
  left_inv x := by
    apply Subtype.ext
    exact (Classical.choose_spec (maximal_divisible hπ x.val x.property)).symm
  right_inv y := by
    apply mul_left_cancel₀ hπ.ne_zero
    exact (Classical.choose_spec (maximal_divisible hπ (π*y) (by
      rw [hπ.maximalIdeal_eq, Ideal.mem_span_singleton]
      exact dvd_mul_right π y))).symm

/-- Arbitrary streams, now indexed from the first positive digit. -/
noncomputable def positiveDigitEquiv : maximalIdeal R ≃ (ℕ → ResidueField R) :=
  (uniformizerEquiv hπ).trans (digitEquiv hπ s hs)

/-- The positive-depth expansion has an error divisible by π^(n+1). -/
theorem positive_encoding (x : maximalIdeal R) (n : ℕ) :
    π^(n+1) ∣ x.val - π*partialSum (π := π) s (positiveDigitEquiv hπ s hs x) n := by
  have hx : x.val = π * uniformizerEquiv hπ x :=
    Classical.choose_spec (maximal_divisible hπ x.val x.property)
  have he := digits_encode hπ s hs (uniformizerEquiv hπ x) n
  rw [hx, pow_succ']
  change π*π^n ∣ π * uniformizerEquiv hπ x - π*partialSum s (digits hπ s hs (uniformizerEquiv hπ x)) n
  rw [← mul_sub]
  exact mul_dvd_mul_left π he

/-- Complete smooth formal maps are exactly d independent positive digit streams. -/
noncomputable def integralPointDigitEquiv (d : ℕ) :
    PaperX.IntegralCharts.IntegralPoint (R := R) d ≃ (Fin d → ℕ → ResidueField R) :=
  (PaperX.IntegralCharts.integralPointEquiv d).trans
    (Equiv.piCongrRight fun _ => positiveDigitEquiv hπ s hs)

/-- The stream equivalence reconstructs each actual formal parameter with the
correct shifted precision. -/
theorem parameter_digit_expansion {d : ℕ}
    (f : PaperX.IntegralCharts.IntegralPoint (R := R) d) (i : Fin d) (n : ℕ) :
    π^(n+1) ∣ f.val (MvPowerSeries.X i) -
      π * partialSum (π := π) s (integralPointDigitEquiv hπ s hs d f i) n := by
  exact positive_encoding hπ s hs (PaperX.IntegralCharts.integralParameters f i) n

end PaperX.Digits

