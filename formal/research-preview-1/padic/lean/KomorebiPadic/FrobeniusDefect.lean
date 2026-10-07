import Mathlib.Algebra.Polynomial.Expand
import Mathlib.FieldTheory.Finite.Basic

/-!
# Integral Frobenius defect

The integer polynomial is constructed by coefficientwise exact division, not
postulated. Prime-field reduction proves that every coefficient is divisible by p.
No unit constant term is needed for this integral polynomial identity.
-/
namespace KomorebiPadic
open Polynomial

/-- Coefficientwise integer division. Totalized at a zero divisor as in `Int.ediv`. -/
noncomputable def polynomialCoefficientQuotient (m : ℤ) (P : ℤ[X]) : ℤ[X] :=
  .ofFinsupp ⟨P.coeff.mapRange (fun a => a / m) (by simp)⟩

@[simp] theorem polynomialCoefficientQuotient_coeff (m : ℤ) (P : ℤ[X]) (n : ℕ) :
    (polynomialCoefficientQuotient m P).coeff n = P.coeff n / m := rfl

/-- The numerator before dividing out the characteristic prime. -/
noncomputable def frobeniusDefectNumerator (p : ℕ) (B : ℤ[X]) : ℤ[X] :=
  B ^ p - expand ℤ p B

/-- Canonical integral Frobenius defect, defined for all natural p. Its intended
identity is proved below with the explicit prime hypothesis. -/
noncomputable def frobeniusDefect (p : ℕ) (B : ℤ[X]) : ℤ[X] :=
  polynomialCoefficientQuotient (p : ℤ) (frobeniusDefectNumerator p B)

/-- Prime-field Frobenius agrees with exponent expansion. -/
theorem polynomial_expand_zmod {p : ℕ} (hp : p.Prime) (f : (ZMod p)[X]) :
    expand (ZMod p) p f = f ^ p := by
  let : Fact p.Prime := ⟨hp⟩
  simpa only [ZMod.frobenius_zmod, Polynomial.map_id] using
    (Polynomial.map_frobenius_expand p f)

/-- The defect numerator vanishes under reduction modulo the prime. -/
theorem frobeniusDefectNumerator_map_zero {p : ℕ} (hp : p.Prime) (B : ℤ[X]) :
    (frobeniusDefectNumerator p B).map (Int.castRingHom (ZMod p)) = 0 := by
  simp only [frobeniusDefectNumerator, Polynomial.map_sub, Polynomial.map_pow,
    Polynomial.map_expand, polynomial_expand_zmod hp, sub_self]

/-- Integrality is established coefficient by coefficient, without an assumed defect. -/
theorem frobeniusDefectNumerator_coeff_dvd {p : ℕ} (hp : p.Prime)
    (B : ℤ[X]) (n : ℕ) : (p : ℤ) ∣ (frobeniusDefectNumerator p B).coeff n := by
  apply (ZMod.intCast_zmod_eq_zero_iff_dvd _ p).mp
  have hc := congrArg (fun P : (ZMod p)[X] => P.coeff n)
    (frobeniusDefectNumerator_map_zero hp B)
  simpa using hc

/-- Exact division reconstructs the original numerator. -/
theorem frobeniusDefect_mul_prime {p : ℕ} (hp : p.Prime) (B : ℤ[X]) :
    C (p : ℤ) * frobeniusDefect p B = frobeniusDefectNumerator p B := by
  ext n
  simp only [coeff_C_mul, frobeniusDefect, polynomialCoefficientQuotient_coeff]
  exact Int.mul_ediv_cancel' (frobeniusDefectNumerator_coeff_dvd hp B n)

/-- Integral identity `B(z)^p = B(z^p) + p E_B(z)`. -/
theorem frobeniusDefect_identity {p : ℕ} (hp : p.Prime) (B : ℤ[X]) :
    B ^ p = expand ℤ p B + C (p : ℤ) * frobeniusDefect p B := by
  rw [frobeniusDefect_mul_prime hp B]
  simp [frobeniusDefectNumerator]

/-- Same identity with literal polynomial substitution. -/
theorem frobeniusDefect_comp_identity {p : ℕ} (hp : p.Prime) (B : ℤ[X]) :
    B ^ p = B.comp (X ^ p) + C (p : ℤ) * frobeniusDefect p B := by
  simpa only [Polynomial.expand_eq_comp_X_pow] using frobeniusDefect_identity hp B

/-- The integral defect is unique, since p is nonzero in the integer polynomial ring. -/
theorem frobeniusDefect_unique {p : ℕ} (hp : p.Prime) (B E : ℤ[X])
    (he : B ^ p = expand ℤ p B + C (p : ℤ) * E) : E = frobeniusDefect p B := by
  apply mul_left_cancel₀ (show C (p : ℤ) ≠ 0 by simp [hp.ne_zero])
  have h := frobeniusDefect_identity hp B
  exact add_left_cancel (he.symm.trans h)

