import PaperX.NormResidueExactScalarCriterion
import Mathlib.Algebra.Group.Hom.Instances

/-!
# Exact obstruction for scalar norm witnesses

The scalar witness exists exactly when the restriction of the residue character
to scalar units does not become trivial after raising character values to the
field degree.  This identifies the precise exceptional scalar-character case;
degree--totient coprimality is only one sufficient way to rule it out.
-/

set_option autoImplicit false
noncomputable section

open scoped NumberField

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- The scalar norm-witness condition is equivalent to nontriviality of the
field-degree power of the restricted multiplicative character. -/
theorem scalar_power_witness_iff_restricted_pow_ne_one
    (m : ℕ) (χ : ZMod m →*₀ ℂ) :
    (∃ a : (ZMod m)ˣ,
      χ ((a : ZMod m) ^ Module.finrank ℚ K) ≠ 1) ↔
    (χ.toMonoidHom.comp (Units.coeHom (ZMod m))) ^ Module.finrank ℚ K ≠ 1 := by
  let ψ : (ZMod m)ˣ →* ℂ := χ.toMonoidHom.comp (Units.coeHom (ZMod m))
  constructor
  · rintro ⟨a, ha⟩ htriv
    apply ha
    have h := DFunLike.congr_fun htriv a
    simpa [ψ, MonoidHom.pow_apply] using h
  · intro hnon
    by_contra hnone
    push Not at hnone
    apply hnon
    ext a
    simpa [ψ, MonoidHom.pow_apply] using hnone a

end PaperX.NormResidue
