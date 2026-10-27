import PaperXI.CyclicInducedCharacter
import PaperXI.TameTensorInduction

/-! Source-facing tame tensor decomposition of genuine induced representations.
The Frobenius convention uses representatives `φ^(-i)` and hence the shifted
character `h ↦ η(φ^(-i) h φ^i)`. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameTensorSource
open TameDegree
open scoped TensorProduct DirectSum Classical

variable {G : Type*} [Group G] (ν : G →* Multiplicative ℤ) (φ : G)
variable (n m : ℕ)
variable (ξ : degreeSubgroup ν n →* ℂˣ) (η : degreeSubgroup ν m →* ℂˣ)

/-- The literal product of the first restricted character and the second shifted restriction. -/
def interactionCharacter (i : Fin (Nat.gcd n m)) :
    degreeSubgroup ν (Nat.lcm n m) →* ℂˣ :=
  (ξ.comp (Subgroup.inclusion (degreeSubgroup_le ν n (Nat.lcm n m)
    (Nat.dvd_lcm_left n m)))) *
    (η.comp (conjugationInto ν m (Nat.lcm n m) (Nat.dvd_lcm_right n m)
      (φ ^ (-(i.val : ℤ)))))

@[simp] theorem interactionCharacter_apply (i : Fin (Nat.gcd n m))
    (h : degreeSubgroup ν (Nat.lcm n m)) :
    interactionCharacter ν φ n m ξ η i h =
      ξ ⟨h, degreeSubgroup_le ν n (Nat.lcm n m) (Nat.dvd_lcm_left n m) h.property⟩ *
      η (conjugationInto ν m (Nat.lcm n m) (Nat.dvd_lcm_right n m)
        (φ ^ (-(i.val : ℤ))) h) := rfl

/-- The character shift is an explicit conjugation, with no assumption of a scalar formula. -/
theorem interactionCharacter_literal (i : Fin (Nat.gcd n m))
    (h : degreeSubgroup ν (Nat.lcm n m)) :
    interactionCharacter ν φ n m ξ η i h =
      ξ ⟨h, degreeSubgroup_le ν n (Nat.lcm n m) (Nat.dvd_lcm_left n m) h.property⟩ *
      η ⟨φ ^ (-(i.val : ℤ)) * (h : G) * φ ^ (i.val : ℤ), by
        have hp := (conjugationInto ν m (Nat.lcm n m) (Nat.dvd_lcm_right n m)
          (φ ^ (-(i.val : ℤ))) h).property
        simpa only [conjugationInto_apply, zpow_neg, inv_inv] using hp⟩ := by
  rw [interactionCharacter_apply]
  congr 1
  apply congrArg η
  apply Subtype.ext
  simp [conjugationInto_apply, zpow_neg]

variable [NeZero n] [NeZero m]
variable (hφ : ν φ = Multiplicative.ofAdd (1 : ℤ))

omit [NeZero n] in
theorem representative_val (i : Fin (Nat.gcd n m)) : (i.val : ZMod m).val = i.val := by
  rw [ZMod.val_natCast, Nat.mod_eq_of_lt]
  exact i.isLt.trans_le (Nat.gcd_le_right n (Nat.pos_of_ne_zero (NeZero.ne m)))

/-- The actual tensor-line coefficient equals the stated product of restricted characters. -/
theorem interactionCharacter_weight (i : Fin (Nat.gcd n m))
    (h : degreeSubgroup ν (Nat.lcm n m)) :
    (interactionCharacter ν φ n m ξ η i h : ℂ) =
      (CyclicInduced.degreeWeight ν φ hφ n ξ h 0 : ℂ) *
        (CyclicInduced.degreeWeight ν φ hφ m η h (i.val : ZMod m) : ℂ) := by
  rw [CyclicInduced.degreeWeight_restrict_zero ν φ hφ n ξ (Nat.dvd_lcm_left n m),
    CyclicInduced.degreeWeight_restrict ν φ hφ m η (Nat.dvd_lcm_right n m),
    representative_val n m i, interactionCharacter_apply, Units.val_mul]

