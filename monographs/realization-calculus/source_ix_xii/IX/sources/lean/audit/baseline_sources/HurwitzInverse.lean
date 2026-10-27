module

public import HurwitzConvolution
public import Triangular

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.HurwitzInverse

open Hurwitz

variable {F : Type*} [Field F]

/-- The inverse is constructed by the actual full coefficient recurrence. -/
def inverse (g : ℕ → F) : ℕ → F :=
  Triangular.solve (fun n k => (n.choose k : F)*g (n-k)) oneSeries

theorem inverse_step (g : ℕ → F) (hg : g 0=1) (n : ℕ) :
    inverse g n = oneSeries n - ∑ k ∈ Finset.range n, (n.choose k : F)*inverse g k*g (n-k) := by
  rw [inverse, Triangular.solve_step]
  simp only [Nat.sub_self, Nat.choose_self, Nat.cast_one, one_mul, hg, div_one]
  rw [Fin.sum_univ_eq_sum_range (fun k => (n.choose k : F)*g (n-k)*
    Triangular.solve (fun n k => (n.choose k : F)*g (n-k)) oneSeries k) n]
  congr 1
  apply Finset.sum_congr rfl
  intro k _
  ring

@[simp] theorem inverse_zero (g : ℕ → F) (hg : g 0=1) : inverse g 0=1 := by
  rw [inverse_step g hg]
  simp [oneSeries]

/-- The defining product equation is proved, not assumed. -/
theorem inverse_convolution (g : ℕ → F) (hg : g 0=1) :
    convolution (inverse g) g = oneSeries := by
  funext n
  rw [convolution, Finset.sum_range_succ, inverse_step g hg n]
  simp [hg, mul_sub]

/-- Reciprocal differentiation in characteristic p, using actual product rules. -/
theorem inverse_prime_difference (p : ℕ) (hp : p.Prime) [CharP F p]
    (g : ℕ → F) (hg : g 0=1) (hperiod : shift p g = shift 1 g) :
    shift p (inverse g) = shift 1 (inverse g) := by
  have h0p : shift p (oneSeries : ℕ → F) = 0 := by
    funext n; simp [shift, oneSeries, hp.ne_zero]
  have h01 : shift 1 (oneSeries : ℕ → F) = 0 := by
    funext n; simp [shift, oneSeries]
  have h1 := prime_shift_convolution p hp (inverse g) g
  have h2 := shift_one_convolution (inverse g) g
  rw [inverse_convolution g hg, h0p, hperiod] at h1
  rw [inverse_convolution g hg, h01] at h2
  have hc : convolution (shift p (inverse g)-shift 1 (inverse g)) g = 0 := by
    rw [convolution_sub_left]
    have he : convolution (shift p (inverse g)) g = convolution (shift 1 (inverse g)) g :=
      add_left_cancel (h1.symm.trans h2)
    rw [he, sub_self]
  exact sub_eq_zero.mp (convolution_left_eq_zero _ g hg hc)

/-- A reciprocal retains the actual degree support of a residue-zero series. -/
theorem inverse_support (m : ℕ) (g : ℕ → F) (hg : g 0=1)
    (hs : ∀ n, ¬ m ∣ n → g n=0) (n : ℕ) (hn : ¬ m ∣ n) : inverse g n=0 := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
    have hn0 : n≠0 := by intro h; subst n; exact hn (dvd_zero m)
    rw [inverse_step g hg, oneSeries, ite_eq_right hn0]
    have hz : (∑ k ∈ Finset.range n, (n.choose k : F)*inverse g k*g (n-k))=0 := by
      apply Finset.sum_eq_zero
      intro k hk
      by_cases hmk : m ∣ k
      · have hdiff : ¬ m ∣ n-k := by
          intro hd
          have hh := dvd_add hmk hd
          rw [Nat.add_sub_of_le (Nat.le_of_lt (Finset.mem_range.mp hk))] at hh
          exact hn hh
        rw [hs (n-k) hdiff, mul_zero]
      · rw [ih k (Finset.mem_range.mp hk) hmk]
        simp
    rw [hz, sub_zero]

/-- Explicit sum reindexing; all off-support terms must actually vanish. -/
theorem sum_on_multiples {R : Type*} [AddCommMonoid R] (m n : ℕ) (hm : 0<m)
    (f : ℕ → R) (hf : ∀ k ≤ m*n, ¬m∣k → f k=0) :
    (∑ k ∈ Finset.range (m*n+1), f k) = ∑ q ∈ Finset.range (n+1), f (m*q) := by
  classical
  have hfilter : (∑ k ∈ (Finset.range (m*n+1)).filter (fun k => m∣k), f k) =
      ∑ k ∈ Finset.range (m*n+1), f k := by
    apply Finset.sum_subset (Finset.filter_subset _ _)
    intro k hk hnot
    exact hf k (Finset.mem_range_succ_iff.mp hk) (by
      intro hd; exact hnot (Finset.mem_filter.mpr ⟨hk,hd⟩))
  rw [← hfilter]
  symm
  apply Finset.sum_bij (fun q _ => m*q)
  · intro q hq
    apply Finset.mem_filter.mpr
    exact ⟨Finset.mem_range_succ_iff.mpr (Nat.mul_le_mul_left m (Finset.mem_range_succ_iff.mp hq)), dvd_mul_right m q⟩
  · intro a _ b _ hab
    exact Nat.eq_of_mul_eq_mul_left hm hab
  · intro k hk
    obtain ⟨hk,hd⟩ := Finset.mem_filter.mp hk
    refine ⟨k/m, ?_, Nat.mul_div_cancel' hd⟩
    apply Finset.mem_range_succ_iff.mpr
    exact (Nat.div_le_iff_le_mul hm).mpr (by
      have hle := Finset.mem_range_succ_iff.mp hk
      rw [Nat.mul_comm m n] at hle
      omega)
  · intro q _; rfl

end KomorebiPaperIX.HurwitzInverse
