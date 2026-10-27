import PaperX.IdealResidueUnitAction
import Mathlib.Analysis.Complex.Basic

/-! Zero mean on the actual ideal residue quotient, obtained from an actual unit
permutation. The unit witness remains explicit. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.IdealResidueUnitAction
open Ideal NumberField
open PaperX.ResidueLattice PaperX.NormResidue PaperX.NormResidueLattice
open scoped nonZeroDivisors BigOperators

variable (K : Type*) [Field K] [NumberField K]

/-- A unit witness forces the norm-character mean on the actual ideal residues to vanish,
including after a fixed sign or other residue multiplier. -/
theorem sum_mul_residueNorm_eq_zero (M J : (Ideal (𝓞 K))⁰) (m : ℕ)
    (hprod : modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)) ≤ M)
    (hM : (M : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m)
    [Fintype (IdealResidues K M J)] (χ : ZMod m →* ℂ)
    (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1)
    (s : ZMod m) :
    ∑ c : IdealResidues K M J, χ (s * residueNorm K M J m hM c) = 0 := by
  have hs : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) *
      (∑ c : IdealResidues K M J, χ (s * residueNorm K M J m hM c)) =
      ∑ c : IdealResidues K M J, χ (s * residueNorm K M J m hM c) := by
    calc
      _ = ∑ c : IdealResidues K M J,
          χ (s * residueNorm K M J m hM (unitPerm K M J m hprod u c)) := by
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro c _
        rw [residueNorm_unitPerm]
        simp only [map_mul]
        ring
      _ = _ := Fintype.sum_equiv (unitPerm K M J m hprod u) _ _ (fun _ => rfl)
  have hz : (χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) - 1) *
      (∑ c : IdealResidues K M J, χ (s * residueNorm K M J m hM c)) = 0 := by
    rw [sub_mul, one_mul, hs, sub_self]
  exact (mul_eq_zero.mp hz).resolve_left (sub_ne_zero.mpr hu)

/-- The actual nonzero product ideal mJ for a nonzero integer modulus. -/
def modulusTimesIdeal (J : (Ideal (𝓞 K))⁰) (m : ℕ) (hm : m ≠ 0) :
    (Ideal (𝓞 K))⁰ :=
  ⟨modulusIdeal (𝓞 K) m * (J : Ideal (𝓞 K)), by
    rw [mem_nonZeroDivisors_iff_ne_zero]
    apply mul_ne_zero
    · change Ideal.span {(m : 𝓞 K)} ≠ ⊥
      exact fun h => (Nat.cast_ne_zero.mpr hm) (Ideal.span_singleton_eq_bot.mp h)
    · exact nonZeroDivisors.coe_ne_zero J⟩

/-- The product ideal is contained in J. -/
theorem modulusTimesIdeal_le (J : (Ideal (𝓞 K))⁰) (m : ℕ) (hm : m ≠ 0) :
    (modulusTimesIdeal K J m hm : Ideal (𝓞 K)) ≤ J :=
  Ideal.mul_le_right

/-- The product ideal is contained in mO. -/
theorem modulusTimesIdeal_le_modulus (J : (Ideal (𝓞 K))⁰) (m : ℕ) (hm : m ≠ 0) :
    (modulusTimesIdeal K J m hm : Ideal (𝓞 K)) ≤ modulusIdeal (𝓞 K) m :=
  Ideal.mul_le_left

/-- The actual additive quotient J/mJ is finite, with no coprimality condition on J. -/
instance modulusTimesIdealResiduesFinite (J : (Ideal (𝓞 K))⁰) (m : ℕ) (hm : m ≠ 0) :
    Finite (IdealResidues K (modulusTimesIdeal K J m hm) J) :=
  finite_idealResidues K (modulusTimesIdeal_le K J m hm)

/-- Explicit specialization to the actual finite quotient J/mJ. -/
theorem sum_modulusTimesIdeal_norm_eq_zero (J : (Ideal (𝓞 K))⁰) (m : ℕ) (hm : m ≠ 0)
    [Fintype (IdealResidues K (modulusTimesIdeal K J m hm) J)]
    (χ : ZMod m →* ℂ) (u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ)
    (hu : χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1)
    (s : ZMod m) :
    ∑ c : IdealResidues K (modulusTimesIdeal K J m hm) J,
      χ (s * residueNorm K (modulusTimesIdeal K J m hm) J m
        (modulusTimesIdeal_le_modulus K J m hm) c) = 0 :=
  sum_mul_residueNorm_eq_zero K (modulusTimesIdeal K J m hm) J m le_rfl
    (modulusTimesIdeal_le_modulus K J m hm) χ u hu s

end PaperX.IdealResidueUnitAction
