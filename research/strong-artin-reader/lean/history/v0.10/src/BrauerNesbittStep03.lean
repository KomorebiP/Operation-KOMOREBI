module

public import BrauerNesbittStep02
public import Mathlib.LinearAlgebra.Projection

open scoped MonoidAlgebra

namespace Komorebi.StrongArtin.SemisimLift

universe uR uM uT
variable {R : Type uR} [Ring R]
variable {M : Type uM} [AddCommGroup M] [Module R M]
variable {T : Type uT} [AddCommGroup T] [Module R T]

/-- A complement to the `T`-isotypic component contains no further copy of
`T`: its own `T`-isotypic component is zero. -/
public theorem isotypicComponent_complement_eq_bot
    [IsSimpleModule R T]
    (D : Submodule R M)
    (hD : IsCompl (isotypicComponent R M T) D) :
    isotypicComponent R D T = ⊥ := by
  apply le_bot_iff.mp
  intro x hx
  have hxC : (x : M) ∈ isotypicComponent R M T := by
    have hle := LinearMap.le_comap_isotypicComponent
      (R := R) (M := D) (N := M) T D.subtype
    exact hle hx
  have hxD : (x : M) ∈ D := x.property
  have hxInf : (x : M) ∈ isotypicComponent R M T ⊓ D := ⟨hxC, hxD⟩
  have hx0 : (x : M) = 0 := by
    have hbot : isotypicComponent R M T ⊓ D = ⊥ := hD.disjoint.eq_bot
    rw [hbot] at hxInf
    simpa using hxInf
  exact Subtype.ext hx0

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.isotypicComponent_complement_eq_bot

namespace Komorebi.StrongArtin.SemisimLift

universe uK uG uV uW
variable {K : Type uK} [Field K]
variable {G : Type uG} [Group G]
variable {V : Type uV} [AddCommGroup V] [Module K V]
variable {W : Type uW} [AddCommGroup W] [Module K W]

/-- Restrict an ambient intertwiner along a group homomorphism. -/
public def restrictIntertwiningMap
    {H : Type*} [Monoid H]
    (φ : H →* G)
    {ρ : Representation K G V} {σ : Representation K G W}
    (f : Representation.IntertwiningMap ρ σ) :
    Representation.IntertwiningMap (ρ.comp φ) (σ.comp φ) :=
  f.toLinearMap.intertwiningMap_of_isIntertwiningMap (ρ.comp φ) (σ.comp φ)
    (by
      intro h v
      have hh := congrArg (fun L : V →ₗ[K] W => L v) (f.isIntertwining' (φ h))
      simpa using hh)

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.restrictIntertwiningMap

namespace Komorebi.StrongArtin.SemisimLift

universe uKsr uGsr uVsr
variable {K : Type uKsr} [Field K]
variable {G : Type uGsr} [Group G]
variable {V : Type uVsr} [AddCommGroup V] [Module K V]

/-- The group-algebra module attached to a subrepresentation is canonically the
same module as the corresponding group-algebra submodule. -/
@[expose] public noncomputable def subrepresentationAsModuleEquiv
    (ρ : Representation K G V) (A : Subrepresentation ρ) :
    A.toRepresentation.asModule ≃ₗ[K[G]] Subrepresentation.asSubmodule A := by
  let f : A.toRepresentation.asModule →ₗ[K[G]] Subrepresentation.asSubmodule A :=
    { toFun := fun x => ⟨(A.toRepresentation.asModuleEquiv x).1,
          (A.toRepresentation.asModuleEquiv x).2⟩
      map_add' := by
        intro x y
        apply Subtype.ext
        rfl
      map_smul' := by
        intro c x
        apply Subtype.ext
        rw [Representation.asModuleEquiv_map_smul]
        change ((A.toRepresentation.asAlgebraHom c)
              (A.toRepresentation.asModuleEquiv x)).1 =
          ρ.asAlgebraHom c (A.toRepresentation.asModuleEquiv x).1
        induction c using MonoidAlgebra.induction_linear with
        | zero => rfl
        | add a b ha hb =>
          simp only [map_add, LinearMap.add_apply]
          exact congrArg₂ (· + ·) ha hb
        | single g a =>
          simp only [Representation.asAlgebraHom_single]
          rfl }
  exact LinearEquiv.ofBijective f ⟨by
    intro x y h
    apply A.toRepresentation.asModuleEquiv.injective
    apply Subtype.ext
    exact congrArg Subtype.val h,
    by
      intro y
      let yy : A.toSubmodule := ⟨y.1, y.2⟩
      refine ⟨A.toRepresentation.asModuleEquiv.symm yy, ?_⟩
      apply Subtype.ext
      simp [f, yy]⟩
end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.subrepresentationAsModuleEquiv

namespace Komorebi.StrongArtin.SemisimLift

universe uK7 uG7 uV7 uW7 uT7
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK7} [Field K] [CharP K p]
variable {G : Type uG7} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uV7} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uW7} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
variable {T : Type uT7} [AddCommGroup T] [Module K[G] T]

