import RealizationBoundaries.Extensions
import Mathlib.Data.Rat.Cast.Defs
import Mathlib.LinearAlgebra.Span.Basic

/-! # Actual rational sections in the unrestricted prime product -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The indicator of a chosen set of prime coordinates. -/
def indicator (S : Set Prime) : Ambient := by
  classical
  exact fun p => if p ∈ S then 1 else 0

@[simp] theorem indicator_apply_mem {S : Set Prime} {p : Prime} (hp : p ∈ S) :
    indicator S p = 1 := by
  classical
  simp [indicator, hp]

@[simp] theorem indicator_apply_not_mem {S : Set Prime} {p : Prime} (hp : p ∉ S) :
    indicator S p = 0 := by
  classical
  simp [indicator, hp]

theorem support_indicator (S : Set Prime) : support (indicator S) = S := by
  classical
  ext p
  simp [support, indicator]

theorem indicator_tail_ne_zero {S : Set Prime} (hS : S.Infinite) :
    quotientMap (indicator S) ≠ 0 := by
  intro h
  have hf := (quotientMap_eq_zero_iff _).mp h
  change (support (indicator S)).Finite at hf
  rw [support_indicator] at hf
  exact hS hf

/-- This is the monograph's reduced-rational section, including its zero branch
at denominator primes. The Rat cast into ZMod is num/den, with inverse zero = zero. -/
def rationalSection (S : Set Prime) (r : ℚ) : Ambient := by
  classical
  exact fun p => if p ∈ S then (r : Coordinate p) else 0

@[simp] theorem rationalSection_zero (S : Set Prime) : rationalSection S 0 = 0 := by
  classical
  funext p
  simp [rationalSection]

@[simp] theorem rationalSection_one (S : Set Prime) : rationalSection S 1 = indicator S := by
  classical
  funext p
  simp [rationalSection, indicator]

@[simp] theorem rationalSection_neg (S : Set Prime) (r : ℚ) :
    rationalSection S (-r) = -rationalSection S r := by
  classical
  funext p
  by_cases hp : p ∈ S <;> simp [rationalSection, hp]

/-- The arbitrary-prime zero-denominator branch is explicitly part of the formal statement. -/
theorem rationalSection_denominator_zero (S : Set Prime) (r : ℚ) (p : Prime)
    (hp : p.val ∣ r.den) : rationalSection S r p = 0 := by
  classical
  simp [rationalSection, Rat.cast_def, (coordinate_cast_eq_zero r.den p).mpr hp]

theorem rationalSection_denominator_defect (S : Set Prime) (r : ℚ) :
    r.den • rationalSection S r - r.num • indicator S ∈ finiteSupport := by
  classical
  apply (exceptional_finite r.den_pos).subset
  intro p hp
  by_contra hn
  have hd : (r.den : Coordinate p) ≠ 0 := (coordinate_cast_eq_zero r.den p).not.mpr hn
  apply hp
  by_cases hs : p ∈ S
  · change r.den • rationalSection S r p - r.num • indicator S p = 0
    rw [nsmul_eq_mul, zsmul_eq_mul]
    simp only [rationalSection, hs, ite_true, indicator_apply_mem hs, mul_one, Rat.cast_def]
    rw [mul_div_cancel₀ _ hd, sub_self]
  · simp [Pi.sub_apply, rationalSection, indicator, hs]

/-- The concrete section lands over the intended rational multiple of the tail. -/
theorem quotientMap_rationalSection (S : Set Prime) (r : ℚ) :
    quotientMap (rationalSection S r) = r • quotientMap (indicator S) := by
  have hd := (quotientMap_eq_zero_iff _).mpr (rationalSection_denominator_defect S r)
  rw [map_sub, map_nsmul, map_zsmul, sub_eq_zero] at hd
  apply tail_nsmul_injective r.den_pos
  change r.den • quotientMap (rationalSection S r) =
    r.den • (r • quotientMap (indicator S))
  rw [hd, ← Nat.cast_smul_eq_nsmul ℚ, ← Int.cast_smul_eq_zsmul ℚ, smul_smul]
  congr 1
  exact (Rat.den_mul_eq_num r).symm

/-- The actual rational line, and its original group of admissible ambient points. -/
def selectorLine (S : Set Prime) : Submodule ℚ TailSpace :=
  Submodule.span ℚ {quotientMap (indicator S)}

def selectorGroup (S : Set Prime) : AddSubgroup Ambient := preimage (selectorLine S)

theorem mem_selectorGroup_iff (S : Set Prime) (x : Ambient) :
    x ∈ selectorGroup S ↔ ∃ r : ℚ, r • quotientMap (indicator S) = quotientMap x := by
  change quotientMap x ∈ Submodule.span ℚ {quotientMap (indicator S)} ↔ _
  exact Submodule.mem_span_singleton

theorem rationalSection_mem (S : Set Prime) (r : ℚ) :
    rationalSection S r ∈ selectorGroup S :=
  (mem_selectorGroup_iff _ _).mpr ⟨r, (quotientMap_rationalSection S r).symm⟩

/-- Every point of the actual preimage has a reduced-rational, finite-support normal form. -/
theorem normalForm_exists (S : Set Prime) (x : selectorGroup S) :
    ∃ r : ℚ, ∃ d : finiteSupport, x.val = rationalSection S r + d.val := by
  obtain ⟨r, hr⟩ := (mem_selectorGroup_iff S x.val).mp x.property
  have hd : x.val - rationalSection S r ∈ finiteSupport := by
    apply (quotientMap_eq_iff _ _).mp
    rw [quotientMap_rationalSection, hr]
  exact ⟨r, ⟨x.val - rationalSection S r, hd⟩, by simp⟩

/-- Infinite support is the precise hypothesis needed for a unique rational coordinate. -/
theorem normalForm_unique {S : Set Prime} (hS : S.Infinite)
    (r t : ℚ) (d e : finiteSupport)
    (h : rationalSection S r + d.val = rationalSection S t + e.val) : r = t ∧ d = e := by
  have hq := congrArg quotientMap h
  simp only [map_add, quotientMap_rationalSection,
    (quotientMap_eq_zero_iff _).mpr d.property,
    (quotientMap_eq_zero_iff _).mpr e.property, add_zero] at hq
  have hrt : r = t := (smul_left_injective ℚ (indicator_tail_ne_zero hS)) hq
  subst t
  exact ⟨rfl, Subtype.ext (add_left_cancel h)⟩

end RealizationBoundaries
