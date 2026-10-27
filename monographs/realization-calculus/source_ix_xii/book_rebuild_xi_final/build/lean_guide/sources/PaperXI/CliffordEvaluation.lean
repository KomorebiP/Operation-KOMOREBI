import PaperXI.IsotypicEvaluation
import PaperXI.FiniteRepresentation
import PaperXI.CliffordMultiplicity
import Mathlib.RepresentationTheory.Maschke
import Mathlib.LinearAlgebra.TensorProduct.Map

set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordEvaluation

open scoped TensorProduct MonoidAlgebra
open Representation

variable {N W X : Type*} [Group N]
  [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
  (ρ : Representation ℂ N W) (σ : Representation ℂ N X)

/-- Evaluation on the actual multiplicity space of intertwining maps. -/
def map : W ⊗[ℂ] IntertwiningMap ρ σ →ₗ[ℂ] X :=
  TensorProduct.lift
    { toFun := fun w =>
        { toFun := fun f => f w
          map_add' := fun _ _ => rfl
          map_smul' := fun _ _ => rfl }
      map_add' := by intro w v; ext f; exact f.toLinearMap.map_add w v
      map_smul' := by intro c w; ext f; exact f.toLinearMap.map_smul c w }

@[simp] theorem map_tmul (w : W) (f : IntertwiningMap ρ σ) :
    map ρ σ (w ⊗ₜ[ℂ] f) = f w := rfl

/-- Evaluation intertwines the literal restricted group action. -/
theorem map_action (n : N) (t : W ⊗[ℂ] IntertwiningMap ρ σ) :
    map ρ σ (TensorProduct.map (ρ n) LinearMap.id t) = σ n (map ρ σ t) := by
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add u v hu hv => simp [hu, hv]
  | tmul w f => simpa using IntertwiningMap.isIntertwining ρ σ f n w

/-- Genuine module isotypy gives canonical evaluation bijectivity. -/
theorem bijective [Finite N] [IsIrreducible ρ] [FiniteDimensional ℂ X]
    (h : IsIsotypicOfType ℂ[N] σ.asModule ρ.asModule) :
    Function.Bijective (map ρ σ) := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : Module.Finite ℂ[N] σ.asModule :=
    Module.Finite.of_restrictScalars_finite ℂ ℂ[N] σ.asModule
  let E : W ⊗[ℂ] IntertwiningMap ρ σ ≃ₗ[ℂ] X :=
    ((TensorProduct.congr ρ.asModuleEquiv.symm (IntertwiningMap.equivLinearMapAsModule ρ σ)).trans
      (IsotypicEvaluation.equiv h)).trans σ.asModuleEquiv
  have hE : E.toLinearMap = map ρ σ := by
    ext w f
    rfl
  exact hE ▸ E.bijective

/-- The actual isotypic evaluation equivalence. -/
def equiv [Finite N] [IsIrreducible ρ] [FiniteDimensional ℂ X]
    (h : IsIsotypicOfType ℂ[N] σ.asModule ρ.asModule) :
    W ⊗[ℂ] IntertwiningMap ρ σ ≃ₗ[ℂ] X :=
  LinearEquiv.ofBijective (map ρ σ) (bijective ρ σ h)

@[simp] theorem equiv_tmul [Finite N] [IsIrreducible ρ] [FiniteDimensional ℂ X]
    (h : IsIsotypicOfType ℂ[N] σ.asModule ρ.asModule)
    (w : W) (f : IntertwiningMap ρ σ) : equiv ρ σ h (w ⊗ₜ[ℂ] f) = f w := rfl

theorem equiv_action [Finite N] [IsIrreducible ρ] [FiniteDimensional ℂ X]
    (h : IsIsotypicOfType ℂ[N] σ.asModule ρ.asModule)
    (n : N) (t : W ⊗[ℂ] IntertwiningMap ρ σ) :
    equiv ρ σ h (TensorProduct.map (ρ n) LinearMap.id t) = σ n (equiv ρ σ h t) :=
  map_action ρ σ n t

/-- Nonzero isotypic representations have nonzero actual multiplicity spaces. -/
theorem multiplicity_nontrivial [Finite N] [IsIrreducible ρ] [FiniteDimensional ℂ X]
    [Nontrivial X] (h : IsIsotypicOfType ℂ[N] σ.asModule ρ.asModule) :
    Nontrivial (IntertwiningMap ρ σ) := by
  by_contra hn
  let : Subsingleton (IntertwiningMap ρ σ) := not_nontrivial_iff_subsingleton.mp hn
  have : Subsingleton X := (equiv ρ σ h).symm.injective.subsingleton
  exact not_subsingleton X this

/-- Currying an equivariant tensor map produces an actual multiplicity endomorphism. -/
def choiceMap (E : W ⊗[ℂ] IntertwiningMap ρ σ →ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : IntertwiningMap ρ σ),
      E ((ρ n w) ⊗ₜ[ℂ] f) = σ n (E (w ⊗ₜ[ℂ] f))) :
    IntertwiningMap ρ σ →ₗ[ℂ] IntertwiningMap ρ σ where
  toFun f :=
    { toLinearMap := E.comp ((TensorProduct.mk ℂ W (IntertwiningMap ρ σ)).flip f)
      isIntertwining' n := by ext w; exact hE n w f }
  map_add' f g := by ext w; simp
  map_smul' c f := by ext w; simp

@[simp] theorem choiceMap_apply (E : W ⊗[ℂ] IntertwiningMap ρ σ →ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : IntertwiningMap ρ σ),
      E ((ρ n w) ⊗ₜ[ℂ] f) = σ n (E (w ⊗ₜ[ℂ] f)))
    (f : IntertwiningMap ρ σ) (w : W) : choiceMap ρ σ E hE f w = E (w ⊗ₜ[ℂ] f) := rfl

/-- An equivariant evaluation isomorphism induces an injective change on multiplicity. -/
theorem choiceMap_injective (E : W ⊗[ℂ] IntertwiningMap ρ σ ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : IntertwiningMap ρ σ),
      E ((ρ n w) ⊗ₜ[ℂ] f) = σ n (E (w ⊗ₜ[ℂ] f))) :
    Function.Injective (choiceMap ρ σ E.toLinearMap hE) := by
  intro f g hfg
  ext w
  have ht : E (w ⊗ₜ[ℂ] f) = E (w ⊗ₜ[ℂ] g) :=
    congrArg (fun q : IntertwiningMap ρ σ => q w) hfg
  exact congrArg (map ρ σ) (E.injective ht)

/-- The actual linear change of multiplicity induced by an arbitrary evaluation choice. -/
def choiceEquiv [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] IntertwiningMap ρ σ ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : IntertwiningMap ρ σ),
      E ((ρ n w) ⊗ₜ[ℂ] f) = σ n (E (w ⊗ₜ[ℂ] f))) :
    IntertwiningMap ρ σ ≃ₗ[ℂ] IntertwiningMap ρ σ :=
  LinearEquiv.ofBijective (choiceMap ρ σ E.toLinearMap hE)
    ⟨choiceMap_injective ρ σ E hE, LinearMap.injective_iff_surjective.mp
      (choiceMap_injective ρ σ E hE)⟩

