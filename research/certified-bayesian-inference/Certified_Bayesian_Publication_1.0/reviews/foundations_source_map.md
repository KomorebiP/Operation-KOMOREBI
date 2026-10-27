# Foundations manuscript source map

Author: Komorebi P. Publication source: `FD_Certified_Inference_Core_v1.0.0_Checked`, exact archive SHA256 `844ae280ea4be7e7c25906e00733f0130996b32aa110c53951df00f8c18fa488`.

## Scope

`manuscripts/foundations.tex` is a complete fragment for the traditional paper. It covers the finite Gaussian model, singular-prior support, rectangular observations, factor-coded exact rational data, exact Bayesian disintegration, canonical-kernel equality evidence-almost everywhere, arbitrary-gain Joseph Gaussian, explicit common-noise transport, residual-energy posterior certificate, complete orthogonal packet accounting, rational candidate checker, and a worked singular example.

All general mathematics is exposition of the project-local raw Lean declarations listed below. The manuscript does not claim a new external theorem, a fresh Lean compilation, a universal Python/parser refinement, or a sampler implementation. The singular worked example is exact explanatory arithmetic derived from the general source identities; no newly compiled instance is claimed. No figures are referenced by this fragment. Root may integrate shared figure placements as appropriate.

## Main statement mapping

| Manuscript label / statement | Raw source file | Exact declaration(s) | Interpretation |
|---|---|---|---|
| `eq:foundation-innovation` | `Komorebi/FDKalmanDefs.lean` | `innovationMatrix`, `gainMatrix`, `posteriorCovMatrix` | Real finite-dimensional matrix definitions. |
| Factor-coded input | `Komorebi/RationalCertificateChecker.lean` | `RationalModel`, `RationalModel.prior`, `RationalModel.noise`, `RationalModel.innovation`, `RationalModel.residual`, `RationalModel.innovationVector` | Rational factor representation, not every arbitrary real covariance. |
| Factor semantics and floor | `Komorebi/RationalModelSemantics.lean` | `RationalModel.prior_real_posSemidef`, `RationalModel.noise_real_posDef`, `RationalModel.noise_real_floor`, `RationalModel.real_residual`, `RationalModel.real_innovationVector` | Exact rational-to-real interpretation. |
| `eq:foundation-coercivity`, `eq:foundation-inverse-bound` | `Komorebi/FDInnovationConditioning.lean` | `QuadraticLowerBound`, `innovation_quadraticLowerBound`, `inverse_norm_le_of_quadraticLowerBound`, `innovation_inverse_norm_le` | Proved inverse operator bound; no supplied approximate inverse. |
| `lem:foundation-exact-joseph` | `Komorebi/FDPosteriorCovPSD.lean` | `josephCovMatrix_eq_posteriorCovMatrix`, `posteriorCovMatrix_posSemidef` | Joseph covariance equality and PSD, singular priors allowed. |
| `thm:foundation-disintegration` | `Komorebi/FDGaussianConditioning.lean` | `fd_joint_disintegration`, `fd_observation_evidence` | Exact equality of actual joint probability measures, genuine evidence marginal. |
| Explicit kernel formula | `Komorebi/FDPosteriorKernel.lean` | `fdPosteriorKernel`, `fdPosteriorKernel_apply` | Pointwise defined posterior version for supplied observation. |
| Canonical-kernel boundary | `Komorebi/FDGaussianConditioning.lean` | `fdPosteriorKernel_eq_canonical`, `canonicalPosterior_eq_multivariateGaussian`, `canonicalPosterior_eq_josephGaussian` | Evidence-almost-everywhere equality, not pointwise equality to every canonical representative. |
| Arbitrary gain Joseph law | `Komorebi/FDInexactGainAlgebra.lean`, `Komorebi/FDGainSampler.lean` | `gainJoseph`, `gainJoseph_posSemidef`, `gainMean`, `gainPosteriorLaw` | Valid Gaussian law for arbitrary gain. |
| `eq:foundation-gap-residual` | `Komorebi/FDInexactGainAlgebra.lean` | `gainResidual_eq_gap_mul`, `gain_gap_eq_residual_mul_inv` | Exact residual/gain-gap identities. |
| `prop:foundation-excess-cov` | `Komorebi/FDInexactGainAlgebra.lean` | `gainJoseph_sub_posterior_eq_gap`, `gainJoseph_sub_posterior_eq_residual`, `gainJoseph_excess_posSemidef` | Excess covariance exact expression and PSD. |
| Shared-noise marginals | `Komorebi/FDGainSampler.lean` | `gainSample`, `gainSample_law`, `gainPosteriorLaw_exact`, `gainSample_exact_posterior_law`, `inexactGainCoupling_isTransportPlan` | Actual law identities and transport-plan marginals. Mathematical sampler map only. |
| `eq:foundation-coupling-cost` | `Komorebi/FDInexactGainCoupling.lean` | `inexactGainCoupling_cost_gap`, `inexactGainCoupling_cost_residual` | Exact cost of constructed coupling; no optimality claim. |
| `eq:foundation-residual-exact-cost` | `Komorebi/FDInexactGainCoupling.lean` | `posterior_wasserstein2Sq_le_gain_residual`, `posterior_wasserstein2Sq_ne_top` | All-coupling W2 infimum bounded by explicit finite coupling. |
| `lem:foundation-energy-majorant` | `Komorebi/FDResidualEnergyCertificate.lean` | `quadratic_residual_cost_le_energy` | Energy majorant; applied to inverse with valid noise-floor constant. |
| `thm:foundation-residual-certificate` | `Komorebi/FDResidualEnergyCertificate.lean` | `gainResidualEnergyBudget`, `posterior_wasserstein2Sq_le_residual_energy`, `posterior_wasserstein2_le_of_residual_tolerance` | Pointwise law tolerance against explicit posterior version, squared rational stopping test. |
| Zero residual exactness | `Komorebi/FDInexactGainCoupling.lean` | `gainPosteriorLaw_eq_of_residual_zero` | Exact equality of probability laws. |
| Packet structure | `Komorebi/SelfAdjointPackets.lean` | `SelfAdjointPackets`, `SelfAdjointPackets.Complete`, `sumOn_transpose`, `sumOn_idempotent` | Self-adjoint disjoint idempotents; completeness separate. |
| `thm:foundation-packet-energy` | `Komorebi/PacketEnergyDecomposition.lean` | `matrixEnergy_sumOn_left`, `matrixEnergy_sumOn_right`, `matrixEnergy_sumOn_both`, `matrixEnergy_eq_sum_blocks` | Exact complete and local parent energy identities. |
| Partial accounting direction | `Komorebi/PacketEnergyDecomposition.lean` | `sum_block_energies_le` | Partial packet energy is a lower bound, not stopping upper bound. |
| `cor:foundation-packet-tolerance` | `Komorebi/FDResidualPacketCertificate.lean`, `Komorebi/PosteriorEnclosureBounds.lean` | `frobeniusSq_le_packet_majorants`, `posterior_wasserstein2_le_of_packet_majorants`, `posterior_wasserstein2Sq_le_energy_majorants` | Complete local energy and innovation majorants imply law bound. |
| Rational packet checks | `Komorebi/RationalPacketCertificates.lean` | `RationalPacketsValid`, `checkRationalPackets_eq_true`, `realPackets`, `realPackets_complete`, `rationalEnergy_cast`, `rational_packet_majorant` | Four exact structural obligations and their real interpretation. |
| Candidate check boundary | `Komorebi/RationalCertificateChecker.lean` | `RationalCandidate`, `ValidCandidate`, `checkCandidate`, `checkCandidate_eq_true`, `candidateScore`, `checkTolerance`, `checkTolerance_eq_true` | Exact finite checks independent of producer assertion. |
| `thm:foundation-checked-tolerance` | `Komorebi/RationalPosteriorCertificate.lean` | `valid_residual_energy_bound`, `valid_innovation_energy_bound`, `checked_score_bounds_posterior`, `checked_tolerance_bounds_posterior` | Real posterior-law guarantee from rational accept/tolerance. |
| Finite speculative batch | `Komorebi/RationalPosteriorCertificate.lean` | `selected_batch_bounds_posterior`, `selected_batch_preserves_posterior_tolerance` | Validity-preserving checked finite acceptance policy. |
| Parameter boundary discussion | `RELEASE_SCOPE.md`; `Komorebi/PosteriorOutputSemantics.lean`; `Komorebi/PosteriorOutputSolver.lean` | `outputMean_real`, `outputCovariance_real`, `approximation_eq_output_gaussian`, `represented_real_errors`, `ResultValid` | Returned intervals describe the same gain-defined Joseph approximation; no exact-posterior coordinate interpretation. |

