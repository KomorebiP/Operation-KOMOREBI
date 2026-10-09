# Additional software

Additional software belongs here when its build and maintenance contract does not require an independent repository. The selected families include the Quadratic-Form Engine/K-COS, SKAT and streaming factor decomposition, GPU structured numerics, AM-SPD, chemistry, Proof Path Theory, Proof Atlas, JSpace tools, chess and operator-reasoning software.

The flagship [Komorebi Math and Polyphase Float](../docs/LIBRARIES.md) source trees remain in their separate repositories. The [K-COS landing page](../papers/quadratic-form-kcos/README.md) supplies its imported companion edition, final engine source, and separately preserved historical packet implementation. Its formal scope and numerical evidence remain explicit.

The K-COS source is imported at that paper landing page. [AM-SPD 1.0.0](komorebi-am-spd/README.md) is imported at `packages/komorebi-am-spd`. Other additional software components await import. Each import supplies its own version, install or build command, validation scope, source provenance, retained failures, and distribution terms.

## AM-SPD 1.0.0 prepublication qualification

Install the maintained CPU implementation from the repository root:

```bash
python -m pip install -e packages/komorebi-am-spd
python -m am_spd verify --full
```

The 1.0.0 component descends from the recovered 0.3.0 final package. It decomposes finite normalized image arrays into a geometry core, singular/local terms, and a stored residual. Exact-mode reconstruction refers to normalized floating-point array coordinates up to roundoff; preview files are quantized, and the scalar parameter proxy is not an encoded bit rate or a global optimality certificate.

Fresh Linux validation passed [240 tests, lint, compilation and 20 integration checks](komorebi-am-spd/validation/source-release-final/summary.json). [Clean offline installed-wheel qualification](komorebi-am-spd/validation/wheel-release/summary.json) passed 20 integration checks and [all four strict paper cases](komorebi-am-spd/validation/wheel-release/paper/paper_reproduction_summary.json) outside the checkout. [Independent clean source-distribution qualification](komorebi-am-spd/validation/sdist-release/summary.json) passed offline installation, 240 extracted tests without skips, 20 integration checks, dependency checks and strict geometry replay, with the archive hash unchanged. Prior [232-test source](komorebi-am-spd/validation/source-qualified/summary.json) and [source-distribution](komorebi-am-spd/validation/sdist-qualified/summary.json) reports, the [228-test source report](komorebi-am-spd/validation/source-final/summary.json), [earlier wheel verification](komorebi-am-spd/validation/wheel-final/summary.json), [wheel metadata refresh](komorebi-am-spd/validation/wheel-final/metadata_refresh.json), and [228-test source-distribution report](komorebi-am-spd/validation/sdist-final/summary.json) remain preserved as earlier evidence.

Replay uses checksummed archived source/core fixtures and the original singular, Lagrange-tree and exact-budget-tree reopening coordinates. It freshly validates the seed spans, projected reconstructions and scalar costs, then recomputes replacement directions, global refits and final portfolio selection with the frozen historical backend. It does not rerun the original geometry-discovery search. The [prepublication release checklist](komorebi-am-spd/RELEASE_CHECKLIST.md) distinguishes current local qualification, historical evidence and pending hosted publication.

Six hosted AM-SPD CI jobs passed for the pre-anchor main revision `f49621c2b660d055646f991bda68afa5ea4761c0`, but [stable release run37878549206](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/37878549206) failed required strict geometry replay during wheel qualification. Hosted qualification of the current anchored replay remains pending; no cause of the earlier failure is confirmed here. [Refreshed Windows static preflight](komorebi-am-spd/validation/windows_offline_preflight.json) passed checks for the four schema-2 fixtures and 12 archived seed coordinate sets. Native Windows offline execution and stable tag/release publication remain pending.

[MIT](komorebi-am-spd/LICENSE) is selected for the current AM-SPD component code. The preserved historical research snapshot retains its recorded notices and terms; other repository components and third-party dependencies keep their own terms. The [distribution record](../docs/DISTRIBUTION_STATUS.md) records that scope.

See the [contribution ledger](../CONTRIBUTIONS.md) for source recovery status.
