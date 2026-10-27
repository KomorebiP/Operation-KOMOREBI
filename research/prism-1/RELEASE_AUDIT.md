# Komorebi PRISM-1 final updated release audit

## Artifact inventory

- architecture specification: **61 pages**
- generated visuals: **43 vector-PDF and 43 PNG figures**
- behavioral, planning, and performance model: `prism_chip_model.py`
- behavioral self-tests: **18**
- independent pytest tests: **18**
- Packet IR examples: **4**
- SystemVerilog boundary modules: **11**
- supporting documents: data sheet, command specification, compiler specification, and microarchitecture specification

## Architectural changes in this edition

- no dense-matrix preservation requirement
- shared Packet IR for CUDA and PRISM
- Packet Streaming Multiprocessor hierarchy with four execution groups per multiprocessor
- PMR-GEMM mixed-representation planning
- explicit output contracts
- measured packet CUDA baselines separated from PRISM architecture estimates
- representation, kernel, architecture, and amortization gains kept distinct
- representation router, PSM scheduler, and execution-group RTL boundaries added

## Mathematical and behavioral checks

- packet reconstruction residual: `0.0`
- polyphase reconstruction residual: `0.0`
- Haar reconstruction residual: `4.441e-16`
- BDLR application residual: `1.421e-14`
- local schedule substitution: passed
- descriptor contract: passed
- precision allocation: passed
- certificate-gated commit: passed
- local refinement bound: passed
- compiler route policy: passed
- package bandwidth hierarchy: passed
- PSM hierarchy: passed
- PMR-GEMM Bellman planner: passed
- output-contract legality: passed
- measured CUDA registry: passed
- gain decomposition: passed
- representation registry: passed

The executable model passed **18 of 18 self-tests**. The independent suite passed **18 of 18 tests**.

## Paper and layout checks

- PDF opens normally and is not encrypted
- PDF is text based rather than image only
- page count: **61**
- PDF preflight warnings: **0**
- LaTeX overfull boxes: **0**
- LaTeX underfull boxes: **0**
- undefined references: **0**
- fonts embedded: yes
- visible semicolons in the paper and prose documentation: **0**
- production-process wording found by the prose scan: **0**
- all pages rendered at 180 DPI and reviewed through the final contact sheet
- representation, PSM, compiler, performance, FPGA, source-map, and RTL pages inspected at full resolution
- no blank or isolated one-line pages observed

## Performance status

The paper carries three kinds of results:

1. measured packet CUDA rows from the earlier RTX 3070 Ti Laptop GPU study
2. exact representation reductions from the operator formulas
3. PRISM architecture-model estimates

The categories remain separate. The dense-route BDLR figure of **37.80x** is a total route model because it combines representation and architecture. It is not labeled as PRISM-over-CUDA architecture gain.

The same-structure architecture models estimate:

- polyphase edge recovery: **2.96x**
- fused multi-atlas pipeline: **1.64x**
- shape-batched Bayesian posterior: **1.42x**

These are estimates, not measured FPGA, ASIC, or silicon timings.

## Work not performed

No HDL simulation, synthesis, static timing, formal equivalence, power signoff, floorplanning, or place-and-route result is claimed. The SystemVerilog files define control and interface boundaries for staged implementation.

## Clean source validation

The source archive was extracted into a separate directory. The extracted copy completed:

- full internal checksum verification
- architecture-model regeneration
- 18 of 18 behavioral self-tests
- 18 of 18 independent tests
- regeneration of all 43 figure pairs
- LaTeX rebuild to the same 61-page paper
- PDF preflight with no warnings
