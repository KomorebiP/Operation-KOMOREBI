# Realization Calculus and Komorebi Space

**Komorebi P. · Work in progress**

[Open the reading website](https://KomorebiP.github.io/Operation-KOMOREBI/) · [Choose a reading route](docs/READING_ROUTES.md) · [Hand-worked examples](docs/HAND_WORKED_EXAMPLES.md) · [Glossary](docs/GLOSSARY.md) · [Download one work](docs/DOWNLOADS.md)

[Browse all works](docs/BROWSE.md) · [Read papers](docs/browse/PAPERS.md) · [Find proofs](docs/browse/PROOFS.md) · [Lean sources](docs/browse/LEAN.md) · [Code](docs/browse/CODE.md)

> **Author’s note:** This work is still in progress. Much of it has been rushed because of circumstances introduced by OpenAI. I am continuing to correct, verify, and organize it.

The [public project and authorship statement](docs/PROJECT_STATEMENT.md#current-state-and-publication-circumstances) explains this context. Each work is at a different stage of completion and review. All executable software remains **beta and work in progress**.

Realization Calculus studies how mathematical structure behaves under decomposition, coordinate change, transfer, and refinement. Its basic objects include packets, operator blocks, compatible realizations, and explicit residuals.

Komorebi Space provides a setting for comparing these constructions through realizations, projections, transfers, compatibility conditions, and obstructions.

## Start here

| Goal | Starting point |
|---|---|
| Open a paper, proof, Lean source, or code file | [Browse by work](docs/BROWSE.md), with direct links to files and evidence for each edition. |
| Understand the framework | [Reading guide](docs/START_HERE.md), then the foundations below. |
| Read the main developments | [Twelve core papers](papers/README.md) and [monographs](monographs/README.md). |
| Choose by readiness | [Completion stage, Lean coverage, and confidence](docs/COMPLETION_STATUS.md), with links to exact evidence. |
| Run or reproduce something | [Small example](#run-a-small-example), [software guide](docs/LIBRARIES.md), and [verification guide](docs/VERIFICATION.md). |
| Help finish the collection | [Finalization queue](docs/FINALIZATION_QUEUE.md) and [contribution guide](CONTRIBUTING.md). |

The [authorship statement](docs/PROJECT_STATEMENT.md) explains the pseudonym, the use of AI assistance, and how to assess the evidence.

## Foundations

| Work | Subject |
|---|---|
| [Realization Calculus](docs/works/realization-calculus-book.md) | The collected core development, from packets and transfer to refinement and applications. |
| [Komorebi Space](docs/works/komorebi-space.md) | The ambient framework for realizations, projections, compatibility, residuals, and obstructions. |
| [Realization Boundaries](docs/works/realization-boundaries.md) | Representability, finite descriptions, and explicit limits of realization. |
| [Sufficient Resolution](docs/works/sufficient-resolution.md) | Resolution conditions and the information retained by a representation. |

## Further reading

| Interest | Starting point |
|---|---|
| Arithmetic, special functions, and sequence constructions | [Special Functions](docs/works/monographs-special-functions.md) |
| Signals, quadratic forms, and numerical probability | [COS Method](docs/works/monographs-cos-method.md) and [Polyphase Signal Calculus](docs/works/paper-v.md) |
| Quantum models and circuit constructions | [Quantum and Circuits](docs/works/monographs-quantum-and-circuits.md) and [Quantum Seed Calculus](docs/works/paper-vii.md) |
| Discrete and continuous physical models | [Physics](docs/works/monographs-physics.md) |
| Algebraic signal models | [Large Signal Model](docs/works/monographs-large-signal-model.md) |
| Machine reasoning, abstraction, and interacting agents | [Machine Native Reasoning](docs/works/monographs-machine-native-reasoning.md) and [Machine Societies](docs/works/monographs-machine-societies.md) |
| Discovery, proof, and review | [Proof Path Theory](docs/works/proof-path-theory.md) and [Komorebi Methodology](docs/works/komorebi-methodology.md) |

## Software and experiments

**All software is beta and work in progress.** The implementations are available for research, evaluation, and feedback. Each package documents its supported inputs, dependencies, and numerical or computational limits.

- [Komorebi Math](https://github.com/KomorebiP/komorebi-math): Python tools for finite operators, packets, coordinates, signals, arithmetic, and certificates you can inspect.
- [Polyphase Float](https://github.com/KomorebiP/polyphase-float): C arithmetic with explicit precision and rounding, constant computation, and selected special functions.
- [Additional packages](packages/README.md): research implementations and their worked examples.
- [Experimental laboratories](experiments/README.md): computational models, protocols, and recorded results.

The [software guide](docs/LIBRARIES.md) links documentation and instructions for checking each package, including [Constructive Repair’s current Windows results and remaining release checks](docs/components/CONSTRUCTIVE_REPAIR.md). Each project in this collection has its own setup instructions and supported environment.

## Run a small example

With Python 3.10 or later, run this command from the collection root:

```text
python -B formal/research-preview-1/demo.py
```

The expected JSON reports `status: PASS` and `scalar_coefficient_comparisons: 96`: three polynomial-mask cases with 32 coefficients each. The example uses only the Python standard library. It compares two finite calculation routes. It does not run Lean or test the minimal-realization compiler. See [Research Preview 1](formal/research-preview-1/README.md) for its mathematical scope.

The [verification guide](docs/VERIFICATION.md) explains how to obtain a Git checkout, run the collection checks, reproduce component results, and interpret failures. The [collection workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/artifact-checks.yml) reports checks for individual commits.

## Read the mathematics with its evidence

Each development distinguishes written results, formal statements, exact calculations, and experiments. Conditional results retain their hypotheses. Paper XI's general arithmetic realization endpoint remains Conjecture 66. Physics and machine-model developments state their remaining construction and empirical obligations alongside completed mathematics.

The [formalization guide](formal/README.md) explains the Lean projects and the claims they cover. The [research index](research/README.md) connects further constructions, partial results, and open questions.

| Status field | What it tells you |
|---|---|
| Completion stage | Whether a specific manuscript, release contract, or prototype has reached its stated milestone. |
| Lean coverage | Which formal claims have recorded compiler evidence and which still need a current replay. |
| Confidence basis | The kind and scope of recorded review, proof, calculation, or experimental evidence. |

Lean is optional: a sound written argument can support a result without formalization. The [records guide](docs/RECORDS.md) collects dated reviews, claim coverage, test reports, and the source revisions they refer to. Entries awaiting sufficient implementation support are listed in the [incubator](docs/INCUBATOR.md).

A finished reading edition can contain open conjectures. A passing collection check verifies its stated integrity and tooling scope. Use the [status catalogue](docs/STATUS_CATALOG.md) for each component's exact evidence and the [finalization queue](docs/FINALIZATION_QUEUE.md) for remaining work.

## Repository map

| Location | Contents |
|---|---|
| [papers/](papers/README.md) | Core papers, current source editions, and retained earlier editions. |
| [monographs/](monographs/README.md) | Extended foundations, applications, and companion volumes. |
| [research/](research/README.md) | Further developments, partial results, and open programs. |
| [formal/](formal/README.md) | Formalization guides and the preserved research preview. Other Lean projects are kept with their components. |
| [packages/](packages/README.md) and [experiments/](experiments/README.md) | Research software, examples, protocols, and computational laboratories. |
| [docs/](docs/README.md) | Maintained reading, status, authorship, and verification guides. |
| [manifests/](manifests/README.md) and [verification/](verification/README.md) | Source inventories, status records, and dated verification evidence. |
| [tools/](tools/) | Collection maintenance and integrity checks. |

The [component index](docs/COMPONENT_INDEX.md) links selected source directories and their file records. Preserved packages can contain older publication or license wording. Consult the current [publication status](docs/PUBLICATION_STATUS.md) and collection terms alongside those records.

## Use and contribute

Read the [collection reuse terms](LICENSE.md), together with the license files and third-party notices in the relevant component. The current collection grant explains how to interpret retained historical licensing notices. Use the [citation guide](CITATION.md) to credit **Komorebi P.**, the specific work, and the source revision used.

The [contribution guide](CONTRIBUTING.md) explains how to report a correction and which records to update. Use the [issue templates](https://github.com/KomorebiP/Operation-KOMOREBI/issues/new/choose) for documentation or mathematical corrections, software problems, and source-record discrepancies. Include the exact component and source revision so the report can be checked.

Original source packages and dated evidence are preserved. Corrections to a sealed component need an identified revision and new evidence. Navigation pages are generated by `tools/update_source_navigation.py` and refreshed with `python -B tools/update_completion_status.py`. See the [maintenance instructions](docs/VERIFICATION.md#maintaining-reader-pages).

[Documentation](docs/README.md) · [Records guide](docs/RECORDS.md) · [Contribution index](CONTRIBUTIONS.md) · [Complete component index](docs/COMPONENT_INDEX.md) · [Source coverage](docs/SOURCE_COVERAGE.md) · [Publication status](docs/PUBLICATION_STATUS.md)
