# OSL-Core 0.3 Certificate Guide

OSL-Core 0.3 deliberately separates complementary evidence layers. No single artifact is presented as a proof of the entire Python implementation.

| Artifact | Scope | Exact result | Principal boundary |
|---|---|---:|---|
| `EXAMPLE_RESULTS.json` | source conformance | 66 of 66 programs and 2 of 2 paired audits | packaged programs only |
| `TRACE_VERIFICATION.json` | source-to-state and source-to-receipt correspondence | 66 deterministic replays | fixed runtime and environment |
| `INDEPENDENT_KERNEL_REPORT.json` | dictionary-based receipt/proof replay | 66 programs, 1,149 receipts, 70 proofs | finite encoded rules; no principal authentication |
| `COMPACT_CLOSURE_CERTIFICATE.json` | integrated abstract state model | 740 states, 19,240 transitions | compact abstract kernel |
| `FINITE_METACORE_CERTIFICATE.json` | five isolated finite mechanisms | 1,590 states, 28,718 transition attempts | explicitly defined subsystem models |
| `INFORMATION_FLOW_REPORT.json` | explicit secret-to-metadata dependencies | only the two deliberately leaky programs are flagged | no implicit, timing, semantic, latent, or tool channels |
| `SESSION_VERIFICATION_REPORT.json` | declared finite session graphs | 2 of 2 explicitly verified terminal protocols pass | no asynchronous queues or recursive multiparty liveness |
| `V03_UNIFIED_VERIFICATION.json` | combined evidence summary | all five principal layers pass | conjunction of finite certificates, not proof-assistant verification |
| `OSL_CORE_0_3_VERIFICATION.json` | byte-identical convenience alias of the unified certificate | same digest and bytes as `V03_UNIFIED_VERIFICATION.json` | alias only; not an additional evidence layer |
| `V03_CERTIFICATE_INDEX.json` | SHA-256 binding of generated reports | all indexed artifacts present and passing | integrity, not authorship |

## Evidence hierarchy

1. **Examples** establish intended accepted and rejected behavior.
2. **Trace certificates** establish deterministic replay and source-statement boundary correspondence.
3. **Independent kernel verification** reconstructs semantic authorization from emitted receipts without calling the runtime's authorization methods.
4. **Exhaustive finite models** explore complete reachable-state closures for declared abstractions.
5. **Release manifests** bind the final source, reports, PDF, and verification scripts.

## Strongest justified statement

Within the declared finite models and packaged source suite, OSL-Core 0.3 preserves the tested provenance, proof-resource, capability, contract, transaction, session, and trace invariants. The evidence is stronger than example testing and weaker than a proof-assistant proof of arbitrary OSL programs or the Python interpreter.
