# Additional software

Additional software belongs here when its build and maintenance contract does not require an independent repository. The selected families include the Quadratic-Form Engine/K-COS, SKAT and streaming factor decomposition, GPU structured numerics, AM-SPD, chemistry, Proof Path Theory, Proof Atlas, JSpace tools, chess and operator-reasoning software.

The flagship [Komorebi Math and Polyphase Float](../docs/LIBRARIES.md) source trees remain in their separate repositories. The [K-COS landing page](../papers/quadratic-form-kcos/README.md) supplies its imported companion edition, final engine source, and separately preserved historical packet implementation. Its formal scope and numerical evidence remain explicit.

The K-COS source is imported at that paper landing page. [AM-SPD 1.0.0](komorebi-am-spd/README.md) is imported at `packages/komorebi-am-spd`. Other additional software components await import. Each import supplies its own version, install or build command, validation scope, source provenance, retained failures, and distribution terms.

## AM-SPD 1.0.0

Install the maintained CPU implementation from the repository root:

```bash
python -m pip install -e packages/komorebi-am-spd
python -m am_spd verify --full
```

The stable component descends from the recovered 0.3.0 final package. It decomposes finite normalized image arrays into a geometry core, singular/local terms, and a stored residual. Exact-mode reconstruction refers to normalized floating-point array coordinates up to roundoff; preview files are quantized, and the scalar parameter proxy is not an encoded bit rate or a global optimality certificate.

Fresh Linux validation passed [228 tests, lint, compilation and 20 integration checks](komorebi-am-spd/validation/source-final/summary.json), [four strict replay cases](komorebi-am-spd/validation/paper-replay-final/paper_reproduction_summary.json), and [clean-venv, outside-checkout wheel verification](komorebi-am-spd/validation/wheel-final/summary.json). The [final wheel metadata refresh](komorebi-am-spd/validation/wheel-final/metadata_refresh.json) records its artifact lineage. [Independent clean source-distribution qualification](komorebi-am-spd/validation/sdist-final/summary.json) passed offline installation, 228 extracted tests, 20 integration checks and dependency checks outside the checkout, with the archive hash unchanged. Replay freshly executes the frozen historical downstream calculation using checksummed archived source/core fixtures; it does not claim a fresh replay of the original geometry search. The [release audit](komorebi-am-spd/RELEASE_CHECKLIST.md) distinguishes fresh runs, historical reports, completed distribution checks and pending hosted checks. Windows wheelhouse static preflight passed, while native Windows execution and the hosted Python/platform matrix remain pending.

[MIT](komorebi-am-spd/LICENSE) is selected for the current AM-SPD component code. The preserved historical research snapshot retains its recorded notices and terms; other repository components and third-party dependencies keep their own terms. The [distribution record](../docs/DISTRIBUTION_STATUS.md) records that scope.

See the [contribution ledger](../CONTRIBUTIONS.md) for source recovery status.
