import PaperXI.IntersectionModel108
import PaperXI.FiniteJointQuotient108

/-! The finite model of the actual conjugate-intersection Hom space exists for
any continuous embedded compact group with a smooth finite-dimensional action. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CompactIntersection108
open Representation IntersectionModel108
variable {k K G W : Type*} [Field k] [Group K] [Group G]
  [AddCommGroup W] [Module k W]
  [TopologicalSpace K] [IsTopologicalGroup K] [CompactSpace K]
  [TopologicalSpace G] [IsTopologicalGroup G] [T2Space G]

omit [IsTopologicalGroup K] in
/-- The relation is closed in the compact product K × K. -/
theorem compact_pairs (ι : K →* G) (hi : Continuous ι) (g : G) :
    CompactSpace (pairs ι g) := by
  apply isCompact_iff_compactSpace.mp
  apply IsClosed.isCompact
  exact isClosed_eq (hi.comp continuous_snd)
    ((continuous_const.mul (hi.comp continuous_fst)).mul continuous_const)

omit [IsTopologicalGroup K] [CompactSpace K] in
/-- Smoothness is preserved by a continuous group homomorphism. -/
theorem smooth_comp {P : Type*} [Group P] [TopologicalSpace P]
    (ρ : Representation k K W) (hρ : SmoothDegreeQuotient.IsSmooth ρ)
    (p : P →* K) (hp : Continuous p) : SmoothDegreeQuotient.IsSmooth (ρ.comp p) := by
  intro v
  exact (hρ v).preimage hp

variable [FiniteDimensional k W]

/-- Both conjugate actions descend through one canonically specified quotient. -/
theorem finite_quotient (ι : K →* G) (hi : Continuous ι)
    (ρ : Representation k K W) (hρ : SmoothDegreeQuotient.IsSmooth ρ) (g : G) :
    Finite (FiniteJointQuotient108.quotient (ρ.comp (left ι g)) (ρ.comp (right ι g))) := by
  let : CompactSpace (pairs ι g) := compact_pairs ι hi g
  exact FiniteJointQuotient108.finite _ _
    (smooth_comp ρ hρ (left ι g) (continuous_fst.comp continuous_subtype_val))
    (smooth_comp ρ hρ (right ι g) (continuous_snd.comp continuous_subtype_val))

omit [TopologicalSpace K] [IsTopologicalGroup K] [CompactSpace K]
  [TopologicalSpace G] [IsTopologicalGroup G] [T2Space G] [FiniteDimensional k W] in
/-- This is the actual Hom dimension, on the original vector space. -/
theorem finrank_quotient (ι : K →* G) (ρ : Representation k K W) (g : G) :
    Module.finrank k (IntertwiningSpace107.space ι ρ g) =
      Module.finrank k (IntertwiningMap
        (FiniteJointQuotient108.first (ρ.comp (left ι g)) (ρ.comp (right ι g)))
        (FiniteJointQuotient108.second (ρ.comp (left ι g)) (ρ.comp (right ι g)))) := by
  exact finrank_model ι ρ g
    (QuotientGroup.mk' (FiniteJointQuotient108.kernel (ρ.comp (left ι g)) (ρ.comp (right ι g))))
    QuotientGroup.mk_surjective _ _ rfl rfl

end PaperXI.CompactIntersection108
