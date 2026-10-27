import ResidualLayer
import Mathlib.RingTheory.Nilpotent.Basic

/-! Leading-layer faithfulness follows intrinsically from a principal nilpotent
residue kernel. A presentation as a truncated DVR quotient is unnecessary. -/
namespace Komorebi.StrongArtin.PrincipalResidueFaithfulness
open Komorebi.StrongArtin.ResidualLayer

variable {R k : Type*} [CommRing R] [Field k]

/-- An element with nonzero residue is a unit when the residue kernel is
principal and nilpotent. -/
theorem isUnit_of_nonzero_residue
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (hnil : IsNilpotent pi)
    (z : R) (hz : q z ≠ 0) : IsUnit z := by
  obtain ⟨u, hu⟩ := hq ((q z)⁻¹)
  have he : z * u - 1 ∈ RingHom.ker q := by
    change q (z * u - 1) = 0
    simp [hu, hz]
  rw [hker, Ideal.mem_span_singleton] at he
  obtain ⟨e, he⟩ := he
  have hpie : IsNilpotent (pi * e) := (Commute.all pi e).isNilpotent_mul_right hnil
  have heq : z * u = pi * e + 1 := sub_eq_iff_eq_add.mp he
  have hunit : IsUnit (z * u) := by rw [heq]; exact hpie.isUnit_add_one
  exact isUnit_of_mul_isUnit_left hunit

/-- Faithfulness holds at every nonzero principal layer; termination is treated
separately at the first power which vanishes. -/
theorem residue_zero_of_nonterminal_power_kills
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (hnil : IsNilpotent pi)
    (n : ℕ) (hnonzero : pi ^ n ≠ 0)
    (z : R) (hz : pi ^ n * z = 0) : q z = 0 := by
  by_contra hqz
  have hu := isUnit_of_nonzero_residue pi q hq hker hnil z hqz
  apply hnonzero
  calc
    pi ^ n = (pi ^ n) * (z * (↑hu.unit⁻¹ : R)) := by rw [hu.mul_val_inv, mul_one]
    _ = 0 := by rw [← mul_assoc, hz, zero_mul]

/-- The intrinsic principal-Artin faithfulness theorem in coordinate form. -/
theorem coordinate_faithful_of_nonterminal_power
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (hnil : IsNilpotent pi)
    (n : ℕ) (hnonzero : pi ^ n ≠ 0) (ι : Type*) :
    FaithfulAt pi (coordinateReduction (ι := ι) pi q hq hker) n := by
  intro z hz
  funext i
  apply residue_zero_of_nonterminal_power_kills pi q hq hker hnil n hnonzero (z i)
  simpa only [Pi.smul_apply, smul_eq_mul, Pi.zero_apply] using congrFun hz i

end Komorebi.StrongArtin.PrincipalResidueFaithfulness
