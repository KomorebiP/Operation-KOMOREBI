# Start here

**Realization Calculus and Komorebi Space · Komorebi P.**

Komorebi studies how mathematical structure behaves when its description changes. Decomposing an object, changing coordinates, or forming an abstraction can make a problem easier to approach. The question is whether that description retains enough information for the task, and how to account for what is lost.

Realization Calculus develops decomposition, transfer, refinement, and reconstruction through packets, seeds, coordinates, and explicit residuals. Komorebi Space provides a setting for comparing realizations, their compatibility conditions, and the obstructions to moving between them.

The collection develops these questions across algebra, analysis, arithmetic, signals, computation, and models of interacting systems. The [project map](PROJECT_MAP.md) shows how the subjects connect. [Browse by work](BROWSE.md) to reach a particular paper or monograph and its source files.

## What the project is trying to contribute

The aim is a reusable mathematical language for resolving objects into parts, transferring operations, comparing descriptions, and exposing failures of compatibility. Recording the conditions for reconstruction and the residuals of a failed transfer makes those conditions part of the construction itself.

Each work's contribution is expressed in its definitions, results, constructions, and proofs. A connection between subjects requires an argument showing that the relevant structures and hypotheses survive the transfer. The scope of that argument determines where the result applies.

## Choose a reading route

Start with the subject or kind of work that interests you. Each route leads to the relevant manuscripts, sources, and recorded evidence.

| Goal | Begin with |
|---|---|
| Understand the common language | [Realization Calculus](works/realization-calculus-book.md) and [Komorebi Space](works/komorebi-space.md) |
| Study the individual developments | [Papers I–XII](../papers/README.md) |
| Understand limits of representation | [Realization Boundaries](works/realization-boundaries.md) |
| Explore the research preview | [Euler numbers through packets, polynomials, and residuals](demonstrations/EULER_PACKETS.md) |
| Follow an application | [Monographs and companion volumes](../monographs/README.md) |
| Explore an open mathematical program | [Research programs and their scope](../research/README.md) |
| Work with executable mathematics | [Software guide](LIBRARIES.md) and [experimental laboratories](../experiments/README.md) |
| Study method and review | [Proof Path Theory](works/proof-path-theory.md) and [Komorebi Methodology](works/komorebi-methodology.md) |

## Where the work stands

The collection contains written mathematics, formal developments, conditional results, software, and experiments at different stages of completion and review. The [completion and confidence guide](COMPLETION_STATUS.md) explains the status labels. The [status catalogue](STATUS_CATALOG.md) and [dated records](RECORDS.md) give the assessments for individual works and revisions.

The [finalization queue](FINALIZATION_QUEUE.md) lists the remaining work. Selected source connections are documented in the [project map](PROJECT_MAP.md#documented-connections); a complete theorem dependency audit remains open. A finished reading edition may still contain open questions, and a conditional result retains its assumptions.

## Four questions to carry through the collection

1. **What is the object?** State the space, coefficient system, and admissible inputs.
2. **How is it resolved?** Identify the packets, coordinates, or other components used to represent it.
3. **How does the operation transfer?** Determine the blocks or compatibility laws relating representations.
4. **What is reconstructed?** State the recovered object and any residual or obstruction.

<a id="start-with-a-complete-demonstration"></a>

## Worked calculations

The [demonstrations](DEMONSTRATIONS.md) offer optional introductions through hand calculations and exact programs. Choose one if you want to see how the terminology is used before following a longer development.

| Start from this question | Follow this route | Background |
|---|---|---|
| Can smaller operations reconstruct the whole operation? | [Reconstruct an operator from packet blocks](demonstrations/PACKETS.md) | Small matrix products |
| What does a finer description preserve, and what does deletion lose? | [Refine a signal and account for a missing packet](demonstrations/REFINEMENT.md) | List indexing and sums |
| Can a summary answer the question being asked? | [Test recovery from a summary](demonstrations/RECOVERY.md) | Addition and functions |

Each route includes a worked calculation, expected program output, and links to the relevant mathematical sources. You can read the calculations without installing software. The [program](DEMONSTRATIONS.md#run-without-installing-a-library) uses Python's standard library.

<a id="a-concrete-arithmetic-example"></a>

<a id="run-the-arithmetic-preview"></a>

## Research preview: Euler numbers

[Euler numbers through packets, polynomials, and residuals](demonstrations/EULER_PACKETS.md) follows one extended derivation through reciprocal series, polynomial coordinates, exact transfer matrices, and residual correction. The page includes hand calculations, failure controls, source references, and downloadable results.

Read the derivation [on the website](https://komorebip.github.io/Operation-KOMOREBI/collection/demonstrations/EULER_PACKETS.html), or run the exact checker from the collection root:

```text
python -B examples/euler_packets.py
```

Python 3.10 or later is sufficient; the checker uses only the standard library. A successful run ends with `PASS: Euler packets, polynomials and residuals`. You can also download the [standalone checker](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/euler_packets.py) or the [complete source and results bundle](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/source-and-checks.zip).

The example records its sources and tested ranges. The [workflow guide](WORKFLOWS.md) explains the collection's verification commands.

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


The [public project and authorship statement](PROJECT_STATEMENT.md) explains the pseudonym, AI assistance, and publication circumstances. For installation and check commands, use the [verification guide](VERIFICATION.md).

[Notation index](NOTATION_INDEX.md) · [Papers](browse/PAPERS.md) · [Written proofs](browse/PROOFS.md) · [Lean](browse/LEAN.md) · [Code](browse/CODE.md) · [Complete component index](COMPONENT_INDEX.md) · [Collection](../README.md)
