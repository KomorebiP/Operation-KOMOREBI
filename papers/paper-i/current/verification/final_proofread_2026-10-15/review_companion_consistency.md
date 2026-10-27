# Paper I companion consistency review

Review date: 15 October 2026 (UTC). Review-only. No manuscript source was edited or rebuilt. No Lean command was run. This review compares the preserved 8 October PDFs and their editable TeX with the accepted Block 08 ledger and completion report dated 12 October 2026. It does not independently revalidate that accepted compiler/kernel evidence.

## Scope reviewed

- Main monograph: `editable/traditional/01_orientation.tex` and `06_reference.tex`, including their formalization summaries and concordance text.
- Lean guide: all hand-written text in `editable/lean_guide/Paper_I_Lean_Guide_Final.tex`; generated contract/import tables were treated as preserved historical records, not re-audited.
- Machine companion: hand-written exposition, worked-example descriptions, release instructions, and receipt explanation in `editable/machine/Paper_I_Machine_Native_Final.tex`; the historical evidence fields in the record catalog and Appendix E were inspected for scope consistency. This is not a new proof audit of the 108 generated statement/proof records.
- Current PDF versions: 106-page traditional monograph, 39-page Lean guide, and 98-page machine companion in `publication/pdfs/`.
- Latest status sources: `Paper_I_Block08_Progress_Ledger_v0.8.0.md`, `Paper_I_Block08_Completion_Report_2026-10-12.md`, and the opening of Block 08's `coverage/COVERAGE_108.md`.

## Findings and exact minimal proposed amendments

### 1. Outdated future-work direction in the Lean guide (meaningful correction)

Location: Lean guide TeX line 501; PDF page 24; subsection “Three concrete extension directions.”

Current text:

> For the primary-decomposition rows, a substantive next step is construction of the needed extraction polynomials and scalar-quotient certificates from a stated decomposition theorem, followed by a bridge from a bare operator under explicit field assumptions.

This is stale as a present research roadmap. The 12 October ledger explicitly says the intrinsic primary quotient, geometric formula, scalar-extension bridge, and six-way cyclic criterion are established and must not be reconstructed as missing work. The same ledger names the actual restart: exact-sequence bounds, invariant-submodule packet restriction/quotient descent, packetwise exactness, and induced transfer blocks.

Replace that first sentence only with:

```tex
The separate Block~08 continuation identifies the next algebraic work as exact-sequence generator bounds, packet restriction and quotient descent for an actual invariant submodule, packetwise exactness, and induced transfer blocks. Its accepted ledger records the primary, geometric, scalar-extension, and cyclic-classification blocks as already established.
```

Retain the two following sentences on executable graph-rank refinements and countable packet topology. They remain appropriately scoped open directions.

### 2. Historical guide scope can be mistaken for current overall coverage

Locations: Lean guide opening note, TeX lines 53–58 / PDF page 2; introductory paragraph line 66 / PDF page 5; split-semisimple summary line 294 / PDF page 15.

The guide accurately describes a preserved 20-file v1.0.2 component, 35 contract rows, 84 mapped targets, and 1,126 historical namespace entries. These quantities should not be replaced by the Block 08 counts. The problem is the unqualified present-tense wording “The main formal component” and “The development does not derive a Wedderburn decomposition ... nor the nonsplit division-algebra form.” The later continuation does integrate the actual Wedderburn-Artin existence result and proves the nonsplit formula without taking a decomposition or rank formula as an input.

At the end of the opening note, add a separate paragraph:

```tex
\medskip
\textbf{Later formalization checkpoint.} The separately preserved Paper~I Block~08 package, version~0.8.0 dated 12 October 2026, records 26 covered, 25 partial, and 18 unmapped records among the expanded core's 69 proof-level records. It integrates the actual Wedderburn--Artin existence result and the nonsplit semisimple formula. The 35-row contract, source excerpts, and historical evidence taught below retain their original scope. This proofreading edition reports that preserved checkpoint and claims no new Lean run.
```

At line 66 change the sentence opening only:

```tex
The preserved historical component explained below is the 20-file project
```

At line 294 replace the paragraph with:

```tex
The output is a genuine rank formula for the supplied realization. This preserved 20-file component does not derive a Wedderburn decomposition from an arbitrary semisimple algebra, nor the nonsplit division-algebra form in the expanded paper. The separate Block~08 continuation supplies that later existence integration and nonsplit formula. A reader applying historical row~10 should still identify its supplied equivalences before quoting its conclusion.
```

