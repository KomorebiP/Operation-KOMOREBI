/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiVerification.PaperII.NestedRefinement
import KomorebiVerification.PaperII.ResidueFourierCRT
import KomorebiVerification.PaperII.WeightedTransfer
import KomorebiVerification.PaperII.TransferZeta
import KomorebiVerification.PaperII.ResultantSeparation
import KomorebiVerification.PaperII.SmithDyadic
import KomorebiVerification.PaperII.LinearDefects
import KomorebiVerification.PaperII.TypedLinearDefects
import KomorebiVerification.PaperII.CommonRefinementConsumers
import KomorebiVerification.PaperII.ReleaseCoordinatesConsumers
import KomorebiVerification.PaperII.ReleaseFilteredPaths
import KomorebiVerification.PaperII.ReleaseResultantIntegralPackets
import KomorebiVerification.PaperII.ReleaseResultantDVR
import KomorebiVerification.PaperII.ReleaseGluingBinary
import KomorebiVerification.PaperII.ReleaseGluingPrecisionBridge
import KomorebiVerification.PaperII.ReleaseGluingFinite
import KomorebiVerification.PaperII.ReleaseGluingEquivSmith
import KomorebiVerification.PaperII.ReleaseGluingMatrix
import KomorebiVerification.PaperII.ReleaseGluingPacketBridge
import KomorebiVerification.PaperII.ReleasePrecisionQuotient
import KomorebiVerification.PaperII.ReleaseDefectCompatibility
import KomorebiVerification.PaperII.ReleaseTransferConsequences
import KomorebiVerification.PaperII.ReleaseSmithTransport
import KomorebiVerification.PaperII.ReleaseSmithSign
import KomorebiVerification.PaperII.ReleaseSmithCharacters
import KomorebiVerification.PaperII.ReleaseRectifiableCycle

/-!
# Projector-Resolved Seed Calculus II

Aggregate import for the current Paper II Lean development.

The accompanying current manuscript correspondence records the scope of each
proved endpoint. General rectifiable-cycle Cauchy and canonical holomorphic
functional-calculus independence are not proved by this aggregate.

The fail-closed trust audit is intentionally a separate build target:
`KomorebiVerification.PaperII.KernelAudit`.
-/
