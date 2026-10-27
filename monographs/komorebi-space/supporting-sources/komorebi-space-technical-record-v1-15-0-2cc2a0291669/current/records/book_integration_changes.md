# Publication prose integration review

**Result:** both new formal connections are accurately integrated. No formal-statement mismatch was found.

## Changes

- Replaced the obsolete written-only qualifier for the concrete diagonal unit-vector and nonclosed-range example with the actual Lean declarations and the zero-to-positive coordinate translation.
- Identified the inexact rounded rate as a named formal theorem and retained the measured-data normal residual, literal ceiling, solver tolerance, and internally derived bias.
- Extended the formal correspondence table and Lean guide with the new APIs, without changing the count of 16 principal theorem groups.
- Added a concise route to `examples/WORKED_EXAMPLE.md`, preserving the distinction between an exact finite executable check and a verified Lean extraction.
- Retained the alternate weak-subsequence proof qualification, the unchanged fixed-space limitations, and the existing table spacing setting.

## Proofreading and validation

- Mode: `proofread-math` self-review, including its detailed checklist. Re-read every changed hunk with adjacent definitions and notation.
- Existing mathematical-token changes: none. Every existing statement, proof, and display in the five assigned files is byte-preserved in its original order.
- Checked 107 existing theorem/proof environments and display blocks. Added four displays to the Lean guide that restate the reviewed new theorem interfaces.
- Matching LaTeX begin/end environments passed. No space-containing `leanname` arguments were introduced.
- Confirmed all five newly cited API names exist in the actual new Lean modules.
- Read both independent mathematical audit reports. Both verdicts are “proved as written”; their exact source hashes are recorded in the JSON.
- PDF generation and rendered-page inspection were not run by this editor. They are assigned to the release owner. The final thematic table has two added rows and needs its final pagination inspected.

## Deferred verification wording

`book_audit_paragraph_proposal.txt` contains six exact old/new replacements in JSON form. They have not been applied. Apply only after the fresh integrated replay passes and the final receipt confirms all target/declaration and control counts. The current proposal expects 56 controls split as 18 successes, 35 intended elaboration rejections, and three policy rejections.

## Recorded local failure

The first preservation-check script falsely treated a table row spacing marker as the beginning of a displayed equation. Its check stopped after the first two file writes. The mathematical source was not damaged. The display matcher was corrected to exclude doubled row separators, and every assigned file was then compared against the unchanged v1.14.0 source. The corrected preservation check passed.

## Frozen edited-source identities

| File | SHA-256 |
| --- | --- |
| `source/chapters/05_geometry.tex` | `04eb9896d549e39afb98119473d57d7edcfe105c10761bb6a2ba4db9597a80a1` |
| `source/chapters/05k_stopping_rules.tex` | `c24603387f4ec8fb297cd294bd9a919af2ce8bf920719ba3189b5a47c7640009` |
| `source/chapters/11_written_extensions.tex` | `d0075dc6aefab5a8daac37c1e88f2368fcc1ca062456b2e58f62bfe9e24dee41` |
| `source/Komorebi_Space_Lean_Guide.tex` | `5ecee6d63a02ab2792896d4a1e9233842b568695fa68442f22c390df237d1031` |
| `source/lean_guide_map.tex` | `d6c9d528f26b9a4b88dc2be840440ea4ced3b3918c6c4d73bc880d188770a93f` |

The JSON and unified diff preserve the before/after identities and exact edit scope. These identities precede any release-owner application of the deferred verification wording or final typesetting adjustments.
