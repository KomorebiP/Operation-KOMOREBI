import PaperX.CompatibleSystemRigidity
import PaperX.TraceRecovery

/-! The common algebraic separator for pairwise nonisomorphic compatible systems.
The system-to-member bridge is derived. Cofinite arithmetic coverage remains
explicit; selected-place comparisons retain each coefficient prime's good set. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CompatibleSystemSeparation
open PaperX.CompatibleSystemRigidity PaperX.CofiniteConjugacyCoverage
open PaperX.FiniteSeparation PaperX.TraceRecovery

variable {Λ I G X E : Type*} [Group G] [Field E] [TopologicalSpace G]
  [IsTopologicalGroup G] [CompactSpace G] [TotallyDisconnectedSpace G]
  [Fintype I] [DecidableEq I]
variable {K : Λ → Type*} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
  [∀ l, TopologicalSpace (K l)] [∀ l, IsTopologicalRing (K l)] [∀ l, T2Space (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)] [∀ l i, FiniteDimensional (K l) (W l i)]
variable (ρ : (l : Λ) → (i : I) → Representation (K l) G (W l i))
variable [∀ l i, (ρ l i).IsIrreducible]
variable (hc : ∀ l i, Continuous (ρ l i).character)
variable (emb : (l : Λ) → E →+* K l) (t : I → X → E)
variable (good : Λ → X → Prop) (hgood : ∀ l, Set.Finite {x | ¬ good l x})
variable (s : X → G) (coverage : CofiniteQuotientCoverage s)
variable (compat : ∀ l i x, good l x → (ρ l i).character (s x) = emb l (t i x))
variable (hne : ∀ i j, MemberwiseEquiv ρ i j → i = j)

include hc hgood coverage compat hne in
/-- Distinct common-algebraic trace samples can avoid any prescribed finite set.
The matrix remains nonsingular at every embedding. Its entries agree with actual
member traces only at the places good for that coefficient prime. -/
theorem finite_system_separator (l₀ : Λ) (bad : Finset X) :
    ∃ v : I → X, Function.Injective v ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, v i ∉ bad) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      ∀ l j i, good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i = (ρ l i).character (s (v j)) := by
  classical
  have hov : ∀ l m, DenseRange
      (fun p : {x : X // good l x ∧ good m x} × G => p.2 * s p.1 * p.2⁻¹) := by
    intro l m
    apply dense_on_cofinite s coverage
    apply ((hgood l).union (hgood m)).subset
    intro x hx
    simpa only [Set.mem_union, Set.mem_ofPred_eq, not_and_or] using hx
  have hni := nonisomorphic_members ρ hc emb t good s compat hov hne l₀
  have hi := PaperX.GeneralCharacters.independent_irreducible_characters (ρ l₀) hni
  have hd : DenseRange
      (fun p : {x : X // good l₀ x ∧ x ∉ bad} × G => p.2 * s p.1 * p.2⁻¹) := by
    apply dense_on_cofinite s coverage
    apply ((hgood l₀).union bad.finite_toSet).subset
    intro x hx
    by_cases hg : good l₀ x
    · exact Or.inr (by simpa only [Set.mem_ofPred_eq, hg, true_and, not_not] using hx)
    · exact Or.inl hg
  obtain ⟨v, hv, hdet⟩ := common_trace_separator (emb l₀)
    (fun i (x : {x : X // good l₀ x ∧ x ∉ bad}) => t i x)
    (fun i => (ρ l₀ i).character) (hc l₀) hi
    (fun x : {x : X // good l₀ x ∧ x ∉ bad} => s x) hd
    (fun i g x => (ρ l₀ i).char_conj (s x) g)
    (fun i x => (compat l₀ i x x.property.1).symm)
  refine ⟨fun i => (v i).val, Subtype.val_injective.comp hv,
    fun i => (v i).property.1, fun i => (v i).property.2, hdet, ?_, ?_⟩
  · intro l
    exact (determinant_transport (emb l) _).mpr hdet
  · intro l j i hj
    exact (compat l i (v j) hj).symm

end PaperX.CompatibleSystemSeparation
