# Signal Reconstruction mathematical scope review

Author of the manuscripts: Komorebi P.  
Review date: 6 October 2026, America/Chicago.  
Primary verdict on the inherited theorem package: **correct only after the stated restrictions and local repairs below**.

The exact finite-rate recovery chain is sound under its printed distinct-node, nonzero-amplitude, spectral-separation and finite-order hypotheses. The July sources contain prose proofs and Python experiments. No Signal Reconstruction specific Lean proof was identified in the bounded source search. Related Paper V declarations support packet coordinates, known-edge cancellation and measurable-mask perturbation. They do not certify the July unknown-edge Prony estimator or its self-calibration rates.

This is an audit of the inherited sources and the published mathematical scope. The final traditional catalogue's 46 SG contracts have been reconciled with the related formal source at the statement, hypothesis and domain level in `lean/Claim_Lean_Concordance.json`. This review does not replace the independent final proof audit of the traditional paper or the visual guide review. The current Lean guide has its own source and publication review in `LEAN_REPORT.md`.

## Source and search scope

The review read all three July source-and-claim maps, the two reconstruction manuscripts, the mathematical/model-boundary sections of the complex signal/image benchmark, and the current Paper V Lean guide's known-edge and perturbation sections. It subsequently inspected the preserved Paper V v1.1.0 packet, integer/Hilbert polyphase, FIR transfer, Laurent bank, known-edge, measurable-mask, complete-pruning and evaluator sources. The exact TeX source hashes and theorem locators appear in `SIGNAL_SOURCE_CLAIM_ASSOCIATIONS.json`; the raw formal declaration inventory and quoted anchors appear under `lean/`.

The Library title search covered Signal, Reconstruction, Polyphase, Gibbs, Unknown_Edge and Self_Calibrating. A second bounded content search paired Lean with Prony, Hankel, Gibbs and annihilator. It identified the current Paper V guide and general projector infrastructure, but no dedicated unknown-edge/self-calibration Lean project. This is a statement about the searched and inspected materials, not proof that no other formalization exists anywhere.

The relevant original claim maps are:

| Source | Current Library identity | Evidence advertised |
|---|---|---|
| Universal_Unknown_Edge_Recovery_SOURCE_AND_CLAIM_MAP.md | libfile_64da7206e7548191a5386144fef20aee | Prose exact theorems and 19 historical named Python checks |
| Self_Calibrating_Polyphase_Gibbs_Reconstruction_SOURCE_AND_CLAIM_MAP.md | libfile_6ec0563800c4819185fd05357695d774 | Prose conditional theorems and finite experiments |
| Complex_Signal_Image_Gibbs_Benchmark_SOURCE_AND_CLAIM_MAP.md | libfile_275b97175908819196036daf2e585f3d | Controlled tests separated from exploratory out-of-model images |
| Paper_V_Lean_Guide_Final.pdf | libfile_19f5cc36cf4081918a8b744a5e2321a1 | Related known-edge and mask-error formal infrastructure |

The July summary maps list 18 and 12 principal items. The raw TeX sources have 19 and 17 named theorem-like environments respectively. These are different indexing conventions, with overlap and supporting results. Their counts must not be added as a count of independent new theorems.

## Normalized reconstruction claim

Work on the periodic circle of length T=2π, with Fourier coefficients fhat(n)=T^-1 integral f(x) exp(-inx) dx. The edge is a mean-zero periodic piecewise-constant packet with finitely many distinct active jumps, amplitudes summing to zero, and a fixed right-continuous representative when pointwise reconstruction is wanted. Otherwise reconstruction means equality almost everywhere.

For a trigonometric background of degree at most K, moments above K satisfy m_n=T i n fhat(n)=sum_l a_l z_l^n, with z_l=exp(-i tau_l). At most L active jumps are recovered from the declared low-mode block and 2L consecutive high modes. The zero-edge case must return the zero mean-zero edge and reconstruct the background directly. Roots and amplitudes are determined up to permutation, then sorted on the circle.

The self-calibrated version uses n=(q0+q)N+r with N≥2 and q0≥1. Its aliased nodes u_l=z_l^N must be distinct for the selected decimation. Adjacent coefficient channels give b_(l,r+1)=z_l b_(l,r). A multi-offset phase estimator requires at least one adjacent product and a nonzero denominator. Perturbed recovery additionally requires a specified singular-value threshold, matched local inverse bounds, nonzero amplitude bounds and a strict branch margin. Physical separation alone does not imply alias separation for every decimation.

