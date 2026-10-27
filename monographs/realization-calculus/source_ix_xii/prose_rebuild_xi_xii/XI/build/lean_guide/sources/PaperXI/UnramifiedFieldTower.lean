import PaperXI.UnramifiedBaseChangeFactor
import Mathlib.RingTheory.Finiteness.Basic
import Mathlib.LinearAlgebra.Dimension.Free

/-! # Recursive unramified local-field towers

This module constructs the upper field over the already constructed lower field,
using the checked residue-field equivalence to transport a finite residue tower.
The resulting map on the integer-degree unramified Weil models is defined by the
actual relative residue degree.  No absolute Weil group is asserted.
-/

set_option autoImplicit false
noncomputable section

namespace PaperXI.UnramifiedFieldTower

open PaperXI.LocalFieldResidueExtension
open PaperXI.IntegerRingComparison
open PaperXI.FiniteUnramifiedWeil
open PaperXI.ResidueDegreeBaseChange
open ValuativeRel
open scoped Classical

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]
variable (t : Type*) [Field t] [Algebra s t] [FiniteDimensional s t]

/-- The first spectral unramified extension in the tower. -/
abbrev LowerField := LocalFieldResidueExtension.field K s

/-- Transport the residue algebra structure on `t` across the checked
residue-field equivalence `𝓀[LowerField] ≃ s`. -/
noncomputable def residueTowerMap : 𝓀[LowerField K s] →+* t :=
  (algebraMap s t).comp (spectralResidueAlgEquiv K s).toRingHom

noncomputable local instance residueTowerAlgebra : Algebra 𝓀[LowerField K s] t :=
  (residueTowerMap K s t).toAlgebra

noncomputable local instance residueTowerFinite :
    FiniteDimensional 𝓀[LowerField K s] t := by
  let e₁ : s ≃+* 𝓀[LowerField K s] :=
    (spectralResidueAlgEquiv K s).symm.toRingEquiv
  let e₂ : t ≃+* t := RingEquiv.refl t
  exact Module.Finite.of_equiv_equiv e₁ e₂ (by
    ext x
    simp [e₁, e₂, residueTowerMap, RingHom.algebraMap_toAlgebra])

/-- The second spectral unramified extension, now constructed over the actual
first local field rather than directly over the original base. -/
abbrev UpperField := LocalFieldResidueExtension.field (LowerField K s) t



/-- The original base acts on the recursively constructed upper field through
the actual two-step field tower. -/
noncomputable local instance upperBaseAlgebra : Algebra K (UpperField K s t) :=
  ((algebraMap (LowerField K s) (UpperField K s t)).comp
    (algebraMap K (LowerField K s))).toAlgebra

noncomputable local instance upperBaseTower :
    IsScalarTower K (LowerField K s) (UpperField K s t) :=
  IsScalarTower.of_algebraMap_eq fun _ => rfl

/-- The actual inclusion of the lower local field into the recursive upper
local field, viewed over the original base. -/
noncomputable def lowerToUpper :
    LowerField K s →ₐ[K] UpperField K s t :=
  IsScalarTower.toAlgHom K (LowerField K s) (UpperField K s t)

omit [FiniteDimensional s t] in
/-- The transported residue degree is the original degree `[t:s]`. -/
theorem residue_finrank :
    Module.finrank 𝓀[LowerField K s] t = Module.finrank s t := by
  apply Algebra.finrank_eq_of_equiv_equiv
    (spectralResidueAlgEquiv K s).toRingEquiv (RingEquiv.refl t)
  ext x
  simp [residueTowerMap, RingHom.algebraMap_toAlgebra]

/-- The actual relative degree of the recursive local-field extension. -/
theorem relative_degree :
    Module.finrank (LowerField K s) (UpperField K s t) = Module.finrank s t := by
  rw [LocalFieldResidueExtension.degree]
  exact residue_finrank K s t


/-- The total degree is the product of the two actual residue degrees. -/
theorem total_degree :
    Module.finrank K (UpperField K s t) =
      Module.finrank 𝓀[K] s * Module.finrank s t := by
  rw [← Module.finrank_mul_finrank K (LowerField K s) (UpperField K s t),
    LocalFieldResidueExtension.degree K s, relative_degree K s t]

