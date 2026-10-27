import PaperX.CyclotomicPrimeCoverage
set_option autoImplicit false
open NumberField

example (K : Type*) [Field K] [NumberField K] (p : ℕ) [Fact (Nat.Prime p)] :
    ∃ P : Ideal (𝓞 K), P.IsMaximal ∧ P.LiesOver (Ideal.span {(p : ℤ)}) := by
  exact Ideal.exists_maximal_ideal_liesOver_of_isIntegral (Ideal.span {(p : ℤ)})

#print axioms PaperX.CyclotomicPrimeCoverage.PermittedPrime
#print axioms PaperX.CyclotomicPrimeCoverage.primeResidue
#print axioms PaperX.CyclotomicPrimeCoverage.exists_prime_with_residue
#print axioms PaperX.CyclotomicPrimeCoverage.primeResidue_surjective
#print axioms PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism
#print axioms PaperX.CyclotomicPrimeCoverage.primeSample
#print axioms PaperX.CyclotomicPrimeCoverage.galEquiv_primePowerAutomorphism
#print axioms PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_apply
#print axioms PaperX.CyclotomicPrimeCoverage.exists_prime_with_automorphism
#print axioms PaperX.CyclotomicPrimeCoverage.primeSample_surjective
#print axioms PaperX.CyclotomicPrimeCoverage.primeSample_quotientCoverage
#print axioms PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_mem_stabilizer
#print axioms PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_residue
#print axioms PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_arithmeticFrobenius
#print axioms PaperX.CyclotomicPrimeCoverage.permitted_prime_ramificationIdx
#print axioms PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_unramified_arithmeticFrobenius
