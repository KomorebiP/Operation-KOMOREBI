# WR03–WR05 target contract

Base checkpoint: KS-v1.9.0-full-monograph-proofread. Exact source and accepted formal predecessor hashes are in records/BASE_CHECKPOINT.json. The authoritative printed statements and proofs are copied without modification in records/TARGET_WR03_WR05.tex.

Work over real complete Hilbert spaces H and Y with a bounded linear map T:H→Y and fixed datum r. The correction norm is the actual Hilbert norm. No finite-dimensional, separability, closed-range, or injectivity hypothesis may be added to count these groups complete. Every budget M is nonnegative, including zero.

WR03: attainment of beta(T,r,M)=inf{norm(r-T a):norm(a)≤M}; nonincreasing profile; convexity; for 0≤M1≤M2, 0≤beta(M1)-beta(M2)≤norm(T)(M2-M1); limit at infinity equals distance to the closure of the range; equality to that floor at finite budget iff its projected datum is attained within that budget; beta(M)=0 iff exact feasibility within that budget. Include closedness/convexity of the fixed-budget image as the bridge used in the proof.

WR04: for all M≥0, beta(T,r,M)=max{inner(r,z)-M norm(T* z):norm(z)≤1}. Prove both the universal inequality and existence of an attaining witness. Handle zero residual and zero budget. Derive the strict exclusion certificate.

WR05: same fixed source/target Hilbert spaces and same feasible ball, norm(T-S)≤eta, norm(r-s)≤delta, eta,delta≥0 imply abs(beta(T,r,M)-beta(S,s,M))≤delta+eta M. Include the nominal dual-witness lower certificate with that uncertainty allowance. No claim across changed protected kernels.

Done requires exact public theorem types, successful compiler runs with warnings as errors and autoImplicit disabled, axiom policy audit, positive boundary examples and meaningful compiler/policy rejection controls, independent mathematical/type review, and a fresh integrated replay. A compiled weaker lemma is partial progress only. Historical accepted sources/evidence remain unchanged.

Shared API: namespace KomorebiSpace.BudgetProfile. BudgetProfile.lean owns beta(T,r,M):ℝ, defined as Metric.infDist r (T '' Metric.closedBall 0 M), equivalent to the printed infimum for M≥0. It must supply exists_budget_minimizer and beta_le_residual for feasible a. BudgetProfileGeometry.lean imports BudgetProfile and owns the WR03 shape and Lipschitz clauses. BudgetDuality.lean imports BudgetProfile and owns WR04. BudgetRobustness.lean imports BudgetDuality and owns WR05. Coordinate exact signatures between owners before depending on them.

Routes: (A) use accepted WR01 bounded-approximation theorem to prove the fixed-budget image closed, then Hilbert projection; (B) derive support sharpness from the minimizing residual and the convex projection inequality; (C) compare candidate residuals on the identical ball for robustness. Boundary falsification/control route probes missing budget bounds, weakened feasibility and deleted uncertainty terms. These are jointly required pieces, with alternative compactness/variational mechanisms preserved if the first route fails.
