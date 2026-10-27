import Mathlib.Algebra.Group.Prod
import Mathlib.Algebra.Group.Subgroup.Ker
import Mathlib.Algebra.GroupWithZero.Action.Basic
import Mathlib.Basic.Finite.Prod

namespace Komorebi.StrongArtin.AffineCocyclePackaging

noncomputable section

set_option linter.unusedSectionVars false

/-- The affine semidirect extension attached to a group acting additively on a group. -/
@[ext]
structure AffineExtension (Γ V : Type*) where
  translation : V
  residual : Γ
  deriving DecidableEq

section GroupStructure

variable {Γ V : Type*} [Group Γ] [AddCommGroup V] [DistribMulAction Γ V]

instance : Mul (AffineExtension Γ V) where
  mul x y := ⟨x.translation + x.residual • y.translation,
    x.residual * y.residual⟩

@[simp]
theorem mul_translation (x y : AffineExtension Γ V) :
    (x * y).translation = x.translation + x.residual • y.translation := rfl

@[simp]
theorem mul_residual (x y : AffineExtension Γ V) :
    (x * y).residual = x.residual * y.residual := rfl

instance : One (AffineExtension Γ V) where
  one := ⟨0, 1⟩

@[simp]
theorem one_translation : (1 : AffineExtension Γ V).translation = 0 := rfl

@[simp]
theorem one_residual : (1 : AffineExtension Γ V).residual = 1 := rfl

instance : Inv (AffineExtension Γ V) where
  inv x := ⟨-(x.residual⁻¹ • x.translation), x.residual⁻¹⟩

@[simp]
theorem inv_translation (x : AffineExtension Γ V) :
    x⁻¹.translation = -(x.residual⁻¹ • x.translation) := rfl

@[simp]
theorem inv_residual (x : AffineExtension Γ V) :
    x⁻¹.residual = x.residual⁻¹ := rfl

instance : Group (AffineExtension Γ V) where
  mul_assoc x y z := by
    apply AffineExtension.ext
    · simp only [mul_translation, mul_residual, smul_add, mul_smul]
      exact add_assoc _ _ _
    · simp only [mul_residual]
      exact mul_assoc _ _ _
  one_mul x := by
    ext <;> simp
  mul_one x := by
    ext <;> simp
  inv_mul_cancel x := by
    ext <;> simp

end GroupStructure

instance affineExtensionFinite {Γ V : Type*} [Finite V] [Finite Γ] :
    Finite (AffineExtension Γ V) :=
  Finite.of_injective
    (fun x : AffineExtension Γ V => (x.translation, x.residual))
    (by
      intro x y h
      exact AffineExtension.ext (congrArg Prod.fst h) (congrArg Prod.snd h))

section Cocycle

variable {G Γ V C : Type*} [Group G] [Group Γ]
  [AddCommGroup V] [DistribMulAction Γ V] [Group C]

/-- Normalized cocycle data for the action pulled back along a residual quotient. -/
structure CocycleData (q : G →* Γ) where
  value : G → V
  map_one : value 1 = 0
  map_mul : ∀ g h : G,
    value (g * h) = value g + q g • value h

/-- A normalized cocycle is exactly a homomorphism into its affine semidirect extension. -/
def CocycleData.affineLift (q : G →* Γ) (f : CocycleData (V := V) q) :
    G →* AffineExtension Γ V where
  toFun g := ⟨f.value g, q g⟩
  map_one' := by
    ext
    · exact f.map_one
    · simp
  map_mul' g h := by
    ext
    · exact f.map_mul g h
    · simp

@[simp]
theorem CocycleData.affineLift_translation
    (q : G →* Γ) (f : CocycleData (V := V) q) (g : G) :
    (f.affineLift q g).translation = f.value g := rfl

@[simp]
theorem CocycleData.affineLift_residual
    (q : G →* Γ) (f : CocycleData (V := V) q) (g : G) :
    (f.affineLift q g).residual = q g := rfl

/-- Package affine cocycle, residual, and cyclotomic/splitting labels in one
finite group-valued homomorphism. -/
def CocycleData.combinedFiniteLabel
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) :
    G →* (AffineExtension Γ V × C) :=
  (f.affineLift q).prod cyc

@[simp]
theorem CocycleData.combinedFiniteLabel_affine
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) (g : G) :
    (f.combinedFiniteLabel q cyc g).1 = f.affineLift q g := rfl

@[simp]
theorem CocycleData.combinedFiniteLabel_cyclotomic
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) (g : G) :
    (f.combinedFiniteLabel q cyc g).2 = cyc g := rfl

@[simp]
theorem CocycleData.combinedFiniteLabel_translation
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) (g : G) :
    (f.combinedFiniteLabel q cyc g).1.translation = f.value g := rfl

@[simp]
theorem CocycleData.combinedFiniteLabel_residual
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) (g : G) :
    (f.combinedFiniteLabel q cyc g).1.residual = q g := rfl


/-- The actual finite quotient cut out by the residual, cocycle, and
cyclotomic/splitting labels. Using the range avoids assuming the combined map is
onto the ambient product. -/
def CocycleData.combinedRange
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) :
    Subgroup (AffineExtension Γ V × C) :=
  (f.combinedFiniteLabel q cyc).range

/-- The canonical surjection onto the finite quotient actually cut out by the
combined labels. -/
def CocycleData.combinedQuotient
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) :
    G →* f.combinedRange q cyc :=
  (f.combinedFiniteLabel q cyc).rangeRestrict

/-- The combined quotient map is surjective by construction. -/
theorem CocycleData.combinedQuotient_surjective
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) :
    Function.Surjective (f.combinedQuotient q cyc) :=
  (f.combinedFiniteLabel q cyc).rangeRestrict_surjective

/-- With finite coefficients and labels, the actual quotient cut out by the
combined map is finite. -/
theorem finite_combined_range
    [Finite V] [Finite Γ] [Finite C]
    (q : G →* Γ) (f : CocycleData (V := V) q) (cyc : G →* C) :
    Finite (f.combinedRange q cyc) := by infer_instance

/-- With finite residual, cocycle-coordinate, and cyclotomic label groups, the
combined target is finite and therefore defines a Chebotarev-ready finite
quotient after taking the range. -/
theorem finite_combined_target
    [Finite V] [Finite Γ] [Finite C] :
    Finite (AffineExtension Γ V × C) := by infer_instance

end Cocycle

end
end Komorebi.StrongArtin.AffineCocyclePackaging

#print axioms Komorebi.StrongArtin.AffineCocyclePackaging.CocycleData.affineLift
#print axioms Komorebi.StrongArtin.AffineCocyclePackaging.CocycleData.combinedFiniteLabel
#print axioms Komorebi.StrongArtin.AffineCocyclePackaging.CocycleData.combinedQuotient_surjective
#print axioms Komorebi.StrongArtin.AffineCocyclePackaging.finite_combined_range
#print axioms Komorebi.StrongArtin.AffineCocyclePackaging.finite_combined_target