## Proofreading self-review

Proofread: full authored `manuscripts/foundations.tex`, including all statement/proof displays and source identifiers.

- Routine edits: source-map correction locating `ResultValid` in `PosteriorOutputSolver.lean` and listing the exact output-semantics declarations. No prose rewrite was required after reread.
- Mathematical-token changes during proofreading: none.
- Unresolved issues: none in the authored fragment. Fresh Lean compilation remains unavailable in this author's session; the archived source is the mathematical authority.
- Validation: Python structural check confirms all 8 proof environments and other TeX environments are correctly nested, all 47 labels are unique, and all local cross-reference targets resolve. Every path-styled source identifier in the fragment was located in raw active Lean source. Root owns PDF compilation and rendered-page layout verification.
- Independent mathematical audit: `bayes_independent_audit` compared the complete proof chain and singular worked example against raw source and reported no requested mathematical correction. That audit confirmed the new example's covariance `5/9`, exact common-noise cost `1/12`, floor-energy score `2/9`, and tolerance `epsilon=1/2`.

The complete fragment contains 5,021 whitespace-separated words, including displayed mathematics and source identifiers. It has 7 sections, 8 theorem/lemma/proposition/corollary statements with detailed proofs, 29 numbered equation/align environments, and 47 labels. This count is a transparent source-text count, not a claim that TeX command names are prose words.
