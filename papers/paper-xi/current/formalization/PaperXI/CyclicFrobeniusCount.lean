import PaperXI.FrobeniusPeriodCount
import Mathlib.GroupTheory.SpecificGroups.Cyclic
import Mathlib.Data.Nat.GCD.Basic

/-! Fixed points and regular orbit counts for the power map on a finite cyclic
 group. No fixed-point cardinality is assumed. -/
set_option autoImplicit false
namespace PaperXI.CyclicFrobeniusCount
open Function Finset PaperXI.FrobeniusPeriodCount
open scoped Classical

variable {G : Type*} [CommGroup G] [Finite G] [IsCyclic G]

omit [Finite G] [IsCyclic G] in
/-- Iteration of the qth-power map is the q^r-th-power map. -/
theorem iterate_power (q r : ℕ) (x : G) :
    (fun y : G => y ^ q)^[r] x = x ^ (q ^ r) := by
  induction r with
  | zero => simp
  | succ r ih => simp [Function.iterate_succ_apply', ih, pow_succ, pow_mul]

omit [Finite G] [IsCyclic G] in
/-- Fixed points are the actual kernel of the (q^r-1)th-power homomorphism. -/
theorem fixed_iff_kernel (q r : ℕ) (hq : 0 < q) (x : G) :
    IsPeriodicPt (fun y : G => y ^ q) r x ↔
      x ∈ (powMonoidHom (q ^ r - 1) : G →* G).ker := by
  have hp : 1 ≤ q ^ r := Nat.one_le_pow r q hq
  change (fun y : G => y ^ q)^[r] x = x ↔ x ^ (q ^ r - 1) = 1
  rw [iterate_power]
  have he : x ^ (q ^ r - 1) * x = x ^ (q ^ r) := by
    rw [← pow_succ, Nat.sub_add_cancel hp]
  constructor
  · intro h
    apply mul_right_cancel (b := x)
    simpa only [one_mul, he] using h
  · intro h
    simpa only [h, one_mul] using he.symm

/-- The fixed-point count is a kernel cardinality, hence a greatest common divisor. -/
theorem fixedCount_gcd (q r : ℕ) (hq : 0 < q) :
    fixedCount (fun y : G => y ^ q) r = (Nat.card G).gcd (q ^ r - 1) := by
  calc
    _ = Nat.card (powMonoidHom (q ^ r - 1) : G →* G).ker :=
      Nat.card_congr (Equiv.subtypeEquivRight (fixed_iff_kernel q r hq))
    _ = _ := IsCyclic.card_powMonoidHom_ker G _

/-- Stronger fixed-point formula, valid for every iterate r, not just r dividing n. -/
theorem fixedCount_pow_gcd (q n r : ℕ) (hq : 0 < q)
    (hc : Nat.card G = q ^ n - 1) :
    fixedCount (fun y : G => y ^ q) r = q ^ (n.gcd r) - 1 := by
  rw [fixedCount_gcd q r hq, hc, Nat.pow_sub_one_gcd_pow_sub_one]

/-- The divisor fixed-point counts used in the manuscript are now derived. -/
theorem fixedCount_of_dvd (q n r : ℕ) (hq : 0 < q)
    (hc : Nat.card G = q ^ n - 1) (hr : r ∣ n) :
    fixedCount (fun y : G => y ^ q) r = q ^ r - 1 := by
  rw [fixedCount_pow_gcd q n r hq hc, Nat.gcd_eq_right hr]

/-- An integral formula for characters of exact Frobenius period n. -/
theorem exactCount_formula (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) :
    (exactCount (fun y : G => y ^ q) n : ℤ) =
      ∑ d ∈ n.divisors, ArithmeticFunction.moebius d * ((q : ℤ) ^ (n / d) - 1) := by
  rw [moebius_exactCount _ n hn]
  apply sum_congr rfl
  intro d hd
  rw [fixedCount_of_dvd q n (n / d) hq hc (Nat.div_dvd_of_dvd (Nat.mem_divisors.mp hd).1)]
  rw [Nat.cast_sub (Nat.one_le_pow _ q hq), Nat.cast_pow, Nat.cast_one]

omit [CommGroup G] [Finite G] [IsCyclic G] in
/-- The power map is invertible for cyclic groups of order q^n-1. -/
theorem card_coprime_q (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) : (Nat.card G).Coprime q := by
  rw [hc]
  have h : (q ^ n - 1).Coprime (q ^ n) :=
    (Nat.coprime_self_sub_left (Nat.one_le_pow n q hq)).mpr (Nat.coprime_one_left _)
  exact h.of_dvd_right (dvd_pow_self q hn.ne')

noncomputable def frobeniusPerm (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) : Equiv.Perm G :=
  powCoprime (card_coprime_q q n hq hn hc)

omit [Finite G] [IsCyclic G] in
@[simp] theorem frobeniusPerm_apply (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) (x : G) :
    frobeniusPerm q n hq hn hc x = x ^ q := rfl

/-- The actual regular-orbit count times n equals the integral Möbius sum. -/
theorem orbitCount_mul_formula (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) :
    (orbitCount (frobeniusPerm q n hq hn hc) n : ℤ) * n =
      ∑ d ∈ n.divisors, ArithmeticFunction.moebius d * ((q : ℤ) ^ (n / d) - 1) := by
  have h := exactCount_eq_orbitCount_mul (frobeniusPerm q n hq hn hc) n
  have he : (exactCount (fun y : G => y ^ q) n : ℤ) =
      (orbitCount (frobeniusPerm q n hq hn hc) n : ℤ) * n := by
    exact_mod_cast h
  exact he.symm.trans (exactCount_formula q n hq hn hc)

/-- The numerator is divisible by n because it counts a disjoint union of n-cycles. -/
theorem moebius_sum_dvd (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) :
    (n : ℤ) ∣ ∑ d ∈ n.divisors,
      ArithmeticFunction.moebius d * ((q : ℤ) ^ (n / d) - 1) := by
  rw [← orbitCount_mul_formula q n hq hn hc]
  exact dvd_mul_left _ _

/-- Rational display of the manuscript's formula, with actual quotient cardinality. -/
theorem orbitCount_formula (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hc : Nat.card G = q ^ n - 1) :
    (orbitCount (frobeniusPerm q n hq hn hc) n : ℚ) =
      (1 / (n : ℚ)) * ∑ d ∈ n.divisors,
        (ArithmeticFunction.moebius d : ℚ) * ((q : ℚ) ^ (n / d) - 1) := by
  have h : (orbitCount (frobeniusPerm q n hq hn hc) n : ℚ) * n =
      ∑ d ∈ n.divisors, (ArithmeticFunction.moebius d : ℚ) * ((q : ℚ) ^ (n / d) - 1) := by
    exact_mod_cast orbitCount_mul_formula q n hq hn hc
  have hnq : (n : ℚ) ≠ 0 := by exact_mod_cast hn.ne'
  apply (eq_div_iff hnq).mpr h |>.trans
  ring

end PaperXI.CyclicFrobeniusCount
