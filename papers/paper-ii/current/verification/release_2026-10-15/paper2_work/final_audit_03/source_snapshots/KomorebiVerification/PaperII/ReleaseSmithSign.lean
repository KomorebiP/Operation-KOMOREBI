import KomorebiVerification.PaperII.SmithDyadic
import KomorebiVerification.PaperII.ResultantSeparation
import Mathlib.NumberTheory.Padics.PadicIntegers
import Mathlib.LinearAlgebra.Matrix.ToLin

/-! The displayed sign projectors on the actual p-adic standard lattice. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.PadicSign
open scoped Matrix
open ResultantSeparation
variable (p : Nat) [Fact p.Prime]

/-- Precisely the vectors with p-adic integer coordinates. -/
def standardLattice : Submodule (PadicInt p) (Fin 2 → Padic p) where
  carrier := {x | ∀ i, x i ∈ PadicInt.subring p}
  zero_mem' _i := (PadicInt.subring p).zero_mem
  add_mem' hx hy i := (PadicInt.subring p).add_mem (hx i) (hy i)
  smul_mem' c _x hx i := (PadicInt.subring p).mul_mem c.property (hx i)

def positiveSign : Module.End (Padic p) (Fin 2 → Padic p) :=
  Matrix.toLin' (SmithDyadic.positiveSignProjector.map (Rat.castHom (Padic p)))

def negativeSign : Module.End (Padic p) (Fin 2 → Padic p) :=
  Matrix.toLin' (SmithDyadic.negativeSignProjector.map (Rat.castHom (Padic p)))

theorem positiveSign_apply (x : Fin 2 → Padic p) :
    positiveSign p x = ![x 0 + (2 : Padic p)⁻¹ * x 1, 0] := by
  ext i
  fin_cases i <;> simp [positiveSign, Matrix.toLin'_apply, Matrix.mulVec,
    dotProduct, Fin.sum_univ_two, SmithDyadic.positiveSignProjector]

theorem negativeSign_apply (x : Fin 2 → Padic p) :
    negativeSign p x = ![-((2 : Padic p)⁻¹ * x 1), x 1] := by
  ext i
  fin_cases i <;> simp [negativeSign, Matrix.toLin'_apply, Matrix.mulVec,
    dotProduct, Fin.sum_univ_two, SmithDyadic.negativeSignProjector, div_eq_mul_inv, neg_mul]

theorem positiveSign_twice (x : Fin 2 → Padic p) :
    (2 : Padic p) • positiveSign p x = ![2 * x 0 + x 1, 0] := by
  rw [positiveSign_apply]
  ext i
  fin_cases i <;> simp [mul_add]

theorem negativeSign_twice (x : Fin 2 → Padic p) :
    (2 : Padic p) • negativeSign p x = ![-x 1, 2 * x 1] := by
  rw [negativeSign_apply]
  ext i
  fin_cases i <;> simp

theorem twice_positive_preserves :
    PreservesLattice ((2 : Padic p) • positiveSign p) (standardLattice p).toAddSubgroup := by
  intro x hx
  change ∀ i, (((2 : Padic p) • positiveSign p) x) i ∈ PadicInt.subring p
  rw [LinearMap.smul_apply, positiveSign_twice]
  intro i
  fin_cases i
  · exact (PadicInt.subring p).add_mem ((PadicInt.subring p).mul_mem
      (by simp) (hx 0)) (hx 1)
  · exact (PadicInt.subring p).zero_mem

theorem twice_negative_preserves :
    PreservesLattice ((2 : Padic p) • negativeSign p) (standardLattice p).toAddSubgroup := by
  intro x hx
  change ∀ i, (((2 : Padic p) • negativeSign p) x) i ∈ PadicInt.subring p
  rw [LinearMap.smul_apply, negativeSign_twice]
  intro i
  fin_cases i
  · exact (PadicInt.subring p).neg_mem (hx 1)
  · exact (PadicInt.subring p).mul_mem (by simp) (hx 1)

theorem half_integral_of_odd (hp : p ≠ 2) : (2 : Padic p)⁻¹ ∈ PadicInt.subring p := by
  rw [PadicInt.mem_subring_iff, norm_inv]
  have hc : p.Coprime 2 := (Fact.out : p.Prime).coprime_iff_not_dvd.mpr (by
    intro h
    rcases (Nat.dvd_prime Nat.prime_two).mp h with h | h
    · exact (Fact.out : p.Prime).ne_one h
    · exact hp h)
  have hn : ‖(2 : Padic p)‖ = 1 := (Padic.norm_natCast_eq_one_iff (p := p)).mpr hc
  rw [hn, inv_one]

