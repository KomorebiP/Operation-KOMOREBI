# Additional software

Additional software belongs here when its build and maintenance contract does not require an independent repository. The selected families include the Quadratic-Form Engine/K-COS, SKAT and streaming factor decomposition, GPU structured numerics, AM-SPD, chemistry, Proof Path Theory, Proof Atlas, JSpace tools, chess and operator-reasoning software.

The flagship [Komorebi Math and Polyphase Float](../docs/LIBRARIES.md) source trees remain in their separate repositories. The [K-COS landing page](../papers/quadratic-form-kcos/README.md) supplies its imported companion edition, final engine source, and separately preserved historical packet implementation. Its formal scope and numerical evidence remain explicit.

The K-COS source is imported at that paper landing page. [AM-SPD 1.0.0](komorebi-am-spd/README.md) is imported at `packages/komorebi-am-spd`. Other additional software components await import. Each import supplies its own version, install or build command, validation scope, source provenance, retained failures, and distribution terms.

## AM-SPD 1.0.0 stable release

Install the maintained CPU implementation from the repository root:

```bash
python -m pip install -e packages/komorebi-am-spd
python -m am_spd verify --full
```

The 1.0.0 component descends from the recovered 0.3.0 final package. It decomposes finite normalized image arrays into a geometry core, singular/local terms, and a stored residual. Exact-mode reconstruction refers to normalized floating-point array coordinates up to roundoff; preview files are quantized, and the scalar parameter proxy is not an encoded bit rate or a global optimality certificate.

Fresh Linux validation passed [240 tests, lint, compilation and 20 integration checks](komorebi-am-spd/validation/source-release-final/summary.json). [Clean offline installed-wheel qualification](komorebi-am-spd/validation/wheel-release/summary.json) passed 20 integration checks and [all four strict paper cases](komorebi-am-spd/validation/wheel-release/paper/paper_reproduction_summary.json) outside the checkout. [Independent clean source-distribution qualification](komorebi-am-spd/validation/sdist-release/summary.json) passed offline installation, 240 extracted tests without skips, 20 integration checks, dependency checks and strict geometry replay, with the archive hash unchanged. Prior [232-test source](komorebi-am-spd/validation/source-qualified/summary.json) and [source-distribution](komorebi-am-spd/validation/sdist-qualified/summary.json) reports, the [228-test source report](komorebi-am-spd/validation/source-final/summary.json), [earlier wheel verification](komorebi-am-spd/validation/wheel-final/summary.json), [wheel metadata refresh](komorebi-am-spd/validation/wheel-final/metadata_refresh.json), and [228-test source-distribution report](komorebi-am-spd/validation/sdist-final/summary.json) remain preserved as earlier evidence.

Replay uses checksummed archived source/core fixtures and the original singular, Lagrange-tree and exact-budget-tree reopening coordinates. It freshly validates the seed spans, projected reconstructions and scalar costs, then recomputes replacement directions, global refits and final portfolio selection with the frozen historical backend. It does not rerun the original geometry-discovery search. The [prepublication release checklist](komorebi-am-spd/RELEASE_CHECKLIST.md) records local qualification before publication; the [publication receipt](../verification/am-spd-v1.0.0-publication.json) records the actual hosted release outcomes.

[AM-SPD 1.0.0 is published](https://github.com/KomorebiP/Operation-KOMOREBI/releases/tag/am-spd-v1.0.0) at immutable tag `am-spd-v1.0.0`, commit `bcfe61c0e46470d54abc829fa6d4324886333436`. [Main CI](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/37881864525) passed all six declared Linux/Windows jobs, including strict geometry replay on both Python3.13 jobs. The [stable release gate](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/37882062302) independently qualified the installed wheel with all four strict reference cases and 20 integration checks, and the source distribution with all 240 tests, no skips or failures, and 20 integration checks. Native Windows CPython3.13 x64 offline installation, full verification, and strict geometry replay passed using this run's exact bundle. The release supplies the qualified wheel, source distribution and Windows offline ZIP; asset hashes and job outcomes are in the [publication receipt](../verification/am-spd-v1.0.0-publication.json). The earlier pre-anchor failure remains preserved as superseded evidence; its specific cause is not claimed as confirmed.

[MIT](komorebi-am-spd/LICENSE) is selected for the current AM-SPD component code. The preserved historical research snapshot retains its recorded notices and terms; other repository components and third-party dependencies keep their own terms. The [distribution record](../docs/DISTRIBUTION_STATUS.md) records that scope.

See the [contribution ledger](../CONTRIBUTIONS.md) for source recovery status.
