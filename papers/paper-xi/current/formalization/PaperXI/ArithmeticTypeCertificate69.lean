import PaperXI.ArithmeticFieldInduction69
import PaperXI.FullIntertwiningLocus69
import Mathlib.Topology.LocallyConstant.Basic

/-! The actual base-field central character and the full intertwining-locus
application. No auxiliary scalar action or quotient compactness is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ArithmeticTypeCertificate69
open Matrix ValuativeRel Representation
open ActualEmbeddedUniformizer58 ActualFieldTypeQuotient69 ArithmeticFieldInduction69
open PaperXI.InductionIrreducibility PaperXI.SmoothDegreeQuotient

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F]
  [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (n : Type*) [Fintype n] [DecidableEq n] [Nonempty n]
  (ι : E →ₐ[F] Matrix n n F) (J : Subgroup (GeneralLinearGroup n F))
variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
  (Λ : Representation ℂ (fieldGroup F E n ι J) V) [IsIrreducible Λ]

/-- A character on the genuine multiplicative group of the base field. -/
def centralCharacter : Fˣ →* ℂˣ :=
  (scalarCharacter F E n ι J Λ).comp (scalarHom F E n ι J).rangeRestrict

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F]
  [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] [Nonempty n] in
theorem centralCharacter_action (a : Fˣ) (v : V) :
    Λ (scalarHom F E n ι J a) v = (centralCharacter F E n ι J Λ a : ℂ) • v :=
  scalarCharacter_action F E n ι J Λ ((scalarHom F E n ι J).rangeRestrict a) v

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F]
  [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] [Nonempty n] in
theorem induced_centralCharacter (a : Fˣ)
    (w : IndV (fieldGroup F E n ι J).subtype Λ) :
    ind (fieldGroup F E n ι J).subtype Λ (GeneralLinearGroup.scalar n a) w =
      (centralCharacter F E n ι J Λ a : ℂ) • w :=
  induced_scalar F E n ι J Λ ((scalarHom F E n ι J).rangeRestrict a) w

theorem scalarHom_continuous (hF : Continuous (algebraMap F E)) :
    Continuous (scalarHom F E n ι J) := by
  have hc := (unitsEmbedding_continuous F E n ι
    (algebraEmbedding_continuous F E n ι hF)).comp (hF.units_map (algebraMap F E).toMonoidHom)
  have he : (fun a : Fˣ => unitsEmbedding F E n ι
      (Units.map (algebraMap F E).toMonoidHom a)) = GeneralLinearGroup.scalar n := by
    funext a
    exact unitsEmbedding_baseScalar F E n ι a
  change Continuous (fun a : Fˣ => unitsEmbedding F E n ι
    (Units.map (algebraMap F E).toMonoidHom a)) at hc
  rw [he] at hc
  exact hc.subtype_mk _

/-- Smoothness of the actual finite-dimensional type gives local constancy
of its derived central character on F-times. -/
theorem centralCharacter_locallyConstant
    (hF : Continuous (algebraMap F E)) (hΛ : IsSmooth Λ) :
    IsLocallyConstant (centralCharacter F E n ι J Λ) := by
  let χ := centralCharacter F E n ι J Λ
  let U := Λ.ker.comap (scalarHom F E n ι J)
  have ho : IsOpen (U : Set Fˣ) :=
    (isOpen_kernel_of_smooth Λ hΛ).preimage (scalarHom_continuous F E n ι J hF)
  have hle : U ≤ χ.ker := by
    intro a ha
    change Λ (scalarHom F E n ι J a) = 1 at ha
    let : Nontrivial V := GeneratedIrreducibility.nontrivial_space Λ
    obtain ⟨v,hv⟩ := exists_ne (0 : V)
    have he := centralCharacter_action F E n ι J Λ a v
    rw [ha] at he
    have he' : (χ a : ℂ) • v = (1 : ℂ) • v := by
      simpa only [Module.End.one_apply, one_smul] using he.symm
    apply Units.ext
    exact smul_left_injective ℂ hv he'
  have hker : IsOpen (χ.ker : Set Fˣ) := Subgroup.isOpen_mono hle ho
  apply (IsLocallyConstant.iff_exists_open χ).mpr
  intro a
  refine ⟨{b : Fˣ | χ (b * a⁻¹) = 1},
    hker.preimage (continuous_id.mul continuous_const), ?_, ?_⟩
  · simp
  · intro b hb
    change χ (b * a⁻¹) = 1 at hb
    rw [map_mul, map_inv] at hb
    exact mul_inv_eq_one.mp hb

/-- The exact source-form of the full extended-type criterion. This applies
the proved arithmetic compact quotient and derived central character. -/
theorem from_full_intertwining_locus
    (hF : Continuous (algebraMap F E))
    (hJcompact : IsCompact (J : Set (GeneralLinearGroup n F)))
    (hJopen : IsOpen (J : Set (GeneralLinearGroup n F)))
    (ht : embeddedUniformizer F E n ι ∈ Subgroup.normalizer (J : Set (GeneralLinearGroup n F)))
    (hu : ∀ u : 𝒪[E]ˣ, unitsEmbedding F E n ι (ActualLocalUnitTopology.unitEmbedding E u) ∈ J)
    (hΛ : IsSmooth Λ)
    (hI : FullIntertwiningLocus69.locus (fieldGroup F E n ι J) Λ =
      (fieldGroup F E n ι J : Set (GeneralLinearGroup n F))) :
    Nontrivial (IndV (fieldGroup F E n ι J).subtype Λ) ∧
      IsSmooth (ind (fieldGroup F E n ι J).subtype Λ) ∧
      IsIrreducible (ind (fieldGroup F E n ι J).subtype Λ) ∧
      IsLocallyConstant (centralCharacter F E n ι J Λ) := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space Λ
  have hM := (FullIntertwiningLocus69.locus_eq_iff (fieldGroup F E n ι J) Λ).mp hI
  obtain ⟨hn,hs,hi⟩ := ArithmeticFieldInduction69.induction_package F E n ι J Λ
    hF hJcompact hJopen ht hu hΛ hM
  exact ⟨hn,hs,hi,centralCharacter_locallyConstant F E n ι J Λ hF hΛ⟩

end PaperXI.ArithmeticTypeCertificate69
