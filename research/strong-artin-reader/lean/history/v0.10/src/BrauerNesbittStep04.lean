module

public import BrauerNesbittStep03
public import Mathlib.LinearAlgebra.DFinsupp

open scoped MonoidAlgebra

namespace Komorebi.StrongArtin.SemisimLift

universe uR4 uM4
variable {R : Type uR4} [Ring R]
variable {M : Type uM4} [AddCommGroup M] [Module R M]

/-- A fixed simple type representing a nonzero isotypic component. -/
@[expose] public noncomputable def simpleTypeOfComponent
    (c : isotypicComponents R M) : Submodule R M :=
  Classical.choose c.2

public theorem simpleTypeOfComponent_simple (c : isotypicComponents R M) :
    IsSimpleModule R (simpleTypeOfComponent c) :=
  (Classical.choose_spec c.2).1

public theorem component_eq_isotypic_simpleType (c : isotypicComponents R M) :
    c.1 = isotypicComponent R M (simpleTypeOfComponent c) :=
  (Classical.choose_spec c.2).2


universe uK9 uG9 uV9 uW9
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK9} [Field K] [CharP K p]
variable {G : Type uG9} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uV9} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uW9} [AddCommGroup W] [Module K W] [FiniteDimensional K W]

/-- The target isotypic block having the same simple `K[G]`-type as a
chosen source isotypic component. -/
@[expose] public noncomputable def transportedIsotypicComponent
    (ρ : Representation K G V) (σ : Representation K G W)
    (c : isotypicComponents K[G] ρ.asModule) : Submodule K[G] σ.asModule :=
  isotypicComponent K[G] σ.asModule (simpleTypeOfComponent c)

set_option linter.style.haveILetI false in
/-- Across a defining-characteristic `C_p` quotient, the transported block of
every nonzero source isotypic component is a nonzero target isotypic component. -/
public theorem transportedIsotypicComponent_mem
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    (c : isotypicComponents K[G] ρ.asModule) :
    transportedIsotypicComponent ρ σ c ∈ isotypicComponents K[G] σ.asModule := by
  let T : Type uV9 := simpleTypeOfComponent c
  letI : AddCommGroup T := inferInstance
  letI : Module K[G] T := inferInstance
  letI : IsSimpleModule K[G] T := simpleTypeOfComponent_simple c
  let C : Submodule K[G] ρ.asModule := isotypicComponent K[G] ρ.asModule T
  have hc : c.1 = C := component_eq_isotypic_simpleType c
  obtain ⟨x, hx⟩ := exists_ne (0 : c.1)
  have hxv : x.1 ≠ (0 : V) := by
    intro h
    apply hx
    apply Subtype.ext
    exact h
  let xC : C := ⟨x.1, by
    rw [← hc]
    exact x.2⟩
  have hy_mem : eH x.1 ∈ transportedIsotypicComponent ρ σ c := by
    change eH xC.1 ∈ isotypicComponent K[G] σ.asModule T
    exact restriction_equiv_maps_isotypicComponent p S eQ ρ σ hσ eH xC
  have hy_ne : eH x.1 ≠ (0 : W) := by
    intro h
    apply hxv
    apply eH.injective
    simpa using h
  have hne : transportedIsotypicComponent ρ σ c ≠ ⊥ := by
    intro hbot
    have hz : eH x.1 = (0 : W) := by
      have : eH x.1 ∈ (⊥ : Submodule K[G] σ.asModule) := by
        rw [← hbot]
        exact hy_mem
      change eH x.1 = (0 : W) at this
      exact this
    exact hy_ne hz
  letI : IsSemisimpleModule K[G] σ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule σ).mp hσ
  exact mem_isotypicComponents_iff.mpr ⟨
    IsIsotypic.isotypicComponent K[G] σ.asModule T,
    Submodule.IsFullyInvariant.isotypicComponent K[G] σ.asModule T,
    hne⟩


