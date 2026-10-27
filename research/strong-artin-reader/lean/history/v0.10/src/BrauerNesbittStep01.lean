module

public import StrongArtinFiniteCore
public import Mathlib.RingTheory.SimpleModule.Isotypic

open scoped MonoidAlgebra

namespace Komorebi.StrongArtin.SemisimLift

universe uK uG uV uW
variable {K : Type uK} [Field K]
variable {G : Type uG} [Group G]
variable {V : Type uV} [AddCommGroup V] [Module K V]
variable {W : Type uW} [AddCommGroup W] [Module K W]

/-- A linear equivalence over the group algebra gives an equivalence of the
corresponding group representations. -/
public noncomputable def repEquivOfAsModuleLinearEquiv
    (ρ : Representation K G V) (σ : Representation K G W)
    (e : ρ.asModule ≃ₗ[K[G]] σ.asModule) : ρ.Equiv σ := by
  let eK : V ≃ₗ[K] W := e.restrictScalars K
  refine Representation.Equiv.mk eK ?_
  intro g
  ext v
  change eK (ρ g v) = σ g (eK v)
  dsimp [eK]
  have hv : ρ.asModuleEquiv (show ρ.asModule from v) = v := rfl
  have heV : σ.asModuleEquiv (show σ.asModule from e v) = e v := rfl
  have hrho : (MonoidAlgebra.of K G g) • (show ρ.asModule from v) = ρ g v := by
    calc
      _ = (1 : K) • ρ g (ρ.asModuleEquiv (show ρ.asModule from v)) := by
        exact Representation.single_smul (ρ := ρ) (1 : K) g (show ρ.asModule from v)
      _ = ρ g v := by rw [hv]; simp
  have hsigma : (MonoidAlgebra.of K G g) • (show σ.asModule from e v) = σ g (e v) := by
    calc
      _ = (1 : K) • σ g (σ.asModuleEquiv (show σ.asModule from e v)) := by
        exact Representation.single_smul (ρ := σ) (1 : K) g (show σ.asModule from e v)
      _ = σ g (e v) := by rw [heV]; simp
  change e (ρ g v) = σ g (e v)
  rw [← hrho, ← hsigma]
  exact e.map_smul (MonoidAlgebra.of K G g) v


/-- A linear map over the group algebra gives an intertwining map of the
corresponding group representations. -/
@[expose] public noncomputable def intertwiningMapOfAsModuleLinearMap
    (ρ : Representation K G V) (σ : Representation K G W)
    (f : ρ.asModule →ₗ[K[G]] σ.asModule) : ρ.IntertwiningMap σ := by
  let fK : V →ₗ[K] W := f.restrictScalars K
  refine fK.intertwiningMap_of_isIntertwiningMap ρ σ ?_
  intro g v
  have hv : ρ.asModuleEquiv (show ρ.asModule from v) = v := rfl
  have hfV : σ.asModuleEquiv (show σ.asModule from f v) = f v := rfl
  have hrho : (MonoidAlgebra.of K G g) • (show ρ.asModule from v) = ρ g v := by
    calc
      _ = (1 : K) • ρ g (ρ.asModuleEquiv (show ρ.asModule from v)) := by
        exact Representation.single_smul (ρ := ρ) (1 : K) g (show ρ.asModule from v)
      _ = ρ g v := by rw [hv]; simp
  have hsigma : (MonoidAlgebra.of K G g) • (show σ.asModule from f v) = σ g (f v) := by
    calc
      _ = (1 : K) • σ g (σ.asModuleEquiv (show σ.asModule from f v)) := by
        exact Representation.single_smul (ρ := σ) (1 : K) g (show σ.asModule from f v)
      _ = σ g (f v) := by rw [hfV]; simp
  change f (ρ g v) = σ g (f v)
  rw [← hrho, ← hsigma]
  exact f.map_smul (MonoidAlgebra.of K G g) v


end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.repEquivOfAsModuleLinearEquiv

namespace Komorebi.StrongArtin.SemisimLift

universe uH uK2 uV2
variable {K : Type uK2} [Field K]
variable {H : Type uH} [Group H]
variable {V : Type uV2} [AddCommGroup V] [Module K V]

