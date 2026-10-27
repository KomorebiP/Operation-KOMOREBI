import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Algebra.Group.IsCommutative
import Mathlib.Tactic.Group

/-! The actual ambient conjugation action on N/H and its descent to J/N.
The quotient action is constructed from groups, not from choices of operators. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeNormalizerAction
open scoped IsMulCommutative

variable {J : Type*} [Group J]

/-- Restriction of ambient conjugation to the actual normal subgroup. -/
def conjugation (N : Subgroup J) [N.Normal] : J →* MulAut N where
  toFun j :=
    { toFun x := ⟨j * (x : J) * j⁻¹, Subgroup.Normal.conj_mem (inferInstance : N.Normal) x x.property j⟩
      invFun x := ⟨j⁻¹ * (x : J) * (j⁻¹)⁻¹, Subgroup.Normal.conj_mem (inferInstance : N.Normal) x x.property j⁻¹⟩
      left_inv x := by apply Subtype.ext; simp [mul_assoc]
      right_inv x := by apply Subtype.ext; simp [mul_assoc]
      map_mul' x y := by apply Subtype.ext; simp [mul_assoc] }
  map_one' := by ext x; simp
  map_mul' j k := by ext x; simp [mul_assoc]

@[simp] theorem conjugation_coe (N : Subgroup J) [N.Normal] (j : J) (x : N) :
    ((conjugation N j x : N) : J) = j * (x : J) * j⁻¹ := rfl

@[simp] theorem conjugation_inner (N : Subgroup J) [N.Normal] (n x : N) :
    conjugation N (n : J) x = n * x * n⁻¹ := by
  apply Subtype.ext
  rfl

/-- Stability under all ambient conjugations, including their inverses. -/
def Stable (N : Subgroup J) [N.Normal] (H : Subgroup N) : Prop :=
  ∀ j x, x ∈ H → conjugation N j x ∈ H

theorem stable_map (N : Subgroup J) [N.Normal] (H : Subgroup N)
    (hH : Stable N H) (j : J) : H.map (conjugation N j).toMonoidHom = H := by
  apply le_antisymm
  · rintro x ⟨y, hy, rfl⟩
    exact hH j y hy
  · intro x hx
    refine ⟨conjugation N j⁻¹ x, hH j⁻¹ x hx, ?_⟩
    apply Subtype.ext
    simp

/-- The induced action before quotienting the normalizing group. -/
def action (N : Subgroup J) [N.Normal] (H : Subgroup N) [H.Normal]
    (hH : Stable N H) : J →* MulAut (N ⧸ H) where
  toFun j := QuotientGroup.congr H H (conjugation N j) (stable_map N H hH j)
  map_one' := by
    ext x
    induction x using QuotientGroup.induction_on with | H n =>
      change QuotientGroup.mk (conjugation N 1 n) = QuotientGroup.mk n
      rw [map_one]
      rfl
  map_mul' j k := by
    ext x
    induction x using QuotientGroup.induction_on with | H n =>
      change QuotientGroup.mk (conjugation N (j*k) n) =
        QuotientGroup.mk (conjugation N j (conjugation N k n))
      rw [map_mul]
      rfl

@[simp] theorem action_mk (N : Subgroup J) [N.Normal] (H : Subgroup N) [H.Normal]
    (hH : Stable N H) (j : J) (x : N) :
    action N H hH j (QuotientGroup.mk' H x) =
      QuotientGroup.mk' H (conjugation N j x) := rfl

/-- N acts trivially on its abelian quotient, so no operator lift is needed
for the honest J/N action. -/
theorem subgroup_le_kernel (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H) :
    N ≤ (action N H hH).ker := by
  intro n hn
  change action N H hH n = 1
  ext x
  induction x using QuotientGroup.induction_on with | H t =>
    change QuotientGroup.mk' H (conjugation N n t) = QuotientGroup.mk' H t
    have h : n = ((⟨n,hn⟩ : N) : J) := rfl
    rw [h, conjugation_inner]
    simp [mul_comm]

/-- The honest quotient action on the actual symplectic quotient. -/
def quotientAction (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H) :
    (J ⧸ N) →* MulAut (N ⧸ H) :=
  QuotientGroup.lift N (action N H hH) (subgroup_le_kernel N H hH)

@[simp] theorem quotientAction_mk (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H) (j : J) (x : N) :
    quotientAction N H hH (QuotientGroup.mk' N j) (QuotientGroup.mk' H x) =
      QuotientGroup.mk' H (conjugation N j x) := rfl

/-- The representative formula uniquely specifies the action. -/
theorem quotientAction_unique (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H)
    (a : (J ⧸ N) →* MulAut (N ⧸ H))
    (ha : ∀ j x, a (QuotientGroup.mk' N j) (QuotientGroup.mk' H x) =
      QuotientGroup.mk' H (conjugation N j x)) : a = quotientAction N H hH := by
  apply MonoidHom.ext
  intro j
  obtain ⟨g,rfl⟩ := QuotientGroup.mk_surjective j
  ext x
  obtain ⟨n,rfl⟩ := QuotientGroup.mk_surjective x
  exact ha g n

end PaperXI.TypeNormalizerAction
