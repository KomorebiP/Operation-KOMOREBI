import KomorebiPhysics.Relativistic3DWeightedDiracDomain

/-!
# Block 50: finite Fourier compatibility for the generator bridge

CURRENT STATUS: UNCOMPILED DRAFT. The pinned Lean 4.34.0-rc2 and Mathlib
environment from the Block 49 verification record is not available in this
execution environment. Consequently NONE of the new declarations below is
represented as an independently checked Lean theorem.

The analytic proof of the full generator, resolvent, and weighted-rate results
is in Block50_Spectral_Generator_Bridge.pdf. Those analytic results are NOT
asserted as Lean theorems in this file until compilation is available.

This file first extracts a robust finite-cutoff compatibility interface, which
is needed before strong convergence and domain arguments can be imported.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open scoped ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics
namespace Relativistic3DGeneratorBridge

open Relativistic3DFullFourierEvolution
open Relativistic3DTorusFourierEvolution
open Relativistic3DUnboundedDirac
open Relativistic3DWeightedDomain

/-- Exact commutation of continuum evolution with any finite Fourier cutoff.
This finite identity is an ingredient, not a proof of strong differentiability. -/
theorem continuum_evolution_commutes_cutoff (m t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    continuumCoeffPropagator m t (coeffTruncation S f) =
      coeffTruncation S (continuumCoeffPropagator m t f) := by
  classical
  apply lp.ext
  funext n
  by_cases hn : n ∈ S
  · simp [continuumCoeffPropagator_apply, coeffTruncation_apply, hn]
  · simp [continuumCoeffPropagator_apply, coeffTruncation_apply, hn]

/-- Exact commutation of centered evolution with any finite Fourier cutoff. -/
theorem centered_evolution_commutes_cutoff (m h t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    centralCoeffPropagator m h t (coeffTruncation S f) =
      coeffTruncation S (centralCoeffPropagator m h t f) := by
  classical
  apply lp.ext
  funext n
  by_cases hn : n ∈ S
  · simp [centralCoeffPropagator_apply, coeffTruncation_apply, hn]
  · simp [centralCoeffPropagator_apply, coeffTruncation_apply, hn]

/-- Physical Fourier cutoff, defined using the existing linear isometry. -/
def physicalCutoff (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    Relativistic3DTorusFourierEvolution.TorusSpinorL2 :=
  torusFourierEquiv.symm (coeffTruncation S (torusFourierEquiv f))

/-- The physical continuum evolution commutes with the physical Fourier cutoff. -/
theorem physical_evolution_commutes_cutoff (m t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    continuumTorusUnitary m t (physicalCutoff S f) =
      physicalCutoff S (continuumTorusUnitary m t f) := by
  apply torusFourierEquiv.injective
  simp only [torusFourierEquiv_continuumTorusUnitary_apply,
    physicalCutoff, LinearIsometryEquiv.apply_symm_apply]
  simpa [continuumCoeffUnitary_apply] using
    (continuum_evolution_commutes_cutoff m t S (torusFourierEquiv f))

/-- The physical centered evolution commutes with the same Fourier cutoff. -/
theorem physical_centered_evolution_commutes_cutoff (m h t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    centralTorusUnitary m h t (physicalCutoff S f) =
      physicalCutoff S (centralTorusUnitary m h t f) := by
  apply torusFourierEquiv.injective
  simp only [torusFourierEquiv_centralTorusUnitary_apply,
    physicalCutoff, LinearIsometryEquiv.apply_symm_apply]
  simpa [centralCoeffUnitary_apply] using
    (centered_evolution_commutes_cutoff m h t S (torusFourierEquiv f))

end Relativistic3DGeneratorBridge
end KomorebiPhysics

/-!
# Pending full formal proof obligations

1. Define the strong derivative of `continuumCoeffUnitary m t` at zero in the
   Banach-space topology for vectors in `continuumDiracDomain m`.
2. Prove the integral / difference quotient estimate mode by mode, bound it
   by the norm of `continuumDiracPMap m f`, and pass through the ℓ² tail.
3. Prove the converse generator-domain inclusion using coordinate continuity.
4. Invoke the appropriate Stone theorem, or show uniqueness of the generator,
   to identify the pre-existing `continuumTorusUnitary` with the spectral
   exponential of `physicalDiracPMap` on its maximal domain.
5. Add the centered bounded selfadjoint family on the SAME torus label set,
   prove its graph convergence, and then strong resolvent convergence.
6. Add third-order spatial Fourier weights and prove the global O(h²) rate.

No unproved theorem or custom axiom is inserted to bypass these obligations.
-/
