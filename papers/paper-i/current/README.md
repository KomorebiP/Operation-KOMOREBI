# Projector Resolved Seed Calculus I

**Typed operator systems, seed rank, and exact packet coordinates**  
Komorebi P.

Paper I develops a linear foundation for generating objects from seeds, resolving them into packets, and tracking operators between those packets.

| Read | Pages |
|---|---:|
| [Traditional manuscript and visual atlas](papers/Paper_I_Traditional_Final.pdf) | 105 |
| [Lean and evidence guide](papers/Paper_I_Lean_Guide_Final.pdf) | 44 |
| [Machine-native companion](papers/Paper_I_Machine_Native_Final.pdf) | 100 |

The traditional manuscript includes ten main figures and twenty-two atlas plates. Open [START_HERE.html](START_HERE.html) for the reading index.

## Sources and verification

- [Editable manuscript and figures](editable/traditional/)
- [Current Lean source closure](formal/current/) and [replay instructions](formal/README.txt)
- [108-record correspondence map](formal/coverage/COVERAGE_108.json)
- [Accepted formal verification](formal/evidence/RELEASE_VERIFICATION.json)
- [Python implementation](code/python/)
- [Freeze record](FREEZE_RECORD.json) and [progress ledger](PROGRESS_LEDGER.md)

All sixty-nine proof-level records have accepted formal correspondences at their stated scopes. Definitions, classical inputs, boundaries and documentary records are classified separately. The accepted October 15 verification checks 3,500 logical declarations through 3,499 ordinary replays and one fresh-name body check of an identical upstream-name duplicate. It inventories thirteen runtime helpers separately. Semantic review comprises forty-seven newly reviewed records and twenty-two retained predecessor acceptances.

This freeze preserves the three readers, mathematical sources, code and accepted proof evidence. Fresh checks authenticate their file identities, PDF structure and selected rendered pages. No new Lean run, TeX rebuild or whole-paper proof audit is claimed. The recorded ninety-six exact visual assertions and thirty-three companion tests retain their original execution dates and bounded scope.

## Verify the complete download

Extract this single ZIP, enter its root directory, and run:

```sh
python3 scripts/verify_integrity.py
```

The verifier checks the exact file set, sizes, SHA-256 values and preservation of all 2,181 baseline files. The historical predecessor ZIP is already included. No separate assembly is required.

Formal reproduction requires the external pinned Lean 4.34.0-rc2 runtime and dependency cache. PDF reproduction uses `python3 scripts/build_pdfs.py --check-only`; despite that option's name, the builder writes build products and generated companion data. Run rebuilds in a separate working copy, then use the original dated evidence to identify its checked inputs. Rebuilding does not preserve the frozen file set.

## Open use

Original code and machine-readable material use MIT. Original papers, guides, figures and explanatory writing, including their editable sources, use CC BY 4.0. Code listings may also be used under MIT. See [LICENSE.md](LICENSE.md) for the grant, full terms and third-party exceptions. The current grant supersedes earlier unassigned-license statements for original project material included here.

The mathematical publication edition is October 15, 2026. This distribution was frozen on October 20, 2026. Older manifests, upload-preparation records and reports identify their earlier input trees; the current whole-package check is the root `MANIFEST_SHA256.json` and verifier. Changed administrative originals are retained under `verification/freeze_2026-10-20/before/`. The PDFs and scientific payload retain their accepted bytes.
