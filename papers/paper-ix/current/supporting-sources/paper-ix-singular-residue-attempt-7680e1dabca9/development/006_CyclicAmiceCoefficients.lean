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
  have he : ((p*(p-1):ℕ):ZMod N)=0 := (ZMod.natCast_zmod_eq_zero_iff_dvd _ _).mpr hN
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

end KomorebiPaperIX.CyclicAmiceCoefficients
