import KomorebiSpace.SectionExtensionFibers

set_option autoImplicit false

/-!
# An exact sequence for partial ambient observations

The connecting map is an actual additive homomorphism into the existing
relative obstruction quotient. Exactness is proved as equality of subgroups.
There is no asserted surjectivity onto all arrow-indexed residual classes.
-/
universe u v w
namespace KomorebiSpace
open CategoryTheory
namespace AdditiveViewSystem
variable {V : Type u} [Category.{v} V]
variable {A : V → Type w} [∀ a, AddCommGroup (A a)]
variable (F : AdditiveViewSystem V A)

/-- The group of all coherent ambient families. -/
def sectionGroup : AddSubgroup (∀ a, A a) := F.differential.ker

/-- Coherent partial families, with their inherited additive structure. -/
def partialGroup (U : Set V) : AddSubgroup (∀ a : U, A a.val) where
  carrier := {x | ∀ (a b : U) (f : a.val ⟶ b.val), F.pull f (x b) = x a}
  zero_mem' := by intro a b f; exact map_zero _
  add_mem' := by
    intro x y hx hy a b f
    change F.pull f (x b + y b) = x a + y a
    rw [map_add, hx, hy]
  neg_mem' := by
    intro x hx a b f
    change F.pull f (-x b) = -x a
    rw [map_neg, hx]

def sectionGroupEquiv : F.sectionGroup ≃ F.views.Ambient where
  toFun x := ⟨x.val,(F.differential_zero_iff _).mp x.property⟩
  invFun x := ⟨x.val,(F.differential_zero_iff _).mpr x.property⟩
  left_inv _ := rfl
  right_inv _ := rfl

def partialGroupEquiv (U : Set V) : F.partialGroup U ≃ F.views.Partial U where
  toFun x := ⟨x.val,x.property⟩
  invFun x := ⟨x.val,x.property⟩
  left_inv _ := rfl
  right_inv _ := rfl

/-- Extension by zero is additive but generally not coherent. -/
noncomputable def rawLift (_F : AdditiveViewSystem V A) (U : Set V) : (∀ a : U, A a.val) →+ (∀ a, A a) := by
  classical
  exact {
    toFun := fun x a => if h : a ∈ U then x ⟨a,h⟩ else 0
    map_zero' := by funext a; split_ifs <;> rfl
    map_add' := by
      intro x y
      funext a
      by_cases h : a ∈ U <;> simp [h]
  }

@[simp] theorem rawLift_observed (U : Set V) (x : ∀ a : U, A a.val) :
    F.observation U (F.rawLift U x) = x := by
  classical
  funext a
  simp [observation,rawLift,a.property]

/-- The independently defined obstruction map on prescribed raw observations. -/
noncomputable def obstructionOfData (U : Set V) :
    (∀ a : U, A a.val) →+ (F.problem U).Obstruction :=
  (QuotientAddGroup.mk' (F.problem U).boundaries).comp
    (F.differential.comp (F.rawLift U))

@[simp] theorem obstructionOfData_apply (U : Set V) (x : ∀ a : U, A a.val) :
    F.obstructionOfData U x = (F.problem U).obstruction (F.rawLift U x) := rfl

/-- Actual restriction on the additive groups of coherent sections. -/
def restrictionHom (U : Set V) : F.sectionGroup →+ F.partialGroup U where
  toFun x := ⟨F.observation U x.val, by
    intro a b f
    exact (F.differential_zero_iff _).mp x.property a.val b.val f⟩
  map_zero' := rfl
  map_add' := by intros; rfl

noncomputable def connectingHom (U : Set V) :
    F.partialGroup U →+ (F.problem U).Obstruction :=
  (F.obstructionOfData U).comp (F.partialGroup U).subtype

@[simp] theorem connecting_eq_extensionClass (U : Set V) (x : F.partialGroup U) :
    F.connectingHom U x = F.extensionClass U (F.partialGroupEquiv U x) := by
  apply F.extensionClass_independent
  intro a
  exact congrFun (F.rawLift_observed U x.val) a

/-- Exactness at partial sections: the obstruction kernel is the restriction image. -/
theorem connecting_zero_iff_lift (U : Set V) (x : F.partialGroup U) :
    F.connectingHom U x = 0 ↔ ∃ y : F.sectionGroup, F.restrictionHom U y = x := by
  rw [F.connecting_eq_extensionClass, F.extensionClass_zero_iff]
  constructor
  · rintro ⟨⟨y,hy⟩⟩
    refine ⟨(F.sectionGroupEquiv).symm y, ?_⟩
    apply Subtype.ext
    exact congrArg Subtype.val hy
  · rintro ⟨y,hy⟩
    refine ⟨⟨F.sectionGroupEquiv y, ?_⟩⟩
    apply ViewSystem.Partial.ext
    intro a
    exact congrFun (congrArg Subtype.val hy) a

theorem connecting_kernel_eq_range (U : Set V) :
    (F.connectingHom U).ker = (F.restrictionHom U).range := by
  ext x
  exact F.connecting_zero_iff_lift U x

@[simp] theorem connecting_restriction_zero (U : Set V) (x : F.sectionGroup) :
    F.connectingHom U (F.restrictionHom U x) = 0 :=
  (F.connecting_zero_iff_lift U _).mpr ⟨x,rfl⟩

/-- The earlier extension class is the value of the same additive connecting map. -/
theorem extensionClass_as_hom (U : Set V) (s : F.views.Partial U) :
    F.extensionClass U s = F.connectingHom U ((F.partialGroupEquiv U).symm s) :=
  (F.connecting_eq_extensionClass U _).symm

/-- Forgetting coherence proofs does not change the homogeneous kernel. -/
theorem restriction_kernel_characterization (U : Set V) (x : F.sectionGroup) :
    F.restrictionHom U x = 0 ↔ x.val ∈ F.ambiguity U := by
  constructor
  · intro h
    exact ⟨x.property, congrArg Subtype.val h⟩
  · intro h
    exact Subtype.ext h.2

/-- Universal extension is vanishing of the connecting homomorphism, not automatic. -/
theorem restriction_surjective_iff_connecting_zero (U : Set V) :
    Function.Surjective (F.restrictionHom U) ↔ F.connectingHom U = 0 := by
  constructor
  · intro hs
    ext x
    obtain ⟨y,rfl⟩ := hs x
    exact F.connecting_restriction_zero U y
  · intro h x
    apply (F.connecting_zero_iff_lift U x).mp
    rw [h]
    rfl

/-- The obstruction carried by partial sections, without irrelevant residual classes. -/
noncomputable def partialObstructionEquiv (U : Set V) :
    F.partialGroup U ⧸ (F.restrictionHom U).range ≃+
      (F.connectingHom U).range :=
  (QuotientAddGroup.quotientAddEquivOfEq (F.connecting_kernel_eq_range U).symm).trans
    (QuotientAddGroup.quotientKerEquivRange (F.connectingHom U))

@[simp] theorem partialObstructionEquiv_class (U : Set V) (s : F.partialGroup U) :
    (F.partialObstructionEquiv U
      (s : F.partialGroup U ⧸ (F.restrictionHom U).range)).val =
        F.connectingHom U s := rfl

end AdditiveViewSystem
end KomorebiSpace
