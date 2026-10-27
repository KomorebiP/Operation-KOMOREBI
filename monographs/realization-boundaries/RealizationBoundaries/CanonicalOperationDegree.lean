import RealizationBoundaries.ComputableNormalCodes
import RealizationBoundaries.OracleCopyOperations

/-! # The exact oracle degree of the fixed natural-name addition operation -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Fix the concrete canonical copy produced by the native normal-form construction. -/
def canonicalPairedCopy (a : ℕ → Bool) : OracleGroupCopy a (pairedGroup a) :=
  pairedOracleCopy a a (TuringReducible.refl _)

/-- The actual addition function on its fixed bijective natural names. -/
def canonicalPairedAddition (a : ℕ → Bool) (k : ℕ) : ℕ :=
  (canonicalPairedCopy a).add k.unpair.1 k.unpair.2

/-- This fixed operation, rather than only the abstract group's least copy degree,
has precisely the selector's oracle strength. -/
theorem canonicalPairedAddition_oracle_iff (a X : ℕ → Bool) :
    OracleComputable X (canonicalPairedAddition a) ↔ SelectorReducible a X := by
  constructor
  · intro h
    let c := canonicalPairedCopy a
    let d : OracleGroupCopy X (pairedGroup a) :=
      { names := c.names
        zero := c.zero
        add := c.add
        zero_spec := c.zero_spec
        add_spec := c.add_spec
        add_computable := h }
    exact oracle_unmarked_copy_reduces a X d
  · intro ha
    exact (canonicalPairedCopy a).add_computable.change_oracle ha

end RealizationBoundaries
