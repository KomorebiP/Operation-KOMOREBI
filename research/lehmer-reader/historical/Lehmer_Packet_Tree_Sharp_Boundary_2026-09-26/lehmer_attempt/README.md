# Lehmer packet-tree continuation

The attempt does **not** solve Lehmer's conjecture.

Read `RESEARCH_NOTE.md` for the complete argument. The principal new result of
this attempt is the exact first mixed-sign shell at every dyadic depth:

    N_k = (20*4^k + 2^(k+1) + gamma_k)/7
    gamma_k = 7, 1, 6 for k = 1, 2, 0 modulo 3.

The note also proves the obstruction to a sign certificate made solely from
sector-preserving corrections. This already applies at prime 7.

Contents:

- `RESEARCH_NOTE.md`: definitions, proofs, explicit witnesses, remaining gap.
- `AUDIT.md`: self-review and dependency status.
- `STATUS.json`: target and route handoff.
- `checks/verify_packet_tree.py`: self-contained exact verifier.
- `checks/explore_bound.py`: exact exploratory witness search, now standard library only.
- `computations/run001/`: completed run, raw output, results and provenance manifest.
- `contract.json`: finite computation contract.
- `BASE.json`: parent checkpoint identity and hash.
- `prior/Lehmer_null_packet_resolution_2026-09-26.zip`: unmodified parent archive.
- `FAILURES.md`: mathematical route failures and environment failures.

Reproduce using Python 3.12 or later, with no additional dependencies:

```sh
python3 checks/verify_packet_tree.py evidence/reproduced_results.json
```

The stored run used CPython 3.12.14 and completed in approximately 4.43 seconds.
The completed provenance manifest passed the mathbox validator with input and
output hash checks. Running the script again is not needed to read the proofs.

No Lean verification, all-prime nonvanishing result, or historical-priority
claim is included. The exact lower-bound proof and the symbolic witness
families establish the all-depth geometric theorem. A bounded test alone does
not establish that theorem or Lehmer's conjecture.
