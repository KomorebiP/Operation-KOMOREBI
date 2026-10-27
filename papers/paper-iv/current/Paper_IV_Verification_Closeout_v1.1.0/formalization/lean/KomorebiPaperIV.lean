/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.CyclicFilters
import KomorebiPaperIV.SectionCycles
import KomorebiPaperIV.FormalExponential
import KomorebiPaperIV.Appell
import KomorebiPaperIV.FiniteAnalytic
import KomorebiPaperIV.ReciprocalCore
import KomorebiPaperIV.AlgebraicCompletion
import KomorebiPaperIV.ThetaCore
import KomorebiPaperIV.EarlyCompletion
import KomorebiPaperIV.HypergeometricCompletion
import KomorebiPaperIV.FiniteModels
import KomorebiPaperIV.ReciprocalCompletion
import KomorebiPaperIV.ParameterThetaCompletion
import KomorebiPaperIV.BellCompletion
import KomorebiPaperIV.EntireBridge
import KomorebiPaperIV.Wronskians
import KomorebiPaperIV.CompanionBridge
import KomorebiPaperIV.CompanionCompletion
import KomorebiPaperIV.CompanionSpectrum
import KomorebiPaperIV.ODESolutions
import KomorebiPaperIV.AnalyticCycles
import KomorebiPaperIV.ExponentialBounds
import KomorebiPaperIV.ZeroGeometry
import KomorebiPaperIV.ZeroPerturbation
import KomorebiPaperIV.ExponentialRemainder
import KomorebiPaperIV.RegularPolygonGap
import KomorebiPaperIV.SignedZeroLocalization
import KomorebiPaperIV.SignedZeroCorrection
import KomorebiPaperIV.SignedSectorConfinement
import KomorebiPaperIV.SignedSectorExhaustion
import KomorebiPaperIV.SignedGlobalExhaustion
import KomorebiPaperIV.SignedZeroOrbits
import KomorebiPaperIV.SignedDerivativeAsymptotics
import KomorebiPaperIV.SignedDominance
import KomorebiPaperIV.SignedFiniteExceptions
import KomorebiPaperIV.ReducedEntire
import KomorebiPaperIV.ReducedZeros
import KomorebiPaperIV.SignedZeroSequence
import KomorebiPaperIV.ZeroSequenceAsymptotics
import KomorebiPaperIV.ZeroSequenceCounting
import KomorebiPaperIV.ReducedCanonicalProduct
import KomorebiPaperIV.WeightedZeroCounts
import KomorebiPaperIV.ZeroEnumeration
import KomorebiPaperIV.FullZeroCounting
import KomorebiPaperIV.ReducedZeroCounting
import KomorebiPaperIV.FullZeroSummability
import KomorebiPaperIV.ZeroZetaConvergence
import KomorebiPaperIV.LargeZeroCompletion
import KomorebiPaperIV.SignedRealPhase
import KomorebiPaperIV.SignedCorrectionCompletion
import KomorebiPaperIV.CubicZeroCorrection
import KomorebiPaperIV.DerivativeGrowth
import KomorebiPaperIV.BranchedDirichlet
import KomorebiPaperIV.DerivativeWeightedZeta
import KomorebiPaperIV.ExponentialZetaComparison
import KomorebiPaperIV.HurwitzLattice
import KomorebiPaperIV.ZeroLatticeComparison
import KomorebiPaperIV.ZeroZetaDecomposition
import KomorebiPaperIV.ZeroZetaContinuation
import KomorebiPaperIV.BranchZetaContinuation
import KomorebiPaperIV.QuarticExactZeros
import KomorebiPaperIV.ExactZetaModels
import KomorebiPaperIV.FullCanonicalProduct
import KomorebiPaperIV.CanonicalProductMultiplicity
import KomorebiPaperIV.CanonicalProductQuotient
import KomorebiPaperIV.SublinearExponentialRigidity
import KomorebiPaperIV.EntireQuotientGrowth
import KomorebiPaperIV.CanonicalProductGrowth
import KomorebiPaperIV.HadamardIdentification
import KomorebiPaperIV.CanonicalPartialFractions
import KomorebiPaperIV.ZeroMomentDerivatives
import KomorebiPaperIV.ZeroMomentCoefficients
import KomorebiPaperIV.ThetaZeroBell
import KomorebiPaperIV.ZeroMomentLogarithm
import KomorebiPaperIV.DominantExponential
import KomorebiPaperIV.SharpGrowth
import KomorebiPaperIV.IndicatorGeometry
import KomorebiPaperIV.UniformDominantSectors
import KomorebiPaperIV.AlignedExponentialRadii
import KomorebiPaperIV.IndicatorLimit
import KomorebiPaperIV.SemanticChecks
import KomorebiPaperIV.AnalyticTaylorAlgebra
import KomorebiPaperIV.AnalyticTaylorDifferential
import KomorebiPaperIV.CompleteHomogeneous
import KomorebiPaperIV.DiagonalFredholm
import KomorebiPaperIV.DiagonalNuclear
import KomorebiPaperIV.DiagonalTrace
import KomorebiPaperIV.InfiniteSymmetric
import KomorebiPaperIV.JensenZeroGrowth
import KomorebiPaperIV.LeadingPoleBounds
import KomorebiPaperIV.NearestPoleExpansion
import KomorebiPaperIV.NormalizedEntire
import KomorebiPaperIV.NormalizedExactOrder
import KomorebiPaperIV.NormalizedGrowth
import KomorebiPaperIV.NormalizedOrder
import KomorebiPaperIV.NormalizedProduct
import KomorebiPaperIV.NormalizedZeroBell
import KomorebiPaperIV.NormalizedAnalyticPowers
import KomorebiPaperIV.OrbitPoleReduction
import KomorebiPaperIV.PoleCoefficientBounds
import KomorebiPaperIV.PoleRemoval
import KomorebiPaperIV.PoleTaylor
import KomorebiPaperIV.PrincipalPartCoefficients
import KomorebiPaperIV.PrincipalPartUniqueness
import KomorebiPaperIV.SecantAsymptotic
import KomorebiPaperIV.SimplePoleParts
import KomorebiPaperIV.SublinearHadamard
import KomorebiPaperIV.WeightedGrowthSummability


