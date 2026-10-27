module

public import Mathlib.Algebra.Group.ForwardDiff
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.Mahler

variable {R : Type*} [CommRing R]

/-- Actual iterated forward differences, with arbitrary natural step. -/
def difference (h s : ℕ) (f : ℕ → R) : ℕ → R := (fwdDiff h)^[s] f

/-- The Newton/Mahler coefficient is the actual difference at zero. -/
def coefficient (f : ℕ → R) (r : ℕ) : R := difference 1 r f 0

/-- The finite binomial interpolant with coefficients c_0,...,c_N. -/
def interpolant (N : ℕ) (c : ℕ → R) (n : ℕ) : R :=
  ∑ r ∈ Finset.range (N+1), c r * (n.choose r : R)

@[simp] theorem difference_zero (h : ℕ) (f : ℕ → R) : difference h 0 f = f := rfl

@[simp] theorem difference_one (h : ℕ) (f : ℕ → R) (n : ℕ) :
    difference h 1 f n = f (n+h)-f n := rfl

@[simp] theorem coefficient_zero (f : ℕ → R) : coefficient f 0 = f 0 := rfl

theorem difference_succ (h s : ℕ) (f : ℕ → R) (n : ℕ) :
    difference h (s+1) f n = difference h s f (n+h) - difference h s f n := by
  rw [difference, Function.iterate_succ_apply']
  rfl

theorem difference_add (h s : ℕ) (f g : ℕ → R) :
    difference h s (fun n => f n + g n) = fun n => difference h s f n + difference h s g n := by
  exact fwdDiff_iter_add h f g s

theorem difference_mul_const (h s : ℕ) (a : R) (f : ℕ → R) :
    difference h s (fun n => a * f n) = fun n => a * difference h s f n := by
  exact fwdDiff_iter_const_smul h a f s

theorem difference_sum {ι : Type*} (h s : ℕ) (S : Finset ι) (f : ι → ℕ → R) :
    difference h s (fun n => ∑ i ∈ S, f i n) = fun n => ∑ i ∈ S, difference h s (f i) n := by
  simpa only [difference, Finset.sum_fn] using fwdDiff_iter_finsetSum h S f s

/-- The explicit signed finite-difference formula, valid without characteristic restrictions. -/
theorem difference_explicit (h s : ℕ) (f : ℕ → R) (n : ℕ) :
    difference h s f n = ∑ j ∈ Finset.range (s+1),
      (-1 : R)^(s-j) * (s.choose j : R) * f (n+j*h) := by
  simpa [difference, zsmul_eq_mul, nsmul_eq_mul] using fwdDiff_iter_eq_sum_shift h f s n

/-- Newton reconstruction at every natural argument, with coefficients derived from f. -/
theorem finite_mahler_reconstruction (f : ℕ → R) (n : ℕ) :
    f n = ∑ r ∈ Finset.range (n+1), coefficient f r * (n.choose r : R) := by
  simpa [coefficient, difference, nsmul_eq_mul, mul_comm] using shift_eq_sum_fwdDiff_iter 1 f n 0

/-- Applying differences shifts the entire coefficient sequence; it does not need convergence. -/
theorem coefficient_difference (f : ℕ → R) (s r : ℕ) :
    coefficient (difference 1 s f) r = coefficient f (s+r) := by
  simp only [coefficient, difference, Function.iterate_add_apply, Nat.add_comm s r]

/-- The apparent infinite sum has at most n+1 nonzero terms at the natural argument n. -/
theorem difference_from_coefficients (f : ℕ → R) (n s : ℕ) :
    difference 1 s f n = ∑ j ∈ Finset.range (n+1),
      coefficient f (s+j) * (n.choose j : R) := by
  rw [finite_mahler_reconstruction (difference 1 s f) n]
  simp only [coefficient_difference]

/-- A difference needs the whole forward stencil, not just its starting value. -/
theorem difference_eq_of_stencil (h s n : ℕ) (f g : ℕ → R)
    (hfg : ∀ j ≤ s, f (n+j*h) = g (n+j*h)) :
    difference h s f n = difference h s g n := by
  rw [difference_explicit, difference_explicit]
  apply Finset.sum_congr rfl
  intro j hj
  rw [hfg j (Finset.mem_range_succ_iff.mp hj)]

theorem coefficient_eq_of_prefix (f g : ℕ → R) (r : ℕ)
    (hfg : ∀ j ≤ r, f j = g j) : coefficient f r = coefficient g r := by
  apply difference_eq_of_stencil
  simpa using hfg

/-- Zero extending the binomial coefficients gives interpolation for n<=N. -/
theorem interpolant_reproduces (f : ℕ → R) (N n : ℕ) (hn : n ≤ N) :
    interpolant N (coefficient f) n = f n := by
  rw [finite_mahler_reconstruction f n]
  unfold interpolant
  symm
  apply Finset.sum_subset (Finset.range_mono (by omega))
  intro r _ hr
  have hnr : n < r := by simpa using hr
  simp [Nat.choose_eq_zero_of_lt hnr]

/-- Exact extraction of the coefficients of the finite binomial interpolant. -/
theorem coefficient_interpolant (N : ℕ) (c : ℕ → R) (s : ℕ) :
    coefficient (interpolant N c) s = if s ≤ N then c s else 0 := by
  classical
  unfold coefficient interpolant
  rw [difference_sum]
  simp only [difference_mul_const]
  simp only [difference, fwdDiff_iter_choose_zero]
  by_cases hs : s ≤ N
  · simp [hs]
  · simp [hs]

/-- All differences of the finite interpolant, including orders beyond its degree. -/
theorem interpolant_difference (N : ℕ) (c : ℕ → R) (n s : ℕ) :
    difference 1 s (interpolant N c) n = ∑ j ∈ Finset.range (n+1),
      (if s+j ≤ N then c (s+j) else 0) * (n.choose j : R) := by
  rw [difference_from_coefficients]
  simp only [coefficient_interpolant]

/-- Finite samples determine precisely the stencils contained in the sample interval. -/
theorem finite_sample_difference (f : ℕ → R) (N n s : ℕ) (hns : n+s ≤ N) :
    difference 1 s f n = difference 1 s (interpolant N (coefficient f)) n := by
  apply difference_eq_of_stencil
  intro j hj
  symm
  exact interpolant_reproduces f N (n+j*1) (by omega)

theorem interpolant_high_difference (N : ℕ) (c : ℕ → R) (n s : ℕ) (hs : N < s) :
    difference 1 s (interpolant N c) n = 0 := by
  rw [interpolant_difference]
  apply Finset.sum_eq_zero
  intro j _
  simp [show ¬ s+j ≤ N by omega]

/-- Finite coefficients are uniquely determined by the values at 0,...,N. -/
theorem interpolant_coefficients_unique (N : ℕ) (c d : ℕ → R)
    (h : ∀ n ≤ N, interpolant N c n = interpolant N d n) :
    ∀ r ≤ N, c r = d r := by
  intro r hr
  have hh := coefficient_eq_of_prefix (interpolant N c) (interpolant N d) r
    (by intro j hj; exact h j (by omega))
  simpa [coefficient_interpolant, hr] using hh

end KomorebiPaperIX.Mahler
