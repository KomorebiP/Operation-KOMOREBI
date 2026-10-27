from pathlib import Path
import json,hashlib,datetime
r=Path(__file__).resolve().parent.parent/'publication'
receipt=Path(__file__).resolve().parent.parent/'verification/centered_run02/receipt.json'
proof=json.loads(receipt.read_text())
assembly=json.loads((r/'book/assembly_validation.json').read_text())
remaining=[
 'Abstract unbounded spectral-functional-calculus API identification',
 'Sampling, interpolation, aliasing and domain comparison with a changing finite spatial grid',
 'Background gauge operator domains and coupled dynamical gauge or gravitational evolution',
 'Resolution of the retained production-energy obstruction by a controlled physical mechanism',
 'Full historical cumulative/gauge evidence audit beyond the exact replayed targets',
 'Independent specialist review of the complete mathematical and physical manuscript'
]
readme='''# Komorebi Physics
## Continuum, Geometry and Refinement

Open `Komorebi_Physics.pdf` for the complete book: **{pages} pages**, comprising one unnumbered cover, seven preliminary pages numbered i–vii, and {arabic} pages numbered 1–{arabic}. The twelve-page `Komorebi_Physics_Design_Preview.pdf` retains the selected pages' printed folios. The seven research themes, five visual atlases, numerical figures, and established typography are preserved.

The current free-field extension has accepted Lean proofs for the bounded centered operator, graph convergence on the complete maximal Hamiltonian domain, actual resolvents at every nonreal spectral parameter, and quadratic error bounds under a finite third-order Fourier moment. The abstract spectral-functional-calculus API identification remains open. These results concern a fixed infinite Fourier space; they do not close the sampled-grid, interacting-field, or cosmological production problems.

## Package map

- `source/`: editable LaTeX, styles, figure assets, and retained scientific data.
- `compiled/`: eighteen component PDFs and final TeX logs.
- `book/`: front matter, reading text, assembly specification, page map, and navigation validation.
- `audit/`: current publication QA, complete-book renders, source-preservation review, and earlier editorial records.
- `formal/continuum/`: the integrated Lean project, precise replay instructions, controls, declaration audit, and current and failed verification records.
- `reference_record/`: unchanged earlier computation and provenance records.
- `history/publication_v0.50.0-g1_metadata/`: the preceding README, release reports, and package manifest, preserved as history.

Original material is licensed under `LICENSE`; third-party rights remain unchanged. Historical filenames and counts identify earlier checkpoints and are not relabelled as new checks.

## Rebuild the publication

Required: Python dependencies from `requirements.txt`; XeLaTeX, PDFLaTeX, and `kpsewhich`; the packages imported by the preambles; and separately installed URW Base35 OpenType, Latin Modern, TeX Gyre Type 1, and Palatino-compatible mathematical fonts. No font files are redistributed in this package.

The XeLaTeX sources use `source/monographs/font-location.tex`, whose Linux default is `/usr/share/fonts/opentype/urw-base35/`. The outer-book script locates TeX Gyre Pagella and Heros metrics and programs with `kpsewhich`.

From the package directory:

```text
python3 build_documents.py
python3 assemble_reading_volume.py
python3 audit_design.py
python3 render_design_audit.py
python3 tools/build_design_preview.py
```

The first command makes three passes per component and accepts filename substrings for a partial rebuild. Assembly preserves vector pages and rebuilds internal destinations. The audit checks final logs, text bounds, fonts and navigation. PDFium renders every book page. The current scoped preservation comparison is `audit/source_preservation_centered.json`; the inherited generic baseline-comparison mode intentionally does not accept the two reviewed hypothesis clarifications in this update.

To regenerate only the current verification-scope schematic:

```text
python3 tools/render_formal_scope.py --publication-root . --accepted-proof-record formal/continuum/verification/block51/current/receipt.json
```

This schematic is separate from numerical figure generation. Layout reproduction requires compatible TeX and font versions; byte-identical cross-platform output is not promised. Document builds do not rerun Lean or scientific experiments. The retained atlas generator references an original-tree `evidence/figure_checks.json` that is absent from this publication copy. That omission and the historical reproduction limitations remain explicit.

## Replay the formal extension

Read `formal/continuum/README.md`. Restore the exact portable Lean 4.34.0-rc2 runtime externally; it is not bundled in the source ZIP. From `formal/continuum`, run:

```text
python3 verification/block51/current/snapshot/runner/verify_centered.py --project . --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --controls CONTROL_MANIFEST.json --out-dir /absolute/path/to/a-new-verification-directory
```

The output directory must be new. Preserve the pinned compiler and dependency identities. The accepted receipt is `formal/continuum/verification/block51/current/receipt.json`, with status `PASS_SCOPED_CENTERED_EXTENSION`.

The accepted run compiled 26 local targets through 64 recorded commands, audited 209 environment declarations (162 new plus 47 generator), completed five module kernel replays, and passed 21 controls: eight positive, twelve elaboration rejections, and one custom-axiom policy rejection. The four new modules contain 74 explicit theorems, 15 definitions and 11 abbreviations; generated auxiliaries explain the larger environment count. Source, objects and relevant runtime identities remained stable.

These checks reuse pinned external compiled dependencies and the same Lean kernel. They do not rebuild the compiler or all Mathlib, provide an independent proof assistant, or certify every historical physics module. Failed attempts remain in the record.

## Publication verification boundary

Five affected component documents were rebuilt. All {pages} book pages rendered successfully, with valid bookmarks and internal destinations. All 107 original explicit proof bodies, 157 source data files, and numerical image assets are unchanged. Exactly two original theorem-like statements add the explicit hypothesis `T >= 0` for a compact-time envelope/supremum. The nonzero-spacing and third-order-moment hypotheses and the coefficient `1/6` remain unchanged. Only the verification-scope diagram changed among the image assets.

The five numerical suites belong to the preceding publication checkpoint; they were not rerun for this formal extension. The production-energy obstruction remains in the book. This is a focused formal-extension and publication audit, not an independent line-by-line review of every chapter or bibliography.

See `RELEASE_VERIFICATION.md`, `RELEASE_VERIFICATION.json`, `audit/continuum_publication_qa.json`, and `formal/continuum/PROGRESS_LEDGER_v0.51.0.md` for the accepted scope and remaining work. The final package manifest records identity, not mathematical validity.
'''.format(pages=assembly['page_count'],arabic=assembly['arabic_pages'])
(r/'README.md').write_text(readme)
release={
 'schema':'komorebi.physics.release.verification.2',
 'checkpoint':'v0.51.0',
 'status':'PASS_SCOPED_CENTERED_EXTENSION_AND_PUBLICATION',
 'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'formal_receipt':'formal/continuum/verification/block51/current/receipt.json',
 'formal_receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),
 'formal_status':proof['status'],
 'mathematical_scope':'Centered bounded self-adjoint operator for nonzero signed spacing; maximal-domain graph convergence; actual nonreal resolvents, inverse identities and strong convergence; third-order moment quadratic generator and propagator rates; physical Fourier transport.',
 'new_explicit_declarations':{'theorems':74,'definitions':15,'abbreviations':11},
 'environment_declarations':{'total':209,'new':162,'unchanged_generator':47},
 'local_targets':26,'commands':64,'kernel_replays':5,
 'controls':proof['control_counts'],
 'identity_stable':{'source':proof['source_unchanged'],'objects':proof['objects_unchanged'],'relevant_runtime':proof['relevant_runtime_unchanged']},
 'trust_boundary':'Pinned external compiled dependencies reused. Replays use the same Lean kernel and imported environment. No compiler bootstrap, dependency-source rebuild, independent kernel or whole-physics certification.',
 'document':{'pages':assembly['page_count'],'arabic_pages':assembly['arabic_pages'],'bookmarks':assembly['bookmarks'],'sha256':assembly['output_sha256'],'qa':'audit/continuum_publication_qa.json'},
 'source_preservation':'audit/source_preservation_centered.json',
 'numerical_evidence':{'rerun_in_this_extension':False,'prior_checkpoint':'v0.50.0-g1','prior_suites':5,'numerical_assets_and_source_data_unchanged':True,'atlas_original_manifest_missing':True},
 'historical_metadata':'history/publication_v0.50.0-g1_metadata/',
 'remaining':remaining,
 'boundary':'This release report summarizes the exact formal receipt and publication QA; it is not a fresh numerical or whole-book specialist audit.'
}
(r/'RELEASE_VERIFICATION.json').write_text(json.dumps(release,indent=2)+'\n')
md='''# Current verification record: v0.51.0

The centered free-field extension is accepted with status **PASS_SCOPED_CENTERED_EXTENSION**. Its exact receipt is `formal/continuum/verification/block51/current/receipt.json` (SHA-256 `{receipt_hash}`).

The result covers the bounded self-adjoint centered operator for nonzero signed spacing, graph convergence on the complete maximal domain, constructed continuum and centered resolvents with both inverse identities at every nonreal spectral parameter, strong resolvent convergence, and quadratic generator/propagator bounds under an actual summable third-order Fourier moment. The physical-space results use the existing Fourier isometry. Compact-time envelopes explicitly require `T >= 0`.

The accepted run records 26 local target compiles and 64 commands; 209 audited environment declarations (162 new and 47 unchanged generator); five module kernel replays; and 21 controls (8 positive, 12 elaboration rejections, 1 custom-axiom policy rejection). The new source contains 74 theorems, 15 definitions and 11 abbreviations. Only `propext`, `Classical.choice` and `Quot.sound` occur as axiom dependencies. Source, object and relevant runtime identities remained stable.

## Trust boundary

The exact portable Lean 4.34.0-rc2 runtime and external compiled dependencies are pinned and reused. Kernel replays use the same Lean kernel and imported environment. This is not a compiler bootstrap, full Mathlib source rebuild, independent proof-assistant verification, or cumulative audit of every historical physics module. The runtime is not bundled in the source ZIP. Follow `formal/continuum/README.md` for a fresh replay into a new directory. Failed development and gate attempts remain separate from accepted records.

## Publication checks

The full book has {pages} pages and {bookmarks} bookmarks. Five affected components were rebuilt with three TeX passes; the full book was assembled and every page rendered. Final PDF/log/navigation checks and visual-review records are in `audit/continuum_publication_qa.json`.

All 107 original proof bodies are unchanged. Two original theorem-like statements explicitly add `T >= 0`; other original mathematical statements and displayed equations are preserved. All 157 source data files and all numerical image assets are byte-identical. Only the verification-scope schematic changed among 196 image assets. Status prose and technical declaration correspondence were updated without redesigning the five visual atlases.

An initial assembly failed because this runtime lacked the declared TeX Gyre Type 1 dependency. The dependency was restored and assembly rerun successfully; failure and restoration logs remain in the publication audit notes. A sparse intermediate generator layout was corrected by shortening status prose. Neither issue altered scientific data or proof bodies.

The five numerical suites were rerun at the preceding v0.50.0-g1 checkpoint, not during this extension. The retained atlas script references an original-tree `evidence/figure_checks.json` absent from this publication copy. Earlier numerical logs and the production-energy obstruction remain explicit. No new empirical or production-mechanism claim is made.

## Remaining work

{remaining}

The prior README, release report and manifest are preserved under `history/publication_v0.50.0-g1_metadata/`. Current source-preservation review is `audit/source_preservation_centered.json`; the detailed restart ledger is `formal/continuum/PROGRESS_LEDGER_v0.51.0.md`.
'''.format(receipt_hash=release['formal_receipt_sha256'],pages=assembly['page_count'],bookmarks=assembly['bookmarks'],remaining='\n'.join('- '+s+'.' for s in remaining))
(r/'RELEASE_VERIFICATION.md').write_text(md)
print('metadata written',assembly['page_count'],assembly['output_sha256'])
