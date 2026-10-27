# Komorebi PRISM-1 reference data sheet

## Product role

PRISM-1 is a packet-programmable mixed-representation accelerator. It executes typed operator graphs without requiring an explicit dense matrix. The same Packet IR may lower to CUDA or PRISM.

## Reference package

| Item | Reference target |
|---|---:|
| Compute chiplets | 4 |
| Packet Streaming Multiprocessors | 64 total |
| Multiprocessors per chiplet | 16 |
| Execution groups | 256 total |
| Execution groups per multiprocessor | 4 |
| Matrix array per execution group | 16 by 16 |
| Clock target | 1.5 GHz |
| Packet scratchpad | 2 MiB per multiprocessor |
| Shared SRAM | 16 MiB per chiplet |
| Total local and shared SRAM | 192 MiB |
| Transform engines | 32 |
| Small-solver engines | 16 |
| Exact arithmetic clusters | 4 |
| HBM4 stacks | 4 |
| HBM capacity | 144 GiB |
| HBM bandwidth | more than 11.2 TB/s aggregate |
| Package link | UCIe 3.0 class at up to 64 GT/s |
| Host link | PCIe 7.0 x16 class |
| Package power target | 500 W |

## Arithmetic model peaks

| Format | Model peak |
|---|---:|
| FP16 or BF16 | 196.608 TFLOP/s |
| FP32 | 98.304 TFLOP/s |
| FP64 | 24.576 TFLOP/s |

These are model peaks. They are not measured device results.

## Executable representation forms

- explicit array
- block diagonal
- block sparse
- low rank
- block diagonal plus low rank
- Kronecker factors
- sparse factor chains
- transform-domain plans
- packet graphs

## Output contracts

- apply an operator
- return a compressed operator
- return a factor graph
- return a transform plan
- return an explicit array

Only the explicit-array contract requires full materialization.

## Principal engines

- Packet Streaming Multiprocessor front end and packet-warp scheduler
- four matrix and vector execution groups per multiprocessor
- projector and polyphase DMA
- shared transform fabric
- resident QR, SVD, root, and Vandermonde solvers
- exact modular and CRT arithmetic
- nonlinear and memory paths
- residual accumulator and certificate-gated commit

## Programming model

1. calculus graph
2. shared Packet IR
3. CUDA or PRISM backend lowering
4. Packet Seed Commands, descriptor tables, and runtime queue

## Verification status

The behavioral model passes 18 of 18 self-tests. The independent suite passes 18 of 18 tests. The RTL files remain boundary modules rather than completed production RTL.
