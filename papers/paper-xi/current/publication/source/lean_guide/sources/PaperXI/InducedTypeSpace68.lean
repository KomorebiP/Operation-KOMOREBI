import PaperXI.InductionIrreducibility
import Mathlib.Algebra.Algebra.Equiv

/-!
# The canonical inducing-type subspace of actual induction

The full off-H Mackey condition gives factorization of every H-map through the
literal identity-coset inclusion.  No topological or semisimplicity hypothesis
is needed for this factorization.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InducedTypeSpace68

open Representation PaperXI.InductionIrreducibility

variable {k G V : Type*} [Field k] [Group G] [AddCommGroup V] [Module k V]
variable (H : Subgroup G) (σ : Representation k H V)

/-- Every type map factors through its identity coefficient. -/
theorem factorization
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0)
    (f : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype)) :
    f = (identityInclusion H σ).comp ((identityEvaluation H σ).comp f) := by
  apply sub_eq_zero.mp
  apply intertwiner_eq_zero_of_mackey H σ hM
  intro v
  change identityEvaluation H σ
    (f v - identityInclusion H σ (identityEvaluation H σ (f v))) = 0
  rw [map_sub, identityEvaluation_inclusion, sub_self]

/-- The pointwise form is useful when comparing actual type images. -/
theorem factorization_apply
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0)
    (f : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype)) (v : V) :
    f v = identityInclusion H σ (identityEvaluation H σ (f v)) :=
  congrArg (fun t => t v) (factorization H σ hM f)

/-- Evaluation and identity-coset inclusion identify the actual Hom space with
the endomorphism space of the inducing representation. -/
def homEquiv
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0) :
    IntertwiningMap σ ((ind H.subtype σ).comp H.subtype) ≃ₗ[k]
      IntertwiningMap σ σ where
  toFun f := (identityEvaluation H σ).comp f
  invFun b := (identityInclusion H σ).comp b
  left_inv f := (factorization H σ hM f).symm
  right_inv b := by ext v; simp
  map_add' f g := by ext v; simp
  map_smul' c f := by ext v; simp

/-- Every nonzero type map has exactly the same image as the identity copy.
Irreducibility suffices, without any scalar-endomorphism assumption. -/
theorem range_eq_identity [IsIrreducible σ]
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0)
    (f : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype)) (hf : f ≠ 0) :
    LinearMap.range f.toLinearMap = LinearMap.range (identityInclusion H σ).toLinearMap := by
  have hb : (identityEvaluation H σ).comp f ≠ 0 := by
    intro hz
    apply hf
    rw [factorization H σ hM f, hz]
    ext v
    simp
  have hsurj := (IsIrreducible.surjective_or_eq_zero
    ((identityEvaluation H σ).comp f)).resolve_right hb
  ext w
  constructor
  · rintro ⟨v, rfl⟩
    exact ⟨identityEvaluation H σ (f v), (factorization_apply H σ hM f v).symm⟩
  · rintro ⟨v, rfl⟩
    obtain ⟨u, hu⟩ := hsurj v
    exact ⟨u, (factorization_apply H σ hM f u).trans
      (congrArg (identityInclusion H σ) hu)⟩

/-- The distinguished type space is a literal submodule of the infinite
induced carrier, not an identification of that carrier with a finite diagram. -/
def typeSpace : Submodule k (IndV H.subtype σ) :=
  LinearMap.range (identityInclusion H σ).toLinearMap

/-- The actual inducing representation is linearly equivalent to its image. -/
def typeEquiv : V ≃ₗ[k] typeSpace H σ :=
  LinearEquiv.ofInjective (identityInclusion H σ).toLinearMap (by
    intro v w h
    simpa using congrArg (identityEvaluation H σ) h)

/-- Conjugation transports all operators faithfully into the canonical type
space. It preserves the full algebra, not merely its scalar invariants. -/
def typeOperators : Module.End k V ≃ₐ[k] Module.End k (typeSpace H σ) :=
  (typeEquiv H σ).conjAlgEquiv k

@[simp] theorem typeOperators_mul (A B : Module.End k V) :
    typeOperators H σ (A * B) = typeOperators H σ A * typeOperators H σ B :=
  map_mul (typeOperators H σ) A B

@[simp] theorem typeOperators_add (A B : Module.End k V) :
    typeOperators H σ (A + B) = typeOperators H σ A + typeOperators H σ B :=
  map_add (typeOperators H σ) A B

@[simp] theorem typeOperators_eq_zero_iff (A : Module.End k V) :
    typeOperators H σ A = 0 ↔ A = 0 :=
  (typeOperators H σ).map_eq_zero_iff

/-- In particular, projector idempotence is preserved and reflected. -/
theorem typeOperators_idempotent_iff (A : Module.End k V) :
    typeOperators H σ A * typeOperators H σ A = typeOperators H σ A ↔ A * A = A := by
  rw [← map_mul]
  exact (typeOperators H σ).injective.eq_iff

/-- Over an algebraically closed field, every type map is a scalar multiple
of the canonical inclusion. -/
theorem type_map_scalar [FiniteDimensional k V] [IsAlgClosed k] [IsIrreducible σ]
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0)
    (f : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype)) :
    ∃ c : k, f = c • identityInclusion H σ := by
  obtain ⟨c, hc⟩ := IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
    (ρ := σ) |>.surjective ((identityEvaluation H σ).comp f)
  refine ⟨c, ?_⟩
  rw [factorization H σ hM f, ← hc]
  ext v
  simp

/-- Conjugating an operator is unchanged when the identifying equivalence is
rescaled. This is the operator-level consequence of scalar uniqueness. -/
theorem conjugation_eq_of_scalar {W : Type*} [AddCommGroup W] [Module k W]
    (e₁ e₂ : V ≃ₗ[k] W) (c : k) (h : ∀ v, e₂ v = c • e₁ v)
    (A : Module.End k V) : e₂.conjAlgEquiv k A = e₁.conjAlgEquiv k A := by
  ext w
  obtain ⟨v, rfl⟩ := e₂.surjective w
  change e₂ (A (e₂.symm (e₂ v))) = e₁ (A (e₁.symm (e₂ v)))
  rw [e₂.symm_apply_apply, h v, map_smul, e₁.symm_apply_apply, map_smul, map_smul, h]

end PaperXI.InducedTypeSpace68
