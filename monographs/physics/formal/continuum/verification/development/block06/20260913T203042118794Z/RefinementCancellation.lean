module

public import Mathlib.Analysis.Normed.Module.Basic
public import Mathlib.Tactic

/-!
Chapter 4.9: exact finite Richardson cancellation. The source uses b=2.
The statements here allow any real refinement ratio b>1, and real vector
space values. No formal infinite sum is interpreted as a convergent series.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.RefinementCancellation
open scoped BigOperators
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- Actual recursive extrapolation of the sampled function. -/
def tower (b : ℝ) (f : ℝ → E) : ℕ → ℝ → E
  | 0, h => f h
  | m+1, h => (b^(m+1)-1)⁻¹ •
      (b^(m+1) • tower b f m (h/b) - tower b f m h)

/-- The source's two-index table, constructed from the actual recursion. -/
def table (b : ℝ) (f : ℝ → E) (h : ℝ) (m j : ℕ) : E :=
  tower b f m (h / b^j)

/-- Exact response multiplier on the degree-r monomial after m levels. -/
def coefficient (b : ℝ) : ℕ → ℕ → ℝ
  | 0, _ => 1
  | m+1, r => ((b^(m+1) / b^r - 1) / (b^(m+1)-1)) * coefficient b m r

theorem denominator_pos {b : ℝ} (hb : 1 < b) (m : ℕ) :
    0 < b^(m+1)-1 := by
  have hp : 1 < b^(m+1) := one_lt_pow₀ hb (Nat.succ_ne_zero m)
  linarith

theorem denominator_ne_zero {b : ℝ} (hb : 1 < b) (m : ℕ) :
    b^(m+1)-1 ≠ 0 := ne_of_gt (denominator_pos hb m)

theorem table_zero (b : ℝ) (f : ℝ → E) (h : ℝ) (j : ℕ) :
    table b f h 0 j = f (h / b^j) := rfl

theorem table_base_column (b : ℝ) (f : ℝ → E) (h : ℝ) (m : ℕ) :
    table b f h m 0 = tower b f m h := by simp [table]

theorem table_succ (b : ℝ) (f : ℝ → E) (h : ℝ) (m j : ℕ) :
    table b f h (m+1) j = (b^(m+1)-1)⁻¹ •
      (b^(m+1) • table b f h m (j+1) - table b f h m j) := by
  simp only [table, tower, div_div, pow_succ]

theorem tower_congr (b : ℝ) {f g : ℝ → E} (hfg : ∀ h, f h = g h)
    (m : ℕ) (h : ℝ) : tower b f m h = tower b g m h := by
  congr 1
  exact funext hfg

theorem tower_zero (b : ℝ) (m : ℕ) (h : ℝ) :
    tower b (fun _ => (0 : E)) m h = 0 := by
  induction m generalizing h with
  | zero => rfl
  | succ m ih => simp [tower, ih]

theorem tower_add (b : ℝ) (f g : ℝ → E) (m : ℕ) (h : ℝ) :
    tower b (fun x => f x + g x) m h = tower b f m h + tower b g m h := by
  induction m generalizing h with
  | zero => rfl
  | succ m ih =>
    simp only [tower, ih, smul_add, smul_sub]
    abel

theorem tower_sub (b : ℝ) (f g : ℝ → E) (m : ℕ) (h : ℝ) :
    tower b (fun x => f x - g x) m h = tower b f m h - tower b g m h := by
  induction m generalizing h with
  | zero => rfl
  | succ m ih =>
    simp only [tower, ih, smul_sub]
    abel

theorem tower_smul (b : ℝ) (c : ℝ) (f : ℝ → E) (m : ℕ) (h : ℝ) :
    tower b (fun x => c • f x) m h = c • tower b f m h := by
  induction m generalizing h with
  | zero => rfl
  | succ m ih =>
    simp only [tower, ih, smul_sub, smul_smul]
    congr 1 <;> congr 1 <;> ring

theorem tower_sum {I : Type*} (s : Finset I) (b : ℝ) (f : I → ℝ → E)
    (m : ℕ) (h : ℝ) :
    tower b (fun x => ∑ i ∈ s, f i x) m h = ∑ i ∈ s, tower b (f i) m h := by
  classical
  induction s using Finset.induction_on with
  | empty => simp [tower_zero]
  | @insert i s hi ih => simp only [Finset.sum_insert hi, tower_add, ih]

