import PaperXI.RamificationPolyphase
import PaperXI.FiniteUnramifiedWeil
import Mathlib.GroupTheory.QuotientGroup.Basic

/-! # Ramified pullbacks and their inertia-free degree quotient

The residue--Frobenius pullback retains a decomposition-group coordinate and an
integer degree.  Its degree kernel is inertia.  This file proves the precise
first-isomorphism statement and compares the quotient with the integer-degree
unramified model only under an explicit degree-one Frobenius-lift hypothesis.

It also proves the exact representation-theoretic information loss: a
representation pulled back only through integer degree kills every lower
ramification subgroup, so every ramification depth projector is the identity
and every positive detail projector is zero.
-/

set_option autoImplicit false
noncomputable section
open scoped Classical BigOperators

namespace PaperXI.RamifiedUnramifiedQuotient

open PaperXI.ResidueWeil
open PaperXI.FiniteUnramifiedWeil
open PaperXI.ValuationConductor
open PaperXI.RamificationPolyphase
open PaperXI.FiniteAverage
open PaperXI.ValuationRamification
open ValuativeRel

section FirstIsomorphism

variable {D C : Type*} [Group D] [Group C]
variable (r : D →* C) (F : C)

/-- The inertia subgroup of a residue--Frobenius pullback is its degree kernel. -/
abbrev Inertia : Subgroup (Pullback r F) := (degree r F).ker

/-- Noether's first isomorphism theorem for the integer-degree map, without a
surjectivity assumption. -/
noncomputable def quotientEquivDegreeRange :
    Pullback r F ⧸ Inertia r F ≃* (degree r F).range :=
  QuotientGroup.quotientKerEquivRange (degree r F)

/-- One degree-one lift generates every integral degree. -/
theorem degree_surjective_of_degree_one
    (w₁ : Pullback r F)
    (hw₁ : degree r F w₁ = Multiplicative.ofAdd (1 : ℤ)) :
    Function.Surjective (degree r F) := by
  intro n
  refine ⟨w₁ ^ Multiplicative.toAdd n, ?_⟩
  rw [map_zpow, hw₁]
  apply Multiplicative.toAdd.injective
  simp

/-- A lift of the chosen residue Frobenius is exactly the hypothesis needed for
surjectivity of integer degree. -/
theorem degree_surjective_of_frobenius_mem_range
    (hF : F ∈ r.range) : Function.Surjective (degree r F) := by
  obtain ⟨w₁, hw₁⟩ := (exists_degree_one_iff r F).2 hF
  exact degree_surjective_of_degree_one r F w₁ hw₁

/-- With an actual degree-one Frobenius lift, quotienting by inertia gives the
full integer-degree group. -/
noncomputable def quotientEquivIntegerDegree
    (hF : F ∈ r.range) : Pullback r F ⧸ Inertia r F ≃* Multiplicative ℤ :=
  QuotientGroup.quotientKerEquivOfSurjective (degree r F)
    (degree_surjective_of_frobenius_mem_range r F hF)

@[simp]
theorem quotientEquivIntegerDegree_mk
    (hF : F ∈ r.range) (w : Pullback r F) :
    quotientEquivIntegerDegree r F hF (QuotientGroup.mk w) = degree r F w := by
  change QuotientGroup.kerLift (degree r F) (QuotientGroup.mk w) = degree r F w
  exact QuotientGroup.kerLift_mk (degree r F) w

/-- Two degree-one Frobenius lifts differ by inertia. -/
theorem frobenius_lift_ratio_mem_inertia
    {w₁ w₂ : Pullback r F}
    (h₁ : degree r F w₁ = Multiplicative.ofAdd (1 : ℤ))
    (h₂ : degree r F w₂ = Multiplicative.ofAdd (1 : ℤ)) :
    w₁ * w₂⁻¹ ∈ Inertia r F := by
  change degree r F (w₁ * w₂⁻¹) = 1
  rw [map_mul, map_inv, h₁, h₂]
  simp

end FirstIsomorphism

section CurrentDegreeModel

variable {D C : Type*} [Group D] [Group C]
variable (r : D →* C) (F : C)

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

/-- Forget the ramified decomposition-group coordinate and retain only integer
degree in the current unramified Weil model. -/
noncomputable def degreeModelMap :
    Pullback r F →* UnramifiedWeil K s :=
  (degreeEquiv K s).symm.toMonoidHom.comp (degree r F)

@[simp]
theorem degreeModelMap_degree (w : Pullback r F) :
    degreeEquiv K s (degreeModelMap r F K s w) = degree r F w := by
  simp [degreeModelMap]

