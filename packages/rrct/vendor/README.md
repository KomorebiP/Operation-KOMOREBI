# Vendored canonical releases

`RELEASE_INDEX.json` lists the canonical archives included in the full offline bundle. They are copied without modification and verified by SHA-256.

Use:

```powershell
.\EXTRACT_LEGACY_RELEASE.ps1 -Version 0.57.0.dev3
```

Then run the extracted release's own `VERIFY_*.ps1` or `RUN_*.ps1` script.

The configurable v0.59 laboratory does not rewrite historical frozen results. It provides a common exploratory interface alongside them.
