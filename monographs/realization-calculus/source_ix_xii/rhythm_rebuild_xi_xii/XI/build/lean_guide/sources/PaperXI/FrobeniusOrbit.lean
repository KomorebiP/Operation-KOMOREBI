import PaperXI.PacketTransport

/-! Frobenius orbits with integer powers, including both transport directions. -/
set_option autoImplicit false
namespace PaperXI.FrobeniusOrbit
variable {M : ℕ}

def Related (q : (ZMod M)ˣ) (j k : ZMod M) : Prop :=
  ∃ n : ℤ, ((q ^ n : (ZMod M)ˣ) : ZMod M) * j = k

theorem refl (q : (ZMod M)ˣ) (j : ZMod M) : Related q j j :=
  ⟨0, by simp⟩

theorem trans (q : (ZMod M)ˣ) {i j k : ZMod M}
    (hij : Related q i j) (hjk : Related q j k) : Related q i k := by
  obtain ⟨m, rfl⟩ := hij
  obtain ⟨n, rfl⟩ := hjk
  exact ⟨n + m, by simp [zpow_add, mul_assoc]⟩

theorem symm (q : (ZMod M)ˣ) {i j : ZMod M}
    (hij : Related q i j) : Related q j i := by
  obtain ⟨n, rfl⟩ := hij
  refine ⟨-n, ?_⟩
  simp [zpow_neg, ← mul_assoc]

theorem step (q : (ZMod M)ˣ) (j : ZMod M) : Related q j ((q : ZMod M) * j) :=
  ⟨1, by simp⟩

theorem back (q : (ZMod M)ˣ) (j : ZMod M) :
    Related q j (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) := ⟨-1, by simp⟩

theorem step_mem (q : (ZMod M)ˣ) {i j : ZMod M} (h : Related q i j) :
    Related q i ((q : ZMod M) * j) := trans q h (step q j)

theorem back_mem (q : (ZMod M)ˣ) {i j : ZMod M} (h : Related q i j) :
    Related q i (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) := trans q h (back q j)

theorem same_orbit_iff (q : (ZMod M)ˣ) {i j : ZMod M} (h : Related q i j)
    (k : ZMod M) : Related q i k ↔ Related q j k :=
  ⟨fun hk => trans q (symm q h) hk, fun hk => trans q h hk⟩

end PaperXI.FrobeniusOrbit
