import RealizationBoundaries.PrimeComputability
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.Data.Rat.Lemmas
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

/-! # Native rational-code arithmetic and total prime reduction -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Positive-minus-negative numerator and positive denominator predecessor.
The carrier is an ordinary native primitive-codable product of naturals. -/
abbrev RationalCode := (ℕ × ℕ) × ℕ
namespace RationalCode

def positive (c : RationalCode) : ℕ := c.1.1
def negative (c : RationalCode) : ℕ := c.1.2
def denominator (c : RationalCode) : ℕ := c.2 + 1
def value (c : RationalCode) : ℚ :=
  mkRat ((positive c : ℤ) - (negative c : ℤ)) (denominator c)

theorem value_eq (c : RationalCode) :
    value c = ((positive c : ℚ) - (negative c : ℚ)) / (denominator c : ℚ) := by
  simp only [value, Rat.mkRat_eq_div, Int.cast_sub, Int.cast_natCast]

theorem denominator_pos (c : RationalCode) : 0 < denominator c := Nat.succ_pos _

theorem value_surjective : Function.Surjective value := by
  intro q
  refine ⟨((q.num.toNat, (-q.num).toNat), q.den - 1), ?_⟩
  unfold value positive negative denominator
  rw [Int.toNat_sub_toNat_neg, Nat.sub_add_cancel q.den_pos, Rat.mkRat_self]

def add (c e : RationalCode) : RationalCode :=
  ((positive c * denominator e + positive e * denominator c,
    negative c * denominator e + negative e * denominator c),
    denominator c * denominator e - 1)

def neg (c : RationalCode) : RationalCode := ((negative c, positive c), c.2)

@[simp] theorem value_add (c e : RationalCode) : value (add c e) = value c + value e := by
  rw [value_eq, value_eq, value_eq]
  have hd : 0 < denominator c * denominator e := Nat.mul_pos (denominator_pos c) (denominator_pos e)
  simp only [add, positive, negative, denominator]
  simp only [denominator] at hd
  rw [Nat.sub_add_cancel hd]
  push_cast
  have hc : (c.2 + 1 : ℚ) ≠ 0 := by positivity
  have he : (e.2 + 1 : ℚ) ≠ 0 := by positivity
  field_simp
  ring

@[simp] theorem value_neg (c : RationalCode) : value (neg c) = -value c := by
  simp only [value_eq, neg, positive, negative, denominator]
  ring

/-- Cross multiplication decides equality of the decoded rational values. -/
def equal (c e : RationalCode) : Bool := decide
  (positive c * denominator e + negative e * denominator c =
    positive e * denominator c + negative c * denominator e)

theorem equal_iff (c e : RationalCode) : equal c e = true ↔ value c = value e := by
  simp only [equal, decide_eq_true_eq, value_eq]
  have hc : (denominator c : ℚ) ≠ 0 := by exact_mod_cast (denominator_pos c).ne'
  have he : (denominator e : ℚ) ≠ 0 := by exact_mod_cast (denominator_pos e).ne'
  rw [div_eq_div_iff hc he]
  constructor
  · intro h
    have h' : (positive c : ℚ) * denominator e + negative e * denominator c =
        positive e * denominator c + negative c * denominator e := by exact_mod_cast h
    nlinarith
  · intro h
    have h' : (positive c : ℚ) * denominator e + negative e * denominator c =
        positive e * denominator c + negative c * denominator e := by nlinarith
    exact_mod_cast h'

theorem primrec_positive : Primrec positive := Primrec.fst.comp Primrec.fst
theorem primrec_negative : Primrec negative := Primrec.snd.comp Primrec.fst
theorem primrec_denominator : Primrec denominator := Primrec.succ.comp Primrec.snd

