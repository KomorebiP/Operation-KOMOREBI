# Komorebi Neuralese Operator Workspace v0.3.0

V0.3 tests whether exact architectural norm preservation repairs the dynamical
collapse found in v0.2 without destroying learned operator execution. The
answer is mixed, and the frozen Stage A primary **failed overall: 8 of 26 gates
passed**.

The sign-canonical QR arm preserved latent norm through 2,048 recurrent steps
in every test seed, exactly as its parameterization requires. It did not learn
reliable operator semantics across seeds. All positive learned-behavior,
anonymous-closure, and cross-context-patch gates failed. The soft-penalty arm
was much more accurate through depth 128, but its state collapsed by depth
2,048.

## Stage A primary result

| Test-split metric | Hard correct | Hard shuffled | Soft correct | Soft shuffled |
|---|---:|---:|---:|---:|
| D4 endpoint accuracy, depth 8 | 0.8757 | 0.8913 | **1.0000** | 0.9990 |
| D4 endpoint accuracy, depth 64 | 0.4840 | 0.1955 | **0.9054** | 0.1466 |
| D4 endpoint accuracy, depth 128 | 0.3576 | 0.1401 | **0.5521** | 0.1361 |
| C8 endpoint accuracy, depth 64 | 0.3960 | 0.1401 | **0.7869** | 0.1489 |
| Random-family accuracy, depth 64 | 0.1800 | 0.1292 | **0.2796** | 0.1403 |
| Median endpoint/start norm, depth 2,048 | **1.0000** | **1.0000** | approximately 0 | approximately 0 |
| Composition substitution | 0.8636 | 0.8621 | 0.8822 | 0.8854 |
| Sequential/direct agreement | 0.5951 | 0.5915 | 0.6697 | 0.6725 |
| Median closure residual | 1.1575 | 1.1714 | 0.8589 | 0.9228 |
| Cross-context patch accuracy | 0.2189 | 0.2150 | 0.4429 | 0.3853 |

The hard arm was strongly bimodal: some seeds executed long compositions well,
while others remained near chance. Its mean D4 depth-64 advantage over the
hard shuffled arm was 0.2886, but only 7/12 seed pairs cleared the frozen
per-seed margin, below the required 8/12. A post-hoc paired bootstrap gave a
95% descriptive interval of [0.1143, 0.4744]. This interval is exploratory and
does not revise the failed frozen gate.

Hard QR solved the stability problem by construction, not by learning it. Its
depth-2,048 norm ratio was 1.00001, P95 transient gain was 1.00009, and P95
orthogonality defect was \(3.11\times10^{-7}\). But it underperformed the soft
correct arm by 0.4214 at D4 depth 64. The result exposes a stability/trainability
tradeoff rather than a successful joint solution.

## Transport result

Six hard-arm seed pairs reached 0.8495 aligned D4 state-patch accuracy, versus
0.1218 for shuffled-pair fitting and 0.1069 for a random map. A discrete
decode-to-state-label then target-re-embed baseline reached 0.9088. Stage A
therefore does not establish transport richer than the eight-state codebook.

## Split discipline

Every sampled training word had every nonempty contiguous subword action in the
train map partition. Direct conditioned sampling produced 49,152,000 primary
training examples with zero split violations. The separate split-conditioned
assay additionally required each full terminal word action to be in the test
partition.

This is still not globally novel group-element evaluation. D4 actions can be
algebraically regenerated from train actions even when the scored primitive
tables and terminal action are test-ranked. The broad depth assay holds out
primitive tables only; the split-conditioned assay has the narrower terminal
action guarantee.

## Protocol and integrity receipts