@[simp] theorem choiceEquiv_apply [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] IntertwiningMap ρ σ ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : IntertwiningMap ρ σ),
      E ((ρ n w) ⊗ₜ[ℂ] f) = σ n (E (w ⊗ₜ[ℂ] f)))
    (f : IntertwiningMap ρ σ) (w : W) : choiceEquiv ρ σ E hE f w = E (w ⊗ₜ[ℂ] f) := rfl

/-- Every equivariant evaluation choice factors uniquely through a multiplicity automorphism. -/
theorem exists_unique_choice [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] IntertwiningMap ρ σ ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : IntertwiningMap ρ σ),
      E ((ρ n w) ⊗ₜ[ℂ] f) = σ n (E (w ⊗ₜ[ℂ] f))) :
    ∃! L : IntertwiningMap ρ σ ≃ₗ[ℂ] IntertwiningMap ρ σ,
      ∀ t : W ⊗[ℂ] IntertwiningMap ρ σ,
        E t = map ρ σ (TensorProduct.map LinearMap.id L.toLinearMap t) := by
  refine ⟨choiceEquiv ρ σ E hE, ?_, ?_⟩
  · intro t
    induction t using TensorProduct.induction_on with
    | zero => simp
    | add u v hu hv => simp [hu, hv]
    | tmul w f => rfl
  · intro L hL
    ext f w
    exact (hL (w ⊗ₜ[ℂ] f)).symm

