# Roots of unity and the ABC conjecture

ABC remains unproved. This checkpoint follows RR2 and tests the proposed
roots-of-unity approach with exact mathematics and explicit counterchecks.

Start with [the current result](abc_work/roots_unity/LATEST.md), then
[the claim ledger](abc_work/roots_unity/CLAIM_LEDGER_RR3.md) and
[the continuation record](abc_work/roots_unity/HANDOFF.md).

The positive result is a cyclotomic degree budget for the exceptional
first-contact factors of A^n+B^n. It yields a stronger restricted criterion:
for every fixed epsilon>0 and 0<delta<1, sufficiently large n obeys the ABC
inequality when all exceptional odd output primes are at most n^(1-delta),
uniformly in the coprime bases. This improves the preceding sufficient
n^(1/2-delta) cutoff. It does not establish that the larger exceptional
primes are absent or small enough in the remaining families.

The other calculations establish precisely what roots and character filters
preserve. Exceptional contact has a depth plateau, different prime filters
can synchronize, and cancellation by a fixed Fourier combination is charged
to its resultant. Applying existing torsion-distance theorems leaves an
uncontrolled coefficient-dependent constant. These are limitations of the
tested proof steps, not impossibility results for roots-of-unity methods.

The complete prior RR2 archive is retained under `ancestry/`, with its exact
hash in `ANCESTRY.json`. Its proof sources and finite checks also remain in
`abc_work/`. The authoritative current view for this continuation is
`abc_work/roots_unity/LATEST.md`; the older `abc_work/LATEST.md` is preserved
as the pinned RR2 input snapshot.

## Reproduction

Python 3.9 or newer is sufficient, with no third-party packages. From this
directory, run:

```bash
python3 abc_work/roots_unity/reproduce.py
python3 abc_work/roots_unity/check_evidence.py
```

On Windows, `python` may be used instead of `python3`.

Six bounded exact contracts passed. Their version 2 manifests and current
input/output hashes validate. The divisor-count corollary is proved directly
from the audited degree bound, rather than inferred from finite data.
Separate agent reviews are included. They are not external peer review or
formal proof certificates. No Lean code was compiled and no historical
priority claim is made.

The package-root `SHA256SUMS.txt` describes the distributed snapshot.
Reproduction changes runtime fields and execution records. Route-local
generated checksum lists that predate those reruns are omitted in favor of
the authoritative package-root list. Original inherited-checkpoint checksum
lists remain with their unchanged sources.

The false ancillary basis sentence caught during review and the invalid
initial test control caught by an assertion are both documented in the new
claim ledger. Their corrections do not change the stated ABC target. The
inherited fixed-offset coprimality correction is retained in
[ERRATA.md](abc_work/ERRATA.md).

The package contains source-contract summaries and primary-source links,
not copies of the external articles.
