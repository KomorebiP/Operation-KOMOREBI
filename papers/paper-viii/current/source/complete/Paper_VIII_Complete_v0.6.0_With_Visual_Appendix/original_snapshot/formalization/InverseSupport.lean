module
public import TransferSupport
import all TransferSupport
import all PacketIR
import all QuantumPacketCore
public import Mathlib.LinearAlgebra.FiniteDimensional.Basic
public import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
public import Mathlib.Tactic

/-!
Author: Komorebi P. Paper VIII item 6.7.
The inverse preserves the actual reachable packet subspace because its forward
restriction is injective and finite dimensional, hence surjective. Includes
zero-length paths. The result uses invertibility, not an assumed inverse sparsity.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators Classical
open KomorebiPaperVII
variable {K R I : Type*} [Field K] [Ring R] [Algebra K R]
variable [Fintype I] [DecidableEq I]
variable (P : PacketFamily R I)

def Reachable (A : R) (b a : I) : Prop := ∃ n, TransferPath P A n b a

theorem reachable_refl (A : R) (a : I) : Reachable P A a a := ⟨0,rfl⟩

theorem reachable_step (A : R) {b c a : I}
    (he : P.block A b c ≠ 0) (h : Reachable P A c a) : Reachable P A b a := by
  obtain ⟨n,hn⟩ := h
  exact ⟨n+1,c,he,hn⟩

/-- The subspace consisting of vectors with no unreachable packet component. -/
def reachableSpace (A : R) (a : I) : Submodule K R where
  carrier := {x | ∀ b, ¬ Reachable P A b a → P.proj b * x = 0}
  zero_mem' := by simp
  add_mem' := by
    intro x y hx hy b hb
    rw [mul_add,hx b hb,hy b hb,add_zero]
  smul_mem' := by
    intro c x hx b hb
    rw [mul_smul_comm,hx b hb,smul_zero]

theorem seed_mem_reachableSpace (A : R) (a : I) :
    P.proj a ∈ reachableSpace (K := K) P A a := by
  intro b hb
  have hba : b ≠ a := by
    intro he; subst b
    exact hb (reachable_refl P A a)
  rw [P.mul_proj]
  simp only [hba,ite_false]

theorem reachableSpace_invariant (A : R) (a : I) (x : R)
    (hx : x ∈ reachableSpace (K := K) P A a) :
    A*x ∈ reachableSpace (K := K) P A a := by
  intro b hb
  have he : P.proj b * (A*x) = ∑ c, P.block A b c * x := by
    simp only [PacketFamily.block,← Finset.sum_mul,← Finset.mul_sum]
    rw [P.sum_proj,mul_one,mul_assoc]
  rw [he]
  apply Finset.sum_eq_zero
  intro c _
  by_cases hc : P.block A b c = 0
  · rw [hc,zero_mul]
  · have hn : ¬ Reachable P A c a := fun hp => hb (reachable_step P A hc hp)
    change (P.proj b*A*P.proj c)*x = 0
    rw [mul_assoc, hx c hn,mul_zero]

variable [FiniteDimensional K R]

/-- Finite-dimensional injectivity makes the restriction onto its invariant range. -/
theorem invariant_space_inverse (A B : R) (hBA : B*A = 1) (W : Submodule K R)
    (hW : ∀ x ∈ W, A*x ∈ W) (x : R) (hx : x ∈ W) : B*x ∈ W := by
  let f : W →ₗ[K] W :=
    { toFun := fun y => ⟨A*y.val,hW y.val y.property⟩
      map_add' := by intro y z; apply Subtype.ext; exact mul_add A y.val z.val
      map_smul' := by intro c y; apply Subtype.ext; exact mul_smul_comm c A y.val }
  have hinj : Function.Injective f := by
    intro y z he
    have he' : A*y.val = A*z.val := congrArg Subtype.val he
    apply Subtype.ext
    have hh := congrArg (fun t => B*t) he'
    simpa only [← mul_assoc,hBA,one_mul] using hh
  obtain ⟨y,hy⟩ := LinearMap.surjective_of_injective hinj ⟨x,hx⟩
  have hy' : A*y.val = x := congrArg Subtype.val hy
  have hbx : B*x = y.val := by rw [←hy',←mul_assoc,hBA,one_mul]
  rw [hbx]
  exact y.property

include K

/-- No reachable path from a to b forces a zero block of the actual inverse. -/
theorem inverse_block_zero_of_no_path (A B : R) (hBA : B*A = 1) (b a : I)
    (h : ¬ Reachable P A b a) : P.block B b a = 0 := by
  have hm := invariant_space_inverse (K := K) A B hBA
    (reachableSpace (K := K) P A a) (reachableSpace_invariant P A a)
    (P.proj a) (seed_mem_reachableSpace P A a)
  have hz := hm b h
  simpa only [PacketFamily.block,mul_assoc] using hz

theorem inverse_support_inclusion (A B : R) (hBA : B*A = 1) (b a : I)
    (h : P.block B b a ≠ 0) : Reachable P A b a := by
  by_contra hn
  exact h (inverse_block_zero_of_no_path (K := K) P A B hBA b a hn)

/-- Unit notation specializes the theorem to a genuine algebraic inverse. -/
theorem unit_inverse_support (A : Rˣ) (b a : I)
    (h : P.block (↑(A⁻¹) : R) b a ≠ 0) : Reachable P (↑A : R) b a := by
  exact inverse_support_inclusion (K := K) P A ↑(A⁻¹) (by simp) b a h

section Matrix
variable {X : Type*} [Fintype X] [DecidableEq X]

/-- Matrix specialization uses Mathlib's actual nonsingular matrix inverse. -/
theorem matrix_inverse_support (Q : PacketFamily (Matrix X X K) I)
    (A : Matrix X X K) (hA : IsUnit A.det) (b a : I)
    (h : Q.block A⁻¹ b a ≠ 0) : Reachable Q A b a := by
  exact inverse_support_inclusion (K := K) Q A A⁻¹
    (Matrix.nonsing_inv_mul A hA) b a h
end Matrix
end KomorebiPaperVIII

-- FIFTH BLOCK AXIOM AUDIT
#print axioms KomorebiPaperVIII.reachable_refl
#print axioms KomorebiPaperVIII.reachable_step
#print axioms KomorebiPaperVIII.seed_mem_reachableSpace
#print axioms KomorebiPaperVIII.reachableSpace_invariant
#print axioms KomorebiPaperVIII.invariant_space_inverse
#print axioms KomorebiPaperVIII.inverse_block_zero_of_no_path
#print axioms KomorebiPaperVIII.inverse_support_inclusion
#print axioms KomorebiPaperVIII.unit_inverse_support
#print axioms KomorebiPaperVIII.matrix_inverse_support
#print axioms KomorebiPaperVIII.reachableSpace
