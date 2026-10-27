# Komorebi Beal Block 79 — v7.9.0
## First-stage ramification control

Authoritative predecessor: the unchanged Block78 archive in `predecessor/`.
SHA256: `52f161856a358670436bf42d18dc9654a1db60b82010e6979f8b7dafd3821713`.

The new result separates the two adjoint stages. The actual first-stage cochain p
cannot acquire inertia away from the fixed primes and beta's ramification support.
For two candidates with the same alpha, beta and reference, their p-difference
is an ordinary character ramified only in beta's support and locally zero at the
four fixed places. A finite ray-character calculation bounds that difference
space for the four frozen support patterns.

The upper q-cochain can still have auxiliary inertia. At beta support its two
local values are forced by p; at beta-unramified bad places nonzero upper inertia
requires local beta splitting. Explicit local toric and Frey controls survive.

No one of the eight patterns is eliminated. No global first-stage particular
solution p0, full affine Selmer image, or actual integral Frey realization is
computed. No new Lean compilation or independent mathematical review.

Reproduce the new finite assertions:

    python -B verify.py --report ../Block79_Replay.json

Add `--replay-predecessor` for ONE immediate Block78 default replay, not the full
historical chain. The verifier regenerates both scientific outputs in a scratch
copy and compares them completely. The algebraic proofs are separate from tests.
