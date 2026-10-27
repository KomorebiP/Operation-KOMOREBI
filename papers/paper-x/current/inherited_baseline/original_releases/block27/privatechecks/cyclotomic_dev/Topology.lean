import PaperX.CyclotomicPrimeCoverage
variable (n : ℕ) [NeZero n] (K : Type*) [Field K] [NumberField K]
[IsCyclotomicExtension {n} ℚ K]
#synth TopologicalSpace Gal(K/ℚ)
#check MulEquiv.mapSubgroup
#check MulEquiv.mem_mapSubgroup
#check Subgroup.mem_zpowers
#check Subgroup.mem_map
#check Subgroup.mem_map_equiv
#check MulAction.mem_stabilizer_iff
#check Ideal.Quotient.eq_zero_iff_mem
