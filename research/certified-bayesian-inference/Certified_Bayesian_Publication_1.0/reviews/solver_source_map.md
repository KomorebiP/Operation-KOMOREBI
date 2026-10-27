# Solver manuscript source map and self-review

Scope: `manuscripts/solver.tex`, eight sections, approximately 5,080 whitespace-delimited tokens. Original source files were read without modification. No new Lean statements were created.

## Canonical contract

The fragment uses exact rational cache entries, `prepare M`, complete self-adjoint mutually orthogonal rational output/input packets, positive noise floor, positive posterior/output tolerances, a seed, and a covering scan. Selection preserves the incumbent on ties; the scan can repeat labels. Input projectors participate in certification, while output projectors control selective updates. Gain trajectory equality applies to validated caches and the prepared model kernel. Cached search uses epsilon squared divided by four, with a final independent outward-rounded certification procedure. Candidate validity is proved from outward construction and setup, not an executed `checkCandidate` call in the canonical route. Explicit Bayesian posterior version scope is retained.

The output contract encloses the Joseph Gaussian at the returned gain. It does not certify a law manufactured from covariance centers, an exact-posterior coordinate delta bound, a sampler, sequential filtering, or arbitrary Python parser refinement.

## Declaration locations

| Source position under `Komorebi` | Exact declaration |
|---|---|
| `CachedPacketState.lean:8` | `Kernel` |
| `CachedPacketState.lean:13` | `State` |
| `CachedPacketState.lean:22` | `prepare` |
| `CachedPacketState.lean:26` | `initialState` |
| `CachedPacketState.lean:33` | `Valid` |
| `CachedPacketState.lean:43` | `step` |
| `CachedPacketState.lean:39` | `initialState_valid` |
| `CachedPacketState.lean:52` | `step_other_residual` |
| `CachedPacketState.lean:56` | `step_other_energy` |
| `CachedPacketState.lean:66` | `step_valid` |
| `CachedPacketState.lean:94` | `total_eq_residual_energy` |
| `CachedPacketState.lean:100` | `score` |
| `CachedPacketState.lean:103` | `score_eq` |
| `PacketSelectiveAlgebra.lean:13` | `sum_left_energy` |
| `PacketSelectiveAlgebra.lean:25` | `packetStep` |
| `PacketSelectiveAlgebra.lean:29` | `packetStep_residual` |
| `PacketSelectiveAlgebra.lean:47` | `selected_residual` |
| `PacketSelectiveAlgebra.lean:37` | `unselected_residual` |
| `PacketSelectiveAlgebra.lean:66` | `input_packet_effect` |
| `PacketSelectiveAlgebra.lean:73` | `packetStep_energy_descent` |
| `GreedyPacketSelection.lean:9` | `winner` |
| `GreedyPacketSelection.lean:13` | `winner_ge_initial` |
| `GreedyPacketSelection.lean:22` | `winner_ge_member` |
| `GreedyPacketSelection.lean:48` | `selectPacket_max` |
| `GreedyPacketSelection.lean:55` | `selected_energy_share` |
| `GreedyPacketSelection.lean:69` | `adaptiveRate` |
| `GreedyPacketSelection.lean:73` | `adaptiveRate_bounds` |
| `GreedyPacketSelection.lean:83` | `greedy_energy_contract` |
| `CachedPacketTrajectory.lean:27` | `chosen_eq` |
| `CachedPacketTrajectory.lean:39` | `advance_gain` |
| `CachedPacketTrajectory.lean:45` | `trajectory_valid` |
| `CachedPacketTrajectory.lean:53` | `trajectory_gain` |
| `CachedPacketTrajectory.lean:62` | `trajectory_score_at_fuel` |
| `GreedyPacketConvergence.lean:40` | `greedy_score_geometric` |
| `GreedyPacketConvergence.lean:51` | `adaptiveFuel` |
| `GreedyPacketConvergence.lean:54` | `greedy_score_at_fuel` |
| `GeometricFuel.lean:11` | `geometric_bernoulli` |
| `GeometricFuel.lean:28` | `toleranceFuel` |
| `GeometricFuel.lean:31` | `geometric_fuel_sufficient` |
| `CachedPacketSearch.lean:10` | `search` |
| `CachedPacketSearch.lean:14` | `search_score` |
| `CachedPacketSearch.lean:29` | `search_origin` |
| `CachedPacketSearch.lean:45` | `search_complete` |
| `PrecisionSelection.lean:7` | `precisionFor` |
| `PrecisionSelection.lean:10` | `coefficient_mesh_le` |
| `PrecisionScore.lean:20` | `scoreRoundCoeff` |
| `PrecisionScore.lean:67` | `rounded_score_inflation` |
| `PrecisionCompleteness.lean:13` | `sufficientPrecision` |
| `PrecisionCompleteness.lean:29` | `certifyRounded_of_slack` |
| `RoundedSolverSearch.lean:12` | `certifyGain` |
| `RoundedSolverSearch.lean:25` | `certifyGain_complete` |
| `RoundedSolverSearch.lean:111` | `solveRounded_terminates` |
| `CachedPacketSolver.lean:14` | `solveCached` |
| `CachedPacketSolver.lean:24` | `solveCached_sound` |
| `CachedPacketSolver.lean:37` | `solveCached_terminates` |
| `CachedPacketSolver.lean:70` | `cached_solver_reaches_posterior_tolerance` |
| `CachedPacketOrigin.lean:10` | `cached_solver_gain_origin` |
| `PosteriorOutputPrecision.lean:11` | `outputCoefficient` |
| `PosteriorOutputPrecision.lean:14` | `outputPrecision` |
| `PosteriorOutputPrecision.lean:23` | `mean_coeff_le` |
| `PosteriorOutputPrecision.lean:32` | `covariance_coeff_le` |
| `PosteriorOutputPrecision.lean:44` | `evaluate_radii_le` |
| `PosteriorOutputPrecision.lean:56` | `represent_spec` |
| `PosteriorOutputSemantics.lean:28` | `outputCovariance_posSemidef` |
| `PosteriorOutputSemantics.lean:36` | `approximation_eq_output_gaussian` |
| `PosteriorOutputSolver.lean:10` | `Result` |
| `PosteriorOutputSolver.lean:28` | `ResultValid` |
| `CachedPacketOutput.lean:11` | `runCached` |
| `CachedPacketOutput.lean:20` | `runCached_terminates` |
| `CachedPacketOutput.lean:34` | `runCached_sound` |
| `CachedPacketOutput.lean:53` | `runCached_rejects_nonpositive_output_tolerance` |
| `GeneratedCachedCoordinate.lean:28` | `fuel_computed` |
| `GeneratedCachedCoordinate.lean:29` | `gain_computed` |
| `GeneratedCachedCoordinate.lean:30` | `exact_score_computed` |
| `GeneratedCachedCoordinate.lean:31` | `rounded_score_computed` |
| `GeneratedCachedCoordinate.lean:32` | `cached_return` |
| `GeneratedCachedCoordinate.lean:40` | `output_precision_computed` |
| `GeneratedCachedCoordinate.lean:41` | `mean_centers_computed` |
| `GeneratedCachedCoordinate.lean:42` | `mean_radii_computed` |
| `GeneratedCachedCoordinate.lean:43` | `covariance_centers_computed` |
| `GeneratedCachedCoordinate.lean:44` | `covariance_radii_computed` |
| `GeneratedCachedCoordinate.lean:46` | `output_return` |
| `GeneratedCachedCoordinate.lean:49` | `output_valid` |
| `GeneratedCachedRotated.lean:28` | `fuel_computed` |
| `GeneratedCachedRotated.lean:29` | `gain_computed` |
| `GeneratedCachedRotated.lean:30` | `exact_score_computed` |
| `GeneratedCachedRotated.lean:31` | `rounded_score_computed` |
| `GeneratedCachedRotated.lean:32` | `cached_return` |
| `GeneratedCachedRotated.lean:38` | `output_precision_computed` |
| `GeneratedCachedRotated.lean:39` | `mean_centers_computed` |
| `GeneratedCachedRotated.lean:40` | `mean_radii_computed` |
| `GeneratedCachedRotated.lean:41` | `covariance_centers_computed` |
| `GeneratedCachedRotated.lean:42` | `covariance_radii_computed` |
| `GeneratedCachedRotated.lean:44` | `output_return` |
| `GeneratedCachedRotated.lean:47` | `output_valid` |
| `CachedRoundingBoundary.lean:27` | `naive_score_zero` |
| `CachedRoundingBoundary.lean:28` | `true_score_two` |
| `CachedRoundingBoundary.lean:29` | `naive_cache_invalid` |
| `CachedRoundingBoundary.lean:32` | `naive_final_verification_rejected` |
| `RoundoffConvergence.lean:21` | `rounded_residual_step` |
| `RoundoffConvergence.lean:35` | `roundedGain_tracking` |
| `RoundoffConvergence.lean:60` | `roundoffScoreCoeff` |
| `RoundoffConvergence.lean:72` | `rounded_score_compare` |
| `RoundoffConvergence.lean:102` | `updateAccuracy` |
| `RoundoffConvergence.lean:105` | `roundedFuel` |
| `RoundoffConvergence.lean:109` | `selected_update_floor` |
| `RoundoffConvergence.lean:118` | `rounded_score_at_fuel` |
| `RoundedSolverOrigin.lean:50` | `rounded_solver_gain_origin` |

