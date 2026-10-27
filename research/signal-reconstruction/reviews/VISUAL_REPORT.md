# Signal Reconstruction visual companion: authoring and self-review

The final guide is `visual/Signal_Reconstruction_Visual_Guide.pdf`, with complete
shared-source TeX and Markdown. It has **29 pages, 33 substantive sections,
93 displayed equations, 21 original figures, and 79 raw-source anchor
occurrences**. The explanatory crosswalk has 57 rows covering all 46 SG claim
groups and pins the current traditional catalogue. Complete traditional proofs
are not claimed to be reproduced in every visual section.

The final PDF SHA-256 is
`1e373ff0d204c3c67b92da55b89065c76844cd892bedd791eae34ab307a00ab3`.
`visual/validation/PUBLICATION_QA.json` records the other source hashes. The
independent scoped final review is in `FINAL_VISUAL_AUDIT.md/.json`.

## Mathematical coverage

The guide proceeds from complete packets, transfer blocks, refinement,
transformed atlases, and convolution channels through measurement/decomposition
obstructions and gcd aliasing. It explains the known-edge Fourier fit and Gibbs
geometry, finite positive mask rays, secant-kernel sparse uniqueness and noise
stability, differentiated finite moments, exact two-edge Prony reconstruction,
Hankel rank and noisy thresholds, coefficient/root/amplitude perturbation,
collision limits, finite polyphase budgets, offset phase, root-branch margins,
conditional root gain, native synthesis, corrected mean-zero L1 control,
shared/confluent models, finite image mismatch, and adaptive packet completion.

Explicit boundaries include a.e. Fourier identification and right-continuous
representatives, nonzero normalization denominators, at least two offset
channels, N>=2 branch geometry with trivial N=1 case, actual column-space
projectors, sparsity of both true and estimated vectors, local inverse and
separation hypotheses, and norm matching in synthesis. The source largest-ratio
rank heuristic is separated from a justified singular-value threshold, with the
fresh true-three/native-two counterexample retained. The six-jump burst case
returning nine jumps is reported as failed order identification despite improved
waveform error.

The mean-zero L1 location coefficient is two, with sharp sawtooth translation
formula `2d(1-d/T)`, and amplitude factor `T/4` for unnormalized integration.
This is a substantive correction to inherited prose, not a proofreading change.
Original source payloads remain unchanged. The guide also explains why a small
location shift does not yield a small uniform function norm.

## Exact finite controls and provenance

The authoritative `visual_run_final_20261006` bounded v2 record completed with
**333 finite assertions** and 21 PDF/SVG/PNG figure triples. The finite domains
are rational and Gaussian-rational controls: an eight-coordinate packet atlas,
eight-sample mask rays, four Gaussian nodes and specified moment/offset ranges,
a hand-checkable two-edge recurrence, three periods with eight rational shifts
each for corrected L1 integration, and a 25-pixel three-mask image dictionary.
Floating Hankel/Vandermonde singular values and continuous curves are drawing
and conditioning diagnostics, not certified interval computations.

The caps were 60 seconds wall time, 45 seconds per-process CPU, 2 GiB address
space, one CPU core, and cooperative one-thread numerical-library caps. The
manifest validated against current inputs and declared results. All 63 current
figure payload hashes match the final scientific result. Dependencies have
version records and the release's separate payload provenance/freshness files.

An initial runner invocation failed before scientific execution because a
relative contract path was looked up from the caller working directory. The
corrected absolute path launched the successful bounded run. Exact argv and
failure cause are retained in `LAUNCH_ATTEMPT.json`.

The first bounded figure run was superseded after a Figure 15 label fix. Its
unchanged manifest validates against an exact reconstructed historical driver
snapshot whose SHA matches both original input hashes. Historical scientific
results and logs are retained, while historical figure payloads were replaced.
The preliminary unbounded `draft_checks.json` reports 334 including a removed
vacuous check; it is explicitly superseded. None of these repeated counts is
added to the authoritative 333.

## Proofreading and layout review

Self-review covered all 33 authored sections and their 93 displays. Routine
changes improved local binding, source paths, representative conventions, and
source/selector grouping. Mathematical notation corrections were: separating
the polyphase active count L from offset r, using offset v in confluent formulas,
using a high odd n0>K and shifted moments in the two-edge example, distinguishing
the actual-index amplitude solve from shifted coefficients, writing corrupted
coefficient data instead of adding a vector to a function, and binding E_Q and
amplitude-stage e_a explicitly. These corrections are recorded here rather
than hidden as prose-only revisions.

All 21 PNG figures were inspected in contact sheets, with full-size inspection
of critical 3D, Gibbs, L1, and final synthesis figures. Figure 15 initially had a
pressed/clipped right-axis label, and an attempted inset overlapped the third
point. The final top-left vertical-axis label and math-text coordinates are
clear. Its genuine 3D geometry remains intact. Figure PDFs use embedded CID
TrueType fonts, not Type 3 bitmap lettering in the inspected 3D figure.

Representative final PDF pages were rendered and inspected, including the cover,
rank/perturbation proof, phase/branch geometry, corrected L1 formula, image
mismatch, adaptive ridge/clip/residual section, and final dense-extension/evidence
page. The independent audit inspected pages 6, 12, 15-17, 19-20, 25, 27-29 and
all 21 figure PNGs; after final local edits pages 17/20 were rerendered and viewed.
Every PDF page passed automated text bounds. No material TeX warning or overfull
box remained. All 93 standalone displays are byte-identical between Markdown and
TeX; a preliminary broad regex accidentally matched a cover line-break optional
argument, and the corrected line-delimited equation check resolved that false
comparison. Source-only final-page overflow was removed by grouping each source
path and selector.

## Limits

This is an authoring/self-review record plus a separate scoped companion audit,
not an adversarial universal-proof audit or formal verification of Python. The
earlier known-edge Lean material does not certify this complete unknown-edge or
self-calibration paper. No fresh Lean run is claimed. A finite image dictionary,
regularized truth-residual approximation experiment, or small internal offset
residual is not promoted to unrestricted blind image recovery.
