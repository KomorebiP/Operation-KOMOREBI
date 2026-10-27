# Public API for 2.3.0

Import from `komorebi_pr_lasm`. The compatibility implementation namespace remains
`komorebi_arc3_offline`. It must not be co-installed with the separate ARC3 agent
package that owns the same namespace.

| Entry point | Contract |
|---|---|
| `analyze_signal(x, modulus=4, maximum_depth=6)` | Nonempty finite real 1D input. Float64 exact-coordinate snapshot without padding. |
| `SignalAnalysis1D.reconstruct(atlas)` | `spatial`, `fourier`, `polyphase`, or `packets`. Returns the full original-length signal, up to floating-point roundoff. |
| `polyphase_analyze(x, modulus)` | Complete residue-channel dictionary, including empty high-index lanes. |
| `polyphase_synthesize(channels, length, modulus)` | Validates the complete channel family and expected lengths. |
| `PolyphaseFIR(taps, modulus)` | Explicit blocks `E[r,s,m] = h[N*m+r-s]` with zero extension. |
| `PolyphaseFIR.apply(x)` | Full finite convolution, length `len(x)+len(taps)-1`. |
| `PolyphaseFIR.compose(earlier)` | Apply `earlier` first, then this filter. Requires equal moduli. |
| `StreamingFIR.process(chunk)` | One causal output per input sample, retaining finite history. |
| `StreamingFIR.flush()` | Return the tail once. Call `reset()` before the next stream. |
| `save_signal_archive(analysis, path)` | Atomic source-signal archive. No trained-model state is saved. |
| `load_signal_archive(path)` | Validates metadata/checksum and recomputes coordinates. No pickle. |
| `MultiAtlasAnalyzer.analyze(image)` | Finite real 2D input. Color atlas only for integral, in-palette data. |
| `PacketTree.analyze(x, maximum_depth)` | Complete dyadic tree at a feasible depth. |
| `best_basis(tree, ...)` | Minimum supplied additive cost among complete antichains of the finite tree. |
| `UltimateLASMPacketizer.resolve(...)` | Exact original categorical frame plus legacy fixed-size statistical features. |
| `ProjectorResolvedLargeSignalModel` | Finite typed regression portfolio, held-out candidate scoring, optional all-record refit. |
| `StateTransitionGraph` | Observed deterministic replay with contradictory-edge exclusion. |

See [the full guide](RELEASE_GUIDE.md) for executable examples, learning semantics,
coordinate conventions and limitations. Constructor details and types are documented
in source docstrings. See [migration notes](migration-2.3.md) before updating callers.
