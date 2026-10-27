import KomorebiVerification.ExactCoordinates
import KomorebiVerification.FibreRefinement
import KomorebiVerification.ResidueProjectors

/-!
# Kernel audit and concrete smoke tests

Author: Komorebi P.

The examples below instantiate the abstract results on four rational
coordinates.  The final commands ask Lean to report every axiom on which the
principal declarations depend.
-/

set_option autoImplicit false

namespace Komorebi.Verification

open Komorebi.Foundation
open Komorebi.Foundation.LinearProjectorFamily
open Komorebi.Packet

/-- Fine addresses are the four individual coordinates. -/
def fineAddress (i : Fin 4) : Fin 4 := i

/-- Coarse addresses merge the four coordinates into their parity classes. -/
def parityAddress (i : Fin 4) : Fin 2 :=
  ⟨i.val % 2, Nat.mod_lt _ (by omega)⟩

/-- The concrete coordinate masks form a complete orthogonal linear family. -/
def fourCoordinateFamily :
    LinearProjectorFamily ℚ (Fin 4 → ℚ) (Fin 4) :=
  fibreLinearProjectorFamily (R := ℚ) (M := ℚ) fineAddress

/-- Exact recovery holds in the concrete four-coordinate model. -/
example (x : Fin 4 → ℚ) :
    fourCoordinateFamily.rangeSynthesis
      (fourCoordinateFamily.rangeAnalysis x) = x := by
  exact fourCoordinateFamily.rangeSynthesis_rangeAnalysis x

/-- Every valid tuple of range packets is recovered by analysis after synthesis. -/
example (packets : fourCoordinateFamily.PacketSpace) :
    fourCoordinateFamily.rangeAnalysis
      (fourCoordinateFamily.rangeSynthesis packets) = packets := by
  exact fourCoordinateFamily.rangeAnalysis_rangeSynthesis packets

/--
The independently defined parity mask is exactly the sum of its fine
coordinate masks.  This is a concrete `Fin 4 → Fin 2` refinement test.
-/
theorem parity_refinement (b : Fin 2) (x : Fin 4 → ℚ) :
    fibreProj parityAddress b x =
      ∑ c, if parityAddress c = b then fibreProj fineAddress c x else 0 := by
  simpa [fineAddress] using
    (fibreProj_refinement fineAddress parityAddress b x)

/-- A linear operator is recovered exactly from all sixteen packet blocks. -/
example (T : (Fin 4 → ℚ) →ₗ[ℚ] (Fin 4 → ℚ)) (x : Fin 4 → ℚ) :
    (∑ j, ∑ i,
      fourCoordinateFamily.proj j (T (fourCoordinateFamily.proj i x))) = T x := by
  exact transferBlock_reconstruction
    fourCoordinateFamily fourCoordinateFamily T x

end Komorebi.Verification

#print axioms Komorebi.Foundation.LinearProjectorFamily.exactPacketCoordinates
#print axioms Komorebi.Packet.fibreLinearProjectorFamily
#print axioms Komorebi.Packet.fibreLinearProj_refinement
#print axioms Komorebi.Foundation.transferBlock_reconstruction
#print axioms Komorebi.Foundation.transferBlock_comp
#print axioms Komorebi.Algebra.MatrixSupported.mul
#print axioms Komorebi.FiniteDifference.iteratedWeightedDiff_geometric
#print axioms Komorebi.Polyphase.coeffSection_comp
#print axioms Komorebi.Verification.parity_refinement
#print axioms Komorebi.Residue.merge_fineAddress
#print axioms Komorebi.Residue.residueProj_refinement
