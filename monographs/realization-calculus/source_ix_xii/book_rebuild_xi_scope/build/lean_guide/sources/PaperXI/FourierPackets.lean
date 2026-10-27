import PaperXI.FourierProjectors

/-! The ranges of the computed projectors are precisely the declared character
spaces. This identifies the algebraic operators with the paper's tame packets. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FourierPackets
open scoped BigOperators
open PaperXI.CyclicAction PaperXI.FourierProjectors
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {M : ℕ} [NeZero M]

def packet (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (j : ZMod M) : Submodule K V where
  carrier := {v | ∀ a, operator ρ a v = ψ (j * a) • v}
  zero_mem' := by simp
  add_mem' hx hy := by intro a; simp [hx a, hy a, smul_add]
  smul_mem' c x hx := by intro a; simp [hx a, smul_smul, mul_comm]

theorem projector_mem_packet (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (j : ZMod M) (v : V) :
    projector ρ ψ j v ∈ packet ρ ψ j := by
  intro a
  have h := LinearMap.congr_fun (action_projector ρ ψ j a) v
  simpa [Module.End.mul_apply] using h

theorem projector_on_packet (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hM : (M : K) ≠ 0)
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ ψ j) : projector ρ ψ j v = v := by
  change ∀ a, operator ρ a v = ψ (j * a) • v at hv
  rw [projector_formula, LinearMap.smul_apply, LinearMap.sum_apply]
  simp_rw [LinearMap.smul_apply, hv, smul_smul, ← AddChar.map_add_eq_mul]
  rw [← Finset.sum_smul]
  simp [neg_mul, smul_smul, hM]

theorem projector_range (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hM : (M : K) ≠ 0) (j : ZMod M) :
    LinearMap.range (projector ρ ψ j) = packet ρ ψ j := by
  ext v
  constructor
  · rintro ⟨w, rfl⟩; exact projector_mem_packet ρ ψ j w
  · intro hv; exact ⟨v, projector_on_packet ρ ψ hM j hv⟩

theorem vector_reconstruction (ρ : Action (K := K) (V := V) (M := M))
    (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive) (hM : (M : K) ≠ 0) (v : V) :
    (∑ j : ZMod M, projector ρ ψ j v) = v := by
  have h := LinearMap.congr_fun (projector_complete ρ ψ hψ hM) v
  simpa using h

end PaperXI.FourierPackets
