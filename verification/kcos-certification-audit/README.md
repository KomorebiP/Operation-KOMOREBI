# K-COS numerical certification audit

Author: Komorebi P.  
Audit date: 4 November 2026

[Reading companion](../../docs/KCOS_NUMERICAL_CERTIFICATION_AUDIT.md) · [Reproduction workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/kcos-certification-audit.yml)

This is a bounded executable audit of publication revision `332d8c86b712fbbabf799c0476a9991848c91c2e`. The retained manuscript and engine are not modified. The three interval/controller source modules are checked against their exact Git blob identities before replay.

## Recorded outcomes

The existing engine suite passed 60 tests and 13 subtests. The new audit made 12 tail evaluations: 11 finite intervals contained their complete independent reference intervals, and 10 met the requested width. The running example at 8,192 modes failed its width request, while the wide-spectrum case did not establish a finite informative interval under the selected limits. Both failures remain explicit.

Thirteen invalid-input controls and one exhausted-budget control passed. Three resource-cap violations were reproduced. A separate candidate patch passed 25 new tests. Six analytic packet point checks passed, but they are not directed packet certificates.

The seven moderate-tail comparison cases produced six successful Davies flags and one accuracy failure. The oscillatory Imhof implementation completed all seven with observed absolute errors below 1e-10. Absolute quadrature errors are not equivalent to the K-COS relative-width contract.

## Run from the repository root

```bash
python -m pip install -r verification/kcos-certification-audit/requirements.txt
python verification/kcos-certification-audit/run_audit.py all
python verification/kcos-certification-audit/compare_davies.py --prepare
python -m pytest -q verification/kcos-certification-audit/test_audit.py
python verification/kcos-certification-audit/check_results.py
python verification/kcos-certification-audit/plot_results.py
```

The `running`, `spectra`, `deep`, `controls`, and `packet` stages can be run individually. Calls using `mpmath.iv` are sequential because its precision context is shared.

`compare_davies.py --prepare` requires a C++ compiler and internet access to obtain one pinned upstream source. It verifies the original blob before compiling. The compatibility headers provide only standard C++ math and allocation declarations. This runs the unmodified Davies C++ core, not the installed R package. No third-party source or compiled library is committed here.

## Inspect the evidence

Each replay writes `results/` with exact decimal inputs, complete outward endpoints, reference intervals, accuracy decisions, unresolved cases, and comparator diagnostics. `check_results.py` verifies the expected audit outcomes and writes `results/summary.json`. `plot_results.py` creates two SVG and two PNG figures from those records.

The dedicated GitHub Actions workflow retains results, figures, the generated patch, and the candidate source as an artifact with a requested 90-day retention. Download artifacts before their expiry when a permanent local record is required. The scripts remain in the repository so the results can be regenerated.

## Resource-cap repair

```bash
python verification/kcos-certification-audit/repair_candidate.py
```

This creates `candidate/accuracy_driven.py` and `controller_caps.patch`. It validates finite positive integer resource settings, rejects initial settings above their caps, and clamps the last support-scale refinement to the actual cap. It does not apply the patch to the retained engine. Integration requires a separately maintained runtime or an explicitly revised publication package.

## Guarantee boundary

The separate reference covers positive spectra whose distinct coefficients have even multiplicities. Exact rational partial fractions supply the law; outward Decimal evaluations supply its numerical enclosure. The implementation remains conditional on Decimal/libmpdec correctness.

The K-COS interval path uses the complete positive central spectrum, rank greater than two, and checked tilt parameters. Its automatic parameter designer also requires the threshold to exceed the mean. Packetized, signed, and noncentral calculations do not inherit the directed guarantee. The audit is not an external review, new Lean compilation, GPU benchmark, or equal-accuracy speed comparison.
