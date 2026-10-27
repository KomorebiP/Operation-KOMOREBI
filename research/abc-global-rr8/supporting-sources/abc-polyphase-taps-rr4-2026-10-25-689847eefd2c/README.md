# Polyphase refinement and taps in the ABC investigation

The tested operations help locate contacts and construct exact nonzero
auxiliary integers. They do not improve the present general bound on the
unresolved primitive channel. ABC remains unproved.

Start with [the current result](abc_work/polyphase_taps/LATEST.md), then
[the claim ledger](abc_work/polyphase_taps/CLAIM_LEDGER_RR4.md) and
[the continuation record](abc_work/polyphase_taps/HANDOFF.md).

For s_n=A^n+B^n, two integer taps can construct

    gcd(s_n,s_(n+h))=gcd(s_n,A^h-B^h)>0.

This is the smallest positive output of any unrestricted integer tap set
at that stride. It is a useful low-order certificate. At primitive stride
h=2n the generator is s_n itself. Refinement retains the same birth/lifting
mass, and its apparent degree reduction is paid for by base height.

Separate proofs track multichannel reconstruction, determinant costs,
denominators and the target scalar functional. Integral banks preserve
minimum channel valuation, rather than the maximum depth of an individual
functional. An adaptive construction with a genuinely small, nonzero,
contact-preserving integer remains an open route.

## Reproduce

Python 3.9 or newer and its standard library are sufficient. From this
directory run:

```bash
python3 abc_work/polyphase_taps/reproduce.py
python3 abc_work/polyphase_taps/check_evidence.py
```

On Windows, `python` may be used instead of `python3`.

All three bounded exact contracts passed, and their version 2 records and
input/output hashes validate. Written proofs and separate agent audits
are included. They are not external peer review or Lean certificates.
No historical originality claim or full ABC conclusion is made.

The full RR3 parent archive is retained under `ancestry/`, pinned by
`ANCESTRY.json`. Older live-view files remain as immutable input snapshots.
The authoritative current view for this continuation is
`abc_work/polyphase_taps/LATEST.md`.

The package-root SHA256SUMS.txt covers the distributed snapshot. Reproduction
updates run records and runtime fields. Superseded generated route-local
checksum lists are omitted in favor of that current list. Original inherited
checkpoint manifests remain with their unchanged source files.
