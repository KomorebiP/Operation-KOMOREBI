import PaperXI.TypeSideDescent
import PaperXI.CentralExtensionCocycle
import Mathlib.Algebra.Group.IsCommutative
import Mathlib.Algebra.Group.AddChar
import Mathlib.LinearAlgebra.BilinearMap

/-! The actual type-side central extension, its source commutator formula,
and scalar nondegeneracy transferred from a supplied source pairing. These
interfaces retain the simple-character facts as explicit inputs. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeSideExtension

open TypeSideDescent
open scoped IsMulCommutative

variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]

/-- The central quotient is abelian because its actual character is faithful. -/
instance centralQuotient_isMulCommutative (H : Subgroup G) (θ : H →* ℂˣ) :
    IsMulCommutative (H ⧸ θ.ker) :=
  ⟨⟨fun a b => (centralCharacter_injective H θ) (by simp [map_mul, mul_comm])⟩⟩

theorem finite_center (H : Subgroup G) (θ : H →* ℂˣ) [Finite θ.range] :
    Finite (H ⧸ θ.ker) := inferInstance

theorem centralCharacter_ne_one (H : Subgroup G) (θ : H →* ℂˣ) (hθ : θ ≠ 1) :
    centralCharacter H θ ≠ 1 := by
  intro heq
  apply hθ
  apply MonoidHom.ext
  intro h
  exact DFunLike.congr_fun heq (QuotientGroup.mk' θ.ker h)

/-- The exact extension formed from the actual source groups and character. -/
def datum (H : Subgroup G) [H.Normal] [IsMulCommutative (G ⧸ H)]
    (θ : H →* ℂˣ) (hθ : Invariant H θ) :
    CentralExtension.Datum (H ⧸ θ.ker) (G ⧸ characterKernel H θ hθ) (G ⧸ H) where
  i := centerInclusion H θ hθ
  q := quotientProjection H θ hθ
  i_injective := centerInclusion_injective H θ hθ
  q_surjective := quotientProjection_surjective H θ hθ
  range_i_eq_ker_q := exact_center_quotient H θ hθ
  central z h :=
    ((Subgroup.mem_center_iff.mp (centerInclusion_central H θ hθ ⟨z, rfl⟩)) h).symm

/-- Commutators lie in the actual normal subgroup because the quotient is abelian. -/
theorem commutator_mem (H : Subgroup G) [H.Normal] [IsMulCommutative (G ⧸ H)]
    (x y : G) : x * y * x⁻¹ * y⁻¹ ∈ H := by
  apply (QuotientGroup.eq_one_iff _).mp
  simp [QuotientGroup.mk_mul, mul_comm, mul_left_comm]

/-- The source scalar pairing on actual representatives, namely `θ([x,y])`. -/
def characterCommutator (H : Subgroup G) [H.Normal] [IsMulCommutative (G ⧸ H)]
    (θ : H →* ℂˣ) (x y : G) : ℂˣ :=
  θ ⟨x * y * x⁻¹ * y⁻¹, commutator_mem H x y⟩

/-- The constructed extension cocycle reproduces exactly the source scalar
commutator on every pair of actual group representatives. -/
theorem scalar_commutator_source (H : Subgroup G) [H.Normal]
    [IsMulCommutative (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ) (x y : G) :
    CocycleCommutator.commutator
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ))
      (QuotientGroup.mk' H x) (QuotientGroup.mk' H y) = characterCommutator H θ x y := by
  let D := datum H θ hθ
  let q := QuotientGroup.mk' (characterKernel H θ hθ)
  change CocycleCommutator.commutator (CentralExtension.scalarCocycle D (centralCharacter H θ))
    (D.q (q x)) (D.q (q y)) = _
  rw [CentralExtension.scalar_commutator]
  have hc : CentralExtension.centralCommutator D (q x) (q y) =
      QuotientGroup.mk' θ.ker ⟨x * y * x⁻¹ * y⁻¹, commutator_mem H x y⟩ := by
    apply D.i_injective
    rw [CentralExtension.i_centralCommutator]
    change q x * q y * (q x)⁻¹ * (q y)⁻¹ = q (x * y * x⁻¹ * y⁻¹)
    simp
  rw [hc]
  rfl

