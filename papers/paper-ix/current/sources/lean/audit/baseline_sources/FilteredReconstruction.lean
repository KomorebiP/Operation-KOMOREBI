module

public import Mathlib.NumberTheory.Padics.PadicIntegers
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.Filtered

/-- An infinite filtration weight means that the corresponding coefficient is zero. -/
def weightPower {R : Type*} [MonoidWithZero R] (p : R) : WithTop ℕ → R
  | ⊤ => 0
  | (k : ℕ) => p ^ k

@[simp] theorem weightPower_top {R : Type*} [MonoidWithZero R] (p : R) :
    weightPower p ⊤ = 0 := rfl

@[simp] theorem weightPower_nat {R : Type*} [MonoidWithZero R] (p : R) (k : ℕ) :
    weightPower p (k : WithTop ℕ) = p ^ k := rfl

theorem power_dvd_weightPower {R : Type*} [CommMonoidWithZero R] (p : R)
    (L : ℕ) (w : WithTop ℕ) (h : (L : WithTop ℕ) ≤ w) : p ^ L ∣ weightPower p w := by
  cases w with
  | top => simp
  | coe k =>
    change p ^ L ∣ p ^ k
    exact pow_dvd_pow p (WithTop.coe_le_coe.mp h)

/-- Generic finite omitted-tail divisibility, with no prime or row-size assumption. -/
theorem omitted_tail_dvd {R ι : Type*} [CommRing R] (p : R) (L : ℕ)
    (s : Finset ι) (w : ι → WithTop ℕ) (f : ι → R)
    (hf : ∀ i ∈ s, (L : WithTop ℕ) ≤ w i → p ^ L ∣ f i) :
    p ^ L ∣ (∑ i ∈ s, f i) - ∑ i ∈ s.filter (fun i => w i < L), f i := by
  classical
  rw [← Finset.sum_filter_add_sum_filter_not s (fun i => w i < L) f]
  rw [add_sub_cancel_left]
  apply Finset.dvd_sum
  intro i hi
  obtain ⟨his, hiw⟩ := Finset.mem_filter.mp hi
  exact hf i his (le_of_not_gt hiw)

/-- Full WithTop-weighted coefficient version of Paper IX, Theorem 2.2. -/
theorem filtered_triangular_reconstruction {R : Type*} [CommRing R]
    (p : R) (w : ℕ → WithTop ℕ) (c S : ℕ → R) (n L : ℕ) :
    p ^ L ∣
      (∑ r ∈ Finset.range (n + 1), (n.choose r : R) * c r * weightPower p (w r) * S (n-r)) -
      ∑ r ∈ (Finset.range (n + 1)).filter (fun r => w r < L),
        (n.choose r : R) * c r * weightPower p (w r) * S (n-r) := by
  apply omitted_tail_dvd
  intro r _ hr
  exact dvd_mul_of_dvd_left
    (dvd_mul_of_dvd_right (power_dvd_weightPower p L (w r) hr) _) _

theorem padic_filtered_reconstruction (p : ℕ) [Fact p.Prime]
    (w : ℕ → WithTop ℕ) (c S : ℕ → ℤ_[p]) (n L : ℕ) :
    (p : ℤ_[p]) ^ L ∣
      (∑ r ∈ Finset.range (n + 1), (n.choose r : ℤ_[p]) * c r * weightPower (p : ℤ_[p]) (w r) * S (n-r)) -
      ∑ r ∈ (Finset.range (n + 1)).filter (fun r => w r < L),
        (n.choose r : ℤ_[p]) * c r * weightPower (p : ℤ_[p]) (w r) * S (n-r) :=
  filtered_triangular_reconstruction (p : ℤ_[p]) w c S n L

/-- The two-powers-per-level tail bound, without assuming an Euler identity. -/
theorem even_weight_tail {R : Type*} [CommRing R] (p : R) (f : ℕ → R) (n M : ℕ) :
    p ^ (2*M+2) ∣ (∑ m ∈ Finset.range (n+1), p^(2*m) * f m) -
      ∑ m ∈ (Finset.range (n+1)).filter (fun m => m ≤ M), p^(2*m) * f m := by
  classical
  have he : (fun m : ℕ => ((2*m : ℕ) : WithTop ℕ) < ((2*M+2 : ℕ) : WithTop ℕ)) =
      (fun m => m ≤ M) := by
    funext m
    apply propext
    norm_cast
    omega
  have h := omitted_tail_dvd p (2*M+2) (Finset.range (n+1))
    (fun m => ((2*m : ℕ) : WithTop ℕ)) (fun m => p^(2*m)*f m) (by
      intro m _ hm
      apply dvd_mul_of_dvd_left
      exact pow_dvd_pow p (by exact_mod_cast hm))
  simpa only [he] using h

end KomorebiPaperIX.Filtered
