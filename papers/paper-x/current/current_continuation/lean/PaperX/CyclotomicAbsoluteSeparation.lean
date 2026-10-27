import PaperX.CyclotomicAbsoluteSamples
import PaperX.CyclotomicSystemSeparation
import PaperX.SurjectiveRepresentationPullback

/-! Prime separators for actual absolute-Galois representations obtained from
one fixed cyclotomic quotient. Values agree at every global lift of the finite
arithmetic Frobenius. This statement does not turn arbitrary choices of such
lifts into a dense sample in the full absolute Galois group. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicAbsoluteSeparation
open PaperX.CyclotomicPrimeCoverage PaperX.CyclotomicAbsoluteSamples
open PaperX.CompatibleSystemRigidity PaperX.FiniteSeparation
open PaperX.SurjectiveRepresentationPullback

variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]

omit [NeZero n] in
/-- Pullback through the actual finite restriction is continuous for any
chosen topology on the coefficient endomorphisms. -/
theorem pullback_action_continuous {K V : Type*} [Field K] [AddCommGroup V]
    [Module K V] [TopologicalSpace (Module.End K V)]
    (ρ : Representation K Gal(L/ℚ) V) :
    Continuous (fun γ : Field.absoluteGaloisGroup ℚ => (ρ.comp (restrictionMap n L)) γ) :=
  (continuous_of_discreteTopology : Continuous (fun σ : Gal(L/ℚ) => ρ σ)).comp
    (restrictionMap_continuous n L)

section Systems
variable {Λ I E : Type*} [Field E] [Fintype I] [DecidableEq I]
variable {K : Λ → Type*} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
  [∀ l, TopologicalSpace (K l)] [∀ l, IsTopologicalRing (K l)] [∀ l, T2Space (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)] [∀ l i, FiniteDimensional (K l) (W l i)]
variable (ρ : (l : Λ) → (i : I) → Representation (K l) Gal(L/ℚ) (W l i))
variable [∀ l i, Representation.IsIrreducible ((ρ l i).comp (restrictionMap n L))]
variable (emb : (l : Λ) → E →+* K l) (t : I → PermittedPrime n ∅ → E)
variable (good : Λ → PermittedPrime n ∅ → Prop)
variable (hgood : ∀ l, Set.Finite {p | ¬ good l p})
variable (compat : ∀ l i p, good l p →
  Representation.character ((ρ l i).comp (restrictionMap n L)) (liftSample n L p) =
    emb l (t i p))
variable (hne : ∀ i j,
  MemberwiseEquiv (fun l i => (ρ l i).comp (restrictionMap n L)) i j → i = j)

include hgood compat hne in
/-- Distinct actual absolute-Galois systems factoring through the fixed field
admit a common algebraic separator at distinct permitted rational primes.
The ordinary trace identity holds for every lift of the finite Frobenius and
retains each member's good-prime condition. -/
theorem finite_absolute_system_separator (l₀ : Λ) (forbidden : Finset ℕ) :
    ∃ v : I → PermittedPrime n ∅, Function.Injective (fun i => (v i).val) ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, (v i).val ∉ forbidden) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      ∀ l j i (γ : Field.absoluteGaloisGroup ℚ),
        restrictionMap n L γ = primeSample n L ∅ (v j) → good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i =
          Representation.character ((ρ l i).comp (restrictionMap n L)) γ := by
  let : ∀ l i, (ρ l i).IsIrreducible := fun l i =>
    (isIrreducible_iff (restrictionMap n L) (restrictionMap_surjective n L) (ρ l i)).mp
      inferInstance
  have hc : ∀ l i p, good l p →
      (ρ l i).character (primeSample n L ∅ p) = emb l (t i p) := by
    intro l i p hp
    simpa only [character_pullback, restriction_liftSample] using compat l i p hp
  have hn : ∀ i j, MemberwiseEquiv ρ i j → i = j := by
    intro i j hij
    exact hne i j ((memberwiseEquiv_iff (restrictionMap n L)
      (restrictionMap_surjective n L) ρ i j).mpr hij)
  obtain ⟨v, hv, hg, hb, hd, hdl, ht⟩ :=
    PaperX.CyclotomicSystemSeparation.finite_prime_system_separator_avoiding
      n L ρ emb t good hgood hc hn l₀ forbidden
  refine ⟨v, hv, hg, hb, hd, hdl, ?_⟩
  intro l j i γ hγ hp
  rw [pullback_character_on_lift n L (ρ l i) (v j) γ hγ]
  exact ht l j i hp

end Systems
end PaperX.CyclotomicAbsoluteSeparation