## Worked-example provenance

- Coordinate model data: `examples/adaptive_coordinate.json`; canonical cached receipt `results/cached_coordinate.json`; full finite-program equations and arrays in `GeneratedCachedCoordinate.lean`. Canonical execution makes six updates with labels 0,1,0,1,0,1. Fuel 410093, exact score 34/117649, precision-12 rounded score 481/1048576, output precision 32. All quoted centers/radii copied from the exact generated source and receipt.
- Rotated model data: `examples/adaptive_rotated.json`; canonical cached receipt `results/cached_rotated.json`; full finite-program equations and arrays in `GeneratedCachedRotated.lean`. Four updates, all label 0. Fuel 4267, exact score 3072/390625, precision-12 rounded score 9111/1048576, output precision 32. Singular prior and rotated projectors are explicit.
- Coordinate covariance 1/117649 * [[156868,-78432],[-78432,98041]] was evaluated from exact Fraction arithmetic in this task and independently expressed by the Joseph identity with exact-gain discrepancy. It is explanatory arithmetic, not a newly claimed named Lean theorem.
- Rotated covariance 130379/390625 * all-ones matrix follows directly from the returned coefficient 203/625, the Joseph formula, and J squared = 2J. It is explanatory algebra.
- Boundary fixture is a down-rounded zero-fractional-bit exact step, not a hardware floating-point simulation. It invalidates center-only exact cache reuse and the final verifier rejects it.

