import Komorebi.PacketEnergyRefinement

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix SelfAdjointPackets

namespace SelfAdjointPackets
variable {ι α γ : Type*} [Fintype ι] [Fintype γ] [DecidableEq α]

/-- Grouping arbitrary disjoint fine packets produces genuine self-adjoint coarse packets. -/
def coarsen (E : SelfAdjointPackets ι γ) (ρ : γ → α) : SelfAdjointPackets ι α where
  proj a := E.sumOn (Finset.univ.filter fun c => ρ c = a)
  symmetric a := E.sumOn_transpose _
  idempotent a := E.sumOn_idempotent _
  disjoint a b hab := by
    apply E.sumOn_mul_eq_zero
    apply Finset.disjoint_left.mpr
    intro c hc hd
    exact hab ((Finset.mem_filter.mp hc).2.symm.trans (Finset.mem_filter.mp hd).2)

theorem coarsen_refines (E : SelfAdjointPackets ι γ) (ρ : γ → α) :
    PacketRefines (E.coarsen ρ) E ρ := by
  intro a
  rfl

theorem coarsen_sum [Fintype α] (E : SelfAdjointPackets ι γ) (ρ : γ → α) :
    (E.coarsen ρ).sumOn Finset.univ = E.sumOn Finset.univ := by
  change (∑ a, ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), E.proj c) = ∑ c, E.proj c
  simpa using Finset.sum_fiberwise_eq_sum_filter
    (Finset.univ : Finset γ) (Finset.univ : Finset α) ρ E.proj

theorem coarsen_complete [Fintype α] [DecidableEq ι]
    (E : SelfAdjointPackets ι γ) (ρ : γ → α) (hE : E.Complete) :
    (E.coarsen ρ).Complete := by
  unfold Complete
  rw [E.coarsen_sum]
  exact hE

end SelfAdjointPackets

/-- The mean-vector contribution obeys the same exact local hierarchy law. -/
theorem parent_vectorEnergy_eq_descendants {ι α γ : Type*}
    [Fintype ι] [Fintype γ] [DecidableEq α]
    (C : SelfAdjointPackets ι α) (E : SelfAdjointPackets ι γ) (ρ : γ → α)
    (hE : PacketRefines C E ρ) (v : ι → ℝ) (a : α) :
    vectorEnergy (C.proj a *ᵥ v) =
      ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), vectorEnergy (E.proj c *ᵥ v) := by
  rw [hE a]
  exact vectorEnergy_sumOn E _ v

end Komorebi.PacketEnergy
