# Block 53 theorem index

| ID | Statement | Dependencies | Status/location |
|---|---|---|---|
| B53.1 | Exact local trace plus residual character separation identifies a=lambda,d=1 at full finite precision | Commutative local-ring algebra, explicit character hypotheses | Written proof, DIAGONAL_RIGIDITY section1 |
| B53.2 | N^2=0, upper in 7O, lower in 7^nO forces diagonal in 7^(floor(n/2)+1)O | Characteristic-zero DVR with uniformizer7 | Written proof, section2 |
| B53.3 | Actual eta_n=1 mod 7^(floor(n/2)+1) | H1--H5, B53.1--2, Cl(K)=1, C1 | Conditional arithmetic theorem, sections3--6 |
| B53.4 | Surviving eta_n=1+7^m theta_n, theta_n additive modulo 7^(n-m) | B53.3 and 2m>=n | Written corollary, section7 |
| B53.5 | 13 not dividing C forces actual n=1 | B53.3, H6 | Conditional arithmetic theorem, ARITHMETIC_CONSEQUENCES section 1 |
| B53.6 | 7^(2m) divides the twisted Jacobian order at every good place; n>=2 forces11*31|C | B53.3, H1--H3, C2 | Conditional arithmetic theorem, section 2 |
| B53.7 | At n=1, beta cannot ramify at both K-places over 71, including bad 13 | H3,H7 and compatible coefficient algebra | Written conditional corollary, section 4 |

Additional combined divisor for n>=2:
1566013238790 = 2*3*5*7*11*13*19*29*31*43*71 divides C.
Uses H1,H7,B53.5--6. It is necessary, not sufficient, and not a contradiction.

The exact finite scripts test the local algebra and arithmetic calculations.
They do not replace H1--H7, C1--C2, or the universal written proofs.
