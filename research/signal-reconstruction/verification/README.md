# Fresh finite verification

The current evidence is indexed by `CURRENT_RELEASE_VERIFICATION.json`. These
are bounded implementation checks and orthogonal mathematical invariants.
They do not establish universal theorems, verify Python formally, or authenticate
the internals of NumPy, SciPy, SymPy, scikit-image, or OpenCV.

The source payloads under `sources/` are preserved byte for byte. The separate
`execution/unknown_edge/` copy repairs two generic numerical rank contracts.
Its diff and original/patched hashes are retained. Native original runs and
repaired-copy runs are explicitly distinct.

## Portable replay

Use Python 3.12 and a virtual environment with the pinned dependencies:

```bash
python3 -m venv .signal-verification-env
. .signal-verification-env/bin/activate
python -m pip install -r requirements-verification.txt
python verification/replay_all_v3.py --suite all --run-name my_scoped_replay
python verification/replay_rank_controls.py --run-name my_rank_controls
python verification/replay_rank_gate_launcher.py --run-name my_rank_ratio_boundary
```

Each run name must be new. The launcher refuses to overwrite evidence. The
optional `--dependency-dir /absolute/path/to/site-packages` supports a private
dependency installation. No Lean executable is needed for these Python runs.

The ordinary suite caps are 180 seconds wall time, 150 seconds CPU time, 2 GiB
address space, one CPU core, one numerical-library thread, and 1 MiB combined
logs. The two small rank suites use 60 seconds wall time and 45 seconds CPU time,
with the same other caps. POSIX address-space/CPU caps are per process. Thread
environment variables are cooperative. Recorded effective caps are in each
manifest.

The unchanged provenance helpers are included under `provenance_runner/`.
Validate a record and its live input/output hashes with:

```bash
python verification/provenance_runner/validate_manifest.py \
  verification/runs/my_scoped_replay/unknown_edge/manifest.json --root .
```

`replay_all_v3.py --plan-only --run-name unused_plan` lists every scientific
range and input without executing an experiment. It does not create evidence.

## Evidence boundaries

The unknown-edge run executes all 19 native named checks, four exact-class
examples, the finite dictionary, a shared-edge multichannel case, and a finite
rectangle dictionary. Five independent piecewise quadrature modes check the
Fourier sign and normalization.

The self-calibration run executes the 31 native named checks, including rate
tables, 150 fixed-seed noise trials, 2,500 offset coefficient perturbations,
28 oracle comparisons, 100 separated random-family cases, and the explicit
19-coefficient finite budget. Their counts are tested families, not numbers of
independent assertions. Runtime/collision tables and all figure regeneration
remain archived rather than being added to fresh evidence.

The complex run repeats six one-dimensional examples. All three controlled
examples recover the expected order. The burst stress case infers nine jumps
instead of six and reports invalid location/amplitude comparisons. Finite
reconstructed RMSE does not repair that identification failure. The small
32 by 32 geometric control supplies the complete raster and checks one native
dictionary recovery plus DCT projection identities. Large image, natural-image,
and out-of-model benchmarks are archived only.

The two infinite-packet scripts execute their native functions reporting 16
test groups. The additional 16 by 16 controls verify the ridge normal equation,
an independent augmented least-squares solve, packet synthesis and residual
archive identities, and an ideal unregularized projection comparison. Seven
identical recorded checks from the SPD variant are excluded from the unique
count. Native group labels and diagnostic fields are not added to assertion
counts. Complete images are inputs to these finite approximation experiments.

The rank-ratio suite reproduces a separate three-jump perturbation for which
the native largest-ratio order heuristic selects two. An independently supplied
threshold selects three under a known error/singular-value gap. This is a
demonstrated distinction between the theorem's threshold hypothesis and the
source's heuristic. No automatic threshold construction or heuristic repair
is claimed.

The exact suite uses Fraction and independently implemented Gaussian-rational
arithmetic for DFT inversion, normalized Parseval, polyphase aliasing,
off-grid Hankel/annihilator identities and zero-mean packet L1 bounds. It
rejects the old coefficient-one location bound on an exact example and tests
the corrected factor-two bound. Finite tests support implementation conventions;
the corrected general bound is proved in the traditional paper.

## Retained unsuccessful and superseded attempts

The first complex replay imposed an unjustified all-stress order/finite-error
check. It failed on the burst case. The failed manifest and original driver
remain intact. The accurate scoped follow-up reports that failure as a boundary.

Two early launcher metadata fields used inaccurate primary seed labels for
self-calibration and complex tests. Current reruns record the actual fixed seed
streams. Earlier scientific runs are preserved and classified as superseded
metadata records. One earlier exact-suite replay is a duplicate and is not
counted twice. The current index identifies the authoritative record for each
suite.

Historical result files are indexed separately in `ARCHIVED_EVIDENCE_INDEX.json`.
Do not run upstream figure/PDF generators in preserved source directories.
For a complete inherited rebuild, first copy the corresponding directory into
a new work area and use its documented command there.
