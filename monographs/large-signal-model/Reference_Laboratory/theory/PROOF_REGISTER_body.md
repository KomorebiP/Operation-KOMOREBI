\begingroup\footnotesize\setlength{\cftbeforesecskip}{0pt}\tableofcontents\endgroup\newpage

# Proof, assumptions and evidence register

**Foundations 1.0.0. Frozen scope: 87 propositions. No new numbered results.**

This register records the source location, principal internal dependencies, necessary inputs and strongest claim boundary for each proposition. Code links identify a reference implementation or finite illustration, not an executable general proof. All general proofs remain written arguments in the cumulative volume. No Lean kernel or independent external referee was used.

Read the entire indicated section before applying a proposition. Assumptions can precede its bold statement. The dependency map is curated rather than extracted from formal proof terms. In particular, Proposition 9 uses Proposition 12, a forward reference in the presentation. The map is acyclic.

All 87 statement-and-proof spans are byte-identical to the immediate 0.9.0 predecessor. The earlier P72 dimension clarification is retained. Relative to preserved 0.8.0, exactly that one correction remains. The release-freeze checker verifies the immediate predecessor separately.

The machine-readable JSON contains full source and code hashes. Hashes identify artifacts; they do not establish truth. The manuscript retains primary-source attribution for the classical ingredients.

\newpage
# Realization and predictive closure
Propositions 1–13. Related finite suite: `checks/exact_foundation_checks.py`.

\Needspace{9\baselineskip}
## P1. Exact realization and consistency

**Location and role.** Section 2, source lines 51–73. Identity. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Finite Hilbert spaces; a declared analysis/synthesis pair with a left inverse.

**Boundary.** Reconstruction is not predictive sufficiency.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P2. Coherent transport and operator realization

**Location and role.** Section 3, source lines 93–112. Identity. Principal dependencies: P1.

**Requires.** Consistent coefficient spaces; one pairwise coherent family of chart maps.

**Boundary.** Agreement across charts does not establish correctness.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P3. Complete refinement preserves reconstruction

**Location and role.** Section 4, source lines 130–153. Identity. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Orthogonal projector tree; a complete antichain.

**Boundary.** Omitted children or energy-only storage lose the reconstruction contract.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P4. Transfer reconstruction and refinement

**Location and role.** Section 4, source lines 130–187. Identity. Principal dependencies: P3.

**Requires.** Linear maps with complete input, intermediate and output projector resolutions.

**Boundary.** Nonlinear maps require interaction terms.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P5. Polynomial packet interactions

**Location and role.** Section 4, source lines 130–209. Identity. Principal dependencies: P4.

**Requires.** A specified finite multilinear polynomial expansion and complete packets.

**Boundary.** No automatic general nonlinear dictionary discovery.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P6. Exact quotient criterion

**Location and role.** Section 5, source lines 213–232. Criterion. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** A summary onto its image; deterministic transitions on the stated domain.

**Boundary.** A quotient must be constant on every summary fiber.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P7. Closure defect and compositional defect

**Location and role.** Section 5, source lines 213–261. Criterion. Principal dependencies: P6.

**Requires.** Orthogonal retained projector; linear dynamics on the declared whole state space.

**Boundary.** Small omitted energy alone does not bound future influence.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P8. Minimal linear predictive completion

**Location and role.** Section 6, source lines 267–286. Construction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Known finite family of linear operators and initial observables.

**Boundary.** The constructed observables need not be measured or low dimensional.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P9. Coarsest joint finite closure

**Location and role.** Section 7, source lines 300–338. Construction. Principal dependencies: P12.

**Requires.** Known finite stochastic transitions; positive likelihoods; initial partition with at least two blocks.

**Boundary.** The one-block Bayesian necessity exception must be retained.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P10. Exact projected memory and a conditional tail bound

**Location and role.** Section 8, source lines 344–385. Bound. Principal dependencies: P7.

**Requires.** Linear retained/unresolved split; contraction and bounded history for the tail estimate.

**Boundary.** One-step tail error is not recursive rollout error.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P11. Ideal statistical benefit of refinement

**Location and role.** Section 9, source lines 393–406. Identity. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Square-integrable target; nested sigma algebras; exact conditional expectations.

**Boundary.** An estimated finite-data predictor can worsen after refinement.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P12. Bayesian closure and its exact defect

