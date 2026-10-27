# v0.9.0 — intrinsic exchange and lifting

Base: exact v0.8.0 source/PDF/ZIP identified by `audit/base_sha256.json`. No Git ancestry is asserted for the standalone package.

Target: construct an arithmetic transformation/resolution comparison with an intrinsic nonzero residual, rather than an imposed scalar, and distinguish valid repairs from loss of necessary information.

## Decisive results

K53–K57 identify the natural kernel/invariant residual, compute its transition law, prove a sharp n+h lifting criterion under fixed integral constraints, and apply it to intertwiners. A norm-quotient cyclic lattice demonstrates nonzero finite invariants with zero inverse limit.

K58 proves the expected fully derived defect vanishes for perfect coefficient change. This rules out an overbroad claim of failure over a regular integral coefficient base.

K59 uses A=I+pJ on (Z/p²)^d, p odd, J invertible mod p. The canonical derived invariant/base-change cone has k^d cohomology in every integer degree. K60 separately proves that no lift of this action satisfies the group relation modulo p³.

K61 uses transitivity and two perfect common-base comparisons to prove exact exchange for coefficient-lifted inputs. Its contrapositive is a necessary obstruction to lifting; its converse is open.

## Evidence

Complete proofs in `proofs/intrinsic_arithmetic_exchange.tex`. Source dictionary in `audit/source_checks.md`. Four exact finite suites rerun successfully; `checks/all_runs.json` records the real commands, hashes, durations, and exits. Full-bar tests independently implement the cyclic cochain calculation in low degrees. No bounded result is promoted to an infinite-degree proof.

## Boundaries

Ordinary invariants are nonexact. The exact counterexample lives in unbounded derived categories and uses a nonperfect coefficient map. Quotienting its residual loses the coefficient unit. Integral actions supplied in advance belong to the positive exact-comparison regime. A vector-lifting obstruction and an action-lifting obstruction are not identical.

## Handoff

Next route: choose a precise finite-group deformation problem and establish a sufficient tower-lifting criterion using its actual relation/cohomology obstruction classes. Compare these with the beta cone without assuming equivalence. Keep the nonzero-cone necessary condition as proved and the zero-cone converse as unproved. For arithmetic applications, specify the relevant finite/profinite action and topology before transfer. K17, K18, and independent review remain outstanding.
