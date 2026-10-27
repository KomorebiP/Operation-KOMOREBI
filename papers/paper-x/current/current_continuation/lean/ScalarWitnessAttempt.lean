import PaperX.NormResidueCharacter
import Mathlib.Data.ZMod.Units
import Mathlib.GroupTheory.OrderOfElement

set_option autoImplicit false
noncomputable section
open scoped NumberField
namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

theorem integerQuotient_mk_nat_eq_of_zmod_eq (m a b : ℕ)
    (h : (a : ZMod m) = (b : ZMod m)) :
    Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) (a : 𝓞 K) =
      Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) (b : 𝓞 K) := by
  apply (Ideal.Quotient.mk_eq_mk_iff_sub_mem _ _).2
  change (a : 𝓞 K) - (b : 𝓞 K) ∈ Ideal.span {(m : 𝓞 K)}
  rw [Ideal.mem_span_singleton]
  have hz : (m : ℤ) ∣ (a : ℤ) - (b : ℤ) :=
    (ZMod.natCast_eq_natCast_iff a b m).mp h |>.symm.dvd
  rcases hz with ⟨z, hz⟩
  refine ⟨(z : 𝓞 K), ?_⟩
  exact_mod_cast hz

theorem integerQuotientNorm_natCast (m a : ℕ) :
    integerQuotientNorm K m
      (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) (a : 𝓞 K)) =
      (a : ZMod m) ^ Module.finrank ℚ K := by
  rw [integerQuotientNorm_mk, Algebra.norm_natCast]
  simp [NumberField.RingOfIntegers.rank]

noncomputable def scalarResidueUnit (m : ℕ) (hm : m ≠ 0) (a : (ZMod m)ˣ) :
    (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ := by
  let _ : NeZero m := ⟨hm⟩
  let av : ℕ := (a : ZMod m).val
  let bv : ℕ := a.inv.val
  refine ⟨Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) (av : 𝓞 K),
    Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) (bv : 𝓞 K), ?_, ?_⟩
  · have hz : ((av * bv : ℕ) : ZMod m) = (1 : ZMod m) := by
      dsimp [av, bv]
      rw [Nat.cast_mul, ZMod.natCast_zmod_val, ZMod.natCast_zmod_val]
      exact a.val_inv
    simpa only [map_mul, Nat.cast_mul, map_one, Nat.cast_one] using
      integerQuotient_mk_nat_eq_of_zmod_eq K m (av * bv) 1 (by simpa using hz)
  · have hz : ((bv * av : ℕ) : ZMod m) = (1 : ZMod m) := by
      dsimp [av, bv]
      rw [Nat.cast_mul, ZMod.natCast_zmod_val, ZMod.natCast_zmod_val]
      exact a.inv_val
    simpa only [map_mul, Nat.cast_mul, map_one, Nat.cast_one] using
      integerQuotient_mk_nat_eq_of_zmod_eq K m (bv * av) 1 (by simpa using hz)

theorem integerQuotientNorm_scalarResidueUnit (m : ℕ) (hm : m ≠ 0)
    (a : (ZMod m)ˣ) :
    integerQuotientNorm K m
      (scalarResidueUnit K m hm a : 𝓞 K ⧸ modulusIdeal (𝓞 K) m) =
      (a : ZMod m) ^ Module.finrank ℚ K := by
  let _ : NeZero m := ⟨hm⟩
  change integerQuotientNorm K m
      (Ideal.Quotient.mk (modulusIdeal (𝓞 K) m) ((a : ZMod m).val : 𝓞 K)) = _
  rw [integerQuotientNorm_natCast]
  rw [ZMod.natCast_zmod_val]

end PaperX.NormResidue

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

theorem exists_scalarResidueUnit_witness_of_restricted_nontrivial
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Module.finrank ℚ K).Coprime m.totient) :
    ∃ u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ,
      χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1 := by
  let _ : NeZero m := ⟨hm⟩
  have hbex : ∃ b : (ZMod m)ˣ, χ (b : ZMod m) ≠ 1 := by
    by_contra h
    push Not at h
    apply hχ
    ext b
    simpa using h b
  obtain ⟨b, hb⟩ := hbex
  have hcard : (Nat.card ((ZMod m)ˣ)).Coprime (Module.finrank ℚ K) := by
    rw [Nat.card_eq_fintype_card, ZMod.card_units_eq_totient]
    exact hdeg.symm
  obtain ⟨a, ha⟩ := (Nat.Coprime.pow_left_bijective hcard).2 b
  refine ⟨scalarResidueUnit K m hm a, ?_⟩
  rw [integerQuotientNorm_scalarResidueUnit]
  have ha' : (a : ZMod m) ^ Module.finrank ℚ K = (b : ZMod m) := by
    simpa using congrArg (fun u : (ZMod m)ˣ => (u : ZMod m)) ha
  rw [ha']
  exact hb

end PaperX.NormResidue
