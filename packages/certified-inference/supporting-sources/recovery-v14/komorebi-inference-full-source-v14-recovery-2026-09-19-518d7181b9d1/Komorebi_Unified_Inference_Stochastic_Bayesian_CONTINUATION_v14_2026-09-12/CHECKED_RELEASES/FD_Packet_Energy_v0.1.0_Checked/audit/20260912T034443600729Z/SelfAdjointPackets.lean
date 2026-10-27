import Komorebi.PacketMatrixEnergy

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix

/-- Algebraically disjoint, self-adjoint idempotents on a real Euclidean coordinate space.
Completeness is a separate hypothesis so local parent identities do not assume global coverage. -/
structure SelfAdjointPackets (ι α : Type*) [Fintype ι] where
  proj : α → Matrix ι ι ℝ
  symmetric : ∀ a, (proj a).transpose = proj a
  idempotent : ∀ a, proj a * proj a = proj a
  disjoint : ∀ a b, a ≠ b → proj a * proj b = 0

namespace SelfAdjointPackets
variable {ι α : Type*} [Fintype ι]

def sumOn (E : SelfAdjointPackets ι α) (s : Finset α) : Matrix ι ι ℝ :=
  ∑ a ∈ s, E.proj a

@[simp] theorem sumOn_transpose (E : SelfAdjointPackets ι α) (s : Finset α) :
    (E.sumOn s).transpose = E.sumOn s := by
  simp [sumOn, Matrix.transpose_sum, E.symmetric]

theorem sumOn_mul_proj (E : SelfAdjointPackets ι α) (s : Finset α) (b : α) :
    E.sumOn s * E.proj b = if b ∈ s then E.proj b else 0 := by
  classical
  have hmul (a : α) : E.proj a * E.proj b = if a = b then E.proj b else 0 := by
    by_cases h : a = b
    · subst a
      simp [E.idempotent]
    · simp [h, E.disjoint a b h]
  simp only [sumOn, Finset.sum_mul, hmul]
  simp

theorem sumOn_idempotent (E : SelfAdjointPackets ι α) (s : Finset α) :
    E.sumOn s * E.sumOn s = E.sumOn s := by
  classical
  change E.sumOn s * (∑ a ∈ s, E.proj a) = ∑ a ∈ s, E.proj a
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro a ha
  rw [E.sumOn_mul_proj, if_pos ha]

theorem sumOn_mul_eq_zero (E : SelfAdjointPackets ι α) (s t : Finset α)
    (h : Disjoint s t) : E.sumOn s * E.sumOn t = 0 := by
  classical
  change E.sumOn s * (∑ b ∈ t, E.proj b) = 0
  rw [Finset.mul_sum]
  apply Finset.sum_eq_zero
  intro b hb
  rw [E.sumOn_mul_proj, if_neg]
  exact fun hs => Finset.disjoint_left.mp h hs hb

/-- A complete family covers the whole state space, rather than only a subspace. -/
def Complete [Fintype α] [DecidableEq ι] (E : SelfAdjointPackets ι α) : Prop :=
  E.sumOn Finset.univ = 1

end SelfAdjointPackets
end Komorebi.PacketEnergy