theorem primrec_add : Primrec₂ add := by
  let a : Primrec (fun p : RationalCode × RationalCode => positive p.1) := primrec_positive.comp Primrec.fst
  let b : Primrec (fun p : RationalCode × RationalCode => negative p.1) := primrec_negative.comp Primrec.fst
  let d : Primrec (fun p : RationalCode × RationalCode => denominator p.1) := primrec_denominator.comp Primrec.fst
  let e : Primrec (fun p : RationalCode × RationalCode => positive p.2) := primrec_positive.comp Primrec.snd
  let f : Primrec (fun p : RationalCode × RationalCode => negative p.2) := primrec_negative.comp Primrec.snd
  let g : Primrec (fun p : RationalCode × RationalCode => denominator p.2) := primrec_denominator.comp Primrec.snd
  exact ((Primrec.nat_add.comp (Primrec.nat_mul.comp a g) (Primrec.nat_mul.comp e d)).pair
    (Primrec.nat_add.comp (Primrec.nat_mul.comp b g) (Primrec.nat_mul.comp f d))).pair
    (Primrec.nat_sub.comp (Primrec.nat_mul.comp d g) (Primrec.const 1))

theorem primrec_neg : Primrec neg :=
  (primrec_negative.pair primrec_positive).pair Primrec.snd

theorem primrec_equal : Primrec₂ equal := by
  let a : Primrec (fun p : RationalCode × RationalCode => positive p.1) := primrec_positive.comp Primrec.fst
  let b : Primrec (fun p : RationalCode × RationalCode => negative p.1) := primrec_negative.comp Primrec.fst
  let d : Primrec (fun p : RationalCode × RationalCode => denominator p.1) := primrec_denominator.comp Primrec.fst
  let e : Primrec (fun p : RationalCode × RationalCode => positive p.2) := primrec_positive.comp Primrec.snd
  let f : Primrec (fun p : RationalCode × RationalCode => negative p.2) := primrec_negative.comp Primrec.snd
  let g : Primrec (fun p : RationalCode × RationalCode => denominator p.2) := primrec_denominator.comp Primrec.snd
  exact (Primrec.eq.comp
    (Primrec.nat_add.comp (Primrec.nat_mul.comp a g) (Primrec.nat_mul.comp f d))
    (Primrec.nat_add.comp (Primrec.nat_mul.comp e d) (Primrec.nat_mul.comp b g))).decide

end RationalCode

/-- Euclid's gcd is native primitive recursive: bounded common-divisor search
returns the same greatest common divisor. The both-zero case is retained. -/
theorem primrec_nat_gcd : Primrec₂ Nat.gcd := by
  have hpred : PrimrecRel (fun p : ℕ × ℕ => fun d : ℕ => d ∣ p.1 ∧ d ∣ p.2) :=
    (primrec_nat_dvd.comp Primrec.snd (Primrec.fst.comp Primrec.fst)).and
      (primrec_nat_dvd.comp Primrec.snd (Primrec.snd.comp Primrec.fst))
  refine (Primrec.nat_findGreatest Primrec.nat_add hpred).of_eq ?_
  intro p
  apply Nat.findGreatest_eq_iff.mpr
  refine ⟨?_, fun _ => ⟨Nat.gcd_dvd_left _ _, Nat.gcd_dvd_right _ _⟩, ?_⟩
  · by_cases hb : p.2 = 0
    · simp [hb]
    · exact (Nat.gcd_le_right p.1 (Nat.pos_of_ne_zero hb)).trans (Nat.le_add_left _ _)
  · intro n hlt hle hn
    have hdn : n ∣ Nat.gcd p.1 p.2 := Nat.dvd_gcd hn.1 hn.2
    by_cases hg : Nat.gcd p.1 p.2 = 0
    · have hz := Nat.gcd_eq_zero_iff.mp hg
      have hsum : p.1 + p.2 = 0 := by simp [hz.1, hz.2]
      change n ≤ p.1 + p.2 at hle
      omega
    · exact (not_lt_of_ge (Nat.le_of_dvd (Nat.pos_of_ne_zero hg) hdn)) hlt

namespace RationalCode

def magnitude (c : RationalCode) : ℕ :=
  (positive c - negative c) + (negative c - positive c)
def divisor (c : RationalCode) : ℕ := Nat.gcd (denominator c) (magnitude c)
def normalPositive (c : RationalCode) : ℕ := (positive c - negative c) / divisor c
def normalNegative (c : RationalCode) : ℕ := (negative c - positive c) / divisor c
def normalDenominator (c : RationalCode) : ℕ := denominator c / divisor c

