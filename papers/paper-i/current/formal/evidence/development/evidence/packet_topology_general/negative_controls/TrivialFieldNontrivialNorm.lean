import Mathlib.Analysis.Normed.Field.WithAbs
import Mathlib.Algebra.Field.ZMod
noncomputable section
instance : Fact (Nat.Prime 2) := ⟨Nat.prime_two⟩
abbrev TrivialField := WithAbs (AbsoluteValue.trivial : AbsoluteValue (ZMod 2) ℝ)
example : NontriviallyNormedField TrivialField := inferInstance
