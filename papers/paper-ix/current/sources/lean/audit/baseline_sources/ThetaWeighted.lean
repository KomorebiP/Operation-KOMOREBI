module
public import WeightedAmiceRing
public import FrobeniusSquare
public import DworkClosure
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.ThetaWeighted
open PowerSeries DworkAlgebra DworkClosure
variable (p : ℕ) [Fact p.Prime]

/-- The actual logarithmic-coordinate derivation. -/
def theta : Derivation ℚ_[p] (PowerSeries ℚ_[p]) (PowerSeries ℚ_[p]) :=
  (1+X:PowerSeries ℚ_[p]) • derivative ℚ_[p]

theorem theta_apply (f : PowerSeries ℚ_[p]) :
    theta p f=(1+X)*derivative ℚ_[p] f := rfl

theorem theta_mem (f : PowerSeries ℚ_[p]) (hf : f∈WeightedAmice.ring p) :
    theta p f∈WeightedAmice.ring p := by
  rw [theta_apply]
  exact (WeightedAmice.ring p).mul_mem
    ((WeightedAmice.ring p).add_mem (one_mem _) (WeightedAmice.X_mem p))
    (WeightedAmice.derivative_mem p f hf)

theorem deriv_mem (n : ℕ) (f : PowerSeries ℚ_[p]) (hf : f∈WeightedAmice.ring p) :
    deriv (theta p) n f∈WeightedAmice.ring p := by
  induction n with
  | zero => exact hf
  | succ n ih => rw [deriv_succ]; exact theta_mem p _ ih

theorem theta_y_power (k : ℕ) : theta p ((1+X:PowerSeries ℚ_[p])^k) =
    (k:ℚ_[p]) • (1+X:PowerSeries ℚ_[p])^k := by
  cases k with
  | zero => simp
  | succ k =>
    rw [theta_apply, derivative_pow]
    simp only [Derivation.map_add, derivative_one, derivative_X, zero_add, mul_one,
      Nat.add_sub_cancel, PowerSeries.smul_eq_C_mul]
    rw [pow_succ]
    simp only [map_natCast]
    ring

theorem deriv_y_power (s k : ℕ) : deriv (theta p) s ((1+X:PowerSeries ℚ_[p])^k) =
    (k:ℚ_[p])^s • (1+X:PowerSeries ℚ_[p])^k := by
  induction s with
  | zero => simp
  | succ s ih =>
    rw [deriv_succ, ih, Derivation.map_smul, theta_y_power, smul_smul, pow_succ]

theorem B_y_power (k : ℕ) : B (theta p) p ((1+X:PowerSeries ℚ_[p])^k) =
    ((p:ℚ_[p])⁻¹*((k:ℚ_[p])^(p^2)-(k:ℚ_[p])^p)) • (1+X:PowerSeries ℚ_[p])^k := by
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, deriv_y_power,
    ←sub_smul, smul_smul]

theorem B_constant (a : ℚ_[p]) : B (theta p) p (C a)=0 := by
  have hD : theta p (C a)=0 := by simp [theta_apply]
  have hd : ∀ n, 0<n → deriv (theta p) n (C a)=0 := by
    intro n hn
    obtain ⟨k,rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hn)
    rw [deriv_succ_right, hD, map_zero]
  simp [B, hd _ (Fact.out : p.Prime).pos, hd _ (pow_pos (Fact.out : p.Prime).pos 2)]

/-- One normalized defect of a weighted expression remains weighted. -/
def Good (f : PowerSeries ℚ_[p]) : Prop :=
  f∈WeightedAmice.ring p ∧ B (theta p) p f∈WeightedAmice.ring p

theorem good_const {a : ℚ_[p]} (ha : a∈PadicInt.subring p) : Good p (C a) := by
  exact ⟨WeightedAmice.constant_mem p ha, by rw [B_constant]; exact zero_mem _⟩

theorem good_add {f g : PowerSeries ℚ_[p]} (hf : Good p f) (hg : Good p g) :
    Good p (f+g) := by
  exact ⟨add_mem hf.1 hg.1, by rw [map_add]; exact add_mem hf.2 hg.2⟩

theorem good_neg {f : PowerSeries ℚ_[p]} (hf : Good p f) : Good p (-f) := by
  exact ⟨neg_mem hf.1, by rw [map_neg]; exact neg_mem hf.2⟩