set_option linter.style.haveILetI false in
/-- A restricted equivalence across a defining-characteristic prime-cyclic
quotient preserves every ambient isotypic block. -/
public theorem restriction_equiv_maps_isotypicComponent
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    [IsSimpleModule K[G] T] :
    ∀ x : isotypicComponent K[G] ρ.asModule T,
      eH x.1 ∈ isotypicComponent K[G] σ.asModule T := by
  letI : IsSemisimpleModule K[G] σ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule σ).mp hσ
  let CVm : Submodule K[G] ρ.asModule := isotypicComponent K[G] ρ.asModule T
  let CWm : Submodule K[G] σ.asModule := isotypicComponent K[G] σ.asModule T
  let CV : Subrepresentation ρ := Subrepresentation.ofSubmodule' CVm
  let CW : Subrepresentation σ := Subrepresentation.ofSubmodule' CWm
  obtain ⟨D, hD⟩ := exists_isCompl CWm
  let Drep : Subrepresentation σ := Subrepresentation.ofSubmodule' D
  let eCVm : CV.toRepresentation.asModule ≃ₗ[K[G]] CVm := by
    have hEq : Subrepresentation.asSubmodule CV = CVm := by rfl
    exact (subrepresentationAsModuleEquiv ρ CV).trans (LinearEquiv.ofEq _ _ hEq)
  let eDm : Drep.toRepresentation.asModule ≃ₗ[K[G]] D := by
    have hEq : Subrepresentation.asSubmodule Drep = D := by rfl
    exact (subrepresentationAsModuleEquiv σ Drep).trans (LinearEquiv.ofEq _ _ hEq)
  let projM : σ.asModule →ₗ[K[G]] D := D.projectionOnto CWm hD.symm
  let projMas : σ.asModule →ₗ[K[G]] Drep.toRepresentation.asModule :=
    eDm.symm.toLinearMap.comp projM
  let projG : Representation.IntertwiningMap σ Drep.toRepresentation :=
    intertwiningMapOfAsModuleLinearMap σ Drep.toRepresentation projMas
  let incG : Representation.IntertwiningMap CV.toRepresentation ρ :=
    subrepresentationInclusion ρ CV
  let projH := restrictIntertwiningMap S.subtype projG
  let incH := restrictIntertwiningMap S.subtype incG
  let fH : Representation.IntertwiningMap
      (CV.toRepresentation.comp S.subtype)
      (Drep.toRepresentation.comp S.subtype) :=
    projH.comp (eH.toIntertwiningMap.comp incH)
  have hDzero : isotypicComponent K[G] D T = ⊥ :=
    isotypicComponent_complement_eq_bot D hD
  have hCVm : IsIsotypicOfType K[G] CVm T := by
    exact IsIsotypicOfType.isotypicComponent K[G] ρ.asModule T
  have hfH0 : fH = 0 := by
    by_contra hfH
    obtain ⟨fG, hfG⟩ :=
      exists_nonzero_ambient_intertwiner_of_nonzero_restriction_intertwiner
        p S eQ CV.toRepresentation Drep.toRepresentation fH hfH
    apply hfG
    let E := Representation.IntertwiningMap.equivLinearMapAsModule
      (ρ := CV.toRepresentation) (σ := Drep.toRepresentation)
    let F0 := E fG
    let F : CVm →ₗ[K[G]] D :=
      eDm.toLinearMap.comp (F0.comp eCVm.symm.toLinearMap)
    have hsrc : isotypicComponent K[G] CVm T = ⊤ := by
      rw [isotypicComponent_eq_top_iff]
      exact hCVm
    have hle := LinearMap.le_comap_isotypicComponent
      (R := K[G]) (M := CVm) (N := D) T F
    rw [hsrc, hDzero] at hle
    have hF : F = 0 := by
      apply LinearMap.ext
      intro x
      have hx : x ∈ (⊤ : Submodule K[G] CVm) := by simp
      have hz := hle hx
      simpa using hz
    have hF0 : F0 = 0 := by
      apply LinearMap.ext
      intro x
      have hz : F (eCVm x) = 0 := by rw [hF]; rfl
      have hz' : eDm (F0 x) = 0 := by
        simpa [F] using hz
      apply eDm.injective
      simpa using hz'
    apply E.injective
    simpa [F0] using hF0
  intro x
  have hfx : fH ⟨x.1, x.2⟩ = 0 := by rw [hfH0]; rfl
  have hproj : projG (eH x.1) = 0 := by
    simpa [fH, projH, incH, incG, restrictIntertwiningMap,
      subrepresentationInclusion] using hfx
  have hprojMas : projMas (show σ.asModule from eH x.1) = 0 := by
    change projMas (show σ.asModule from eH x.1) = 0 at hproj
    exact hproj
  have hprojM : projM (show σ.asModule from eH x.1) = 0 := by
    change eDm.symm (projM (show σ.asModule from eH x.1)) = 0 at hprojMas
    exact (LinearEquiv.map_eq_zero_iff eDm.symm).mp hprojMas
  exact (D.projectionOnto_apply_eq_zero_iff hD.symm).mp hprojM

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.restriction_equiv_maps_isotypicComponent