## Dependency graph

1. Noninjectivity or overlapping model components obstruct identifiability. This is direct internal logic.
2. Projecting away the finite background changes the sparse observation operator to A=(I-P_S)D. The null-secant condition gives uniqueness. This is direct finite linear algebra.
3. Distributional differentiation converts periodic jumps into a finite atomic measure. Integration by parts proves the Fourier moment identity.
4. Vandermonde factorization gives Hankel rank. A nonsingular leading Hankel solve determines the annihilator. Polynomial root extraction determines locations. A Vandermonde solve determines amplitudes. Mean-zero integration and low-mode subtraction reconstruct the packets.
5. Offset coefficient progression supplies the phase omitted by decimation. The strict nearest-root margin and corresponding-root chord bound give the one-order lifting gain.
6. Weyl's singular-value bound controls rank thresholds. Rouché's theorem controls roots in supplied true-root disks. These are external classical inputs verified by the literature review, with the complex matrix form obtained by the indicated minimax/realification argument.
7. Bounded linear smooth synthesis gives the reconstruction error estimate. Edge parameter errors require the corrected mean-zero periodic L1 bound below.
8. Python experiments test specific solvers, thresholds, geometries, noise scales and images. They do not prove the universal theorem hypotheses or verify the implementation in Lean.

## Obligation matrix

| Obligation | Result | Exact boundary |
|---|---|---|
| Measurement and decomposition obstruction | Passed | Different target packets must genuinely be admissible objects with equal data |
| Residualized sparse secant criterion | Passed | Coefficient uniqueness in a fixed finite dictionary, without a guarantee for a greedy solver |
| Spark shorthand at high sparsity | Correct only with explicit convention | Use spark=∞ for a full independent dictionary, or replace the usual shorthand by spark(A)>min(2s,N) |
| Restricted separation minimum | Passed for s≥1 and nonempty dictionary | Handle s=0 separately, avoiding a minimum over an empty set |
| Periodic derivative/Fourier convention | Passed | Mean zero and zero-sum jumps are retained |
| Rank and annihilator reconstruction | Passed | Distinct nodes, nonzero active amplitudes, enough consecutive moments; handle rank zero separately |
| Exact pointwise reconstruction | Conditional on representative convention | Fourier data determine equivalence classes; a right-continuous convention fixes jump values |
| Separation-free location stability obstruction | Passed after metric/proof clarification | Compare two fixed-order narrow pulses using a permutation-matched circular location metric |
| Exact offset phase | Passed with R≥1 | The R=0 normalizer is undefined |
| Branch-margin and one-order root gain | Passed | Correct continuous root branch, normalized nonzero estimate, strict margin, N≥2 |
| Non-bandlimited recovery rates | Conditional on printed uniform inverse, gap and margin inputs | No derivation of those inputs from arbitrary Fourier data |
| Resolved synthesis inequality | Passed for bounded linear A_M | An arbitrary nonlinear bounded function need not satisfy the error decomposition |
| Printed mean-zero edge L1 location bound | Refuted | A normalization constant doubles the leading location cost; correction below |
| Image model guarantee | Passed in the finite model only | Full-rank background basis or genuine orthogonal projection; dictionary membership and secant condition required |
| Empirical unknown-order/image measurements | Bounded computations with failures retained | Floating point, concrete thresholds and model mismatch; improved synthesis does not imply correct parameter order |
| Dedicated signal Lean coverage | Not addressed by inspected original sources | Related Paper V support must remain explicitly separate |

## Decisive L1 correction

The July self-calibration manuscript prints

    ||j-jhat||_1 ≤ T sum |a-ahat| + sum |ahat| d_T(tau,tauhat).

That inequality is false with the declared mean-zero normalization. Let

    j = 1_[0,π) - 1/2,
    jhat = 1_[δ,π) - (π-δ)/(2π),    0<δ<π.

Both packets have amplitudes (+1,-1). Only the first location changes. The proposed right side is δ. Direct integration gives

    ||j-jhat||_1 = 2δ(1-δ/T) > δ.