theorem good_sum {ι : Type*} (s : Finset ι) (f : ι → PowerSeries ℚ_[p])
    (hf : ∀ i∈s, Good p (f i)) : Good p (∑ i∈s, f i) := by
  constructor
  · exact (WeightedAmice.ring p).sum_mem (fun i hi => (hf i hi).1)
  · rw [map_sum]
    exact (WeightedAmice.ring p).sum_mem (fun i hi => (hf i hi).2)

theorem middle_mem (q : ℕ) {f g : PowerSeries ℚ_[p]}
    (hf : f∈WeightedAmice.ring p) (hg : g∈WeightedAmice.ring p) :
    middle (theta p) p q f g∈WeightedAmice.ring p := by
  unfold middle
  apply (WeightedAmice.ring p).sum_mem
  intro k _
  exact mul_mem (mul_mem (natCast_mem _ _) (deriv_mem p _ f hf)) (deriv_mem p _ g hg)

theorem good_mul {f g : PowerSeries ℚ_[p]} (hf : Good p f) (hg : Good p g) :
    Good p (f*g) := by
  refine ⟨mul_mem hf.1 hg.1, ?_⟩
  rw [B_mul _ p (Fact.out : p.Prime)]
  exact sub_mem (add_mem (add_mem (mul_mem hf.2 hg.1) (mul_mem hf.1 hg.2))
    (middle_mem p _ hf.1 hg.1)) (middle_mem p _ hf.1 hg.1)

theorem good_pow {f : PowerSeries ℚ_[p]} (hf : Good p f) (n : ℕ) : Good p (f^n) := by
  induction n with
  | zero => simpa using good_const p (one_mem (PadicInt.subring p))
  | succ n ih => rw [pow_succ]; exact good_mul p ih hf

theorem good_y : Good p (1+X:PowerSeries ℚ_[p]) := by
  constructor
  · exact add_mem (one_mem _) (WeightedAmice.X_mem p)
  · have he : B (theta p) p (1+X:PowerSeries ℚ_[p])=0 := by simpa using B_y_power p 1
    rw [he]
    exact zero_mem _

theorem good_X : Good p (X:PowerSeries ℚ_[p]) := by
  have h := good_add p (good_y p) (good_neg p (good_const p (one_mem (PadicInt.subring p))))
  simpa using h

/-- The divided generator T^p/p is weighted, even though it is not ordinarily integral. -/
def dividedGenerator : PowerSeries ℚ_[p] := C ((p:ℚ_[p])⁻¹)*X^p

theorem dividedGenerator_mem : dividedGenerator p∈WeightedAmice.ring p := by
  rw [dividedGenerator, ←monomial_eq_C_mul_X_pow]
  apply WeightedAmice.monomial_mem
  simp [Nat.div_self (Fact.out : p.Prime).pos, (Fact.out : p.Prime).ne_zero]

theorem divided_y_defect_mem (k : ℕ) :
    B (theta p) p ((p:ℚ_[p])⁻¹ • (1+X:PowerSeries ℚ_[p])^k)∈WeightedAmice.ring p := by
  rw [map_smul, B_y_power, smul_smul, PowerSeries.smul_eq_C_mul]
  exact mul_mem (WeightedAmice.constant_mem p (FrobeniusSquare.normalized_defect_integral p k))
    (pow_mem (good_y p).1 k)

/-- The finite binomial expansion is an identity in the actual power-series ring. -/
theorem X_binomial (d : ℕ) : (X:PowerSeries ℚ_[p])^d =
    ∑ k∈Finset.range (d+1), (((d.choose k:ℚ_[p])*(-1:ℚ_[p])^(d-k))) •
      (1+X:PowerSeries ℚ_[p])^k := by
  have h := add_pow (1+X:PowerSeries ℚ_[p]) (-1) d
  have he : (1+X:PowerSeries ℚ_[p])+(-1)=X := by ring
  rw [he] at h
  rw [h]
  apply Finset.sum_congr rfl
  intro k _
  simp [PowerSeries.smul_eq_C_mul]
  ring

theorem good_dividedGenerator : Good p (dividedGenerator p) := by
  refine ⟨dividedGenerator_mem p, ?_⟩
  rw [dividedGenerator, ←PowerSeries.smul_eq_C_mul, X_binomial, Finset.smul_sum, map_sum]
  apply (WeightedAmice.ring p).sum_mem
  intro k _
  have h := divided_y_defect_mem p k
  have hc : ((p.choose k:ℚ_[p])*(-1:ℚ_[p])^(p-k))∈PadicInt.subring p :=
    mul_mem (natCast_mem _ _) (pow_mem (neg_mem (one_mem _)) _)
  rw [smul_comm, map_smul, PowerSeries.smul_eq_C_mul]
  exact mul_mem (WeightedAmice.constant_mem p hc) h

