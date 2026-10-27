# Public API map

New code should import from `komorebi_pr_lasm`. The
`komorebi_arc3_offline` namespace remains the implementation and backwards
compatibility layer.

## Exact atlases

```python
from komorebi_pr_lasm import MultiAtlasAnalyzer, MultiAtlasConfig
from komorebi_pr_lasm.atlas import haar2d_forward, polyphase2d_analyze
```

Key objects:

- `AtlasAnalysis`
- `MultiAtlasAnalyzer`
- `MultiAtlasConfig`
- exact Haar, Fourier, polyphase, wavelet-projector, and color functions

## Refinement

```python
from komorebi_pr_lasm.refinement import PacketTree, best_basis
```

Key objects:

- `PacketTree`
- `BestBasisResult`
- `best_basis`
- `l1_packet_cost`
- `shannon_packet_cost`

## World model

```python
from komorebi_pr_lasm import ProjectorResolvedLargeSignalModel
```

The model fits a posterior over `LASMProgram` objects and exposes posterior
summaries and action-predictive mixtures.

## Agent

```python
from komorebi_pr_lasm.agent import UltimateAgentConfig, UltimateLargeSignalAgent
```

The agent combines the exact packetizer, typed model, memory, replay graph,
and action utility.