set_option linter.style.haveILetI false in
/-- In a semisimple representation, every subrepresentation admits an
H-equivariant retraction. -/
public theorem semisimple_subrepresentation_retraction
    (ρ : Representation K H V)
    (A : Subrepresentation ρ)
    (hρ : Representation.IsSemisimpleRepresentation ρ) :
    ∃ r : ρ.IntertwiningMap A.toRepresentation,
      ∀ a : A.toSubmodule, r a.1 = a := by
  letI : IsSemisimpleModule K[H] ρ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule ρ).mp hρ
  let AM : Submodule K[H] ρ.asModule := Subrepresentation.asSubmodule A
  obtain ⟨rM, hrM⟩ := IsSemisimpleModule.extension_property
    (Submodule.subtype AM) (Submodule.injective_subtype AM) (LinearMap.id (R := K[H]) (M := AM))
  let rK : V →ₗ[K] A.toSubmodule := rM.restrictScalars K
  let rH : ρ.IntertwiningMap A.toRepresentation := by
    refine rK.intertwiningMap_of_isIntertwiningMap ρ A.toRepresentation ?_
    intro h v
    apply Subtype.ext
    change (rM (ρ h v)).1 = ρ h (rM v).1
    have hm := rM.map_smul (MonoidAlgebra.of K H h) (show ρ.asModule from v)
    have hv : ρ.asModuleEquiv (show ρ.asModule from v) = v := rfl
    have hl : (MonoidAlgebra.of K H h) • (show ρ.asModule from v) = ρ h v := by
      calc
        _ = (1 : K) • ρ h (ρ.asModuleEquiv (show ρ.asModule from v)) := by
          exact Representation.single_smul (ρ := ρ) (1 : K) h (show ρ.asModule from v)
        _ = ρ h v := by rw [hv]; simp
    have hx : ρ.asModuleEquiv (show ρ.asModule from (rM v).1) = (rM v).1 := rfl
    have hr : (((MonoidAlgebra.of K H h) • rM v : AM) : ρ.asModule) = ρ h (rM v).1 := by
      change (MonoidAlgebra.of K H h) • (show ρ.asModule from (rM v).1) = ρ h (rM v).1
      calc
        _ = (1 : K) • ρ h (ρ.asModuleEquiv (show ρ.asModule from (rM v).1)) := by
          exact Representation.single_smul (ρ := ρ) (1 : K) h
            (show ρ.asModule from (rM v).1)
        _ = ρ h (rM v).1 := by rw [hx]; simp
    have hmval := congrArg Subtype.val hm
    rw [hl] at hmval
    exact hmval.trans hr
  refine ⟨rH, ?_⟩
  intro a
  have ha := congrArg (fun f => f a) hrM
  change rM a.1 = a at ha
  change rM a.1 = a
  exact ha

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.intertwiningMapOfAsModuleLinearMap
#print axioms Komorebi.StrongArtin.SemisimLift.semisimple_subrepresentation_retraction

namespace Komorebi.StrongArtin.SemisimLift

universe uK3 uH3 uV3
variable {K : Type uK3} [Field K]
variable {H : Type uH3} [Group H]
variable {V : Type uV3} [AddCommGroup V] [Module K V]

/-- The inclusion of a subrepresentation is an intertwining map. -/
@[expose] public def subrepresentationInclusion
    (ρ : Representation K H V) (A : Subrepresentation ρ) :
    A.toRepresentation.IntertwiningMap ρ :=
  (A.toSubmodule.subtype).intertwiningMap_of_isIntertwiningMap A.toRepresentation ρ
    (by intro h a; rfl)


end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.subrepresentationInclusion

namespace Komorebi.StrongArtin.SemisimLift

universe uK4 uG4 uV4 uW4
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK4} [Field K] [CharP K p]
variable {G : Type uG4} [Group G] [Fintype G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uV4} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uW4} [AddCommGroup W] [Module K W] [FiniteDimensional K W]

