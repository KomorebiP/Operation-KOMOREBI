import PaperXI.DVRCartan106
import PaperXI.ActualLocalUnitDecomposition
import PaperXI.ActualIntegralGeneralLinear
import PaperXI.ActualResidueGeneralLinear

/-! The arithmetic Cartan and residue support theorems on actual local-field
matrices, with a uniformizer chosen from the proved valuation-ring structure. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualLocalCartan106
open Matrix ValuativeRel
variable (E : Type*) [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E]
variable (ι : Type*) [Fintype ι] [DecidableEq ι] [Nonempty ι]

theorem uniformizer_residue_zero :
    IsLocalRing.residue 𝒪[E] (ActualLocalUnitDecomposition.uniformizer E) = 0 := by
  apply (IsLocalRing.residue_eq_zero_iff _).mpr
  rw [(ActualLocalUnitDecomposition.uniformizer_irreducible E).maximalIdeal_eq]
  exact Ideal.subset_span (Set.mem_singleton _)

theorem hasCartan :
    CuspidalCartan105.HasCartan (ι := ι) (valuation E).integer.subtype
      (ActualLocalUnitDecomposition.uniformizer E)
      (ActualLocalUnitDecomposition.uniformizer_ne_zero E) :=
  DVRCartan106.hasCartan (F := E) _ (ActualLocalUnitDecomposition.uniformizer_irreducible E)

variable {C V : Type*} [Field C] [CharZero C] [AddCommGroup V] [Module C V]

/-- No arithmetic decomposition is supplied to this support bound. -/
theorem intertwining_support [Fintype 𝓀[E]]
    (σ : Representation C (GL ι 𝓀[E]) V) (hσ : CuspidalCartan105.Cuspidal σ)
    (g : GL ι E)
    (hg : IntertwiningAlong105.ExistsAt (ActualIntegralGeneralLinear.embedding E ι)
      (σ.comp (ActualResidueGeneralLinear.reduction E ι)) g) :
    ∃ c : Eˣ, ∃ u : GL ι 𝒪[E],
      g = GeneralLinearGroup.scalar ι c * ActualIntegralGeneralLinear.embedding E ι u :=
  CuspidalCartan105.intertwining_support (valuation E).integer.subtype
    (IsLocalRing.residue 𝒪[E]) IsLocalRing.residue_surjective
    (ActualLocalUnitDecomposition.uniformizer E)
    (ActualLocalUnitDecomposition.uniformizer_ne_zero E)
    (uniformizer_residue_zero E) (hasCartan E ι) σ hσ g hg

end PaperXI.ActualLocalCartan106
