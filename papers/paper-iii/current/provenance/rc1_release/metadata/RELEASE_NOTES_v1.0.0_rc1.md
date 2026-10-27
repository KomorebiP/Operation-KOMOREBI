# Operation Komorebi · Paper III
## Private scoped release candidate v1.0.0-rc1 · 20 October 2026

**Decision: package finalized for private technical review. It is NOT an unrestricted, fully Lean-closed or publicly licensed release.**

### Scope and editorial state

The original 98-page traditional monograph, 26-page verified visual guide and 49-page historical finite Lean guide are preserved exactly from the recovered 8 October package. A new five-page Section 17 mathematical supplement provides explicit, general Banach-space proofs, including continuous range jets, a stronger restricted-jet norm estimate, exact packet Taylor identities with Bochner remainder, and the partition Faà di Bruno formula. The integrated 180-page reading edition has five bookmarks and leaves the original monograph pages unchanged.

The paper's manuscript statement source has been audited by exact text hashing: **167 preserved environments**, of which **100 are result-like** (98 theorem/proposition/lemma/corollary environments and two separately identified classical `standardfact` environments). This is a source census, not a formal proof count or a novelty census. Every source environment hash matched the October 8 crosswalk. The per-record evidence classifications appear in `metadata/MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json` and `.csv`.

### Verified record and what was freshly executed

- **Historical formal core:** The 41-row finite contract retains its recorded 143 targets. Section 16 contains an accepted 12-module production closure with an inherited successful 558 logical declaration replay and 14 separately audited generated runtime helpers. All 12 accepted source files and `.olean` objects were freshly SHA-256 verified against the inherited identities. **No Lean compiler or kernel was run in this closeout.**
- **New Section 17 result:** We proved that the literal continuous range jet has norm at most `||Q||·||B||`, stronger than the manuscript's product-of-input-projections bound. We separately established the latter for the ambient extension. The proof treats zero packet ranges explicitly.
- **Fresh exact tests:** 15,331 Section 16 assertions; 2,622 Section 17 assertions; 677 new independent symbolic higher-order assertions, including derivative orders 1–4, rational polynomial Bochner integral remainders, and a genuinely oblique two-packet system. All passed. Finite exact checks do not certify universal theorems or full computer algebra correctness.
- **Reader QA:** All 180 merged pages have text identical to their corresponding source pages. No text spans beyond the page crop were detected. The proof supplement compiles using pdflatex without overfull boxes.
- **Archive:** New manifest checks every file; ZIP CRC and a fresh extraction verification are required before delivery.

### Unaccepted material and substantive blockers

1. **Fresh Section 17 Lean verification**: The two drafted source modules remain outside production and have not passed the compiler. The pinned Lean 4.34.0-rc2 toolchain and nine dependencies were previously recovered as seven external chunks totaling about 2.9 GB, but those chunks are not present in this workspace. No new Lean code is counted as accepted.
2. **Full expanded manuscript formalization**: The remaining 59 later result-like environments after Section 17 are preserved with ordinary proofs but do not have new accepted exact Lean mappings. Not all expanded mathematical claims have been independently re-proved in this closeout.
3. **October 16 visual claim**: The later visual guide's final page claims 2,693 kernel-replayed declarations and 98+2 formally accepted results. Its matching source and replay receipts were not recovered. The guide is preserved in `provenance/unverified_oct16_visual/`, but is *not* the selected release guide. The claim is unverified, not refuted.
4. **Licensing**: The original `LICENSE_STATUS.md` says no public copying, modification or redistribution license is selected. This private release candidate does not grant rights or impose a license on the user. Public GitHub release requires an explicit author licensing decision and third-party notices.
5. **External review**: Neither peer review nor a full manual audit of every manuscript proof was performed. A complete formalization is not prerequisite for a clearly bounded mathematics paper, but claims of unrestricted formal closure would require substantially more evidence.

### Scope decision

The Section 16 formal continuation is a closed, authenticated **scoped contract**. Section 17 has a closed **ordinary mathematical derivation**, with formal integration open. The rest of the expanded monograph remains a valuable research manuscript with a different formal coverage level. For that reason, this package is versioned as `1.0.0-rc1` instead of being falsely marked `1.0.0 fully formal verified`.

**Do not promote this candidate to a final public release simply by renaming the ZIP.** The next verification block is the pinned Lean compilation and audit of the two Section 17 source candidates, followed by the author’s licensing choice. Broader formal coverage may be a separate research release rather than holding the finite mathematics indefinitely.
