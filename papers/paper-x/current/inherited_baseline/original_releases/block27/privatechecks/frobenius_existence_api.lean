import PaperX.AbsoluteIntegralFrobenius

open PaperX.AbsoluteIntegralFrobenius
open scoped Pointwise

example : ∃ Q : Ideal IntegralClosure,
    Q.IsMaximal ∧ Q.LiesOver (Ideal.span {(2 : ℤ)}) ∧
      ∃ σ : MulAction.stabilizer GQ Q, ∀ x : IntegralClosure,
        Ideal.Quotient.mk Q (σ.val • x) = (Ideal.Quotient.mk Q x) ^ 2 :=
  exists_frobenius 2

#check @exists_frobenius
#check @exists_frobenius_at
#check @residueFrobenius
#print axioms PaperX.AbsoluteIntegralFrobenius.algebraic_int
#print axioms PaperX.AbsoluteIntegralFrobenius.fractionRing
#print axioms PaperX.AbsoluteIntegralFrobenius.galoisGroup_integral
#print axioms PaperX.AbsoluteIntegralFrobenius.continuous_integral_action
#print axioms PaperX.AbsoluteIntegralFrobenius.residue_charP
#print axioms PaperX.AbsoluteIntegralFrobenius.residue_perfect
#print axioms PaperX.AbsoluteIntegralFrobenius.residueFrobenius
#print axioms PaperX.AbsoluteIntegralFrobenius.residueFrobenius_apply
#print axioms PaperX.AbsoluteIntegralFrobenius.exists_frobenius_at
#print axioms PaperX.AbsoluteIntegralFrobenius.exists_frobenius
