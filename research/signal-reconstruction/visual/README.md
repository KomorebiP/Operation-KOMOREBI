# Signal Reconstruction visual companion

`Signal_Reconstruction_Visual_Guide.pdf`, `.tex`, and `.md` are built from the
same mathematical content in `build_guide.py`. The complete Markdown files are
included. `guide_content.json` retains section text, equations, source anchors,
figure captions, and the explanatory SG crosswalk.

The guide contains 21 original matplotlib figures, each supplied as PDF, SVG,
and PNG. The helix in Figure 15 retains genuine three-dimensional coefficient
and offset geometry. No generated imagery is used.

`generate_figures.py` checks 333 finite assertions using rational and
Gaussian-rational controls. Continuous curves and singular-value diagnostics
use ordinary floating evaluation and do not certify interval bounds or analytic
limits. The finite tested ranges and exclusions are in
`validation/computation_contract.json`.

The current run is `validation/visual_run_final_20261006/manifest.json`, with
scientific results and exact figure hashes in the adjacent
`scientific_result.json`. It completed under 60 seconds wall time, 45 seconds
per-process CPU time, 2 GiB address-space limit, one CPU core, and cooperative
one-thread library caps. Its input and declared outputs passed the v2 manifest
validator. External dependency payload provenance and freshness are recorded in
`../verification/DEPENDENCY_PROVENANCE.json` and
`../verification/DEPENDENCY_FRESHNESS.json`; the manifest itself records versions
and the listed input driver hash, not the complete external dependency closure.

The earlier `validation/visual_run_20261006` is superseded. Its manifest was
preserved unchanged. `validation/HISTORICAL_RUN_STATUS.json` identifies the exact
matching historical driver and result/log validation root. Those 333 repeated
assertions are not counted again. The old figure payloads were replaced; their
recorded hashes describe the historical drawing, not final figures.

`validation/draft_checks.json` is also superseded preliminary output. It reports
334 checks including one vacuous empty-preparation check later removed, and
earlier figure hashes. It was not produced under the bounded runner and is not
current publication evidence. The unchanged draft is indexed with its hash in
`HISTORICAL_RUN_STATUS.json`. The final 333-assertion result is authoritative.
The computation contract remains current: its tested bounds and conventions
apply to the final run, whose actual driver hash is pinned by the manifest.

`validation/LAUNCH_ATTEMPT.json` records an initial pre-execution rejection:
the runner could not locate a relative contract path from the caller directory.
The corrected absolute path launched the succeeding bounded run.

Rebuild prose and PDF from the release root:

```sh
python3 visual/build_guide.py
python3 build_release.py --only visual
```

Regenerate figures under a fresh bounded manifest with the mathbox
computation-audit runner, using the recorded contract, driver, and caps. Select
a new output directory; the runner does not overwrite existing evidence.

`validation/source_anchors.json` records exact raw file hashes and selector
locations. `validation/claim_crosswalk.json` pins the current traditional claim
catalogue. The map is explanatory coverage, not a claim that every complete
traditional proof is reproduced in the visual guide.

Related earlier Lean sources do not certify this complete unknown-edge and
self-calibration paper. No fresh Lean verification is claimed here. The complete
release records distinguish inherited formal evidence, source inspection,
fresh finite numerical runs, and open conditions.