import KomorebiPaperIV.PointwiseFilters
import KomorebiPaperIV.PointwiseAddition
import KomorebiPaperIV.AnalyticReciprocalLaws
import KomorebiPaperIV.OperatorEncodingBridge
import KomorebiPaperIV.TangentBoundary
import KomorebiPaperIV.CompactReciprocal
import KomorebiPaperIV.NewtonDeterminant
import KomorebiPaperIV.HypergeometricAnalytic
import KomorebiPaperIV.QuotientExponential

/-!
# Projector-Resolved Seed Calculus IV

Formal-power-series, finite root-of-unity and quotient-algebra models,
companion-shift identities, reciprocal parameter recurrences, residue-section
Appell systems, tangent/Riccati identities, theta polynomials, entire transfer
and signed functions, analytic Wronskians, and companion trace formulas. The exact companion spectrum, entire ODE basis, order-two zeros, and quantitative
near-cancellation lemma are included. Local positive real simple zero strings for all N >= 3, explicit canonical
remainder estimates, and quantitative correction bounds are proved. Exact sector
confinement, global exhaustion, rotation and multiplicity identities, disk-index
uniqueness, and original-denominator derivative error bounds are included.
The reduced entire denominator, finite exceptional sets, named zero sequences,
sharp tail summability thresholds, bounded-error tail counting, and an entire
canonical tail product are proved. Full multiplicity-weighted counting and
convergence exponents, unique global zero strings with derivative asymptotics,
and the exact zero-zeta convergence half-planes and holomorphy are now proved.
Real leading corrections, alternating derivative signs, the explicit cubic
correction, and derivative-weighted zeta convergence/holomorphy are proved.
Unweighted Hurwitz continuation with exact poles/residues, branch dependence,
and the exact order-two/four models are proved. Jensen and Poisson estimates
now prove rigidity of the actual canonical-product quotient, completing
Hadamard identification. Sharp maximum-modulus order and type, the full
indicator polygon including tie directions, and uniform zero-free dominant
sectors are proved. Mittag-Leffler partial fractions, normalized
logarithm series, Newton zero sums and their tangent, reciprocal and theta
Bell coefficient formulas are proved. The specialized diagonal determinant, complete homogeneous form, normalized-section product/order/Bell identities and nearest-pole asymptotics are now proved. Pointwise filters/addition, Gamma-normalized hypergeometric evaluation, actual quotient-algebra exponential convergence, fixed-logarithm laws, the Newton determinant, compact reciprocal formulas, global Riccati identity and the named operator inverse close the final 15 partial records.
-/

