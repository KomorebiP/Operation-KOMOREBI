# START HERE — Komorebi Cross-Radix Rigidity Continuation v0.5.0

This is the durable continuation checkpoint after closing the Reynolds/DFT/affine-decoder/lcm-intersection layer requested from the certified v0.4.0 baseline.

## Mandatory reading order

1. `CONTINUE_HERE.md`
2. `PROTOCOL.md`
3. `AUDIT.json`
4. `PROOF_BOUNDARIES.md`
5. `README.md`
6. Relevant files in `src/`

The v0.4.0 baseline is preserved verbatim in `frozen_baseline/Komorebi_Cross_Radix_Rigidity_Lean_v0.4.0.zip`; its 20 source files are copied byte-for-byte into this checkpoint and verified against the v0.4.0 audit hashes.

## Certified v0.5.0 increment

The new durable layer now contains an actual cyclic subgroup Reynolds average, exact Mathlib-DFT 0/1 masks, two-radix and finite-family lcm projector/intersection laws, raw-radix reduction through `gcd(T,m)`, an explicit affine normal-form decoder with `AB=P`, `ABA=A`, `BAB=B`, and a DFT shell construction proved to agree with the saved Möbius/divisor shells.

Bell's generalized Cobham theorem remains external. The naive base-independent integral normal form remains rejected.

## One-line continuation command

> Open `START_HERE.md`, read `CONTINUE_HERE.md`, `PROTOCOL.md`, and `AUDIT.json`, then continue the Komorebi Cross-Radix Rigidity program from certified v0.5.0. Preserve every proof boundary, keep Bell external, do not revive naive base-independent integral normalization, and attack the exact characteristic-zero rank/nullity law next; only after that add the explicit Bell-conclusion interface and uniform all-radix hull theorem.
