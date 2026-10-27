# Isolated figure-generator execution review

Status: PASS. All five generators execute successfully and the report-path metadata finding is resolved.

The public generators were executed unchanged in an isolated copy containing `tools`, `examples`, and `source/figures`. The delivered canonical figure directory was never used as an output destination. This is a bounded reproducibility check, not an audit or proof of the underlying mathematical claims.

## Commands and results

Working directory for every command: `build/figure_rebuild`, resolved to the absolute directory in the JSON receipt.

| Exact command | Exit | Produced figure PDFs | Log |
|---|---:|---:|---|
| `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/plot_foundations.py` | 0 | 8 | `build/figure_rebuild/logs/plot_foundations.log` |
| `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/plot_transport.py` | 0 | 6 | `build/figure_rebuild/logs/plot_transport.log` |
| `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/plot_limits.py` | 0 | 6 | `build/figure_rebuild/logs/plot_limits.log` |
| `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/plot_regularization.py` | 0 | 6 | `build/figure_rebuild/logs/plot_regularization.log` |
| `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/plot_certificates.py` | 0 | 4 | `build/figure_rebuild/logs/plot_certificates.log` |

Every command exited normally and wrote its expected JSON report. The combined stdout/stderr logs contain only the generators’ success summaries, with no warnings, errors, or traceback. Reports are preserved in `build/figure_rebuild/build/figure_reports`.

All 30 generated PDFs are readable single-page files. Every generated PDF hash agrees with its generator report. All 90 canonical figure-file hashes are identical before and after execution. The copied tool hashes matched `records/FIGURE_SOURCE_ADAPTATIONS.json` before execution.

## Metadata finding

The first foundation run reported `checks/build_figures.py` as its source. The coordinator corrected that field to `tools/plot_foundations.py` and updated the adaptation hash. The first execution and its reports remain untouched. A fresh isolated second run of only the foundation generator passed. All eight source fields now identify the public tool path, all eight PDFs are readable and agree with their report hashes, and the model/parameter records are unchanged. The second run also left all 90 canonical figure files byte-identical.

## Evidence

`build/figure_rebuild_validation.json` preserves exact commands, working directories, Python and plotting-library versions, timings, exits, source hashes, logs and report hashes, report contents, output PDF inspection, and complete canonical figure inventories before and after the run.

No test suite was introduced. No canonical figure was overwritten. No mathematical formula or model was changed.

## Corrected foundation rerun

Exact command: `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python tools/plot_foundations.py`.

Working directory: `build/figure_rebuild/foundation_attempt_002`. Exit: 0. Log: `build/figure_rebuild/foundation_attempt_002/logs/plot_foundations.log`. Report: `build/figure_rebuild/foundation_attempt_002/build/figure_reports/plot_foundations.json`.

Corrected source SHA256: `fcf78aa7ac5f45d92b3c63a97a573b9929105afb80c00d278fc5bf0152fae014`. No formula changes were made by this validation task.