set_option linter.style.haveILetI false in
/-- If two irreducible ambient representations have a common irreducible
constituent after restriction to a normal subgroup with prime-cyclic quotient
in characteristic p, then the ambient representations are equivalent. -/
public theorem irreducible_equiv_of_common_restricted_constituent
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (A : Subrepresentation (show Representation K S V from ρ.comp S.subtype))
    (B : Subrepresentation (show Representation K S W from σ.comp S.subtype))
    [Representation.IsIrreducible A.toRepresentation]
    (eAB : A.toRepresentation.Equiv B.toRepresentation) :
    Nonempty (ρ.Equiv σ) := by
  let ρH : Representation K S V := ρ.comp S.subtype
  let σH : Representation K S W := σ.comp S.subtype
  have hρH : Representation.IsSemisimpleRepresentation ρH :=
    Komorebi.StrongArtin.QuotientRestriction.irreducible_restrict_normal_semisimple S ρ
  obtain ⟨rA, hrA⟩ := semisimple_subrepresentation_retraction ρH A hρH
  let iB : B.toRepresentation.IntertwiningMap σH := subrepresentationInclusion σH B
  let fH : ρH.IntertwiningMap σH :=
    iB.comp (eAB.toIntertwiningMap.comp rA)
  have hfH : fH ≠ 0 := by
    haveI : IsSimpleModule K[S] A.toRepresentation.asModule :=
      (Representation.irreducible_iff_isSimpleModule_asModule A.toRepresentation).mp inferInstance
    letI : Nontrivial A.toRepresentation.asModule :=
      IsSimpleModule.nontrivial K[S] A.toRepresentation.asModule
    letI : Nontrivial A.toSubmodule := A.toRepresentation.asModuleEquiv.toEquiv.symm.nontrivial
    obtain ⟨a, ha⟩ : ∃ a : A.toSubmodule, a ≠ 0 := exists_ne 0
    intro hzero
    have hz := congrArg (fun f : ρH.IntertwiningMap σH => f a.1) hzero
    have hret : rA a.1 = a := hrA a
    have hfa : fH a.1 = (eAB a : B.toSubmodule).1 := by
      change (eAB (rA a.1) : B.toSubmodule).1 = (eAB a : B.toSubmodule).1
      rw [hret]
    rw [hfa] at hz
    simp at hz
    exact ha hz
  exact Komorebi.StrongArtin.QuotientRestriction.irreducible_equiv_of_nonzero_restriction_intertwiner
    p S eQ ρ σ fH hfH

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.irreducible_equiv_of_common_restricted_constituent

namespace Komorebi.StrongArtin.SemisimLift

universe uK5 uG5 uV5 uW5
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK5} [Field K] [CharP K p]
variable {G : Type uG5} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uV5} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uW5} [AddCommGroup W] [Module K W] [FiniteDimensional K W]

