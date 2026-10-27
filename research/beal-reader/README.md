# The Beal Conjecture

Komorebi P. · Operation Komorebi · Conjecture Series 05 · Reader edition 1.0 · 8 October 2026

This set contains a full mathematical paper and a separate visual guide. The paper explains the general conjecture, the recovered work on the (3,5,7) signature, the exact local and finite representation calculations, and the restricted affine obstruction at the current research boundary. This work does not prove the general Beal conjecture or complete the recovered signature route.

## Deliverables

- `pdf/Komorebi_Beal_Conjecture_Piece_v1.0.pdf`
- `pdf/Komorebi_Beal_Visual_Guide_v1.0.pdf`
- LaTeX sources in `paper/` and `shared/`
- Exact figure generator, data, and source descriptions in `visual/`
- Literature leaves, internal proof review, exact computation replays, formal checks, and layout evidence in `evidence/`

## Rebuild the readers

Run from the extracted project directory:

```sh
python3 build.py --figures
python3 quality_check.py
```

The reader build uses Python, matplotlib, and TeX with the packages named in the shared preambles. Version records appear in `evidence/AUTHORING_ENVIRONMENT.json`. Rebuilding with another TeX installation may change PDF bytes without changing the mathematics. Exact input data and source hashes are the principal reproducibility anchors.

`evidence/COMPUTATION_AUDIT.md` and its reproduction instructions distinguish successful fresh runs of the original archive verifiers from the portable scientific replay included here. The latter uses the exact selected code and input snapshots, without claiming to run archival integrity checks on excluded nested archives. `evidence/FORMAL_STATUS.md` gives the exact compiler, dependency revision, checked sources, axiom outputs, and formalization limits.

## Reading the evidence

`evidence/PROOF_AUDIT.md` gives the internal independent mathematical review. The final source hashes in `evidence/REVIEW_PINS.json` identify its reviewed revision. Hashes, theorem counts, and finite output agreement do not supply a proof of arithmetic realization.

The current endpoint is a canonical affine obstruction. Homogeneous kernels and synthetic targets cannot replace its actual arithmetic origin. The recovered upstream Frey and residual-pattern hypotheses remain explicit. The paper also reports a recent external claim about the (3,5,7) equation within the literature review's stated scope, without certifying that separate proof.

`AUTHORING_REPORT.md` records the final edition, corrections, checks, and release boundaries. Failure records are preserved alongside passing final checks.

## Historical preservation

The latest cumulative Block 80 archive and four companion records were recovered. All 35 nested archive nodes were authenticated and decoded for inspection. Block 51 has four predecessor branches rather than one chain. Older work is also contained in the accumulated Block 47 payload. No claim is made that distinct archives for Blocks 1–46 were recovered.

The original complete archive remains unchanged outside this distributed release. It contains a third-party full paper and its text extraction, as well as captured external pages. The release preserves 1,949 original nonZIP historical payload files byte for byte under `evidence/recovered/Preserved_Payload/`, including 18 original manifests, proofs, code, data, failure logs, and historical disclosures. It excludes the 97 external paper, full-text, and HTML capture files. `evidence/recovered/PAYLOAD_SELECTION.json` records every included and excluded source hash. `evidence/RECOVERY_INPUTS.json` authenticates the original whole archives and their relations.

Original manifests describe the historical complete packages. They are retained unchanged, with no claim that every listed excluded file is present in this selected release. Pacetti and Villagra Torcomian's source code and numerical data retain their original attribution and provenance. They are not new Operation Komorebi algorithms or freshly executed GP/Magma outputs.

Downloaded external papers, compiler runtimes, mathlib caches, and private transfer helpers are excluded from the release.

Three bounded figure-development snapshots remain under `visual/computations/` as ZIPs. They contain this edition's own figure code, 24 figure pairs, source snapshots and run records. They preserve earlier accepted visual revisions and are distinct from the excluded complete historical archives.