theorem positive_preserves_of_odd (hp : p ≠ 2) :
    PreservesLattice (positiveSign p) (standardLattice p).toAddSubgroup := by
  intro x hx
  change ∀ i, positiveSign p x i ∈ PadicInt.subring p
  rw [positiveSign_apply]
  intro i
  fin_cases i
  · exact (PadicInt.subring p).add_mem (hx 0)
      ((PadicInt.subring p).mul_mem (half_integral_of_odd p hp) (hx 1))
  · exact (PadicInt.subring p).zero_mem

theorem negative_preserves_of_odd (hp : p ≠ 2) :
    PreservesLattice (negativeSign p) (standardLattice p).toAddSubgroup := by
  intro x hx
  change ∀ i, negativeSign p x i ∈ PadicInt.subring p
  rw [negativeSign_apply]
  intro i
  fin_cases i
  · exact (PadicInt.subring p).neg_mem
      ((PadicInt.subring p).mul_mem (half_integral_of_odd p hp) (hx 1))
  · exact hx 1


local instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩

theorem dyadic_half_norm : ‖(2 : Padic 2)⁻¹‖ = 2 := by
  have hn : ‖(2 : Padic 2)‖ = (2 : ℝ)⁻¹ := Padic.norm_p
  rw [norm_inv, hn]
  norm_num

theorem positive_dyadic_not_preserves :
    ¬ PreservesLattice (positiveSign 2) (standardLattice 2).toAddSubgroup := by
  intro h
  have hx : (![0, 1] : Fin 2 → Padic 2) ∈ (standardLattice 2).toAddSubgroup := by
    intro i
    fin_cases i <;> simp
  have hi := h ![0, 1] hx
  have hn : ‖(2 : Padic 2)⁻¹‖ ≤ 1 := by
    simpa [positiveSign_apply] using hi 0
  rw [dyadic_half_norm] at hn
  norm_num at hn

theorem negative_dyadic_not_preserves :
    ¬ PreservesLattice (negativeSign 2) (standardLattice 2).toAddSubgroup := by
  intro h
  have hx : (![0, 1] : Fin 2 → Padic 2) ∈ (standardLattice 2).toAddSubgroup := by
    intro i
    fin_cases i <;> simp
  have hi := h ![0, 1] hx
  have hn : ‖(2 : Padic 2)⁻¹‖ ≤ 1 := by
    simpa [negativeSign_apply] using hi 0
  rw [dyadic_half_norm] at hn
  norm_num at hn

theorem positive_dyadic_clears_one :
    IsSeparationWeight (2 : Padic 2) (positiveSign 2) (standardLattice 2).toAddSubgroup 1 := by
  simpa only [IsSeparationWeight, pow_one] using twice_positive_preserves 2

theorem negative_dyadic_clears_one :
    IsSeparationWeight (2 : Padic 2) (negativeSign 2) (standardLattice 2).toAddSubgroup 1 := by
  simpa only [IsSeparationWeight, pow_one] using twice_negative_preserves 2

theorem positive_dyadic_finite :
    HasFiniteSeparationWeight (2 : Padic 2) (positiveSign 2) (standardLattice 2).toAddSubgroup :=
  ⟨1, positive_dyadic_clears_one⟩

theorem negative_dyadic_finite :
    HasFiniteSeparationWeight (2 : Padic 2) (negativeSign 2) (standardLattice 2).toAddSubgroup :=
  ⟨1, negative_dyadic_clears_one⟩

/-- The least clearing exponent on the actual Z_2 standard lattice is exactly one. -/
theorem positive_dyadic_separationWeight : separationWeight positive_dyadic_finite = 1 := by
  apply Nat.le_antisymm (separationWeight_le_of_clears _ positive_dyadic_clears_one)
  apply Nat.one_le_iff_ne_zero.mpr
  intro hz
  have h := separationWeight_clears positive_dyadic_finite
  rw [hz] at h
  exact positive_dyadic_not_preserves (by simpa [IsSeparationWeight] using h)

theorem negative_dyadic_separationWeight : separationWeight negative_dyadic_finite = 1 := by
  apply Nat.le_antisymm (separationWeight_le_of_clears _ negative_dyadic_clears_one)
  apply Nat.one_le_iff_ne_zero.mpr
  intro hz
  have h := separationWeight_clears negative_dyadic_finite
  rw [hz] at h
  exact negative_dyadic_not_preserves (by simpa [IsSeparationWeight] using h)

end Komorebi.PaperII.PadicSign
#print axioms Komorebi.PaperII.PadicSign.positive_preserves_of_odd
#print axioms Komorebi.PaperII.PadicSign.twice_negative_preserves

#print axioms Komorebi.PaperII.PadicSign.positive_dyadic_separationWeight
#print axioms Komorebi.PaperII.PadicSign.negative_dyadic_separationWeight
