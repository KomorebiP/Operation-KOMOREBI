# v1.2.0 release audit — Lean Block 02

## Scope and result

C01, the maintained NCT degree dependency, and the C02 lower-bound component are Lean-verified. The exact joint endpoint is `CircuitObstructions.restored_degree_and_cover_bound`. The C02 evaluation-span dual and C03-C08 remain outside the formal block. The research scope is unchanged, and no P-versus-NP or superpolynomial result is claimed.

All 115 theorem declarations (75 new, 40 inherited) were rebuilt under Lean 4.34.0-rc2 with bundled Std only. Eight modules passed strict checking and bundled-kernel replay. Eight invalid controls were rejected. Axiom dependencies are confined to propext, Classical.choice and Quot.sound. No independent reviewer or independent kernel implementation was used.

## Preservation and finite evidence

The three original proof modules are byte-identical to v1.1.0. Its exact archive is preserved in `archive/releases/` and its Git history is retained. The predecessor's full scientific suite and its 40-declaration formal verifier were reproduced before edits. The seven baseline scientific outputs remain unchanged.

The independent Block 02 checker returned the same deterministic output twice. It covers all 278 functions on zero through three inputs, 2,698 legal circuit words, 28,088 register-product bounds, 28,088 reversal assignment cases, 251 restored oracle words, 2,632 restored boundary assignments, and 37,752 generic target-elimination cases. The generic product lists may repeat wires; primitive circuit gates must have distinct wires.

The quick suite has 21 test methods. Full verification adds the new finite checker while preserving the seven original comparisons. The formal and finite manifests validate with current input/output hashes.

## Document

The cumulative 30-page reference includes every indexed declaration, source location and axiom list, with unmodified UTF8 statements in sidecar files. It was rendered and visually inspected. The PDF is an editorial rendering, not a replacement for the Lean source.

## Failures and trust boundary

See `DEVELOPMENT_FAILURES.md` for failed compiler acquisition, partial archive recovery, strict-proof development corrections, and the draft missing-PDF link. The recovered core executable hashes match v1.1.0, but the entire multipart archive was not reconstructed or authenticated. Tool binaries and font binaries are not redistributed.

## Local delivery

No hosted GitHub repository is created, changed, published, privatized or archived. ZIP/bundle extraction and rebuild checks are recorded separately in the final delivery JSON, which identifies the final commit and artifact hashes. This source audit does not substitute for those checks.
