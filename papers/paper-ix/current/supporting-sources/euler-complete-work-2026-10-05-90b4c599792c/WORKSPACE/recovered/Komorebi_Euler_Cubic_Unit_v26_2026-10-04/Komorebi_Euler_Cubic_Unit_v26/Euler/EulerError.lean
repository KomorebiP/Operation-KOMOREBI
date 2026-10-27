module
public import Euler.EulerSequence
@[expose] public section
noncomputable section
namespace Komorebi.Euler

lemma eulerSource_reval_rat (n : ℕ) :
    (reval eulerSource (n:D):ℚ_[2])=(eulerSourceRat n:ℚ_[2]) := by
  rw [coe_reval eulerSource_restricted,PadicInt.coe_natCast,eulerSource_integer_formula]
  unfold eulerSourceRat
  push_cast
  rfl

/-- The already-constructed dyadic reconstruction equals the independent rational Euler number. -/
theorem reconstructionRow_coe_euler (N : ℕ) :
    (reconstructionRow N:ℚ_[2])=(signedEulerRat (2*N):ℚ_[2]) := by
  rw [signedEulerRat_reconstruction,reconstructionRow,PadicInt.coe_sum,Rat.cast_sum]
  apply Finset.sum_congr rfl
  intro m _
  simp only [reconstructionTerm,PadicInt.coe_mul,PadicInt.coe_natCast,
    eulerKappa_coe,eulerSource_reval_rat,Rat.cast_mul,Rat.cast_natCast]

/-- Dyadic integrality is a consequence of identification, not an assumption on Euler numbers. -/
theorem signedEulerRat_even_norm_le_one (N : ℕ) :
    ‖(signedEulerRat (2*N):ℚ_[2])‖≤1 := by
  rw [← reconstructionRow_coe_euler]
  exact PadicInt.norm_le_one _

/-- The independent signed Euler number, embedded into Z_2 after proving integrality. -/
def signedEulerEven (N : ℕ) : D :=
  ⟨(signedEulerRat (2*N):ℚ_[2]),signedEulerRat_even_norm_le_one N⟩

@[simp] lemma signedEulerEven_coe (N : ℕ) :
    (signedEulerEven N:ℚ_[2])=(signedEulerRat (2*N):ℚ_[2]) := rfl

/-- All-row identification in the actual dyadic integer ring. -/
theorem reconstructionRow_eq_euler (N : ℕ) : reconstructionRow N=signedEulerEven N := by
  apply Subtype.ext
  exact reconstructionRow_coe_euler N

/-- The signed Euler approximation error is exactly the previously constructed omitted tail. -/
theorem signedEuler_error_identity (M N : ℕ) :
    signedEulerEven N-reconstructionTrunc M N=reconstructionTail M N := by
  rw [← reconstructionRow_eq_euler]
  exact reconstruction_error_identity M N

/-- The sharp all-row modulus is now an Euler-number theorem. -/
theorem signedEuler_error_modulus (M N : ℕ) :
    redPow (4*M+3) (signedEulerEven N-reconstructionTrunc M N)=0 := by
  rw [signedEuler_error_identity]
  exact reconstructionTail_modulus M N

/-- Exact norm control for the independently defined Euler sequence. -/
theorem signedEuler_error_norm_bound (M N : ℕ) :
    ‖signedEulerEven N-reconstructionTrunc M N‖≤(2:ℝ)^(-(4*(M:ℤ)+3)) := by
  rw [signedEuler_error_identity]
  exact reconstructionTail_norm_bound M N

/-- Every truncation depth has an explicit Euler-row witness to optimality. -/
theorem signedEuler_error_first_row (M : ℕ) :
    signedEulerEven (M+1)-reconstructionTrunc M (M+1)=eulerKappa (M+1) := by
  rw [signedEuler_error_identity]
  exact reconstructionTail_first_row M

theorem signedEuler_error_first_norm (M : ℕ) :
    ‖signedEulerEven (M+1)-reconstructionTrunc M (M+1)‖=(2:ℝ)^(-(4*(M:ℤ)+3)) := by
  rw [signedEuler_error_identity]
  exact reconstructionTail_first_norm M

/-- No extra binary digit can be added uniformly to this Euler approximation. -/
theorem signedEuler_error_next_modulus_nonzero (M : ℕ) :
    redPow (4*M+4) (signedEulerEven (M+1)-reconstructionTrunc M (M+1))≠0 := by
  rw [signedEuler_error_identity]
  exact reconstructionTail_next_modulus_nonzero M

theorem signedEuler_trunc_exact (M N : ℕ) (h : N≤M) :
    signedEulerEven N=reconstructionTrunc M N := by
  have he := signedEuler_error_identity M N
  rw [reconstructionTail_empty M N h] at he
  exact sub_eq_zero.mp he

@[simp] lemma signedEulerEven_zero : signedEulerEven 0=1 := by
  apply Subtype.ext
  simp

@[simp] lemma signedEulerEven_one : signedEulerEven 1 = -1 := by
  apply Subtype.ext
  simp

@[simp] lemma signedEulerEven_two : signedEulerEven 2 = 5 := by
  apply PadicInt.ext
  change (signedEulerEven 2:ℚ_[2])=(5:ℚ_[2])
  simp

end Komorebi.Euler
