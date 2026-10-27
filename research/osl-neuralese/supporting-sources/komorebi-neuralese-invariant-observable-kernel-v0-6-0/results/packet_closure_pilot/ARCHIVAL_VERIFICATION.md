# Archival verification of a retained invalid pilot

- Author: `Komorebi P.`
- Scientific status: `NOT_EVALUATED`
- Integrity/replay status: `PASS_WITH_RETAINED_ASSAY_INVALIDATION`

This document distinguishes integrity from scientific validity. The official
pilot executed all twelve runs but failed the frozen A15 assay contract, so its
completion flag is false and its full developmental claim is not evaluated.
No archival check can convert that status into a pass.

## Unchanged verifier outcome

The frozen package verifier was run unchanged with isolated flags. Its test
suite completed successfully:

```text
505 passed in 150.26s
```

It then stopped, as designed, at the first strict archival incompatibility:

```text
Archived deterministic contract mismatch: d4
```

The v0.3 bank bytes and tensor receipts are exact. The incompatibility is that
the archived v0.3 episode contract stored five fields, while the current
hardened contract adds family, tensor-shape, one-hot, permutation, range, and
canonical-realization invariants. For D4, C8, mixed-cycle, and random-pair
banks, the old contract exactly equals the corresponding projection of the
new contract, every tensor receipt is exact, and all applicable strengthened
invariants pass. The unchanged verifier nevertheless requires whole-object
equality and therefore fails closed before it reaches v0.4.

## Failure-aware replay

`verify_retained_failure.py` imports the frozen manifest-bootstrapped verifier.
Before permitting any mismatch, it independently proves:

- byte-exact inherited bank receipts and exact legacy-contract projections;
- canonical JSON conversion of six unavailable raw-arm summaries from
  in-memory `NaN` to stored `null`;
- exact equality of gate readjudication after sorting only two unordered
  observation-row lists;
- exact report regeneration after restoring the preregistered paired-metric
  row order; and
- exact decoded chart pixels.

It then permits only the enumerated messages in
`ARCHIVAL_VERIFICATION.json`. Every other assertion remains fail-closed. In
particular, it verifies:

- the package manifest and inherited lineage;
- every evaluation-bank recipe and receipt;
- all twelve checkpoint files, state dictionaries, and checkpoint metadata;
- deterministic reevaluation of all twelve seed-by-arm cells;
- aggregate and paired-contrast recomputation;
- full gate readjudication, including reproduction of A15's failure;
- report content; and
- decoded chart pixels.

The replay completed with exit code zero and source digest:

```text
2dcc963478b892cb02c8216619c2acf9c02d43512577b90a18d23dac226dee0f
```

Run it with:

```powershell
python -E -P -B .\results\packet_closure_pilot\verify_retained_failure.py
```

The correct interpretation is:

> Integrity and deterministic replay passed with the official assay
> invalidation retained. The scientific full claim remains not evaluated.