/-- A supplied scalar source pairing is the scalar commutator of the actual
constructed extension, not merely a pairing on an unrelated quotient. -/
theorem scalar_commutator_eq_pairing (H : Subgroup G) [H.Normal]
    [IsMulCommutative (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (b : (G ⧸ H) → (G ⧸ H) → ℂˣ)
    (hb : ∀ x y, b (QuotientGroup.mk' H x) (QuotientGroup.mk' H y) =
      characterCommutator H θ x y) (a d : G ⧸ H) :
    CocycleCommutator.commutator
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) a d = b a d := by
  obtain ⟨x, rfl⟩ := QuotientGroup.mk_surjective a
  obtain ⟨y, rfl⟩ := QuotientGroup.mk_surjective d
  exact (scalar_commutator_source H θ hθ x y).trans (hb x y).symm

/-- Source nondegeneracy is needed after applying the character. No assertion
that an arbitrary nontrivial central character is faithful is used here. -/
theorem nondegenerate_of_pairing (H : Subgroup G) [H.Normal]
    [IsMulCommutative (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (b : (G ⧸ H) → (G ⧸ H) → ℂˣ)
    (hb : ∀ x y, b (QuotientGroup.mk' H x) (QuotientGroup.mk' H y) =
      characterCommutator H θ x y)
    (hnd : ∀ a, (∀ d, b a d = 1) → a = 1) :
    CocycleCommutator.radical
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) = ⊥ := by
  apply le_antisymm ?_ bot_le
  intro a ha
  apply Subgroup.mem_bot.mpr
  apply hnd a
  intro d
  rw [← scalar_commutator_eq_pairing H θ hθ b hb]
  exact (CocycleCommutator.mem_radical_iff _ a).mp ha d

section BilinearSource

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- A nonzero functional is surjective, so composing a nondegenerate
bilinear pairing with a nontrivial additive character is still nondegenerate
as a scalar pairing. No faithfulness of the additive character is assumed. -/
theorem bilinear_character_nondegenerate
    (β : X →ₗ[K] X →ₗ[K] K)
    (hβ : ∀ x, (∀ y, β x y = 0) → x = 0)
    (ψ : AddChar K ℂˣ) (hψ : ψ ≠ 1) (x : X)
    (hx : ∀ y, ψ (β x y) = 1) : x = 0 := by
  apply hβ x
  intro y
  by_contra hxy
  have ht : ∃ t : K, ψ t ≠ 1 := by
    by_contra hn
    apply hψ
    apply AddChar.ext
    intro t
    exact not_not.mp (not_exists.mp hn t)
  obtain ⟨t, ht⟩ := ht
  have heq : β x ((t / β x y) • y) = t := by
    rw [map_smul, smul_eq_mul, div_mul_cancel₀ t hxy]
  exact ht (heq ▸ hx ((t / β x y) • y))

/-- The source vector-space pairing gives the actual extension's scalar
nondegeneracy through an explicit identification of the quotient group. -/
theorem nondegenerate_of_bilinear_pairing (H : Subgroup G) [H.Normal]
    [IsMulCommutative (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (e : (G ⧸ H) ≃* Multiplicative X) (β : X →ₗ[K] X →ₗ[K] K)
    (hβ : ∀ x, (∀ y, β x y = 0) → x = 0)
    (ψ : AddChar K ℂˣ) (hψ : ψ ≠ 1)
    (hsource : ∀ x y,
      ψ (β (e (QuotientGroup.mk' H x)).toAdd (e (QuotientGroup.mk' H y)).toAdd) =
        characterCommutator H θ x y) :
    CocycleCommutator.radical
      (CentralExtension.scalarCocycle (datum H θ hθ) (centralCharacter H θ)) = ⊥ := by
  apply nondegenerate_of_pairing H θ hθ
    (fun a d => ψ (β (e a).toAdd (e d).toAdd)) hsource
  intro a ha
  have hz : (e a).toAdd = 0 := by
    apply bilinear_character_nondegenerate β hβ ψ hψ
    intro y
    simpa using ha (e.symm (Multiplicative.ofAdd y))
  apply e.injective
  simpa using congrArg Multiplicative.ofAdd hz

end BilinearSource

/-- The supplied irreducible source action, descended through its proved
character kernel, has the required action of the constructed extension center. -/
theorem representation_central_action (H : Subgroup G) [H.Normal]
    [IsMulCommutative (G ⧸ H)] (θ : H →* ℂˣ) (hθ : Invariant H θ)
    (η : Representation ℂ G V) [Representation.IsIrreducible η]
    (hcontains : Contains H θ η) (z : H ⧸ θ.ker) :
    representation H θ hθ η hcontains ((datum H θ hθ).i z) =
      (centralCharacter H θ z : ℂ) • LinearMap.id :=
  central_action H θ hθ η hcontains z

end PaperXI.TypeSideExtension
