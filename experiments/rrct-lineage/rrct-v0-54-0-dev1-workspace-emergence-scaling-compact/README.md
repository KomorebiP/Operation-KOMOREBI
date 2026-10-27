# RRCT v0.54 Workspace-Emergence Scaling

This compact research release maps when terminal-only training produces causally usable local and global workspace representations inside the supplied v0.53 two-level hierarchy.

Start with:

1. `BLOCK_SUMMARY.md`
2. `FORMULAIC_SCALING_LAW.md`
3. `PROTOCOL.md`
4. `RESULT_REPORT.md`
5. `holdout_results/HOLDOUT_ANALYSIS.json`
6. `holdout_results/SCALING_VALIDATION.json`

The frozen holdout deliberately remains `V054_HOLDOUT_ENDPOINTS_NOT_MET`: 13 of 16 preregistered endpoints passed. The failed d2 reliability thresholds are preserved. A post-hoc 1200-step extension identifies the revised boundary but does not retroactively convert the frozen result into a pass.

Run the compact verification with:

```bash
./RUN_V054_SCALING.sh
```

or on Windows:

```powershell
.\RUN_V054_SCALING.ps1
```
