module
public import PrimeBlockPolynomial
public import Mathlib.Algebra.MonoidAlgebra.Basic
public import Mathlib.NumberTheory.Padics.PadicIntegers
public import Mathlib.Tactic
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.CyclicAmiceCoefficients
open PrimeBlockPolynomial

/-- Integral cyclic group ring, with exact residue addresses. -/
abbrev CyclicRing (N : ℕ) := AddMonoidAlgebra ℤ (ZMod N)

def generator (N : ℕ) : CyclicRing N := AddMonoidAlgebra.single 1 1

theorem generator_pow (N k : ℕ) :
    generator N ^ k = AddMonoidAlgebra.single (k : ZMod N) (1:ℤ) := by
  simp [generator, AddMonoidAlgebra.single_pow, nsmul_eq_mul]

theorem generator_relation (p N : ℕ) (hN : N ∣ p*(p-1)) :
    generator N ^ (p*(p-1))=1 := by
  have he : ((p*(p-1):ℕ):ZMod N)=0 := (ZMod.natCast_eq_zero_iff _ _).mpr hN
  rw [generator_pow, he]
  rfl

theorem coeff_nat_mul (N k : ℕ) (f : CyclicRing N) (r : ZMod N) :
    ((k:CyclicRing N)*f).coeff r = (k:ℤ)*f.coeff r := by
  rw [AddMonoidAlgebra.natCast_def, AddMonoidAlgebra.coeff_single_zero_mul]

theorem coeff_nat_pow_mul (N p e : ℕ) (f : CyclicRing N) (r : ZMod N) :
    ((p:CyclicRing N)^e*f).coeff r = (p:ℤ)^e*f.coeff r := by
  rw [←Nat.cast_pow, coeff_nat_mul, Nat.cast_pow]

/-- The integer numerator of a transformed section coefficient. -/
def numerator (N d : ℕ) (r : ZMod N) : ℤ :=
  (fallingAt (generator N) d).coeff r

/-- All residue coordinates satisfy the factorial bound, including singular residues. -/
theorem numerator_divisibility (p : ℕ) (hp : p.Prime) (N d : ℕ)
    (hN : N ∣ p*(p-1)) (r : ZMod N) :
    (p:ℤ)^(padicValNat p (d/p).factorial) ∣ numerator N d r := by
  obtain ⟨f,hf⟩ := falling_factorial_divisibility p hp (generator N) (generator_relation p N hN) d
  refine ⟨f.coeff r, ?_⟩
  have hh := congrArg (fun f : CyclicRing N => f.coeff r) hf
  simpa only [numerator, coeff_nat_pow_mul] using hh

/-- The ordinary coefficient obtained by binomial expansion of the cyclic generator. -/
def coefficient (N d : ℕ) (r : ZMod N) : ℚ :=
  (numerator N d r : ℚ)/(d.factorial:ℚ)

/-- The scalar that cancels exactly the p-part of a factorial. -/
def normalizer (p d : ℕ) : ℚ :=
  (p:ℚ)^(padicValNat p d.factorial)/(d.factorial:ℚ)

theorem normalizer_nonzero (p d : ℕ) (hp : p.Prime) : normalizer p d ≠ 0 := by
  apply div_ne_zero
  · exact pow_ne_zero _ (Nat.cast_ne_zero.mpr hp.ne_zero)
  · exact Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero d)

theorem normalizer_valuation (p d : ℕ) (hp : p.Prime) :
    padicValRat p (normalizer p d)=0 := by
  let : Fact p.Prime := ⟨hp⟩
  rw [normalizer, padicValRat.div
    (pow_ne_zero _ (Nat.cast_ne_zero.mpr hp.ne_zero))
    (Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero d))]
  simp [padicValRat.self hp.one_lt]

theorem normalizer_integral (p d : ℕ) [hp : Fact p.Prime] :
    (normalizer p d : ℚ_[p]) ∈ PadicInt.subring p := by
  change ‖(normalizer p d : ℚ_[p])‖≤1
  rw [Padic.eq_padicNorm, padicNorm.eq_zpow_of_nonzero (normalizer_nonzero p d hp.out),
    normalizer_valuation p d hp.out]
  norm_num

/-- The full ordinary-coefficient weight bound, in the actual completed p-adic integer subring. -/
theorem coefficient_weighted_integral (p N d : ℕ) [hp : Fact p.Prime]
    (hN : N ∣ p*(p-1)) (r : ZMod N) :
    (p:ℚ_[p])^(d/p)*(coefficient N d r : ℚ_[p]) ∈ PadicInt.subring p := by
  obtain ⟨z,hz⟩ := numerator_divisibility p hp.out N d hN r
  have hv : padicValNat p d.factorial = padicValNat p (d/p).factorial+d/p := by
    rw [←padicValNat_mul_div_factorial (p:=p) d, padicValNat_factorial_mul]
  have he : (p:ℚ)^(d/p)*coefficient N d r = normalizer p d * (z:ℚ) := by
    rw [coefficient, hz, normalizer, hv, pow_add]
    push_cast
    ring
  have he' : (p:ℚ_[p])^(d/p)*(coefficient N d r : ℚ_[p]) =
      (normalizer p d : ℚ_[p])*(z:ℚ_[p]) := by
    exact_mod_cast he
  rw [he']
  exact (PadicInt.subring p).mul_mem (normalizer_integral p d)
    (intCast_mem (PadicInt.subring p) z)

end KomorebiPaperIX.CyclicAmiceCoefficients
