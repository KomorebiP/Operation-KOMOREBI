import PaperXI.SpectralLocalField
import Mathlib.RingTheory.Polynomial.Subring
import Mathlib.FieldTheory.Minpoly.IsIntegrallyClosed

/-!
# Comparison of the algebraic and spectral integer rings

For the unramified residue extension constructed in `LocalFieldResidueExtension`,
the finite-extension spectral norm has unit ball equal to the image of the
algebraically constructed complete DVR.  The proof proceeds through the exact
integrality criterion over the base local-field integers.
-/

set_option autoImplicit false
noncomputable section

namespace PaperXI.IntegerRingComparison

open PaperXI.LocalFieldResidueExtension
open PaperXI.CanonicalDVRValuation
open PaperXI.SpectralLocalField
open ValuativeRel
open scoped WithZero Polynomial

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

private local instance baseValued : Valued K (ValueGroupWithZero K) := inferInstance

private local instance baseRankOne :
    Valuation.RankOne (Valued.v (R := K) (Γ₀ := ValueGroupWithZero K)) :=
  { hom' := IsRankLeOne.nonempty.some.emb (R := K).comp
      MonoidWithZeroHom.ValueGroup₀.embedding
    strictMono' := IsRankLeOne.nonempty.some.strictMono.comp
      MonoidWithZeroHom.ValueGroup₀.embedding_strictMono }

private local instance baseNormedField : NormedField K :=
  Valued.toNormedField K (ValueGroupWithZero K)

private local instance baseNontriviallyNormedField : NontriviallyNormedField K :=
  Valued.toNontriviallyNormedField K (ValueGroupWithZero K)

abbrev UpperRing := LocalFieldResidueExtension.ring K s
abbrev UpperField := LocalFieldResidueExtension.field K s

