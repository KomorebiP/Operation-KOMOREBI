# Source and Claim Map

**Author:** Komorebi P.

## Exact coordinate layer

| Source | Role | Principal claim type |
|---|---|---|
| `src/komorebi_arc3_offline/exact_atlas.py` | Spatial, Fourier, Haar, polyphase, color, and weighted multi-atlas transforms | Exact finite identities and constructions |
| `src/komorebi_arc3_offline/lasm_packetizer.py` | Exact archive, feature groups, nested statistical states | Deterministic construction |
| `src/komorebi_arc3_offline/lasm_refinement.py` | Complete packet trees, mixed-depth synthesis, best-basis dynamic program | Exact finite theorems and algorithms |

## Learned operator layer

| Source | Role | Principal claim type |
|---|---|---|
| `src/komorebi_arc3_offline/lasm_programs.py` | Typed linear, quadratic, bilinear, delay, fractional, Volterra, phase, gated, and hybrid programs | Definitions and exact design maps |
| `src/komorebi_arc3_offline/lasm_model.py` | Normal-inverse-gamma fits, posterior weights, predictive moments | Exact formulas under the declared finite model |
| `src/komorebi_arc3_offline/lasm_memory.py` | Lag, power-law, exponential memory, role statistics | Deterministic construction |

## Planning layer

| Source | Role | Principal claim type |
|---|---|---|
| `src/komorebi_arc3_offline/lasm_graph.py` | Exact state-action graph, frontiers, paths, nondeterminism marking | Exact finite graph algorithms |
| `src/komorebi_arc3_offline/lasm_agent.py` | Replay probes, utility, posterior planning, trace output | Executable finite algorithm |
| `src/komorebi_arc3_offline/lasm_mock_envs.py` | Four deterministic interactive systems | Controlled tests |

## Verification layer

| Source | Role | Principal claim type |
|---|---|---|
| `src/komorebi_arc3_offline/lasm_synthetic.py` | Seven controlled algebraic transition mechanisms | Controlled generators |
| `src/komorebi_arc3_offline/lasm_benchmark.py` | Exactness, operator identification, interactive benchmark | Finite numerical certificates |
| `tests/` | 36 automated tests | Implementation verification |
| `validation/suite_static_audit.json` | Static audit of 25 supplied local environments | Static certificate only |
| `paper/Projector_Resolved_Large_Algebraic_Signal_Model.tex` | Formal architecture, theorems, proofs, benchmark boundaries | Canonical paper source |

## Claims established by the release

1. Every included finite atlas has an explicit analysis and synthesis pair with checked reconstruction.
2. The positively weighted direct sum of the included unitary atlases is a finite tight frame with canonical synthesis.
3. Every complete mixed-depth pruning of the implemented finite packet tree synthesizes exactly.
4. The program posterior is a finite, typed Bayesian mixture under the declared normal-inverse-gamma model.
5. Deterministic observed transitions produce an exact finite state-action graph; detected nondeterministic edges are excluded from exact replay claims.
6. The controlled benchmark identifies the intended mechanism and atlas in all seven supplied cases.
7. The four supplied deterministic interactive systems are solved under their declared action interfaces.

## Claims not established

- an official ARC-AGI-3 score;
- successful execution of the 25 official local environments in this build container;
- universal or unrestricted program induction;
- universal optimality of one atlas, tree, prior, utility, or operator grammar;
- universal deterministic replay;
- AGI or general intelligence;
- historical priority over all related architectures.
