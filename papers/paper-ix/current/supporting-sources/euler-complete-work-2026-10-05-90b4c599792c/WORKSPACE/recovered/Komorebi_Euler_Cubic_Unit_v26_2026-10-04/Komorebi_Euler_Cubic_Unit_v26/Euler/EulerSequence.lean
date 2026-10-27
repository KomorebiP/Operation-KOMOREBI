module
public import Euler.EulerIdentification
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

lemma signedEulerEGF_mul_cosh : signedEulerEGF*formalCosh 1=1 :=
  PowerSeries.inv_mul_cancel _ (by simp)

lemma signedEulerEGF_coeff (n : ℕ) :
    coeff n signedEulerEGF = signedEulerRat n/n.factorial := by
  unfold signedEulerRat
  have h : (n.factorial:ℚ)≠0 := by exact_mod_cast Nat.factorial_ne_zero n
  field_simp

@[simp] lemma signedEulerRat_zero : signedEulerRat 0=1 := by
  simp [signedEulerRat,signedEulerEGF,coeff_zero_eq_constantCoeff,constantCoeff_inv]

lemma signedEulerEGF_odd (N : ℕ) : coeff (2*N+1) signedEulerEGF=0 := by
  rw [← formal_euler_reconstruction,coeff_mul,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk,Finset.sum_range_succ,
    formalKernel_coeff_odd,zero_mul,add_zero]
  rw [sum_even_range _ (fun m => by rw [formalKernel_coeff_odd,zero_mul])]
  apply Finset.sum_eq_zero
  intro m hm
  have hmn : m≤N := Finset.mem_range_succ_iff.mp hm
  rw [show 2*N+1-2*m=2*(N-m)+1 by omega,formalSource_coeff_odd,mul_zero]

@[simp] theorem signedEulerRat_odd (N : ℕ) : signedEulerRat (2*N+1)=0 := by
  simp [signedEulerRat,signedEulerEGF_odd]

lemma factorial_convolution_weight (n k : ℕ) (hk : k≤n) (a b : ℚ) :
    (n.factorial:ℚ)*((a/k.factorial)*(b/(n-k).factorial)) =
      a*(n.choose k:ℚ)*b := by
  have hf : (n.choose k:ℚ)*k.factorial*(n-k).factorial=n.factorial := by
    exact_mod_cast Nat.choose_mul_factorial_mul_factorial hk
  have h1 : (k.factorial:ℚ)≠0 := by exact_mod_cast Nat.factorial_ne_zero k
  have h2 : ((n-k).factorial:ℚ)≠0 := by exact_mod_cast Nat.factorial_ne_zero (n-k)
  rw [← hf]
  field_simp

/-- The defining reciprocal-cosh convolution recurrence, valid at every even index. -/
theorem signedEulerRat_even_convolution (N : ℕ) :
    (∑ m ∈ Finset.range (N+1), ((2*N).choose (2*m):ℚ)*signedEulerRat (2*m)) =
      if N=0 then 1 else 0 := by
  have h := congrArg (fun f:PowerSeries ℚ => ( (2*N).factorial:ℚ)*coeff (2*N) f)
    signedEulerEGF_mul_cosh
  rw [coeff_mul,Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at h
  rw [sum_even_range _ (fun m => by rw [signedEulerEGF_odd,zero_mul]),Finset.mul_sum] at h
  have hsum :
      (∑ m ∈ Finset.range (N+1), ((2*N).factorial:ℚ)*
        (coeff (2*m) signedEulerEGF*coeff (2*N-2*m) (formalCosh 1))) =
      ∑ m ∈ Finset.range (N+1), ((2*N).choose (2*m):ℚ)*signedEulerRat (2*m) := by
    apply Finset.sum_congr rfl
    intro m hm
    have hmn : m≤N := Finset.mem_range_succ_iff.mp hm
    rw [show 2*N-2*m=2*(N-m) by omega,formalCosh_coeff_even,one_pow,signedEulerEGF_coeff]
    rw [← show 2*N-2*m=2*(N-m) by omega]
    rw [factorial_convolution_weight (2*N) (2*m) (by omega)]
    ring
  rw [hsum] at h
  rw [h,coeff_one]
  by_cases hN : N=0
  · subst N; norm_num
  · simp [hN,show 2*N≠0 by omega]

/-- The usual signed even-Euler recurrence; no reconstruction appears in its statement. -/
theorem signedEulerRat_even_succ (N : ℕ) :
    signedEulerRat (2*(N+1)) =
      -(∑ m ∈ Finset.range (N+1),
        ((2*(N+1)).choose (2*m):ℚ)*signedEulerRat (2*m)) := by
  have h := signedEulerRat_even_convolution (N+1)
  rw [Finset.sum_range_succ] at h
  simp only [Nat.choose_self,Nat.cast_one,one_mul,ite_eq_right (by omega : N+1≠0)] at h
  exact eq_neg_of_add_eq_zero_right h

@[simp] lemma signedEulerRat_two : signedEulerRat 2 = -1 := by
  have h := signedEulerRat_even_succ 0
  simpa using h

@[simp] lemma signedEulerRat_four : signedEulerRat 4 = 5 := by
  have h := signedEulerRat_even_succ 1
  norm_num [Finset.sum_range_succ,Nat.choose] at h ⊢
  exact h

@[simp] lemma signedEulerRat_six : signedEulerRat 6 = -61 := by
  have h := signedEulerRat_even_succ 2
  norm_num [Finset.sum_range_succ,Nat.choose] at h ⊢
  exact h

/-- The cosh convolution uniquely characterizes the independently defined even Euler sequence. -/
theorem signedEulerRat_even_unique (e : ℕ→ℚ)
    (h : ∀ N, (∑ m ∈ Finset.range (N+1), ((2*N).choose (2*m):ℚ)*e m) =
      if N=0 then 1 else 0) : ∀ N, e N=signedEulerRat (2*N) := by
  intro N
  induction N using Nat.strong_induction_on with
  | h N ih =>
    have h1 := h N
    have h2 := signedEulerRat_even_convolution N
    rw [Finset.sum_range_succ] at h1 h2
    simp only [Nat.choose_self,Nat.cast_one,one_mul] at h1 h2
    have hs : (∑ m ∈ Finset.range N, ((2*N).choose (2*m):ℚ)*e m) =
      ∑ m ∈ Finset.range N, ((2*N).choose (2*m):ℚ)*signedEulerRat (2*m) := by
        apply Finset.sum_congr rfl
        intro m hm
        rw [ih m (Finset.mem_range.mp hm)]
    rw [hs] at h1
    exact add_left_cancel (h1.trans h2.symm)

end Komorebi.Euler
