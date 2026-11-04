import KomorebiPolynomial.PolynomialPackets
import KomorebiPolynomial.FallingFactorial
import KomorebiReader.ResiduePackets

/-!
# Concrete falling-factorial residue packets

The linear equivalence `fallingEquiv` sends the ordinary monomial `X^k`
to the falling factorial `X (X - 1) ... (X - k + 1)`. Conjugation by this
constructed equivalence therefore gives the operator `Φ P Φ⁻¹` displayed
in the reading example. Every carrier in this module is `ℚ[X]`.
-/

set_option autoImplicit false

open scoped BigOperators Polynomial

namespace Komorebi.Polynomial.FallingPackets

open Komorebi.Polynomial.Packets
open Komorebi.Polynomial.FallingFactorial
open Komorebi.Reader.ResiduePackets

/-- Transport a rational polynomial linear operator through the actual
falling-factorial coordinate equivalence. -/
noncomputable def fallingOperator (T : ℚ[X] →ₗ[ℚ] ℚ[X]) : ℚ[X] →ₗ[ℚ] ℚ[X] :=
  fallingEquiv.toLinearMap.comp (T.comp fallingEquiv.symm.toLinearMap)

@[simp] theorem fallingOperator_apply (T : ℚ[X] →ₗ[ℚ] ℚ[X]) (p : ℚ[X]) :
    fallingOperator T p = fallingEquiv (T (fallingEquiv.symm p)) := rfl

theorem fallingOperator_on_coordinates (T : ℚ[X] →ₗ[ℚ] ℚ[X]) (p : ℚ[X]) :
    fallingOperator T (fallingEquiv p) = fallingEquiv (T p) := by
  simp

theorem fallingOperator_comp (T U : ℚ[X] →ₗ[ℚ] ℚ[X]) :
    fallingOperator (T.comp U) = (fallingOperator T).comp (fallingOperator U) := by
  ext p
  simp

/-- The concrete falling-degree residue projector `Φ P_r^(N) Φ⁻¹`. -/
noncomputable def fallingPacket (N r : ℕ) : ℚ[X] →ₗ[ℚ] ℚ[X] :=
  fallingOperator (packetLinear N r)

@[simp] theorem fallingPacket_apply (N r : ℕ) (p : ℚ[X]) :
    fallingPacket N r p = fallingEquiv (packet N r (fallingEquiv.symm p)) := rfl

theorem fallingPacket_on_coordinates (N r : ℕ) (p : ℚ[X]) :
    fallingPacket N r (fallingEquiv p) = fallingEquiv (packet N r p) := by
  simp

@[simp] theorem fallingPacket_coordinates (N r : ℕ) (p : ℚ[X]) :
    fallingEquiv.symm (fallingPacket N r p) = packet N r (fallingEquiv.symm p) := by
  simp

theorem fallingPacket_coordinate_coeff (N r k : ℕ) (p : ℚ[X]) :
    (fallingEquiv.symm (fallingPacket N r p)).coeff k =
      if k % N = r then (fallingEquiv.symm p).coeff k else 0 := by
  rw [fallingPacket_coordinates, coeff_packet]

/-- Every polynomial has this finite packet formula in its actual falling
coordinates, obtained from the inverse equivalence. -/
theorem fallingPacket_formula (N r : ℕ) (p : ℚ[X]) :
    fallingPacket N r p =
      ∑ k ∈ (fallingEquiv.symm p).support,
        if k % N = r then (fallingEquiv.symm p).coeff k • descPochhammer ℚ k else 0 := by
  rw [fallingPacket_apply, packet_eq_sum, map_sum]
  apply Finset.sum_congr rfl
  intro k _
  split_ifs <;> simp [fallingEquiv_monomial]

/-- A falling-factorial basis vector belongs to its own degree packet. -/
theorem fallingPacket_basis (N r k : ℕ) :
    fallingPacket N r (descPochhammer ℚ k) =
      if k % N = r then descPochhammer ℚ k else 0 := by
  rw [← fallingEquiv_X_pow k, fallingPacket_on_coordinates, packet_X_pow]
  split_ifs <;> simp

/-- The explicit finite falling-factorial formula, for any finite list of
basis degrees and rational coefficients. -/
theorem fallingPacket_expansion (N r : ℕ) (s : Finset ℕ) (a : ℕ → ℚ) :
    fallingPacket N r (∑ k ∈ s, a k • descPochhammer ℚ k) =
      ∑ k ∈ s, if k % N = r then a k • descPochhammer ℚ k else 0 := by
  rw [map_sum]
  apply Finset.sum_congr rfl
  intro k _
  rw [map_smul, fallingPacket_basis]
  split_ifs <;> simp

theorem fallingPacket_idempotent (N r : ℕ) (p : ℚ[X]) :
    fallingPacket N r (fallingPacket N r p) = fallingPacket N r p := by
  exact coordinateTransfer_idempotent fallingEquiv.toAddEquiv
    (packetLinear N r).toAddMonoidHom (packet_idempotent N r) p

theorem fallingPacket_orthogonal (N : ℕ) {r s : ℕ} (hrs : r ≠ s) (p : ℚ[X]) :
    fallingPacket N r (fallingPacket N s p) = 0 := by
  exact coordinateTransfer_orthogonal fallingEquiv.toAddEquiv
    (packetLinear N r).toAddMonoidHom (packetLinear N s).toAddMonoidHom
    (packet_orthogonal N hrs) p

theorem fallingPacket_reconstruct {N : ℕ} (hN : 0 < N) (p : ℚ[X]) :
    (∑ r ∈ Finset.range N, fallingPacket N r p) = p := by
  exact coordinateTransfer_reconstruct fallingEquiv.toAddEquiv
    (fun r => (packetLinear N r).toAddMonoidHom) (Finset.range N)
    (packet_reconstruct hN) p

theorem fallingPacket_refinement {N M : ℕ} (hM : 0 < M) (hNM : N ∣ M)
    (r : ℕ) (p : ℚ[X]) :
    fallingPacket N r p =
      ∑ s ∈ Finset.range M, if s % N = r then fallingPacket M s p else 0 := by
  simp only [fallingPacket_apply]
  rw [packet_refinement hM hNM, map_sum]
  apply Finset.sum_congr rfl
  intro s _
  split_ifs <;> simp

/-- Every input/output packet interaction reconstructs the concrete transported
operator. The two positive moduli may be different. -/
theorem fallingOperator_block_reconstruction (T : ℚ[X] →ₗ[ℚ] ℚ[X])
    {N M : ℕ} (hN : 0 < N) (hM : 0 < M) (p : ℚ[X]) :
    fallingOperator T p =
      ∑ r ∈ Finset.range N, ∑ s ∈ Finset.range M,
        fallingPacket N r (fallingOperator T (fallingPacket M s p)) := by
  exact coordinateTransfer_block_reconstruction fallingEquiv.toAddEquiv T.toAddMonoidHom
    (fun r => (packetLinear N r).toAddMonoidHom)
    (fun s => (packetLinear M s).toAddMonoidHom)
    (Finset.range N) (Finset.range M) (packet_reconstruct hN) (packet_reconstruct hM) p

end Komorebi.Polynomial.FallingPackets