**Location and role.** Section 10, source lines 412–442. Criterion. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** At least two coarse blocks; strictly positive likelihoods for universal necessity.

**Boundary.** Fixed-prior defect permits nonnegative likelihoods only with positive evidence.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P13. Strong fixed-horizon refinement limit

**Location and role.** Section 12, source lines 473–499. Limit. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Bounded operator; orthogonal projections converging strongly to the identity.

**Boundary.** Fixed horizon and strong convergence, not norm or time-uniform convergence.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\newpage
# Learning and stability
Propositions 14–25. Related finite suite: `checks/learning_stability_checks.py`.

\Needspace{9\baselineskip}
## P14. Exact causal delay closure

**Location and role.** Section 15, source lines 586–618. Criterion. Principal dependencies: P6, P8.

**Requires.** Autonomous finite linear process; positive delay length; true observation-map rank plateau.

**Boundary.** An empirical rank plateau alone is not predictive-space coverage.

**Code link.** `checks/observable_reference.py`, `learn_delay`, lines 107–109. Exact finite delay learner under supplied closure and span assumptions.

\Needspace{9\baselineskip}
## P15. Data-span identification and its boundary

**Location and role.** Section 16, source lines 626–646. Criterion. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Paired exact columns; input-kernel inclusion in successor kernel.

**Boundary.** Interpolation identifies the sampled span, not unseen directions.

**Code link.** `checks/observable_reference.py`, `fit_closed_span`, lines 62–90. Exact sampled-span interpolation and kernel compatibility.

\Needspace{9\baselineskip}
## P16. Fixed-space identification bound

**Location and role.** Section 16, source lines 626–688. Bound. Principal dependencies: P15.

**Requires.** Fixed full-row-rank coordinates; input error below the smallest singular value.

**Boundary.** Does not learn a coordinate space or certify its rank.

**Code link.** `checks/stochastic_reference.py`, `noisy_core_bound`, lines 168–186. Related finite fixed-core perturbation bound, not a general noisy-coordinate learner.

\Needspace{9\baselineskip}
## P17. Finite-prefix indistinguishability

**Location and role.** Section 17, source lines 694–698. Obstruction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Any fixed finite observation horizon; no supplied dimension bound.

**Boundary.** A finite prefix cannot rule out a later hidden response.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P18. Compositional defect propagation

**Location and role.** Section 19, source lines 764–800. Bound. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Lipschitz maps on domains containing both compared trajectories; declared local defects.

**Boundary.** Different policies need a separate action-mismatch bound.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P19. Uniform prediction bound for a stable finite-memory truncation

**Location and role.** Section 20, source lines 842–893. Bound. Principal dependencies: P10, P18.

**Requires.** Finite-memory gain sum below one; uniformly bounded true-history defect.

**Boundary.** Spectral radius alone is not the stated induced-norm condition.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P20. Packet-interaction truncation bound

**Location and role.** Section 21, source lines 920–952. Bound. Principal dependencies: P5.

**Requires.** Declared polynomial terms; restricted multilinear norms; bounded domain.

**Boundary.** Bounds omitted terms, not the quality of an undiscovered basis.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P21. Coherent reconciliation and coordinate-stable transport

**Location and role.** Section 22, source lines 970–1012. Construction. Principal dependencies: P1, P2.

**Requires.** Fixed exact atlases; normalized nonnegative weights; linear chart predictors.

**Boundary.** Consistent reconciliation need not improve accuracy.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P22. The upward-lift obstruction

**Location and role.** Section 23, source lines 1024–1042. Criterion. Principal dependencies: P6.

**Requires.** Coarse and proposed finer state maps; a norm for the lower bound.

**Boundary.** A genuinely finer state generally cannot be initialized from the coarse state alone.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P23. Exact accounting for an enumerated grammar

**Location and role.** Section 24, source lines 1060–1093. Identity. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Countable fixed grammar and prior; finite positive full and active evidence; common likelihood measure.

**Boundary.** Continuous likelihood densities need not be bounded by one.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P24. Prior-preserving program refinement

**Location and role.** Section 24, source lines 1060–1117. Identity. Principal dependencies: P23.

**Requires.** Prior-mass-preserving split; a whole-record likelihood mixture identity.

**Boundary.** A fixed child mixture is not independent switching at each step.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P25. Observationally grounded finite linear realization

