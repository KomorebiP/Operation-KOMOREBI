import PaperXI.ResidueFrobeniusAttachment
import PaperXI.ResidueDegreeBaseChange
import Mathlib.RepresentationTheory.Irreducible

/-! # Finite unramified Weil quotient of the constructed local field -/

set_option autoImplicit false
noncomputable section

namespace PaperXI.FiniteUnramifiedWeil

open PaperXI.LocalFieldResidueExtension
open PaperXI.IntegerRingComparison
open PaperXI.ResidueWeil
open PaperXI.ResidueDegreeBaseChange
open ValuativeRel
open scoped Classical

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

/-- The integer-degree unramified Weil model attached to the actual residue
Galois group and geometric Frobenius. -/
abbrev UnramifiedWeil :=
  Pullback (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)

/-- Its degree is an exact group equivalence with the infinite cyclic group. -/
noncomputable def degreeEquiv :
    UnramifiedWeil K s ≃* Multiplicative ℤ where
  toFun := degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
  invFun n :=
    ⟨((geometricFrobenius K s) ^ Multiplicative.toAdd n, n), rfl⟩
  left_inv w := by
    apply Subtype.ext
    apply Prod.ext
    · exact w.property.symm
    · rfl
  right_inv n := rfl
  map_mul' _ _ := rfl

@[simp]
theorem degreeEquiv_apply (w : UnramifiedWeil K s) :
    degreeEquiv K s w = degree (MonoidHom.id (ResidueGalois K s))
      (geometricFrobenius K s) w :=
  rfl

/-- Projection is exactly the geometric Frobenius power prescribed by degree. -/
theorem projection_eq_geometric_zpow_degree (w : UnramifiedWeil K s) :
    projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w =
      geometricFrobenius K s ^ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) := by
  exact w.property

/-- The degree map is bijective; this model retains the full integer degree. -/
theorem degree_bijective : Function.Bijective
    (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)) :=
  (degreeEquiv K s).bijective

/-- Inertia in the unramified Weil model is trivial. -/
theorem inertia_eq_bot :
    (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)).ker = ⊥ := by
  exact (MonoidHom.ker_eq_bot_iff _).2 (degreeEquiv K s).injective

/-- The canonical degree-one lift of geometric Frobenius. -/
noncomputable def geometricLift : UnramifiedWeil K s :=
  (degreeEquiv K s).symm (Multiplicative.ofAdd 1)

@[simp]
theorem degree_geometricLift :
    degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
      (geometricLift K s) = Multiplicative.ofAdd 1 :=
  (degreeEquiv K s).apply_symm_apply _

@[simp]
theorem projection_geometricLift :
    projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
      (geometricLift K s) = geometricFrobenius K s := by
  rw [projection_eq_geometric_zpow_degree, degree_geometricLift]
  simp

/-- The inverse lift is arithmetic Frobenius and has degree minus one. -/
noncomputable def arithmeticLift : UnramifiedWeil K s :=
  (geometricLift K s)⁻¹

@[simp]
theorem degree_arithmeticLift :
    degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
      (arithmeticLift K s) = Multiplicative.ofAdd (-1 : ℤ) := by
  rw [arithmeticLift, map_inv, degree_geometricLift]
  rfl

@[simp]
theorem projection_arithmeticLift :
    projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
      (arithmeticLift K s) = arithmeticFrobenius K s := by
  rw [arithmeticLift, map_inv, projection_geometricLift]
  simp [geometricFrobenius]


/-- Every element of the integer-degree model is the corresponding integral
power of the distinguished geometric-Frobenius lift. -/
theorem eq_geometricLift_zpow_degree (w : UnramifiedWeil K s) :
    w = geometricLift K s ^ Multiplicative.toAdd
      (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) := by
  calc
    w = (degreeEquiv K s).symm ((degreeEquiv K s) w) :=
      ((degreeEquiv K s).symm_apply_apply w).symm
    _ = (degreeEquiv K s).symm (Multiplicative.ofAdd 1) ^
        Multiplicative.toAdd ((degreeEquiv K s) w) :=
      MonoidHom.apply_mint (UnramifiedWeil K s)
        (degreeEquiv K s).symm.toMonoidHom ((degreeEquiv K s) w)
    _ = geometricLift K s ^ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) := rfl