The single-operator discussion at line 305 says “The file does not independently construct ...” and the cyclic discussion says “in this component.” Those are accurate descriptions of the named preserved file/component. With the front note and corrected future-work paragraph, they need not be rewritten or have their old certificates silently removed.

### 3. Main monograph should point to the newer coverage checkpoint

Location: `01_orientation.tex`, immediately after the “Companion volumes” paragraph at line 16; current PDF page 5.

The main monograph's conclusions and 108-record concordance distinguish written proofs from Lean coverage correctly. There is no false blanket formal-completion claim in the two assigned main-manuscript files. However, the companion-volume paragraph currently sends readers to historical guides without identifying the later accepted coverage map.

Add:

```tex
\noindent\textbf{Formalization checkpoint.} The separately preserved Paper~I Block~08 package, version~0.8.0 dated 12 October 2026, records 26 covered, 25 partial, and 18 unmapped records among the 69 proof-level records in the expanded 108-record core. The companion guides retain their earlier evidence scopes. This edition reports preserved verification and claims no new Lean run.
```

No change is needed to the numerical 108-record concordance or the mathematical conclusions in `06_reference.tex` on formalization grounds. Do not describe 26/69 as a blanket completion percentage.

### 4. Machine companion's frozen eight-record map is valid, but add a newer-status pointer

Location: edition statement after the second paragraph, TeX line 46 / PDF page 2; evidence semantics around lines 137–153 / PDF page 8; historical map PDF page 96.

The machine companion repeatedly says the eight entries map to the “attached historical Lean tranche” and uses `NOT_MAPPED_TO_ATTACHED_SOURCE_TRANCHE`. This is correctly scoped. Its generated catalog fields and Appendix E should remain unchanged. They do not assert that those records lack all later formal support.

After the edition statement's paragraph ending “with differing degrees of source agreement,” add:

```tex
Later Paper~I formalization is recorded separately in the Block~08 package, version~0.8.0 dated 12 October 2026: 26 covered, 25 partial, and 18 unmapped records among the 69 proof-level records. Those later correspondences do not alter this frozen payload's eight-entry historical map or its evidence fields. No new Lean run is claimed by this proofreading edition.
```

The word “current” in the historical receipt may be dated to prevent a new publication date from implying a new execution. Minimal optional amendments:

- `\subsection{Current reproduction}` -> `\subsection{Reproduction for the 8 October edition}` (line 148).
- `\section{Current verification receipt}` -> `\section{Preserved verification receipt}` (line 3615).
- `The following is the successful current run of the documented frozen release gate.` -> `The following is the successful release-gate run preserved from the 8 October edition.` (line 3616).

Do not rerun `build_companion.py` merely to alter the prose without first preserving these hand-written changes: the document says that script generates the TeX and runs checks. A straight TeX render is the proportionate presentation check for these editorial amendments.

### 5. Objective terminology clarification in the Lean guide

Location: line 265 / PDF page 14, paragraph beginning “For several seeds.”

Current text says “when the module is finite.” The actual theorem `Komorebi.SeedRankOperations.seedFinrank_isLeast_free_surjection` has `[Module.Finite A M]`, which means finitely generated as a module, not finite as a set. The surrounding guide already uses “finite generation.”

Replace only:

```tex
when the module is finite
```

with:

```tex
when the module is finitely generated
```

Source check: preserved `SeedRankOperations.lean`, lines 62–65, and `SeedRankBasics.lean`, lines 157–173. This clarification changes prose only, not a mathematical token or theorem hypothesis.

## What should stay unchanged

- Historical source counts, contract-row counts, target names, namespace-entry totals, dependency pins, historical execution dates, and generated theorem maps.
- The machine payload's 108-record identity, frozen source digest, eight attached mapping fields, generated record statements, and proof bodies.
- The original 35-row normative contract. Block 08 explicitly preserves it.
- “No fresh Lean compilation/replay” claims for the editorial companion builds.
- The distinctions between 8 newly compiled production modules, 46 authenticated predecessor source/object pairs, and the 54-module whole-closure logical replay. If these are mentioned, do not say all 54 modules were freshly recompiled.

## Light proofreading outcome

No additional high-confidence spelling, grammar, unmatched-label, or local mathematical-token correction was identified in the assigned hand-written companion prose. The finitely-generated wording above is the one objective terminology clarification. The readable historical listings and generated record proofs were not altered or treated as newly checked formal mathematics.

Validation performed: read-only source/PDF text inspection and targeted source-signature lookup. No TeX build, Python release gate, or Lean verification was run by this reviewer.
