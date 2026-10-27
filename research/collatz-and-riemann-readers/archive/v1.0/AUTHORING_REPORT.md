# Reader edition validation

Author pseudonym: Komorebi P. Edition 1.0, 8 October 2026.

## Mathematical scope

The Collatz and Riemann conjectures remain open in these manuscripts. Printed universal claims are supported by the displayed ordinary mathematical proofs and the classical results cited with their hypotheses. Historical Lean checks are expressly attributed to the recovered project records. This authoring task did not replay the original Lean projects.

The independent mathematical review is in `shared/REVIEW.md`. Exact bounded controls are recorded in `shared/review_check_results.json`. Figure inputs, numerical tolerances, software versions, run history and output hashes are in `shared/COMPUTATION_REPORT.json`. Conservative manuscript proofreading is recorded separately for each piece.

## Corrections to the recovered Riemann argument

Two errors in the archived prime cube barrier report were repaired. A finite interval mass cannot upper bound the full signed infinite sum. The revised proof uses the full absolute triangle majorant and lower bounds it by an interval contribution. Also, a count of every coprime base does not count the squarefree support of the Möbius function. The revised proof supplies the squarefree coprime count and its error term. The repaired conclusion concerns the failure of this absolute upper bound route, and does not give a lower bound for the signed coefficient itself.

The original recovered reports remain unchanged. The new statements and their proofs are distinguished from that history.

## Access limitations and resolved failures

- Historical Riemann checkpoint archive transfers returned HTTP 403. The readable reports and core mathematical source were recovered instead. No unseen archive contents are claimed as inspected.
- Attempts to access original Terras paper downloads returned HTTP 403. The literature report records the available bibliographic sources and the directly verified Tao preprint used for precise density orientation. Original Everett and Guinand text bodies were not available, and are not claimed as independently read.
- The default and primary Python environments initially lacked an importable mpmath module. The successful figure run used a recovered local mpmath 1.3.0 package. The public script uses an ordinary import and provides pinned dependencies.
- An initial Matplotlib fraction label failed to render. Braced fraction syntax corrected it. A first TeX style smoke test also failed because shell quoting consumed a mathematical token. A file patch corrected the test, after which the shared style compiled. These failures did not persist in the final reader builds.
- One extra reviewer check initially expected the wrong final valuation for the orbit from 27. The manuscript did not make that assertion. Correcting the check to the actual valuation made it pass. This is recorded in the independent review.

## Layout and delivery verification

The final TeX sources were compiled twice. Every PDF page was rendered, all page contact sheets were visually reviewed, and mathematical pages and figures were inspected at readable scale. Machine checks found no text outside the page, unresolved placeholders, missing characters, undefined references, or overfull boxes in the final builds. Exact final counts and hashes are recorded in `shared/LAYOUT_VALIDATION.json` and `MANIFEST.json`.

The source archive contains the manuscripts, common design, bibliography and source registers, selected recovered evidence with read metadata, reproducible figures and their inputs, independent arithmetic controls, review and proofreading notes, and both reader PDFs. Build caches and intermediate test files are excluded. Every archived payload was checked against its SHA256 manifest, and the ZIP integrity check passed.
