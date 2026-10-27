import PaperXI.ActualCharacterCandidate108
import PaperXI.FiniteIntersectionCriterion108

/-! The canonical finite quotient for the actual first-subgroup intertwining
space. This proves existence of the finite model, not its arithmetic profile. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualIntersection108
open Matrix ValuativeRel Representation
open ActualCharacterType61 ActualCuspidalCandidate105 IntersectionModel108
variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)
variable {W : Type*} [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  (κ : Representation ℂ (compact F E m n e D θ) W)

abbrev embedding := (compact F E m n e D θ).subtype.comp
  (firstSubgroup F E m n e D θ).subtype

abbrev restriction := κ.comp (firstSubgroup F E m n e D θ).subtype

abbrev quotient (g : GL n F) := FiniteJointQuotient108.quotient
  ((restriction F E m n e D θ κ).comp (left (embedding F E m n e D θ) g))
  ((restriction F E m n e D θ κ).comp (right (embedding F E m n e D θ) g))

/-- Finiteness at every ambient element, proved for the same prescribed kappa. -/
theorem finite (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (hκ : SmoothDegreeQuotient.IsSmooth κ) (g : GL n F) :
    Finite (quotient F E m n e D θ κ g) := by
  let : CompactSpace (compact F E m n e D θ) := isCompact_iff_compactSpace.mp
    (compactGroup_compact_open F E m n e D θ hF hDo).1
  let : CompactSpace (firstSubgroup F E m n e D θ) := isCompact_iff_compactSpace.mp
    ((firstSubgroup F E m n e D θ).isClosed_of_isOpen
      (firstSubgroup_open F E m n e D θ hF)).isCompact
  exact CompactIntersection108.finite_quotient (embedding F E m n e D θ)
    (continuous_subtype_val.comp continuous_subtype_val)
    (restriction F E m n e D θ κ)
    (CompactIntersection108.smooth_comp κ hκ
      (firstSubgroup F E m n e D θ).subtype continuous_subtype_val) g

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m]
  [Nonempty n] [FiniteDimensional ℂ W] in
/-- Actual operator dimension equals the canonical quotient Hom dimension. -/
theorem dimension (g : GL n F) :
    Module.finrank ℂ (IntertwiningSpace107.space (embedding F E m n e D θ)
      (restriction F E m n e D θ κ) g) =
    Module.finrank ℂ (IntertwiningMap
      (FiniteJointQuotient108.first
        ((restriction F E m n e D θ κ).comp (left (embedding F E m n e D θ) g))
        ((restriction F E m n e D θ κ).comp (right (embedding F E m n e D θ) g)))
      (FiniteJointQuotient108.second
        ((restriction F E m n e D θ κ).comp (left (embedding F E m n e D θ) g))
        ((restriction F E m n e D θ κ).comp (right (embedding F E m n e D θ) g)))) :=
  CompactIntersection108.finrank_quotient _ _ _

end PaperXI.ActualIntersection108
