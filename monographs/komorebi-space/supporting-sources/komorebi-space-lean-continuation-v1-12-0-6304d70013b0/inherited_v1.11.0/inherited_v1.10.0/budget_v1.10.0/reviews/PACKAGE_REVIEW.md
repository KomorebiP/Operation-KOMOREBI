# Independent package review

Status: **PASS — source and prepackaging review**. Final archive verification is separate and pending.

Scope: the release packaging script, evidence inclusion policy, preservation mapping, and documented replay paths. This is not a new mathematical proof audit or an independently repeated Lean compilation.

## Source review

The initial `package_release.py` revision was read in full. The updated revision with SHA-256 `65d654a46bd8dc057b6e9819d9b1460ceaa38caa7d01b4bf7d1f7f988921d8db` was then read in full. Its improvements bind the accepted receipt to postflight, the current overlay to the accepted assembly inventory, verification helpers and axiom/log evidence to recorded hashes, the release ledger to the formal run, and the manuscript source/PDF to publication verification. They also compare the complete deliverable budget tree before and after copying.

These checks resolve the first reported issue: a status string alone must not permit combining a stale accepted run with changed production sources or an unrelated PDF. The final archive check will independently verify the actual bindings rather than relying only on this source inspection.

Other findings sent to the coordinator:

1. The reviewed revision omitted the previous edition's five `scripts/` files from `history/v1.9.0/`. Current scripts are not a substitute for preserving the historical versions. Include the old script tree in the historical copy.
2. Local extracted-directory comparisons establish equality to that directory, not authenticity against the fixed parent archive. The final independent review will compare the preserved historical entries directly against the v1.9 ZIP whose SHA-256 is fixed in `records/BASE_CHECKPOINT.json`.
3. The integration README's workspace command uses `--published output/Komorebi_Space_Monograph_v1.9.0/formal`. In the released layout that argument must instead point to `history/v1.9.0/formal`. Fresh attempt labels and a separately supplied portable runtime must also be explicit. Historical development commands may retain their actual absolute paths as provenance; they are not relocatable commands as written.

The v1.9 extracted payload was scanned and contains no `.olean`, `.ilean`, `.pyc`, or `.so` files. The release exclusion policy removes development build trees and generated Lean objects while retaining sources, logs, declarations, receipts, controls, and replay scripts. Runtime contents are outside the copied budget tree. Final absence and completeness checks remain pending on the actual archive.

Follow-up source inspection: revision `10dbca99a2eae4e0a7a39f97d17e8b3cc73b5ad2062331a854d41269a35ab5dc` adds the missing historical `scripts/` tree and verifies the entire extracted predecessor against its hash-pinned ZIP. Findings 1 and 2 are resolved in source. An independent read of that parent ZIP confirms the recorded SHA-256 and finds 3,653 file entries, all beneath its expected package prefix.

The final root README, SHA-256 `d691b07ce0b43a119fd21b995f6c5ad753cf4740064f2aa87374d5aa31079475`, was read in full. It supplies extracted-package replay commands using `history/v1.9.0/formal`, a separately provided `RUNTIME_DIR`, and fresh immutable labels. It explains that original absolute paths are provenance and that repeating terminal postflight elsewhere requires first creating a new local replay. Finding 3 is resolved by that explicit release-specific command block; the integration README retains the original development-workspace example.

The reviewed packager parses successfully as Python source. Static review found no remaining blocking source issue. It refuses release until formal receipt and postflight are PASS and mutually hash-bound, the accepted overlay/helpers/axiom report/logs remain unchanged, the ledger binds that run, and publication verification binds the current source and PDF to the same formal receipt. It verifies the predecessor ZIP identity, current source copies, complete deliverable evidence copy, package checksums, ZIP CRCs, and archived payload SHA-256 values. Existing release directories and ZIPs cannot be overwritten.

The script is a coordinator for the recorded independent reviews and receipts, not a replacement for them. Its release-tree and ZIP operations have not been executed by this reviewer. The source-gates PASS verdict does not by itself assert that a release already exists or that pending formal/publication gates have passed.

The narrow render-exclusion revision, SHA-256 `fbc25b0e955f5eafe8e01770fc11856137019f6619c31f2db7ed10058051d2d9`, was reviewed and parses successfully. It adds the `renders` directory exclusion only when copying the current publication's `audit/` directory, and explicitly reports `reproducible_publication_page_renders_included: false`. At this check the excluded subtree contained 336 files, all PNG page renders. Draft PDFs, render manifests, build logs, and review reports are outside that subtree and remain included. No historical-tree copy or budget source/evidence copy receives that exclusion.

The record-finalization helper was also read in full at SHA-256 `6652c7c8e9a0aeb1d0585a9be5e511648b7ff1505922cc86a4b427e9a40a507d`. It requires passing formal/postflight/publication receipts, binds their hashes, and checks all four frozen new source modules before writing accepted records. The review noted that its initial Python `assert` gates could be disabled by optimized execution. The final helper revision, SHA-256 `2387ecac4661faad803be66ef5028144833f924d1e291b1c2505e985da83a187`, replaces those gates with explicit `SystemExit` failures; the change was inspected and the source parses successfully. The observation is resolved. No helper execution or generated acceptance record was asserted by this source review.

The final packager revision, SHA-256 `29839ab3fe952d9d1f78875e27bfc52a90fb93f2431ce2545e192f1983bf2f7d`, adds a further gate that rehashes every acceptance-review/control file named by the accepted ledger before copying. This additional binding was inspected and the source parses successfully.

The final record-finalizer revision has SHA-256 `1a4f51e73e5d698ce4fc032d6267c6ecce1e92d515e79e3c13ff7154745ace60`. It adds one literal paragraph to the generated progress prose, explaining that the detailed exporter finished before an attempted interruption and that no process was affected. Removing exactly that paragraph in memory reproduces the previously reviewed `2387ecac...` file hash. Thus the only change is that literal output text; all gates and computation are unchanged. The revised Python source parses successfully. **The source-gates PASS verdict binds packager `29839ab3...` and finalizer `1a4f51e7...`, with their full hashes above.** No unresolved source-review finding remains.

The script creates `SHA256SUMS.txt` after hashing the payload; consequently the checksum manifest intentionally does not list itself. The final review will check its exact inventory and every listed value, check the manifest bytes in the ZIP, require unique safe entry names and no extra payload entries, and verify ZIP CRCs.

## Final archive checklist

- Confirm package script revision and no unresolved source-review issue.
- Check archive SHA-256, file size, ZIP CRC, unique safe paths, exact entry inventory, and every payload SHA-256.
- Bind formal receipt, postflight, helper review, overlay/assembly/run sources, types/axioms, command logs, and accepted ledger.
- Compare the published current formal tree with the accepted replay source tree, and each new overlay production/control file with its accepted mapping.
- Compare every historical v1.9 archive entry with its preserved location, including scripts and root files; compare inherited trees directly against the parent ZIP.
- Verify all deliverable development attempts retain their source snapshots, logs, types and receipts; verify replay scripts and all accepted/rejected run evidence are present.
- Verify no compiled project object, cache, or portable runtime binary is included, while their recorded hashes and stated trust boundaries remain available.
- Verify manuscript source, PDF, publication receipt, visual review coverage, progress sidecar, and exported PDF identities.
- Verify that the documented extracted-package replay paths resolve, apart from the explicitly external runtime and newly generated attempt destinations.

This report is frozen before packaging. To avoid changing the evidence tree during copying, the final archive findings will be delivered separately after the actual ZIP is available. No final archive acceptance is claimed by this prepackaging report.