/-- The gcd/lcm formula for the tensor product of two genuine induced representations. -/
def decomposition : Representation.Equiv
    ((CyclicInduced.degreeInduced ν n ξ).tprod (CyclicInduced.degreeInduced ν m η))
    (Representation.directSum (fun i : Fin (Nat.gcd n m) =>
      CyclicInduced.degreeInduced ν (Nat.lcm n m) (interactionCharacter ν φ n m ξ η i))) :=
  TameTensorInduction.decompositionWithCharacters ν n m
    (CyclicInduced.degreeInduced ν n ξ) (CyclicInduced.degreeInduced ν m η)
    (CyclicInduced.degreeBasis ν φ hφ n ξ) (CyclicInduced.degreeBasis ν φ hφ m η)
    (CyclicInduced.degreeWeight ν φ hφ n ξ) (CyclicInduced.degreeWeight ν φ hφ m η)
    (CyclicInduced.degreeBasis_action ν φ hφ n ξ)
    (CyclicInduced.degreeBasis_action ν φ hφ m η) φ hφ
    (interactionCharacter ν φ n m ξ η)
    (fun i h => by simpa only [Units.val_mul] using
      interactionCharacter_weight ν φ n m ξ η hφ i h)

/-- The displayed decomposition is an actual group intertwiner. -/
theorem decomposition_intertwines (g : G)
    (v : CyclicInduced.DegreeIndSpace ν n ξ ⊗[ℂ] CyclicInduced.DegreeIndSpace ν m η) :
    decomposition ν φ n m ξ η hφ
      (((CyclicInduced.degreeInduced ν n ξ).tprod (CyclicInduced.degreeInduced ν m η)) g v) =
      (Representation.directSum (fun i : Fin (Nat.gcd n m) =>
        CyclicInduced.degreeInduced ν (Nat.lcm n m) (interactionCharacter ν φ n m ξ η i))) g
          (decomposition ν φ n m ξ η hφ v) :=
  Representation.IntertwiningMap.isIntertwining _ _
    (decomposition ν φ n m ξ η hφ).toIntertwiningMap g v

include hφ in
/-- Each summand in the displayed genuine induction formula has dimension lcm. -/
theorem interaction_dimension (i : Fin (Nat.gcd n m)) :
    Module.finrank ℂ (CyclicInduced.DegreeIndSpace ν (Nat.lcm n m)
      (interactionCharacter ν φ n m ξ η i)) = Nat.lcm n m := by
  simpa only [ZMod.card] using Module.finrank_eq_card_basis
    (CyclicInduced.degreeBasis ν φ hφ (Nat.lcm n m) (interactionCharacter ν φ n m ξ η i))

omit [NeZero n] [NeZero m] in
/-- The direct sum is indexed by exactly gcd-many interaction packets before merging. -/
theorem interaction_count : Fintype.card (Fin (Nat.gcd n m)) = Nat.gcd n m :=
  Fintype.card_fin _

include hφ in
/-- The dimensions of the actual induced summands, not hypothetical blocks, sum to `n*m`. -/
theorem interaction_dimension_sum :
    (∑ i : Fin (Nat.gcd n m), Module.finrank ℂ
      (CyclicInduced.DegreeIndSpace ν (Nat.lcm n m) (interactionCharacter ν φ n m ξ η i))) =
      n*m := by
  simp only [interaction_dimension ν φ n m ξ η hφ, Finset.sum_const,
    Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  exact Nat.gcd_mul_lcm n m

include hφ in
/-- The genuine tensor source has the same dimension as the constructed direct sum. -/
theorem tensor_dimension : Module.finrank ℂ
    (CyclicInduced.DegreeIndSpace ν n ξ ⊗[ℂ] CyclicInduced.DegreeIndSpace ν m η) = n*m := by
  simpa only [Fintype.card_prod, ZMod.card] using Module.finrank_eq_card_basis
    ((CyclicInduced.degreeBasis ν φ hφ n ξ).tensorProduct
      (CyclicInduced.degreeBasis ν φ hφ m η))

end PaperXI.TameTensorSource