**Location and role.** Section 25, source lines 1125–1139. Integration. Principal dependencies: P1, P2, P3, P4, P14, P15, P16, P18.

**Requires.** Autonomous linear truth; sufficient delay; observed windows spanning the true predictive space.

**Boundary.** The learner does not infer its model-class and coverage assumptions from a fit.

**Code link.** `checks/observable_reference.py`, `learn_delay`, lines 107–109. Autonomous finite example only.

\newpage
# Controlled stochastic realization
Propositions 26–37. Related finite suite: `checks/controlled_stochastic_checks.py`.

\Needspace{9\baselineskip}
## P26. Finite instrument closure

**Location and role.** Section 27, source lines 1159–1225. Construction. Principal dependencies: P8.

**Requires.** Known nonnegative finite instrument; all initial beliefs; exact mass row.

**Boundary.** A known-model completion is not an observable-data learner.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P27. Minimal finite behavior realization

**Location and role.** Section 28, source lines 1231–1264. Construction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Causal nonnegative finite-alphabet behavior; finite full history/test rank.

**Boundary.** Minimality is within linear realizations of the declared behavior.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P28. Observable table reconstruction

**Location and role.** Section 29, source lines 1270–1300. Construction. Principal dependencies: P27.

**Requires.** Known rank upper bound; invertible matching core; exact shifted tables and initial tests.

**Boundary.** Finite invertibility alone supplies only a rank lower bound.

**Code link.** `checks/stochastic_reference.py`, `fit_core`, lines 109–145. Population-table reconstruction with declared full-rank coverage.

\Needspace{9\baselineskip}
## P29. Canonical probability cone

**Location and role.** Section 30, source lines 1308–1334. Existence. Principal dependencies: P27, P28.

**Requires.** Canonical finite behavior space and all future tests.

**Boundary.** An all-test cone is not automatically finitely describable.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P30. Positive packet decomposition and its boundary

**Location and role.** Section 31, source lines 1342–1358. Criterion. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Complete cone-preserving packet maps; strictly positive mass functional.

**Boundary.** Signed Fourier or Haar details need not be probability components.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P31. Missing-intervention nonidentifiability

**Location and role.** Section 32, source lines 1372–1376. Obstruction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** At least two possible interventions with a missing action.

**Boundary.** No amount of data restricted to one action identifies an unobserved action.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P32. Finite-table rank separation and subspace stability

**Location and role.** Section 33, source lines 1388–1426. Bound. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** True finite-table rank; known perturbation budget; singular gap above twice that budget.

**Boundary.** Does not exclude true directions absent from the selected table.

**Code link.** `checks/stochastic_reference.py`, `finite_subspace_report`, lines 148–165. Finite matrix singular-subspace report.

\Needspace{9\baselineskip}
## P33. Noisy core-block realization

**Location and role.** Section 34, source lines 1434–1477. Bound. Principal dependencies: P28.

**Requires.** Fixed square invertible core and stated operator/table perturbation budgets.

**Boundary.** Good core inversion is not global positivity certification.

**Code link.** `checks/stochastic_reference.py`, `noisy_core_bound`, lines 168–186. Fixed-core perturbation calculation.

\Needspace{9\baselineskip}
## P34. Normalization-aware filtering stability

**Location and role.** Section 35, source lines 1483–1523. Bound. Principal dependencies: P18.

**Requires.** Common declared norm; bounded true states; positive likelihood margin.

**Boundary.** Rare-event conditioning can amplify a small unnormalized error.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P35. Reset-experiment probability certificate

**Location and role.** Section 36, source lines 1531–1555. Confidence. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** A prospectively fixed list of experiments; independent resets per experiment; known reset law.

**Boundary.** Not a guarantee for one dependent stream or post-selected experiments.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P36. Exact normalized closure defect

**Location and role.** Section 37, source lines 1563–1593. Identity. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Mass-preserving summary; nonnegative instrument; two positive branch likelihoods.

**Boundary.** Posterior agreement can hide incorrect likelihoods.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P37. Conditional observation-based stochastic completion

**Location and role.** Section 39, source lines 1687–1702. Integration. Principal dependencies: P27, P28, P29, P30, P32, P33, P34, P35.

**Requires.** Full rank coverage; exact population core; separate perturbation and likelihood assumptions.