section Operators
variable {G : Type*} [Group G] (N : Subgroup G) [N.Normal]
  (π : Representation ℂ G X) (ρ : Representation ℂ N W)
  (g : G) (I : Representation.Equiv ρ (CliffordDatum.conjugate N ρ g))

/-- The constructed multiplicity operator has the required literal tensor action. -/
theorem map_operator (t : W ⊗[ℂ] CliffordMultiplicity.Space N ρ π) :
    map ρ (CliffordDatum.restriction N π)
      (TensorProduct.map I.toLinearMap (CliffordMultiplicity.operator N ρ π g I).toLinearMap t) =
        π g (map ρ (CliffordDatum.restriction N π) t) := by
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add u v hu hv => simp [hu, hv]
  | tmul w f => simp [map_tmul, CliffordMultiplicity.operator_apply]

/-- Tensor evaluation determines the actual multiplicity operator uniquely. -/
theorem operator_unique (T : CliffordMultiplicity.Space N ρ π →ₗ[ℂ]
    CliffordMultiplicity.Space N ρ π)
    (hT : ∀ (w : W) (f : CliffordMultiplicity.Space N ρ π),
      map ρ (CliffordDatum.restriction N π) ((I w) ⊗ₜ[ℂ] T f) =
        π g (map ρ (CliffordDatum.restriction N π) (w ⊗ₜ[ℂ] f))) :
    T = (CliffordMultiplicity.operator N ρ π g I).toLinearMap := by
  ext f w
  simpa using hT (I.symm w) f

/-- Changing any equivariant isotypic evaluation conjugates the actual action on multiplicity. -/
theorem choice_operator_conjugation [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] CliffordMultiplicity.Space N ρ π ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : CliffordMultiplicity.Space N ρ π),
      E ((ρ n w) ⊗ₜ[ℂ] f) = π (n : G) (E (w ⊗ₜ[ℂ] f)))
    (T : CliffordMultiplicity.Space N ρ π →ₗ[ℂ] CliffordMultiplicity.Space N ρ π)
    (hT : ∀ (w : W) (f : CliffordMultiplicity.Space N ρ π),
      E ((I w) ⊗ₜ[ℂ] T f) = π g (E (w ⊗ₜ[ℂ] f)))
    (f : CliffordMultiplicity.Space N ρ π) :
    T f = (choiceEquiv ρ (CliffordDatum.restriction N π) E hE).symm
      (CliffordMultiplicity.operator N ρ π g I
        (choiceEquiv ρ (CliffordDatum.restriction N π) E hE f)) := by
  apply (choiceEquiv ρ (CliffordDatum.restriction N π) E hE).injective
  simp only [LinearEquiv.apply_symm_apply]
  ext w
  change E (w ⊗ₜ[ℂ] T f) = π g (E (I.symm w ⊗ₜ[ℂ] f))
  simpa using hT (I.symm w) f

