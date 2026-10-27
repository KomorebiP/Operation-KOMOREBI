# Source and Claim Map

## Projector-Resolved Seed Calculus VIII
### Packet Algorithms and GPU Realization: Dense Operators, Block Transfer, and CUDA

**Author:** Komorebi P.

## Internal mathematical results

The paper proves the following within the document and verifies them in the companion code:

- exact reconstruction of a finite operator from packet blocks;
- arithmetic and representation counts for dense, block-diagonal, block-sparse, and block-diagonal-plus-low-rank operators;
- the equal-block BDLR reduction factor `n / (b + 2r)`;
- exact compressed multiplication of two BDLR operators with unrecompressed rank at most `r_A + r_B`;
- the Woodbury packet inverse under the stated invertibility hypotheses;
- path support of powers of a packet transfer graph;
- the block-Jacobi condition-number bound under normalized coupling norm below one;
- invariant-packet Krylov decomposition;
- packetwise mixed-precision error bounds;
- the continuous sensitivity-weighted precision-allocation formula;
- structure-discovery, transfer, compilation, and CUDA Graph amortization thresholds;
- launch-count reduction by grouping equal-shape packets.

## Classical inputs

The paper uses standard finite linear algebra, matrix multiplication counts, the Woodbury identity, Krylov methods, operator norms, batched matrix multiplication, GPU device-resident timing, CUDA Graph replay, and floating-point formats as classical inputs. Paper-local references are intentionally omitted. These sources will be entered in the consolidated end-of-series bibliography.

## Measured source corpus

The empirical section is derived from the supplied full benchmark corpus. The sanitized release contains 154 measured rows from sixteen suites, with 74 CPU and 80 GPU measurements. The recorded GPU is an NVIDIA GeForce RTX 3070 Ti Laptop GPU. The sanitization process removes:

- local user paths;
- user-directory names;
- raw machine timestamps;
- process listings;
- toolchain file paths.

The benchmark source distinguishes:

- case identifiers;
- mathematical output contracts;
- timing scopes;
- CPU and GPU representations;
- device-resident and end-to-end timings;
- logical and modeled executed work;
- representation memory;
- correctness errors;
- one-time discovery and reuse counts.

No measured row is invented or re-timed in the paper build. Figures and summary tables are computed from the sanitized measurements.

## Numerical certificates generated in this release

The current release reruns exact finite CPU certificates for:

- BDLR application;
- Woodbury solve;
- exact compressed BDLR product;
- block-sparse application;
- mixed-precision error bounds;
- packet-preconditioned conjugate gradient;
- complexity and storage formulas;
- amortization thresholds.

These finite certificates are separate from the imported measured GPU corpus.

## Conjectural statements

The following are not presented as proved:

- existence of an automatic packet compiler with a universal approximation factor;
- globally optimal packet discovery;
- refinement-stable compilation for arbitrary operator families;
- asymptotic data-movement optimality of a packet-native memory hierarchy;
- optimality of a proposed packet accelerator;
- a new generic dense matrix-multiplication exponent.

## Negative evidence retained

The source corpus includes cases where the candidate structured or mixed-precision method is slower than the matched baseline. The paper retains Strassen, recursive HODLR, iterative-refinement, small Walsh-Hadamard, and two-stream overlap negative controls.

## Reference policy

The LaTeX source contains no `\cite`, `\bibitem`, or `thebibliography` commands. References will be added only to the consolidated bibliography at the end of the complete series.
