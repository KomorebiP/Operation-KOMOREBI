module

public import ZigzagCoefficients
public import FilteredReconstruction

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.OddEuler

open PowerSeries OddPower EulerCoefficients

/-- Rescaling the already constructed reciprocal preserves its inverse law. -/
theorem scaled_sech_cosh (a : ℚ) : rescale a sech * coshAt a = 1 := by
  have h := congrArg (rescale a) sech_mul_cosh
  simpa only [map_mul, rescale_cosh, mul_one, map_one] using h

/-- The actual inverse-series identity underlying the odd-prime coordinate transform. -/
theorem odd_reconstruction_series (p : ℕ) (hp : Odd p) :
    rescale (p:ℚ) (sech^2) * evenPart (sourceSeries p) = sech := by
  rw [odd_source_even_egf p hp, map_pow]
  calc
    _ = (rescale (p:ℚ) sech * coshAt p)^2 * sech := by ring
    _ = _ := by rw [scaled_sech_cosh, one_pow, one_mul]

theorem decode_rescale (a : ℚ) (f : PowerSeries ℚ) (n : ℕ) :
    EGF.decode (rescale a f) n = a^n * EGF.decode f n := by
  simp [EGF.decode, mul_assoc]

theorem decode_even_source (p n : ℕ) :
    EGF.decode (evenPart (sourceSeries p)) n = if Even n then (source p n : ℚ) else 0 := by
  unfold EGF.decode
  rw [evenPart_coeff]
  by_cases hn : Even n
  · rw [ite_eq_left hn, ite_eq_left hn]
    simp [sourceSeries, Nat.factorial_ne_zero]
  · rw [ite_eq_right hn, ite_eq_right hn, zero_mul]

/-- A parity-separated sum, with the odd summands proved zero. -/
theorem sum_even_terms {R : Type*} [AddCommMonoid R] (f : ℕ → R)
    (hf : ∀ m, f (2*m+1) = 0) (n : ℕ) :
    (∑ r ∈ Finset.range (2*n+1), f r) = ∑ m ∈ Finset.range (n+1), f (2*m) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [show 2*(n+1)+1 = (2*n+1)+1+1 by omega, Finset.sum_range_succ,
      Finset.sum_range_succ, hf n, add_zero, ih]
    conv_rhs => rw [Finset.sum_range_succ]
    rw [show 2*n+1+1=2*(n+1) by omega]

/-- Coefficient extraction before the even-index change of variables. -/
theorem reconstruction_all_indices (p n : ℕ) (hp : Odd p) (hn : Even n) :
    euler n = ∑ r ∈ Finset.range (n+1),
      (n.choose r : ℤ) * inverseCoeff r * (p:ℤ)^r * source p (n-r) := by
  have hs := congrArg (fun f => EGF.decode f n) (odd_reconstruction_series p hp)
  have hprod := EGF.egf_product (EGF.decode (rescale (p:ℚ) (sech^2)))
      (EGF.decode (evenPart (sourceSeries p))) n
  simp only [EGF.encode_decode] at hprod
  have heuler : EGF.decode sech n = (euler n : ℚ) := by
    rw [← euler_egf, EGF.decode_encode]
  rw [hprod, heuler] at hs
  apply Int.cast_injective (α := ℚ)
  simp only [Int.cast_sum, Int.cast_mul, Int.cast_natCast, Int.cast_pow]
  rw [← hs]
  apply Finset.sum_congr rfl
  intro r hr
  rw [decode_rescale, ← inverse_coeff_cast, decode_even_source]
  by_cases he : Even r
  · have hnr : Even (n-r) := by
      rw [Nat.even_iff] at hn he ⊢
      have hle := Finset.mem_range_succ_iff.mp hr
      omega
    rw [ite_eq_left hnr]
    ring
  · rw [inverse_odd_zero r (Nat.not_even_iff_odd.mp he)]
    simp

/-- Theorem 4.2 in integral coordinates, valid for every odd length p, not just primes. -/
theorem odd_euler_reconstruction (p n : ℕ) (hp : Odd p) :
    eulerEven n = ∑ m ∈ Finset.range (n+1),
      ((2*n).choose (2*m) : ℤ) * inverseEven m * (p:ℤ)^(2*m) * source p (2*(n-m)) := by
  have h := reconstruction_all_indices p (2*n) hp (even_two_mul n)
  rw [euler_even] at h
  rw [sum_even_terms (fun r => ((2*n).choose r : ℤ)*inverseCoeff r*(p:ℤ)^r*source p (2*n-r))
    (fun m => by rw [inverse_odd_zero _ (by exact ⟨m,rfl⟩)]; simp)] at h
  simpa only [inverseEven, Nat.mul_sub_left_distrib] using h

