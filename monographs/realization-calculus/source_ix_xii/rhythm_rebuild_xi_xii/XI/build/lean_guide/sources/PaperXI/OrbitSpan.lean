import PaperXI.FrobeniusOrbit

/-! The span of a Frobenius orbit of actual character spaces. Its stability and
separation from other packets are proved, not assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OrbitSpan
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusOrbit
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

def orbitSpan (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) (j : ZMod M) : Submodule ℂ V :=
  Submodule.span ℂ {v | ∃ k, Related q j k ∧ v ∈ packet ρ k}

theorem packet_le (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) {j k : ZMod M} (hk : Related q j k) :
    packet ρ k ≤ orbitSpan ρ q j := by
  intro v hv
  exact Submodule.subset_span ⟨k, hk, hv⟩

theorem self_packet_le (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) (j : ZMod M) : packet ρ j ≤ orbitSpan ρ q j :=
  packet_le ρ q (FrobeniusOrbit.refl q j)

theorem map_mem (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) (j : ZMod M) (A : Module.End ℂ V)
    (hA : ∀ k, Related q j k → ∀ v, v ∈ packet ρ k → A v ∈ orbitSpan ρ q j)
    {v : V} (hv : v ∈ orbitSpan ρ q j) : A v ∈ orbitSpan ρ q j := by
  induction hv using Submodule.span_induction with
  | mem v hv => obtain ⟨k, hk, hvk⟩ := hv; exact hA k hk v hvk
  | zero => simp
  | add x y _ _ hx hy => simpa using (orbitSpan ρ q j).add_mem hx hy
  | smul c x _ hx => simpa using (orbitSpan ρ q j).smul_mem c hx

theorem inertia_stable (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) (j a : ZMod M) {v : V} (hv : v ∈ orbitSpan ρ q j) :
    operator ρ a v ∈ orbitSpan ρ q j :=
  map_mem ρ q j (operator ρ a)
    (fun k hk _ hvk => packet_le ρ q hk (inertia_mem ρ a k hvk)) hv

theorem forward_stable (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ orbitSpan ρ q j) : F v ∈ orbitSpan ρ q j :=
  map_mem ρ q j F.toLinearMap
    (fun k hk _ hvk => packet_le ρ q (step_mem q hk) (forward_mem ρ F q h k hvk)) hv

theorem backward_stable (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ orbitSpan ρ q j) : F.symm v ∈ orbitSpan ρ q j :=
  map_mem ρ q j F.symm.toLinearMap
    (fun k hk _ hvk => packet_le ρ q (back_mem q hk) (backward_mem ρ F q h k hvk)) hv

theorem outside_projector_zero (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) {j k : ZMod M} (hk : ¬Related q j k)
    {v : V} (hv : v ∈ orbitSpan ρ q j) : projector ρ k v = 0 := by
  have hle : orbitSpan ρ q j ≤ LinearMap.ker (projector ρ k) := by
    apply Submodule.span_le.mpr
    rintro w ⟨i, hi, hwi⟩
    have hki : k ≠ i := by rintro rfl; exact hk hi
    exact projector_on_other_packet ρ hki hwi
  exact hle hv

theorem span_ne_bot (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) {j : ZMod M} (hj : packet ρ j ≠ ⊥) : orbitSpan ρ q j ≠ ⊥ := by
  intro h
  exact hj (eq_bot_iff.mpr (h ▸ self_packet_le ρ q j))

theorem outside_packet_eq_bot (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) {j k : ZMod M} (hk : ¬Related q j k)
    (htop : orbitSpan ρ q j = ⊤) : packet ρ k = ⊥ := by
  apply eq_bot_iff.mpr
  intro v hv
  have hz := outside_projector_zero ρ q hk (v := v) (by simp [htop])
  rw [(mem_iff_projector ρ k v).mp hv] at hz
  simpa using hz

theorem related_of_span_top (ρ : Action (K := ℂ) (V := V) (M := M))
    (q : (ZMod M)ˣ) {j k : ZMod M} (htop : orbitSpan ρ q j = ⊤)
    (hk : packet ρ k ≠ ⊥) : Related q j k := by
  by_contra hn
  exact hk (outside_packet_eq_bot ρ q hn htop)

end PaperXI.OrbitSpan
