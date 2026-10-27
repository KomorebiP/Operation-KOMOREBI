# Komorebi PRISM-1 final updated architecture

**Projector-Resolved Integrated Signal Machine**

PRISM-1 is a packet-programmable mixed-representation processor for Projector-Resolved Seed Calculus and PR-LASM workloads. A program may remain in block, low-rank, Kronecker, sparse-factor, transform, packet-graph, or explicit-array form. The chip preserves the requested output contract rather than an unnecessary dense intermediate.

## Release contents

- final updated architecture paper
- 43 vector-PDF and 43 PNG figures
- executable architecture, planning, and performance model
- 18 behavioral self-tests
- 18 independent tests
- four Packet IR examples
- eleven SystemVerilog boundary modules
- data sheet, command specification, compiler specification, and microarchitecture notes
- machine-readable results, manifest, and checksums

## Reference configuration

- 4 compute chiplets
- 16 Packet Streaming Multiprocessors per chiplet
- 64 Packet Streaming Multiprocessors total
- 4 execution groups per multiprocessor
- 256 execution groups total
- one 16 by 16 matrix array plus vector lanes per execution group
- 2 MiB packet scratchpad per multiprocessor
- 32 transform engines
- 16 small-solver engines
- 4 exact-arithmetic clusters
- 192 MiB total local and shared SRAM
- 4 HBM4 stacks with 144 GiB reference capacity
- more than 11.2 TB/s aggregate reference HBM bandwidth
- UCIe 3.0 class package links
- PCIe 7.0 x16 class host attachment
- 500 W package target

These are architecture targets, not measured silicon results.

## Run the model and tests

Linux or WSL:

```bash
./run_all.sh
```

PowerShell:

```powershell
& .\Run_All.ps1
```

Direct commands:

```bash
python prism_chip_model.py --root .
PYTHONPATH=. python -m pytest -q
```

## Build the paper

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error Komorebi_PRISM_1_Final_Updated.tex
```

## Design boundary

The package contains a behavioral architecture, a mixed-representation planner, a CUDA-compatible Packet IR, an executable cost model, and RTL boundary modules. It does not contain completed production RTL, synthesis, static timing, place and route, or measured FPGA or silicon performance.
