import ConjugationProjectorProbes
import QuotientNoInvariantsAveraging
import Mathlib.RepresentationTheory.Irreducible

namespace Komorebi.StrongArtin.ConjugationQuotientNoInvariants

open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.QuotientNoInvariantsAveraging

noncomputable section

variable {k G W : Type*}
  [Field k] [Group G]
  [AddCommGroup W] [Module k W]

/-- The scalar/cyclic defect line in the endomorphism representation. -/
def scalarLine : Submodule k (Module.End k W) :=
  k ∙ (1 : Module.End k W)

/-- The scalar line is stable under conjugation by any representation. -/
theorem scalarLine_stable
    (ρ : Representation k G W) :
    ∀ g : G,
      scalarLine (k := k) (W := W) ≤
        (scalarLine (k := k) (W := W)).comap
          (conjugationRepresentation ρ g) := by
  intro g X hX
  change conjugationRepresentation ρ g X ∈ scalarLine (k := k) (W := W)
  rw [scalarLine, Submodule.mem_span_singleton] at hX ⊢
  rcases hX with ⟨a, rfl⟩
  refine ⟨a, ?_⟩
  ext w
  simp [conjugationRepresentation_apply]

/-- A conjugation-fixed endomorphism commutes with the original representation. -/
theorem commutes_of_conjugation_fixed
    (ρ : Representation k G W) (X : Module.End k W)
    (hfixed : ∀ g : G, conjugationRepresentation ρ g X = X) :
    ∀ g : G, ρ g * X = X * ρ g := by
  intro g
  calc
    ρ g * X = (ρ g * X * ρ g⁻¹) * ρ g := by
      simp [mul_assoc, ← ρ.map_mul]
    _ = X * ρ g := congrArg (fun Y : Module.End k W => Y * ρ g) (hfixed g)

/-- Under an explicit Schur-commutant hypothesis, the conjugation quotient by
scalars has no invariant vectors. -/
theorem quotient_by_scalars_has_no_invariants_of_commutant
    [Fintype G]
    (ρ : Representation k G W)
    (hcomm : ∀ X : Module.End k W,
      (∀ g : G, ρ g * X = X * ρ g) →
        X ∈ scalarLine (k := k) (W := W))
    (hcard : (Fintype.card G : k) ≠ 0) :
    ∀ q : Module.End k W ⧸ scalarLine (k := k) (W := W),
      (∀ g : G,
        ((conjugationRepresentation ρ).quotient
          (scalarLine (k := k) (W := W)) (scalarLine_stable ρ)) g q = q) →
      q = 0 := by
  apply quotient_has_no_invariants
    (conjugationRepresentation ρ)
    (scalarLine (k := k) (W := W))
    (scalarLine_stable ρ)
  · intro X hX
    exact hcomm X (commutes_of_conjugation_fixed ρ X hX)
  · exact hcard

/-- Schur's lemma in the exact form needed above: for an irreducible
finite-dimensional representation over an algebraically closed field, every
commuting endomorphism lies in the scalar line. -/
theorem commutant_le_scalarLine_of_irreducible
    [FiniteDimensional k W] [IsAlgClosed k]
    (ρ : Representation k G W) [ρ.IsIrreducible]
    (X : Module.End k W)
    (hcomm : ∀ g : G, ρ g * X = X * ρ g) :
    X ∈ scalarLine (k := k) (W := W) := by
  let f : ρ.IntertwiningMap ρ :=
    X.intertwiningMap_of_isIntertwiningMap ρ ρ (by
      intro g w
      have h := congrArg (fun Y : Module.End k W => Y w) (hcomm g).symm
      simpa using h)
  obtain ⟨a, ha⟩ :=
    Representation.IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
      (ρ := ρ) |>.2 f
  rw [scalarLine, Submodule.mem_span_singleton]
  refine ⟨a, ?_⟩
  ext w
  have haw := congrArg (fun z : ρ.IntertwiningMap ρ => z w) ha
  simpa [f, Algebra.algebraMap_eq_smul_one] using haw

/-- **Transverse no-invariants theorem.** In the prime-to-characteristic
irreducible regime, the conjugation representation modulo the scalar/cyclic
line has no nonzero invariant vector. -/
theorem quotient_by_scalars_has_no_invariants
    [Fintype G] [FiniteDimensional k W] [IsAlgClosed k]
    (ρ : Representation k G W) [ρ.IsIrreducible]
    (hcard : (Fintype.card G : k) ≠ 0) :
    ∀ q : Module.End k W ⧸ scalarLine (k := k) (W := W),
      (∀ g : G,
        ((conjugationRepresentation ρ).quotient
          (scalarLine (k := k) (W := W)) (scalarLine_stable ρ)) g q = q) →
      q = 0 := by
  apply quotient_by_scalars_has_no_invariants_of_commutant ρ
  · intro X hX
    exact commutant_le_scalarLine_of_irreducible ρ X hX
  · exact hcard

end

end Komorebi.StrongArtin.ConjugationQuotientNoInvariants

namespace Komorebi.StrongArtin.ConjugationQuotientNoInvariants

open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.NoTrivialQuotientAveraging

noncomputable section

variable {k G W T : Type*}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W]
  [AddCommGroup T] [Module k T]

/-- **No cyclotomic trivial quotient of the transverse adjoint module.** In the
prime-to-characteristic irreducible regime, no nontrivial trivial
representation can occur as an equivariant quotient of
`End(W) / k·Id`. This is the exact representation-theoretic contradiction
needed once a nonzero cyclotomic field intersection is converted into such a
quotient. -/
theorem no_surjective_trivial_quotient_of_transverse_adjoint
    [FiniteDimensional k W] [IsAlgClosed k] [Nontrivial T]
    (ρ : Representation k G W) [ρ.IsIrreducible]
    (hcard : (Fintype.card G : k) ≠ 0)
    (q : (Module.End k W ⧸ scalarLine (k := k) (W := W)) →ₗ[k] T)
    (hequiv : ∀ g x,
      q (((conjugationRepresentation ρ).quotient
        (scalarLine (k := k) (W := W)) (scalarLine_stable ρ)) g x) = q x) :
    ¬ Function.Surjective q := by
  apply not_surjective_equivariant_to_nontrivial_trivial
    ((conjugationRepresentation ρ).quotient
      (scalarLine (k := k) (W := W)) (scalarLine_stable ρ))
    q hequiv
  · exact quotient_by_scalars_has_no_invariants ρ hcard
  · exact hcard

end

end Komorebi.StrongArtin.ConjugationQuotientNoInvariants
