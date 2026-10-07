# Start here

Operation Komorebi studies representation changes through transformations, compatibility, residuals, obstructions, and realization. The program combines written mathematics, formal statements, executable constructions, finite certificates, and controlled experiments. Each contribution retains the evidence appropriate to its claim.

## Read one complete development

Begin with [Research Preview 1](../formal/research-preview-1/README.md), then its [mathematical note](../formal/research-preview-1/THEOREM_NOTE.md) and [claim map](../formal/research-preview-1/CLAIMS.md). This component gives a precise arithmetic example of the program: an integer polynomial mask determines a formal series at fixed prime-power precision, and a finite linear machine computes its coefficients from digit words.

The result concerns finite linear realizations over the supplied coefficient ring and alphabet. Its minimum-cardinality theorem does not assert one finite machine for all precisions or a fastest implementation.

Run its small Python example from the component directory:

```bash
python -B demo.py
```

The [reproduction contract](../formal/research-preview-1/REPRODUCE.md) separates finite calculation, source-integrity checks, and a Lean proof replay.

## Follow the paper sequence

[Papers I–IV](../papers/README.md) establish the core language and early applications. Subsequent papers extend the calculus to signals, stochastic and quantum models, algorithms, arithmetic, residual systems, and local/global comparison. The paper index states which editions are actually imported.

The selected final Paper XI edition presents the general realization endpoint as **Conjecture 66**. Its proved finite constructions and conditional comparisons remain substantive results. The existence input in a comparison interface is not a proof of its arithmetic realization.

The recent Signal, Stratified Universality, K-COS, and OSL/Neuralese editions have separate source candidates. Their status and evidence are recorded individually in the [contribution ledger](../CONTRIBUTIONS.md). A final reader edition does not automatically provide a new proof or implementation replay.

## Install the independent libraries

[Komorebi Math and Polyphase Float](LIBRARIES.md) are separately staged source candidates. Each keeps its own build, dependency, version, license, and validation contracts. The central repository will identify their exact published commits once those commits exist.

## Interpret the evidence

| Evidence | What it establishes |
|---|---|
| Written proof | The stated mathematical argument under its explicit assumptions. |
| Accepted Lean declaration | The formal conclusion follows from its binders, imports, and foundational dependencies in the recorded environment. |
| Exact finite certificate | The named finite property, or a universal result when a proved reduction supplies that bridge. |
| Experiment | The recorded outcome under its protocol, tested range, controls, and model selection procedure. |
| Software test | Behavior on the tested inputs, platforms, and configurations. |
| Integrity check | Agreement of files or manifests with a selected source snapshot. |

A complete implication retains its theorem status while an application premise remains open. A parent program can remain unfinished while its completed components are publishable. Preserved failures and amendments help readers determine which guarantees survive.

## Contribute a correction

Identify the exact component and revision, the claim or function concerned, and the discrepancy. Include an input or proof dependency when relevant. The [contribution index](../CONTRIBUTIONS.md) tracks source recovery and release disposition without silently turning older reports into current validation.

See [distribution status](DISTRIBUTION_STATUS.md) before treating this assembly as a published release.

