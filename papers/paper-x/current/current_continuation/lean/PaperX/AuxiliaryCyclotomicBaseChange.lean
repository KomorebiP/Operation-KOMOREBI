import PaperX.AuxiliaryCyclotomicExistence

/-! Base change of a disjoint cyclic auxiliary extension. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AuxiliaryCyclotomicBaseChange
open IntermediateField

variable {k M : Type*} [Field k] [Field M] [Algebra k M]

/-- The compositum, viewed as an extension of the new base field. -/
def compositumOver (K A : IntermediateField k M) : IntermediateField K M :=
  IntermediateField.extendScalars (show K ≤ A ⊔ K from le_sup_right)

theorem compositumOver_restrictScalars (K A : IntermediateField k M) :
    (compositumOver K A).restrictScalars k = A ⊔ K := rfl

theorem compositumOver_isGalois (K A : IntermediateField k M)
    [FiniteDimensional k A] [IsGalois k A] :
    IsGalois K (compositumOver K A) := by
  let D : IntermediateField k M := A ⊔ K
  let : Algebra K D := (IntermediateField.inclusion (show K ≤ D from le_sup_right)).toAlgebra
  let A' : IntermediateField k D := A.restrict le_sup_left
  let K' : IntermediateField k D := K.restrict le_sup_right
  have hgal : IsGalois k A' := IsGalois.of_algEquiv (restrictAlgEquiv le_sup_left)
  have : FiniteDimensional k A' :=
    (restrictAlgEquiv (show A ≤ D from le_sup_left)).toLinearEquiv.finiteDimensional
  have hsup : A' ⊔ K' = ⊤ := by
    apply IntermediateField.lift_injective D
    simp only [lift_sup, A', K', lift_restrict, lift_top, D]
  have : IsGalois K' D := IsGalois.sup_right A' K' hsup
  apply IsGalois.of_equiv_equiv (F := K') (E := D)
    (f := (restrictAlgEquiv (show K ≤ D from le_sup_right)).symm.toRingEquiv)
    (g := RingEquiv.refl D)
  apply RingHom.ext
  intro x
  exact congrArg Subtype.val ((restrictAlgEquiv (show K ≤ D from le_sup_right)).apply_symm_apply x)

theorem compositumOver_isCyclic (K A : IntermediateField k M)
    [FiniteDimensional k A] [IsGalois k A] [IsCyclic Gal(A/k)] :
    IsCyclic Gal((compositumOver K A)/K) := by
  let D : IntermediateField k M := A ⊔ K
  let : Algebra K D := (IntermediateField.inclusion (show K ≤ D from le_sup_right)).toAlgebra
  let A' : IntermediateField k D := A.restrict le_sup_left
  let K' : IntermediateField k D := K.restrict le_sup_right
  let eK : K ≃ₐ[k] K' := restrictAlgEquiv le_sup_right
  have hgal : IsGalois k A' := IsGalois.of_algEquiv (restrictAlgEquiv le_sup_left)
  have : Normal k A' := hgal.to_normal
  have : IsCyclic Gal(A'/k) := isCyclic_of_surjective
    (restrictAlgEquiv (show A ≤ D from le_sup_left)).autCongr
    (restrictAlgEquiv (show A ≤ D from le_sup_left)).autCongr.surjective
  have hsup : A' ⊔ K' = ⊤ := by
    apply IntermediateField.lift_injective D
    simp only [lift_sup, A', K', lift_restrict, lift_top, D]
  have hcycD : IsCyclic Gal(D/K') := isCyclic_of_injective
    (restrictRestrictAlgEquivMapHom k A' K' D)
    (restrictRestrictAlgEquivMapHom_injective A' K' hsup)
  let : Algebra K' K := eK.symm.toAlgHom.toAlgebra
  let : Algebra K' (compositumOver K A) := inferInstanceAs (Algebra K' D)
  have : IsScalarTower K' K (compositumOver K A) :=
    IsScalarTower.of_algebraMap_eq (fun x =>
      (congrArg Subtype.val (eK.apply_symm_apply x)).symm)
  have : IsCyclic Gal((compositumOver K A)/K') := hcycD
  exact isCyclic_of_injective
    (MulSemiringAction.toAlgAut Gal((compositumOver K A)/K) K' (compositumOver K A))
    (fun f g h => AlgEquiv.ext (fun x => DFunLike.congr_fun h x))

theorem compositumOver_eq_adjoin (K A : IntermediateField k M) :
    compositumOver K A = IntermediateField.adjoin K (A : Set M) := by
  apply IntermediateField.restrictScalars_injective k
  rw [compositumOver_restrictScalars, restrictScalars_adjoin,
    adjoin_union, adjoin_self, adjoin_self, sup_comm]

/-- Disjoint base change preserves the degree of the original extension. -/
theorem compositumOver_finrank (K A : IntermediateField k M)
    [FiniteDimensional k A] (h : A.LinearDisjoint K) :
    Module.finrank K (compositumOver K A) = Module.finrank k A := by
  rw [compositumOver_eq_adjoin]
  exact congrArg Cardinal.toNat h.adjoin_rank_eq_rank_left_of_isAlgebraic_left

/-- Base change inside the second field preserves linear disjointness. -/
theorem compositumOver_linearDisjoint (K A L : IntermediateField k M)
    [FiniteDimensional k K] [FiniteDimensional k A] [FiniteDimensional k L]
    (hKL : K ≤ L) (h : A.LinearDisjoint L) :
    (compositumOver K A).LinearDisjoint (IntermediateField.extendScalars hKL) := by
  let B := compositumOver K A
  let L' := IntermediateField.extendScalars hKL
  have : FiniteDimensional k B := inferInstanceAs (FiniteDimensional k (A ⊔ K : IntermediateField k M))
  have : FiniteDimensional K B := FiniteDimensional.right k K B
  have : FiniteDimensional k L' := inferInstanceAs (FiniteDimensional k L)
  have : FiniteDimensional K L' := FiniteDimensional.right k K L'
  have : FiniteDimensional K (B ⊔ L' : IntermediateField K M) :=
    IntermediateField.finiteDimensional_sup B L'
  have : Module.Free K (B ⊔ L' : IntermediateField K M) := Module.Free.of_divisionRing K _
  have : FiniteDimensional k (B ⊔ L' : IntermediateField K M) :=
    Module.Finite.trans K (B ⊔ L' : IntermediateField K M)
  have hsup : (B ⊔ L' : IntermediateField K M).restrictScalars k = A ⊔ L := by
    rw [← restrictScalars_sup, compositumOver_restrictScalars, extendScalars_restrictScalars]
    exact sup_assoc A K L ▸ congrArg (fun E : IntermediateField k M => A ⊔ E)
      (sup_eq_right.mpr hKL)
  have htotal : Module.finrank k (B ⊔ L' : IntermediateField K M) =
      Module.finrank k A * Module.finrank k L := by
    change Module.finrank k ((B ⊔ L' : IntermediateField K M).restrictScalars k) = _
    rw [hsup]
    exact h.finrank_sup
  have hB : Module.finrank K B = Module.finrank k A :=
    compositumOver_finrank K A (h.of_le_right hKL)
  have hL := Module.finrank_mul_finrank k K L'
  have htot := Module.finrank_mul_finrank k K (B ⊔ L' : IntermediateField K M)
  have hK : 0 < Module.finrank k K := Module.finrank_pos
  apply IntermediateField.LinearDisjoint.of_finrank_sup
  change Module.finrank K (B ⊔ L' : IntermediateField K M) = _
  rw [hB]
  change Module.finrank k K * Module.finrank K L' = Module.finrank k L at hL
  nlinarith

end PaperX.AuxiliaryCyclotomicBaseChange