namespace Komorebi.StrongArtin.SemisimLift

universe uK8 uG8 uV8 uW8 uT8
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK8} [Field K] [CharP K p]
variable {G : Type uG8} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uV8} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uW8} [AddCommGroup W] [Module K W] [FiniteDimensional K W]
variable {T : Type uT8} [AddCommGroup T] [Module K[G] T]

set_option linter.style.haveILetI false in
/-- A restricted equivalence across `G/H ≃ C_p` preserves the underlying
field dimension of every ambient isotypic block. -/
public theorem restriction_equiv_isotypic_finrank_eq
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hρ : Representation.IsSemisimpleRepresentation ρ)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    [IsSimpleModule K[G] T] :
    Module.finrank K (isotypicComponent K[G] ρ.asModule T) =
      Module.finrank K (isotypicComponent K[G] σ.asModule T) := by
  let CV : Submodule K[G] ρ.asModule := isotypicComponent K[G] ρ.asModule T
  let CW : Submodule K[G] σ.asModule := isotypicComponent K[G] σ.asModule T
  have hVW : ∀ x : CV, eH x.1 ∈ CW := by
    intro x
    exact restriction_equiv_maps_isotypicComponent p S eQ ρ σ hσ eH x
  have hWV : ∀ y : CW, eH.symm y.1 ∈ CV := by
    intro y
    exact restriction_equiv_maps_isotypicComponent p S eQ σ ρ hρ eH.symm y
  let f : CV →ₗ[K] CW :=
    { toFun := fun x => ⟨eH x.1, hVW x⟩
      map_add' := by
        intro x y
        apply Subtype.ext
        exact eH.toLinearEquiv.map_add x.1 y.1
      map_smul' := by
        intro a x
        apply Subtype.ext
        exact eH.toLinearEquiv.map_smul a x.1 }
  let g : CW →ₗ[K] CV :=
    { toFun := fun y => ⟨eH.symm y.1, hWV y⟩
      map_add' := by
        intro x y
        apply Subtype.ext
        exact eH.symm.toLinearEquiv.map_add x.1 y.1
      map_smul' := by
        intro a x
        apply Subtype.ext
        exact eH.symm.toLinearEquiv.map_smul a x.1 }
  have hf : Function.Injective f := by
    intro x y hxy
    apply Subtype.ext
    apply eH.injective
    exact congrArg Subtype.val hxy
  have hg : Function.Injective g := by
    intro x y hxy
    apply Subtype.ext
    apply eH.symm.injective
    exact congrArg Subtype.val hxy
  let iV : CV →ₗ[K] V :=
    { toFun := fun x => x.1
      map_add' := by intro x y; rfl
      map_smul' := by intro a x; rfl }
  let iW : CW →ₗ[K] W :=
    { toFun := fun y => y.1
      map_add' := by intro x y; rfl
      map_smul' := by intro a x; rfl }
  letI : FiniteDimensional K CV :=
    FiniteDimensional.of_injective iV (by
      intro x y hxy
      exact Subtype.ext hxy)
  letI : FiniteDimensional K CW :=
    FiniteDimensional.of_injective iW (by
      intro x y hxy
      exact Subtype.ext hxy)
  exact le_antisymm
    (LinearMap.finrank_le_finrank_of_injective hf)
    (LinearMap.finrank_le_finrank_of_injective hg)


set_option linter.style.haveILetI false in
/-- Corresponding ambient isotypic blocks are equivalent as `K[G]`-modules
whenever the full semisimple representations have equivalent restrictions
across a defining-characteristic prime-cyclic quotient. -/
public theorem restriction_equiv_isotypicComponent_equiv
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hρ : Representation.IsSemisimpleRepresentation ρ)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    [Module K T] [IsScalarTower K K[G] T] [FiniteDimensional K T]
    [IsSimpleModule K[G] T] :
    Nonempty (
      (isotypicComponent K[G] ρ.asModule T) ≃ₗ[K[G]]
        (isotypicComponent K[G] σ.asModule T)) := by
  let CV : Submodule K[G] ρ.asModule := isotypicComponent K[G] ρ.asModule T
  let CW : Submodule K[G] σ.asModule := isotypicComponent K[G] σ.asModule T
  let iV : CV →ₗ[K] V :=
    { toFun := fun x => x.1
      map_add' := by intro x y; rfl
      map_smul' := by intro a x; rfl }
  let iW : CW →ₗ[K] W :=
    { toFun := fun y => y.1
      map_add' := by intro x y; rfl
      map_smul' := by intro a x; rfl }
  letI : FiniteDimensional K CV :=
    FiniteDimensional.of_injective iV (by
      intro x y hxy
      exact Subtype.ext hxy)
  letI : FiniteDimensional K CW :=
    FiniteDimensional.of_injective iW (by
      intro x y hxy
      exact Subtype.ext hxy)
  exact isotypic_equiv_of_finrank_eq
    (IsIsotypicOfType.isotypicComponent K[G] ρ.asModule T)
    (IsIsotypicOfType.isotypicComponent K[G] σ.asModule T)
    (restriction_equiv_isotypic_finrank_eq p S eQ ρ σ hρ hσ eH)

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.restriction_equiv_isotypic_finrank_eq
#print axioms Komorebi.StrongArtin.SemisimLift.restriction_equiv_isotypicComponent_equiv
