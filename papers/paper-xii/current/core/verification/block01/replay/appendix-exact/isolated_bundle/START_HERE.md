# Paper XII — complete source and evidence bundle

**Komorebi P.**

This bundle combines the reverified v0.17.1 formal release, the unchanged v0.17.0
manuscript, and the 18-page worked visual appendix. It is a packaging release,
not a new mathematical or Lean certification release.

## Open first

- `pdfs/Paper_XII_With_Visual_Appendix.pdf` — complete reading edition, 54 pages.
- `pdfs/Paper_XII_Manuscript.pdf` — original manuscript, 36 pages.
- `pdfs/Paper_XII_Visual_Appendix.pdf` — standalone visual appendix, 18 pages.
- `formal_release/LATEST_STATUS.md` — authoritative formal status.
- `visual_appendix/README.md` — appendix contents, examples, and interpretation limits.

## Where to edit

| Material | Location |
|---|---|
| Current manuscript LaTeX, bibliography, matching `.bbl`, and 18 vector figures | `formal_release/paper/` |
| All 96 registered production Lean modules, including reused Paper X sources | `formal_release/lean/` |
| Compiled project objects, cumulative checks, logs, and claim maps | `formal_release/build/`, `checks/`, `logs/`, and root JSON records |
| Three additional end-to-end claim tests | `formal_release/checks/FinalClaimsConsumer.lean` |
| Appendix typography and document entry point | `visual_appendix/appendix.tex` |
| All appendix prose, formulas, and inline diagrams | `visual_appendix/source/pages.tex` |
| Appendix Python figure generator | `visual_appendix/source/generate_graphics.py` |
| Editable generated TikZ figures | `visual_appendix/graphics/` |
| Exact illustrative-example checks | `visual_appendix/checks/verify_examples.py` |
| Portable original-manuscript Python figure generator | `tools/generate_original_figures.py` |
| Unchanged original generator, original finite checker, and older manuscript package | `history/original_manuscript/` |
| Original archive hashes, member-by-member provenance, and sidecar audits | `provenance/` |

The formal-release and visual-appendix directory trees are preserved byte-for-byte.
The original manuscript's plotting script was recovered from the initial manuscript
package nested inside the v0.15.0 release. Its unchanged copy is kept in `history/`.
Only a separate operational copy has its old absolute output path replaced with an
explicit `--output` option. No drawing rule or production Lean source was changed.

## Integrity check — no third-party Python packages needed

From this directory, in PowerShell, a terminal, or WSL:

```text
python Run-PaperXII.py verify
```

The checker verifies delivered file hashes, all 96 production source/object pairs,
project-local Lean imports, Python syntax, manuscript figure/bibliography references,
appendix graphic references, PDF baseline copies, and source-archive preservation.
This is not a Lean proof replay.

## Rebuild or rerun

With Python 3.10+ and the dependencies in `requirements.txt` available:

```text
python Run-PaperXII.py examples
python Run-PaperXII.py figures
python Run-PaperXII.py appendix
python Run-PaperXII.py manuscript
python Run-PaperXII.py pdfs
```

Each task writes to a separate `build/` copy. Supplied proof evidence, manuscripts,
and final PDFs are not overwritten. Add `--fresh` to replace an earlier generated
build copy. The `pdfs` task rebuilds the main manuscript, then uses that regenerated
PDF as the appendix integration baseline.

For the cumulative Lean replay, run inside Linux or WSL with the existing pinned kit:

```text
python3 Run-PaperXII.py lean --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The inherited direct commands still work inside their own directories. Full details
are in `BUILD_AND_DEPENDENCIES.md`.

## What is and is not included

Included: current project LaTeX, bibliography, Python, Lean, TikZ/vector figures,
PDFs, compiled project objects, replay/check scripts, original-versus-revised claim
ledgers, mathematical reviews, recorded failures/corrections, and verification logs.
The small predecessor archive already carried by v0.17.1 is retained as history.

Not included: the multi-gigabyte Lean compiler/Mathlib portable kit, a TeX
installation, installed Python packages, or font files. Their required versions and
entry points are documented. This is the complete current source/evidence bundle,
not a self-contained operating environment or a collection of every historical release.

## Proof boundary

The inherited v0.17.1 record reports **49/49 revised internal claims complete**.
Its separate original-wording ledger remains **41 complete, 7 partial, 1 unchecked**.
The eight inherited amendments and external arithmetic inputs remain explicit.
The appendix is explanatory material with exact finite/symbolic checks, not new
Lean-certified theorems. Packaging does not establish external arithmetic existence,
classicality, universal companions, or unrestricted Langlands reciprocity.

No Lean build is claimed for this packaging operation. Fresh packaging checks and
any exact-example/generator checks are separated from inherited compiler evidence
in `PACKAGING_REPORT.json`.