## Benchmark scope

All values are archived values from `BENCHMARK_REPORT.md`, with the seven-case raw report `results/FULL_COST_BENCHMARK.json`. They were not presented as fresh publication-session timings. Producer totals include solve validation/preparation, initial cache, iteration, final certificate, and parameter output. They exclude initial Model.parse, exporter and Lean checking. Iteration ratios exclude setup/certificate/output. Counters omit Fraction bit growth and non-iteration arithmetic. The cached implementation does not establish overall superiority over the efficient full recurrence baseline. All 21 archived exported benchmark candidates have explicit final-gain/posterior checks; their timings and numeric output arrays are not Lean execution traces.

## Proofreading self-review

- Read the proofread-math skill and its checklist, then reviewed this fragment's prose, theorem statements, algebra displays, labels, local notation, and declared macro usage.
- Routine edits: repaired missing backslashes in four `C_{\mathrm{...}}` occurrences, clarified canonical executed checks versus proved candidate validity, replaced an unsupported precision-monotonicity sentence with the proved sufficient-inflation statement, and moved a source identifier out of math mode.
- Mathematical-token changes: renamed the cardinality shorthand from overloaded A to A_count consistently; changed the precision display to explicitly use the source natural-number logarithm, whose value at zero is defined. These are source-consistency corrections made during authoring, rather than changes to any formal source.
- Unresolved issues: none found in the fragment after source comparison and independent review. Shared-document notation alignment and final page layout remain root assembly tasks.
- Validation: declaration-location inventory resolved every listed name to an actual source declaration. Environment/braces/labels checked locally. A two-pass standalone fragment compilation using the shared common.tex succeeded (12 pages, zero overfull boxes, zero undefined references, zero missing glyph warnings). Fresh Lean compilation was not run because no pinned compiler is available in this session. Archived checks are distinguished from fresh execution evidence.
