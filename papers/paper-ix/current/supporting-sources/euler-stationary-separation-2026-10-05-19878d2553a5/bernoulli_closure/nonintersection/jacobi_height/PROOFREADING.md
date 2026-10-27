# Self-review and independent review

Proofread: SAFE_JACOBI_AND_HEIGHT_BOUNDARY.md.

- Routine edits: none required after final read.
- Mathematical-token changes: none during proofreading.
- Validation: the exact rational run completed; its manifest validated against current inputs and outputs.
- Independent review: cross_cartier_review reported that the proof, implementation, and independent replay passed with no correction requested. The review covers the completed c₀ lattice, exact first-exit path calculation, loss of178 bits in the source normalization, half-derivative loss of one bit, and distinction between depleted approximation and actual undepletion.
- Remaining mathematical gap: no uniform strict comparison between the model's stationary value and its error precision has been proved. The new safe finite model is not a proof of actual Euler simplicity.