/-- The induced map from nonzero source isotypic components to nonzero target
isotypic components. -/
@[expose] public noncomputable def transportedComponentMap
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype)) :
    isotypicComponents K[G] ρ.asModule → isotypicComponents K[G] σ.asModule :=
  fun c => ⟨transportedIsotypicComponent ρ σ c,
    transportedIsotypicComponent_mem p S eQ ρ σ hσ eH c⟩

set_option linter.style.haveILetI false in
/-- Distinct source isotypic components transport to distinct target components. -/
public theorem transportedComponentMap_injective
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype)) :
    Function.Injective (transportedComponentMap p S eQ ρ σ hσ eH) := by
  intro c d hcd
  have hval : transportedIsotypicComponent ρ σ c =
      transportedIsotypicComponent ρ σ d := congrArg Subtype.val hcd
  let Tc : Type uV9 := simpleTypeOfComponent c
  let Td : Type uV9 := simpleTypeOfComponent d
  letI : AddCommGroup Tc := inferInstance
  letI : Module K[G] Tc := inferInstance
  letI : IsSimpleModule K[G] Tc := simpleTypeOfComponent_simple c
  letI : AddCommGroup Td := inferInstance
  letI : Module K[G] Td := inferInstance
  letI : IsSimpleModule K[G] Td := simpleTypeOfComponent_simple d
  have hqc : transportedIsotypicComponent ρ σ c ∈
      isotypicComponents K[G] σ.asModule :=
    transportedIsotypicComponent_mem p S eQ ρ σ hσ eH c
  have hqne : transportedIsotypicComponent ρ σ c ≠ ⊥ :=
    (bot_lt_isotypicComponents hqc).ne'
  letI : IsSemisimpleModule K[G] (transportedIsotypicComponent ρ σ c) := by
    change IsSemisimpleModule K[G]
      (isotypicComponent K[G] σ.asModule (simpleTypeOfComponent c))
    infer_instance
  obtain ⟨U, hU, hUsimple⟩ :=
    (IsSemisimpleModule.eq_bot_or_exists_simple_le
      (transportedIsotypicComponent ρ σ c)).resolve_left hqne
  letI : IsSimpleModule K[G] U := hUsimple
  have hUc : Nonempty (U ≃ₗ[K[G]] Tc) := by
    change Nonempty (U ≃ₗ[K[G]] simpleTypeOfComponent c)
    exact (isIsotypicOfType_submodule_iff.mp
      (IsIsotypicOfType.isotypicComponent K[G] σ.asModule
        (simpleTypeOfComponent c))) U hU
  have hUd_le : U ≤ transportedIsotypicComponent ρ σ d := by
    rw [← hval]
    exact hU
  have hUd : Nonempty (U ≃ₗ[K[G]] Td) := by
    change Nonempty (U ≃ₗ[K[G]] simpleTypeOfComponent d)
    exact (isIsotypicOfType_submodule_iff.mp
      (IsIsotypicOfType.isotypicComponent K[G] σ.asModule
        (simpleTypeOfComponent d))) U hUd_le
  obtain ⟨ec⟩ := hUc
  obtain ⟨ed⟩ := hUd
  apply Subtype.ext
  rw [component_eq_isotypic_simpleType c, component_eq_isotypic_simpleType d]
  exact (ec.symm.trans ed).isotypicComponent_eq


