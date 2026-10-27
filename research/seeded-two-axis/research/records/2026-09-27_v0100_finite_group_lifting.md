# v0.10.0 — Complete finite-group lifting criterion

## Base and target

Base is the supplied v0.9.0 checkpoint, identified by the three hashes in audit/base_sha256.json. No Git repository or .mathbox ledger was present. The target was a sufficient intrinsic condition for a specified representation tower, not merely another necessary exchange diagnostic. The executed scope fixes a finite source G, rank d, p, and the coefficient tower Z/p^n.

## Routes

1. **Classical one-step obstruction.** Construct c(g,h)=(A_g A_h A_gh^{-1}-I)/p^n. Associativity gives a normalized cocycle. Left corrections change it by delta b. This proves necessary and sufficient next-level lifting, affine H^1 ambiguity, and exact finite positive/negative certificates. Outcome: proved as written.
2. **Attempted sufficiency of derived-invariant exchange.** Add a central C2 acting by -I to the bad Cp action over Z/p². Derived invariants vanish before and after reduction while the Cp restriction remains nonliftable. Outcome: the broad converse is refuted.
3. **Averaging and full reconstruction.** Approximate action defects of depth m admit correction of depth m-e and improved defect 2m-2e, where e=v_p(|G|). For m>2e the iteration converges. Consequently extension to h=max(n+e,2e+1) is equivalent to a full integral lift preserving n. Outcome: proved as written, using a direct proof of an already-known ultrametric stability threshold.

The last route also gives controlled conjugacy and a finite catalogue of integral class sets. The cyclic Jacobian supplies a smaller finite certificate. An explicit Z_p-source action proves why the fixed finite quotient is not an innocuous hypothesis.

## Mathematical status

K62–K71, written proofs and authoring-session self-review. Standard H² deformation theory and known finite-group stability are attributed. No historical novelty or independently checked Lean proof.

## Tests and files

New proof: proofs/finite_group_lifting.tex.
New suite: checks/check_action_lifting.py.
Integrated audit: proofs/audit_v0100.tex.
Source reproduction: audit/integrate_v0100.py.
Five suites pass, with 367 exhaustively listed cyclic action inputs and 40,987 next-lift matrices; 330 averaging steps; eight cochain fixtures; explicit conjugacy and scope-boundary checks. All counts refer to declared bounded families. Infinite convergence follows from the separate valuation proof.

## Failed/superseded statement

The zero canonical derived-invariant comparison cone is not sufficient for integral liftability, even for a fixed finite group and finite free modules. The counterexample is retained. Current prose is corrected; earlier historical audit statements are preserved as history.

## Open continuation

Specify a continuous/profinite lifting problem and its local conditions. The known finite-group threshold is not uniform over growing p-parts, and a fixed-quotient failure need not be a profinite failure. A useful next route must address those distinctions. Independent mathematical review and Lean formalization remain open.