/-- The degree-only map kills exactly inertia. -/
theorem degreeModelMap_ker :
    (degreeModelMap r F K s).ker = Inertia r F := by
  ext w
  simp [degreeModelMap]

/-- Under a degree-one lift, the degree-only comparison is onto the current
integer-degree unramified model. -/
theorem degreeModelMap_surjective
    (hF : F ∈ r.range) : Function.Surjective (degreeModelMap r F K s) := by
  intro u
  obtain ⟨w, hw⟩ := degree_surjective_of_frobenius_mem_range r F hF
      ((degreeEquiv K s) u)
  refine ⟨w, ?_⟩
  apply (degreeEquiv K s).injective
  simpa [degreeModelMap] using hw

/-- The quotient by inertia is the current unramified degree model, under the
explicit degree-one lift hypothesis. -/
noncomputable def quotientEquivUnramified
    (hF : F ∈ r.range) :
    Pullback r F ⧸ Inertia r F ≃* UnramifiedWeil K s :=
  (quotientEquivIntegerDegree r F hF).trans (degreeEquiv K s).symm

@[simp]
theorem quotientEquivUnramified_mk_degree
    (hF : F ∈ r.range) (w : Pullback r F) :
    degreeEquiv K s
        (quotientEquivUnramified r F K s hF (QuotientGroup.mk w)) =
      degree r F w := by
  simp [quotientEquivUnramified]

/-- Every ramified Frobenius lift of degree one maps to the distinguished
geometric Frobenius lift of the unramified model. -/
theorem degreeModelMap_eq_geometricLift_of_degree_one
    {w : Pullback r F}
    (hw : degree r F w = Multiplicative.ofAdd (1 : ℤ)) :
    degreeModelMap r F K s w = geometricLift K s := by
  apply (degreeEquiv K s).injective
  rw [degreeModelMap_degree, hw, degreeEquiv_apply, degree_geometricLift]

section Representations

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- Pull a representation of the inertia-free model back through integer
degree.  This deliberately forgets every ramification coordinate. -/
def pullbackDegreeRepresentation
    (σ : Representation ℂ (UnramifiedWeil K s) V) :
    Representation ℂ (Pullback r F) V :=
  σ.comp (degreeModelMap r F K s)

/-- A degree-only pullback is trivial on inertia. -/
theorem inertia_le_pullbackDegreeRepresentation_ker
    (σ : Representation ℂ (UnramifiedWeil K s) V) :
    Inertia r F ≤ (pullbackDegreeRepresentation r F K s σ).ker := by
  intro w hw
  change σ (degreeModelMap r F K s w) = 1
  have hd : degree r F w = 1 := hw
  apply LinearMap.ext
  intro v
  simp [degreeModelMap, hd]

/-- Any representation trivial on inertia descends first to the quotient. -/
noncomputable def quotientRepresentation
    (ρ : Representation ℂ (Pullback r F) V)
    (hI : Inertia r F ≤ ρ.ker) :
    Representation ℂ (Pullback r F ⧸ Inertia r F) V :=
  QuotientGroup.lift (Inertia r F) ρ hI

/-- Under a degree-one lift, an inertia-trivial representation descends to the
current unramified integer-degree model. -/
noncomputable def descendRepresentation
    (hF : F ∈ r.range)
    (ρ : Representation ℂ (Pullback r F) V)
    (hI : Inertia r F ≤ ρ.ker) :
    Representation ℂ (UnramifiedWeil K s) V :=
  (quotientRepresentation r F ρ hI).comp
    (quotientEquivUnramified r F K s hF).symm.toMonoidHom

/-- Pulling the descended representation back recovers the original one. -/
theorem descendRepresentation_comp_degreeModelMap
    (hF : F ∈ r.range)
    (ρ : Representation ℂ (Pullback r F) V)
    (hI : Inertia r F ≤ ρ.ker) :
    (descendRepresentation r F K s hF ρ hI).comp
        (degreeModelMap r F K s) = ρ := by
  apply MonoidHom.ext
  intro w
  apply LinearMap.ext
  intro v
  let e := quotientEquivUnramified r F K s hF
  have heU : e (QuotientGroup.mk w) = degreeModelMap r F K s w := by
    apply (degreeEquiv K s).injective
    rw [quotientEquivUnramified_mk_degree, degreeModelMap_degree]
  have heQ : e.symm (degreeModelMap r F K s w) = QuotientGroup.mk w := by
    rw [← heU]
    exact e.symm_apply_apply _
  change (quotientRepresentation r F ρ hI
      (e.symm (degreeModelMap r F K s w))) v = ρ w v
  rw [heQ]
  rfl

