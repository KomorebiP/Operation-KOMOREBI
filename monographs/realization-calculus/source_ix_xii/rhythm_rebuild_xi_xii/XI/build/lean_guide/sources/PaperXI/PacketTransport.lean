import PaperXI.TameProjectors

/-! Actual Frobenius transport between the ranges of the computed projectors. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketTransport
open PaperXI.CyclicAction
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

abbrev packet (ρ : Action (K := ℂ) (V := V) (M := M)) (j : ZMod M) :=
  PaperXI.FourierPackets.packet ρ ZMod.stdAddChar j

abbrev projector (ρ : Action (K := ℂ) (V := V) (M := M)) (j : ZMod M) :=
  PaperXI.TameProjectors.projector ρ j

theorem mem_iff_projector (ρ : Action (K := ℂ) (V := V) (M := M))
    (j : ZMod M) (v : V) : v ∈ packet ρ j ↔ projector ρ j v = v := by
  constructor
  · exact PaperXI.FourierPackets.projector_on_packet ρ _ (NeZero.ne (M : ℂ)) j
  · intro h
    rw [← h]
    exact PaperXI.FourierPackets.projector_mem_packet ρ _ j v

theorem projector_on_other_packet (ρ : Action (K := ℂ) (V := V) (M := M))
    {i j : ZMod M} (hij : i ≠ j) {v : V} (hv : v ∈ packet ρ j) :
    projector ρ i v = 0 := by
  have hp := LinearMap.congr_fun (PaperXI.TameProjectors.orthogonal ρ hij) v
  change projector ρ i (projector ρ j v) = 0 at hp
  rwa [(mem_iff_projector ρ j v).mp hv] at hp

theorem inertia_mem (ρ : Action (K := ℂ) (V := V) (M := M))
    (a j : ZMod M) {v : V} (hv : v ∈ packet ρ j) : operator ρ a v ∈ packet ρ j := by
  change ∀ b, operator ρ b v = ZMod.stdAddChar (j * b) • v at hv
  rw [hv a]
  exact (packet ρ j).smul_mem _ (by exact hv)

theorem transport_of_conjugation (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) {i j : ZMod M}
    (h : F.conj (projector ρ i) = projector ρ j) {v : V} (hv : v ∈ packet ρ i) :
    F v ∈ packet ρ j := by
  apply (mem_iff_projector ρ j (F v)).mpr
  have hp := LinearMap.congr_fun h (F v)
  simpa [LinearEquiv.conj_apply_apply, (mem_iff_projector ρ i v).mp hv] using hp.symm

theorem forward_mem (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) :
    F v ∈ packet ρ ((q : ZMod M) * j) :=
  transport_of_conjugation ρ F (PaperXI.TameProjectors.geometric_covariance ρ F q h j) hv

theorem backward_mem (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) :
    F.symm v ∈ packet ρ (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) :=
  transport_of_conjugation ρ F.symm
    (PaperXI.TameProjectors.forward_generator_covariance ρ F.symm q h j) hv

/-- Frobenius is an actual linear equivalence between the two packet spaces. -/
def packetEquiv (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    packet ρ j ≃ₗ[ℂ] packet ρ ((q : ZMod M) * j) where
  toFun v := ⟨F v, forward_mem ρ F q h j v.property⟩
  invFun w := ⟨F.symm w, by
    simpa only [← mul_assoc, Units.inv_mul, one_mul] using
      backward_mem ρ F q h ((q : ZMod M) * j) w.property⟩
  left_inv v := by ext; simp
  right_inv w := by ext; simp
  map_add' v w := by ext; simp
  map_smul' c v := by ext; simp

theorem packet_finrank_step (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    Module.finrank ℂ (packet ρ j) = Module.finrank ℂ (packet ρ ((q : ZMod M) * j)) :=
  (packetEquiv ρ F q h j).finrank_eq

end PaperXI.PacketTransport
