import PaperX.NormResidueArithmetic

/-!
# Why the norm sign is part of a residue filter

The rational integers `-1` and `2` agree modulo `3`. Their signed norms agree
modulo `3`, but their principal ideal norms do not. This is an actual ideal
counterexample to omitting the sign hypothesis.
-/

namespace PaperX.NormResidue

theorem opposite_sign_elements_congruent :
    (-1 : ℤ) - 2 ∈ modulusIdeal ℤ 3 := by
  change (-1 : ℤ) - 2 ∈ Ideal.span {(3 : ℤ)}
  exact Ideal.mem_span_singleton.mpr ⟨-1, by norm_num⟩

theorem opposite_sign_signed_norms_congruent :
    (Algebra.norm ℤ (-1 : ℤ) : ZMod 3) = (Algebra.norm ℤ (2 : ℤ) : ZMod 3) := by
  norm_num
  decide

theorem opposite_sign_principal_norms_differ :
    (Ideal.absNorm (Ideal.span {(-1 : ℤ)}) : ZMod 3) ≠
      (Ideal.absNorm (Ideal.span {(2 : ℤ)}) : ZMod 3) := by
  norm_num [Ideal.absNorm_span_singleton]
  decide

end PaperX.NormResidue