**Boundary.** No global fitted cone follows from the spectral estimate alone.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\newpage
# Probability-domain certificates
Propositions 38–49. Related finite suite: `checks/certified_domain_checks.py`.

\Needspace{9\baselineskip}
## P38. Test-cone hierarchy and a finite stopping certificate

**Location and role.** Section 42, source lines 1750–1772. Criterion. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Exact mass law; finite symbol family; all words through each depth.

**Boundary.** A finite stopping equality is sufficient, not guaranteed to occur.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P39. Finite positive-lift certificate

**Location and role.** Section 43, source lines 1778–1812. Certificate. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Rational/full-rank normalized generators; nonnegative lifts; initial weights; exact intertwining and mass.

**Boundary.** Certifies the supplied model, not the generating process.

**Code link.** `checks/cone_reference.py`, `verify_certificate`, lines 42–89. Exact supplied finite-generator witness replay.

\Needspace{9\baselineskip}
## P40. Robust finite-domain certificate

**Location and role.** Section 44, source lines 1818–1851. Certificate. Principal dependencies: P39.

**Requires.** One common domain for every complete uncertainty-family vertex; exact mass constraints.

**Boundary.** Independent entry boxes can discard essential uncertainty correlations.

**Code link.** `checks/cone_reference.py`, `verify_certificate`, lines 42–89. Vertex witnesses replayed separately in the related suite.

\Needspace{9\baselineskip}
## P41. Certified correction and its error budget

**Location and role.** Section 45, source lines 1857–1882. Bound. Principal dependencies: P39.

**Requires.** Fixed generator matrix; feasible correction; separately justified error budgets.

**Boundary.** Existence of one valid fit does not show the true model preserves that domain.

**Code link.** `checks/cone_reference.py`, `minimum_mixture_repair`, lines 154–176. Explicit simplicial mixture sector, not general convex fitting.

\Needspace{9\baselineskip}
## P42. Instrument contraction before normalization

**Location and role.** Section 46, source lines 1905–1938. Bound. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Proper cone; strictly positive mass; cone-preserving normalized instrument.

**Boundary.** Base norm is not an arbitrary Euclidean coefficient norm.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P43. Observation-tree total-variation bound

**Location and role.** Section 47, source lines 1949–1975. Bound. Principal dependencies: P42.

**Requires.** Two models valid on one domain; common policy; summed instrument-error budgets.

**Boundary.** Full-law bound grows with horizon and need not remain informative.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P44. Sharp event-probability dependence of conditioning

**Location and role.** Section 48, source lines 1979–2006. Bound. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Two probability laws; positive evidence in both; unconditional TV bound.

**Boundary.** Conditioning costs inverse event probability.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P45. Rational finite-certificate search

**Location and role.** Section 49, source lines 2010–2016. Search. Principal dependencies: P39.

**Requires.** Rational inputs and existence of a rational finite-generator certificate.

**Boundary.** Semidecision guarantee is not an efficient complete implemented search.

**Code link.** `checks/cone_reference.py`, `search_interval`, lines 105–141. Bounded two-coordinate interval search, not the general enumerator.

\Needspace{9\baselineskip}
## P46. A rational rank-three model with no polyhedral probability-domain certificate

**Location and role.** Section 51, source lines 2052–2101. Obstruction. Principal dependencies: P38.

**Requires.** Declared rational rotation/probe model; closed convex invariant domain containing its initial state.

**Boundary.** Rules out polyhedral domains here, not all finite certificates.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P47. Polyhedral approximation of the rotation model

**Location and role.** Section 52, source lines 2109–2144. Bound. Principal dependencies: P39, P43, P46.

**Requires.** Attenuated rotation and sufficient polygon size; common Lorentz comparison domain.

**Boundary.** Damping changes the model and its observation law.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P48. Sequential confidence accounting for certified proposals

**Location and role.** Section 53, source lines 2150–2164. Confidence. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Conditionally covered successive sets with a summable failure budget.

**Boundary.** Does not establish resets, rank or dictionary validity.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P49. Conditional learning with an all-horizon probability certificate

**Location and role.** Section 54, source lines 2170–2183. Integration. Principal dependencies: P37, P39, P40, P43, P44.

**Requires.** Declared identification model; a covering uncertainty set; robust witness for all members.

**Boundary.** A nominal witness alone establishes only internal validity.