/-- Construct the multiplicity operator for an arbitrary equivariant evaluation choice. -/
def choiceOperator [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] CliffordMultiplicity.Space N ρ π ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : CliffordMultiplicity.Space N ρ π),
      E ((ρ n w) ⊗ₜ[ℂ] f) = π (n : G) (E (w ⊗ₜ[ℂ] f))) :
    CliffordMultiplicity.Space N ρ π ≃ₗ[ℂ] CliffordMultiplicity.Space N ρ π :=
  ((choiceEquiv ρ (CliffordDatum.restriction N π) E hE).trans
    (CliffordMultiplicity.operator N ρ π g I)).trans
      (choiceEquiv ρ (CliffordDatum.restriction N π) E hE).symm

/-- The constructed operator satisfies the defining tensor identity for that evaluation. -/
theorem choiceOperator_tensor [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] CliffordMultiplicity.Space N ρ π ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : CliffordMultiplicity.Space N ρ π),
      E ((ρ n w) ⊗ₜ[ℂ] f) = π (n : G) (E (w ⊗ₜ[ℂ] f)))
    (w : W) (f : CliffordMultiplicity.Space N ρ π) :
    E ((I w) ⊗ₜ[ℂ] choiceOperator N π ρ g I E hE f) = π g (E (w ⊗ₜ[ℂ] f)) := by
  let L := choiceEquiv ρ (CliffordDatum.restriction N π) E hE
  change (L (L.symm (CliffordMultiplicity.operator N ρ π g I (L f)))) (I w) =
    π g ((L f) w)
  simp

/-- Every equivariant evaluation has a unique invertible multiplicity factor. -/
theorem exists_unique_choice_operator [FiniteDimensional ℂ W] [FiniteDimensional ℂ X]
    (E : W ⊗[ℂ] CliffordMultiplicity.Space N ρ π ≃ₗ[ℂ] X)
    (hE : ∀ (n : N) (w : W) (f : CliffordMultiplicity.Space N ρ π),
      E ((ρ n w) ⊗ₜ[ℂ] f) = π (n : G) (E (w ⊗ₜ[ℂ] f))) :
    ∃! T : CliffordMultiplicity.Space N ρ π ≃ₗ[ℂ] CliffordMultiplicity.Space N ρ π,
      ∀ (w : W) (f : CliffordMultiplicity.Space N ρ π),
        E ((I w) ⊗ₜ[ℂ] T f) = π g (E (w ⊗ₜ[ℂ] f)) := by
  refine ⟨choiceOperator N π ρ g I E hE, choiceOperator_tensor N π ρ g I E hE, ?_⟩
  intro T hT
  apply LinearEquiv.ext
  intro f
  exact choice_operator_conjugation N π ρ g I E hE T.toLinearMap hT f

end Operators

section Restriction
variable {G : Type*} [Group G] [Finite G] (N : Subgroup G)
  (π : Representation ℂ G X) (ρ : Representation ℂ N W)
  [IsIrreducible π] [IsIrreducible ρ]

/-- The finite Clifford datum supplies every hypothesis of canonical evaluation. -/
theorem restriction_bijective
    (h : IsIsotypicOfType ℂ[N] (Representation.asModule (π.comp N.subtype)) ρ.asModule) :
    Function.Bijective (map ρ (π.comp N.subtype)) := by
  let : FiniteDimensional ℂ X := FiniteRepresentation.finiteDimensional π
  exact bijective ρ (π.comp N.subtype) h

/-- The actual finite Clifford multiplicity space is nonzero. -/
theorem restriction_multiplicity_nontrivial
    (h : IsIsotypicOfType ℂ[N] (Representation.asModule (π.comp N.subtype)) ρ.asModule) :
    Nontrivial (IntertwiningMap ρ (π.comp N.subtype)) := by
  let : FiniteDimensional ℂ X := FiniteRepresentation.finiteDimensional π
  let : Nontrivial X := ((RepresentationStability.irreducible_iff π).mp inferInstance).1
  exact multiplicity_nontrivial ρ (π.comp N.subtype) h

end Restriction
end PaperXI.CliffordEvaluation
