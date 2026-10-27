import PaperX.CyclotomicPrimeCoverage
import PaperX.CompatibleSystemSeparation
import Mathlib.Data.Finset.Preimage

/-! Arithmetic prime separators for representations of a fixed finite cyclotomic
Galois group. Prime coverage survives arbitrary finite exclusions by the proved
Dirichlet theorem. The existing Krull topology is discrete for this number-field
extension, so continuity of the representation characters is automatic.
The automorphisms use the arithmetic p-power Frobenius convention established
in `CyclotomicPrimeCoverage`; they are not elements of the full absolute Galois group. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicSystemSeparation
open PaperX.CyclotomicPrimeCoverage PaperX.CofiniteConjugacyCoverage
open PaperX.CompatibleSystemRigidity PaperX.FiniteSeparation

variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]

/-- Every finite deletion of permitted rational primes still covers the actual
finite cyclotomic Galois group, hence every one of its open normal quotients. -/
theorem primeSample_cofiniteQuotientCoverage (forbidden : Finset ℕ) :
    CofiniteQuotientCoverage (primeSample n L forbidden) := by
  classical
  intro bad H σ
  obtain ⟨p, hpgt, hσ⟩ := exists_prime_with_automorphism n L forbidden σ
    ((bad.image Subtype.val).sup id)
  have hp : p ∉ bad := by
    intro hm
    have hle : p.val ≤ (bad.image Subtype.val).sup id :=
      Finset.le_sup (f := id) (Finset.mem_image.mpr ⟨p, hm, rfl⟩)
    exact (not_lt_of_ge hle) hpgt
  refine ⟨⟨p, hp⟩, 1, ?_⟩
  simp [hσ]

/-- Density on any cofinite good-prime set is a consequence of arithmetic prime
existence for this extension, not an additional sampling hypothesis. -/
theorem dense_good_prime_samples (good : PermittedPrime n ∅ → Prop)
    (hgood : Set.Finite {p | ¬ good p}) :
    DenseRange (fun q : {p : PermittedPrime n ∅ // good p} × Gal(L/ℚ) =>
      q.2 * primeSample n L ∅ q.1 * q.2⁻¹) :=
  dense_on_cofinite _ (primeSample_cofiniteQuotientCoverage n L ∅) good hgood

section Systems
variable {Λ I E : Type*} [Field E] [Fintype I] [DecidableEq I]
variable {K : Λ → Type*} [∀ l, Field (K l)] [∀ l, CharZero (K l)]
  [∀ l, TopologicalSpace (K l)] [∀ l, IsTopologicalRing (K l)] [∀ l, T2Space (K l)]
variable {W : Λ → I → Type*} [∀ l i, AddCommGroup (W l i)]
  [∀ l i, Module (K l) (W l i)] [∀ l i, FiniteDimensional (K l) (W l i)]
variable (ρ : (l : Λ) → (i : I) → Representation (K l) Gal(L/ℚ) (W l i))
variable [∀ l i, (ρ l i).IsIrreducible]
variable (emb : (l : Λ) → E →+* K l) (t : I → PermittedPrime n ∅ → E)
variable (good : Λ → PermittedPrime n ∅ → Prop)
variable (hgood : ∀ l, Set.Finite {p | ¬ good l p})
variable (compat : ∀ l i p, good l p →
  (ρ l i).character (primeSample n L ∅ p) = emb l (t i p))
variable (hne : ∀ i j, MemberwiseEquiv ρ i j → i = j)

include hgood compat hne in
/-- Pairwise componentwise nonisomorphic systems on the fixed cyclotomic Galois
group have a common algebraic prime separator. Its determinant remains nonzero
under every coefficient embedding. Each actual trace comparison retains its own
member's good-prime condition. No coverage or character-continuity hypothesis is supplied. -/
theorem finite_prime_system_separator (l₀ : Λ) (bad : Finset (PermittedPrime n ∅)) :
    ∃ v : I → PermittedPrime n ∅, Function.Injective v ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, v i ∉ bad) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      ∀ l j i, good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i =
          (ρ l i).character (primeSample n L ∅ (v j)) := by
  exact PaperX.CompatibleSystemSeparation.finite_system_separator ρ
    (fun _ _ => continuous_of_discreteTopology) emb t good hgood
    (primeSample n L ∅) (primeSample_cofiniteQuotientCoverage n L ∅) compat hne l₀ bad

include hgood compat hne in
/-- Exclusions can be stated directly as a finite set of rational primes.
The selected underlying natural numbers are pairwise distinct. -/
theorem finite_prime_system_separator_avoiding (l₀ : Λ) (forbidden : Finset ℕ) :
    ∃ v : I → PermittedPrime n ∅, Function.Injective (fun i => (v i).val) ∧
      (∀ i, good l₀ (v i)) ∧ (∀ i, (v i).val ∉ forbidden) ∧
      (sampleMatrix t v).det ≠ 0 ∧
      (∀ l, ((emb l).mapMatrix (sampleMatrix t v)).det ≠ 0) ∧
      ∀ l j i, good l (v j) →
        (emb l).mapMatrix (sampleMatrix t v) j i =
          (ρ l i).character (primeSample n L ∅ (v j)) := by
  classical
  let bad : Finset (PermittedPrime n ∅) :=
    forbidden.preimage Subtype.val Subtype.val_injective.injOn
  obtain ⟨v, hv, hg, hb, hd, hdl, ht⟩ :=
    finite_prime_system_separator n L ρ emb t good hgood compat hne l₀ bad
  refine ⟨v, Subtype.val_injective.comp hv, hg, ?_, hd, hdl, ht⟩
  intro i hp
  exact hb i (Finset.mem_preimage.mpr hp)

end Systems

/-- The conductor-four instance uses Mathlib's actual cyclotomic field over ℚ. -/
def quarticSample (p : PermittedPrime 4 ∅) : Gal(CyclotomicField 4 ℚ/ℚ) := by
  let : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) :=
    CyclotomicField.isCyclotomicExtension 4 ℚ
  exact primeSample 4 (CyclotomicField 4 ℚ) ∅ p

/-- Concrete arithmetic coverage for the actual conductor-four field survives
arbitrary finite deletions of permitted rational primes. -/
theorem quartic_cofinite_coverage : CofiniteQuotientCoverage quarticSample := by
  let : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) :=
    CyclotomicField.isCyclotomicExtension 4 ℚ
  exact primeSample_cofiniteQuotientCoverage 4 (CyclotomicField 4 ℚ) ∅

/-- Every automorphism of the conductor-four field occurs at arbitrarily large
actual rational primes, with the previously fixed arithmetic convention. -/
theorem exists_large_quartic_sample (σ : Gal(CyclotomicField 4 ℚ/ℚ)) (B : ℕ) :
    ∃ p : PermittedPrime 4 ∅, B < p.val ∧ quarticSample p = σ := by
  let : IsCyclotomicExtension {4} ℚ (CyclotomicField 4 ℚ) :=
    CyclotomicField.isCyclotomicExtension 4 ℚ
  exact exists_prime_with_automorphism 4 (CyclotomicField 4 ℚ) ∅ σ B

end PaperX.CyclotomicSystemSeparation
