import Mathlib.RingTheory.PowerSeries.Expand
import Mathlib.Tactic.Ring
import Lean.Elab.Tactic.Omega

/-!
# Cartier digit sections on complete formal power series

The digit-product theorem uses only a commutative coefficient ring, a nonzero
radix and an in-range digit. Coefficient induction proves it without truncation,
convergence, or a characteristic hypothesis.
-/
namespace KomorebiPadic

variable {R : Type*} [CommRing R]

/-- Extract coefficients at indices p*n+d. Meaningful as a digit when d<p. -/
noncomputable def cartierSection (p d : ℕ) : PowerSeries R →ₗ[R] PowerSeries R where
  toFun F := PowerSeries.mk (fun n => PowerSeries.coeff (p*n+d) F)
  map_add' F G := by ext n; simp
  map_smul' a F := by ext n; simp

@[simp] theorem coeff_cartierSection (p d n : ℕ) (F : PowerSeries R) :
    PowerSeries.coeff n (cartierSection p d F) = PowerSeries.coeff (p*n+d) F := by
  simp [cartierSection]

@[simp] theorem cartierSection_mul_C (p d : ℕ) (F : PowerSeries R) (a : R) :
    cartierSection p d (F * PowerSeries.C a) = cartierSection p d F * PowerSeries.C a := by
  ext n
  simp

/-- Multiplication by X^p shifts every in-range digit section by one. -/
theorem cartierSection_X_pow_mul {p d : ℕ} (hd : d < p) (F : PowerSeries R) :
    cartierSection p d (PowerSeries.X ^ p * F) =
      PowerSeries.X * cartierSection p d F := by
  ext n
  cases n with
  | zero => simp [PowerSeries.coeff_X_pow_mul', Nat.not_le.mpr hd]
  | succ n =>
    rw [coeff_cartierSection, PowerSeries.coeff_succ_X_mul, coeff_cartierSection]
    have hi : p * (n + 1) + d = (p*n+d) + p := by ring
    rw [hi, PowerSeries.coeff_X_pow_mul]

/-- Split a product into its constant-coefficient and shifted-tail contributions. -/
theorem series_mul_tail (H G : PowerSeries R) :
    H * G = PowerSeries.X * (H * PowerSeries.mk (fun n => PowerSeries.coeff (n+1) G)) +
      H * PowerSeries.C (PowerSeries.constantCoeff G) := by
  calc
    H * G = H * (PowerSeries.X * PowerSeries.mk (fun n => PowerSeries.coeff (n+1) G) +
        PowerSeries.C (PowerSeries.constantCoeff G)) :=
      congrArg (H * ·) (PowerSeries.eq_X_mul_shift_add_const G)
    _ = _ := by ring

/-- Same decomposition after exponent expansion of the right factor. -/
theorem series_mul_expand_tail (p : ℕ) (hp : p ≠ 0) (H G : PowerSeries R) :
    H * PowerSeries.expand p hp G =
      PowerSeries.X ^ p * (H * PowerSeries.expand p hp
        (PowerSeries.mk (fun n => PowerSeries.coeff (n+1) G))) +
      H * PowerSeries.C (PowerSeries.constantCoeff G) := by
  calc
    H * PowerSeries.expand p hp G = H * PowerSeries.expand p hp
        (PowerSeries.X * PowerSeries.mk (fun n => PowerSeries.coeff (n+1) G) +
          PowerSeries.C (PowerSeries.constantCoeff G)) :=
      congrArg (fun F => H * PowerSeries.expand p hp F)
        (PowerSeries.eq_X_mul_shift_add_const G)
    _ = _ := by rw [map_add, map_mul, PowerSeries.expand_X, PowerSeries.expand_C]; ring

/-- The Cartier product law is a full series identity over any commutative ring. -/
theorem cartierSection_mul_expand {p d : ℕ} (hp : p ≠ 0) (hd : d < p)
    (H G : PowerSeries R) :
    cartierSection p d (H * PowerSeries.expand p hp G) = cartierSection p d H * G := by
  apply PowerSeries.ext
  intro n
  induction n generalizing G with
  | zero =>
    rw [series_mul_expand_tail, map_add, cartierSection_X_pow_mul hd, cartierSection_mul_C]
    simp
  | succ n ih =>
    rw [series_mul_expand_tail, map_add, cartierSection_X_pow_mul hd, cartierSection_mul_C]
    conv_rhs => rw [series_mul_tail]
    simp only [map_add, PowerSeries.coeff_succ_X_mul, PowerSeries.coeff_mul_C]
    rw [ih]

/-- Digit zero is a left inverse to exponent expansion. -/
@[simp] theorem cartierSection_zero_expand (p : ℕ) (hp : p ≠ 0) (F : PowerSeries R) :
    cartierSection p 0 (PowerSeries.expand p hp F) = F := by
  ext n
  simp

/-- All in-range sections jointly determine the entire formal series. -/
theorem cartierSection_joint_injective {p : ℕ} (hp : 0 < p)
    {F G : PowerSeries R} (h : ∀ d, d < p → cartierSection p d F = cartierSection p d G) :
    F = G := by
  ext n
  have hn := congrArg (PowerSeries.coeff (n / p)) (h (n % p) (Nat.mod_lt n hp))
  simpa only [coeff_cartierSection, Nat.div_add_mod] using hn

/-- A series vanishes iff all its in-range digit sections vanish. -/
theorem cartierSection_all_zero_iff {p : ℕ} (hp : 0 < p) (F : PowerSeries R) :
    (∀ d, d < p → cartierSection p d F = 0) ↔ F = 0 := by
  constructor
  · intro h
    apply cartierSection_joint_injective hp
    simpa using h
  · rintro rfl
    simp

/-- Coefficient output is the constant coefficient after the corresponding section. -/
@[simp] theorem constantCoeff_cartierSection (p d : ℕ) (F : PowerSeries R) :
    PowerSeries.constantCoeff (cartierSection p d F) = PowerSeries.coeff d F := by
  rw [← PowerSeries.coeff_zero_eq_constantCoeff, coeff_cartierSection]
  simp

end KomorebiPadic
