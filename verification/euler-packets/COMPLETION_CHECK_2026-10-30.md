# Euler example: completion check

Checked 30 October 2026 against collection revision
`2636b24ac9a340d599b6ac3c85ac11b295288af3`.

**Outcome: implementation and finite assertion verified in the stated range.**
The final stage 007 calculations reproduce, the printed CLI output matches the
worked page, and the live IO downloads match their bound source files. The
published mathematical statements retain their written proofs and source
qualifications. This check does not resolve the universal root-simplicity problem.

## Exact scope and provenance

The manuscript SHA-256 is
`ea6b9a8be77f87d43015ae3566285ad3fedb526cce57c55349c10c3c93b6db94`;
the standalone program SHA-256 is
`aef7b88eabf577ffa6caaa00dec41fea796b9d098657a24d30dfcb9a9ed1e421`.
Both, the supplementary checker, publisher and publication manifest matched the
GitHub blobs at the revision above. All 150 existing publication-bound file
hashes passed before the documentation correction.

The fresh bounded [run manifest](completion-run-2026-10-30/manifest.json) has
`run.status=completed`; its 20 declared input hashes were unchanged and its
result hash passed the v2 manifest validator. The snapshot has no Git metadata,
so the runner honestly records its checkout commit as unavailable. The remote
revision and byte identities above provide the source correspondence. Python
3.12.14 was used. The wall limit was 60 seconds and combined-log cap 1 MiB;
no hard Windows memory or CPU cap is claimed.

## Checks performed

| Obligation | Result and evidence |
|---|---|
| Full finite calculation and manuscript output | Passed: [fresh results](completion-run-2026-10-30/results.json) reproduce every accepted stage 007 result, the printed output, 24 Schur packet coefficients, 12 complete sampling-kernel rows and 18 index-shift cases, retaining the failing degree-zero control. The exact population remains that of [contract 007](contract-007.json). |
| Pinned library agreement | Passed: [fresh comparison](completion-check-2026-10-30/library-comparison.json), 7,442 comparisons: 605 reciprocal, 1,012 local-chart, 921 Fibonacci, 3,506 packet/calculus, 1,164 atlas and 234 dyadic-tail. Tracked `src/` and imported source hashes matched pin `a3aa04ac18a523f30c50c7f5dba709f88e904eff`; NumPy 2.5.4. |
| Publication safeguards | All six existing `test_euler_publication.py` tests passed, including tampered downloads, changed source, incomplete runs, wrong input hashes and unsafe source paths. The first sandbox attempt was blocked by Windows temporary-folder permissions; the successful repeat used the same tests. |
| Live source correspondence | Passed: [IO record](completion-check-2026-10-30/live-before.json), 15 downloads and all 152 archive members, including every one of the 150 publication-bound files, matched hashes and local source bytes. This records the site before this documentation correction. |
| Browser rendering | At 1280px: 64 section headings, 1,238 rendered math containers, zero MathJax errors, zero broken same-page anchors and no document-wide horizontal overflow. Opening layout and the exact-checks section were inspected. This is a focused page check, not a full accessibility audit. |
| Reproducibility instructions | Corrected the stale stage 003 references to the final stage 007 evidence. Earlier runs and the failed 004 comparison remain preserved. |

## Mathematical boundary review

Normalized claim: for first omitted index r at least one and natural row N at
least r, the finite dyadic reconstruction error factors as stated in C53.
For binary digit sum at most three, C55 gives the exact row valuation. The
uniform bound is attained on the first omitted row; the r=15, N=16 cancellation
example does not improve it uniformly.

**Focused proof verdict: proved as written** for C53–C56, using the stated
Bernoulli denominator input. The dependency chain is: exact reciprocal kernel
and dyadic-unit source -> finite tail factorization -> binary coefficient
weights -> finite carry cutoff -> sparse-binary valuation and the explicit
cancellation witness. The factorization uses only finite sums at natural rows;
the first omitted row and empty-tail cases were checked. The DLMF
[von Staudt–Clausen formula](https://dlmf.nist.gov/24.10.E1) confirms the needed
single factor of two in the Bernoulli denominator.

C57's restricted-series preparation theorem remains the exact named source
input recorded in [the source check](LITERATURE_EDGE.md), not a conclusion of
this finite rerun. The earlier packet, matrix, Fibonacci and atlas proofs retain
their existing review records; they were not all independently re-audited here.
Universal classification and simplicity of the preparation-polynomial roots
remain explicitly open. Review provenance: same-assistant self-review; no
independent review, new Lean execution, global novelty or speed claim.

## Reproduction

From the collection root, with Python 3.10 or later:

```text
python -B examples/euler_packets.py
python -B tools/check_euler_case.py
python -B tools/check_euler_case.py --math-root PATH_TO_PINNED_KOMOREBI_MATH
python -B -m unittest discover -s tools -p test_euler_publication.py -v
```

The optional library command needs its declared dependencies and source pin.
The bounded runner's exact command, inputs, results and observed limits are in
the fresh manifest. No remaining failed check was found in this declared scope.
