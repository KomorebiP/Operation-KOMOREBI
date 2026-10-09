# Migration from 0.1.1 to 0.2.0

The original high-level API remains valid:

```python
from am_spd import AMSpdConfig, reconstruct
```

`AMSpdConfig.paper()` remains available as an alias. New code should use `AMSpdConfig.paper_scale()` to make clear that it runs paper-sized budgets rather than historical packet replay.

New functionality includes:

- `AMSpdModel`, including `AMSpdModel.from_legacy_archive()`
- `AMSpdResult.to_model()` and `save_model()`
- `fit_packet_core()`
- `fit_singular_packets()`
- `optimize_trees()`
- `fit_portfolio()`
- `complete_with_pixels()`
- `compare_baselines()`
- `run_builtin_benchmark()`
- `reproduce_paper_case()` and `reproduce_paper()`

The CLI retains `reconstruct`, `demo`, `verify`, and `info`, and adds `decompose`, `decode`, `convert-archive`, `inspect`, `complete`, `baselines`, `benchmark`, and `reproduce-paper`.

## Upgrade an existing 0.1.x result archive

```powershell
am-spd convert-archive reconstruction.npz reconstruction.amspd
```

This preserves the old archive’s approximation and exact residual closure. The old format did not store packet atoms, tree selections, or portfolio trials, so those component records cannot be reconstructed by conversion alone.
