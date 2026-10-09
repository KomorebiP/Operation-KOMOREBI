# AM-SPD 0.3.0 functionality matrix

| Manuscript or practical operation | Implementation | Public route | Verification |
|---|---|---|---|
| Moving generative packet atlas | `am_spd.atlas` | `fit_packet_core`, `reconstruct --method core` | Unit, exact-resume, and historical verification |
| Singular Packet Decomposition | `am_spd.singular` | `fit_singular_packets`, `--method spd` | Unit and historical verification |
| Lagrange tree | `am_spd.multiscale` | `optimize_trees`, `--method tree` | Unit and full verification |
| Exact integer-budget tree | `am_spd.final` | `optimize_trees`, `--method tree` | Nondominance tests and historical exhaustive comparisons |
| Backward replacement portfolio | `am_spd.final` | `fit_portfolio`, `--method portfolio` | Unit and historical verification |
| Exact residual accounting | Result and model classes | `decode --mode exact` | Dense, sparse, single, and tiled round trips |
| Resumable packet checkpoint | `am_spd.model`, `am_spd.api` | `AMSpdModel.resume`, `resume` | Exact parity, frontier-exact, schema-1 warm-start, and CLI tests |
| Tiled large-image reconstruction | `am_spd.tiled` | `tiled_reconstruct`, `tiled` | Coverage, blend, closure, archive, and CLI tests |
| Resumable tiled checkpoint | `am_spd.tiled` | `TiledAMSpdModel.resume`, `resume` | Per-tile uninterrupted parity and round-trip tests |
| Single-image model format | `.amspd`, schema 2 | `AMSpdModel` | Checksum, schema compatibility, migration, and tamper tests |
| Tiled model format | `.amspdt`, schema 1 | `TiledAMSpdModel` | Global and embedded checksums plus structural validation |
| Model comparison | `am_spd.tiled` | `compare_model_archives`, `compare` | Pairwise reconstruction and metadata tests |
| Automatic finite-grid selection | `am_spd.tuning` | `auto_tune`, `tune` | Deterministic objective and CLI tests |
| Recursive batch processing | `am_spd.batch` | `run_batch`, `batch` | Single/tiled execution, skip, content hash, and configuration fingerprint tests |
| Pixel-coordinate closure | `am_spd.components` | `complete_with_pixels`, `complete` | Exact identity test |
| Fourier/DCT/SVD/quadtree/TV comparisons | `am_spd.components` | `compare_baselines`, `baselines` | Finite-output test |
| Built-in multi-method benchmark | `am_spd.benchmark` | `run_builtin_benchmark`, `benchmark` | CLI integration test |
| Exact four-case replay | `am_spd.reference` | `reproduce_paper_case`, `reproduce-paper` | Reference comparison ledger |
| Figure and table regeneration | `research/original` | Reproduction scripts | Historical verification |
| Focused manuscript build | `docs/paper/final` | Build scripts | Clean LaTeX audit |

## Remaining work before 1.0

- Define a stable multi-version migration policy for both model formats.
- Add an entropy-coded rate-distortion codec if compressed bit rate is a goal.
- Add GPU kernels for candidate scoring, refitting, and local SVD stages.
- Add a genuinely streaming execution path that does not materialize the complete raster.
- Add calibrated statistical noise models before presenting AM-SPD as an automatic denoiser.
- Add digital signatures or an external provenance mechanism if authorship authentication is required.
- Select a public-use license if unrestricted external adoption is intended.