/-- The residue field of the recursive upper local field is the declared top
finite field. -/
noncomputable def upperResidueAlgEquiv :
    𝓀[UpperField K s t] ≃ₐ[𝓀[LowerField K s]] t :=
  spectralResidueAlgEquiv (LowerField K s) t

/-- The recursive upper extension is unramified at the level of spectral
integer rings. -/
theorem relative_ramificationIdx_one :
    (IsLocalRing.maximalIdeal 𝒪[UpperField K s t]).ramificationIdx
      𝒪[LowerField K s] = 1 :=
  spectral_ramificationIdx_one (LowerField K s) t

/-- Restriction on the current integer-degree unramified Weil models.  In degree
coordinates it is multiplication by the actual relative field degree. -/
noncomputable def restriction :
    UnramifiedWeil (LowerField K s) t →* UnramifiedWeil K s :=
  (degreeEquiv K s).symm.toMonoidHom.comp
    ((integerDegreeDilation (Module.finrank s t)).comp
      (degreeEquiv (LowerField K s) t).toMonoidHom)


/-- In canonical degree coordinates, field-tower restriction is literally the
Block 40 integer-degree dilation. -/
theorem restriction_degree_square :
    (degreeEquiv K s).toMonoidHom.comp (restriction K s t) =
      (integerDegreeDilation (Module.finrank s t)).comp
        (degreeEquiv (LowerField K s) t).toMonoidHom :=
  rfl

@[simp]
theorem restriction_degree (w : UnramifiedWeil (LowerField K s) t) :
    Multiplicative.toAdd (degreeEquiv K s (restriction K s t w)) =
      (Module.finrank s t : ℤ) *
        Multiplicative.toAdd (degreeEquiv (LowerField K s) t w) := by
  simp [restriction, integerDegreeDilation]

/-- Upper geometric Frobenius restricts to the relative-degree power of lower
geometric Frobenius. -/
@[simp]
theorem restriction_geometricLift :
    restriction K s t (geometricLift (LowerField K s) t) =
      geometricLift K s ^ (Module.finrank s t : ℕ) := by
  apply (degreeEquiv K s).injective
  apply Multiplicative.toAdd.injective
  calc
    Multiplicative.toAdd
        (degreeEquiv K s
          (restriction K s t (geometricLift (LowerField K s) t))) =
        (Module.finrank s t : ℤ) *
          Multiplicative.toAdd
            (degreeEquiv (LowerField K s) t
              (geometricLift (LowerField K s) t)) :=
      restriction_degree K s t _
    _ = (Module.finrank s t : ℤ) := by
      rw [degreeEquiv_apply, degree_geometricLift]
      simp
    _ = Multiplicative.toAdd
        (degreeEquiv K s (geometricLift K s ^ Module.finrank s t)) := by
      rw [map_pow, degreeEquiv_apply, degree_geometricLift]
      simp

/-- The restriction map is injective. -/
theorem restriction_injective : Function.Injective (restriction K s t) := by
  intro a b h
  apply (degreeEquiv (LowerField K s) t).injective
  apply Multiplicative.toAdd.injective
  have hf_nat : Module.finrank s t ≠ 0 := Module.finrank_pos.ne'
  have hf : (Module.finrank s t : ℤ) ≠ 0 := by
    exact_mod_cast hf_nat
  have hdeg :
      (Module.finrank s t : ℤ) *
          Multiplicative.toAdd (degreeEquiv (LowerField K s) t a) =
        (Module.finrank s t : ℤ) *
          Multiplicative.toAdd (degreeEquiv (LowerField K s) t b) := by
    calc
      (Module.finrank s t : ℤ) *
          Multiplicative.toAdd (degreeEquiv (LowerField K s) t a) =
        Multiplicative.toAdd (degreeEquiv K s (restriction K s t a)) :=
          (restriction_degree K s t a).symm
      _ = Multiplicative.toAdd (degreeEquiv K s (restriction K s t b)) :=
        congrArg (fun w : UnramifiedWeil K s =>
          Multiplicative.toAdd (degreeEquiv K s w)) h
      _ = (Module.finrank s t : ℤ) *
          Multiplicative.toAdd (degreeEquiv (LowerField K s) t b) :=
        restriction_degree K s t b
  exact mul_left_cancel₀ hf hdeg