theorem primrec_magnitude : Primrec magnitude :=
  Primrec.nat_add.comp (Primrec.nat_sub.comp primrec_positive primrec_negative)
    (Primrec.nat_sub.comp primrec_negative primrec_positive)
theorem primrec_divisor : Primrec divisor :=
  primrec_nat_gcd.comp primrec_denominator primrec_magnitude
theorem primrec_normalPositive : Primrec normalPositive :=
  Primrec.nat_div.comp (Primrec.nat_sub.comp primrec_positive primrec_negative) primrec_divisor
theorem primrec_normalNegative : Primrec normalNegative :=
  Primrec.nat_div.comp (Primrec.nat_sub.comp primrec_negative primrec_positive) primrec_divisor
theorem primrec_normalDenominator : Primrec normalDenominator :=
  Primrec.nat_div.comp primrec_denominator primrec_divisor

/-- The native normalized fields are the literal reduced Rat numerator and
denominator, including zero and negative numerators. -/
theorem normal_fields (c : RationalCode) :
    (value c).num = (normalPositive c : ℤ) - (normalNegative c : ℤ) ∧
    (value c).den = normalDenominator c := by
  by_cases h : negative c ≤ positive c
  · have hsub : negative c - positive c = 0 := Nat.sub_eq_zero_of_le h
    have he : (positive c : ℤ) - (negative c : ℤ) = ((positive c - negative c : ℕ) : ℤ) :=
      (Int.ofNat_sub h).symm
    simp only [value, he, Rat.num_mkRat, Rat.den_mkRat,
      (denominator_pos c).ne', ↓reduceIte, Int.natAbs_natCast,
      normalPositive, normalNegative, normalDenominator, divisor, magnitude,
      hsub, Nat.add_zero, Nat.zero_div, Int.natCast_ediv, Nat.cast_zero, sub_zero]
    exact ⟨trivial, trivial⟩
  · have hle : positive c ≤ negative c := Nat.le_of_lt (Nat.lt_of_not_ge h)
    have hsub : positive c - negative c = 0 := Nat.sub_eq_zero_of_le hle
    have he : (positive c : ℤ) - (negative c : ℤ) = -((negative c - positive c : ℕ) : ℤ) := by
      rw [Int.ofNat_sub hle]
      ring
    have hdvd : (divisor c : ℤ) ∣ ((negative c - positive c : ℕ) : ℤ) := by
      apply Int.ofNat_dvd.mpr
      simpa [divisor, magnitude, hsub] using Nat.gcd_dvd_right (denominator c) (negative c - positive c)
    simp only [value, he, Rat.num_mkRat, Rat.den_mkRat,
      (denominator_pos c).ne', ↓reduceIte, Int.natAbs_neg, Int.natAbs_natCast,
      normalPositive, normalNegative, normalDenominator, divisor, magnitude,
      hsub, Nat.zero_add, Nat.zero_div, Nat.cast_zero, zero_sub]
    constructor
    · have hdvd' : ((denominator c).gcd (negative c - positive c) : ℤ) ∣
          ((negative c - positive c : ℕ) : ℤ) := by
        simpa [divisor, magnitude, hsub] using hdvd
      rw [Int.neg_ediv_of_dvd hdvd', Int.natCast_ediv]
    · trivial

/-- A nonnegative representative of the reduced signed numerator modulo `p`. -/
def numeratorResidue (c : RationalCode) (p : ℕ) : ℕ :=
  (normalPositive c % p + p - normalNegative c % p) % p

/-- Fermat inversion is a total natural-number operation. The zero-denominator
branch is explicit and agrees with the Rat-to-ZMod cast at denominator primes. -/
def primeResidue (c : RationalCode) (p : ℕ) : ℕ :=
  if normalDenominator c % p = 0 then 0
  else (numeratorResidue c p * normalDenominator c ^ (p - 2)) % p

theorem primrec_numeratorResidue : Primrec₂ numeratorResidue := by
  let a : Primrec (fun z : RationalCode × ℕ => normalPositive z.1) :=
    primrec_normalPositive.comp Primrec.fst
  let b : Primrec (fun z : RationalCode × ℕ => normalNegative z.1) :=
    primrec_normalNegative.comp Primrec.fst
  exact Primrec.nat_mod.comp
    (Primrec.nat_sub.comp (Primrec.nat_add.comp (Primrec.nat_mod.comp a Primrec.snd) Primrec.snd)
      (Primrec.nat_mod.comp b Primrec.snd)) Primrec.snd

theorem primrec_primeResidue : Primrec₂ primeResidue := by
  have hpow : Primrec₂ (fun a b : ℕ => a ^ b) := Primrec₂.unpaired'.mp Nat.Primrec.pow
  let d : Primrec (fun z : RationalCode × ℕ => normalDenominator z.1) :=
    primrec_normalDenominator.comp Primrec.fst
  exact Primrec.ite
    (Primrec.eq.comp (Primrec.nat_mod.comp d Primrec.snd) (Primrec.const 0))
    (Primrec.const 0)
    (Primrec.nat_mod.comp
      (Primrec.nat_mul.comp primrec_numeratorResidue
        (hpow.comp d (Primrec.nat_sub.comp Primrec.snd (Primrec.const 2)))) Primrec.snd)

/-- The natural numerator residue casts to the literal normalized Rat numerator. -/
theorem numeratorResidue_cast (c : RationalCode) {p : ℕ} (hp : p.Prime) :
    (numeratorResidue c p : ZMod p) = ((value c).num : ZMod p) := by
  have hb : normalNegative c % p ≤ normalPositive c % p + p :=
    (Nat.mod_lt _ hp.pos).le.trans (Nat.le_add_left _ _)
  rw [numeratorResidue, ZMod.natCast_mod, Nat.cast_sub hb, Nat.cast_add,
    ZMod.natCast_mod, ZMod.natCast_mod, ZMod.natCast_self, add_zero, (normal_fields c).1]
  push_cast
  rfl

/-- Exact reduction at every prime, including all exceptional denominator primes.
This is the total Rat cast used by the actual rational sections. -/
theorem primeResidue_cast (c : RationalCode) {p : ℕ} [Fact p.Prime] :
    (primeResidue c p : ZMod p) = ((value c : ℚ) : ZMod p) := by
  have hp : p.Prime := Fact.out
  by_cases hden : normalDenominator c % p = 0
  · have hd : (normalDenominator c : ZMod p) = 0 :=
      (ZMod.natCast_eq_zero_iff _ _).mpr (Nat.dvd_of_mod_eq_zero hden)
    simp only [primeResidue, hden, ↓reduceIte, Nat.cast_zero]
    rw [Rat.cast_def, (normal_fields c).2, hd, div_zero]
  · have hd : (normalDenominator c : ZMod p) ≠ 0 := by
      intro hz
      exact hden (Nat.mod_eq_zero_of_dvd ((ZMod.natCast_eq_zero_iff _ _).mp hz))
    have hinv : (normalDenominator c : ZMod p) ^ (p - 2) =
        (normalDenominator c : ZMod p)⁻¹ := by
      symm
      apply ZMod.inv_eq_of_mul_eq_one
      have he : p - 2 + 1 = p - 1 := by have := hp.two_le; omega
      rw [mul_comm, ← pow_succ, he]
      exact ZMod.pow_card_sub_one_eq_one hd
    rw [primeResidue, ite_eq_right hden, ZMod.natCast_mod, Nat.cast_mul,
      numeratorResidue_cast c hp, Nat.cast_pow, hinv, Rat.cast_def, (normal_fields c).2,
      div_eq_mul_inv]

/-- The emitted representative is canonical in the finite field. -/
theorem primeResidue_lt (c : RationalCode) {p : ℕ} (hp : p.Prime) : primeResidue c p < p := by
  unfold primeResidue
  split
  · exact hp.pos
  · exact Nat.mod_lt _ hp.pos

theorem primeResidue_eq_val (c : RationalCode) {p : ℕ} [Fact p.Prime] :
    primeResidue c p = (((value c : ℚ) : ZMod p)).val := by
  rw [← primeResidue_cast c, ZMod.val_natCast_of_lt (primeResidue_lt c (Fact.out : p.Prime))]

end RationalCode
end RealizationBoundaries