**Code link.** `checks/cone_reference.py`, `verify_certificate`, lines 42–89. Deterministic witness portion; statistical assumptions are external.

\newpage
# Curved domains and continuous observations
Propositions 50–61. Related finite suite: `checks/curved_continuous_checks.py`.

\Needspace{9\baselineskip}
## P50. Matrix-embedding probability certificate

**Location and role.** Section 56, source lines 2209–2246. Certificate. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Injective symmetric-matrix embedding; strict interior witness; positive congruences; exact mass.

**Boundary.** Matrix embedding and positive lift are different constructions.

**Code link.** `checks/continuous_reference.py`, `verify_certificate`, lines 135–181. Supplied symmetric-matrix/congruence witness sector.

\Needspace{9\baselineskip}
## P51. Exact rational matrix witness for the rotation model

**Location and role.** Section 57, source lines 2258–2300. Certificate. Principal dependencies: P46, P50.

**Requires.** The exact rational disk model and its explicit matrix-unit witnesses.

**Boundary.** No attenuation or quantum-physical interpretation is involved.

**Code link.** `checks/continuous_reference.py`, `verify_certificate`, lines 135–181. Exact two-by-two matrix embedding example.

\Needspace{9\baselineskip}
## P52. Continuous-observation instrument semantics

**Location and role.** Section 58, source lines 2308–2338. Semantics. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Standard Borel observations; common probability reference measure; integrable positive operator density.

**Boundary.** Point densities are version dependent; zero branches have no model-determined posterior.

**Code link.** `checks/continuous_reference.py`, `VerifiedInstrument`, lines 114–132. Finite polynomial reference class only.

\Needspace{9\baselineskip}
## P53. Polynomial Gram certificate for interval observations

**Location and role.** Section 59, source lines 2346–2388. Certificate. Principal dependencies: P50, P52.

**Requires.** Fixed embedding; positive polynomial Gram witness; exact coefficients and integrated mass.

**Boundary.** A sufficient certificate, not completeness for all positive maps.

**Code link.** `checks/continuous_reference.py`, `verify_certificate`, lines 135–181. Sufficient polynomial positivity certificate replay.

\Needspace{9\baselineskip}
## P54. Conditional finite-moment identification

**Location and role.** Section 60, source lines 2403–2448. Construction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Correct finite predictive dimension and degree; invertible complete event core; exact moment tables.

**Boundary.** Rank and degree are supplied assumptions, not inferred from an inverse.

**Code link.** `checks/continuous_reference.py`, `fit_population_moments`, lines 184–210. Exact event/moment tables with supplied rank and degree.

\Needspace{9\baselineskip}
## P55. A valid continuous counterexample to finite-moment identification

**Location and role.** Section 61, source lines 2460–2479. Obstruction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Uniform reference measure; declared two polynomial densities with matching low moments.

**Boundary.** Moment agreement and validity do not identify the entire density.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P56. Exact bin coarsening and its posterior

**Location and role.** Section 62, source lines 2483–2500. Identity. Principal dependencies: P52.

**Requires.** Exact cell integration; a measurable partition; bin-measurable policy.

**Boundary.** Does not preserve a policy responding to within-bin values.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P57. Exact covariance correction for an averaged congruence

**Location and role.** Section 63, source lines 2506–2522. Identity. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Square-integrable matrix function; a probability averaging measure.

**Boundary.** Average congruence differs from congruence of the average.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P58. Positive cell-average approximation

**Location and role.** Section 64, source lines 2534–2567. Bound. Principal dependencies: P52, P56.

**Requires.** Finite positive-measure cells; Lipschitz density in the base norm.

**Boundary.** This is a declared density approximation, not exact continuous-law equality.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P59. Continuous-record total-variation bound

**Location and role.** Section 65, source lines 2587–2624. Bound. Principal dependencies: P42, P52.

**Requires.** Common cone, mass and reference measure; common policy; integrated error budgets.

**Boundary.** No uniform posterior contraction is supplied.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P60. Exact recognition of a fixed certified template

**Location and role.** Section 67, source lines 2753–2770. Construction. Principal dependencies: P53.

**Requires.** A fixed certified template; coefficient intertwining; invertible alignment.

**Boundary.** Template recognition is not domain discovery.

**Code link.** `checks/continuous_reference.py`, `recognize_template`, lines 213–236. Fixed-template recognition, not geometry discovery.

