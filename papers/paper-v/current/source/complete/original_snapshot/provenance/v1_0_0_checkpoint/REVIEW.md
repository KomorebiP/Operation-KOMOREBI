# Paper V completion review, v1.0.0

Author: Komorebi P.

The actual full verifier returns exit 0 with lean_kernel_checked=true. It accepts 225 theorem targets and audits all 827 project-namespace declarations. All 133 previously checked targets remain. No proof placeholders, user axioms, unsafe declarations, or native proof shortcuts were introduced.

## Progress from the starting checkpoint

The manual manuscript ledger moved from 8 matching results and 12 incomplete results to 20 completed corrected scope rows. The statement ledger, principal-target map and machine-readable scope contract now agree. The verifier rejects incomplete rows or targets absent from the theorem inventory; it does not mechanically determine whether a PDF sentence matches a theorem.

Nine new modules add 92 targets: 81 additional proof statements and 11 identified adaptations from Paper IV. They cover interleaved Haar energy, true-adjoint packet reconstruction, measurable masks, literal antichain sums, finite optimization and operation counts, formal power-series products/powers, projective cyclic Smith actions, convergent z-transforms, and a faithful Laurent-matrix action on bilateral signals. PruningSums also proves that the positive gap is attained by a competing pruning.

## Why the final boundaries matter

The original paper's transform wording does not specify convergence. The checked replacement separates a universal time-domain FIR theorem from a numerical transform theorem whose weighted channel series converge. It constructs summability of the output from summability of the input channels.

For perfect reconstruction, matrices have finite Laurent-polynomial entries and act on arbitrary bilateral sequences. Matrix multiplication is proved to match bank composition. Applying a bank to individual channel impulses recovers every coefficient, which proves faithfulness and the necessity direction of the reconstruction criterion. The original-sample consequence has delay N*d. A separate transform bridge evaluates those Laurent entries wherever the input transforms converge.

The actual bottom-up solver stores child results, returns the same globally optimal selector as the specification, stops on ties, and has one comparison per internal node. Its operation count explicitly includes visits and cached child-value additions. The bound assumes node costs are supplied; it is not a runtime claim about Lean or an arbitrary cost function.

The formal series, projective quotient, measurable-mask and complex l2 constructions retain the scope stated in the ledger and correction supplement. No conjecture or reported numerical experiment is promoted to a theorem.

## Cumulative census

The census reproduces the I–IV mapped declaration counts from authoritative archives and counts the current V contract. It removes two shared I/II theorem names and eleven adapted IV proofs, yielding 1,443 mapped proof declarations. The five manuscripts contain 168 theorem-like records. Their different roles are explained in CUMULATIVE_COUNTS.md.

Papers I–IV were not freshly rebuilt in this census. Their previously completed build/audit status comes from their bundled release records. Paper V was freshly checked with the real compiler in this session.

## Deliverable status

The 31-page original manuscript remains byte-identical. The updated five-page supplement is authoritative for corrections and formalization scope. The original 33-test numerical companion suite was not rerun; the independent mathematical and verifier suites in this release all pass. Source patches, historical checkpoints, build/audit logs, hashes, census inputs and the runtime adapter disclosure are retained.
