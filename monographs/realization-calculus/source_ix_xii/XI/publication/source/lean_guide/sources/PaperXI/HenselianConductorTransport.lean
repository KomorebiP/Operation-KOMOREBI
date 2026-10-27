import PaperXI.HenselianWeilAttachment

/-! Conductor invariance for the actual base change to the Hensel-generated field.
The valuation ring is unchanged upstairs. This is not ramified quotient invariance. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HenselianConductorTransport
open IsLocalRing PaperXI.ResidueWeil PaperXI.FiniteResidueBaseChange
open PaperXI.ValuationRamification PaperXI.ValuationConductor PaperXI.HenselianWeilAttachment
variable (k k' K : Type*) {L : Type*} [Field k] [Fintype k] [Field k'] [Fintype k']
  [Algebra k k'] [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A]
  [Algebra k (ResidueField A)] [Algebra k' (ResidueField A)]
  [Algebra.IsAlgebraic k (ResidueField A)] [Algebra.IsAlgebraic k' (ResidueField A)]

/-- Lower congruence groups commute with the constructed decomposition equivalence. -/
def localLowerEquiv (i : ℕ) :
    lower A (A.decompositionSubgroup (liftedField k' K A)) i ≃*
    lower A (UnramifiedValuation.fixingGroup k' K A) i where
  toFun g := ⟨decompositionEquiv k' K A g.val, g.property⟩
  invFun g := ⟨(decompositionEquiv k' K A).symm g.val, by
    intro x
    rw [← HenselianWeilAttachment.ring_action k' K A,
      (decompositionEquiv k' K A).apply_symm_apply]
    exact g.property x⟩
  left_inv g := Subtype.ext ((decompositionEquiv k' K A).symm_apply_apply g.val)
  right_inv g := Subtype.ext ((decompositionEquiv k' K A).apply_symm_apply g.val)
  map_mul' g h := Subtype.ext ((decompositionEquiv k' K A).map_mul g.val h.val)

/-- Every lower group over the new field is isomorphic to the original lower group. -/
def lowerEquiv (i : ℕ) :
    lower A (A.decompositionSubgroup (liftedField k' K A)) i ≃*
    lower A (A.decompositionSubgroup K) i :=
  (localLowerEquiv k' K A i).trans (UnramifiedConductor.lowerEquiv A
    (A.decompositionSubgroup K) (UnramifiedValuation.fixingGroup k' K A)
    (UnramifiedValuation.contains_inertia k' K A) i)

omit [Algebra.IsAlgebraic k' (ResidueField A)] in
theorem lower_card (i : ℕ) :
    Nat.card (lower A (A.decompositionSubgroup (liftedField k' K A)) i) =
    Nat.card (lower A (A.decompositionSubgroup K) i) :=
  Nat.card_congr (lowerEquiv k' K A i).toEquiv

/-- The actual operators agree under the degree-dilating embedding. -/
theorem embedding_lift (i : ℕ) (g : lower A (A.decompositionSubgroup (liftedField k' K A)) i) :
    HenselianWeilAttachment.embedding k k' K A
      (lift A (A.decompositionSubgroup (liftedField k' K A)) (geometric k' (ResidueField A)) i g) =
    lift A (A.decompositionSubgroup K) (geometric k (ResidueField A)) i (lowerEquiv k' K A i g) := by
  apply Subtype.ext
  apply Prod.ext
  · rfl
  · simp [HenselianWeilAttachment.embedding, HenselianWeilAttachment.pullbackEquiv,
      UnramifiedValuation.embedding, UnramifiedConductor.embedding, lift]

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- Equality of genuine fixed subspaces on the same carrier. -/
theorem fixed_eq
    (ρ : Representation ℂ (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A))) V) (i : ℕ) :
    fixed A (A.decompositionSubgroup (liftedField k' K A)) (geometric k' (ResidueField A))
      (ρ.comp (HenselianWeilAttachment.embedding k k' K A)) i =
    fixed A (A.decompositionSubgroup K) (geometric k (ResidueField A)) ρ i := by
  ext v
  constructor
  · intro hv g
    let g' := (lowerEquiv k' K A i).symm g
    have h := hv g'
    change ρ (HenselianWeilAttachment.embedding k k' K A (lift A _ _ i g')) v = v at h
    rw [embedding_lift, (lowerEquiv k' K A i).apply_symm_apply] at h
    exact h
  · intro hv g
    change ρ (HenselianWeilAttachment.embedding k k' K A (lift A _ _ i g)) v = v
    rw [embedding_lift]
    exact hv _

/-- The conventional inertia denominator and fixed-space codimension agree together. -/
theorem summand_eq
    (ρ : Representation ℂ (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A))) V) (i : ℕ) :
    summand A (A.decompositionSubgroup (liftedField k' K A)) (geometric k' (ResidueField A))
      (ρ.comp (HenselianWeilAttachment.embedding k k' K A)) i =
    summand A (A.decompositionSubgroup K) (geometric k (ResidueField A)) ρ i := by
  unfold summand codimension
  rw [lower_card k' K A i, lower_card k' K A 0, fixed_eq k k' K A ρ i]

theorem swan_eq
    (ρ : Representation ℂ (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A))) V) :
    swan A (A.decompositionSubgroup (liftedField k' K A)) (geometric k' (ResidueField A))
      (ρ.comp (HenselianWeilAttachment.embedding k k' K A)) =
    swan A (A.decompositionSubgroup K) (geometric k (ResidueField A)) ρ := by
  unfold swan
  apply tsum_congr
  intro i
  exact summand_eq k k' K A ρ (i+1)

theorem artin_eq
    (ρ : Representation ℂ (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A))) V) :
    artin A (A.decompositionSubgroup (liftedField k' K A)) (geometric k' (ResidueField A))
      (ρ.comp (HenselianWeilAttachment.embedding k k' K A)) =
    artin A (A.decompositionSubgroup K) (geometric k (ResidueField A)) ρ := by
  unfold artin codimension
  rw [swan_eq, fixed_eq]

/-- For a finite decomposition group over a DVR, the common sum is summable. -/
theorem summable_source [IsDiscreteValuationRing A] [Finite (A.decompositionSubgroup K)]
    (ρ : Representation ℂ (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A))) V) :
    Summable (summand A (A.decompositionSubgroup (liftedField k' K A))
      (geometric k' (ResidueField A)) (ρ.comp (HenselianWeilAttachment.embedding k k' K A))) := by
  have h : summand A (A.decompositionSubgroup (liftedField k' K A))
      (geometric k' (ResidueField A)) (ρ.comp (HenselianWeilAttachment.embedding k k' K A)) =
      summand A (A.decompositionSubgroup K) (geometric k (ResidueField A)) ρ := by
    funext i; exact summand_eq k k' K A ρ i
  rw [h]
  exact summable_summands A (A.decompositionSubgroup K) _ ρ

end PaperXI.HenselianConductorTransport
