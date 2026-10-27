import PaperX.DenseTraceSeparation

/-! Character independence with all representation hypotheses discharged in the
finite-group, splitting-field case. This is NOT a proof for arbitrary profinite
Galois representations. Mathlib's character orthogonality theorem is the input. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.FiniteCharacters

open scoped BigOperators
open PaperX.FiniteSeparation
universe u v w
variable {K : Type u} [Field K] {I : Type v} [Fintype I]

/-- A biorthogonal family of linear tests proves linear independence. -/
theorem independent_of_tests {X : Type*} [DecidableEq I]
    (f : I → X → K) (test : I → (X → K) →ₗ[K] K)
    (ht : ∀ i j, test i (f j) = if j = i then 1 else 0) :
    LinearIndependent K f := by
  rw [Fintype.linearIndependent_iff]
  intro c hc i
  have h := congrArg (test i) hc
  simpa [ht] using h

/-- Averaging against an inverse character is an actual linear functional. -/
def characterTest {G : Type w} [Group G] [Fintype G]
    (χ : G → K) : (G → K) →ₗ[K] K :=
  (Nat.card G : K)⁻¹ • ∑ g, χ g⁻¹ • LinearMap.proj g

theorem characterTest_apply {G : Type w} [Group G] [Fintype G]
    (χ ψ : G → K) : characterTest χ ψ =
      (Nat.card G : K)⁻¹ * ∑ g, ψ g * χ g⁻¹ := by
  simp [characterTest, mul_comm]

/-- Pairwise nonisomorphic irreducible finite-dimensional representations of a finite
 group have independent characters over an algebraically closed field in which the
 group order is invertible. Dimensions are allowed to differ. -/
theorem independent_irreducible_characters {G : Type w} [Group G] [Fintype G]
    [IsAlgClosed K] [Invertible (Nat.card G : K)]
    (n : I → ℕ) (ρ : ∀ i, Representation K G (Fin (n i) → K))
    [∀ i, (ρ i).IsIrreducible]
    (hne : ∀ i j, Nonempty ((ρ i).Equiv (ρ j)) → i = j) :
    LinearIndependent K (fun i => (ρ i).character) := by
  classical
  apply independent_of_tests _ (fun i => characterTest (ρ i).character)
  intro i j
  rw [characterTest_apply, Representation.char_orthonormal]
  by_cases h : j = i
  · subst j
    simp only [ite_true]
    have he : Nonempty ((ρ i).Equiv (ρ i)) := ⟨Representation.Equiv.refl _⟩
    simp [he]
  · have he : ¬ Nonempty ((ρ i).Equiv (ρ j)) := fun hn => h (hne i j hn).symm
    simp [he, h]

/-- In this finite-group case the separator does not assume character independence. -/
theorem finite_group_separator {G : Type w} [Group G] [Fintype G]
    [DecidableEq I] [IsAlgClosed K] [Invertible (Nat.card G : K)]
    (n : I → ℕ) (ρ : ∀ i, Representation K G (Fin (n i) → K))
    [∀ i, (ρ i).IsIrreducible]
    (hne : ∀ i j, Nonempty ((ρ i).Equiv (ρ j)) → i = j) :
    ∃ s : I → G, Function.Injective s ∧
      (sampleMatrix (fun i => (ρ i).character) s).det ≠ 0 :=
  exists_nonsingular_samples _ (independent_irreducible_characters n ρ hne)

end PaperX.FiniteCharacters
