# Verification record

Author: Komorebi P.  
Verified: 2026-09-03

## Primary v0.4 probe

- Complete final run: `COMPLETE`
- Frozen-checkpoint census: `12/12`
- Archive and checkpoint receipts: `PASS`
- Strict `weights_only=True` loads: `12/12`
- Unit tests: `7/7 PASS`
- Exact compiled D4 controls: `12/12 PASS`
- Compact additive quotient test: `UNSUPPORTED`

The final primary run was independently replayed. Because wall-clock elapsed
time is intentionally recorded, raw JSON bytes differ in that one field.
After deleting only `runtime.elapsed_seconds` and canonicalizing JSON, both
runs have SHA-256:

`8939c4ad20a7934ab0eced40f12d25ca26bded9f84ab3ab1639e6084ce4b7292`

Final retained `v04_probe/RESULTS.json` SHA-256:

`d3aace0e9d2fcb201cbff31f24d54effc0ea336258a2db85f3537364176291b0`

## Independent v0.4 cross-check

- Checkpoints: `12/12`
- Regenerated sealed banks: `PASS`
- Every bank tensor receipt: `PASS`
- Independent audit verdict: `PASS with stated numerical/estimand caveats`

The cross-check was independently rerun byte-for-byte. Both outputs had
SHA-256:

`767a532f43bc0518a246bf65d2dcdd64dfda28ef19eb059a66e2bfa3e313d0b7`

## Secondary v0.3 hard-QR bridge

- Checkpoints: `12/12`
- Eligible held-out coordinate permutations: `2,080/2,080`
- Independent reviewer hardening: applied

The final v0.3 analysis was independently rerun byte-for-byte. Both outputs
had SHA-256:

`7dd6967d2405153f9f6c7b590d9d51bdd632987c2135797a5733ee1d76e7a5c2`

## Review caveats preserved

- The rank conclusion concerns an exact linear, centered-logit observable
  quotient; it does not rule out coarser argmax-neutral directions or a
  nonlinear finite decision-packet description.
- Cross-check endpoint accuracy is exhaustive current-label accuracy on its
  crossed sealed bank, not the original conditional-retention estimator.
- NumPy and PyTorch hard-polar SVDs differ at retraction-scale radial precision;
  source-runtime replay agrees on the materially larger angles and decisions.
- All analyses are posthoc and leave the original retained v0.4 A15 assay
  failure unchanged.
