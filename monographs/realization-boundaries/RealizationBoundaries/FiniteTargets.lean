import RealizationBoundaries.ProductTopology

/-!
# All finite targets extend uniquely to the ambient product

The extension is built from the actual integer quotient. Continuity is a theorem,
not a condition imposed on the original abstract homomorphism.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

variable (W : Submodule ℚ TailSpace)
variable (F : Type*) [AddGroup F] [Finite F]

theorem finite_target_kills_ncard (f : preimage W →+ F) :
    multiples W (Nat.card F) ≤ f.ker := by
  let : Fintype F := Fintype.ofFinite F
  simpa only [Nat.card_eq_fintype_card] using finite_target_kills_multiples W F f

/-- The finite factor obtained from the exact quotient equivalence. -/
def finiteTargetFactor (f : preimage W →+ F) : DivisorCoordinates (Nat.card F) →+ F :=
  (QuotientAddGroup.lift (multiples W (Nat.card F)) f (finite_target_kills_ncard W F f)).comp
    (integerQuotientEquiv W (Nat.card_pos)).symm.toAddMonoidHom

@[simp] theorem finiteTargetFactor_coordinate (f : preimage W →+ F) (x : preimage W) :
    finiteTargetFactor W F f (coordinateMap W (Nat.card F) x) = f x := by
  change (QuotientAddGroup.lift (multiples W (Nat.card F)) f (finite_target_kills_ncard W F f))
    ((integerQuotientEquiv W Nat.card_pos).symm (coordinateMap W (Nat.card F) x)) = f x
  have hi : (integerQuotientEquiv W Nat.card_pos).symm (coordinateMap W (Nat.card F) x) =
      QuotientAddGroup.mk x := by
    apply (integerQuotientEquiv W Nat.card_pos).injective
    rw [AddEquiv.apply_symm_apply]
    exact (integerQuotientEquiv_mk W Nat.card_pos x).symm
  rw [hi]
  rfl

/-- A finite-target map on H_W extends to the same fixed infinite product P. -/
def finiteTargetExtension (f : preimage W →+ F) : Ambient →+ F :=
  (finiteTargetFactor W F f).comp (ambientCoordinates (Nat.card F))

@[simp] theorem finiteTargetExtension_subtype (f : preimage W →+ F) (x : preimage W) :
    finiteTargetExtension W F f x.val = f x :=
  finiteTargetFactor_coordinate W F f x

/-- The extension factors through finitely many discrete coordinates. -/
theorem finiteTargetExtension_continuous [TopologicalSpace F] (f : preimage W →+ F) :
    Continuous (finiteTargetExtension W F f) := by
  let := divisorCoordinates_discrete (m := Nat.card F) Nat.card_pos
  exact (continuous_of_discreteTopology : Continuous (finiteTargetFactor W F f)).comp
    (ambientCoordinates_continuous (Nat.card F))

/-- Continuity of every abstract finite-target homomorphism in the induced topology. -/
theorem finiteTarget_continuous [TopologicalSpace F] (f : preimage W →+ F) : Continuous f := by
  have h := (finiteTargetExtension_continuous W F f).comp
    (continuous_subtype_val : Continuous (fun x : preimage W => x.val))
  simpa only [Function.comp_def, finiteTargetExtension_subtype] using h

/-- Uniqueness is with respect to continuous ambient maps, as required by completion. -/
theorem finiteTargetExtension_unique [TopologicalSpace F] [T2Space F]
    (f : preimage W →+ F) (g : Ambient →+ F) (hg : Continuous g)
    (heq : ∀ x : preimage W, g x.val = f x) : g = finiteTargetExtension W F f := by
  apply DFunLike.ext'
  apply (preimage_denseRange W).equalizer hg (finiteTargetExtension_continuous W F f)
  funext x
  exact (heq x).trans (finiteTargetExtension_subtype W F f x).symm

/-- Extension commutes with every homomorphism of finite target groups. -/
theorem finiteTargetExtension_natural (E : Type*) [AddGroup E] [Finite E]
    (f : preimage W →+ F) (g : F →+ E) :
    finiteTargetExtension W E (g.comp f) = g.comp (finiteTargetExtension W F f) := by
  let : TopologicalSpace F := ⊥
  let : DiscreteTopology F := ⟨rfl⟩
  let : TopologicalSpace E := ⊥
  let : DiscreteTopology E := ⟨rfl⟩
  symm
  apply finiteTargetExtension_unique W E
  · exact (continuous_of_discreteTopology : Continuous g).comp
      (finiteTargetExtension_continuous W F f)
  · intro x
    simp

/-- Precise finite-target universal property, without identifying unequal Hom types. -/
def finiteTargetHomEquiv [TopologicalSpace F] [DiscreteTopology F] :
    (Ambient →ₜ+ F) ≃ (preimage W →+ F) where
  toFun g := g.toAddMonoidHom.comp (preimage W).subtype
  invFun f := { toAddMonoidHom := finiteTargetExtension W F f,
                continuous_toFun := finiteTargetExtension_continuous W F f }
  left_inv g := by
    apply ContinuousAddMonoidHom.ext
    intro x
    exact DFunLike.congr_fun (finiteTargetExtension_unique W F
      (g.toAddMonoidHom.comp (preimage W).subtype) g.toAddMonoidHom g.continuous_toFun
      (fun _ => rfl)).symm x
  right_inv f := by
    ext x
    exact finiteTargetExtension_subtype W F f x

end RealizationBoundaries