\Needspace{9\baselineskip}
## P61. Conditional continuous realization with a finite domain certificate

**Location and role.** Section 68, source lines 2778–2786. Integration. Principal dependencies: P52, P53, P54, P56, P58, P59, P60.

**Requires.** Correct continuous class and event core; an independent exact domain witness.

**Boundary.** No unmodeled measurement error or unknown-degree inference is covered.

**Code link.** `checks/continuous_reference.py`, `fit_population_moments`, lines 184–210. Worked continuous polynomial sector only.

\newpage
# Discovery, approximation and evidence
Propositions 62–70. Related finite suite: `checks/discovery_evidence_checks.py`.

\Needspace{9\baselineskip}
## P62. Oriented quadratic probability certificate

**Location and role.** Section 70, source lines 2806–2858. Certificate. Principal dependencies: P52.

**Requires.** Positive definite ellipsoidal metric; oriented quadratic and polynomial positivity witnesses.

**Boundary.** Preserving a double cone without mass orientation is insufficient.

**Code link.** `checks/quadratic_reference.py`, `verify_quadratic`, lines 108–130. Exact oriented quadratic witness.

\Needspace{9\baselineskip}
## P63. Conditional operator-only ellipsoid discovery

**Location and role.** Section 71, source lines 2864–2894. Search. Principal dependencies: P62.

**Requires.** Suitable mass-preserving ratio; unique invariant-form direction; nonzero rank-one image scale.

**Boundary.** Every geometry proposal still requires full-family verification.

**Code link.** `checks/quadratic_reference.py`, `discover_quadratic`, lines 151–197. Restricted invariant-form/rank-one-image discovery.

\Needspace{9\baselineskip}
## P64. Valid positive polynomial approximation

**Location and role.** Section 72, source lines 2928–2997. Bound. Principal dependencies: P59.

**Requires.** A valid Lipschitz density on a common cone; doubly stochastic positive kernel.

**Boundary.** Avoids an exact-degree hypothesis but still assumes regularity and a domain.

**Code link.** `checks/sequential_reference.py`, `positive_coefficients`, lines 30–34. Positive approximation in a finite symbolic example.

\Needspace{9\baselineskip}
## P65. Certified coefficient error and approximation bias

**Location and role.** Section 73, source lines 3027–3062. Bound. Principal dependencies: P64.

**Requires.** Positive estimated Bernstein coefficients; exact integrated mass; covered coefficient errors.

**Boundary.** Increasing polynomial degree does not automatically reduce estimation error.

**Code link.** `checks/sequential_reference.py`, `reconstruct_bernstein`, lines 37–40. Finite coefficient reconstruction; no unknown-basis learner.

\Needspace{9\baselineskip}
## P66. Time-uniform predictable-residual certificate

**Location and role.** Section 74, source lines 3068–3105. Confidence. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Prospectively registered predictable bounded tests and a summable budget.

**Boundary.** Nonrejection is not an upper error or correctness guarantee.

**Code link.** `checks/sequential_reference.py`, `anytime_radius`, lines 43–47. Declared elementary time-uniform radius.

\Needspace{9\baselineskip}
## P67. Covered adaptive-action evidence

**Location and role.** Section 75, source lines 3111–3129. Confidence. Principal dependencies: P66.

**Requires.** Known predictable randomized actions with positive coverage.

**Boundary.** Estimates contextual action means, not unobserved-policy long-run distributions.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P68. Sequential evidence gives a lower error certificate

**Location and role.** Section 76, source lines 3135–3156. Bound. Principal dependencies: P66.

**Requires.** Actual common-history observation laws and registered tests.

**Boundary.** A lower discrepancy certificate cannot be used as an upper accuracy bound.

**Code link.** `checks/sequential_reference.py`, `dependent_example`, lines 50–69. One seeded conditional-mismatch illustration.

\Needspace{9\baselineskip}
## P69. Observation-law error without a shared state space

**Location and role.** Section 77, source lines 3170–3194. Bound. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Common observation/action space and policy; conditional TV discrepancies on true histories.

**Boundary.** Allows different internal state spaces but still needs true discrepancy control.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P70. Separate structural acceptance, approximation control and sequential rejection

**Location and role.** Section 78, source lines 3200–3210. Integration. Principal dependencies: P62, P63, P64, P65, P66, P67, P68, P69.

