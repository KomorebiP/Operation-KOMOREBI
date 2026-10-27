# Block 56 theorem index

| ID | Statement | Evidence and dependency |
|---|---|---|
| B56.1 | Actual good-Frobenius precision r=min(n,m+h), polynomial target and order divisibility | notes/FROBENIUS_PRECISION.md; G1-G3 |
| B56.2 | n>=3 implies 197 divides C | notes/FINITE_FROBENIUS_CERTIFICATE.md; G1-G3; complete finite certificate |
| B56.3 | n>=2 implies 491 divides C | same note; G1-G3; complete finite certificate |
| B56.4 | Good-prime character consequences and updated necessary divisors | notes/ARITHMETIC_CONSEQUENCES.md; earlier forced divisor only for the product statements |
| B56.5 | H(C) subset {97,293} forces n=1; H(C) subset {97,293,491} forces n<=2 | same note; G4 only for the remaining multiplicity consequence |
| B56.6 | Exact local 97/293 toric controls survive the ramified-local test | notes/LOCAL_SURVIVOR_BOUNDARY.md; explicit integer identities |

These are written conditional results and exact finite certificates, not
new Lean theorem declarations or an independent review of upstream geometry.
