# Continuation — Sufficient Resolution v0.2.0

Read README.md, BLOCK_02_THEOREMS.md, PROGRESS.md and AUDIT.json first. Inspect
verification/release/report.json and verification/roundtrip/report.json. Replay
with scripts/verify.py and the exact pinned portable runtime before new work.

This is a standalone formalization program. Do not add its headline counts to
Papers I–XII or inference archives without qualified-name deduplication.

## Current production order

1. ExactResolution
2. Compression
3. Globalization
4. ObstructionTransport
5. Behavioral
6. Examples
7. DiscreteMemory
8. MemoryClosure
9. FiniteMemory
10. SplitMemory
11. MemoryExamples

All live under Komorebi/SufficientResolution/. Komorebi.lean imports them.
There are 125 explicit theorems and 169 explicitly named declarations. The six
v0.1.0 proof sources are unchanged. The original archive is preserved in history/.

## Completed new bridge

For block dynamics, E_n=A^n at all depths iff every M_k=B D^k G vanishes. The
actual hidden elimination and state/operator memory recurrences are checked.
Finite hidden dimension d gives a necessary-and-sufficient certificate M_k=0 for
k<d, equivalently operator equality through depth d+1. A monic annihilator gives
an even more general degree-controlled certificate. The zero-dimensional hidden
case is included. Any split compression is canonically represented using ker(C),
with exact conjugacy and certificate transfer.

## Recommended next block

Complete the finite-dimensional behavioral realization layer. The current
Behavioral.lean constructs the actual quotient and comparison map and proves
kernel-inclusion minimality. Prove comparison surjectivity, the minimal-dimension
inequality, and a finite closure construction with a termination bound. Specify a
finite alphabet when claiming an executable enumeration algorithm. Distinguish
universal source proofs from bounded tests and from inference of unknown operators.

The following directions remain open in this package: quantitative stability;
Hilbert-space compatibility/obstruction estimates; continuous-time memory;
positivity and integrality; nonlinear and categorical globalization; arithmetic
existence. Do not relabel the discrete recurrence as a continuous-time theorem.

## One-line continuation instruction

Open this ZIP, read CONTINUE_HERE.md and PROGRESS.md, replay the pinned verifier,
then prove the finite-dimensional behavioral minimality and terminating-construction
block while preserving every recorded proof boundary.