theorem monomial_factorization (n : ℕ) (a : ℚ_[p]) :
    C ((p:ℚ_[p])^(n/p)*a)*(dividedGenerator p)^(n/p)*X^(n%p) = monomial n a := by
  have hp : (p:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Fact.out : p.Prime).ne_zero
  have he : (p:ℚ_[p])^(n/p)*a*((p:ℚ_[p])⁻¹)^(n/p)=a := by
    rw [inv_pow]
    field_simp
  calc
    _ = C (((p:ℚ_[p])^(n/p)*a)*((p:ℚ_[p])⁻¹)^(n/p)) * X^(p*(n/p)+n%p) := by
      rw [dividedGenerator, mul_pow, ←map_pow, ←pow_mul, pow_add]
      simp only [map_mul]
      ring
    _ = C a*X^n := by rw [he, Nat.div_add_mod]
    _ = monomial n a := (monomial_eq_C_mul_X_pow _ _).symm

theorem good_monomial (n : ℕ) (a : ℚ_[p])
    (ha : (p:ℚ_[p])^(n/p)*a∈PadicInt.subring p) : Good p (monomial n a) := by
  rw [←monomial_factorization p n a]
  exact good_mul p (good_mul p (good_const p ha) (good_pow p (good_dividedGenerator p) _))
    (good_pow p (good_X p) _)

theorem theta_coeff (f : PowerSeries ℚ_[p]) (n : ℕ) :
    coeff n (theta p f)=(n+1:ℚ_[p])*coeff (n+1) f+(n:ℚ_[p])*coeff n f := by
  rw [theta_apply, add_mul, one_mul, map_add]
  cases n with
  | zero => simp [coeff_derivative, mul_comm]
  | succ n =>
    rw [coeff_succ_X_mul, coeff_derivative, coeff_derivative]
    push_cast
    ring

/-- Finite coefficient dependence of the actual iterated differential operator. -/
theorem deriv_prefix (s n : ℕ) (f g : PowerSeries ℚ_[p])
    (h : ∀ d≤n+s, coeff d f=coeff d g) :
    coeff n (deriv (theta p) s f)=coeff n (deriv (theta p) s g) := by
  induction s generalizing n with
  | zero => exact h n (by omega)
  | succ s ih =>
    rw [deriv_succ, deriv_succ, theta_coeff, theta_coeff,
      ih (n+1) (by intro d hd; apply h; omega), ih n (by intro d hd; apply h; omega)]

theorem B_prefix (n : ℕ) (f g : PowerSeries ℚ_[p])
    (h : ∀ d≤n+p^2, coeff d f=coeff d g) :
    coeff n (B (theta p) p f)=coeff n (B (theta p) p g) := by
  have hp : p≤p^2 := by have := (Fact.out : p.Prime).one_lt; nlinarith
  simp only [B, LinearMap.smul_apply, LinearMap.sub_apply, coeff_smul, map_sub]
  rw [deriv_prefix p (p^2) n f g h,
    deriv_prefix p p n f g (by intro d hd; apply h; omega)]

/-- The normalized Frobenius defect preserves the entire weighted formal-series ring. -/
theorem B_mem (f : PowerSeries ℚ_[p]) (hf : f∈WeightedAmice.ring p) :
    B (theta p) p f∈WeightedAmice.ring p := by
  intro n
  let g : PowerSeries ℚ_[p] := ∑ d∈Finset.range (n+p^2+1), monomial d (coeff d f)
  have hg : Good p g := good_sum p _ _ (by intro d _; exact good_monomial p d _ (hf d))
  have he : ∀ d≤n+p^2, coeff d f=coeff d g := by
    intro d hd
    dsimp [g]
    simp only [map_sum, coeff_monomial]
    simp [Finset.mem_range.mpr (by omega : d<n+p^2+1)]
  rw [B_prefix p n f g he]
  exact hg.2 n

theorem B_iter_mem (s : ℕ) (f : PowerSeries ℚ_[p]) (hf : f∈WeightedAmice.ring p) :
    (B (theta p) p ^ s) f∈WeightedAmice.ring p := by
  induction s with
  | zero => exact hf
  | succ s ih => rw [pow_succ', Module.End.mul_apply]; exact B_mem p _ ih

end KomorebiPaperIX.ThetaWeighted
