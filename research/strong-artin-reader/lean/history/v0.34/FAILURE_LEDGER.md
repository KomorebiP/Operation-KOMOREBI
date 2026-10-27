# Failure ledger — v0.34

Only completed source replays and axiom audits constitute accepted verification.

## Operational failures

- Streaming execution was unavailable; no streamed process was used as proof evidence.
- Initial portable-runtime extraction exceeded its wrapper. A second streaming archive pass compared every file size and restored 5,267 missing/incomplete files; its process returned zero. The assembled archive SHA-256 matched the supplied manifest.
- One oversized development dependency batch was interrupted after six recorded successful compilations. The remaining dependencies were recompiled in smaller batches. No interrupted module was counted as passed.
- The first release verifier referenced a wrongly substituted parent filename v0.34 instead of v0.33 and stopped before a theorem compile. The parent constant was repaired; the exact v0.33 checksum is required.
- Lake reported a file-type change in the portable Batteries docs/README.md symlink. Git status confirmed that only this documentation path differed. It was restored from the pinned commit; no Lean source was changed and the checkout is clean. The Mathlib cache was reused, not rebuilt.

## Rejected Lean drafts

- ZModSquareZeroLayer: RC 1; diagnostic `ZModSquareZeroLayer_1789198926930691343.log`. Coercion, constructor annotation, or warning-check issue; subsequently repaired.
- MixedCharacteristicMatrixKernel: RC 1; diagnostic `MixedCharacteristicMatrixKernel_1789199117905849745.log`. Coercion, constructor annotation, or warning-check issue; subsequently repaired.
- MixedCharacteristicMatrixKernel: RC 1; diagnostic `MixedCharacteristicMatrixKernel_1789199152116407737.log`. Coercion, constructor annotation, or warning-check issue; subsequently repaired.
- MixedCharacteristicMatrixKernel: RC 1; diagnostic `MixedCharacteristicMatrixKernel_1789199175103557962.log`. Coercion, constructor annotation, or warning-check issue; subsequently repaired.
- MixedCharacteristicExplicitCoordinates: RC 1; diagnostic `MixedCharacteristicExplicitCoordinates_1789199671486573157.log`. Coercion, constructor annotation, or warning-check issue; subsequently repaired.

The rejected diagnostics remain under development/. No failing source or placeholder declaration is counted as accepted.

- One fresh replay wrapper interrupted after 36 successful source modules. No verdict for the interrupted module was recorded. Resuming from hash-checked unchanged sources compiled the remainder and the axiom audit, producing PASS for all 44 source modules.
