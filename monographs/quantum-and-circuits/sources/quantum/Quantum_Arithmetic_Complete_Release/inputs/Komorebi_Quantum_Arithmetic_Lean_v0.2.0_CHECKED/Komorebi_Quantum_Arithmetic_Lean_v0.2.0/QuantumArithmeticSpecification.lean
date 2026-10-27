module
public import QuantumArithmeticBridge

@[expose] public section

set_option autoImplicit false
set_option maxRecDepth 16384
set_option maxHeartbeats 0

namespace Komorebi.QuantumArithmetic

/-! These certificates connect the literal tables to their intended finite specifications.
They do not assert an arbitrary-modulus theorem or a hardware implementation. -/

/-- The selected indices really are exactly the coprime residues modulo 12. -/
theorem unitResidues12_specification :
    (List.range 12).filter (fun a => decide (Nat.Coprime a 12)) = unitResidues12 := by
  decide +kernel

/-- The coordinate root has exact order 12, not just order dividing 12. -/
theorem zeta12_no_smaller_positive_power :
    ∀ k : Fin 11, cPow zeta12 (k.val + 1) ≠ cOne := by
  decide +kernel

/-- Every entry of the literal matrix agrees with the cyclic convolution formula. -/
theorem projector12_kernel_specification :
    ∀ i j : Fin 12,
      (projector12.getD i.val []).getD j.val 0 =
        ramanujan12.getD ((i.val + 12 - j.val) % 12) 0 / 12 := by
  decide +kernel

/-- The test vector really is the signal plus the displayed perturbation. -/
theorem testSignal12_decomposition :
    testSignal12 = vecAdd ramanujan12 noise12 := by
  decide +kernel

/-- The energy identity is supported by an explicit zero cross term. -/
theorem ramanujan12_noise12_orthogonal : dot ramanujan12 noise12 = 0 := by
  decide +kernel

/-- The independently written rational and cyclotomic signal tables coincide. -/
theorem ramanujanCVector_matches_rational :
    ramanujanCVector = ramanujan12.map cRat := by
  decide +kernel

/-- The independently written absolute-value tables also coincide. -/
theorem absRamanujanCVector_matches_rational :
    absRamanujanCVector = absRamanujan12.map cRat := by
  decide +kernel

/-- Signed half-period antisymmetry, with indices interpreted cyclically. -/
theorem ramanujan12_half_period :
    ∀ n : Fin 12, ramanujan12.getD ((n.val + 6) % 12) 0 =
      -(ramanujan12.getD n.val 0) := by
  decide +kernel

/-- The absolute-value signal instead has period 6. -/
theorem absRamanujan12_half_period :
    ∀ n : Fin 12, absRamanujan12.getD ((n.val + 6) % 12) 0 =
      absRamanujan12.getD n.val 0 := by
  decide +kernel

/-- Exact probability table in the original basis, normalized by energy 48. -/
def sampleProbabilities12 (v : QVector) : QVector :=
  v.map (fun a => a * a / 48)

theorem sampleProbabilities12_normalized :
    (sampleProbabilities12 ramanujan12).sum = 1 ∧
      (sampleProbabilities12 absRamanujan12).sum = 1 := by
  decide +kernel

theorem sampleProbabilities12_agree :
    sampleProbabilities12 ramanujan12 = sampleProbabilities12 absRamanujan12 := by
  decide +kernel

/-- Both Fourier tables have purely rational entries, so no other coordinate
contributes to their squared absolute values. -/
theorem both_dft_tables_rational :
    ∀ k : Fin 12,
      dft12 ramanujanCVector k.val = cRat (dft12 ramanujanCVector k.val).a ∧
      dft12 absRamanujanCVector k.val = cRat (dft12 absRamanujanCVector k.val).a := by
  decide +kernel

/-- For these rational Fourier tables only, the square is the full squared
absolute value.  The factor 48*12 accounts for state and unitary normalization. -/
def fourierProbabilities12 (v : List Cyclo12) : QVector :=
  (List.range 12).map (fun k => (dft12 v k).a ^ 2 / (48 * 12))

def coprimeMass12 (v : List Cyclo12) : ℚ :=
  (unitResidues12.map (fun k => (dft12 v k).a ^ 2 / (48 * 12))).sum

/-- Both transformed tables also have total probability one. -/
theorem fourierProbabilities12_normalized :
    (fourierProbabilities12 ramanujanCVector).sum = 1 ∧
      (fourierProbabilities12 absRamanujanCVector).sum = 1 := by
  decide +kernel

/-- This is tied to the actual computed DFTs, not just the scalar identity 12^2/576. -/
theorem phase_sensitive_coprime_mass :
    coprimeMass12 ramanujanCVector = 1 ∧ coprimeMass12 absRamanujanCVector = 0 := by
  decide +kernel

/-- The two states have the same local probabilities but different transported ones. -/
theorem finite_phase_sensitivity :
    sampleProbabilities12 ramanujan12 = sampleProbabilities12 absRamanujan12 ∧
    coprimeMass12 ramanujanCVector = 1 ∧ coprimeMass12 absRamanujanCVector = 0 := by
  exact ⟨sampleProbabilities12_agree, phase_sensitive_coprime_mass⟩

end Komorebi.QuantumArithmetic
