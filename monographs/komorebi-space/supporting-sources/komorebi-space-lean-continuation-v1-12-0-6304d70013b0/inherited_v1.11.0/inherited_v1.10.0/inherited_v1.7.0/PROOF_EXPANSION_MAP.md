# Komorebi Space proof expansion map — v1.7.0

The theorem program and evidence identifiers are retained. This map records changes to written arguments, not new Lean results.

**67 existing proof blocks expanded**, across 17 chapter source files. Five classical background lemmas are added in the analytic appendix.

| ID | Source chapter | What the expanded proof makes explicit |
|---|---|---|
| KS01 | `01_views.tex` | Construct the lift, verify coherence, and separate two extensionality arguments, including empty domains. |
| KS04 | `01_views.tex` | Make object coverage, arrow coverage, choice independence and both inverse maps explicit. |
| KS06 | `01_views.tex` | Verify the bridge restriction maps before using the gluing theorem and retain both projection equations. |
| KS09 | `02_obstructions.tex` | Unpack image membership, lift independence and both protected correction equations. |
| KS10 | `02_obstructions.tex` | Give explicit inverse functions and explain dependence on the selected origin. |
| KS12 | `02_obstructions.tex` | Prove homomorphism structure before exactness, rather than appealing only to a set-level criterion. |
| KS14 | `02_obstructions.tex` | Display witness transformations and distinguish residual invariance from quotient invariance. |
| KS15 | `02_obstructions.tex` | Provide the direct contradiction and justify quotient descent without a converse separation claim. |
| KS18 | `03_towers.tex` | Use composite restrictions explicitly, handle repeated schedule levels and give both inverse checks. |
| KS19 | `03_towers.tex` | Supply the finite tail estimate, all limit passages and bounded linear projection construction. |
| KS20 | `03_towers.tex` | Show the recurrence lands in the bounded product before bundling the operator, and prove projection identities. |
| KS21 | `03_towers.tex` | Verify projection identities and bounded products before the observable separation and both chart inverses. |
| KS26 | `03_towers.tex` | Expose all typed composites and the left-inverse argument needed for the persistent-space converse. |
| KS27 | `03_towers.tex` | Make kernel nesting and the approximation/depth quantifiers explicit, including zero uniform gain. |
| KS61 | `03a_observation.tex` | Resolve all common-stage indices in quotient composition instead of leaving the naturality moves implicit. |
| KS62 | `03a_observation.tex` | Use one common stage before elementwise lifting, then prove the source projection-surjectivity criterion. |
| KS63 | `03a_observation.tex` | Prove uniform finite-level naturality using lifts of arbitrary finite states, then independence of witness choices. |
| KS64 | `03a_observation.tex` | Supply both eventual-identity witnesses for repeated schedules and the explicit conjugation inverse. |
| KS65 | `03b_repair_transport.tex` | Check kernel membership, both chart identities, commuting-projection equations and the section test. |
| KS66 | `03b_repair_transport.tex` | Keep exact-valued mismatch typed and expand the fixed-map convergence and composition law. |
| KS67 | `03b_repair_transport.tex` | Prove actual telescoping and bounded-product membership, separating unbounded-gap exactness from residual boundedness. |
| KS30 | `04_symmetry.tex` | Check the twisted view system, cocycle law, action order, section equivalence and groupoid laws separately. |
| KS31 | `04_symmetry.tex` | Display the noncommutative cancellation for normalization independence and both trivialization directions. |
| KS32 | `04_symmetry.tex` | Retain multiplication order, the boundary condition and both torsor inverses. |
| KS34 | `04_symmetry.tex` | Expand the actual nonabelian effectuation, all morphisms, and the construction of a quasi-inverse. |
| KS35 | `04_symmetry.tex` | Translate sieves into downward-closed subsets and verify every Grothendieck topology axiom explicitly. |
| KS36 | `04_symmetry.tex` | Unpack the bridge from arbitrary common subpatches to singleton values and back, then handle all sieves. |
| KS37 | `04_symmetry.tex` | Show naturality and both triangle-identity computations, then isolate where saturated prescribed domains are needed. |
| KS39 | `04_symmetry.tex` | Fully type the transport, reflect the boundary equation through faithfulness, and construct essential-image preimages. |
| KS40 | `05_geometry.tex` | Type all prefix transports and exhibit each telescoping difference before taking the norm. |
| KS41 | `05_geometry.tex` | Derive fixed-space equivalence, bounded inverse maps and route independence only on the extendable locus. |
| KS42 | `05_geometry.tex` | Make the projection background explicit and separate kernel closedness from range closedness. |
| KS43 | `05_geometry.tex` | Prove the transverse map is bijective, isolate both completeness assumptions, and establish least gain and the converse. |
| KS44 | `05_geometry.tex` | Derive every amplification factor and prove necessity using infima, without assuming a global nearest exact family. |
| KS46 | `05_geometry.tex` | Establish the inherited Hilbert structures and orthogonal decomposition, not ambient projection commutation. |
| KS47 | `05_geometry.tex` | Separate the two implications and explain why the invisible sequence need not converge. |
| KS48 | `05_geometry.tex` | Replace the terse adjoint argument with the required restricted dual estimate and two Pythagorean decompositions. |
| KS49 | `05_geometry.tex` | Construct the inverse by its series, verify both inverse sides and distinguish exact competitors from orthogonal repair. |
| KS50 | `05_geometry.tex` | Prove the two annihilation identities and both inverse restrictions with correct operator order. |
| KS51 | `05_geometry.tex` | Compute the matrix square and unit-vector lower bound; distinguish general theorem radius from all-real formulas. |
| KS56 | `05_geometry.tex` | Identify the full affine correction fiber, track the signs in the distance identity, and prove necessity on the permitted subspace. |
| KS70 | `05a_certificates.tex` | Locate the use of old-kernel preservation and strict positivity before absorbing the perturbation. |
| KS71 | `05c_iteration.tex` | Give Cauchy and tail-limit quantifiers, then use closed sublevels rather than incorrectly upgrading lower semicontinuity to continuity. |
| KS72 | `05c_iteration.tex` | Separate the two inductions, summability and limiting argument, including zero residual and zero contraction cases. |
| KS73 | `05c_iteration.tex` | Construct the actual limiting admissible correction and distinguish image membership from closure membership. |
| KS74 | `05c_iteration.tex` | Write the three-distance estimate with metric separation and an explicit feasible-fiber counterexample. |
| KS76 | `05d_floors.tex` | Make both infimum/closure implications explicit and avoid silently asserting attainment. |
| WR01 | `05f_bounded_realization.tex` | Separate weak continuity of the operator from the assumed strong convergence of its images. |
| WR02 | `05f_bounded_realization.tex` | Derive orthogonality from two-sided line variations and supply the full Cauchy and intersection argument. |
| lem:weak-subsequence | `05f_bounded_realization.tex` | Prove the weak subsequence result without assuming ambient separability; spell out diagonal selection and test-vector approximation. |
| WR03 | `05g_budget_certificates.tex` | Prove budget attainment, convexity, endpoint continuity and equality cases with quantifiers and no minimax shortcut. |
| WR04 | `05g_budget_certificates.tex` | Derive the variational inequality without a differentiability shortcut and handle every dual support degeneracy. |
| WR05 | `05g_budget_certificates.tex` | Keep the common feasible domain explicit and show both directions of the infimum comparison. |
| WR06 | `05h_regularized_repair.tex` | Construct the inverse from coercivity, show onto-ness rather than assume it, and expand every mixed term in the objective. |
| WR07 | `05h_regularized_repair.tex` | Keep the sign of each parameter comparison explicit and compute the normalized witness penalty. |
| WR08 | `05h_regularized_repair.tex` | Give all epsilon/subsequence quantifiers, distinguish vanishing penalty from boundedness, and justify full-family strong convergence. |
| WR09 | `05h_regularized_repair.tex` | Show the scalar square-completion and sharpness separately from the written limiting argument. |
| WR10 | `05i_diagonal_regularization.tex` | Verify Hilbert membership before coordinate optimality and state both directions of each integral tail comparison. |
| WR11 | `05i_diagonal_regularization.tex` | Supply explicit uniform tail bounds and the full budget interpolation argument behind the pi/4 limit. |
| WR12 | `05i_diagonal_regularization.tex` | Retain the exact ceiling inequalities and distinguish bias from propagated data noise. |
| WR13 | `05j_inexact_certificates.tex` | Expand the exact error equation and retain the square-completion that produces the sharp fitted-data constant. |
| WR14 | `05j_inexact_certificates.tex` | Show the cancellation of every dual mixed term, construct the maximizing witness and derive the correction guarantee. |
| WR15 | `05k_stopping_rules.tex` | Prove the Gram projection formula, treat the residual as a covector and cancel every basis-change factor. |
| WR16 | `05k_stopping_rules.tex` | Insert the measured and intended exact optimizers separately and track which theorem controls each error term. |
| KS54 | `06_boundaries.tex` | Separate the finite-solvability quantifiers from a matching family and use an explicit global contradiction. |
| KS57 | `06_boundaries.tex` | Carry row operations, field normalization signs, affine parametrization, exclusivity and degenerate dimensions explicitly. |
| KS58 | `06_boundaries.tex` | Prove stabilization, induced surjectivity, seeded lifting, and both evaluation-image inclusions. |

## Evidence boundary

Canonical v1.2.0 and focused v1.6.0 formal records are retained, with both source trees unchanged. No new Lean compilation or axiom audit was run. Ten WR groups remain written-only; two retain written limiting consequences alongside formal pointwise inequalities.

The audit preserves the exact principal theorem statements and checks proof text hashes and labels. It cannot certify the correctness of natural-language mathematics. The supporting analytic appendix is a written treatment of classical facts, not five new formalized claims.
