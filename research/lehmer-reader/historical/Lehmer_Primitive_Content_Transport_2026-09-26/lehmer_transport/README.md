# Lehmer content and transport continuation

Read `RESEARCH_NOTE.md` for the proofs and exact limitations.

The original conjecture remains unresolved. This block proves:

1. An exact refinement sequence for the permitted null-transfer spaces.
2. Conservation of every coordinate-gcd sector under homogeneous universal
   null corrections and their finite rational span.
3. The primitive decomposition
   R(n)=sum_{d^2|n} mu(d) chi_5(d) d^10 tau(n/d^2).
4. R(s^2) is nonzero for every positive integer s.
5. For odd primes p other than 5, R(p^(2m+1)) equals tau(p) times an odd integer.
6. R and tau have the same zero set. In particular, the prime-level obstruction
   has not been solved or assumed away.

Exact finite work constructs 22 more null polynomials, taking the stored family
to 36 through degree 28. It resolves the p=31 transfer defect at degree 22 and
stores a complete two-stage rational transport certificate.

Contents:

- `RESEARCH_NOTE.md`: full mathematical argument and source dependencies.
- `AUDIT.md`: self-review, evidence boundaries and remaining gap.
- `STATUS.json`: current claims and route handoff.
- `FAILURES.md`: failed proposals and source-access failure.
- `checks/exact_algebra.py`: exact sparse polynomials and rational linear algebra.
- `checks/packet_core.py`: packet and tau arithmetic from the parent checkpoint.
- `checks/verify_transport.py`: complete standard-library verifier.
- `computations/run001/`: validated provenance, exact results and certificates.
- `evidence/`: retained input polynomials and exploratory results.
- `prior/`: the unmodified parent archive, including its earlier ancestry.

Reproduce with Python 3.12 or later. No external package is required:

```sh
python3 checks/verify_transport.py evidence/reproduced
```

The recorded run completed successfully in approximately 12.4 seconds.
The Mathbox provenance validator passed with input and output hashes checked.
There is no Lean proof, independent-agent review, or historical-priority claim.
