import PaperXI.ActualCuspidalCandidate105

/-! The previously constructed residue map agrees with literal entrywise
reduction on integral centralizer matrices. This identity is proved, not supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ResidueRestriction107
open Matrix ValuativeRel
open ActualCharacterType61 ActualCharacterResidue61 ActualCuspidalCandidate105
open ActualELatticeResidue59 ActualELatticeTopology60 ActualEmbeddedUniformizer58 LatticeCongruenceTopology60

theorem quotient_inclusion {G Q : Type*} [Group G] [Group Q]
    (H N : Subgroup G) (hn : H ≤ Subgroup.normalizer (N : Set G))
    (q : H →* Q) (hq : Function.Surjective q) (hk : N.subgroupOf H = q.ker)
    (h : H) :
    let := Subgroup.normal_subgroupOf_sup_of_le_normalizer hn
    ProductNormalizerQuotient59.quotientEquivOfKernel H N hn q hq hk
      (QuotientGroup.mk' (N.subgroupOf (H ⊔ N)) (Subgroup.inclusion le_sup_left h)) = q h := by
  dsimp only
  let := Subgroup.normal_subgroupOf_of_le_normalizer hn
  let := Subgroup.normal_subgroupOf_sup_of_le_normalizer hn
  have he : QuotientGroup.quotientInfEquivProdNormalizerQuotient H N hn
      (QuotientGroup.mk' (N.subgroupOf H) h) =
      QuotientGroup.mk' (N.subgroupOf (H ⊔ N)) (Subgroup.inclusion le_sup_left h) := rfl
  rw [← he]
  change (QuotientGroup.quotientKerEquivOfSurjective q hq)
    (QuotientGroup.quotientMulEquivOfEq hk
      ((QuotientGroup.quotientInfEquivProdNormalizerQuotient H N hn).symm
        (QuotientGroup.quotientInfEquivProdNormalizerQuotient H N hn
          (QuotientGroup.mk' (N.subgroupOf H) h)))) = q h
  rw [MulEquiv.symm_apply_apply]
  rfl

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)
  (hmodel : compact F E m n e D θ ≤ matrixType F E m n e)
  (hB : ∀ u : GL m 𝒪[E],
    (coordinateAut e).symm (integralMatrix F E m u) ∈ CharacterNormalizer61.normalizer D θ)

def integralInclusion : GL m 𝒪[E] →* compact F E m n e D θ :=
  (centralizerMap F E m n e |>.comp (ActualIntegralGeneralLinear.embedding E m)).codRestrict _
    (fun u => integralMatrix_mem_compactGroup F E m n e D θ hB u)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
@[simp] theorem integralInclusion_coe (u : GL m 𝒪[E]) :
    (integralInclusion F E m n e D θ hB u : GL n F) =
      centralizerMap F E m n e (ActualIntegralGeneralLinear.embedding E m u) := rfl

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- Equality on the exact old quotient construction; no unspecified residue
isomorphism or conjugate finite representation is substituted. -/
theorem reduction_integral (u : GL m 𝒪[E]) :
    reduction F E m n e D θ hmodel (integralInclusion F E m n e D θ hB u) =
      ActualResidueGeneralLinear.reduction E m u := by
  have he : intoModel F E m n e D θ hmodel (integralInclusion F E m n e D θ hB u) =
      Subgroup.inclusion (show integralImage F E m ≤ ActualELatticeTypeGroup59.typeGroup F E m
        from le_sup_left) (integralImageEquiv F E m u) := by
    apply Subtype.ext
    exact (coordinateAut e).apply_symm_apply (integralMatrix F E m u)
  change ActualELatticeQuotient59.reduction F E m _ = _
  rw [he]
  have h := quotient_inclusion (integralImage F E m)
    (ActualELatticeTypeGroup59.congruence F E m)
    (ActualELatticeTypeGroup59.integralImage_normalizes F E m)
    (residueAction F E m) (residueAction_surjective F E m)
    (ActualELatticeTypeGroup59.congruence_subgroupOf_integralImage F E m)
    (integralImageEquiv F E m u)
  exact h.trans (congrArg (ActualResidueGeneralLinear.reduction E m)
    ((integralImageEquiv F E m).symm_apply_apply u))

end PaperXI.ResidueRestriction107