set_option linter.style.haveILetI false in
/-- With finite ambient group, the transported map of nonzero isotypic
components is a bijection.  The proof uses the injective construction in both
directions and finite cardinality. -/
public theorem transportedComponentMap_bijective
    [Fintype G]
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hρ : Representation.IsSemisimpleRepresentation ρ)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype)) :
    Function.Bijective (transportedComponentMap p S eQ ρ σ hσ eH) := by
  letI : IsSemisimpleModule K[G] ρ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule ρ).mp hρ
  letI : IsSemisimpleModule K[G] σ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule σ).mp hσ
  letI : Module.Finite K[G] ρ.asModule :=
    Module.Finite.of_restrictScalars_finite K K[G] ρ.asModule
  letI : Module.Finite K[G] σ.asModule :=
    Module.Finite.of_restrictScalars_finite K K[G] σ.asModule
  letI : Finite (isotypicComponents K[G] ρ.asModule) := inferInstance
  letI : Finite (isotypicComponents K[G] σ.asModule) := inferInstance
  have hf : Function.Injective (transportedComponentMap p S eQ ρ σ hσ eH) :=
    transportedComponentMap_injective p S eQ ρ σ hσ eH
  have hg : Function.Injective (transportedComponentMap p S eQ σ ρ hρ eH.symm) :=
    transportedComponentMap_injective p S eQ σ ρ hρ eH.symm
  have hcard : Nat.card (isotypicComponents K[G] σ.asModule) ≤
      Nat.card (isotypicComponents K[G] ρ.asModule) :=
    Nat.card_le_card_of_injective
      (transportedComponentMap p S eQ σ ρ hρ eH.symm) hg
  exact hf.bijective_of_nat_card_le hcard


