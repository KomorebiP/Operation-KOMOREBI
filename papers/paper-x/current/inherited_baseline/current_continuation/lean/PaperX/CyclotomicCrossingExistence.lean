import PaperX.CyclotomicCrossingContainment
import PaperX.AuxiliaryCyclotomicExistence

/-!
# Existence of the cyclotomic crossing over Q

The auxiliary field, prime conductor, primitive root, and crossing automorphism
are constructed. No prescribed arithmetic Frobenius occurrence is asserted.
-/

set_option autoImplicit false

noncomputable section

namespace PaperX.CyclotomicCrossingExistence

open IntermediateField CyclotomicCrossing AuxiliaryCyclotomicDisjoint

section Restriction

variable {K M : Type*} [Field K] [Field M] [Algebra K M]

/-- The left field, considered inside the compositum. -/
def leftPart (L A : IntermediateField K M) : IntermediateField K (L ⊔ A : IntermediateField K M) :=
  L.restrict le_sup_left

/-- The auxiliary field, considered inside the compositum. -/
def rightPart (L A : IntermediateField K M) : IntermediateField K (L ⊔ A : IntermediateField K M) :=
  A.restrict le_sup_right

/-- The restricted fields generate the compositum as an actual ambient field. -/
theorem parts_sup_eq_top (L A : IntermediateField K M) : leftPart L A ⊔ rightPart L A = ⊤ := by
  apply lift_injective
  simp only [leftPart, rightPart, lift_sup, lift_restrict, lift_top]

/-- Linear disjointness is preserved upon changing the ambient field to the compositum. -/
theorem parts_linearDisjoint (L A : IntermediateField K M)
    [FiniteDimensional K L] [FiniteDimensional K A] [IsGalois K L]
    (hdisj : L.LinearDisjoint A) : (leftPart L A).LinearDisjoint (rightPart L A) := by
  let eL : L ≃ₐ[K] leftPart L A := restrictAlgEquiv (le_sup_left : L ≤ L ⊔ A)
  have : IsGalois K (leftPart L A) := IsGalois.of_algEquiv eL
  apply LinearDisjoint.of_inf_eq_bot
  apply lift_injective
  simp only [leftPart, rightPart, lift_inf, lift_restrict, lift_bot, hdisj.inf_eq_bot]

/-- The restriction automorphism equality gives the actual action on each
element of the original left field after embedding in the compositum. -/
theorem action_of_restriction_eq (L A : IntermediateField K M)
    [Normal K (leftPart L A)] (sigma : L ≃ₐ[K] L)
    (rho : (L ⊔ A : IntermediateField K M) ≃ₐ[K] (L ⊔ A : IntermediateField K M))
    (h : AlgEquiv.restrictNormalHom (leftPart L A) rho =
      (restrictAlgEquiv (le_sup_left : L ≤ L ⊔ A)).autCongr sigma) :
    ∀ x : L, (rho (inclusion (le_sup_left : L ≤ L ⊔ A) x) : M) = (sigma x : M) := by
  let eL : L ≃ₐ[K] leftPart L A := restrictAlgEquiv le_sup_left
  intro x
  have hh := AlgEquiv.restrictNormal_commutes rho (leftPart L A) (eL x)
  change rho.restrictNormal (leftPart L A) = eL.autCongr sigma at h
  rw [h] at hh
  simp only [AlgEquiv.autCongr_apply, AlgEquiv.trans_apply, AlgEquiv.symm_apply_apply] at hh
  have heL (y : L) : (algebraMap (leftPart L A) (L ⊔ A : IntermediateField K M)) (eL y) =
      inclusion (le_sup_left : L ≤ L ⊔ A) y := rfl
  rw [heL, heL] at hh
  exact congrArg ((↑) : (L ⊔ A : IntermediateField K M) → M) hh.symm

end Restriction

section Existence

variable (M : Type*) [Field M] [CharZero M] [IsAlgClosed M] [Algebra.IsAlgebraic ℚ M]

