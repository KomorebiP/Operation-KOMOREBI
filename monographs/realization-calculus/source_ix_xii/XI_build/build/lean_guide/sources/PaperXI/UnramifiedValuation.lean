import PaperXI.FiniteResidueSubgroup
import PaperXI.UnramifiedConductor
import PaperXI.ValuationTameEndpoint

/-! Source-facing unramified residue-base attachment to an actual valuation
subring and decomposition-group action. The subgroup fixes the actual embedded
finite residue extension, rather than being assigned an index by a certificate.
This still does not construct its lift to a local-field unramified extension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.UnramifiedValuation
open PaperXI.ResidueWeil PaperXI.ResidueDegreeBaseChange PaperXI.FiniteResidueBaseChange
open PaperXI.ValuationRamification PaperXI.ValuationConductor

variable (k k' K : Type*) {L : Type*} [Field k] [Fintype k] [Field k'] [Fintype k']
  [Algebra k k'] [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [Algebra k (IsLocalRing.ResidueField A)]
  [Algebra k' (IsLocalRing.ResidueField A)]
  [Algebra.IsAlgebraic k (IsLocalRing.ResidueField A)]
  [Algebra.IsAlgebraic k' (IsLocalRing.ResidueField A)]

abbrev fixingGroup :=
  FiniteResidueSubgroup.fixing k' (IsLocalRing.ResidueField A)
    (residue A (A.decompositionSubgroup K))

/-- No new convention relative to the preceding valuation release. -/
theorem frobenius_agrees : geometric k (IsLocalRing.ResidueField A) =
    ValuationTameEndpoint.geometricFrobenius k A := rfl

omit [Fintype k'] [Algebra.IsAlgebraic k' (IsLocalRing.ResidueField A)] in
/-- The pointwise residue-field stabilizer contains all actual inertia. -/
theorem contains_inertia : lower A (A.decompositionSubgroup K) 0 ≤ fixingGroup k' K A := by
  rw [lower_zero_eq_residue_kernel]
  exact FiniteResidueSubgroup.kernel_le_fixing k' (IsLocalRing.ResidueField A) _

/-- Natural inclusion of the two actually constructed residue-action pullbacks. -/
def embedding :
    Pullback (residue A (fixingGroup k' K A)) (geometric k' (IsLocalRing.ResidueField A)) →*
      Pullback (residue A (A.decompositionSubgroup K)) (geometric k (IsLocalRing.ResidueField A)) :=
  UnramifiedConductor.embedding A (A.decompositionSubgroup K) (fixingGroup k' K A)
    (geometric k (IsLocalRing.ResidueField A)) (geometric k' (IsLocalRing.ResidueField A))
    (Module.finrank k k') (geometric_tower k (IsLocalRing.ResidueField A) k')

/-- The arithmetic field degree controls the integer degree dilation. -/
theorem degree_formula (w : Pullback (residue A (fixingGroup k' K A))
    (geometric k' (IsLocalRing.ResidueField A))) :
    Multiplicative.toAdd (degree (residue A (A.decompositionSubgroup K))
      (geometric k (IsLocalRing.ResidueField A)) (embedding k k' K A w)) =
    (Module.finrank k k' : ℤ) * Multiplicative.toAdd
      (degree (residue A (fixingGroup k' K A)) (geometric k' (IsLocalRing.ResidueField A)) w) := rfl

/-- The equivalence is to the subgroup defined by divisibility, not merely a subgroup
having the same finite index. -/
def degreeSubgroupEquiv :
    Pullback (residue A (fixingGroup k' K A)) (geometric k' (IsLocalRing.ResidueField A)) ≃*
      periodSubgroup (residue A (A.decompositionSubgroup K))
        (geometric k (IsLocalRing.ResidueField A)) (Module.finrank k k') :=
  FiniteResidueSubgroup.unramifiedEquiv k k' (IsLocalRing.ResidueField A) _

/-- This direct inclusion is faithful before passing to a quotient. -/
theorem embedding_injective : Function.Injective (embedding k k' K A) :=
  UnramifiedConductor.embedding_injective A (A.decompositionSubgroup K) (fixingGroup k' K A)
    _ _ Module.finrank_pos.ne' (geometric_tower k (IsLocalRing.ResidueField A) k')

/-- The natural embedding has exactly the stated degree-divisible range. -/
theorem embedding_range : (embedding k k' K A).range =
    periodSubgroup (residue A (A.decompositionSubgroup K))
      (geometric k (IsLocalRing.ResidueField A)) (Module.finrank k k') := by
  ext w
  constructor
  · rintro ⟨v, rfl⟩
    rw [mem_periodSubgroup, degree_formula]
    exact dvd_mul_right _ _
  · intro hw
    obtain ⟨m, hm⟩ := (mem_periodSubgroup _ _ _ w).mp hw
    have hg : w.val.1 ∈ fixingGroup k' K A :=
      (FiniteResidueSubgroup.projection_mem_iff k k' (IsLocalRing.ResidueField A) _ w).mpr
        ((mem_periodSubgroup _ _ _ w).mp hw)
    let v : Pullback (residue A (fixingGroup k' K A)) (geometric k' (IsLocalRing.ResidueField A)) :=
      ⟨(⟨w.val.1, hg⟩, Multiplicative.ofAdd m), by
        change residue A (A.decompositionSubgroup K) w.val.1 =
          geometric k' (IsLocalRing.ResidueField A) ^ m
        rw [← geometric_tower k (IsLocalRing.ResidueField A) k', ← zpow_natCast, ← zpow_mul, ← hm]
        exact w.property⟩
    refine ⟨v, ?_⟩
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · exact Multiplicative.toAdd.injective hm.symm

omit [Algebra k' (IsLocalRing.ResidueField A)] [Algebra.IsAlgebraic k' (IsLocalRing.ResidueField A)] in
/-- Index f is a theorem once degree one lifts; existence of that lift stays explicit. -/
theorem degree_index (hF : geometric k (IsLocalRing.ResidueField A) ∈
    (residue A (A.decompositionSubgroup K)).range) :
    Nat.card (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (IsLocalRing.ResidueField A)) ⧸
      periodSubgroup (residue A (A.decompositionSubgroup K))
        (geometric k (IsLocalRing.ResidueField A)) (Module.finrank k k')) = Module.finrank k k' := by
  let : NeZero (Module.finrank k k') := ⟨Module.finrank_pos.ne'⟩
  exact quotient_card _ _ _ hF

/-- Compatible q^{-degree} normalization; no reduction of integer degree modulo a residue order. -/
theorem norm_compatibility (w : Pullback (residue A (fixingGroup k' K A))
    (geometric k' (IsLocalRing.ResidueField A))) :
    (Fintype.card k' : ℝ) ^ (-Multiplicative.toAdd
      (degree (residue A (fixingGroup k' K A)) (geometric k' (IsLocalRing.ResidueField A)) w)) =
    (Fintype.card k : ℝ) ^ (-Multiplicative.toAdd
      (degree (residue A (A.decompositionSubgroup K)) (geometric k (IsLocalRing.ResidueField A))
        (embedding k k' K A w))) := by
  have hc : (Fintype.card k' : ℝ) = (Fintype.card k : ℝ) ^ Module.finrank k k' := by
    exact_mod_cast (Module.card_eq_pow_finrank (K := k) (V := k'))
  rw [hc, ← zpow_natCast, ← zpow_mul, degree_formula, mul_neg]

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- All fixed spaces and ALL weighted terms are invariant under the actual residue-base restriction.
The statement does not assume tame action, irreducibility, or a precomputed conductor. -/
theorem source [IsDiscreteValuationRing A] [Finite (A.decompositionSubgroup K)]
    (ρ : Representation ℂ (Pullback (residue A (A.decompositionSubgroup K))
      (geometric k (IsLocalRing.ResidueField A))) V) :
    (∀ i : ℕ, Nat.card (lower A (fixingGroup k' K A) i) = Nat.card (lower A (A.decompositionSubgroup K) i)) ∧
    (∀ i : ℕ, fixed A (fixingGroup k' K A) (geometric k' (IsLocalRing.ResidueField A))
      (ρ.comp (embedding k k' K A)) i =
      fixed A (A.decompositionSubgroup K) (geometric k (IsLocalRing.ResidueField A)) ρ i) ∧
    (∀ i : ℕ, summand A (fixingGroup k' K A) (geometric k' (IsLocalRing.ResidueField A))
      (ρ.comp (embedding k k' K A)) i =
      summand A (A.decompositionSubgroup K) (geometric k (IsLocalRing.ResidueField A)) ρ i) ∧
    swan A (fixingGroup k' K A) (geometric k' (IsLocalRing.ResidueField A))
      (ρ.comp (embedding k k' K A)) =
      swan A (A.decompositionSubgroup K) (geometric k (IsLocalRing.ResidueField A)) ρ ∧
    artin A (fixingGroup k' K A) (geometric k' (IsLocalRing.ResidueField A))
      (ρ.comp (embedding k k' K A)) =
      artin A (A.decompositionSubgroup K) (geometric k (IsLocalRing.ResidueField A)) ρ ∧
    Summable (summand A (fixingGroup k' K A) (geometric k' (IsLocalRing.ResidueField A))
      (ρ.comp (embedding k k' K A))) := by
  let hI := contains_inertia k' K A
  let hp := geometric_tower k (IsLocalRing.ResidueField A) k'
  exact ⟨UnramifiedConductor.lower_card A (A.decompositionSubgroup K) _ hI,
    UnramifiedConductor.fixed_eq A (A.decompositionSubgroup K) _ _ _ _ hp hI ρ,
    UnramifiedConductor.summand_eq A (A.decompositionSubgroup K) _ _ _ _ hp hI ρ,
    UnramifiedConductor.swan_eq A (A.decompositionSubgroup K) _ _ _ _ hp hI ρ,
    UnramifiedConductor.artin_eq A (A.decompositionSubgroup K) _ _ _ _ hp hI ρ,
    UnramifiedConductor.summable_restriction A (A.decompositionSubgroup K) _ _ _ _ hp hI ρ⟩

end PaperXI.UnramifiedValuation
