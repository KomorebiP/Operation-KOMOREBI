import PowerDivisibility
import Mathlib.RingTheory.Ideal.Span
import Mathlib.RingTheory.Ideal.Maps

/-! Residue maps and the precise leading-layer faithfulness needed to reduce a
normalized error. No division in an arbitrary compatible submodule is used. -/
namespace Komorebi.StrongArtin.ResidualLayer
open Komorebi.StrongArtin.PowerDivisibility

variable {R M V : Type*} [CommRing R]
  [AddCommGroup M] [Module R M] [AddCommGroup V]

/-- An additive residue map with kernel exactly `pi M`. -/
structure Reduction (pi : R) (M V : Type*)
    [AddCommGroup M] [Module R M] [AddCommGroup V] where
  map : M →+ V
  onto : Function.Surjective map
  zero_iff : ∀ z, map z = 0 ↔ PowDivisible pi 1 z

/-- No element killed by the current leading power has nonzero residue. -/
def FaithfulAt (pi : R) (red : Reduction pi M V) (n : ℕ) : Prop :=
  ∀ z : M, (pi ^ n) • z = 0 → red.map z = 0

namespace Reduction
variable {pi : R} (red : Reduction pi M V)

@[simp] theorem map_pi_smul (z : M) : red.map (pi • z) = 0 := by
  apply (red.zero_iff _).mpr
  exact ⟨z, by simp⟩

theorem map_eq_of_difference_divisible {x y : M}
    (h : PowDivisible pi 1 (x - y)) : red.map x = red.map y := by
  have he := (red.zero_iff _).mpr h
  rw [map_sub, sub_eq_zero] at he
  exact he

theorem scaled_error_raises_one {e : M} (n : ℕ) (he : red.map e = 0) :
    PowDivisible pi (n + 1) ((pi ^ n) • e) := by
  obtain ⟨w, hw⟩ := (red.zero_iff _).mp he
  refine ⟨w, ?_⟩
  rw [← hw, pow_one, pow_succ, mul_smul]

theorem leading_residue_unique {n : ℕ} (hf : FaithfulAt pi red n)
    {e e' : M} (h : (pi ^ n) • e = (pi ^ n) • e') :
    red.map e = red.map e' := by
  have hz : (pi ^ n) • (e - e') = 0 := by rw [smul_sub, h, sub_self]
  have hr := hf (e - e') hz
  simpa only [map_sub, sub_eq_zero] using hr

theorem faithfulAt_of_injective_smul (n : ℕ)
    (hinj : Function.Injective (fun z : M => pi • z)) : FaithfulAt pi red n := by
  intro z hz
  have hpow : ∀ m : ℕ, ∀ w : M, (pi ^ m) • w = 0 → w = 0 := by
    intro m
    induction m with
    | zero => intro w hw; simpa using hw
    | succ m ih =>
        intro w hw
        have hh : pi • ((pi ^ m) • w) = pi • (0 : M) := by
          simpa [pow_succ', mul_smul] using hw
        exact ih w (hinj hh)
  rw [hpow n z hz, map_zero]

end Reduction

section Coordinates
variable {k ι : Type*} [CommRing k]

/-- Coordinatewise reduction through a principal residue homomorphism. -/
noncomputable def coordinateReduction (pi : R) (q : R →+* k)
    (hq : Function.Surjective q) (hker : RingHom.ker q = Ideal.span {pi}) :
    Reduction pi (ι → R) (ι → k) where
  map :=
    { toFun := fun x i => q (x i)
      map_zero' := by funext i; simp
      map_add' := by intro x y; funext i; simp }
  onto := by
    intro y
    classical
    choose x hx using fun i => hq (y i)
    exact ⟨x, funext hx⟩
  zero_iff := by
    intro x
    constructor
    · intro hx
      have hi : ∀ i, pi ∣ x i := by
        intro i
        apply Ideal.mem_span_singleton.mp
        rw [← hker]
        exact congrFun hx i
      classical
      choose y hy using hi
      refine ⟨y, ?_⟩
      funext i
      simpa [pow_one, smul_eq_mul] using (hy i).symm
    · rintro ⟨y, hy⟩
      have hpi : q pi = 0 := by
        change pi ∈ RingHom.ker q
        rw [hker]
        exact Ideal.subset_span (by simp)
      funext i
      have hx := congrFun hy i
      simp only [pow_one, Pi.smul_apply, smul_eq_mul] at hx
      change q (x i) = 0
      rw [← hx, map_mul, hpi, zero_mul]

@[simp] theorem coordinateReduction_apply (pi : R) (q : R →+* k)
    (hq : Function.Surjective q) (hker : RingHom.ker q = Ideal.span {pi})
    (x : ι → R) (i : ι) :
    (coordinateReduction pi q hq hker).map x i = q (x i) := rfl

end Coordinates
end Komorebi.StrongArtin.ResidualLayer
