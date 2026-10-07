import KomorebiPadic.FrobeniusDefect
import KomorebiPadic.ConcreteBinomialModel
import Mathlib.RingTheory.Polynomial.Content
import Mathlib.Algebra.GCDMonoid.Nat
import Mathlib.NumberTheory.Padics.PadicVal.Basic

/-!
# Exact polynomial branch valuation and the checked edge model

The order of a nonzero integer polynomial is the p-adic order of its content.
Zero is handled separately by vanishing predicates, not assigned infinite order
inside a natural-number value. The branch theorem applies BEFORE Cartier section
and BEFORE adding different branches; neither operation is asserted cancellation-free.
-/
namespace KomorebiPadic
open Polynomial

/-- Natural-valued content order. Like padicValInt, the value at zero is 0. -/
noncomputable def polynomialPadicOrder (p : ℕ) (P : ℤ[X]) : ℕ :=
  padicValInt p P.content

/-- Exact coefficientwise divisibility, with zero explicitly separated. -/
theorem polynomialVanishing_iff_zero_or_le {p : ℕ} (hp : p.Prime)
    (r : ℕ) (P : ℤ[X]) :
    PolynomialVanishing p r P ↔ P = 0 ∨ r ≤ polynomialPadicOrder p P := by
  let : Fact p.Prime := ⟨hp⟩
  rw [PolynomialVanishing, ← C_dvd_iff_dvd_coeff, ← dvd_content_iff_C_dvd,
    padicValInt_dvd_iff]
  simp only [content_eq_zero_iff, polynomialPadicOrder]

/-- On nonzero polynomials, divisibility is exactly the order inequality. -/
theorem polynomialVanishing_iff_le_order {p : ℕ} (hp : p.Prime)
    (r : ℕ) (P : ℤ[X]) (hP : P ≠ 0) :
    PolynomialVanishing p r P ↔ r ≤ polynomialPadicOrder p P := by
  simp only [polynomialVanishing_iff_zero_or_le hp, hP, false_or]

/-- A nonzero integer polynomial is zero modulo p^r exactly at or above precision r. -/
theorem polynomial_map_eq_zero_iff_order {p : ℕ} (hp : p.Prime)
    (r : ℕ) (P : ℤ[X]) (hP : P ≠ 0) :
    P.map (Int.castRingHom (ZMod (p ^ r))) = 0 ↔ r ≤ polynomialPadicOrder p P := by
  rw [← polynomialVanishing_iff_map_zero, polynomialVanishing_iff_le_order hp r P hP]

/-- Gauss content multiplicativity supplies the exact product order. -/
theorem polynomialPadicOrder_mul {p : ℕ} (hp : p.Prime)
    (P Q : ℤ[X]) (hP : P ≠ 0) (hQ : Q ≠ 0) :
    polynomialPadicOrder p (P * Q) = polynomialPadicOrder p P + polynomialPadicOrder p Q := by
  let : Fact p.Prime := ⟨hp⟩
  simp only [polynomialPadicOrder, content_mul]
  exact padicValInt.mul (content_eq_zero_iff.not.mpr hP) (content_eq_zero_iff.not.mpr hQ)

@[simp] theorem polynomialPadicOrder_C (p : ℕ) (a : ℤ) :
    polynomialPadicOrder p (C a) = padicValInt p a := by
  rw [polynomialPadicOrder, content_C]
  simp only [padicValInt, ← Int.abs_eq_normalize, Int.natAbs_abs]

@[simp] theorem polynomialPadicOrder_one (p : ℕ) :
    polynomialPadicOrder p (1 : ℤ[X]) = 0 := by
  simp [polynomialPadicOrder]

/-- Exact powers of a nonzero polynomial; the exponent may be zero. -/
theorem polynomialPadicOrder_pow {p : ℕ} (hp : p.Prime)
    (P : ℤ[X]) (hP : P ≠ 0) (k : ℕ) :
    polynomialPadicOrder p (P ^ k) = k * polynomialPadicOrder p P := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [pow_succ, polynomialPadicOrder_mul hp _ _ (pow_ne_zero _ hP) hP, ih]
    ring

