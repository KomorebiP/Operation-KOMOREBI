# Release notes - Finite Metatheory and Independent-Kernel Draft v0.5

## OSL-Core 0.3

Version 0.3 completes and documents a previously unfinished resource and verification layer that was already partially present in the source tree.

### Language and runtime

- persistent, affine, and linear proof modes
- exactly-once completion requirement for linear proofs
- append-only audit log distinct from transactional semantic state
- receipt predecessor links, transaction labels, and state indices
- statement commit/reject boundaries with source and semantic digests
- deterministic whole-program replay verification
- finite session terminal declarations and graph verification
- static explicit secret-to-metadata dependency analysis
- canonical terminal completion and rejection receipts

### Independent verification

- source conformance over 66 programs
- paired safe/leaky public-projection audits
- independent packet, proof, provenance, action, session, and transaction kernel
- raw receipt tamper rejection
- fully rehashed semantic provenance-forgery rejection
- complete integrated abstract-kernel exploration
- complete decomposed explorations of provenance, capabilities, contracts, transactions, and sessions

### Corpus

- 42 accepted programs
- 24 expected safe rejections
- 66 total conformance programs
- 2 paired-run information-flow examples
- 61 focused automated tests

### Finite certificate counts

- integrated kernel: 740 reachable states, 19,240 transitions
- decomposed metacore: 1,590 reachable states, 28,718 transition attempts
- independent receipt kernel: 66 programs, 1,149 receipts, 70 proofs
- combined: 2,330 states and 47,958 finite transition checks

### Manuscript

The paper adds a new OSL-Core 0.3 section covering proof resources, append-only audit semantics, trace correspondence, independent receipt reconstruction, finite session verification, explicit information flow, two exhaustive finite metatheories, adversarial tamper cases, and exact trust boundaries.

### Boundaries

The finite certificates are computer-assisted results over declared models. They are not a proof-assistant verification of the full Python interpreter, a universal noninterference proof, an authentication scheme, a production sandbox, or a liveness proof for unbounded distributed protocols.