/-- Spectral integrality is exactly algebraic integrality over the base local
field integers. -/
theorem norm_le_one_iff_isIntegral (x : UpperField K s) :
    ‖x‖ ≤ 1 ↔ IsIntegral 𝒪[K] x := by
  constructor
  · intro hx
    have hxalg : IsIntegral K x := Algebra.IsIntegral.isIntegral x
    have hmonic : (minpoly K x).Monic := minpoly.monic hxalg
    have hcoeffNorm : ∀ n : ℕ, ‖(minpoly K x).coeff n‖ ≤ 1 := by
      have hspectral : spectralNorm K (UpperField K s) x ≤ 1 := by
        simpa [SpectralLocalField.norm_eq_spectralNorm] using hx
      exact (spectralValue_le_one_iff hmonic).mp hspectral
    have hcoeff : (↑(minpoly K x).coeffs : Set K) ⊆ (𝒪[K] : Set K) := by
      intro c hc
      rw [Finset.mem_coe, Polynomial.mem_coeffs_iff] at hc
      obtain ⟨n, -, rfl⟩ := hc
      have hv : Valued.v ((minpoly K x).coeff n) ≤ 1 :=
        (Valued.toNormedField.norm_le_one_iff).mp (hcoeffNorm n)
      change (ValuativeRel.valuation K) ((minpoly K x).coeff n) ≤ 1
      exact hv
    let p : Polynomial 𝒪[K] := Polynomial.toSubring (minpoly K x) 𝒪[K] hcoeff
    have hpmonic : p.Monic :=
      (Polynomial.monic_toSubring (minpoly K x) 𝒪[K] hcoeff).2 hmonic
    have hpmapSubtype : p.map (Subring.subtype 𝒪[K]) = minpoly K x := by
      dsimp [p]
      exact Polynomial.map_toSubring (minpoly K x) 𝒪[K] hcoeff
    have hpmap : p.map (algebraMap 𝒪[K] K) = minpoly K x := by
      rw [Algebra.algebraMap_ofSubring]
      exact hpmapSubtype
    have hpeval : Polynomial.aeval x p = 0 := by
      rw [← Polynomial.aeval_map_algebraMap K x p, hpmap]
      exact minpoly.aeval K x
    exact ⟨p, hpmonic, hpeval⟩
  · intro hx
    have hxalg : IsIntegral K x := Algebra.IsIntegral.isIntegral x
    rw [SpectralLocalField.norm_eq_spectralNorm, spectralNorm,
      spectralValue_le_one_iff (minpoly.monic hxalg)]
    intro n
    rw [minpoly.isIntegrallyClosed_eq_field_fractions' K hx, Polynomial.coeff_map]
    change ‖(((minpoly 𝒪[K] x).coeff n : 𝒪[K]) : K)‖ ≤ 1
    rw [Valued.toNormedField.norm_le_one_iff]
    change (ValuativeRel.valuation K) (((minpoly 𝒪[K] x).coeff n : 𝒪[K]) : K) ≤ 1
    exact ((minpoly 𝒪[K] x).coeff n).property

omit [IsUniformAddGroup K] in
/-- Algebraic integrality over the base integer ring is equivalent to coming
from the constructed upper DVR. -/
theorem isIntegral_iff_exists_upper_lift (x : UpperField K s) :
    IsIntegral 𝒪[K] x ↔
      ∃ c : UpperRing K s,
        algebraMap (UpperRing K s) (UpperField K s) c = x := by
  constructor
  · intro hx
    have hxC : IsIntegral (UpperRing K s) x := hx.tower_top
    exact IsIntegrallyClosedIn.isIntegral_iff.mp hxC
  · rintro ⟨c, rfl⟩
    exact (IsIntegral.of_finite 𝒪[K] c).algebraMap

/-- Literal equality in the ambient fraction field between the algebraically
constructed DVR and the spectral local-field integer ring. -/
theorem upper_integerRing_eq_spectral :
    Subring.map (algebraMap (UpperRing K s) (UpperField K s)) ⊤ =
      𝒪[UpperField K s] := by
  ext x
  constructor
  · rintro ⟨c, -, rfl⟩
    exact (SpectralLocalField.mem_integer_iff_norm_le_one K s _).2 <|
      (norm_le_one_iff_isIntegral K s _).2
        ((IsIntegral.of_finite 𝒪[K] c).algebraMap)
  · intro hx
    have hnorm := (SpectralLocalField.mem_integer_iff_norm_le_one K s x).1 hx
    obtain ⟨c, hc⟩ :=
      (isIntegral_iff_exists_upper_lift K s x).1
        ((norm_le_one_iff_isIntegral K s x).1 hnorm)
    exact ⟨c, by simp, hc⟩


/-- The algebraically constructed upper DVR is canonically ring-equivalent to
    the spectral local field's integer ring. -/
noncomputable def upperRingEquivSpectralIntegers :
    UpperRing K s ≃+* 𝒪[UpperField K s] :=
  (Subring.topEquiv : (⊤ : Subring (UpperRing K s)) ≃+* UpperRing K s).symm |>.trans
    (((⊤ : Subring (UpperRing K s)).equivMapOfInjective
      (algebraMap (UpperRing K s) (UpperField K s))
      (FaithfulSMul.algebraMap_injective (UpperRing K s) (UpperField K s))).trans
        (RingEquiv.subringCongr (upper_integerRing_eq_spectral K s)))

/-- The base integer ring acts on the spectral integer ring through the checked
    identification with the algebraic upper DVR. -/
noncomputable instance spectralIntegerAlgebra :
    Algebra 𝒪[K] 𝒪[UpperField K s] :=
  RingHom.toAlgebra
    ((upperRingEquivSpectralIntegers K s).toRingHom.comp
      (algebraMap 𝒪[K] (UpperRing K s)))

noncomputable instance spectralIntegerAlgebra_isLocal :
    IsLocalHom (algebraMap 𝒪[K] 𝒪[UpperField K s]) := by
  change IsLocalHom
    ((upperRingEquivSpectralIntegers K s).toRingHom.comp
      (algebraMap 𝒪[K] (UpperRing K s)))
  refine ⟨fun a ha => ?_⟩
  have haUpper : IsUnit (algebraMap 𝒪[K] (UpperRing K s) a) :=
    (isLocalHom_equiv (upperRingEquivSpectralIntegers K s)).map_nonunit _ ha
  exact (inferInstance : IsLocalHom (algebraMap 𝒪[K] (UpperRing K s))).map_nonunit a haUpper

/-- The integer-ring comparison is compatible with the original base integer
    ring algebra structures. -/
noncomputable def upperRingAlgEquivSpectralIntegers :
    UpperRing K s ≃ₐ[𝒪[K]] 𝒪[UpperField K s] :=
  AlgEquiv.ofRingEquiv (f := upperRingEquivSpectralIntegers K s) (fun _ => rfl)

noncomputable instance spectralIntegersEtale :
    Algebra.Etale 𝒪[K] 𝒪[UpperField K s] := by
  let _ : Algebra.Etale 𝒪[K] (UpperRing K s) :=
    PaperXI.ResidueExtensionRealization.etale 𝒪[K] s
  exact Algebra.Etale.of_equiv (upperRingAlgEquivSpectralIntegers K s)

@[simp]
theorem upperRingEquivSpectralIntegers_coe (x : UpperRing K s) :
    (((upperRingEquivSpectralIntegers K s x : 𝒪[UpperField K s]) :
      UpperField K s)) = algebraMap (UpperRing K s) (UpperField K s) x := by
  rfl

/-- The integer-ring equivalence carries the algebraic maximal ideal to the
    spectral local field's maximal ideal. -/
theorem upper_maximalIdeal_map :
    Ideal.map (upperRingEquivSpectralIntegers K s).toRingHom
      (IsLocalRing.maximalIdeal (UpperRing K s)) =
        IsLocalRing.maximalIdeal 𝒪[UpperField K s] :=
  IsLocalRing.map_ringEquiv_maximalIdeal
    (upperRingEquivSpectralIntegers K s)

/-- The spectral integer extension has ramification index one over the base
    local-field integers. -/
theorem spectral_ramificationIdx_one :
    (IsLocalRing.maximalIdeal 𝒪[UpperField K s]).ramificationIdx 𝒪[K] = 1 :=
  Ideal.ramificationIdx_eq_one _ _

/-- The residue field of the algebraic upper DVR is canonically ring-equivalent
    to the residue field of the spectral local field. -/
noncomputable def upperResidueFieldEquivSpectral :
    IsLocalRing.ResidueField (UpperRing K s) ≃+* 𝓀[UpperField K s] :=
  IsLocalRing.ResidueField.mapEquiv (upperRingEquivSpectralIntegers K s)

/-- The residue-field comparison respects the base residue field. -/
noncomputable def upperResidueFieldAlgEquivSpectral :
    IsLocalRing.ResidueField (UpperRing K s) ≃ₐ[𝓀[K]] 𝓀[UpperField K s] :=
  IsLocalRing.ResidueField.mapAlgEquiv'
    (upperRingAlgEquivSpectralIntegers K s)

/-- The spectral local field has the prescribed residue field as an algebra over
    the original residue field. -/
noncomputable def spectralResidueAlgEquiv :
    𝓀[UpperField K s] ≃ₐ[𝓀[K]] s :=
  (upperResidueFieldAlgEquivSpectral K s).symm.trans
    (PaperXI.ResidueExtensionRealization.residueEquiv 𝒪[K] s)

/-- The spectral local field has the prescribed residue field, as an actual ring
    equivalence. -/
noncomputable def spectralResidueEquiv :
    𝓀[UpperField K s] ≃+* s :=
  (upperResidueFieldEquivSpectral K s).symm.trans
    (PaperXI.ResidueExtensionRealization.residueEquiv 𝒪[K] s).toRingEquiv

/-- The spectral residue degree is exactly the prescribed residue-extension
    degree. -/
theorem spectral_residue_finrank :
    Module.finrank 𝓀[K] 𝓀[UpperField K s] = Module.finrank 𝓀[K] s :=
  LinearEquiv.finrank_eq (spectralResidueAlgEquiv K s).toLinearEquiv

/-- The field degree equals the spectral residue degree, the expected numerical
    identity for the constructed unramified extension. -/
theorem upper_degree_eq_spectral_residue_finrank :
    Module.finrank K (UpperField K s) = Module.finrank 𝓀[K] 𝓀[UpperField K s] := by
  rw [LocalFieldResidueExtension.degree K s, spectral_residue_finrank K s]

/-- Cardinality of the spectral residue field agrees with the prescribed finite
    residue extension. -/
theorem natCard_spectralResidue :
    Nat.card 𝓀[UpperField K s] = Nat.card s :=
  Nat.card_congr (spectralResidueEquiv K s).toEquiv

end PaperXI.IntegerRingComparison
