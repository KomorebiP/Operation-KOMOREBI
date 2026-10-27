# H12 bounded numerical evidence

Read `FRESH_NUMERICAL_VALIDATION.md` for tested ranges, actual working precision, preserved failures and the four unverified historical receipt outputs. Fresh evidence supports the stated finite tests; it does not certify an infinite product or class-field equality.

From the extracted `Komorebi_H12_Cubic_Divisor_Final_2026-10-07` folder, using Python 3.12 and the pinned dependencies:

```bash
python -m pip install -r verification/numerical/requirements.txt
python verification/numerical/replay.py --group exact
python verification/numerical/replay.py --group numerical40
python verification/numerical/replay.py --group numerical70
python verification/numerical/replay.py --group independent
python verification/numerical/replay.py --group continuation
python verification/numerical/replay.py --group visual
python verification/numerical/replay.py --group provenance
```

Run groups serially. Each writes a uniquely named bounded result, raw logs and version-2 execution manifest under `verification/numerical/replay_results/`. The independent group took about 92 seconds in the recorded environment and retains a 120-second wall / 90-second CPU cap; a slower machine may stop at the cap rather than emit a completed result. The driver pins one core and one cooperative library thread, 1 GiB per-process memory and 1 MiB output. Do not increase bounds silently or interpret a capped partial run as a pass.

To validate a newly produced execution manifest:

```bash
python verification/numerical/runner/validate_manifest.py verification/numerical/replay_results/GROUP-TIMESTAMP/manifest.json --root .
```

Historical `runs/` manifests record the actual executed workspace paths. `FRESH_MANIFEST_VALIDATION.json` records their successful validation there; relocation changes those paths. New replay runs generate current relative paths. The provenance driver recreates missing ZIP aliases named by the archived intake record from hash-matched source archives, then validates their bytes; it does not alter archived source payloads. Historical receipt payload gaps remain disclosed on replay.

`checks/history/` preserves the scripts that triggered the documented domain/resource and strict receipt-hash failures. The final implementation and selected runs are identified by `NUMERICAL_PACKET_SHA256.json`. This driver was syntax-checked during closeout; no extra complete seven-group driver rerun is implied.
