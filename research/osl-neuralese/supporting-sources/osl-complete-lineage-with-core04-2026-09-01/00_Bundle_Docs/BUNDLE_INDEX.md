# OSL complete lineage bundle

This archive collects every distinct OSL source release and preserved result package found in the current lineage, together with the Discovery Bridge and the Core 0.4 receipt-hardening development. Each packaged release appears expanded for immediate browsing and as a byte-identified release archive.

## Version resolution

The latest canonical language remains **OSL v0.5 with OSL-Core 0.3**. OSL-Core 0.4 is a separately packaged executable receipt-hardening development; it does not rewrite the frozen canonical package. The geometry pilot's v0.6 label belongs to an experimental branch and does not supersede the language specification.

| Folder | Release | Role | Preserved status |
| --- | --- | --- | --- |
| `01_Canonical_OSL_v0.5` | OSL v0.5 / OSL-Core 0.3 | Language, manuscript, interpreter, finite metatheory | Complete canonical package |
| `02_Discovery_Bridge_v0.1.0` | Discovery Bridge v0.1.0 | Exact bounded operator synthesis and admission | New verified sidecar toward OSL-Core 0.4 |
| `03_Geometry_Pilot_v0.6` | Geometry Pilot v0.6 | Representation and intervention experiment | Results, reports, figures, and checkpoints included |
| `04_Micro_Emergence_Lab_v0.1.1` | Micro-Emergence v0.1.1 hotfix2 | Exact finite worlds and role-binding protocol | Source complete, confirmatory run not bundled |
| `05_HF_Causal_Lab_v0.2.1` | HF Causal v0.2.1 hotfix | Transformer causal-compositional experiment | Recovery source and partial evidence, no returned model-run ZIP |
| `06_HF_Operand_Slot_Lab_v0.3.1` | Operand-Slot v0.3.1 | Typed 24-slot causal experiment | Packaging hotfix, scientific run absent |
| `07_OSL_Core_0.4_Receipt_Hardening_v0.1.0` | OSL-Core 0.4 / v0.1.0 | Versioned receipts, independent protected-state replay, and compatibility evidence | 66/66 corpus, 93/93 tests, and 24/24 adversarial witnesses verified |
| `90_Original_Release_Archives` | Seven release archives | Byte-preserved or deterministic release deliverables | SHA-256 values recorded in `BUNDLE_MANIFEST.json` |

The three separate continuation and final-verification records are under `00_Bundle_Docs/Source_Records`.

## Recommended starting points

1. Read `01_Canonical_OSL_v0.5/README.md` and `01_Canonical_OSL_v0.5/LANGUAGE_REFERENCE.md` for the language itself.
2. Read `07_OSL_Core_0.4_Receipt_Hardening_v0.1.0/README.md`, `CORE04_RECEIPT_SPEC.md`, and `CLAIM_BOUNDARY.md` for the receipt-hardening development.
3. Read `02_Discovery_Bridge_v0.1.0/README.md` for bounded operator synthesis and admission.
4. Read `02_Discovery_Bridge_v0.1.0/UPSTREAM_AUDIT.md` and `CORE_0.3_AUDIT.md` before interpreting the empirical or formal claims.
5. Use each experimental package's own README and frozen protocol when reproducing a run.

## What the Discovery Bridge adds

The bridge accepts a typed finite-world operator proposal, enumerates every primitive program through a declared depth, quotients programs by their exact full-state transformation, and returns one of five decisions: admitted, ambiguous, unsatisfiable, false-law rejection, or nonnovel rejection. Certificates embed their normalized proposals and are semantically replayed before registration or OSL emission. The registry supports an externally retained tip for suffix-truncation detection.

This is bounded finite operator discovery. It is not open-world discovery, proof that a neural network internally invented an operator, or a proof-assistant verification of the Python runtime.

## Important formal boundary

The frozen v0.5/Core0.3 receipt kernel retains its original limits. The separate Core 0.4 package addresses the named empty-trace, terminal, capability-lineage, constructor-provenance, protected-action, rollback, and final-state gaps for the packaged finite corpus. Its independent layer reconstructs protected identity, packet, proof, memory, capability, action, and rollback state; a separately labeled same-runtime replay binds delegated interpreter semantics. Numerical algebra and complete session graphs are not independently reconstructed, and dedicated finite results apply only where explicitly invoked. SHA-256 establishes byte integrity, not principal identity or authorship, and neither Python implementation is a mechanized proof.

## Verify the bundle

From PowerShell:

```powershell
$Root="C:\path\to\OSL_Complete_Lineage_with_Core04_2026-09-01"; Set-Location $Root; python .\verify_bundle.py
```

The verifier checks the top-level SHA-256 manifest, every expanded package's exact file count and byte count, every preserved archive's SHA-256 and size, and each ZIP's CRC records. Individual packages retain their own verification scripts and reports.