set_option linter.style.haveILetI false in
/-- Across a prime-cyclic quotient in its defining characteristic, every
nonzero intertwiner after restriction produces a nonzero ambient intertwiner.
No irreducibility or semisimplicity hypothesis is needed for this lifting step. -/
public theorem exists_nonzero_ambient_intertwiner_of_nonzero_restriction_intertwiner
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    (fH : Representation.IntertwiningMap
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    (hfH : fH ≠ 0) :
    ∃ fG : ρ.IntertwiningMap σ, fG ≠ 0 := by
  let L : Representation K G (V →ₗ[K] W) := Representation.linHom ρ σ
  let U : Submodule K (V →ₗ[K] W) :=
    Representation.invariants (show Representation K S (V →ₗ[K] W) from L.comp S.subtype)
  let qRep : Representation K (G ⧸ S) U := Representation.quotientToInvariants L S
  let θ : Representation K (Komorebi.StrongArtin.CyclicSimple.Cp p) U :=
    qRep.comp eQ.symm.toMonoidHom
  let u0 : U := by
    refine ⟨fH.toLinearMap, ?_⟩
    have hint : Representation.IsIntertwiningMap
        (show Representation K S V from ρ.comp S.subtype)
        (show Representation K S W from σ.comp S.subtype)
        fH.toLinearMap :=
      ⟨fun h v => Representation.IntertwiningMap.isIntertwining
        (ρ := (show Representation K S V from ρ.comp S.subtype))
        (σ := (show Representation K S W from σ.comp S.subtype))
        fH h v⟩
    exact (Representation.mem_linHom_invariants_iff_isIntertwining
      (ρ := (show Representation K S V from ρ.comp S.subtype))
      (σ := (show Representation K S W from σ.comp S.subtype))
      fH.toLinearMap).2 hint
  have hu0_ne : u0 ≠ 0 := by
    intro hz
    apply hfH
    apply Representation.IntertwiningMap.ext
    have hv := congrArg Subtype.val hz
    simpa [u0] using hv
  letI : Nontrivial U := ⟨⟨u0, 0, hu0_ne⟩⟩
  obtain ⟨u, hu0, hufix⟩ :=
    Komorebi.StrongArtin.CyclicSimple.exists_nonzero_fixed_vector_cp p θ
  have huG : ∀ g : G, L g u.1 = u.1 := by
    intro g
    have hqfix : qRep ((QuotientGroup.mk' S) g) u = u := by
      have hcp := hufix (eQ ((QuotientGroup.mk' S) g))
      simpa [θ] using hcp
    have hqfix' : ((qRep.comp (QuotientGroup.mk' S)) g) u = u := by
      simpa using hqfix
    have hlift := Representation.IntertwiningMap.isIntertwining
      (show Representation K G U from qRep.comp (QuotientGroup.mk' S)) L
      (Representation.quotientToInvariants_lift L S) g u
    rw [hqfix'] at hlift
    exact hlift.symm
  have huInv : u.1 ∈ Representation.invariants L := huG
  let xG : Representation.invariants L := ⟨u.1, huInv⟩
  let EG := Representation.invariantsEquivIntertwiningMap ρ σ
  let fG : ρ.IntertwiningMap σ := EG xG
  have hfG_ne : fG ≠ 0 := by
    intro hz
    have hx0 : xG = 0 := by
      apply EG.injective
      simpa [fG, EG] using hz
    apply hu0
    apply Subtype.ext
    have hxv := congrArg Subtype.val hx0
    simpa [xG] using hxv
  exact ⟨fG, hfG_ne⟩

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.exists_nonzero_ambient_intertwiner_of_nonzero_restriction_intertwiner

namespace Komorebi.StrongArtin.SemisimLift

universe uK6 uG6 uV6 uW6
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK6} [Field K] [CharP K p]
variable {G : Type uG6} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uV6} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uW6} [AddCommGroup W] [Module K W] [FiniteDimensional K W]

set_option linter.style.haveILetI false in
/-- If an irreducible ambient type occurs nontrivially after restriction in an
arbitrary target representation, then it occurs by an injective ambient
intertwiner. This is the occurrence-reflection form needed for semisimple
multiplicity bookkeeping. -/
public theorem exists_injective_ambient_intertwiner_of_irreducible_source
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    [Representation.IsIrreducible ρ]
    (fH : Representation.IntertwiningMap
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    (hfH : fH ≠ 0) :
    ∃ fG : ρ.IntertwiningMap σ, fG ≠ 0 ∧ Function.Injective fG := by
  obtain ⟨fG, hfG⟩ :=
    exists_nonzero_ambient_intertwiner_of_nonzero_restriction_intertwiner
      p S eQ ρ σ fH hfH
  have hsimple : IsSimpleModule K[G] ρ.asModule :=
    (Representation.irreducible_iff_isSimpleModule_asModule ρ).mp inferInstance
  letI : IsSimpleModule K[G] ρ.asModule := hsimple
  let E := Representation.IntertwiningMap.equivLinearMapAsModule (ρ := ρ) (σ := σ)
  have hfGM : E fG ≠ 0 := by
    intro hz
    apply hfG
    apply E.injective
    simpa using hz
  have hinjM : Function.Injective (E fG) :=
    LinearMap.injective_of_ne_zero hfGM
  exact ⟨fG, hfG, hinjM⟩

end Komorebi.StrongArtin.SemisimLift

#print axioms Komorebi.StrongArtin.SemisimLift.exists_injective_ambient_intertwiner_of_irreducible_source
