import PaperXI.PacketReturn
import Mathlib.RepresentationTheory.Invariants

/-! Actual inertia invariants of a cyclic packet, without irreducibility or
an assumption that its inertia labels are distinct. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InertiaFixed
open PaperXI.CyclicAction PaperXI.PacketTransport
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

theorem invariants_eq_packet_zero (ρ : Action (K := ℂ) (V := V) (M := M)) :
    ρ.invariants = packet ρ 0 := by
  ext v
  constructor
  · intro hv a
    simpa [operator] using hv (Multiplicative.ofAdd a)
  · intro hv a
    simpa [operator] using hv a.toAdd

omit [NeZero M] in
theorem orbit_label_eq_zero_iff (q : (ZMod M)ˣ) (j : ZMod M) (n : ℕ) :
    ((q ^ n : (ZMod M)ˣ) : ZMod M) * j = 0 ↔ j = 0 := by
  constructor
  · intro h
    have h' := congrArg (fun x : ZMod M => (((q ^ n)⁻¹ : (ZMod M)ˣ) : ZMod M) * x) h
    simpa only [← mul_assoc, Units.inv_mul, one_mul, mul_zero] using h'
  · rintro rfl
    simp

theorem invariants_eq_top_of_basis (ρ : Action (K := ℂ) (V := V) (M := M))
    {ι : Type*} (b : Module.Basis ι ℂ V) (hb : ∀ i, b i ∈ packet ρ 0) :
    ρ.invariants = ⊤ := by
  rw [invariants_eq_packet_zero]
  apply top_unique
  rw [← b.span_eq]
  exact Submodule.span_le.mpr (by rintro _ ⟨i, rfl⟩; exact hb i)

theorem invariants_eq_bot_of_basis (ρ : Action (K := ℂ) (V := V) (M := M))
    {ι : Type*} (b : Module.Basis ι ℂ V) (labels : ι → ZMod M)
    (hlabels : ∀ i, labels i ≠ 0) (hb : ∀ i, b i ∈ packet ρ (labels i)) :
    ρ.invariants = ⊥ := by
  have hp : projector ρ 0 = 0 := by
    apply b.ext
    intro i
    exact projector_on_other_packet ρ (Ne.symm (hlabels i)) (hb i)
  rw [invariants_eq_packet_zero]
  apply le_antisymm
  · intro v hv
    have he := (mem_iff_projector ρ 0 v).mp hv
    rw [hp] at he
    exact he.symm
  · exact bot_le

theorem fixed_forward (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {v : V} (hv : v ∈ ρ.invariants) : F v ∈ ρ.invariants := by
  rw [invariants_eq_packet_zero] at hv ⊢
  simpa using forward_mem ρ F q h 0 hv

theorem fixed_backward (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {v : V} (hv : v ∈ ρ.invariants) : F.symm v ∈ ρ.invariants := by
  rw [invariants_eq_packet_zero] at hv ⊢
  simpa using backward_mem ρ F q h 0 hv

theorem invariants_of_cycle_basis (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {n : ℕ} (b : Module.Basis (Fin n) ℂ V) (j : ZMod M) {v : V}
    (hv : v ∈ packet ρ j) (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v) :
    ρ.invariants = if j = 0 then ⊤ else ⊥ := by
  classical
  have hmem (i : Fin n) : b i ∈ packet ρ (((q ^ (i : ℕ) : (ZMod M)ˣ) : ZMod M) * j) := by
    rw [hb]
    exact PaperXI.PacketReturn.power_mem ρ F q h j i hv
  by_cases hj : j = 0
  · rw [ite_eq_left hj]
    apply invariants_eq_top_of_basis ρ b
    intro i
    simpa [hj] using hmem i
  · rw [ite_eq_right hj]
    apply invariants_eq_bot_of_basis ρ b _ _ hmem
    intro i hz
    exact hj ((orbit_label_eq_zero_iff q j i).mp hz)

end PaperXI.InertiaFixed