/-- For every finite Galois number field inside an algebraic closure of Q and
every automorphism, the actual cyclotomic crossing exists. The prime conductor
can avoid any supplied finite set and exceed any supplied bound. -/
theorem exists_cyclotomic_crossing
    (L : IntermediateField ℚ M) [NumberField L] [IsGalois ℚ L]
    (sigma : L ≃ₐ[ℚ] L) (forbidden : Finset ℕ) (B : ℕ) :
    ∃ p : Nat.Primes, ∃ A : IntermediateField ℚ M, ∃ ζ : M,
      ∃ rho : (L ⊔ A : IntermediateField ℚ M) ≃ₐ[ℚ] (L ⊔ A : IntermediateField ℚ M),
      B < (p : ℕ) ∧ (p : ℕ) ∉ forbidden ∧ IsPrimitiveRoot ζ (p : ℕ) ∧
      NumberField (L ⊔ A : IntermediateField ℚ M) ∧
      IsGalois ℚ (L ⊔ A : IntermediateField ℚ M) ∧
      (∀ x : L, (rho (inclusion (le_sup_left : L ≤ L ⊔ A) x) : M) = (sigma x : M)) ∧
      fixedField (Subgroup.zpowers rho) ⊔ rightPart L A = ⊤ ∧
      IsGalois (fixedField (Subgroup.zpowers rho)) (L ⊔ A : IntermediateField ℚ M) ∧
      IsCyclic ((L ⊔ A : IntermediateField ℚ M) ≃ₐ[fixedField (Subgroup.zpowers rho)]
        (L ⊔ A : IntermediateField ℚ M)) ∧
      Module.finrank (fixedField (Subgroup.zpowers rho)) (L ⊔ A : IntermediateField ℚ M) =
        orderOf sigma ∧
      (L ⊔ A : IntermediateField ℚ M) ≤
        (adjoin ((fixedField (Subgroup.zpowers rho)).map (L ⊔ A).val) ({ζ} : Set M)).restrictScalars ℚ := by
  have hn : 0 < orderOf sigma := orderOf_pos sigma
  have : NeZero (orderOf sigma) := ⟨hn.ne'⟩
  obtain ⟨p, A, hpB, hpnot, hA, hdegree, hgal, hcyc, hdis⟩ :=
    AuxiliaryCyclotomicExistence.exists_cyclic_cyclotomic_disjoint
      M L (orderOf sigma) forbidden B
  have : IsGalois ℚ A := hgal
  have : IsCyclic (A ≃ₐ[ℚ] A) := hcyc
  have : FiniteDimensional ℚ A := Module.finite_of_finrank_pos (hdegree.symm ▸ hn)
  have : IsGalois ℚ (L ⊔ A : IntermediateField ℚ M) := {}
  let eL : L ≃ₐ[ℚ] leftPart L A := restrictAlgEquiv le_sup_left
  let eA : A ≃ₐ[ℚ] rightPart L A := restrictAlgEquiv le_sup_right
  have : IsGalois ℚ (leftPart L A) := IsGalois.of_algEquiv eL
  have : IsGalois ℚ (rightPart L A) := IsGalois.of_algEquiv eA
  have : IsCyclic ((rightPart L A) ≃ₐ[ℚ] (rightPart L A)) :=
    isCyclic_of_surjective eA.autCongr eA.autCongr.surjective
  have hdegree' : Module.finrank ℚ (rightPart L A) = orderOf (eL.autCongr sigma) := by
    rw [← eA.toLinearEquiv.finrank_eq, eL.autCongr.orderOf_eq, hdegree]
  obtain ⟨rho, hrestrict, hsup, hcyclic, hdeg⟩ := exists_crossing_of_cyclic_auxiliary
    (leftPart L A) (rightPart L A) (parts_linearDisjoint L A hdis.symm)
    (parts_sup_eq_top L A) (eL.autCongr sigma) hdegree'
  have : NeZero (p : ℕ) := ⟨p.property.ne_zero⟩
  let ζ : M := Classical.choose (HasEnoughRootsOfUnity.exists_primitiveRoot M (p : ℕ))
  have hζ : IsPrimitiveRoot ζ (p : ℕ) :=
    Classical.choose_spec (HasEnoughRootsOfUnity.exists_primitiveRoot M (p : ℕ))
  have hAζ : (rightPart L A).map (L ⊔ A).val ≤ adjoin ℚ ({ζ} : Set M) := by
    change lift (A.restrict (le_sup_right : A ≤ L ⊔ A)) ≤ _
    rw [lift_restrict]
    exact hA
  refine ⟨p, A, ζ, rho, hpB, hpnot, hζ, {}, inferInstance,
    action_of_restriction_eq L A sigma rho hrestrict,
    hsup, isGalois_fixedField_zpowers rho, hcyclic, ?_, ?_⟩
  · simpa only [eL.autCongr.orderOf_eq] using hdeg
  · have hh := fieldRange_le_adjoin_of_sup_eq_top _ (rightPart L A) hsup (L ⊔ A).val ζ hAζ
    simpa only [fieldRange_val] using hh

end Existence

end PaperX.CyclotomicCrossingExistence
