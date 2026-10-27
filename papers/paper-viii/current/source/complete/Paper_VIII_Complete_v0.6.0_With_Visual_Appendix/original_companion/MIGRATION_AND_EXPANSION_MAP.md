# Paper VIII migration and expansion map

## Purpose of the rewrite

The original Paper VIII combined exact packet algebra, complexity formulas, GPU implementation notes, measured benchmark rows, and several broad compiler and hardware conjectures. The strengthened edition reorganizes the material as a standalone computational mathematics article.

The revised theorem line is

```text
exact representation
→ cost model
→ structured primitives
→ low rank algebra
→ graph support
→ numerical certification
→ exact finite compilation
→ device scheduling
→ matched measurement
```

Generic operator identities already established in the foundational papers are used only where needed. The article focuses on the additional computational content.

## Section migration

| Original section | Final destination | Change |
|---|---|---|
| The computational seed realization | Packet operator representations | Rewritten as an exact intermediate representation with evaluation semantics, output contracts, and timing scopes |
| Arithmetic and storage models | Arithmetic, storage, and data movement | Expanded with a streaming byte model, arithmetic intensity, a roofline lower bound, capacity thresholds, and materialization cost |
| Exact BDLR algebra | Exact low rank algebra and recompression | Retained product and Woodbury identities, then added compact small core recompression and certified error propagation |
| Block sparse transfer graphs | Sparse transfer graphs and schedules | Expanded with polynomial support, acyclic nilpotence, triangular level schedules, inverse support, and Schur fill inclusion |
| Packet Krylov and preconditioning | Krylov methods and packet preconditioning | Tightened the Krylov definitions and preconditioned conjugate gradient hypotheses |
| Packetwise mixed precision | Packetwise mixed precision | Expanded from a block perturbation bound to continuous, clipped, and exact discrete precision allocation |
| GPU mapping of packet operators | Device scheduling and amortization | Recast as shape classes, critical path, graph replay, materialization, and reuse thresholds |
| Benchmark protocol and measured corpus | Benchmark contracts and measurement protocol | Added formal case signatures, output contracts, timing scopes, and fair matching |
| Dense baselines and the precision frontier | Recorded CPU and GPU corpus | Retained the sanitized values with matched scope and error statements |
| Measured structured operators | Recorded CPU and GPU corpus | Regrouped by regular packets, compressed products, discovery, transfer, and negative controls |
| Discovery, transfer, and reuse | Discovery and exact packet compilation plus scheduling | Separated structure discovery from compilation and one time amortization |
| Negative controls and crossover failures | Recorded CPU and GPU corpus | Retained as part of the main evidence rather than as an appendix |
| A fair packet benchmark decomposition | Benchmark contracts and measurement protocol | Replaced narrative decomposition with explicit definitions of representation, device, kernel, and amortization gain |
| Implementation patterns | Implementation and verification | Reduced to the declared reference interface and verification layers |
| Hardware co design | Hardware implications and exact boundaries | Kept as a delimited consequence section rather than a hardware claim |
| Proof, measurement, and claim ledger | Audit files outside the article | Removed from the visible manuscript and preserved in the package |
| Verification | Implementation and verification plus package tests | Expanded through a new deterministic verifier |
| Reproducibility and software map | Package README and verification directory | Removed from the article body |

## New mathematical material

### Exact representation and contracts

The revised article adds:

- a finite packet operator intermediate representation
- exact evaluation semantics
- composition, adjoint, and tensor rules
- output contract and timing scope definitions
- a formal contract conversion criterion

### Data movement and structured primitives

The revision adds:

- a one pass streaming byte model
- a roofline lower bound in the declared model
- memory capacity and materialization thresholds
- block banded counts
- sparse plus low rank counts
- circulant Fourier diagonalization
- Toeplitz circulant embedding
- Kronecker modewise application
- Walsh Hadamard recursion

### Low rank closure and certification

The revision adds:

- compact QR based small core recompression
- the best truncated approximation guarantee through the Eckart Young Mirsky theorem
- product chain perturbation
- a separate inhomogeneous repeated recompression recurrence

The final recurrence was written separately because repeated additive recompression error is not the same as perturbing every multiplicative factor.

### Graph algebra and scheduling

The revision adds:

- support of powers and polynomials
- nilpotence for acyclic strict transfer graphs
- topological level schedules
- inverse support inside the transitive closure
- Schur complement fill inclusion

### Mixed precision and compilation

The revision adds:

- continuous sensitivity weighted allocation
- clipped allocation with upper tolerance bounds
- an exact multiple choice dynamic program for discrete data types
- exact spectral block discovery certificates
- an exact Lagrangian tree compiler
- a monotone cost and error frontier theorem
- an exact quantized budget compiler
- compiler decision stability
- local recompilation along one ancestor chain

### Measurement discipline

The revision adds formal definitions of:

- case signature
- fair match
- representation gain
- device gain
- kernel gain
- amortization gain

The measured rows are not reinterpreted as universal hardware laws. They remain statements about the recorded environment and case signatures.

## Material retained outside the main article

The package preserves the following in `legacy/`:

- the original LaTeX manuscript
- the original source and claim map
- the original benchmark corpus
- the original implementation
- the original tests
- the original generated tables and figures

This material supports provenance and comparison but is not part of the final article body.

## Claims deliberately not promoted

The final article does not claim:

- a universal packet discovery algorithm
- a universal approximation factor for overlapping decompositions
- asymptotically optimal packet data movement
- an optimal packet accelerator
- a new exponent for generic dense matrix multiplication
- portability of the recorded speedups to other hardware
