# Development failures and nonclosures

1. The initial new primary run stopped at a wrongly untruncated matrix-valuation
   assertion. In O/7^j, zero has truncated valuation j, so a coefficient known
   divisible by7^(2n) must be checked against min(j,2n), not2n when j<2n.
   The assertion was corrected. This was a finite-check implementation error,
   not a counterexample to the integral matrix theorem. No output from the failed
   run was accepted.
2. The second run stopped at an incorrect expected count2304 for all units in O_F/49.
   The correct complete count is49^2-7^2=2352, equivalently49 images times48 residue
   torsion choices. The expectation was corrected and independently reproduced.
   The primitive coordinate images themselves were unchanged. The rejected initial
   source is retained as historical text in this directory's verification area.
3. The attempted direct pattern exclusion is not achieved. The current dataset
   supplies no actual joint word traces modulo343. All eight patterns remain,
   and the finite matrix family is nonempty for every declared local value.
4. An exploratory Massey-product/general obstruction route did not supply a theorem
   with the prescribed twist, coefficient field, ramification and local-period
   conditions. It contributes no claimed arithmetic conclusion.

The predecessor's default verifier passed cleanly. No fresh full historical-chain
run is claimed. Final verification must rebuild both scientific outputs and reject
altered identities and false exclusion flags before release.