- Primary protocol: `protocols/V0_3_STAGE_A_PRIMARY.json`
- Primary protocol SHA-256: `ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf`
- Scientific-code SHA-256: `814ea6f2301523965bf8d94dd9da8bbb598451f03e0200cae1cde2ab8de53624`
- Coordinate-split SHA-256: `3aceaac6852f88360de0851eefc43bf46331d3b4efe3a04d0f2b9dfeff455340`
- Primary seal: `protocols/V0_3_STAGE_A_PRIMARY_SEAL.json`
- Primary seal file SHA-256: `84c15ffcef8553288fe3e3393e7056ca0c1cfcdd8c78639f61d0adfe6d80f5c9`
- Primary result: `results/v0.3.0/stage_a_primary_v3/`
- Completed primary receipt SHA-256: `1854d622e6154a44107da80164c77c306ac7a5472583e089e6188738b9e294e7`
- Qualification protocol SHA-256: `0bca42f89400904180f36872aaa4fb8040c2cb848b86e50dc084eb90a47634a0`
- Qualification receipt SHA-256: `511d706bd82f910d1817e21e99aa58823e86707b5652736fd74281e2d75e7f55`
- Grid: 4 arms x 12 seeds = 48 complete cells; 6 transport pairs
- Training: 49,152,000 directly conditioned examples; zero split violations
- Exact table oracle: passed

The primary was sealed after disclosed development-only calibration and before
test coordinates were opened. An execution supervisor later interrupted the
original process without a scientific failure record; deterministic recovery
validated existing cells and completed the remaining cells and transport pairs.
`results/v0.3.0/stage_a_primary_v3/RECOVERY_EVENTS.json` records every resume.

## Stage B scaffold

V0.3 also adds a sparse GF(5)^4 task and a functional transport assay, but no
trained Stage B primary result. The learner-facing sparse input contains five
demonstrations per anonymous primitive, a start state, and a length-at-least-two
word—no dense tables, intermediate targets, truth IDs, or audit masks.

The monomial family has zero held-out primitive collisions within the bounded
length-2--4 same-context training language. The shear family has 86/96 such
collisions and is unsafe for that novelty claim. Pooling train generators makes
all 96 held-out primitives reachable by depth 3 in both families, so neither
supports unbounded group-element novelty.

## Interpretation boundary

Stage A uses complete transition tables, a fixed \(G=I\), and an explicit 8x8
matrix-operator channel. The hard and soft arms share raw initialization
tensors, but their projections produce different effective initial dynamics
and computational costs. This is a whole-treatment engineering comparison, not
a clean one-factor causal contrast or a formal noninferiority test.

The package does not establish a learned invariant metric, exact latent algebra,
cross-context causal state semantics, spontaneous Neuralese, an unconstrained
language-model mechanism, awareness, or consciousness.

## Next block

The canonical next block is a **developmental sparse factor-inference bridge**.
A model must infer anonymous signed-monomial affine factors from five
demonstrations, then compile them into the exact orthogonal torus executor. This
removes the full-table shortcut and separates learned operator identification
from guaranteed recurrent stability. It should remain developmental until
joint execution, depth-2,048 stability, causal specificity, and
residual-within-codebook transport gates can be frozen for a later primary.

A small Stage A trainability sidecar should compare smoother orthogonal or
staged soft-to-hard treatments from matched *effective* initial operators. It
is a diagnostic for the QR optimization failure, not the flagship next block.

Read `results/v0.3.0/INTEGRATED_FINDINGS.md` for the complete interpretation and
next-block recommendation.

## Verify and rerun

```powershell
$ErrorActionPreference="Stop"; $Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.3.0"; Set-Location $Root; python .\verify_package.py
```

```powershell
$ErrorActionPreference="Stop"; $Root="$HOME\Downloads\Komorebi_Neuralese_Operator_Workspace_v0.3.0"; Set-Location $Root; $Out=Join-Path .\local_runs ("primary_"+(Get-Date -Format "yyyyMMdd_HHmmss")); python .\run_experiment.py --protocol .\protocols\V0_3_STAGE_A_PRIMARY.json --output-dir $Out --device cpu --threads 4
```

The runner refuses a nonempty output directory. Scientific gate failure is
preserved as a result and is distinct from operational failure.
