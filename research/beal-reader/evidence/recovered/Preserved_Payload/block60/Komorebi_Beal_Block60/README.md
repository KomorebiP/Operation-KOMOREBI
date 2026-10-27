# Komorebi Beal research — Block 60
## Diagonal periods, a complete local torsion test, and surviving local families

Version 6.0.0. Execution predecessor: the exact original Block 59 ZIP.

The other two marked Jacobian periods have now been computed modulo principal
units. For a primitive local triple A^3+B^5=C^7 at a variable prime q, write
C=q^k C0 and let F=K_v, K=Q(sqrt5), Q=#kappa(v). Under the preserved actual
model/uniformization inputs, full natural J^nu[49] is F-rational if and only if

    49 | Q-1,   7 | k,
    phi is a 49th power in kappa(v)^*,
    3*5^9*A/C0^35 is a 49th power in kappa(v)^*.

This is a local torsion criterion, not a criterion for the actual global beta.
At a depth-two beta place it is a necessary condition; the inherited stronger
multiplicity condition remains v7(k)=1.

The four primes {197,883,1373,1667} all survive. At each, explicit primitive
q-adic solutions satisfy the equation and the complete local 49-torsion test.
They are NOT global integer solutions or global reducible representations.
No new prime exclusion, full depth-two theorem, or Beal solution is claimed.

Read work60/REPORT.md, TARGET_CONTRACT.md and PROOF_BOUNDARY.md. Proofs and the
local-to-global boundary are in work60/notes/. Run using Python 3.10+:

    python verify.py --replay-predecessors --report ../Block60_Replay.json

The standard library suffices. No new Lean compilation or independent
mathematical review was performed. The second implementation is independent
finite arithmetic, not an independent mathematical referee.
