import PaperXI.CyclicFrobeniusCount
import Mathlib.NumberTheory.MulChar.Duality
import Mathlib.RingTheory.RootsOfUnity.Complex
import Mathlib.FieldTheory.Finite.Basic

/-! Proposition 3.6 on actual complex-valued multiplicative characters.
The cyclicity and cardinality of the character group are derived, not assumed. -/
set_option autoImplicit false
namespace PaperXI.FiniteFieldOrbitCount
open Function Finset PaperXI.FrobeniusPeriodCount PaperXI.CyclicFrobeniusCount
open scoped Classical

noncomputable instance complexEnoughRoots (m : ℕ) [NeZero m] : HasEnoughRootsOfUnity ℂ m where
  prim := ⟨_, Complex.isPrimitiveRoot_exp m (NeZero.ne m)⟩
  cyc := inferInstance

variable (F : Type*) [Field F] [Finite F]

theorem characterGroup_isCyclic : IsCyclic (MulChar F ℂ) :=
  (MulChar.mulEquiv_units F ℂ).some.isCyclic.mpr inferInstance

attribute [local instance] characterGroup_isCyclic

/-- The full multiplicative character group has |F|-1 elements. -/
theorem character_card : Nat.card (MulChar F ℂ) = Nat.card F - 1 := by
  rw [MulChar.card_eq_card_units_of_hasEnoughRootsOfUnity, Nat.card_units]

noncomputable def characterFrobenius (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hF : Nat.card F = q ^ n) : Equiv.Perm (MulChar F ℂ) :=
  frobeniusPerm q n hq hn (by rw [character_card, hF])

/-- This permutation is exactly precomposition with the qth-power map on units. -/
theorem characterFrobenius_apply (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hF : Nat.card F = q ^ n) (χ : MulChar F ℂ) (x : Fˣ) :
    characterFrobenius F q n hq hn hF χ x = χ (x ^ q : Fˣ) := by
  change (χ ^ q) (x : F) = χ (x ^ q : Fˣ)
  rw [MulChar.pow_apply_coe]
  simp only [Units.val_pow_eq_pow_val, map_pow]

/-- Every iterate has a derived fixed-character count, q^gcd(n,r)-1. -/
theorem fixed_character_count (q n r : ℕ) (hq : 0 < q)
    (hF : Nat.card F = q ^ n) :
    fixedCount (fun χ : MulChar F ℂ => χ ^ q) r = q ^ (n.gcd r) - 1 := by
  exact fixedCount_pow_gcd q n r hq (by rw [character_card, hF])

/-- Exact-period character count with no division and no free count certificate. -/
theorem exact_character_count (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hF : Nat.card F = q ^ n) :
    (exactCount (fun χ : MulChar F ℂ => χ ^ q) n : ℤ) =
      ∑ d ∈ n.divisors, ArithmeticFunction.moebius d * ((q : ℤ) ^ (n / d) - 1) := by
  exact exactCount_formula q n hq hn (by rw [character_card, hF])

/-- Proposition 3.6: cardinality of the quotient of actual regular characters. -/
theorem regular_character_orbits (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hF : Nat.card F = q ^ n) :
    (orbitCount (characterFrobenius F q n hq hn hF) n : ℚ) =
      (1 / (n : ℚ)) * ∑ d ∈ n.divisors,
        (ArithmeticFunction.moebius d : ℚ) * ((q : ℚ) ^ (n / d) - 1) := by
  exact orbitCount_formula q n hq hn (by rw [character_card, hF])

/-- Integrality of the manuscript's numerator follows from the orbit quotient. -/
theorem regular_numerator_divisible (q n : ℕ) (hq : 0 < q) (hn : 0 < n)
    (hF : Nat.card F = q ^ n) :
    (n : ℤ) ∣ ∑ d ∈ n.divisors,
      ArithmeticFunction.moebius d * ((q : ℤ) ^ (n / d) - 1) := by
  exact moebius_sum_dvd (G := MulChar F ℂ) q n hq hn (by rw [character_card, hF])


/-- All hypotheses can be supplied by a genuine finite-field extension K ⊆ F. -/
noncomputable def extensionFrobenius (K : Type*) [Field K] [Fintype K]
    [Fintype F] [Algebra K F] : Equiv.Perm (MulChar F ℂ) :=
  characterFrobenius F (Fintype.card K) (Module.finrank K F)
    Fintype.card_pos Module.finrank_pos
    (by simpa only [Nat.card_eq_fintype_card] using (Module.card_eq_pow_finrank (K := K) (V := F)))

/-- The manuscript count on a finite-field extension, with its true extension degree. -/
theorem extension_regular_orbits (K : Type*) [Field K] [Fintype K]
    [Fintype F] [Algebra K F] :
    (orbitCount (extensionFrobenius F K) (Module.finrank K F) : ℚ) =
      (1 / (Module.finrank K F : ℚ)) * ∑ d ∈ (Module.finrank K F).divisors,
        (ArithmeticFunction.moebius d : ℚ) *
          ((Fintype.card K : ℚ) ^ (Module.finrank K F / d) - 1) := by
  exact regular_character_orbits F (Fintype.card K) (Module.finrank K F)
    Fintype.card_pos Module.finrank_pos
    (by simpa only [Nat.card_eq_fintype_card] using (Module.card_eq_pow_finrank (K := K) (V := F)))

/-- The extension action evaluates characters on the actual qth power of field units. -/
theorem extensionFrobenius_apply (K : Type*) [Field K] [Fintype K]
    [Fintype F] [Algebra K F] (χ : MulChar F ℂ) (x : Fˣ) :
    extensionFrobenius F K χ x = χ (x ^ Fintype.card K : Fˣ) := by
  exact characterFrobenius_apply F _ _ _ _ _ χ x

end PaperXI.FiniteFieldOrbitCount
