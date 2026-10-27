import PaperXI.TypeNormalizerPairing
import PaperXI.SchurScalar
import PaperXI.CliffordDatum

/-! Implementation by an actual extension representation. Scalars compare
intertwiners for the same automorphism, not arbitrary quotient representatives.
The section defect is retained as an operator until scalarity is proved. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeProjectiveImplementation
open TypeNormalizerAction TypeNormalizerPairing TypeSideDescent TypeSideExtension
open scoped IsMulCommutative

variable {J V : Type*} [Group J] [AddCommGroup V] [Module ℂ V]

/-- The invertible linear operator supplied by an actual representation. -/
def operator (κ : Representation ℂ J V) (j : J) : V ≃ₗ[ℂ] V where
  toFun := κ j
  invFun := κ j⁻¹
  left_inv v := by
    change (κ j⁻¹ * κ j) v = v
    rw [← map_mul, inv_mul_cancel, map_one]
    rfl
  right_inv v := by
    change (κ j * κ j⁻¹) v = v
    rw [← map_mul, mul_inv_cancel, map_one]
    rfl
  map_add' := (κ j).map_add
  map_smul' := (κ j).map_smul

@[simp] theorem operator_apply (κ : Representation ℂ J V) (j : J) (v : V) :
    operator κ j v = κ j v := rfl

/-- Conjugation is implemented by the supplied extension, without an extra
intertwining assumption. -/
theorem implements_conjugation (N : Subgroup J) [N.Normal]
    (κ : Representation ℂ J V) (j : J) (n : N) (v : V) :
    operator κ j (κ (n : J) v) =
      κ (conjugation N j n : J) (operator κ j v) := by
  change (κ j * κ (n : J)) v = (κ (conjugation N j n : J) * κ j) v
  rw [← map_mul, ← map_mul]
  congr 2
  simp [mul_assoc]

section Schur
variable [FiniteDimensional ℂ V]

/-- Two implementers of the same ambient conjugation differ by a unique unit
scalar. The result is Schur's lemma for the actual irreducible N-action. -/
theorem implementer_unique (N : Subgroup J) [N.Normal]
    (κ : Representation ℂ J V) [Representation.IsIrreducible (κ.comp N.subtype)]
    (j : J) (T : V ≃ₗ[ℂ] V)
    (hT : ∀ (n : N) v, T (κ (n : J) v) = κ (conjugation N j n : J) (T v)) :
    ∃! c : ℂˣ, ∀ v, T v = (c : ℂ) • operator κ j v := by
  exact SchurScalar.bridge_unique (κ.comp N.subtype)
    ((κ.comp N.subtype).comp (conjugation N j).toMonoidHom)
    (operator κ j) T (implements_conjugation N κ j) hT

/-- Any two choices for the same automorphism have the same scalar ambiguity. -/
theorem two_implementers (N : Subgroup J) [N.Normal]
    (κ : Representation ℂ J V) [Representation.IsIrreducible (κ.comp N.subtype)]
    (j : J) (T U : V ≃ₗ[ℂ] V)
    (hT : ∀ (n : N) v, T (κ (n : J) v) = κ (conjugation N j n : J) (T v))
    (hU : ∀ (n : N) v, U (κ (n : J) v) = κ (conjugation N j n : J) (U v)) :
    ∃! c : ℂˣ, ∀ v, U v = (c : ℂ) • T v :=
  SchurScalar.bridge_unique (κ.comp N.subtype)
    ((κ.comp N.subtype).comp (conjugation N j).toMonoidHom) T U hT hU

end Schur

/-- The lift of a quotient representative has an operator-valued multiplication
defect. It is not automatically a scalar multiplier. -/
theorem section_operators_mul (N : Subgroup J) [N.Normal]
    (κ : Representation ℂ J V) (a b : J ⧸ N) :
    κ (CliffordDatum.sectionMap N a) * κ (CliffordDatum.sectionMap N b) =
      κ (CliffordDatum.defect N a b : J) * κ (CliffordDatum.sectionMap N (a*b)) := by
  rw [← map_mul, ← map_mul, CliffordDatum.section_mul]

/-- Changing a quotient representative multiplies the implementer by the
actual N-operator. This factor need not be scalar. -/
theorem representative_change (N : Subgroup J) (κ : Representation ℂ J V)
    (j : J) (n : N) : κ ((n : J)*j) = κ (n : J) * κ j := map_mul κ _ _

