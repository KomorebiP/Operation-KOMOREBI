module
public import Euler.EulerFormalSource
public import Euler.ReconstructionTail
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

lemma coeff_X_derivative_rat (f : PowerSeries ℚ) (n : ℕ) :
    coeff n (X*(d⁄dX ℚ f)) = (n:ℚ)*coeff n f := by
  cases n with
  | zero => simp
  | succ n => rw [coeff_succ_X_mul, coeff_derivative]; push_cast; ring

lemma formalKernel_coeff (n : ℕ) :
    coeff n formalKernel = (1-(n:ℚ))*4^n*bernoulli n/n.factorial := by
  rw [formalKernel,map_sub,coeff_X_derivative_rat,scaledBernoulli_coeff]
  ring

lemma formalKernel_coeff_even (m : ℕ) :
    coeff (2*m) formalKernel = eulerKappaRat m/(2*m).factorial := by
  have hp : (4:ℚ)^(2*m)=(2:ℚ)^(4*m) := by
    rw [show (4:ℚ)=(2:ℚ)^2 by norm_num,← pow_mul]
    congr 1
    omega
  rw [formalKernel_coeff,hp,eulerKappaRat]
  push_cast
  ring

lemma formalKernel_coeff_odd (m : ℕ) : coeff (2*m+1) formalKernel=0 := by
  rw [formalKernel_coeff]
  by_cases hm : m=0
  · subst m; norm_num
  · rw [bernoulli_eq_zero_of_odd (show Odd (2*m+1) from ⟨m,rfl⟩) (by omega)]
    ring

/-- Rational source values, independent of the p-adic series representation. -/
def eulerSourceRat (n : ℕ) : ℚ :=
  (9^(n+1)-1)/(8*((n:ℚ)+1)*(2*(n:ℚ)+1))

lemma formalSource_coeff_even (n : ℕ) :
    coeff (2*n) formalSource = eulerSourceRat n/(2*n).factorial := by
  rw [formalSource_coeff,show 2*n+2=2*(n+1) by omega,
    formalCosh_coeff_even,formalCosh_coeff_even]
  have hp : (3:ℚ)^(2*(n+1))=(9:ℚ)^(n+1) := by rw [pow_mul]; norm_num
  rw [hp,one_pow]
  unfold eulerSourceRat
  rw [show 2*(n+1)=2*n+1+1 by omega, Nat.factorial_succ,Nat.factorial_succ]
  push_cast
  have hf : ((2*n).factorial:ℚ)≠0 := by exact_mod_cast Nat.factorial_ne_zero (2*n)
  have h1 : (n:ℚ)+1≠0 := by positivity
  have h2 : 2*(n:ℚ)+1≠0 := by positivity
  have h3 : 2*(n:ℚ)+1+1≠0 := by positivity
  field_simp
  ring

lemma formalSource_coeff_odd (n : ℕ) : coeff (2*n+1) formalSource=0 := by
  rw [formalSource_coeff,show 2*n+1+2=2*(n+1)+1 by omega,
    formalCosh_coeff_odd,formalCosh_coeff_odd]
  ring

/-- Signed Euler numbers defined by the reciprocal-cosh EGF, not the reconstruction. -/
def signedEulerRat (n : ℕ) : ℚ := n.factorial * coeff n signedEulerEGF

/-- Exact parity projection of a finite convolution row. -/
lemma sum_even_range {R : Type*} [AddCommMonoid R] (f : ℕ→R)
    (hf : ∀n, f (2*n+1)=0) (N : ℕ) :
    (∑ n ∈ Finset.range (2*N+1), f n) =
      ∑ m ∈ Finset.range (N+1), f (2*m) := by
  induction N with
  | zero => simp
  | succ N ih =>
    rw [show 2*(N+1)+1=(2*N+1)+1+1 by omega,
      Finset.sum_range_succ, Finset.sum_range_succ, ih, hf,
      add_zero, Finset.sum_range_succ]
    rw [show 2*N+1+1=2*(N+1) by omega]
    simp only [Finset.sum_range_succ]

/-- Coefficient extraction of the proved EGF identity gives the all-row reconstruction. -/
theorem signedEulerRat_reconstruction (N : ℕ) :
    signedEulerRat (2*N) =
      ∑ m ∈ Finset.range (N+1),
        eulerKappaRat m * ((2*N).choose (2*m):ℚ) * eulerSourceRat (N-m) := by
  unfold signedEulerRat
  rw [← formal_euler_reconstruction,coeff_mul,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
  rw [sum_even_range _ (fun m => by rw [formalKernel_coeff_odd,zero_mul])]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro m hm
  have hmn : m≤N := by simpa using (Finset.mem_range_succ_iff.mp hm)
  rw [formalKernel_coeff_even,show 2*N-2*m=2*(N-m) by omega,formalSource_coeff_even]
  have hfac : ((2*N).choose (2*m):ℚ) * (2*m).factorial * (2*(N-m)).factorial =
      (2*N).factorial := by
    have h := Nat.choose_mul_factorial_mul_factorial (show 2*m≤2*N by omega)
    rw [show 2*N-2*m=2*(N-m) by omega] at h
    exact_mod_cast h
  have hf1 : ((2*m).factorial:ℚ)≠0 := by exact_mod_cast Nat.factorial_ne_zero (2*m)
  have hf2 : ((2*(N-m)).factorial:ℚ)≠0 := by exact_mod_cast Nat.factorial_ne_zero (2*(N-m))
  rw [← hfac]
  field_simp

end Komorebi.Euler