theorem tower_const {b : ℝ} (hb : 1 < b) (c : E) (m : ℕ) (h : ℝ) :
    tower b (fun _ => c) m h = c := by
  induction m generalizing h with
  | zero => rfl
  | succ m ih =>
    simp only [tower, ih]
    have hc : b^(m+1) • c - c = (b^(m+1)-1) • c := by
      rw [sub_smul, one_smul]
    rw [hc, smul_smul, inv_mul_cancel₀ (denominator_ne_zero hb m), one_smul]

theorem coefficient_product (b : ℝ) (m r : ℕ) :
    coefficient b m r = ∏ k ∈ Finset.range m,
      ((b^(k+1) / b^r - 1) / (b^(k+1)-1)) := by
  induction m with
  | zero => simp [coefficient]
  | succ m ih => simp only [coefficient, Finset.prod_range_succ, ih, mul_comm]

theorem coefficient_zero_degree {b : ℝ} (hb : 1 < b) (m : ℕ) :
    coefficient b m 0 = 1 := by
  induction m with
  | zero => rfl
  | succ m ih => simp [coefficient, ih, denominator_ne_zero hb m]

theorem coefficient_diagonal {b : ℝ} (hb : 1 < b) (r : ℕ) (hr : 0 < r) :
    coefficient b r r = 0 := by
  obtain ⟨m, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hr)
  simp [coefficient, pow_ne_zero _ (ne_of_gt (lt_trans zero_lt_one hb))]

theorem coefficient_cancel {b : ℝ} (hb : 1 < b) (m r : ℕ)
    (hr : 0 < r) (hrm : r ≤ m) : coefficient b m r = 0 := by
  induction m with
  | zero => omega
  | succ m ih =>
    rcases Nat.eq_or_lt_of_le hrm with heq | hlt
    · subst r
      exact coefficient_diagonal hb (m+1) (Nat.succ_pos m)
    · simp [coefficient, ih (Nat.lt_succ_iff.mp hlt)]

theorem tower_monomial (b : ℝ) (m r : ℕ) (v : E) (h : ℝ) :
    tower b (fun x => x^r • v) m h = (coefficient b m r * h^r) • v := by
  induction m generalizing h with
  | zero => simp [tower, coefficient]
  | succ m ih =>
    simp only [tower, ih, smul_smul, ← sub_smul, coefficient, div_pow]
    congr 1
    ring

theorem tower_monomial_cancel {b : ℝ} (hb : 1 < b) (m r : ℕ)
    (hr : 0 < r) (hrm : r ≤ m) (v : E) (h : ℝ) :
    tower b (fun x => x^r • v) m h = 0 := by
  rw [tower_monomial, coefficient_cancel hb m r hr hrm]
  simp

/-- A finite expansion polynomial. c k multiplies degree k+1. -/
def expansion (F : E) (c : ℕ → E) (n : ℕ) (h : ℝ) : E :=
  F + ∑ k ∈ Finset.range n, h^(k+1) • c k

theorem tower_expansion {b : ℝ} (hb : 1 < b) (F : E) (c : ℕ → E)
    (n m : ℕ) (h : ℝ) :
    tower b (expansion F c n) m h = F + ∑ k ∈ Finset.range n,
      (coefficient b m (k+1) * h^(k+1)) • c k := by
  unfold expansion
  rw [tower_add, tower_const hb, tower_sum]
  simp only [tower_monomial]

theorem tower_expansion_exact {b : ℝ} (hb : 1 < b) (F : E) (c : ℕ → E)
    (n m : ℕ) (hnm : n ≤ m) (h : ℝ) :
    tower b (expansion F c n) m h = F := by
  rw [tower_expansion hb]
  have hz : (∑ k ∈ Finset.range n,
      (coefficient b m (k+1) * h^(k+1)) • c k) = 0 := by
    apply Finset.sum_eq_zero
    intro k hk
    rw [coefficient_cancel hb m (k+1) (Nat.succ_pos k)
      (by have := Finset.mem_range.mp hk; omega)]
    simp
  rw [hz, add_zero]

/-- Exact error identity; the sampled remainder is still evaluated by the
actual tower. The asymptotic control of this remainder is a separate theorem. -/
theorem tower_error_identity {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (m : ℕ) (h : ℝ) :
    tower b f m h - F =
      tower b (fun x => f x - expansion F c m x) m h := by
  rw [tower_sub, tower_expansion_exact hb F c m m le_rfl]

end KomorebiPhysics.RefinementCancellation
