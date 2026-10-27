# Signal Reconstruction computation review

The ten current bounded suites completed successfully under their printed
contracts. They record 288 explicit checks, or 281 after removing the seven
repeated checks of the closely related SPD variant. This count excludes native
diagnostic fields, declared test-group labels, tested-family sizes, duplicate
runs, archived evidence, and file/hash checks. It is not a theorem count.

Two recovery failures are retained as scientific findings. The burst stress
case infers nine jumps instead of six. A separate exact three-jump perturbation
makes the native largest-singular-value-ratio heuristic infer two instead of
three, although an independently supplied threshold correctly selects three.
Finite reconstructed error and successful other examples do not remove either
failure.

## Sources and preservation

Six source archives and two standalone scripts supplied 765 retained file
payloads. Each payload was compared directly with its original ZIP member or
standalone input bytes. The archive hashes and per-file correspondences are in
`verification/SOURCE_PRESERVATION.json`. All retained source hashes still
matched after execution. Only `__pycache__` and `.pyc` payloads were excluded.
Original upstream directories were not modified.

The reviewed scientific contracts cover the executed unknown-edge, polyphase,
finite interval/dictionary, complex one-dimensional, DCT and small packet-solver
paths. Plotting/PDF generators, large image stress and natural-image benchmarks,
the whole cross-domain seed calculus, and external numerical library internals
were not independently audited or fully rerun. Historical evidence is preserved
and separately indexed by `verification/ARCHIVED_EVIDENCE_INDEX.json`.

## Current finite checks

| Suite | Recorded checks | Unique counted checks | Scope |
|---|---:|---:|---|
| Exact invariants | 134 | 134 | 24 Q(i) DFT/polyphase cases, off-grid orders 2/3/4, exact L1 counterexample and 24 perturbations |
| Original unknown edge | 24 | 24 | 19 native checks plus five independent quadrature modes |
| Original self-calibration | 31 | 31 | Native rate/noise/offset/oracle/random-family/finite-budget checks |
| Singularity dictionary | 26 | 26 | Three raster sizes, finite interval selection, Haar identities and five quadrature modes |
| Gibbs case | 8 | 8 | Three direct synthesis orders and a 48-point interval dictionary |
| Complex benchmark | 23 | 23 | Three controlled and three descriptive stress cases, 32 by 32 in-dictionary/DCT control |
| Infinite packet | 7 | 7 | Native reported 16 groups plus six independent ridge/archive/projection checks |
| Infinite packet SPD | 7 | 0 | The same seven checks repeated on the close variant |
| Rank-aware execution copy | 16 | 16 | Two generic counterexamples, corrected projector/separation and retained native dictionary |
| Rank-ratio boundary | 12 | 12 | Exact Q(i) factorization, native order-two failure and supplied-threshold order-three selection |

The unknown-edge native run repeats four finite-rate examples with background
degrees 3 through 6 and jump counts 2, 4, 6 and 8. It also checks one finite
sparse dictionary, two shared-edge channels, and an 18 by 18 rectangle
dictionary. Piecewise integration, with jump breakpoints, independently verifies
the sign and normalization of five Fourier coefficients.

The self-calibration native checks use 44 power-tail rate entries, 150 fixed-seed
noise trials, 2,500 direct offset-coefficient perturbations, 28 oracle
comparisons, and 100 separated random-family cases. These observations support
the tested implementation; they do not give an unrestricted noisy rank-selection
or branch-selection theorem. The explicit exact control uses 19 high-frequency
coefficients for the declared maximum order six.

The exact L1 counterexample moves one endpoint of a unit-period zero-mean
interval packet by delta = 1/10. Its integrated L1 difference is 9/50, larger
than the old bound 1/10. The corrected factor-two location bound passes the
exact perturbation controls. The archived `edge_l1_error` functions compute a
sampled Riemann sum directly and do not implement the false coefficient-one
bound, so no numerical source patch was needed for this prose repair. A sampled
L1 diagnostic alone is not an exact continuous-norm certificate.

## Minimal numerical source repair

The original generic dictionary projector uses every QR column of the supplied
background. Dependent columns can introduce an extra projected direction. The
original restricted-separation function reads compact SVD's last returned
singular value, which can be positive when a wide coefficient matrix has a
kernel. The documented 24 by 8 example is not affected by these counterexamples.

The separate `execution/unknown_edge/` copy uses an SVD numerical-rank basis for
the background range and returns separation zero when a support is wider than
the observation space. Original and patched hashes, the exact diff, and the
numerical rank tolerance are recorded. Sixteen independent finite controls pass,
including full-row-rank underdetermined support, dependent and zero background
columns, projector identities, and preservation of the documented example's
support, reconstruction and separation. This repair is numerical and does not
certify exact rank near a floating singularity.

The theorem's zero-edge case is mathematically trivial but remains outside the
nonconstant `EdgeModel` constructor/native recovery API. No zero-edge wrapper
is included or claimed.

## Order heuristic and ridge boundaries

The rank witness has nodes 1, i and -1, amplitudes 100, -99 and -1, moments
starting at index four, and added moment noise (1/10)(-i)^n. A unitary
Gaussian-rational Fourier factorization gives square-Hankel singular values
400, 396, 4, 0 before noise and 400, 396, 4, 2/5 after noise. The noise operator
norm is 2/5, below half the smallest active singular value. The largest ratio
selects two; threshold two selects three. The native rectangular-matrix
heuristic also selects two on a 16-moment version. A theorem assuming supplied
noise/singular-value bounds does not certify that heuristic.

Both packet variants default to ridge = 1e-9 and solve a regularized normal
equation. Their fresh small controls verify M-transpose times residual equals
ridge times coefficient, an independent augmented least-squares solve, and
the archive/synthesis identities. An ideal unregularized projection is tested
separately. Exact projection stationarity, monotone residual theorems and exact
pixel-span completion must be distinguished from finite ridge tolerances.
Complete image rasters are known inputs. These experiments are finite image
approximation, not blind Fourier inversion or verified universal convergence.

## Reproducibility and attempt history

Runs used Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, SymPy
1.14.0, mpmath 1.3.0, scikit-image 0.26.0, OpenCV package 5.0.0.93 and Pillow
12.3.0. Lightweight image dependencies are pinned in
`requirements-verification.txt`. Task-local installed files were hashed before
and checked after the runs: 2,736 files matched. External library internals are
not formally verified by this check.

The ordinary suites have 180-second wall and 150-second CPU caps. The rank
controls have 60-second wall and 45-second CPU caps. All runs impose 2 GiB
address-space, one-core affinity, cooperative one-thread limits and 1 MiB
combined logs. Actual argv, input/output hashes, versions, run status, UTC start,
runtime and effective caps are in version-two manifests. Fourteen complete,
failed or superseded records passed schema/live-hash validation. That validation
does not make a failed scientific check true or repair inaccurate historical
metadata.

The initial complex surrogate mistakenly required correct parameter recovery
in every stress case. It failed on the burst case and is retained unchanged.
The corrected scope retains that case as an observed identification failure.
Two earlier primary-seed metadata labels were inaccurate; fresh current reruns
explicitly record the actual self-calibration streams 0 through 29, 17 and
20260729, and complex small-control seed 20261006. Prior records are classified
as superseded. Duplicate exact-suite output is not counted twice.

`verification/CURRENT_RELEASE_VERIFICATION.json` is the current authoritative
index. `verification/README.md` gives replay/validation commands. No fresh Lean
execution or formal verification of current Signal claims was performed. Related
Paper V source/history is a separately identified archived formal dependency.