/-- Explicit coefficients of the unique defect. -/
theorem frobeniusDefect_coeff (p : ℕ) (B : ℤ[X]) (n : ℕ) :
    (frobeniusDefect p B).coeff n =
      ((B ^ p).coeff n - (expand ℤ p B).coeff n) / (p : ℤ) := by
  simp [frobeniusDefect, frobeniusDefectNumerator]

/-- Coefficientwise vanishing modulo p^r; unlike a valuation, this handles zero directly. -/
def PolynomialVanishing (p r : ℕ) (P : ℤ[X]) : Prop :=
  ∀ n, (p : ℤ) ^ r ∣ P.coeff n

/-- Coefficient divisibility agrees exactly with polynomial reduction to Z/(p^r). -/
theorem polynomialVanishing_iff_map_zero (p r : ℕ) (P : ℤ[X]) :
    PolynomialVanishing p r P ↔ P.map (Int.castRingHom (ZMod (p ^ r))) = 0 := by
  simp only [PolynomialVanishing, Polynomial.ext_iff, Polynomial.coeff_map, Polynomial.coeff_zero]
  change (∀ n, (p : ℤ) ^ r ∣ P.coeff n) ↔
    ∀ n, (P.coeff n : ZMod (p ^ r)) = 0
  simp only [ZMod.intCast_zmod_eq_zero_iff_dvd, Int.natCast_pow]

/-- One power of the prime is removed exactly, including the zero-defect case. -/
theorem frobeniusDefect_precision_shift {p : ℕ} (hp : p.Prime) (B : ℤ[X]) (s : ℕ) :
    PolynomialVanishing p (s + 1) (frobeniusDefectNumerator p B) ↔
      PolynomialVanishing p s (frobeniusDefect p B) := by
  rw [← frobeniusDefect_mul_prime hp B]
  simp only [PolynomialVanishing, coeff_C_mul, pow_succ']
  exact forall_congr' (fun _ => Int.mul_dvd_mul_iff_left (by exact_mod_cast hp.ne_zero))

/-- Exact prime-power Frobenius congruence, not yet the full Cartier one-layer theorem. -/
theorem frobeniusDefect_congruence_iff {p : ℕ} (hp : p.Prime) (B : ℤ[X]) (s : ℕ) :
    (B ^ p).map (Int.castRingHom (ZMod (p ^ (s + 1)))) =
      (expand ℤ p B).map (Int.castRingHom (ZMod (p ^ (s + 1)))) ↔
    PolynomialVanishing p s (frobeniusDefect p B) := by
  rw [← frobeniusDefect_precision_shift hp B s, polynomialVanishing_iff_map_zero]
  simp only [frobeniusDefectNumerator, Polynomial.map_sub, sub_eq_zero]

/-- Defect vanishing is equivalent to the exact characteristic-zero identity. -/
theorem frobeniusDefect_eq_zero_iff {p : ℕ} (hp : p.Prime) (B : ℤ[X]) :
    frobeniusDefect p B = 0 ↔ B ^ p = expand ℤ p B := by
  constructor
  · intro h
    simpa [h] using frobeniusDefect_identity hp B
  · intro h
    apply (frobeniusDefect_unique hp B 0 (by simpa using h)).symm

/-- Multiplicative compatibility of the canonical defect. -/
theorem frobeniusDefect_mul {p : ℕ} (hp : p.Prime) (A B : ℤ[X]) :
    frobeniusDefect p (A * B) =
      expand ℤ p A * frobeniusDefect p B + expand ℤ p B * frobeniusDefect p A +
        C (p : ℤ) * frobeniusDefect p A * frobeniusDefect p B := by
  symm
  apply frobeniusDefect_unique hp (A * B)
  rw [mul_pow, map_mul, frobeniusDefect_identity hp A, frobeniusDefect_identity hp B]
  ring

/-- The prime hypothesis cannot be omitted: the middle coefficient is 6, not divisible by 4. -/
theorem composite_four_has_no_integral_defect :
    ¬ ∃ E : ℤ[X], (1 + X) ^ 4 = expand ℤ 4 (1 + X) + C (4 : ℤ) * E := by
  rintro ⟨E, h⟩
  have hc := congrArg (fun P : ℤ[X] => P.coeff 2) h
  norm_num [Polynomial.coeff_one_add_X_pow, map_add, Polynomial.expand_X,
    coeff_add, coeff_C_mul, Polynomial.coeff_one] at hc
  have hchoose : Nat.choose 4 2 = 6 := by decide
  rw [hchoose] at hc
  norm_num at hc
  omega

end KomorebiPadic
