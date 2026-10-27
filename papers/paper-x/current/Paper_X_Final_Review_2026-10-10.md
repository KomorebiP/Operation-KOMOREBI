# Paper X: final reading-edition review

**Date:** 10 October 2026  
**Title:** Universal Residual Seeds: Deformation forests, transport categories, and conditional system completion  
**Author:** Komorebi P.  
**Disposition:** Coordinated monograph, visual guide, and formal-evidence reader release. The mathematical contract and verification boundaries below are part of this disposition.

## 1. Delivered readers

| Volume | Pages | Content |
|---|---:|---|
| Traditional monograph | 90 | Retained mathematical development, residue-counting continuation, final conditional assembly, and the integrated thirty-page atlas. |
| Visual guide | 33 | Two current-contract pages and thirty worked atlas pages, plus cover. |
| Lean and evidence guide | 35 | Twenty-record correspondence, explanatory chapters, exact assumptions, countermodels, and four complete production-source listings. |

There are **158 PDF pages** in the coordinated set. The same thirty atlas pages intentionally occur in both the monograph and standalone visual guide. This is duplication for reading convenience, not sixty independent additions. The predecessor readers had 57, 33, and 8 pages respectively.

The canonical PDFs are under `publication/pdfs/`. Keep them in the same directory to retain the formal guide's relative companion links. `CURRENT_PUBLICATION_LOCATORS.json` gives the final statement and atlas routes. All substantive original numbered proof statements and explicit proof bodies remain present.

## 2. Recovery and source preservation

The input was recovered from the Library as `Komorebi_Papers_IX-X_2026-10-05.zip`, version 1. The Library snapshot contains the 8 October integrated Paper X update despite the archive's earlier filename date. Its SHA-256 is:

`c16436eab128d4ea05bb992f35bd7c9db50974e10dd37d6c2733e3cdb2d231cf`

The original archive passed its ZIP CRC check. The integrated Paper X directory and inherited Paper X baseline were recovered. Unrelated Paper IX content was not copied into this release. The input recovery register records 6,259 recovered files and their original hashes.

Fresh comparison preserves **6,170 inherited evidence files byte for byte** across `formal_preservation/`, `inherited_baseline/`, `current_continuation/`, and `status_records/`. This is a preservation result, not a new mathematical audit of every preserved file. All **16 explicit main-manuscript proof environments** are unchanged. All **20 theorem/proposition/corollary records** are unchanged except for newly inserted PDF locator labels. Original versions of edited presentation files are retained in `predecessor_files/`.

The compact formal store verifies **3,079 distinct payloads** at **13,730 mapped leaf occurrences**. It retains checked conditional, later residual-attempt, and terminal-history content with a restoration map. It preserves exact extracted leaf bytes, **not original nested ZIP container streams**. No font binaries or software installation are distributed.

See `verification/2026-10-10/INPUT_RECOVERY.json` and `SOURCE_PRESERVATION.json`.

## 3. Actual proofreading corrections

### Digit extraction

The displayed algorithm in Appendix A omitted the floor in `x_m / p^(m-1) mod p`. The implementation already used integer floor division. The corrected display is:

`a_(m-1) = floor(x_m / p^(m-1)) mod p`.

For compatible canonical representatives `0 <= x_m < p^m`, setting `x_0 = 0` also gives

`a_(m-1) = (x_m - x_(m-1)) / p^(m-1)`.

The reader explains why base-five residues 4 and 19 give the second digit 3 rather than the rational value 19/5. Regression tests cover exhaustive bounded canonical towers, noncanonical representative shifts, invalid towers, and the omitted-floor counterexample. No implementation was silently changed to conceal the publication error.

### Status and reading flow

The original historical Block 27 frontmatter has been retained in the historical appendix rather than left as competing live status at the front of the current edition. The visual guide's initial and final checklists distinguish:

- Historical **17/20**: the Block 27 and scalar/Mellin checkpoints at their own source revisions.
- Recorded checked **20/20**: the later amended conditional occupied-system contract.
- Later **19/20**: a stronger residual-system attempt with no promoted terminal endpoint and an unavailable pinned Lean executable.