/-- Projective constancy on quotient fibers, expressed without choosing PGL
coordinates or a quotient section. -/
def ProjectiveDescends (N : Subgroup J) [N.Normal] (κ : Representation ℂ J V) : Prop :=
  ∀ j k, QuotientGroup.mk' N j = QuotientGroup.mk' N k →
    ∃ c : ℂˣ, κ j = (c : ℂ) • κ k

/-- Exact descent criterion: the subgroup being quotiented must act by scalars. -/
theorem projectiveDescends_iff (N : Subgroup J) [N.Normal] (κ : Representation ℂ J V) :
    ProjectiveDescends N κ ↔ ∀ n : N, ∃ c : ℂˣ, κ (n : J) = (c : ℂ) • LinearMap.id := by
  constructor
  · intro hd n
    obtain ⟨c,hc⟩ := hd n 1 (by simp)
    exact ⟨c, by simpa [Module.End.one_eq_id] using hc⟩
  · intro hs j k hjk
    have hm : j * k⁻¹ ∈ N := by
      apply (QuotientGroup.eq_one_iff _).mp
      change QuotientGroup.mk' N (j*k⁻¹) = 1
      rw [map_mul, map_inv, hjk, mul_inv_cancel]
    obtain ⟨c,hc⟩ := hs ⟨j*k⁻¹,hm⟩
    refine ⟨c, ?_⟩
    calc
      κ j = κ (j*k⁻¹) * κ k := by rw [← map_mul]; simp
      _ = (c : ℂ) • κ k := by
        rw [hc]
        ext v
        rfl

/-- An element represented by a scalar has trivial operator commutator with
all other elements. -/
theorem scalar_element_commutator (κ : Representation ℂ J V) (x y : J)
    (c : ℂ) (hx : κ x = c • LinearMap.id) :
    κ (x*y*x⁻¹*y⁻¹) = 1 := by
  have hcomm : κ x * κ y = κ y * κ x := by
    rw [hx]
    ext v
    exact ((κ y).map_smul c v).symm
  calc
    κ (x*y*x⁻¹*y⁻¹) = ((κ x * κ y) * κ x⁻¹) * κ y⁻¹ := by simp only [map_mul]
    _ = ((κ y * κ x) * κ x⁻¹) * κ y⁻¹ := by rw [hcomm]
    _ = 1 := by rw [mul_assoc (κ y) (κ x), ← map_mul, mul_inv_cancel, map_one,
                    mul_one, ← map_mul, mul_inv_cancel, map_one]

/-- The representation realizes exactly the character's commutator scalar. -/
theorem source_operator_commutator (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (κ : Representation ℂ J V) [Representation.IsIrreducible (κ.comp N.subtype)]
    (hcontains : Contains H θ (κ.comp N.subtype)) (x y : N) :
    κ ((x*y*x⁻¹*y⁻¹ : N) : J) = (characterCommutator H θ x y : ℂ) • LinearMap.id :=
  scalar_restriction H θ (inertiaInvariant N H hH θ hθ)
    (κ.comp N.subtype) hcontains ⟨x*y*x⁻¹*y⁻¹,commutator_mem H x y⟩

/-- A nontrivial Heisenberg commutator prevents the ambient implementers
from being projectively constant on J/N. -/
theorem nontrivial_pairing_obstructs_descent (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (κ : Representation ℂ J V) [Representation.IsIrreducible (κ.comp N.subtype)]
    (hcontains : Contains H θ (κ.comp N.subtype))
    (x y : N) (hxy : characterCommutator H θ x y ≠ 1) :
    ¬ ProjectiveDescends N κ := by
  intro hd
  obtain ⟨c,hc⟩ := (projectiveDescends_iff N κ).mp hd x
  have ht := source_operator_commutator N H hH θ hθ κ hcontains x y
  have hz := scalar_element_commutator κ (x : J) (y : J) (c : ℂ) hc
  have : Nontrivial V := GeneratedIrreducibility.nontrivial_space (κ.comp N.subtype)
  obtain ⟨v,hv⟩ := exists_ne (0 : V)
  apply hxy
  apply Units.ext
  have he : (characterCommutator H θ x y : ℂ) • v = (1 : ℂ) • v := by
    simpa using LinearMap.congr_fun (ht.symm.trans hz) v
  exact (smul_left_injective ℂ hv) he

end PaperXI.TypeProjectiveImplementation