**Requires.** Separate structural, approximation and sequential-evidence assumptions.

**Boundary.** Acceptance, accuracy and statistical nonrejection are not equivalent.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\newpage
# Robust curved certificates
Propositions 71–79. Related finite suite: `checks/robust_curved_checks.py`.

\Needspace{9\baselineskip}
## P71. Robust oriented margin

**Location and role.** Section 80, source lines 3232–3267. Certificate. Principal dependencies: P52.

**Requires.** Common transformed domain; uniform oriented margin and output-error bounds; exact mass.

**Boundary.** Margins and uncertainty must be expressed in the same coordinates.

**Code link.** `checks/robust_reference.py`, `replay_certificate`, lines 217–251. Uniform margin certificate and uncertainty-budget check.

\Needspace{9\baselineskip}
## P72. Boundary fragility under mass preserving perturbations

**Location and role.** Section 81, source lines 3271–3283. Obstruction. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** At least one spatial coordinate; a cone-positive map with a boundary image.

**Boundary.** Mass-only dimension zero is explicitly excluded in 0.9.0.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

**Correction.** The mass-only case has no nonzero mass-preserving perturbation. The added dimension hypothesis excludes that case. The inherited exact regression checks cover both sides of this boundary.

\Needspace{9\baselineskip}
## P73. Interior repair with an explicit error budget

**Location and role.** Section 82, source lines 3292–3340. Bound. Principal dependencies: P59, P71.

**Requires.** A known valid reference; center-reset mixture; stated discrepancy and mass conditions.

**Boundary.** The repair changes the model; its uncertainty tube need not contain the original truth.

**Code link.** `checks/robust_reference.py`, `make_certificate`, lines 197–214. Explicit center-reset repair witness construction.

\Needspace{9\baselineskip}
## P74. A posteriori proposal error

**Location and role.** Section 83, source lines 3346–3405. Bound. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** A true normalized invariant metric; a separated linear system; covered proposal perturbations.

**Boundary.** A small numerical residual alone is not acceptance or coverage.

**Code link.** `checks/robust_reference.py`, `propose_geometry`, lines 152–194. Numerical proposal only; not the theorem's unknown true-metric assumptions.

\Needspace{9\baselineskip}
## P75. Rational semicircle and Bernstein certificate

**Location and role.** Section 84, source lines 3411–3444. Certificate. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Three-coordinate rational polynomial family; both boundary charts; complete subdivision.

**Boundary.** A negative Bernstein coefficient alone is not a counterexample.

**Code link.** `checks/robust_reference.py`, `replay_polynomial`, lines 117–139. Exact complete tensor-Bernstein subdivision replay.

\Needspace{9\baselineskip}
## P76. Coefficient boxes and convex uncertainty

**Location and role.** Section 85, source lines 3450–3475. Certificate. Principal dependencies: P71.

**Requires.** Coefficient boxes in declared Lorentz coordinates; exact mass affine constraints.

**Boundary.** Jointly optimizing unknown geometry and operators is not asserted convex.

**Code link.** `checks/robust_reference.py`, `replay_certificate`, lines 217–251. Coefficient-box inclusion in declared coordinates.

\Needspace{9\baselineskip}
## P77. Conditional search for strict rational curved certificates

**Location and role.** Section 86, source lines 3481–3487. Search. Principal dependencies: P75, P76.

**Requires.** A real transform with strictly interior initial states and a common strict margin.

**Boundary.** Conditional existence of rational witnesses is not an implemented general optimizer.

**Code link.** `checks/robust_reference.py`, `make_certificate`, lines 197–214. Finite candidate construction; no complete general search implemented.

\Needspace{9\baselineskip}
## P78. Data-selected geometry with honest coverage

**Location and role.** Section 87, source lines 3493–3507. Confidence. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** One covered fixed-coordinate operator/initial-state set; verifier quantifies over its entire set.

**Boundary.** Data-selected geometry must transport uncertainty, not just the fitted center.

**Code link.** `checks/robust_reference.py`, `replay_certificate`, lines 217–251. Deterministic set certificate only, not upstream statistical coverage.

\Needspace{9\baselineskip}
## P79. Certified repair with a retained comparison budget

**Location and role.** Section 89, source lines 3564–3595. Integration. Principal dependencies: P59, P71, P73, P75, P76.

