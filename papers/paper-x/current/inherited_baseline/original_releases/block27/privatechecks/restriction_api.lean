import PaperX.AbsoluteGaloisRestriction
import PaperX.CyclotomicPrimeCoverage

open PaperX.AbsoluteGaloisRestriction

local instance : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) :=
  CyclotomicField.isCyclotomicExtension 4 ℚ

local instance : IsGalois ℚ (CyclotomicField 4 ℚ) :=
  IsCyclotomicExtension.isGalois {4} ℚ (CyclotomicField 4 ℚ)

example : Function.Surjective (restriction (CyclotomicField 4 ℚ)) :=
  restriction_surjective (CyclotomicField 4 ℚ)

example : Continuous (restriction (CyclotomicField 4 ℚ)) :=
  restriction_continuous (CyclotomicField 4 ℚ)

example : IsOpen ((restriction (CyclotomicField 4 ℚ)).ker :
    Set (Field.absoluteGaloisGroup ℚ)) :=
  restriction_kernel_isOpen (CyclotomicField 4 ℚ)

#print axioms PaperX.AbsoluteGaloisRestriction.embedding
#print axioms PaperX.AbsoluteGaloisRestriction.restriction
#print axioms PaperX.AbsoluteGaloisRestriction.restriction_commutes
#print axioms PaperX.AbsoluteGaloisRestriction.restriction_surjective
#print axioms PaperX.AbsoluteGaloisRestriction.restriction_eq_one_iff
#print axioms PaperX.AbsoluteGaloisRestriction.restriction_continuous
#print axioms PaperX.AbsoluteGaloisRestriction.restriction_kernel_isOpen
#print axioms PaperX.AbsoluteGaloisRestriction.continuousRestriction
