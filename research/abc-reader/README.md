# The abc Conjecture

Komorebi P. · Operation Komorebi · Conjecture Series 04 · Reader edition 1.0 · 8 October 2026

This set contains a substantial mathematical reader and a separate visual guide. It brings the recovered prime-contact corpus, signed-filter route, September jet determinant block, and IUT/KTG proof interface into one account. The exact reductions and stated local determinant results do not supply a proof of the uniform abc inequality.

## Deliverables

- `pdf/Komorebi_ABC_Conjecture_Piece_v1.0.pdf`
- `pdf/Komorebi_ABC_Visual_Guide_v1.0.pdf`
- LaTeX sources in `paper/` and `shared/`
- Exact figure generator and figure data in `visual/`
- Source authentication, literature leaves, proof review, finite replays, formal status, and layout evidence in `evidence/`

## Rebuild the readers

Run from the extracted project directory:

```sh
python3 build.py --figures
python3 quality_check.py
```

The build uses Python, matplotlib, and a TeX installation with the packages named in the two shared preambles. Computation replays also use SymPy. `evidence/AUTHORING_ENVIRONMENT.json` records the versions used for this edition. PDF byte identity across different TeX installations is not promised. Exact mathematical data and source hashes provide the reproducibility anchors.

The standalone computation scripts, contracts, captured outputs, and manifests in `evidence/computation/` record their tested ranges and invocation details. `evidence/FORMAL_STATUS.md` distinguishes the exact pinned compiler replays, the source revisions checked, and the propositions outside their formal scope. Compiler runtimes and downloaded mathematical source papers are not bundled.

## Reading the evidence

`evidence/PROOF_AUDIT.md` records the independent mathematical review and its scope. The revision hashes in `evidence/REVIEW_PINS.json` authenticate the reviewed reader sources. These hashes and static checks do not themselves prove a theorem. `evidence/LITERATURE_CHECK.md` gives the exact external source leaves and the search boundary, including the current published claims and differing IUT assessments.

`evidence/COMPUTATION_AUDIT.md` separates freshly executed finite checks from written general proofs. The finite computations do not establish abc, global arithmetic realization, or the IUT witness obligation. `AUTHORING_REPORT.md` records editorial changes, corrections, verification, and limitations.

## Historical inputs

The seven recovered ABC archives are retained byte for byte in `evidence/recovered/`, including their historical disclosures, status files, and failure records. They are evidence of prior revisions and do not override the new reader's corrected statements. The separately recovered IUT/KTG archive contains four third-party full papers. The release includes its original non-paper payloads unchanged, the original manifest and replay record, and the original whole-archive hash, while excluding those full papers from redistribution. `KTG_PAYLOAD_SELECTION.json` records this selection explicitly. No retained historical file was silently rewritten.

The private external literature cache is excluded from the release. Bibliographic identifiers, authenticated hashes, precise theorem leaves, and acquisition outcomes remain in the evidence reports.
