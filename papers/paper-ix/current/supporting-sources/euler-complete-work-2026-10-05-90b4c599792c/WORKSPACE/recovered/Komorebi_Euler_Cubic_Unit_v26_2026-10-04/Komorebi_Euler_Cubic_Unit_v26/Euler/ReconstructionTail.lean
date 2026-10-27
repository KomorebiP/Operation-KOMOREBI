module
public import Euler.EulerKernel
public import Euler.SourceCertificates
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- A genuine reconstruction summand, using the Bernoulli coefficient and actual analytic source. -/
def reconstructionTerm (N m : ℕ) : D :=
  eulerKappa m * ((2*N).choose (2*m):D) * reval eulerSource ((N-m:ℕ):D)

/-- The finite reconstruction sum. Identification with the signed Euler sequence is separate. -/
def reconstructionRow (N : ℕ) : D :=
  ∑ m ∈ Finset.range (N+1), reconstructionTerm N m

/-- Omitted terms of the actual coefficient/source reconstruction, not a definition of Euler numbers. -/
def reconstructionTail (M N : ℕ) : D :=
  ∑ m ∈ (Finset.range (N+1)).filter (fun m => M<m), reconstructionTerm N m

lemma reconstructionTerm_norm_le (N m : ℕ) (hm : 0<m) :
    ‖reconstructionTerm N m‖≤(2:ℝ)^(-(4*(m:ℤ)-1)) := by
  rw [reconstructionTerm,norm_mul,norm_mul,eulerSource_norm_one,mul_one,
    eulerKappa_norm m hm]
  exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)

/-- Uniform truncation bound, proved without identifying the reconstruction with Euler numbers. -/
theorem reconstructionTail_norm_bound (M N : ℕ) :
    ‖reconstructionTail M N‖≤(2:ℝ)^(-(4*(M:ℤ)+3)) := by
  unfold reconstructionTail
  apply IsUltrametricDist.norm_sum_le_of_forall_le_of_nonneg (by positivity)
  intro m hm
  have hlt : M<m := (Finset.mem_filter.mp hm).2
  apply (reconstructionTerm_norm_le N m (by omega)).trans
  apply zpow_le_zpow_right₀ (by norm_num)
  omega

lemma reconstructionTail_empty (M N : ℕ) (h : N≤M) : reconstructionTail M N=0 := by
  unfold reconstructionTail
  apply Finset.sum_eq_zero
  intro m hm
  have hr : m<N+1 := Finset.mem_range.mp (Finset.mem_filter.mp hm).1
  have hl := (Finset.mem_filter.mp hm).2
  omega

@[simp] lemma eulerSource_at_zero : reval eulerSource 0=1 := by
  have h:=eulerSource_integer_identity 0
  norm_num at h
  exact h

lemma reconstructionTerm_diagonal (N : ℕ) : reconstructionTerm N N=eulerKappa N := by
  simp [reconstructionTerm,eulerSource_at_zero]

/-- The first omitted row contains exactly one term. -/
theorem reconstructionTail_first_row (M : ℕ) :
    reconstructionTail M (M+1)=eulerKappa (M+1) := by
  unfold reconstructionTail
  rw [Finset.sum_eq_single (M+1)]
  · exact reconstructionTerm_diagonal _
  · intro m hm hne
    have hr : m<M+1+1 := Finset.mem_range.mp (Finset.mem_filter.mp hm).1
    have hl := (Finset.mem_filter.mp hm).2
    omega
  · intro hnot
    apply False.elim
    exact hnot (Finset.mem_filter.mpr ⟨Finset.mem_range.mpr (by omega),by omega⟩)

/-- Equality at the first omitted row proves optimality of the uniform reconstruction bound. -/
theorem reconstructionTail_first_norm (M : ℕ) :
    ‖reconstructionTail M (M+1)‖=(2:ℝ)^(-(4*(M:ℤ)+3)) := by
  rw [reconstructionTail_first_row,eulerKappa_norm (M+1) (by omega)]
  congr 1
  push_cast
  ring

/-- A residue formulation of the uniform tail bound in the actual ring Z_2. -/
theorem reconstructionTail_modulus (M N : ℕ) :
    redPow (4*M+3) (reconstructionTail M N)=0 := by
  apply (redPow_zero_iff_norm _ _).mpr
  convert reconstructionTail_norm_bound M N using 1
  push_cast
  ring

/-- The sharp exponent cannot be increased even by one binary digit uniformly. -/
theorem reconstructionTail_next_modulus_nonzero (M : ℕ) :
    redPow (4*M+4) (reconstructionTail M (M+1))≠0 := by
  intro hz
  have hn := (redPow_zero_iff_norm _ _).mp hz
  rw [reconstructionTail_first_norm] at hn
  have he := (zpow_le_zpow_iff_right₀ (show (1:ℝ)<2 by norm_num)).mp hn
  push_cast at he
  omega


/-- The retained prefix with exactly the same original-index summands. -/
def reconstructionTrunc (M N : ℕ) : D :=
  ∑ m ∈ (Finset.range (N+1)).filter (fun m => m≤M), reconstructionTerm N m

lemma reconstructionRow_split (M N : ℕ) :
    reconstructionRow N=reconstructionTrunc M N+reconstructionTail M N := by
  unfold reconstructionRow reconstructionTrunc reconstructionTail
  rw [Finset.sum_filter,Finset.sum_filter,← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro m _
  by_cases h : m≤M
  · simp [h,show ¬M<m by omega]
  · simp [h,show M<m by omega]

/-- The tail is exactly the reconstruction error; no Euler-sequence equality is assumed. -/
theorem reconstruction_error_identity (M N : ℕ) :
    reconstructionRow N-reconstructionTrunc M N=reconstructionTail M N := by
  rw [reconstructionRow_split]
  ring

theorem reconstruction_error_modulus (M N : ℕ) :
    redPow (4*M+3) (reconstructionRow N-reconstructionTrunc M N)=0 := by
  rw [reconstruction_error_identity]
  exact reconstructionTail_modulus M N

end Komorebi.Euler
