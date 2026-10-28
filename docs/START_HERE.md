# Start here

**Realization Calculus and Komorebi Space · Komorebi P.**

[Browse by work](BROWSE.md) · [Papers](browse/PAPERS.md) · [Written proofs](browse/PROOFS.md) · [Lean](browse/LEAN.md) · [Code](browse/CODE.md)

This collection studies how a construction can be represented, transformed, and checked while keeping track of the structure that makes it work. Realization Calculus develops operations on packets, coordinates, transfer blocks, and refinements. Komorebi Space supplies the ambient framework for comparing realizations, projections, compatibility, residuals, and obstructions.

The [public project and authorship statement](PROJECT_STATEMENT.md) explains the project's purpose, authorship, use of AI assistance, and publication circumstances. The collection remains a work in progress. For setup and check commands, use the [verification guide](VERIFICATION.md).

## Choose a reading route

For project readiness and remaining work, use the [completion and confidence guide](COMPLETION_STATUS.md) and [finalization queue](FINALIZATION_QUEUE.md).

| Goal | Begin with |
|---|---|
| Understand the common language | [Realization Calculus](works/realization-calculus-book.md) and [Komorebi Space](works/komorebi-space.md) |
| Study the individual developments | [Papers I–XII](../papers/README.md) |
| Understand limits of representation | [Realization Boundaries](works/realization-boundaries.md) |
| Read a small formal example | [Research Preview 1](../formal/research-preview-1/README.md) |
| Follow an application | [Monographs and companion volumes](../monographs/README.md) |
| Explore an open mathematical program | [Research programs and their scope](../research/README.md) |
| Work with executable mathematics | [Software guide](LIBRARIES.md) and [experimental laboratories](../experiments/README.md) |
| Study method and review | [Proof Path Theory](works/proof-path-theory.md) and [Komorebi Methodology](works/komorebi-methodology.md) |

## Four questions to carry through the collection

1. **What is the object?** State the space, coefficient system, and admissible inputs.
2. **How is it resolved?** Identify the packets, coordinates, or other components used to represent it.
3. **How does the operation transfer?** Determine the blocks or compatibility laws relating representations.
4. **What is reconstructed?** State the recovered object and any residual or obstruction.

For a finite projector decomposition, the starting identity is

$$
x=\sum_i P_i x.
$$

The useful content lies in the projector hypotheses, the maps acting between components, and the behavior under refinement. An example's finite identity retains its own scope in a larger argument.

## A concrete arithmetic example

[Research Preview 1](../formal/research-preview-1/README.md) studies prime-power Cartier systems. An integer polynomial mask determines a formal series at fixed prime-power precision. A finite linear machine computes coefficients from digit words. Its minimum-cardinality statement concerns the declared finite linear realization class, coefficient ring, and alphabet.

From that component directory, run:

```bash
python -B demo.py
```

For proof reproduction, follow its [pinned Lean environment](../formal/research-preview-1/REPRODUCE.md). The [workflow guide](WORKFLOWS.md) explains the separate collection checks and manual proof replay.

## Interpret the evidence

| Evidence | What to inspect |
|---|---|
| Written theorem | Exact conclusion, assumptions, and argument. |
| Lean declaration | Formal statement, imports, axioms, environment, and compilation record. |
| Exact finite calculation | Inputs, arithmetic model, computed property, and the argument connecting it to a broader result. |
| Numerical experiment | Precision, tested range, reference calculation, error criteria, and retained outcomes. |
| Software test | Exercised behavior, platform, dependencies, and source revision. |
| File-integrity record | The exact bytes and source snapshot it identifies. |

A proved implication remains a result when an application premise is open. Applying it requires that premise. Paper XI's Conjecture 66 and the remaining Physics and machine-model obligations retain that distinction.

All software is **beta and work in progress**. Follow the [citation guidance](../CITATION.md) for the specific work and revision you use.

[Complete component index](COMPONENT_INDEX.md) · [Collection](../README.md)