/-- Integer polynomial weight of one negative-binomial correction branch. -/
noncomputable def cartierBranchWeight (p q k : ℕ) (E : ℤ[X]) : ℤ[X] :=
  C ((-1 : ℤ) ^ k) * C (((q + k - 1).choose k : ℕ) : ℤ) * C ((p : ℤ) ^ k) * E ^ k

/-- Nonzero defect and positive quotient ensure the branch polynomial is nonzero over Z. -/
theorem cartierBranchWeight_ne_zero {p q : ℕ} (hp : p.Prime) (hq : 0 < q)
    (k : ℕ) (E : ℤ[X]) (hE : E ≠ 0) : cartierBranchWeight p q k E ≠ 0 := by
  have hc : (q + k - 1).choose k ≠ 0 := Nat.choose_ne_zero (by omega)
  simp [cartierBranchWeight, hc, hp.ne_zero, hE]

/-- Exact branch-content formula. No polynomial valuation identity is assumed. -/
theorem cartierBranchWeight_order {p q : ℕ} (hp : p.Prime) (hq : 0 < q)
    (k : ℕ) (E : ℤ[X]) (hE : E ≠ 0) :
    polynomialPadicOrder p (cartierBranchWeight p q k E) =
      branchCost (polynomialPadicOrder p E) k (padicValNat p ((q + k - 1).choose k)) := by
  let : Fact p.Prime := ⟨hp⟩
  have hc : (q + k - 1).choose k ≠ 0 := Nat.choose_ne_zero (by omega)
  have hs : C ((-1 : ℤ) ^ k) ≠ (0 : ℤ[X]) := by simp
  have hn : C (((q + k - 1).choose k : ℕ) : ℤ) ≠ (0 : ℤ[X]) := by simpa using hc
  have hpw : C ((p : ℤ) ^ k) ≠ (0 : ℤ[X]) := by simp [hp.ne_zero]
  unfold cartierBranchWeight
  rw [polynomialPadicOrder_mul hp _ _ (mul_ne_zero (mul_ne_zero hs hn) hpw) (pow_ne_zero _ hE),
    polynomialPadicOrder_mul hp _ _ (mul_ne_zero hs hn) hpw,
    polynomialPadicOrder_mul hp _ _ hs hn,
    polynomialPadicOrder_C, polynomialPadicOrder_C, polynomialPadicOrder_C,
    polynomialPadicOrder_pow hp E hE]
  simp [padicValInt, branchCost]
  ring

/-- The pre-section polynomial survives modulo p^r iff the existing ActiveAt predicate holds. -/
theorem cartierBranchWeight_survives_iff_activeAt {p q : ℕ}
    (hp : p.Prime) (hq : 0 < q) (r k : ℕ) (E : ℤ[X]) (hE : E ≠ 0) :
    (cartierBranchWeight p q k E).map (Int.castRingHom (ZMod (p ^ r))) ≠ 0 ↔
      ActiveAt r (polynomialPadicOrder p E) k (padicValNat p ((q + k - 1).choose k)) := by
  rw [ne_eq, polynomial_map_eq_zero_iff_order hp r _ (cartierBranchWeight_ne_zero hp hq k E hE),
    cartierBranchWeight_order hp hq k E hE, Nat.not_le]
  rfl

/-- Concrete bridge to the inherited valuation-edge definition, without changing that model. -/
theorem frobeniusBranch_survives_iff_valuationEdge {p q : ℕ}
    (hp : p.Prime) (hq : 0 < q) (r k : ℕ) (B : ℤ[X])
    (hE : frobeniusDefect p B ≠ 0) :
    (cartierBranchWeight p q k (frobeniusDefect p B)).map
        (Int.castRingHom (ZMod (p ^ r))) ≠ 0 ↔
      valuationEdge (binomialPadicModel p hp.one_lt) r
        (polynomialPadicOrder p (frobeniusDefect p B)) q k := by
  exact cartierBranchWeight_survives_iff_activeAt hp hq r k _ hE