/-- The manuscript's signed zigzag formulation, with the sign identity proved independently. -/
theorem odd_euler_reconstruction_zigzag (p n : ℕ) (hp : Odd p) :
    (eulerEven n : ℚ) = ∑ m ∈ Finset.range (n+1),
      (-1:ℚ)^m * Zigzag.zigzag (2*m+1) * ((2*n).choose (2*m) : ℚ) *
        (p:ℚ)^(2*m) * (source p (2*(n-m)) : ℚ) := by
  rw [odd_euler_reconstruction p n hp]
  push_cast
  apply Finset.sum_congr rfl
  intro m _
  rw [Zigzag.inverse_is_signed_zigzag]
  ring

/-- Literal row coefficients acting on even source indices. -/
def rowEntry (p n q : ℕ) : ℤ :=
  if q ≤ n then ((2*n).choose (2*q):ℤ) * inverseEven (n-q) * (p:ℤ)^(2*(n-q)) else 0

/-- The displayed lower-triangular row acts on the original even source coordinates. -/
theorem row_action (p n : ℕ) (hp : Odd p) :
    eulerEven n = ∑ q ∈ Finset.range (n+1), rowEntry p n q * source p (2*q) := by
  rw [odd_euler_reconstruction p n hp]
  rw [← Finset.sum_range_reflect
    (fun m => ((2*n).choose (2*m):ℤ)*inverseEven m*(p:ℤ)^(2*m)*source p (2*(n-m))) (n+1)]
  simp only [Nat.add_sub_cancel]
  apply Finset.sum_congr rfl
  intro q hq
  have hqn := Finset.mem_range_succ_iff.mp hq
  have hmul : 2*q ≤ 2*n := Nat.mul_le_mul_left 2 hqn
  have hchoose : (2*n).choose (2*(n-q)) = (2*n).choose (2*q) := by
    rw [Nat.mul_sub_left_distrib, Nat.choose_symm hmul]
  rw [rowEntry, ite_eq_left hqn, Nat.sub_sub_self hqn, hchoose]

@[simp] theorem row_diagonal (p n : ℕ) : rowEntry p n n = 1 := by
  simp [rowEntry, inverseEven]

theorem row_above_diagonal (p n q : ℕ) (h : n < q) : rowEntry p n q = 0 := by
  simp [rowEntry, Nat.not_le.mpr h]

theorem row_weight (p n q : ℕ) : (p:ℤ)^(2*(n-q)) ∣ rowEntry p n q := by
  unfold rowEntry
  split_ifs
  · exact dvd_mul_left _ _
  · exact dvd_zero _

/-- Truncation includes the smaller of the prescribed depth and the actual row length. -/
def truncation (p n M : ℕ) : ℤ :=
  ∑ m ∈ Finset.range (min M n+1),
    ((2*n).choose (2*m):ℤ) * inverseEven m * (p:ℤ)^(2*m) * source p (2*(n-m))

theorem filter_range_le (n M : ℕ) :
    (Finset.range (n+1)).filter (fun m => m ≤ M) = Finset.range (min M n+1) := by
  ext m
  simp only [Finset.mem_filter, Finset.mem_range]
  omega

/-- The uniform congruence is divisibility in Z, not divisibility in the field Q. -/
theorem odd_euler_supercongruence (p n M : ℕ) (hp : Odd p) :
    (p:ℤ)^(2*M+2) ∣ eulerEven n - truncation p n M := by
  rw [odd_euler_reconstruction p n hp]
  have h := Filtered.even_weight_tail (p:ℤ)
    (fun m => ((2*n).choose (2*m):ℤ)*inverseEven m*source p (2*(n-m))) n M
  rw [filter_range_le] at h
  simpa only [truncation, mul_assoc, mul_left_comm, mul_comm] using h

/-- The paper's odd-prime corollary is a specialization of the stronger odd-length identity. -/
theorem odd_prime_supercongruence (p n M : ℕ) (hp : p.Prime) (hodd : p ≠ 2) :
    (p:ℤ)^(2*M+2) ∣ eulerEven n - truncation p n M :=
  odd_euler_supercongruence p n M (hp.odd_of_ne_two hodd)

theorem full_depth_exact (p n M : ℕ) (hp : Odd p) (hn : n ≤ M) :
    truncation p n M = eulerEven n := by
  rw [truncation, min_eq_right hn, odd_euler_reconstruction p n hp]

end KomorebiPaperIX.OddEuler
