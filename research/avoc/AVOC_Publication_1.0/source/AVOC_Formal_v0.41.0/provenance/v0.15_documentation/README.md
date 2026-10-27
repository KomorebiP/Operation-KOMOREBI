# AVOC Formal v0.15.0

**Author: Komorebi P.**

## Bayesian/model errors to certificate-safe policy guarantees

This release closes the serious audit's primitive-model-error-to-feasible-Q gap for an explicit finite-observation compatibility class. It does not assume a true Bellman-Q error as a primitive premise. Instead it derives that error from prior/channel errors, posterior encoding, reward mismatch, regularity of supplied continuation tables, and model Bellman residuals.

The average posterior theorem needs no positive evidence floor:

    sum_o p(o) ||b_o - c_o||_1 <= 2 J <= 2(alpha + beta).

This is an expectation guarantee, not a pointwise rare-observation guarantee. The finite observation comparison and exact metadata/guard preservation yield

    t_k = L_k chi_k + (2L_k + R_k)(alpha + beta)
    D_0 = 0
    D_(k+1) = D_k + epsilon + t_k + xi_k
    H_k = D_k + epsilon + t_k.

The complete deployed policy has

    0 <= regret_n <= sum_(k<n) [2(H_k + kappa_k) + tau_k],

while the inherited research controller preserves its dependency, certified-admission, queue and budget invariants.

Main theorem: `Komorebi.AVOC.Research.certified_bayesian_model_policy`.

## Recorded verification

- 55 new theorem/lemma declarations, 734 in the complete inventory.
- 75 non-audit modules and 12,402 non-audit Lean source lines.
- 76/76 fresh local compilation targets passed against the exact pinned dependency cache.
- 734/734 axiom reports, only `propext`, `Classical.choice`, `Quot.sound` where needed.
- 24/24 intended negative files substantively rejected.
- 68/68 inherited non-audit source modules unchanged from the frozen v0.14 release.
- Exact Python regression: 15,625 Bayesian comparisons and 15,625 posterior-codec comparisons, including zero-probability branches.

Counts include helpers and examples, not independent discoveries. The regression is independent finite implementation evidence, not Lean extraction or empirical LLM validation.

Read `FORMAL_THEORY.md`, `PROOF_BOUNDARY.md`, `GAP_LEDGER.md`, and `results/VERIFICATION_v0.15.0.md`. Start a new session from `CONTINUE_HERE.md`. Use `REPRODUCE.md` to rerun proof checks. The portable Lean runtime and external dependency caches are not included in this small release.