/-- Zero defect has no positive-order corrections, at any base or precision. -/
theorem cartierBranchWeight_zero_defect (p q k : ℕ) (hk : 0 < k) :
    cartierBranchWeight p q k (0 : ℤ[X]) = 0 := by
  simp [cartierBranchWeight, hk.ne']

/-- A p-unit constant term ensures nonzero polynomial content of order zero. -/
theorem polynomial_constant_unit_order {p : ℕ} (hp : p.Prime) (P : ℤ[X])
    (hunit : ¬ (p : ℤ) ∣ P.coeff 0) :
    P ≠ 0 ∧ polynomialPadicOrder p P = 0 := by
  have hn : P ≠ 0 := by intro hz; apply hunit; simp [hz]
  have hv : ¬ PolynomialVanishing p 1 P := by
    intro h
    exact hunit (by simpa only [pow_one] using h 0)
  rw [polynomialVanishing_iff_le_order hp 1 P hn] at hv
  exact ⟨hn, by omega⟩

/-- Multiplication by an integer polynomial with p-unit constant coefficient does
not change the exact content order of a nonzero branch. -/
theorem preCartierKernel_order {p q : ℕ} (hp : p.Prime) (hq : 0 < q)
    (k t : ℕ) (A B E : ℤ[X]) (hA : ¬ (p : ℤ) ∣ A.coeff 0)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hE : E ≠ 0) :
    polynomialPadicOrder p (A * B ^ t * cartierBranchWeight p q k E) =
      branchCost (polynomialPadicOrder p E) k (padicValNat p ((q + k - 1).choose k)) := by
  obtain ⟨ha, ha0⟩ := polynomial_constant_unit_order hp A hA
  obtain ⟨hb, hb0⟩ := polynomial_constant_unit_order hp B hB
  rw [polynomialPadicOrder_mul hp _ _ (mul_ne_zero ha (pow_ne_zero _ hb))
      (cartierBranchWeight_ne_zero hp hq k E hE),
    polynomialPadicOrder_mul hp _ _ ha (pow_ne_zero _ hb),
    polynomialPadicOrder_pow hp B hb, ha0, hb0,
    cartierBranchWeight_order hp hq k E hE]
  simp

/-- Exact kernel pruning before Cartier digit extraction and before branch addition. -/
theorem preCartierKernel_survives_iff_activeAt {p q : ℕ} (hp : p.Prime) (hq : 0 < q)
    (r k t : ℕ) (A B E : ℤ[X]) (hA : ¬ (p : ℤ) ∣ A.coeff 0)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hE : E ≠ 0) :
    (A * B ^ t * cartierBranchWeight p q k E).map
        (Int.castRingHom (ZMod (p ^ r))) ≠ 0 ↔
      ActiveAt r (polynomialPadicOrder p E) k (padicValNat p ((q + k - 1).choose k)) := by
  have ha := (polynomial_constant_unit_order hp A hA).1
  have hb := (polynomial_constant_unit_order hp B hB).1
  rw [ne_eq, polynomial_map_eq_zero_iff_order hp r _
      (mul_ne_zero (mul_ne_zero ha (pow_ne_zero _ hb)) (cartierBranchWeight_ne_zero hp hq k E hE)),
    preCartierKernel_order hp hq k t A B E hA hB hE, Nat.not_le]
  rfl

/-- Highest unchanged Frobenius-congruence precision for nonzero defect. This
polynomial criterion is not yet identified with all Cartier digit sections. -/
theorem frobeniusDefect_congruence_depth {p : ℕ} (hp : p.Prime) (B : ℤ[X]) (s : ℕ)
    (hE : frobeniusDefect p B ≠ 0) :
    (B ^ p).map (Int.castRingHom (ZMod (p ^ (s + 1)))) =
      (expand ℤ p B).map (Int.castRingHom (ZMod (p ^ (s + 1)))) ↔
      s ≤ polynomialPadicOrder p (frobeniusDefect p B) := by
  rw [frobeniusDefect_congruence_iff hp B s, polynomialVanishing_iff_le_order hp s _ hE]

end KomorebiPadic
