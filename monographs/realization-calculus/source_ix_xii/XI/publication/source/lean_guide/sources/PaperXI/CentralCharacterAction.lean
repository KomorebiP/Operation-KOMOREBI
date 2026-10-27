import PaperXI.CentralExtensionCocycle
import PaperXI.TwistedAction
import Mathlib.RepresentationTheory.Basic

/-! An actual representation with a prescribed central character yields an
actual action of its section's twisted group algebra. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralCharacter
open PaperXI.CentralExtension
variable {Z H A V W : Type*} [CommGroup Z] [Group H] [CommGroup A]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- Section operators preserve the normalized identity. -/
theorem section_operators_one (D : Datum Z H A) (σ : Representation ℂ H W) :
    σ (sectionMap D 1) = 1 := by
  rw [section_one, map_one]

/-- Section operators satisfy the actual scalar cocycle multiplication law. -/
theorem section_operators_mul (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) (a b : A) :
    σ (sectionMap D a) * σ (sectionMap D b) =
      ((scalarCocycle D ζ).coeff a b : ℂ) • σ (sectionMap D (a * b)) := by
  rw [← map_mul, section_mul, map_mul, hcentral]
  change ((ζ (defect D a b) : ℂ) • (1 : Module.End ℂ W)) *
      σ (sectionMap D (a * b)) =
    (ζ (defect D a b) : ℂ) • σ (sectionMap D (a * b))
  rw [smul_mul_assoc, one_mul]

/-- The twisted algebra attached to the actual extension and central character. -/
abbrev Algebra (D : Datum Z H A) (ζ : Z →* ℂˣ) :=
  TwistedAlgebra.Algebra (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)

variable [Fintype A]

/-- Its canonical basis is indexed by the actual quotient group. -/
abbrev basis (D : Datum Z H A) (ζ : Z →* ℂˣ) :=
  TwistedAlgebra.basis (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)

/-- Linear extension of the actual section operators to an algebra action. -/
def toAlgebraAction (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    Algebra D ζ →ₐ[ℂ] Module.End ℂ W :=
  TwistedAction.action (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)
    (fun a => σ (sectionMap D a)) (section_operators_one D σ)
    (section_operators_mul D ζ σ hcentral)

@[simp] theorem toAlgebraAction_basis (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) (a : A) :
    toAlgebraAction D ζ σ hcentral (basis D ζ a) = σ (sectionMap D a) :=
  TwistedAction.action_basis (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)
    (fun a => σ (sectionMap D a)) (section_operators_one D σ)
    (section_operators_mul D ζ σ hcentral) a

/-- The algebra action recovers every group operator by the actual normal form. -/
theorem action_normal_form (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) (h : H) :
    σ h = (ζ (coordinate D h) : ℂ) •
      toAlgebraAction D ζ σ hcentral (basis D ζ (D.q h)) := by
  rw [toAlgebraAction_basis]
  calc
    σ h = σ (D.i (coordinate D h) * sectionMap D (D.q h)) :=
      congrArg σ (normal_form D h)
    _ = (ζ (coordinate D h) : ℂ) • σ (sectionMap D (D.q h)) := by
      rw [map_mul, hcentral]
      change ((ζ (coordinate D h) : ℂ) • (1 : Module.End ℂ W)) *
          σ (sectionMap D (D.q h)) = _
      rw [smul_mul_assoc, one_mul]

/-- A complex subspace is stable under the algebra action exactly when it
is stable under the original group representation. -/
theorem action_stable_iff (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H W)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (S : Submodule ℂ W) :
    (∀ b : Algebra D ζ, ∀ w ∈ S, toAlgebraAction D ζ σ hcentral b w ∈ S) ↔
      ∀ h : H, ∀ w ∈ S, σ h w ∈ S := by
  constructor
  · intro hb h w hw
    rw [action_normal_form D ζ σ hcentral h, LinearMap.smul_apply]
    exact S.smul_mem _ (hb (basis D ζ (D.q h)) w hw)
  · intro hh b w hw
    rw [← (basis D ζ).sum_repr b, map_sum]
    simp only [map_smul, LinearMap.sum_apply, LinearMap.smul_apply, toAlgebraAction_basis]
    exact S.sum_mem (fun a _ => S.smul_mem _ (hh (sectionMap D a) w hw))

/-- Group intertwiners are exactly the complex-linear maps intertwining the
constructed algebra actions. -/
theorem action_intertwines_iff (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (σ : Representation ℂ H V) (τ : Representation ℂ H W)
    (hσ : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (hτ : ∀ z, τ (D.i z) = (ζ z : ℂ) • LinearMap.id)
    (F : V →ₗ[ℂ] W) :
    (∀ h v, F (σ h v) = τ h (F v)) ↔
      ∀ b : Algebra D ζ, ∀ v,
        F (toAlgebraAction D ζ σ hσ b v) = toAlgebraAction D ζ τ hτ b (F v) := by
  constructor
  · intro hF b v
    rw [← (basis D ζ).sum_repr b]
    simp only [map_sum, map_smul, LinearMap.sum_apply, LinearMap.smul_apply,
      toAlgebraAction_basis, hF]
  · intro hF h v
    rw [action_normal_form D ζ σ hσ h, action_normal_form D ζ τ hτ h]
    simp only [LinearMap.smul_apply, map_smul]
    rw [hF]

end PaperXI.CentralCharacter
