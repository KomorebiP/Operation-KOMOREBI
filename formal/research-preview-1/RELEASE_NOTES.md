# Research Preview 1 — Release candidate 1

**Identifier:** `research-preview-1-rc1`  
**Prepared:** 21 September 2026  
**Publication status:** not published

This is an editorial and packaging revision of the launch-preparation candidate. The mathematical checkpoint remains Block 34. No production theorem, proof, transition, or reference-engine implementation was changed. The new replay harness also rejects mixed diagnostics rather than counting an expected contradiction alongside an unrelated compiler error as a successful control.

## What changed

The overview and technical note now present the result directly, without requiring the reader to follow the internal block chronology. The technical note includes a worked modulus-four example. A separate Future Research document identifies executable refinement, cross-precision state maps, inverse-limit machines, structural comparison, and broader abstraction as proposed work rather than publication prerequisites.

The claim register now includes machine-checked anchors for the one-layer obstruction, exact branch valuation, and positive-precision output reduction. The package adds an attribution note, an explicit correction process, a release checker, and a separate proof-replay harness. Citation metadata identifies this exact unpublished candidate.

## Evidence boundary

The retained historical proof records are unchanged. New release tests check their relationship to the packaged source and run exact finite references. A fresh Lean replay of the public candidate remains separate and must not be inferred from Python or checksum results.

See [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md) for the remaining release checks and [REPRODUCE.md](REPRODUCE.md) for commands. Future theoretical extensions are not release blockers.