/-- The image is exactly the subgroup whose lower integer degrees are divisible
by the actual relative residue degree. -/
theorem restriction_range :
    (restriction K s t).range =
      periodSubgroup (MonoidHom.id (ResidueGalois K s))
        (geometricFrobenius K s) (Module.finrank s t) := by
  ext w
  constructor
  · rintro ⟨v, rfl⟩
    rw [mem_periodSubgroup]
    rw [← degreeEquiv_apply]
    rw [restriction_degree]
    exact dvd_mul_right _ _
  · intro hw
    have hd : (Module.finrank s t : ℤ) ∣
        Multiplicative.toAdd (degreeEquiv K s w) := by
      simpa only [degreeEquiv_apply] using
        (mem_periodSubgroup _ _ _ w).mp hw
    obtain ⟨m, hm⟩ := hd
    let v : UnramifiedWeil (LowerField K s) t :=
      (degreeEquiv (LowerField K s) t).symm (Multiplicative.ofAdd m)
    refine ⟨v, ?_⟩
    apply (degreeEquiv K s).injective
    apply Multiplicative.toAdd.injective
    rw [restriction_degree]
    have hv : Multiplicative.toAdd
        (degreeEquiv (LowerField K s) t v) = m := by
      simp [v]
    rw [hv]
    simpa only [degreeEquiv_apply] using hm.symm

/-- Restriction is an equivalence onto the exact degree-period subgroup. -/
noncomputable def restrictionEquivPeriod :
    UnramifiedWeil (LowerField K s) t ≃*
      periodSubgroup (MonoidHom.id (ResidueGalois K s))
        (geometricFrobenius K s) (Module.finrank s t) :=
  (MonoidHom.ofInjective (restriction_injective K s t)).trans
    (MulEquiv.subgroupCongr (restriction_range K s t))

/-- Any homomorphism between the same current Weil models with the genuine
relative-degree formula is the restriction map constructed above.  This is the
uniqueness principle used to reconcile older Henselian tower embeddings with
the newer spectral models. -/
theorem restriction_unique
    (φ : UnramifiedWeil (LowerField K s) t →* UnramifiedWeil K s)
    (hφ : ∀ w, Multiplicative.toAdd (degreeEquiv K s (φ w)) =
      (Module.finrank s t : ℤ) *
        Multiplicative.toAdd (degreeEquiv (LowerField K s) t w)) :
    φ = restriction K s t := by
  apply MonoidHom.ext
  intro w
  apply (degreeEquiv K s).injective
  apply Multiplicative.toAdd.injective
  exact (hφ w).trans (restriction_degree K s t w).symm


section Representation

variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

/-- Restriction of a representation along the actual recursive field-tower map. -/
def restrictRepresentation
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    Representation ℂ (UnramifiedWeil (LowerField K s) t) V :=
  ρ.comp (restriction K s t)

omit [FiniteDimensional ℂ V] in
@[simp]
theorem restrictRepresentation_geometricLift
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    restrictRepresentation K s t ρ (geometricLift (LowerField K s) t) =
      ρ (geometricLift K s ^ Module.finrank s t) := by
  simp [restrictRepresentation]

/-- The Frobenius polynomial after actual tower restriction is the reverse
characteristic polynomial of the relative-degree Frobenius power. -/
theorem restriction_frobeniusPolynomial
    (ρ : Representation ℂ (UnramifiedWeil K s) V) :
    frobeniusPolynomial (LowerField K s) t (restrictRepresentation K s t ρ) =
      (LinearMap.charpoly
        (ρ (geometricLift K s ^ Module.finrank s t))).reverse := by
  rw [frobeniusPolynomial, restrictRepresentation_geometricLift]

end Representation

end PaperXI.UnramifiedFieldTower
