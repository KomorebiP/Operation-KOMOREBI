# Inherited checkpoint provenance

These files preserve the original v0.16.0 archive's top-level metadata, source
hash records, verification summary, and original generic verifier. The original
`AUDIT.json` describes v0.15.0, and the original runtime metadata retains Block
13 verification wording. They are historical records, not the current edition's
status.

All 93 production Lean sources in the current formal directory remain
byte-identical to that checkpoint. The current edition repairs the generic
verification runner and supplies truthful current metadata. Historical runs in
`../verification` describe their original executed inputs and retain their
original version-1 manifests. Their input hashes must be interpreted against
the original checkpoint, not the amended generic runner. The original ZIP is
retained separately in the final paper bundle.

Current evidence and source-preservation records are in the release-level
`verification` directory. No historical run is relabeled as a fresh full-corpus
proof build.

`AxiomAudit_original_v0.16.0.lean` preserves the original 1,010-command wrapper;
the current root wrapper is regenerated for all 1,159 enumerated names.
