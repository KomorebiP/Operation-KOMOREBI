# Beal research — Block 72
## Higher-precision natural periods and the required valuation coordinate

Version 7.2.0. The sole predecessor is the exact Block71 archive in predecessor/.
The work is conditional on the pinned actual geometry and representation inputs.
It does not close the eight bounded configurations or prove Beal.

The actual fixed-seven period comparison now holds at every precision 7^j with
1<=j<=7c-1, where c=v7(C)>=1. In particular, when c=1 it is valid through 7^6,
not only modulo7. The actual coefficient action is +/-R through this window.
The natural scalar extension has THREE local Kummer coordinates:

    kappa_j = 2*epsilon*w*X_j + Lambda_j(A,C0)*H_j + 7c*T_j,
    X_j=[phi], H_j=[3], T_j=[7], C=7^c*C0.

At j=2, put Q_A=(A^6-1)/7 mod49 and q0=(C0^6-1)/7 mod7. Then

    Lambda_2 = 47 + 38 Q_A + 14 Q_A^2 - 7 q0 mod49.

The valuation term 7c*T_j, invisible at level7, cannot be discarded at level49
when7 does not divide c. Whenever the actual global representation really is
triangular with characters chi and1 at precision7^j, the local valuation coordinate
W_j of its actual upper extension has truncated valuation min(j,1+v7(c)).
The inherited half-depth theorem guarantees that hypothesis for j<=floor(n/2)+1.
This statement does NOT manufacture a global mod49 Kummer lift at actual n=1.

All eight bounded patterns remain. Every one of the seven lifts of each retained
A mod49 class to A mod343 is locally compatible. With C0 mod49 allowed to vary,
there are28224 augmented pattern/A/C0 choices and7056 distinct local root controls.
These local controls are not global Frey representations or integer solutions.

Read work72/REPORT.md and the proof notes. Run from this directory:

    python -B verify.py --report ../Block72_Replay.json

This regenerates both new scientific JSONs and performs corruption tests. Use
--replay-predecessor to additionally run the immediate Block71 default verifier.
Neither is a fresh full historical-chain replay. No new Lean compilation or
external independent mathematical review is claimed.