The revised opening route and formal guide make the rational-base scope of the printed arithmetic source explicit. They also separate construction, comparison, and occupancy. Historical details remain accessible instead of being erased or retroactively promoted.

### A substantive formal reader

The formal guide is expanded from 8 to 35 pages. It explains the residual partition, convergence distinction, inverse-limit coherence, finite-level compactness, weighted and singular counts, chain-projector conditions, directed seed rank, horizontal admissibility, arithmetic separation, carrier presentations, capacity restrictions, local comparison inputs, and the exact terminal conjunction.

Its four complete source listings total **1,117 lines**: the 291-line terminal module and its three direct dependency modules. They are byte-preserved executable sources. The printed views use reversible typographic escapes for braces and two unsupported glyphs. The executable Lean files are unchanged.

Terminal source hash:

`ba15fd1ea175fecfcc705243c75d1061c8bdf500221dafe86f29fe1c5d21c5e0`

`SOURCE_EXCERPT_LINEAGE.json` and `PRINTED_SOURCE_MANIFEST.json` identify every listing. Four displayed modules are not a standalone transitive Lean project. The full inherited source histories remain in the preservation tree.

## 4. Fresh bounded checks

The delivered runner passed all **seven gates**, with separate logs:

| Gate | Actual result |
|---|---|
| Compact source preservation | All 3,079 payload hashes and 13,730 leaf mappings verified. |
| Reader/source integrity | The 6,170 evidence files, 16 proof bodies, 20 numbered records, and four printed sources matched their stated preservation contracts. |
| Reader regressions | **13 unittest methods passed**, including all **3,123 canonical towers** through depth four over bases 2, 3, 5, and 7. |
| Visual exact checks | **263 positive assertions passed; 14 false controls were rejected.** |
| Original companion tests | **28 pytest tests passed.** |
| Original worked models | Model generation completed, including sixteen figure pairs, seed-rank and finite-occupancy examples. |
| Residue saved-object checks | **255 saved source/object hash pairs** matched. This is not a compiler run. |

The regression examples also test that residual invariance need not imply convergence, pairwise occupancy need not imply joint occupancy, two independent existential conclusions need not share a witness, and zero multiplicity does not imply nonzero occupancy. These are exact bounded illustrations of logical distinctions, not new universal arithmetic theorems.

Test counts are not added into a single inflated assertion total. Some checks overlap. The reports identify their domains and bounds.

Six separate release-engineering controls verified a positive integrity case, rejection of modified bytes, missing files, unsafe manifest paths, unexpected extra files in strict mode, and a missing-TeX-engine failure that returns nonzero and removes a stale output PDF.

## 5. Publication and reproducibility checks

The final coordinated build passed **3/3 documents with no reported TeX warnings**. A clean isolated rebuild also passed all three documents. Every corresponding PDF page has identical ordered text and identical 86.4-dpi raster output.

**Strict binary reproducibility did not pass.** The only PDF byte differences are generated trailer identifiers. After removing only those identifiers from the comparison, each complete PDF byte stream matches. Both sets of original hashes are recorded in `REBUILD_COMPARISON.json`. The delivered PDFs are not presented as byte-identical rebuild products.

The final publication validator resolved **99 internal PDF links**, **20 relative companion links**, **20 numbered statement routes**, and all **30 duplicated atlas page pairs**. Page counts are 90, 33, and 35. It found no out-of-page text spans under its stated bounds.

All **158 pages** were rendered and inspected through **14 contact sheets**. Ten selected pages were independently rendered with Poppler at 144 dpi and inspected at larger scale, including the corrected digit formula, final assembly, revised visual checklist, explanatory logical distinction, complete arithmetic-separator source, and a formerly unsupported direct-sum glyph. Cached reviewed page renders were compared against the final PDFs and matched exactly. The internal visual review found no clipped text, overlapping text, malformed panels, or missing mathematical glyphs in those rendered pages.

## 6. Failed attempts and repairs

