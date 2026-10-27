# Komorebi Beal research — Block 62
## Actual trace products and depth-one conductor exclusion

Version 6.2.0. 20 September 2026.

This release continues the exact original Block 61 checkpoint, preserved in
`predecessor/`. Every earlier checkpoint remains nested byte for byte. It does
not replace the upstream conditional geometry with an unconditional claim.

**New bounded result:** the actual opposite extension at depth one cannot have
all its ramification over

    Splus={43,113,127,197,883,1373,1667}.

The proof uses a same-representation trace identity, correctly twisted ray
values, actual Frey point counts, and one common natural Kummer vector. It allows
other primes to divide C without ramifying in beta. It does not allow unrecorded
extra beta ramification.

For the old complete high-divisor class H(C) subset U, depth one still remains:
its beta must now ramify at a new low-congruence prime outside U union{43,113,127}.
A separate precise exclusion is obtained when that enlarged set contains the
COMPLETE geometrically eligible divisor set E(C). Read the quantifiers in
`work62/notes/ARITHMETIC_CONSEQUENCES.md`.

## Reproduce

Use Python 3.10 or later. The production verifier and all six production
scientific programs need only the standard library. From this directory run:

    python verify.py --replay-predecessors --report ../Block62_Replay.json

`--timeout-seconds` controls a per-job wall cap, default 180 seconds. A timeout
is inconclusive. Reports must be outside this immutable package. Omitting
`--replay-predecessors` runs the new checks and inherited byte audits, but does
not execute the historical checks. The retained historical replay is a selected
chain, not a fresh independent proof audit of every old mathematical assertion.

The verifier recreates outputs in a clean scratch copy and compares complete
JSON results, not cached success flags. Its deliberately corrupted inputs must
be rejected. Payload checksums exclude their own manifest. Final archive audit
and fresh-extraction replay records are supplied separately.

## Evidence and non-claims

There are written conditional proofs, exact finite certificates, and a separate
arithmetic implementation. There is NO new Lean compilation, NO independent
mathematical reviewer, NO unconditional depth-one theorem, and NO proof of Beal.
The earlier analytical period, actual-model, class-group and endpoint hypotheses
remain explicit dependencies. File hashes authenticate bytes, not mathematics.

Start with `work62/REPORT.md`, `work62/TARGET_CONTRACT.md`,
`work62/PROOF_BOUNDARY.md`, and `CONTINUE_HERE.md`.
