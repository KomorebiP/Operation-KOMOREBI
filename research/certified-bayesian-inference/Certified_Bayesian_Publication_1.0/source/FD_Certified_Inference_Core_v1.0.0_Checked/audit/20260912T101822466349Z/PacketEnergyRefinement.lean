import Komorebi.PacketVectorEnergy

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix SelfAdjointPackets

/-- Exact fiber refinement. Source and target packet maps may be different. -/
def PacketRefines {ι α γ : Type*} [Fintype ι] [Fintype γ] [DecidableEq α]
    (C : SelfAdjointPackets ι α) (E : SelfAdjointPackets ι γ) (ρ : γ → α) : Prop :=
  ∀ a, C.proj a = E.sumOn (Finset.univ.filter fun c => ρ c = a)

variable {ι κ α β γ δ : Type*} [Fintype ι] [Fintype κ] [Fintype γ] [Fintype δ]
variable [DecidableEq α] [DecidableEq β]

/-- Every parent block has exactly the energy of all its descendant blocks, locally.
No completeness of either coarse or fine family is required for this identity. -/
theorem parent_energy_eq_descendants
    (C : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (E : SelfAdjointPackets ι γ) (F : SelfAdjointPackets κ δ)
    (ρ : γ → α) (τ : δ → β) (hE : PacketRefines C E ρ) (hF : PacketRefines D F τ)
    (A : Matrix ι κ ℝ) (a : α) (b : β) :
    matrixEnergy (C.proj a * A * D.proj b) =
      ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ∑ d ∈ Finset.univ.filter (fun d => τ d = b),
          matrixEnergy (E.proj c * A * F.proj d) := by
  rw [hE a, hF b]
  exact matrixEnergy_sumOn_both E F _ _ A

/-- Zero parent energy is equivalent to every descendant block being the zero matrix. -/
theorem parent_energy_zero_iff_descendants_zero
    (C : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β)
    (E : SelfAdjointPackets ι γ) (F : SelfAdjointPackets κ δ)
    (ρ : γ → α) (τ : δ → β) (hE : PacketRefines C E ρ) (hF : PacketRefines D F τ)
    (A : Matrix ι κ ℝ) (a : α) (b : β) :
    matrixEnergy (C.proj a * A * D.proj b) = 0 ↔
      ∀ c d, ρ c = a → τ d = b → E.proj c * A * F.proj d = 0 := by
  rw [parent_energy_eq_descendants C D E F ρ τ hE hF A a b]
  rw [Finset.sum_eq_zero_iff_of_nonneg
    (fun c _ => Finset.sum_nonneg (fun d _ => matrixEnergy_nonneg _))]
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  constructor
  · intro h c d hc hd
    have hh := (Finset.sum_eq_zero_iff_of_nonneg
      (fun d _ => matrixEnergy_nonneg (E.proj c*A*F.proj d))).mp (h c hc)
    exact (matrixEnergy_eq_zero_iff _).mp (hh d (Finset.mem_filter.mpr ⟨Finset.mem_univ d, hd⟩))
  · intro h c hc
    apply Finset.sum_eq_zero
    intro d hd
    exact (matrixEnergy_eq_zero_iff _).mpr (h c d hc (Finset.mem_filter.mp hd).2)

end Komorebi.PacketEnergy
