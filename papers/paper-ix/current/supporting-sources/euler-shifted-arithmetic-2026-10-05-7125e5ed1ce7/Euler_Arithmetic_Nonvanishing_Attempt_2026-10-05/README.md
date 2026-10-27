# Euler arithmetic nonvanishing attempt

Checkpoint: `Euler-arithmetic-nonvanishing-20261005`.
Parent: `Euler-coupled-stationarity-20261005`.

**The focused arithmetic nonvanishing theorem and universal Euler simplicity remain open.**

Start with [the focused mathematical report](arithmetic_nonvanishing/README.md)
and [the independent audit](arithmetic_nonvanishing/review/INDEPENDENT_REVIEW.md).
The package contains the complete parent checkpoint and all new proofs,
exact arithmetic checks, failed implications, outputs and provenance.

The weighted Bernoulli identity has been transferred with its full cutoff.
Its apparent4^r forcing cancels exactly at the first packet. The transferred
half-shift relation retains an additional Bernoulli series whose value and
derivative are not yet excluded from the required matching equations.

From this directory, one inexpensive replay is:

```bash
python3 arithmetic_nonvanishing/root/unit_filter_discriminator.py replay_unit_filter.json
```

This reconstructs the actual ordinary index whose critical value has
valuation91 and leading unit15mod32. It is a counterexample to a proposed
parity/unit shortcut, not to Euler simplicity.

The exact kernel identities can be replayed with:

```bash
python3 arithmetic_nonvanishing/unit_identity/check_kernel_identities.py --out replay_kernel.json
```

Current manifest execution roots are recorded in
`arithmetic_nonvanishing/MANIFEST_ROOTS.json`. The parent retains its own
manifest root map. The superseded structural run is historical, and its
replacement is explicitly recorded. No Lean compilation was performed.

`PACKAGING_REPORT.json` records portable manifest and pinned-source checks.
