# Moving from AM-SPD 0.3 to 1.0

Existing high-level methods and valid model schemas remain available. The following corrections intentionally reject or change previously ambiguous behavior.

| Earlier behavior | Version 1.0 behavior |
|---|---|
| Out-of-range floats silently min/max normalized | Normalize explicitly before calling, or supply a valid integer raster |
| Constant integer images could become zero | Integer values scale by their declared dtype maximum |
| Fractional or Boolean counts were coerced | Supply integers; invalid values raise `ValueError` |
| Zero refresh intervals could fail during search | Supply positive refresh intervals |
| Explicit downstream budget could be exceeded by a retained seed | SPD/tree/portfolio added proxy cost respects the budget, including zero |
| Exact CLI decode could write a quantized display file | Use `decode model.amspd exact.npy --mode exact`; use bounded mode for PNG |
| RGBA/palette transparency discarded | Alpha remains a separate channel |
| 16-bit grayscale converted to 8-bit | Loading preserves declared 16-bit depth |
| Batch files sharing the same relative stem could overwrite | Resolve the filename collision before starting the batch |
| Missing requested models could still count as skipped | The file is reprocessed |
| Runtime broke tuning ties | Parameters, RMSE, then declaration order break ties |
| Empty/fractional grids and nonfinite objective arguments accepted | Supply a nonempty finite valid grid |

The finite source contract is a nonempty H×W or H×W×C raster. High-level reconstruction requires height and width at least 8. Float values must be finite and lie in `[0,1]`. For signed integer arrays, negative values are rejected and nonnegative values use the dtype maximum. Signed scientific Pillow files require explicit conversion to a normalized `.npy` raster. Standard display output supports 1, 3, or 4 channels and quantizes to 8-bit; other channel counts should use NumPy output.

Regenerated decompositions may differ from 0.3 because corrected orthogonalization removes spurious numerical directions. Historical benchmark references remain available through the dedicated replay path.
