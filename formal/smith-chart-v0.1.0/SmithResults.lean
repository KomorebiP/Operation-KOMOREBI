import SmithPackets
import SmithGeometry

/-! Explicit domain and nonpassivity consequences for the displayed packets. -/

namespace SmithChart

theorem zero_packet_positive_real {t : ℂ} (ht : ‖t‖ < 1) {N : ℕ} (hN : 0 < N) :
    0 < (impedancePacket N 0 t).re := by
  rw [packet_zero ht hN]
  exact SmithGeometry.impedance_positive_real (norm_pow_lt_one ht hN)

/-- The first nonconstant packet is not, by itself, a passive impedance. -/
theorem nonzero_packet_not_always_passive :
    ∃ t : ℂ, ‖t‖ < 1 ∧ (impedancePacket 2 1 t).re < 0 := by
  have ht : ‖(-1 / 2 : ℂ)‖ < 1 := by norm_num
  refine ⟨-1 / 2, ht, ?_⟩
  rw [packet_nonzero ht (by decide) (by decide)]
  norm_num [Complex.div_re, Complex.normSq_apply]

end SmithChart
