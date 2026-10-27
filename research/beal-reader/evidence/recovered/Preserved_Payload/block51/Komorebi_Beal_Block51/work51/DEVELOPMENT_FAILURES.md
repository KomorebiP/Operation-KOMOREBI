# Failures, excluded cases and verification limitations

## Preserved historical failure

Block 50's independent extension-geometry reviewer did not complete its
audit after an availability/usage-limit error. The checkpoint explicitly
records this. Block 51 adds a fresh self-review, not a fictional completed
independent review. No historical files or review labels were changed.

## Rejected stronger claim

The tempting bound n<=t+h is false. At Q=29, t=h=1, the explicit matrices
with n=3 satisfy all the local theorem's hypotheses. This negative control
is preserved in the verifier. The factor two in the correct t+2h bound
comes from the square of the lower coordinate of the toric line.

## Coverage correction before release

The initial independent quadratic basis grid had no nonzero upper-endpoint
cup cases among its admissible examples. This was a coverage limitation,
not a failed theorem. A separate targeted quadratic sharpness family was
added, retaining the original grid and adding endpoint and non-F_7 residue
directions. Both categories are reported separately; no empty category is
presented as evidence for a nonzero phenomenon.

Of the 8640 basis-grid cases, 7110 do not satisfy the stated opposite-depth
hypotheses. They are excluded inputs, not counterexamples or timeouts.
The malformed-matrix and invalid-input tests are expected rejections, not
failed accepted computations. The arithmetic checks use exact values.

## Formal and global limitations

No Lean/lake executable was available in the current runtime inspection.
No new Lean compilation was attempted or claimed. Existing predecessor
Lean source is retained as source only, with its original status. Written
proof and finite-check success are reported separately.

The actual n and compatible global Kummer/diagonal characters were not
computed. Neither of the ordinary n=1 or n=3 cases was eliminated. This
block therefore refines the obstruction rather than closing the conjecture.
