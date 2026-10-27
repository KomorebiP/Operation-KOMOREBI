import PaperXI.TameOrbitTransitivity

/-! Exact support, and constant packet dimension along the Frobenius orbit. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketSupport
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusOrbit
open PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

theorem nonzero_step_iff (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    packet ρ j ≠ ⊥ ↔ packet ρ ((q : ZMod M) * j) ≠ ⊥ := by
  rw [← Submodule.nontrivial_iff_ne_bot, ← Submodule.nontrivial_iff_ne_bot]
  exact (packetEquiv ρ F q h j).toEquiv.nontrivial_congr

theorem nonzero_back_iff (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    packet ρ j ≠ ⊥ ↔ packet ρ (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) ≠ ⊥ := by
  simpa only [← mul_assoc, Units.mul_inv, one_mul] using
    (nonzero_step_iff ρ F q h (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j)).symm

theorem nonzero_zpow_iff (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) (n : ℤ) :
    packet ρ j ≠ ⊥ ↔ packet ρ (((q ^ n : (ZMod M)ˣ) : ZMod M) * j) ≠ ⊥ := by
  induction n using Int.induction_on with
  | zero => simp
  | succ n ih =>
    simpa [zpow_add_one, mul_assoc, mul_left_comm] using
      ih.trans (nonzero_step_iff ρ F q h (((q ^ (n : ℤ) : (ZMod M)ˣ) : ZMod M) * j))
  | pred n ih =>
    simpa [zpow_sub_one, mul_assoc, mul_left_comm] using
      ih.trans (nonzero_back_iff ρ F q h (((q ^ (-(n : ℤ)) : (ZMod M)ˣ) : ZMod M) * j))

theorem finrank_zpow (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) (n : ℤ) :
    Module.finrank ℂ (packet ρ j) =
      Module.finrank ℂ (packet ρ (((q ^ n : (ZMod M)ˣ) : ZMod M) * j)) := by
  induction n using Int.induction_on with
  | zero => rw [zpow_zero, Units.val_one, one_mul]
  | succ n ih =>
    have hi : ((q ^ ((n : ℤ) + 1) : (ZMod M)ˣ) : ZMod M) * j =
        (q : ZMod M) * (((q ^ (n : ℤ) : (ZMod M)ˣ) : ZMod M) * j) := by
      simp [zpow_add_one, mul_assoc, mul_left_comm]
    rw [hi]
    exact ih.trans (packet_finrank_step ρ F q h _)
  | pred n ih =>
    have hb (k : ZMod M) : Module.finrank ℂ (packet ρ k) =
        Module.finrank ℂ (packet ρ (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * k)) := by
      have hi : (q : ZMod M) * (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * k) = k := by
        simp [← mul_assoc]
      have hs := packet_finrank_step ρ F q h (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * k)
      rw [hi] at hs
      exact hs.symm
    have hi : ((q ^ (-(n : ℤ) - 1) : (ZMod M)ˣ) : ZMod M) * j =
        ((q⁻¹ : (ZMod M)ˣ) : ZMod M) * (((q ^ (-(n : ℤ)) : (ZMod M)ˣ) : ZMod M) * j) := by
      simp [zpow_sub_one, mul_assoc, mul_left_comm]
    rw [hi]
    exact ih.trans (hb _)

variable {G : Type*} [Group G]

theorem support_iff_orbit (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥) (k : ZMod M) :
    packet (tameRestriction π ι) k ≠ ⊥ ↔ Related q j k := by
  constructor
  · exact nonzero_packets_one_orbit π ι φ q hgen hrel hj
  · rintro ⟨n, rfl⟩
    exact (nonzero_zpow_iff (tameRestriction π ι) (actionEquiv π φ) q
      (geometric_relation π ι φ q hrel) j n).mp hj

/-- Nonempty support is exactly one full orbit, including the converse direction. -/
theorem support_is_one_orbit (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M))) :
    ∃ j : ZMod M, packet (tameRestriction π ι) j ≠ ⊥ ∧
      ∀ k, packet (tameRestriction π ι) k ≠ ⊥ ↔ Related q j k := by
  obtain ⟨j, hj⟩ := exists_nonzero_packet π ι
  exact ⟨j, hj, support_iff_orbit π ι φ q hgen hrel hj⟩

theorem equal_packet_dimensions (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j k : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥)
    (hk : packet (tameRestriction π ι) k ≠ ⊥) :
    Module.finrank ℂ (packet (tameRestriction π ι) j) =
      Module.finrank ℂ (packet (tameRestriction π ι) k) := by
  obtain ⟨n, rfl⟩ := nonzero_packets_one_orbit π ι φ q hgen hrel hj hk
  exact finrank_zpow (tameRestriction π ι) (actionEquiv π φ) q
    (geometric_relation π ι φ q hrel) j n

end PaperXI.PacketSupport
