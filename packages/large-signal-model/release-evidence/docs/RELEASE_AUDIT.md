# PR-LASM 2.3.0 release audit

**Author:** Komorebi P.  
**Date:** 9 October 2026  
**Scope:** locally verified finite-core source handoff. No remote publication.

## Release identity and lineage

The authoritative core predecessor is `Komorebi_PR_LASM_GitHub_Ready_2.1.0.zip`,
SHA-256 `63418283d5e7fdea5744a27252d0af0c79048b3a1b3e8a5ef46e7ebe25b7bbd7`.
Its hash and archive integrity were checked before modification. The standalone
ARC3 agent 2.2.0 is a separate distribution, not the core predecessor. The core
and that agent share `komorebi_arc3_offline` and must not be co-installed.

The original ARC2 0.4.0 diagnostic, October signal reconstruction corpus and
Euler–signal bridge remain separately identified companions. Their preservation
is not integration, a new proof certificate or a transfer of benchmark scores.
Exact recovered-archive hashes and CRC checks are in `verification/SOURCE_LINEAGE.json`.

The core license remains all rights reserved / `LicenseRef-Proprietary`.
Public open-source publication needs the owner's explicit license decision.
The publication workflow cannot publish automatically on a tag push. Manual draft
publication additionally runs the intentionally blocked owner-license gate.
No GitHub repository, release or package index was modified in this work.

## Freshly executed verification

| Check | Result |
|---|---:|
| Core source tests | 184 passed |
| Core plus optional fixture tests | 192 passed |
| Warnings policy | Treated as errors |
| FIR and streaming combinations | 2,025 passed |
| Additional irregular-image cases | 160 passed |
| Additional signal lengths | 160 passed |
| Controlled operator family identification | 35 / 35 |
| Controlled atlas identification | 35 / 35 |
| Synthetic interactive systems | 4 / 4 solved |
| New worked examples | 8 executed successfully |

The fixture run used the separately supplied 25-environment archive. Its eight
checks inspect structure, metadata and static planning inputs. They do not execute
official ARC games. The game source trees were removed from the distributable copy.

The full source suite is recorded in `verification/full_tests.log` and
`verification/full_tests.xml`. The final installed-wheel and clean-source checks
are recorded separately in `verification/packaging_verification.json` and its logs.
A configured CI job is not counted as an executed test.

## Numerical observations

- Maximum normalized FIR discrepancy: `4.7697596881976109e-16`.
- Maximum normalized streaming discrepancy: `3.1582592111298392e-16`.
- Maximum additional irregular-image reconstruction residual: `1.7763568394002505e-14`.
- Maximum additional signal reconstruction residual: `2.6645352591003757e-15`.
- Original 24-frame control's maximum Haar residual: `2.4868995751603507e-14`.
- Original control's maximum selected-basis residual: `1.9539925233402755e-14`.

The FIR normalization is `max(1, max(abs(reference_output)))`. The independent
reference is `numpy.convolve`. These are measured finite float64 checks, not
arbitrary-precision or all-input numerical guarantees.

The shuffled-training-target negative control produced RMSE
`0.0104662263247` with intact pairing and
`1.92162941476` with shuffled pairing on the same
unseen test rows. Its ratio was `183.602891351`.
This supports dependence on the trained correspondence, not universal robustness.

## Model-selection protocol and bounded performance claim

Each operator case has 120 independent synthetic typed-feature records. The model
receives 84 training rows: 63 for preliminary coefficient fits and 21 for candidate
scores, followed by refitting on all 84 training rows. The remaining 36 target rows
are never supplied to fit. These are feature-space mechanism controls whose
intended families are represented in the candidate grammar. They are not a
raw-sensor, raw-image or free-running time-series benchmark.

The current seven-scenario median state-RMSE ratio to the current single-linear
portfolio is `0.112483314896`. Across five seeds and 35 cases
it is `0.112383666822`. These ratios concern state outputs.
In 5 of the seven current cases, scalar-outcome RMSE is worse than the baseline.
Both state and scalar metrics remain in the row-level ledgers.

