import PaperXI.ActualFieldTypeQuotient69
import PaperXI.DerivedCentralCharacter69
import PaperXI.CompactModCenterInduction68
import Mathlib.Analysis.Complex.Polynomial.Basic

/-! The compact-mod-center induction theorem specialized to literal local-field matrices.
The actual field scalar subgroup and compact quotient are constructed. The common
scalar character is derived from finite-dimensional irreducibility, not supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ArithmeticFieldInduction69
open Matrix ValuativeRel Representation
open ActualEmbeddedUniformizer58 ActualFieldTypeQuotient69
open PaperXI.InductionIrreducibility PaperXI.SmoothDegreeQuotient

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F]
  [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (ι : E →ₐ[F] Matrix n n F) (J : Subgroup (GeneralLinearGroup n F))
variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
  (Λ : Representation ℂ (fieldGroup F E n ι J) V) [IsIrreducible Λ]

omit [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] [Nonempty n] in
/-- Openness of the compact type subgroup implies openness of the actual field join. -/
theorem fieldGroup_open (hJ : IsOpen (J : Set (GeneralLinearGroup n F))) :
    IsOpen (fieldGroup F E n ι J : Set (GeneralLinearGroup n F)) :=
  Subgroup.isOpen_mono le_sup_left hJ

/-- The derived scalar character on the literal base-field scalar subgroup. -/
def scalarCharacter : scalarSubgroup F E n ι J →* ℂˣ :=
  DerivedCentralCharacter69.character Λ (scalarSubgroup F E n ι J)
    (fun z g => Subtype.ext (scalar_central F E n ι J z g).eq)

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F]
  [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] [Nonempty n] in
theorem scalarCharacter_action (z : scalarSubgroup F E n ι J) (v : V) :
    Λ (z : fieldGroup F E n ι J) v = (scalarCharacter F E n ι J Λ z : ℂ) • v :=
  DerivedCentralCharacter69.character_apply Λ (scalarSubgroup F E n ι J)
    (fun z g => Subtype.ext (scalar_central F E n ι J z g).eq) z v

/-- Actual arithmetic specialization: no compact-quotient or scalar-character
hypothesis is received. The full-H intertwining condition remains explicit and
must be obtained from the supplied genuine extended type. -/
theorem induction_package
    (hF : Continuous (algebraMap F E))
    (hJcompact : IsCompact (J : Set (GeneralLinearGroup n F)))
    (hJopen : IsOpen (J : Set (GeneralLinearGroup n F)))
    (ht : embeddedUniformizer F E n ι ∈ Subgroup.normalizer (J : Set (GeneralLinearGroup n F)))
    (hu : ∀ u : 𝒪[E]ˣ, unitsEmbedding F E n ι (ActualLocalUnitTopology.unitEmbedding E u) ∈ J)
    (hΛ : IsSmooth Λ)
    (hM : ∀ g : GeneralLinearGroup n F, g ∉ fieldGroup F E n ι J →
      ∀ A : IntertwiningMap
        (Λ.comp (intersectionSubgroup (fieldGroup F E n ι J) g).subtype)
        (Λ.comp (intersectionConjugation (fieldGroup F E n ι J) g)), A = 0) :
    Nontrivial (IndV (fieldGroup F E n ι J).subtype Λ) ∧
      IsSmooth (ind (fieldGroup F E n ι J).subtype Λ) ∧
      IsIrreducible (ind (fieldGroup F E n ι J).subtype Λ) := by
  let : CompactSpace (fieldGroup F E n ι J ⧸ scalarSubgroup F E n ι J) :=
    quotient_compact F E n ι J hF hJcompact ht hu
  exact CompactModCenterInduction68.induction_package
    (fieldGroup F E n ι J) Λ (scalarSubgroup F E n ι J)
    (scalarCharacter F E n ι J Λ)
    (scalar_central F E n ι J)
    (scalarCharacter_action F E n ι J Λ)
    (fieldGroup_open F E n ι J hJopen) hΛ hM

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F]
  [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] [Nonempty n] in
/-- The same derived character acts on every vector of the actual induced carrier. -/
theorem induced_scalar (z : scalarSubgroup F E n ι J)
    (w : IndV (fieldGroup F E n ι J).subtype Λ) :
    ind (fieldGroup F E n ι J).subtype Λ
      (((z : fieldGroup F E n ι J) : GeneralLinearGroup n F)) w =
        (scalarCharacter F E n ι J Λ z : ℂ) • w := by
  exact CompactModCenterInduction68.induced_central_scalar
    (fieldGroup F E n ι J) Λ (z : fieldGroup F E n ι J)
    (scalar_central F E n ι J z)
    (scalarCharacter F E n ι J Λ z : ℂ)
    (scalarCharacter_action F E n ι J Λ z) w

end PaperXI.ArithmeticFieldInduction69