A valid simple correction keeps the original amplitude term and multiplies the location term by 2. A stronger bound in the same additive form is

    ||j-jhat||_1 ≤ (T/4) sum |a-ahat|
                  + 2 sum |ahat| d_l(1-d_l/T),
    d_l = d_T(tau_l,tauhat_l).

Proof: define the mean-zero periodic sawtooth G(x)=1/2-x/T for 0<x<T. Its distributional derivative is δ_0-dx/T, and its L1 norm is T/4. The amplitude sums vanish, so j=sum a_l G(x-tau_l) is piecewise constant, has the prescribed jumps and has mean zero. Furthermore, direct integration gives

    ||G(·-tau)-G(·-tauhat)||_1 = 2d(1-d/T).

Subtract the two representations and apply the triangle inequality. The amplitude coefficient is attained by changing two antipodal jump amplitudes. Each nonlinear location term is attained by shifting exactly one endpoint of a mean-zero interval packet. An independent agent derived this counterexample and correction from the definitions without being given the suspected defect.

Three exact rational checks on the unit-period counterpart give actual costs 15/128, 7/32 and 3/8 for location shifts 1/16, 1/8 and 1/4, each exceeding the old right side and lying below twice that right side. These small checks illustrate the analytic counterexample. They are not a new broad computation suite and must not be added to another agent's assertion totals.

## A fixed-order stability witness

The inherited proof compares a collapsing two-edge packet with the zero packet, without defining a metric across different edge counts. Use a fixed-order proof instead. Compare the (+1,-1) locations (0,epsilon) and (theta,theta+epsilon), with theta=T/4 and 0<epsilon<theta. The permutation-matched bottleneck circular distance is theta. For each fixed integer Fourier index n,

    m_n-mhat_n = (1-exp(-in theta))(1-exp(-in epsilon)),
    |m_n-mhat_n| ≤ 2|n| epsilon.

For any fixed finite measurement block, the data difference tends to zero while the location distance stays positive. Thus no inverse for the declared location target can have a separation-uniform Lipschitz constant. The argument does not assert the same obstruction for every possible metric on the synthesized signal.

## Formal association and open obligations

The preserved sources identify `KomorebiPaperV.known_edge_error` in `KnownEdge.lean` and `KomorebiPaperV.MaskPerturbation.finite_p_perturbation`, `infinity_perturbation`, and `full_signal_perturbation` in `MaskPerturbation.lean`. `KnownEdge` is not an extra namespace component. The first theorem has an arbitrary `Q : E → E`; it does not assume linearity, projection structure or a Fourier rate. The finite-exponent mask results use extended norms, with measurable masks and `1 ≤ p`, `p ≠ ∞`. The infinity bound's condition is actual empty symmetric difference, not almost-everywhere equality. Its packet and integer/Hilbert polyphase modules support the coordinate infrastructure. Its historical 20-result/225-target contract must not be relabeled as a formalization of the July reconstruction theorems.

The Signal Lean guide explains these related declarations, quotes their raw types, and records the remaining formal obligations for Hankel/annihilator recovery, matching, rank gaps, offset phases and branch lifting. No new Signal Lean code or fresh-build certificate is asserted. The current runtime probe found no `lean` or `lake` on PATH, and no new build was attempted. Current source-name/hash/line consistency is a static check, distinct from the inherited build.

The exact reconstruction is a finite **algebraic** procedure: polynomial roots are an additional operation beyond linear system solves. Calling the whole method only finite linear algebra hides this step. No efficient general sparse-search algorithm, global noisy minimax theorem, unrestricted two-dimensional geometry result, model-free recovery theorem or historical novelty conclusion is established by this publication task.

## Current source and contract reconciliation

The new catalogue explicitly retains the sparse null-secant condition and capped spark convention (SG-14), nonzero and zero-order branches (SG-19–22), representative convention (SG-21–22), supplied-threshold rank gate (SG-28), nonempty adjacent-product and branch gates (SG-29–35), bounded linear synthesis (SG-36), corrected sawtooth L1 bound (SG-37), and the Fourier truncation norm growth (SG-38). The last point prevents the global rate theorem from assuming a uniformly bounded L1 Fourier partial-sum operator. SG-38 also normalizes the recovered real amplitudes to sum zero before canonical periodic integration. The conditional root-disk argument uses the true centers and coefficient errors and remains distinct from a data-only posterior certificate.

