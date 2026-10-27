# Expansion Notes: v0.4 to v0.5

Version 0.5 advances the executable language from **OSL-Core 0.2** to **OSL-Core 0.3** and changes the manuscript emphasis from a mechanized control prototype to a layered finite metatheory.

## Language additions

- persistent, affine, and linear proof-resource modes
- exactly-once completion obligations for linear proofs
- proof consumption receipts
- append-only audit history distinct from rollback state
- source-statement commit and rejection boundaries
- semantic before/after state digests
- terminal program completion and rejection receipts
- terminal declarations and graph verification for finite sessions
- explicit static secret-to-metadata dependency analysis

## Verification additions

- deterministic source-to-trace replay over 66 programs
- runtime-state invariant checker
- independent receipt and proof kernel
- rehashed semantic-forgery tests
- 740-state integrated compact closure
- five decomposed exhaustive models totaling 1,590 states
- certificate index binding all generated reports

## Scale change

- Programs: **53 → 66**
- Expected rejections: **17 → 24**
- Tests: **26 → 61**
- Independent receipt reconstruction: **1,149 receipts**
- Exhaustive finite states: **2,330**
- Finite transition checks: **47,958**

## Remaining formal boundary

The release is computer-assisted finite metatheory, not proof-assistant mechanization. Preservation, progress, receipt correspondence, linear-resource preservation, rollback equivalence, and typed noninterference should next be formalized in Lean, Coq, Agda, or Isabelle.