The historical ratio near 0.239 used a different refit protocol and is not a
like-for-like predecessor performance comparison. Normalized finite-candidate
weights are not open-world truth probabilities. Clipped win/loss heads are not
empirically calibrated event probabilities.

The four synthetic game runs used 85 committed actions,
28 explicit probe actions and 4 resets in total.
Their success is an integration result under that probe/reset protocol, not a
single-trajectory official ARC score.

## Implemented corrections and additions

The release corrects categorical rounding/clipping, infeasible Haar defaults,
empty-bin NaNs, malformed polyphase families, invalid packet antichains, invalid
real Fourier masks, resized exact frame archives and stale contradictory graph
edges. It also stabilizes regression scale calculation, compares candidate scores
on shared target coordinates, retains candidate failure diagnostics, refits on all
training rows by default and computes benchmark split lengths exactly with integers.
The predecessor reproduction and migration notes document the changed behavior.

New public interfaces expose continuous 1D signal analysis, explicit finite
polyphase FIR blocks, causal chunked filtering and versioned source-signal archives.
The archive API persists samples and settings, not trained model or agent state.
The standalone signal path is not claimed to be a trained general forecasting agent.

## Documentation and package contents

The current guide has 22 pages, nine newly generated Matplotlib figure pairs and a
Markdown/source-content companion. The unchanged historical capstone has 38 pages.
The repository includes eight verified worked examples, regression tests, a full
stress script, offline backend build tooling and machine-readable evidence.
The complete handoff preserves the broader companion archives separately.

The guide was rendered in full for contact-sheet review, with selected dense and
figure pages inspected at full resolution. Text bounding-box and font checks are
recorded separately. No new Lean build or current-corpus theorem reverification is
claimed. Retaining a source file is not the same as executing its verifier.

## Failed attempts retained

The first extra build-tool installation failed on DNS resolution. Distribution
building succeeded using the already installed setuptools backend instead.
One initial regression failure came from the test subprocess not inheriting the
source path and was fixed in the test harness. A figure run failed on a local output
folder permission before producing figures and succeeded after permission repair.
A combined verification command timed out before the final stress sweep completed,
which was then rerun separately. An initial optional-fixture extraction matched the
wrong path prefix and left eight tests skipped. Correct extraction and a full rerun
produced 192 passes. Earlier checkpoints and failures remain separately preserved.

## Unexecuted boundaries

Execution was on Linux / Python 3.13.5, NumPy 2.3.5,
SciPy 1.17.0, PyTest 9.0.2 and setuptools 82.0.1.
Windows and Python 3.12 are configured but not run here. Remote CI, official ARC,
external real-signal benchmarks, a fresh Lean build, hardware scaling and independent
third-party reproduction were not performed. The release carries no AGI claim,
no unbounded operator-discovery claim and no pretrained foundation-model checkpoint.

## Final distribution checkpoint

The wheel was installed into an isolated target and its import location was checked
outside the source tree. All 184 core tests passed against that installed package,
and all eight worked examples ran against it. A fresh source-distribution extraction
passed source consistency checks, rebuilt a wheel, installed it separately, passed
self-check, and passed all 184 core tests. Every nonempty wheel RECORD hash was checked.
The wheel rebuilt from the source distribution was byte-identical to the tested wheel.
These are isolated installation targets using pre-existing scientific dependencies,
not fresh operating-system installations.

One isolated test collection initially failed because the copied tests had lost the
registered local_suite marker from pyproject.toml. A minimal pytest.ini restored only
the marker, without pointing at the original source. The corrected installed-wheel
suite passed. The combined packaging runner also timed out before its final summary.
Its completed step logs were retained, the final source test was repeated separately,
and wheel RECORD and rebuild-identity checks were independently completed.

Final artifact identities and clean-ZIP verification are supplied with the external
release manifest. No change to the public-release licensing boundary follows from a
successful build or test run.

The final declared-file archive comparison found 40 source-distribution omissions:
legacy PowerShell wrappers, their README and CSV versions of evidence ledgers.
They were present in the source ZIP but absent from the first source distribution.
The MANIFEST.in inclusion rules were corrected. The final external archive check
compares every declared source file, rather than relying only on passing Python tests.
