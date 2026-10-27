# Komorebi Unified Inference / Stochastic / Bayesian — v13

Author: Komorebi P. Date: 2026-09-12.
Active release: CHECKED_RELEASES/FD_Adaptive_Packet_Posterior_Solver_v0.1.0_Checked.
Parent archive SHA256:
508aa1d65b7591b94fc638e6fccb2541f1b42e2778826d97eb07fc52d42e6b70.

## Newly completed

A genuine packet-selective computation policy is implemented and Lean checked:
choose the largest current output-packet residual energy and update only that
output packet. The model and packet geometry remain fixed. The new updates are
EXACT RATIONAL; certification and output intervals use rounded dyadic arithmetic.
The inherited v11 rounded FULL-update solver remains a separate checked branch.
Do not claim this block proves rounded selective-update convergence.

For sigma>0, valid complete self-adjoint rational packet families, a seed and a
scan covering all output labels, and positive rational epsilon and delta, the
canonical program Komorebi.AdaptivePosterior.runAdaptive returns a result with

    W2(actual posterior, Joseph Gaussian of returned gain) <= epsilon,

passing candidate/tolerance checks, and mean/covariance interval arrays of THAT
Gaussian with every radius <= delta. The returned gain is an actual greedy
iterate within computed fuel. Returned parameter precision and arrays equal the
actual v12 evaluator. Covariance centers do not define a separately certified law.

## Mechanism

F(B)=P H^T-B S, S=H P H^T+R, tau=1/(sigma+trace S),
q=(1-sigma/(sigma+trace S))^2. A single output-packet update is

    B' = B + tau Q_a F(B),
    F(B') = F(B) - tau Q_a F(B) S.

All unselected OUTPUT gains/residuals are unchanged. The selected residual obeys
Q_a F(B')=(Q_a F(B))(I-tau S). Complete accounting and max-energy selection give

    E(F(B')) <= r E(F(B)),   r=1-(1-q)/A,   0<=r<1,

where A is the positive number of output packet labels. The seed ensures A>0.
Ties retain the incumbent; repeated or unsorted scan labels are allowed. Coverage
is checked by the actual solver. Zero output residual packets stay zero.

The exact score a(B)=E(F(B))*(sigma+||y-Hm||^2)/sigma^2 obeys a(B_n)<=r^n a(B_0).
Fuel N=ceil_nat(a(B_0)/((epsilon/2)^2*(1-r))) gives a(B_N)<=epsilon^2/4.
At each iterate the solver tries verification probes plus the inherited computed
sufficient precision. That fallback passes at the horizon, proving actual early-
stopping termination without a fallback to the full-update solver.

## Main declarations

Namespace Komorebi.AdaptivePosterior:
  packetStep_energy_descent, input_packet_effect,
  selected_energy_share, greedy_energy_contract, greedy_score_at_fuel,
  solveAdaptive_terminates, adaptive_solver_gain_origin,
  adaptive_solver_reaches_posterior_tolerance,
  runAdaptive_terminates, runAdaptive_sound, zero_packet_invariant.

## Checked executions and counterexample

Coordinate case: P=diag(4,1), H=[1,1], R=[1], y=[1], m=0.
Selections 0,1,0,1,0; gain (228/343,8/49)^T; epsilon=1/20;
12-bit certificate score 1525/1048576. Sufficient fuel 410093; actual updates 5.

Singular rotated case: P=ones(2,2), H=R=I, y=(1,-1), m=0.
Selections 0,0,0; gain (39/125)ones(2,2); epsilon=1/4;
12-bit certificate score 215859/4194304. Fuel 4267; actual updates 3.
The second output packet has zero exact residual and is not updated in this run.
Both examples use 32-bit output arrays with radius tolerance delta=1/1000.
All selected labels, actual returns, gain, scores, parameter arrays and posterior
statements are kernel-checked, not inferred from Python diagnostics.

A boundary proves why input locality must not be assumed: S=[[2,1],[1,2]],
tau=1/5 and F=[1,0] become F'=[3/5,-1/5]. Total energy falls 1 -> 2/5 but the
second INPUT packet energy rises 0 -> 1/25. Valid model setup is also checked.

## Evidence

90 active modules have matching successful source/log/compiled-output/dependency
receipts. Twelve new modules were compiled in this block; 78 unchanged inherited
modules reuse the matching v12 receipts and compiled hashes, not a claimed fresh
rebuild. All 455 theorem/lemma declarations are axiom-audited; 69 are new support,
universal and concrete statements. Only propext, Classical.choice, Quot.sound.
Lean 4.34.0-rc2 and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06, one thread,
warnings as errors. Five corrected current-block draft failures, six preserved
inherited failures, no incomplete compile snapshots. Three invalid controls
rejected. Independent exact diagnostics: six shapes, eight updates each, two
complete outputs, 911 assertions and eight expected rejections. Final Mathbox
computation manifest validated. No new literature or performance claim.

## Reproduction and remaining finish line

Read the active README for producer and rebuild commands. Python
PASS_ADAPTIVE_PROVISIONAL becomes a formal instance only when its emitted explicit
Lean source compiles. Resource caps can prevent completion and success-proof export.
The reference implementation still computes full residuals, scans all output
packets, and evaluates full rounded certificates. Selective updating is proved;
computational savings are not. Conservative fuel bounds are not cost estimates.

Next bounded routes: maintain cached residual/packet scores with checked update
identities and work counts, or prove rounded selective updates with a controlled
selection-error contract. Then benchmark full computation plus verification costs.
Hierarchy-changing refinement, sequential filtering, uncertain-input/parser
semantics, point-valued factor/sampler output and literature comparison remain
open. Preserve v12 interval semantics and the v11 rounded-solver boundary.
Do not reopen completed foundations without identifying a concrete defect.