The related source is the CRC-checked Paper V v1.1.0 archive, SHA-256 `7a15b94133739c26b8da5aadb2a2415c0bc539888430cec1baf0fb6425ea580e`. Two downloaded copies of the later final ZIP both had the advertised size and the same hash, but neither passed archive validation. The cause is undetermined; the failure and retry are preserved as provenance. The valid fallback contains 23 production proof modules, 25 Lean files including root/audit, and 349 explicit declarations. All 225 theorem targets match source names, files and lines and the inherited allowed-axiom records. This is current static consistency plus inherited build evidence, without current elaboration.

The live per-SG map copies all 46 current statements, hypotheses and domains and records the input catalogue SHA. Sixteen SG statements have related formal infrastructure; thirty have no recovered target in this inspected corpus. None is claimed as a fully formalized current Signal theorem. Original manuscripts and logs remain preserved unchanged. Current numerical reruns and their assertion totals belong to the execution agent's independent records.

## Rank and implementation controls

The largest-adjacent-singular-ratio rule does not follow from the supplied-threshold theorem. An exact four-dimensional Fourier-matrix witness has true Hankel singular values `(400,396,4,0)` and perturbed values `(400,396,4,0.4)`. The perturbation norm is below half the last true singular value, yet the largest ratio chooses order two rather than three. A supplied threshold in `(0.4,3.6)` still selects order three. The general ratio claim is excluded; the mathematical threshold gate remains intact.

The generic nuisance-projector implementation originally used an unvalidated QR basis, which can over-project a rank-deficient basis. Its compact-SVD separation computation can return a positive last listed singular value for a wide support even though the column map has a nullspace. The documented full-rank 24-by-8 example does not exercise either defect. The rank-aware execution copy and its negative controls are separate from the preserved originals and from formal evidence. The traditional theorem handles order zero; the native nonconstant `EdgeModel` and `recover_unknown_edges` API exclude it, and the dictionary rank patch adds no zero-order wrapper.

The fresh complex stress case `bursts_6_jump` estimates order nine rather than six. Its unmatched location/jump errors are infinite while the synthesized RMSE is finite and improved. The initial overstrong all-cases parameter-success assertion failed and is preserved. The follow-up scope records the stress failure explicitly. This publication must not relabel it as successful identification or all-model certification.

## Additional standalone infinite-packet source review

The separate `infinite_packet_gibbs_reconstruction_spd.py` was inspected at its generator, refit, clipping, pixel-completion, tests, benchmark and final claim-boundary functions. This is a bounded source review, not a review of every line or a fresh execution.

- `benchmark_case` passes the full input image to the reconstructor and forms residual completion from `image - result.reconstruction`. Its experiment is adaptive approximation of available pixel data. It is not blind inference from a finite Fourier measurement block.
- The ideal dyadic grammar and coordinate-basis completion can be discussed mathematically. The implemented generator has finite candidate and seed-mask caps, so its actual run is a finite frontier. The comments about a countably dense unbounded atlas are not themselves a proof of density for the capped implementation.
- `_refit` solves a ridge-regularized normal equation by default, with ridge 1e-9. The mathematical stationarity law is exactly M^T r = ridge*c; numerical tests check it within tolerance. The exact nested-subspace projection theorem remains a valid ideal statement, but the generally nonzero ridge contribution prevents the implemented refit from being that orthogonal projector. Pixel-span completeness similarly does not mean its ridge solver returns an exactly zero residual.
- `bounded_synthesis` is clipping to [0,1]. It is a nonlinear metric projection with a nonincrease-of-error guarantee toward truths in that box. It must not be substituted into the bounded **linear** resolved-synthesis identity.
- The exact residual archive f=q+r retains the residual itself and therefore has no universal sparse compression claim.
- The historical per-method timing field compares the method string with `infinite_packet`, whereas the method dictionary uses `packet_core` and `packet_completed`. Every stored method timing is therefore zero. Those cells are placeholders, not measured zero runtime or fair timing comparisons. The case-level measured runtime is a separate valid field.

The traditional author and computation reviewer were notified of these boundaries. The computation record owns any implementation correction, rerun and resulting counts.