/-- The geometric-Frobenius lift generates the whole unramified Weil model. -/
theorem geometricLift_zpowers_eq_top :
    Subgroup.zpowers (geometricLift K s) = ⊤ := by
  rw [Subgroup.eq_top_iff']
  intro w
  rw [Subgroup.mem_zpowers_iff]
  exact ⟨Multiplicative.toAdd
    (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w),
      (eq_geometricLift_zpow_degree K s w).symm⟩

/-- The integer-degree unramified Weil model is commutative. -/
instance unramifiedWeil_isMulCommutative : IsMulCommutative (UnramifiedWeil K s) :=
  ⟨⟨fun a b => by
    apply (degreeEquiv K s).injective
    exact mul_comm _ _⟩⟩

open scoped IsMulCommutative in
/-- Every finite-dimensional irreducible complex representation of this
unramified model is one-dimensional. -/
theorem irreducible_finrank_eq_one {V : Type*} [AddCommGroup V] [Module ℂ V]
    [FiniteDimensional ℂ V]
    (ρ : Representation ℂ (UnramifiedWeil K s) V) [Representation.IsIrreducible ρ] :
    Module.finrank ℂ V = 1 := by
  exact Representation.IsIrreducible.finrank_eq_one_of_isMulCommutative ρ


/-- Projection from the infinite-degree model onto the residue Galois group is surjective. -/
theorem projection_surjective : Function.Surjective
    (projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)) := by
  intro σ
  have hσ : σ ∈ Subgroup.zpowers (geometricFrobenius K s) := by
    rw [geometricFrobenius_zpowers_eq_top K s]
    trivial
  obtain ⟨m, hm⟩ := Subgroup.mem_zpowers_iff.mp hσ
  refine ⟨⟨(σ, Multiplicative.ofAdd m), ?_⟩, rfl⟩
  change σ = geometricFrobenius K s ^ m
  exact hm.symm

/-- The projection kernel consists exactly of degrees divisible by the residue degree. -/
theorem projection_ker_eq_period :
    (projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)).ker =
      periodSubgroup (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
        (ResidueDegree K s) := by
  ext w
  constructor
  · intro hw
    change projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w = 1 at hw
    have hpow : geometricFrobenius K s ^ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) = 1 := by
      rw [← projection_eq_geometric_zpow_degree K s]
      exact hw
    have hd : (orderOf (geometricFrobenius K s) : ℤ) ∣ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) :=
      (orderOf_dvd_iff_zpow_eq_one).2 hpow
    apply (mem_periodSubgroup _ _ _ _).2
    simpa only [geometricFrobenius_order_eq_fieldDegree K s] using hd
  · intro hw
    have hd : (ResidueDegree K s : ℤ) ∣ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) :=
      (mem_periodSubgroup _ _ _ _).1 hw
    have hd' : (orderOf (geometricFrobenius K s) : ℤ) ∣ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) := by
      simpa only [geometricFrobenius_order_eq_fieldDegree K s] using hd
    have hpow : geometricFrobenius K s ^ Multiplicative.toAdd
        (degree (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w) = 1 :=
      (orderOf_dvd_iff_zpow_eq_one).1 hd'
    change projection (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s) w = 1
    rw [projection_eq_geometric_zpow_degree K s]
    exact hpow

/-- Quotienting the infinite-degree model by one residue period gives the actual
residue Galois group. -/
noncomputable def finiteResidueQuotientEquiv :
    UnramifiedWeil K s ⧸
      periodSubgroup (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
        (ResidueDegree K s) ≃* ResidueGalois K s :=
  (quotientEquiv (MonoidHom.id (ResidueGalois K s)) (geometricFrobenius K s)
      (ResidueDegree K s) ⟨geometricFrobenius K s, rfl⟩).trans
    (geometricCycleEquiv K s)


end PaperXI.FiniteUnramifiedWeil