set_option linter.style.haveILetI false in
/-- **Prime-cyclic semisimple restriction rigidity in defining characteristic.**
For a finite group with normal subgroup of quotient `C_p`, two finite-dimensional
semisimple representations in characteristic `p` are equivalent once their
restrictions to the normal subgroup are equivalent. -/
public theorem semisimple_equiv_of_restriction_equiv_cp
    [Fintype G]
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (hρ : Representation.IsSemisimpleRepresentation ρ)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype)) :
    Nonempty (ρ.Equiv σ) := by
  classical
  letI : IsSemisimpleModule K[G] ρ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule ρ).mp hρ
  letI : IsSemisimpleModule K[G] σ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule σ).mp hσ
  letI : Module.Finite K[G] ρ.asModule :=
    Module.Finite.of_restrictScalars_finite K K[G] ρ.asModule
  letI : Module.Finite K[G] σ.asModule :=
    Module.Finite.of_restrictScalars_finite K K[G] σ.asModule
  let I := isotypicComponents K[G] ρ.asModule
  let J := isotypicComponents K[G] σ.asModule
  let f : I → J := transportedComponentMap p S eQ ρ σ hσ eH
  have hf : Function.Bijective f :=
    transportedComponentMap_bijective p S eQ ρ σ hρ hσ eH
  let φ : I ≃ J := Equiv.ofBijective f hf
  let blockEquiv : ∀ c : I, c.1 ≃ₗ[K[G]] (φ c).1 := fun c => by
    let T : Type uV9 := simpleTypeOfComponent c
    letI : AddCommGroup T := inferInstance
    letI : Module K[G] T := inferInstance
    letI : Module K T := inferInstance
    letI : IsScalarTower K K[G] T := inferInstance
    letI : IsSimpleModule K[G] T := simpleTypeOfComponent_simple c
    let iT : T →ₗ[K] V :=
      { toFun := fun x => x.1
        map_add' := by intro x y; rfl
        map_smul' := by intro a x; rfl }
    letI : FiniteDimensional K T :=
      FiniteDimensional.of_injective iT (by
        intro x y hxy
        exact Subtype.ext hxy)
    have eblock : Nonempty (
        (isotypicComponent K[G] ρ.asModule T) ≃ₗ[K[G]]
          (isotypicComponent K[G] σ.asModule T)) :=
      restriction_equiv_isotypicComponent_equiv p S eQ ρ σ hρ hσ eH
    let eSrc : c.1 ≃ₗ[K[G]] isotypicComponent K[G] ρ.asModule T :=
      LinearEquiv.ofEq _ _ (component_eq_isotypic_simpleType c)
    have hTarget : (φ c).1 = isotypicComponent K[G] σ.asModule T := by
      rfl
    exact eSrc.trans eblock.some |>.trans (LinearEquiv.ofEq _ _ hTarget.symm)
  have hindV : iSupIndep ((↑) : I → Submodule K[G] ρ.asModule) :=
    (sSupIndep_iff _).mp (sSupIndep_isotypicComponents K[G] ρ.asModule)
  have htopV : ⨆ c : I, c.1 = ⊤ :=
    (sSup_eq_iSup' _).symm.trans (sSup_isotypicComponents K[G] ρ.asModule)
  have hindW : iSupIndep ((↑) : J → Submodule K[G] σ.asModule) :=
    (sSupIndep_iff _).mp (sSupIndep_isotypicComponents K[G] σ.asModule)
  have htopW : ⨆ c : J, c.1 = ⊤ :=
    (sSup_eq_iSup' _).symm.trans (sSup_isotypicComponents K[G] σ.asModule)
  let eV : (Π₀ c : I, c.1) ≃ₗ[K[G]] ρ.asModule := hindV.linearEquiv htopV
  let eW : (Π₀ c : J, c.1) ≃ₗ[K[G]] σ.asModule := hindW.linearEquiv htopW
  let eBlocks : (Π₀ c : I, c.1) ≃ₗ[K[G]] (Π₀ c : I, (φ c).1) :=
    DFinsupp.mapRange.linearEquiv blockEquiv
  let eReindex : (Π₀ c : I, (φ c).1) ≃ₗ[K[G]] (Π₀ d : J, d.1) :=
    (DirectSum.lequivCongrLeft K[G] (M := fun d : J => d.1) φ.symm).symm
  let eGlobal : ρ.asModule ≃ₗ[K[G]] σ.asModule :=
    eV.symm.trans (eBlocks.trans (eReindex.trans eW))
  exact ⟨repEquivOfAsModuleLinearEquiv ρ σ eGlobal⟩


end Komorebi.StrongArtin.SemisimLift

namespace Komorebi.StrongArtin.QuotientRestriction

universe uGdirect uVdirect uWdirect

/-- **Unconditional internal prime-cyclic residual collapse.**  Over the prime
field `F_p`, semisimple finite-dimensional representations of a finite group
whose restrictions agree on a normal subgroup with quotient `C_p` are already
equivalent.  This bypasses the v0.9 general Brauer--Nesbitt interface. -/
public theorem semisimple_residual_collapse_cp
    (p : ℕ) [Fact p.Prime]
    {G : Type uGdirect} [Group G] [Fintype G]
    (S : Subgroup G) [S.Normal]
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    {V : Type uVdirect} [AddCommGroup V] [Module (ZMod p) V]
    {W : Type uWdirect} [AddCommGroup W] [Module (ZMod p) W]
    [FiniteDimensional (ZMod p) V] [FiniteDimensional (ZMod p) W]
    (ρ : Representation (ZMod p) G V)
    (σ : Representation (ZMod p) G W)
    (hρ : Representation.IsSemisimpleRepresentation ρ)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation (ZMod p) S V from ρ.comp S.subtype)
      (show Representation (ZMod p) S W from σ.comp S.subtype)) :
    Nonempty (ρ.Equiv σ) :=
  Komorebi.StrongArtin.SemisimLift.semisimple_equiv_of_restriction_equiv_cp
    p S eQ ρ σ hρ hσ eH

end Komorebi.StrongArtin.QuotientRestriction

#print axioms Komorebi.StrongArtin.QuotientRestriction.semisimple_residual_collapse_cp

#print axioms Komorebi.StrongArtin.SemisimLift.simpleTypeOfComponent_simple
#print axioms Komorebi.StrongArtin.SemisimLift.component_eq_isotypic_simpleType
#print axioms Komorebi.StrongArtin.SemisimLift.transportedIsotypicComponent_mem
#print axioms Komorebi.StrongArtin.SemisimLift.transportedComponentMap_injective
#print axioms Komorebi.StrongArtin.SemisimLift.transportedComponentMap_bijective
#print axioms Komorebi.StrongArtin.SemisimLift.semisimple_equiv_of_restriction_equiv_cp