/-- Descent to the current degree model is unique. -/
theorem descendRepresentation_unique
    (hF : F ∈ r.range)
    (ρ : Representation ℂ (Pullback r F) V)
    (hI : Inertia r F ≤ ρ.ker)
    (σ : Representation ℂ (UnramifiedWeil K s) V)
    (hσ : σ.comp (degreeModelMap r F K s) = ρ) :
    σ = descendRepresentation r F K s hF ρ hI := by
  apply MonoidHom.ext
  intro u
  apply LinearMap.ext
  intro v
  obtain ⟨w, rfl⟩ := degreeModelMap_surjective r F K s hF u
  have hleft := congrArg (fun τ : Representation ℂ (Pullback r F) V => τ w v) hσ
  have hright := congrArg
    (fun τ : Representation ℂ (Pullback r F) V => τ w v)
    (descendRepresentation_comp_degreeModelMap r F K s hF ρ hI)
  exact hleft.trans hright.symm

end Representations
end CurrentDegreeModel

section PolyphaseCollapse

variable (R D : Type*) [CommRing R] [IsLocalRing R]
  [Group D] [Fintype D] [MulSemiringAction D R]
variable (F : RingAut (IsLocalRing.ResidueField R))

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (σ : Representation ℂ (UnramifiedWeil K s) V)

abbrev degreeOnlyRepresentation :
    Representation ℂ (Pullback (residue R D) F) V :=
  pullbackDegreeRepresentation (residue R D) F K s σ

omit [Fintype D] in
/-- Every lower ramification element acts trivially after passing through the
degree-only quotient. -/
theorem degreeOnlyRepresentation_lift_eq_one
    (i : ℕ) (g : lower R D i) :
    degreeOnlyRepresentation R D F K s σ (lift R D F i g) = 1 := by
  have hmap : degreeModelMap (residue R D) F K s (lift R D F i g) = 1 := by
    apply (degreeEquiv K s).injective
    rw [degreeModelMap_degree, lift_degree]
    simp
  change σ (degreeModelMap (residue R D) F K s (lift R D F i g)) = 1
  rw [hmap]
  exact map_one σ

omit [Fintype D] in
/-- Every lower fixed space becomes the whole representation space after the
inertia quotient. -/
theorem degreeOnly_fixed_eq_top (i : ℕ) :
    fixed R D F (degreeOnlyRepresentation R D F K s σ) i = ⊤ := by
  apply top_unique
  intro v _ g
  change degreeOnlyRepresentation R D F K s σ (lift R D F i g) v = v
  rw [degreeOnlyRepresentation_lift_eq_one]
  rfl

/-- Every depth averaging projector becomes the identity. -/
theorem degreeOnly_depthProjector_eq_id (i : ℕ) :
    depthProjector (R := R) (D := D) (F := F)
      (ρ := degreeOnlyRepresentation R D F K s σ) i = LinearMap.id := by
  ext v
  exact fixes _ (by
    intro g
    change degreeOnlyRepresentation R D F K s σ (lift R D F i g) v = v
    rw [degreeOnlyRepresentation_lift_eq_one]
    rfl)

/-- Every positive ramification detail channel is erased by the inertia-free
quotient. -/
theorem degreeOnly_detailProjector_eq_zero (i : ℕ) :
    detailProjector (R := R) (D := D) (F := F)
      (ρ := degreeOnlyRepresentation R D F K s σ) i = 0 := by
  unfold detailProjector
  rw [degreeOnly_depthProjector_eq_id, degreeOnly_depthProjector_eq_id]
  exact sub_self _

/-- Every lower-numbering conductor summand vanishes after quotienting by
inertia. -/
theorem degreeOnly_summand_eq_zero (i : ℕ) :
    summand R D F (degreeOnlyRepresentation R D F K s σ) i = 0 := by
  unfold summand codimension
  rw [degreeOnly_fixed_eq_top]
  simp

/-- The Swan conductor vanishes on the degree-only quotient. -/
theorem degreeOnly_swan_eq_zero :
    swan R D F (degreeOnlyRepresentation R D F K s σ) = 0 := by
  unfold swan
  simp only [degreeOnly_summand_eq_zero, tsum_zero]

/-- The Artin conductor vanishes on the degree-only quotient. -/
theorem degreeOnly_artin_eq_zero :
    artin R D F (degreeOnlyRepresentation R D F K s σ) = 0 := by
  unfold artin codimension
  rw [degreeOnly_fixed_eq_top, degreeOnly_swan_eq_zero]
  simp

end PolyphaseCollapse

end PaperXI.RamifiedUnramifiedQuotient
