import PaperXI.TypeNormalizerAction
import PaperXI.TypeSideExtension
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-! Character invariance yields preservation of the actual quotient pairing.
No form-preservation hypothesis is inserted into the normalizer theorem. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeNormalizerPairing
open TypeNormalizerAction TypeSideDescent TypeSideExtension
open scoped IsMulCommutative

variable {J : Type*} [Group J]

/-- Ambient conjugation restricted to the character subgroup. -/
def subgroupAut (N : Subgroup J) [N.Normal] (H : Subgroup N)
    (hH : Stable N H) (j : J) : MulAut H where
  toFun x := ⟨conjugation N j x, hH j x x.property⟩
  invFun x := ⟨conjugation N j⁻¹ x, hH j⁻¹ x x.property⟩
  left_inv x := by apply Subtype.ext; apply Subtype.ext; simp
  right_inv x := by apply Subtype.ext; apply Subtype.ext; simp
  map_mul' x y := by apply Subtype.ext; exact map_mul (conjugation N j) (x : N) (y : N)

/-- The source hypothesis that the ambient normalizer fixes the character. -/
def CharacterInvariant (N : Subgroup J) [N.Normal] (H : Subgroup N)
    (hH : Stable N H) (θ : H →* ℂˣ) : Prop :=
  ∀ j h, θ (subgroupAut N H hH j h) = θ h

/-- Ambient invariance includes the subgroup invariance required for the
actual central extension N/ker(theta). -/
theorem inertiaInvariant (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] (hH : Stable N H) (θ : H →* ℂˣ)
    (hθ : CharacterInvariant N H hH θ) : Invariant H θ := by
  intro n h
  have he : conjugate H n h = subgroupAut N H hH (n : J) h := by
    apply Subtype.ext
    exact (conjugation_inner N n h).symm
  rw [he]
  exact hθ (n : J) h

/-- The invariant is theta evaluated on the actual group commutator. -/
theorem characterCommutator_preserved (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (j : J) (x y : N) :
    characterCommutator H θ (conjugation N j x) (conjugation N j y) =
      characterCommutator H θ x y := by
  let h : H := ⟨x * y * x⁻¹ * y⁻¹, commutator_mem H x y⟩
  have he : (⟨conjugation N j x * conjugation N j y *
      (conjugation N j x)⁻¹ * (conjugation N j y)⁻¹,
      commutator_mem H (conjugation N j x) (conjugation N j y)⟩ : H) =
      subgroupAut N H hH j h := by
    apply Subtype.ext
    simp [subgroupAut, h]
  change θ _ = θ h
  rw [he]
  exact hθ j h

/-- The canonical scalar pairing on the actual quotient N/H. -/
def pairing (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H)
    (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ) :
    (N ⧸ H) → (N ⧸ H) → ℂˣ :=
  CocycleCommutator.commutator
    (CentralExtension.scalarCocycle (datum H θ (inertiaInvariant N H hH θ hθ))
      (centralCharacter H θ))

@[simp] theorem pairing_on_representatives (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ) (x y : N) :
    pairing N H hH θ hθ (QuotientGroup.mk' H x) (QuotientGroup.mk' H y) =
      characterCommutator H θ x y :=
  scalar_commutator_source H θ (inertiaInvariant N H hH θ hθ) x y

/-- The honest J/N action preserves the pairing, independently of projective lifts. -/
theorem quotientAction_preserves_pairing (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (j : J ⧸ N) (x y : N ⧸ H) :
    pairing N H hH θ hθ (quotientAction N H hH j x) (quotientAction N H hH j y) =
      pairing N H hH θ hθ x y := by
  obtain ⟨g,rfl⟩ := QuotientGroup.mk_surjective j
  obtain ⟨a,rfl⟩ := QuotientGroup.mk_surjective x
  obtain ⟨b,rfl⟩ := QuotientGroup.mk_surjective y
  change pairing N H hH θ hθ
    (QuotientGroup.mk' H (conjugation N g a))
    (QuotientGroup.mk' H (conjugation N g b)) =
    pairing N H hH θ hθ (QuotientGroup.mk' H a) (QuotientGroup.mk' H b)
  simp only [pairing_on_representatives]
  exact characterCommutator_preserved N H hH θ hθ g a b

theorem pairing_alternating (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ) (x : N ⧸ H) :
    pairing N H hH θ hθ x x = 1 := CocycleCommutator.commutator_self _ x

theorem pairing_mul_left (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (x y z : N ⧸ H) :
    pairing N H hH θ hθ (x*y) z =
      pairing N H hH θ hθ x z * pairing N H hH θ hθ y z :=
  CocycleCommutator.commutator_mul_left _ x y z

theorem pairing_mul_right (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (x y z : N ⧸ H) :
    pairing N H hH θ hθ x (y*z) =
      pairing N H hH θ hθ x y * pairing N H hH θ hθ x z :=
  CocycleCommutator.commutator_mul_right _ x y z

section FieldValued
variable {k X : Type*} [Field k] [AddCommGroup X] [Module k X]

/-- Equality after a nontrivial additive character determines a bilinear form.
The character need not be injective: varying a scalar recovers every field value. -/
theorem bilinear_character_separates (B C : X →ₗ[k] X →ₗ[k] k)
    (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (h : ∀ x y, ψ (B x y) = ψ (C x y)) : B = C := by
  ext x y
  by_contra hn
  have hd : B x y - C x y ≠ 0 := sub_ne_zero.mpr hn
  obtain ⟨t,ht⟩ : ∃ t : k, ψ t ≠ 1 := by
    by_contra hnone
    apply hψ
    apply AddChar.ext
    intro t
    exact not_not.mp (not_exists.mp hnone t)
  let a := t / (B x y - C x y)
  have hm : ψ (a * (B x y - C x y)) = 1 := by
    rw [mul_sub, AddChar.map_sub_eq_div]
    have hs := h (a • x) y
    simpa only [map_smul, LinearMap.smul_apply, smul_eq_mul] using
      (div_eq_one.mpr hs)
  have he : a * (B x y - C x y) = t := div_mul_cancel₀ t hd
  exact ht (he ▸ hm)

/-- Scalar-pairing preservation plus the declared residue-field linearity
recovers preservation of the actual field-valued form. -/
theorem fieldForm_preserved (B : X →ₗ[k] X →ₗ[k] k) (L : X ≃ₗ[k] X)
    (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (h : ∀ x y, ψ (B (L x) (L y)) = ψ (B x y)) (x y : X) :
    B (L x) (L y) = B x y := by
  let C : X →ₗ[k] X →ₗ[k] k :=
    { toFun x := (B (L x)).comp L.toLinearMap
      map_add' x y := by ext z; simp
      map_smul' a x := by ext z; simp }
  have he : C = B := bilinear_character_separates C B ψ hψ h
  exact LinearMap.congr_fun (LinearMap.congr_fun he x) y

end FieldValued
end PaperXI.TypeNormalizerPairing