The first residue replay was invoked without its required mode argument and failed. The corrected command uses the original residue package and `--verify-only`; it then passed the 255-pair saved-hash check. The compact current continuation alone was not misreported as a runnable complete replay package.

The inherited publication driver reported overall exit status zero even though the Lean reader failed its math-font lookup. That failure was not counted as a three-document pass. The revised driver uses the installed TeX math-font filename, checks per-document results, returns nonzero on failure, and removes stale success-shaped PDFs.

During the revision, a wide visual checklist table overflowed, and a newly printed direct-sum glyph was absent from the code font. The table was reflowed and the printed glyph given a reversible mathematical rendering. A remaining bold-math warning and a mathematical heading's PDF-string warning were repaired. Long module-name tags in the residue appendix were made breakable. The final build has no such warnings.

Appending the atlas initially dropped nine named-destination links. They are now restored as explicit internal links. Twenty cross-document links initially used an incorrect literal destination prefix; they now target the actual manuscript destinations. The final validator checks them.

A build call and a later combined rendering call were interrupted by tool execution limits. Clean reruns completed the builds and remaining page renders. Interrupted attempts are not counted as successful builds or reviews. The original failures and revised logs remain under the dated verification directory. A first fresh-extraction replay was also interrupted during figure generation after five completed gates. The final runner explicitly selects the headless Agg backend and marks a suite complete only after all seven gates have returned. Two bundled delivery-review tool calls timed out while orchestrating model generation. Invoking the delivered replay command directly completed all seven gates. The cause of those tool-level timeouts was not established. Interrupted partial records are retained and are not full-suite passes. A post-replay integrity check then correctly detected eight generated Python bytecode caches rewritten after extraction. Those non-source caches have been removed, and the runner now disables bytecode writes. The final delivery receipt requires a strict manifest pass before and after replay.

## 7. Exact mathematical endpoint and remaining scope

The terminal theorem is

`PaperX.ConditionalOccupiedSystemCompletion.conditional_occupied_system_completion`.

Its first branch constructs a transported target family from actual completed source members, all-depth admissible horizontal transport, finite quotient hypotheses, and inverse-limit closure of the target profile. Its second branch recovers a split summand inside a supplied compatible carrier from explicit constituent presentations, admissible multiplicities, arithmetic trace separation, and supplied local comparisons.

These are **independent conjuncts**. The terminal source does not manufacture an isomorphism between their witnesses, identify their local structures, or supply a missing comparison merely because both outputs are called a system. Zero multiplicities are allowed. Nonzero occupancy needs an additional nonzero premise. The carrier theorem is pointwise at an arbitrary distinguished coefficient place; application at every place needs the corresponding presentations there.

The printed arithmetic source uses the rational absolute Galois group. Broader number-field wording in retained historical prose is not automatically promoted to the same formal scope. No universal companion existence, universal carrier existence, automorphic occupancy, or general arithmetic attachment theorem is asserted by this editorial release.

## 8. Inherited Lean evidence versus this pass

The saved conditional release records two warnings-as-errors builds from separate frozen-cache copies, equal corresponding proof objects, source checks, and transitive axiom audits allowing `propext`, `Classical.choice`, and `Quot.sound`. False proofs, placeholders, and omitted premises are controlled. The injected custom axiom **compiled and was then detected by the audit**; it was not rejected by Lean merely for being an axiom.

Those are inherited source-bound records. Their frozen dependency caches and execution assumptions are not transformed into a full cold transitive replay by this document build. The pinned Lean version is 4.34.0-rc2, with commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

**No Lean or Lake executable was available on PATH for this pass. No fresh Lean/Lake compilation or external peer review occurred.** The source preservation, exact examples, PDF builds, layout review, and package integrity checks are the fresh results.

## 9. Delivery records

`MANIFEST.json` covers the frozen package files by size and SHA-256. The standard-library `verify_release.py` checks that contract. The external dated delivery-verification JSON records final ZIP CRC, archive hashes, fresh extraction, and replay results against the delivered archive without making the archive's own digest self-referential. See `BUILD_AND_VERIFY.md` before rebuilding or restoring historical sources.