**Requires.** Worked deterministic perturbed family; nominal and comparison-domain witnesses.

**Boundary.** The original repair's bound is trivial at horizon eight.

**Code link.** `checks/robust_reference.py`, `replay_certificate`, lines 217–251. Nominal and comparison-domain witnesses for one deterministic example.

\newpage
# Data-supported domains
Propositions 80–87. Related finite suite: `checks/data_supported_checks.py`.

\Needspace{9\baselineskip}
## P80. Convex repair bracketing

**Location and role.** Section 91, source lines 3617–3636. Bound. Principal dependencies: P75, P79.

**Requires.** Fixed geometry, reset path and requested margin; exact separator and upper witness.

**Boundary.** Brackets this repair path, not optimal geometry or all repair methods.

**Code link.** `checks/robust_reference.py`, `replay_certificate`, lines 217–251. Upper certificate; exact lower separator is in the related suite.

\Needspace{9\baselineskip}
## P81. Time-uniform regression confidence

**Location and role.** Section 92, source lines 3686–3743. Confidence. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Predictable regressors; correct fixed conditional mean; positive sub-Gaussian scale; parameter bound.

**Boundary.** Estimated hidden regressors and response-dependent features need new analysis.

**Code link.** `checks/data_certificate_reference.py`, `radius`, lines 50–54. Scalar specialization only, not general vector online regression.

\Needspace{9\baselineskip}
## P82. Sequential observable-moment operator sets

**Location and role.** Section 93, source lines 3749–3786. Confidence. Principal dependencies: P81.

**Requires.** Exact accessible predictive state; correct finite basis; known invertible moment matrix.

**Boundary.** General multirow theorem is not a hidden-state discovery algorithm.

**Code link.** `checks/data_certificate_reference.py`, `sufficient_statistics`, lines 59–71. Observable scalar specialization; general matrix learner not implemented.

\Needspace{9\baselineskip}
## P83. Structured curved-domain certificate

**Location and role.** Section 94, source lines 3794–3852. Certificate. Principal dependencies: No principal internal prerequisite recorded.

**Requires.** Specified moment feature curve; known reference moments; two-parameter conditional family.

**Boundary.** Geometry, dictionary and family are supplied, while parameters can be learned.

**Code link.** `checks/data_certificate_reference.py`, `probability_row`, lines 30–33. Fixed two-parameter family and five-node measure.

\Needspace{9\baselineskip}
## P84. Exact rational outer confidence intervals

**Location and role.** Section 95, source lines 3858–3892. Confidence. Principal dependencies: P81.

**Requires.** Exact observed node path; declared measure and prior bounds; rational outward rounding.

**Boundary.** Replay cannot authenticate data or prove model assumptions from one path.

**Code link.** `checks/data_certificate_reference.py`, `confidence_box`, lines 73–86. Exact rational scalar intervals and outward rounding.

\Needspace{9\baselineskip}
## P85. Parameter-to-law error without a state-estimation term

**Location and role.** Section 96, source lines 3922–3956. Bound. Principal dependencies: P69, P83.

**Requires.** Covered parameter distances; common measure and common observed history.

**Boundary.** Likelihood error remains even when normalized posterior states agree.

**Code link.** `checks/data_certificate_reference.py`, `make_certificate`, lines 91–112. Finite parameter rectangle and declared measure constants.

\Needspace{9\baselineskip}
## P86. Uniform marginal and rolling-window stability

**Location and role.** Section 97, source lines 3970–3990. Bound. Principal dependencies: P69.

**Requires.** Markov kernels; positive common minorization; uniform one-step discrepancy.

**Boundary.** Uniform marginal control is not uniform complete-record control.

**Evidence.** Written proof. The related suite contains finite block-level examples; no dedicated general algorithm is claimed for this result.

\Needspace{9\baselineskip}
## P87. Observable structured learning with a covered domain

**Location and role.** Section 98, source lines 4007–4013. Integration. Principal dependencies: P81, P83, P84, P85, P86.

**Requires.** Correct observable family; predictable protocol; full confidence rectangle and valid chosen center.

**Boundary.** Does not transfer statistical coverage to the unrelated repaired-operator example.

**Code link.** `checks/data_certificate_reference.py`, `replay_certificate`, lines 114–128. Data fingerprint, statistics, radii and whole-rectangle validity; assumptions not inferred.

