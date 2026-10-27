# External attribution

Reference repository: CBirkbeck/AINTLIB.
Pinned commit: c62aa9dd4638d86b50f46d4000cf87157e333a6f.
Relevant source: projects/Chebotarev/CebotarevDensity/FixedFieldDensity.lean.
Connector-reported Git blob: 7d40bad6a09112255b5bafca096d2f143083fd8c.

The classical cyclic-fixed-field reduction, arithmetic Frobenius correspondence,
main-term count and density argument follow the upstream development and its
cited sources (Sharifi, Algebraic Number Theory, Theorem 7.2.2; Stevenhagen and
Lenstra, Chebotarev and his density theorem, Appendix). Those texts were not
independently re-audited in this block.

This contribution repairs/reconstructs selected proofs on the pinned Mathlib API,
separates reusable sum/error/transfer modules, and checks the original visible
public interface. It does not claim a new Chebotarev theorem or independent
novelty for that classical argument. The inherited Frobenius source identifies
Chris Birkbeck and Apache License 2.0. Original notices and the licence text are
preserved. No live repository edits were made.
