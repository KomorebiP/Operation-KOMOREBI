module

public import CongruentialEuler
public import Mathlib.RingTheory.PowerSeries.Expand

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.ExponentialSection

open PowerSeries Congruential

/-- The original source section, with its literal residue-selector coefficients. -/
def originalSection (N j : ℕ) : PowerSeries ℚ :=
  PowerSeries.mk (fun d => if d % N = j then 1 / (d.factorial : ℚ) else 0)

def expandedSource (N : ℕ) (hN : N ≠ 0) (j : ℕ) : PowerSeries ℚ :=
  C (1 / (j.factorial : ℚ)) * (X^j * expand N hN (sectionKernel N j))

def expandedPacket (N : ℕ) (hN : N ≠ 0) (j : ℕ) : PowerSeries ℚ :=
  expand N hN (packetSeries N j)

theorem source_coefficient_at_address (N : ℕ) (hN : N ≠ 0) (j n : ℕ) :
    PowerSeries.coeff (N*n+j) (expandedSource N hN j) = 1 / ((N*n+j).factorial : ℚ) := by
  simp only [expandedSource, coeff_C_mul, coeff_X_pow_mul, coeff_expand_mul,
    sectionKernel, coeff_mk]
  have hf : (j.factorial : ℚ) ≠ 0 := by positivity
  field_simp

theorem source_coefficient_off_address (N : ℕ) (hN : N ≠ 0) (j d : ℕ)
    (hj : j < N) (hd : d % N ≠ j) :
    PowerSeries.coeff d (expandedSource N hN j) = 0 := by
  simp only [expandedSource, coeff_C_mul, coeff_X_pow_mul']
  by_cases hle : j ≤ d
  · rw [ite_eq_left hle]
    have hdiv : ¬ N ∣ d-j := by
      intro h
      obtain ⟨q,hq⟩ := h
      have hdq : d=N*q+j := by omega
      apply hd
      rw [hdq]
      simp [Nat.add_mod, Nat.mod_eq_of_lt hj]
    rw [coeff_expand_of_not_dvd N hN _ hdiv, mul_zero]
  · rw [ite_eq_right hle, mul_zero]

theorem original_section_factorization (N : ℕ) (hN : N ≠ 0) (j : ℕ) (hj : j < N) :
    originalSection N j = expandedSource N hN j := by
  ext d
  simp only [originalSection, coeff_mk]
  by_cases hd : d % N = j
  · rw [ite_eq_left hd]
    have he := Nat.mod_add_div d N
    have hdq : d=N*(d/N)+j := by omega
    rw [hdq]
    exact (source_coefficient_at_address N hN j (d/N)).symm
  · rw [ite_eq_right hd]
    exact (source_coefficient_off_address N hN j d hj hd).symm

/-- Actual generating-function product in t, not merely a formal row recurrence. -/
theorem original_section_inverse_identity (N : ℕ) (hN : N ≠ 0) (j : ℕ) (hj : j < N) :
    expandedPacket N hN j * originalSection N j = C (1/(j.factorial : ℚ)) * X^j := by
  rw [original_section_factorization N hN j hj]
  have hi := congrArg (expand N hN) (packet_times_kernel N j)
  rw [map_mul, map_one] at hi
  unfold expandedPacket expandedSource
  calc
    _ = (C (1/(j.factorial : ℚ)) * X^j) *
      (expand N hN (packetSeries N j) * expand N hN (sectionKernel N j)) := by ring
    _ = _ := by rw [hi, mul_one]

theorem packet_coefficient_at_address (N : ℕ) (hN : N ≠ 0) (j n : ℕ) :
    PowerSeries.coeff (N*n) (expandedPacket N hN j) =
      Congruential.coeff N j n / ((N*n).factorial : ℚ) := by
  simp [expandedPacket]

end KomorebiPaperIX.ExponentialSection
