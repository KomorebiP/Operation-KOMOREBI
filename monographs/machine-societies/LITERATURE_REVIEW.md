# Final targeted source review

Checked 15 October 2026. This is an implication and attribution check for the central proof review, not a novelty or citation-impact survey. No external PDF is redistributed. The prior reference review remains in the original source release.

## Finite convex duality

- Primary source: Stephen Boyd and Lieven Vandenberghe, *Convex Optimization*, author lecture slides, summer 2023 update linked from https://web.stanford.edu/~boyd/cvxbook/ . Text consulted: https://web.stanford.edu/~boyd/cvxbook/bv_cvxslides.pdf .
- Exact locators: slides 5.13–5.14, PDF pages 167–168, on the affine refinement of Slater's condition and inequality-form LP duality. The material states the needed feasible-LP equality and displays the dual.
- Application: Theorem 19.1 reduces its compact monitor polytope to a finite vertex matrix. The primal maximizes the minimum column payoff; its LP dual minimizes the maximum row payoff over deviation mixtures. Both are feasible and finite. No strict interior is needed at cap zero because the constraints are affine. The reduction and attainment are checked in the claim card.
- Classification: application of classical finite LP duality. No novelty claim.
- Retrieval limit: the full book PDF timed out or returned an internal fetch error. The authors' slides were successfully retrieved and checked instead. This review does not claim a successful fresh download of the book itself.

## Knowledge-state construction

- Primary source: K. Chatterjee, L. Doyen, T. A. Henzinger and J.-F. Raskin, *Algorithms for Omega-Regular Games with Imperfect Information*, LMCS 3(3:4), 2007, DOI https://doi.org/10.2168/LMCS-3(3:4)2007 . Published full text: https://lmcs.episciences.org/1094/pdf .
- Exact locators: Section 3.1, Lemma 3.1, Theorem 3.4, printed pages 7–9. These define the nonempty successor union intersected with an observation class and prove the deterministic sure-winning reduction.
- Dictionary: the source's knowledge set is the manuscript's B; its action is the implemented profile u; its observation class is a fibre of h. The manuscript additionally intersects statewise admissibility and gives direct safety and certified-completion proofs.
- Boundary: the source starts at a known state and uses observation objectives. It is cited as a foundation, not treated as an automatic proof for an arbitrary initial possibility set, hidden safety label, private-history controller, or almost-sure objective. Those manuscript-specific obligations are checked directly.
- Classification: established construction applied to the stated finite contract. An unrelated journal page encountered during lookup was rejected.

## Pairwise privacy and transcript composition

- Primary source: C. Dwork and A. Roth, *The Algorithmic Foundations of Differential Privacy*, Foundations and Trends in Theoretical Computer Science 9(3–4), 2014, DOI https://doi.org/10.1561/0400000042 . Author-hosted full text: https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf .
- Exact locators: Definition 2.4, Proposition 2.1, and Appendix B, Theorem B.1 and Corollary B.2. The first defines neighboring-input privacy; the others give common postprocessing and sequential conditional composition.
- Dictionary: set delta=0 and lambda=exp(epsilon), and restrict to the declared pair of neighboring inputs. Symmetry of that relation gives the two directional inequalities. The manuscript's finite-prefix product proof allows the separately stated factors lambda_t.
- Boundary: arbitrary compliance and misconduct inputs need not be neighbors. Unconditional marginal privacy does not imply joint-transcript privacy. The sharp sanction envelope is proved directly in Theorem 43.3, rather than attributed as a new general privacy theorem.
- Classification: known foundations with a direct finite testing calculation. No global novelty claim.

## Other dependencies and limits

The required finite Hall implication is proved within Theorem 41.1 and reused for Proposition 43.6, so the appeal result has no unchecked matching-theorem leaf. The inspection equilibrium and guarded-handover proof are direct arguments. Historical inspection-game, shutdown-incentive and runtime-assurance references supply context; their broader conclusions are not used as premises of the reviewed implications. Those citations retain their previous targeted review status rather than being represented as a new exhaustive bibliography audit.
