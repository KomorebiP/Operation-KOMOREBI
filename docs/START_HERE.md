# Start here

**Realization Calculus and Komorebi Space · Komorebi P.**

[Notation index](NOTATION_INDEX.md) · [Browse by work](BROWSE.md) · [Papers](browse/PAPERS.md) · [Written proofs](browse/PROOFS.md) · [Lean](browse/LEAN.md) · [Code](browse/CODE.md)

Komorebi studies how to describe an object in parts, carry out operations through those parts, and account for what changes when the description changes. A central question is whether a representation preserves enough information for the task we want to perform.

For example, we can split a vector into coordinate pieces and reconstruct a matrix operation from the blocks between them. We can reorganize a signal into finer address classes and recover the same signal. If a summary discards a distinction needed by a question, we can sometimes exhibit a specific witness showing why exact recovery is impossible.

Realization Calculus develops the language of packets, seeds, coordinates, transfer and refinement. Komorebi Space supplies a broader setting for comparing realizations, compatibility conditions, residuals and obstructions. The collection develops these questions across algebra, analysis, arithmetic, signals, computation and models of interacting systems.

The [project map](PROJECT_MAP.md) shows the subject groups and selected source dependencies. The [three demonstrations](DEMONSTRATIONS.md) let you follow the basic ideas from a hand calculation to a runnable program and the relevant mathematical sources.

The [public project and authorship statement](PROJECT_STATEMENT.md) explains the project's purpose, authorship, use of AI assistance, and publication circumstances. The collection remains a work in progress. For setup and check commands, use the [verification guide](VERIFICATION.md).

## What the project is trying to contribute

The aim is a reusable mathematical language for constructions that can otherwise look unrelated: resolving an object into parts, transferring operations, comparing resolutions and exposing compatibility failures. The papers state particular results within particular settings. Their definitions, hypotheses and proofs are where a contribution must be assessed.

Elementary examples make the language concrete. They do not by themselves establish novelty, a general unification theorem or an application claim. A result over a finite module cannot be transferred to an infinite, analytic or empirical setting without the required argument.

## Start with a complete demonstration

| Start from this question | Follow this route | Background |
|---|---|---|
| Can smaller operations reconstruct the whole operation? | [Reconstruct an operator from packet blocks](demonstrations/PACKETS.md) | Small matrix products |
| What does a finer description preserve, and what does deletion lose? | [Refine a signal and account for a missing packet](demonstrations/REFINEMENT.md) | List indexing and sums |
| Can a summary answer the question being asked? | [Test recovery from a summary](demonstrations/RECOVERY.md) | Addition and functions |

Each route includes a worked calculation, a small exact program, expected output and evidence links. You can read it without installing software. The [program](DEMONSTRATIONS.md#run-without-installing-a-library) needs only Python's standard library.

These are representative starting points chosen for clarity and reproducibility. The [work pages](BROWSE.md) retain the separate completion, Lean and confidence assessments for the wider results.

## Where the work stands

The collection contains scoped formal results, written mathematics, conditional developments and experiments at different stages. A finished reading edition can still contain open conjectures. Software remains beta.

Use the [current finalization queue](FINALIZATION_QUEUE.md) for the work still to do. Its maintenance focus remains navigation, edition records and reproducibility. Further proof reviews are deferred. When review resumes, the [project map](PROJECT_MAP.md#documented-connections) provides selected source connections to inspect, while the [status catalogue](STATUS_CATALOG.md) and [dated records](RECORDS.md) provide the actual assessments. A complete theorem dependency audit remains to be done.

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

For a finite family of pairwise annihilating idempotents whose sum is the identity, the starting reconstruction identity is

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
