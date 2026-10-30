# Realization Calculus and Komorebi Space

**Komorebi P. · Work in progress**

Komorebi studies how mathematical objects can be represented in parts, transformed through those parts, and reconstructed. It asks what a change of representation preserves, what it loses, and how the difference can be measured.

Realization Calculus develops the mathematics of decomposition, transfer, refinement, and reconstruction. Komorebi Space provides a setting for comparing realizations and the conditions under which they are compatible.

[Open the reading website](https://KomorebiP.github.io/Operation-KOMOREBI/).

## Start here

| What would you like to do? | Begin here |
|---|---|
| Understand the ideas | [Read the introduction](docs/START_HERE.md), then explore the [complete demonstrations](docs/DEMONSTRATIONS.md). |
| Read the mathematics | [Browse the works](docs/BROWSE.md), with links to papers, monographs, source files, and evidence. |
| Use the software | [Install a library and run a first example](docs/FIRST_RUN.md), or explore the [software guide](docs/LIBRARIES.md). |

> **Author’s note:** This work is still in progress. Much of it has been rushed because of circumstances introduced by OpenAI. I am continuing to correct, verify, and organize it.

The [public project and authorship statement](docs/PROJECT_STATEMENT.md) explains the pseudonym, AI assistance, and publication circumstances. Each work is at a different stage of completion and review. All executable software remains **beta and work in progress**.

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

The [software guide](docs/LIBRARIES.md) links documentation and instructions for checking each package, including [Constructive Repair’s qualified beta and platform results](docs/components/CONSTRUCTIVE_REPAIR.md). Each project in this collection has its own setup instructions and supported environment.

<a id="run-a-small-example"></a>

## Research preview: Euler numbers

Read [Euler numbers through packets, polynomials, and residuals](https://komorebip.github.io/Operation-KOMOREBI/collection/demonstrations/EULER_PACKETS.html). The extended derivation follows Euler numbers through reciprocal series, polynomial coordinates, exact transfer matrices, and residual correction. It includes hand calculations, failure controls, source references, and downloadable results.

From a collection checkout, run the exact checker with Python 3.10 or later:

```text
python -B examples/euler_packets.py
```

The checker uses Python's standard library. A successful run ends with `PASS: Euler packets, polynomials and residuals`. The example records the tested ranges and provides a [standalone checker](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/euler_packets.py) and a [source and results bundle](https://komorebip.github.io/Operation-KOMOREBI/downloads/euler-packets/source-and-checks.zip).

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

## Find a specific resource

[Reading routes](docs/READING_ROUTES.md) · [Project map](docs/PROJECT_MAP.md) · [Glossary](docs/GLOSSARY.md) · [Completion and confidence](docs/COMPLETION_STATUS.md)

[Hand-worked examples](docs/HAND_WORKED_EXAMPLES.md) · [Papers](docs/browse/PAPERS.md) · [Written proofs](docs/browse/PROOFS.md) · [Lean sources](docs/browse/LEAN.md) · [Code](docs/browse/CODE.md) · [Downloads](docs/DOWNLOADS.md)

[Accessibility and reading options](docs/ACCESSIBILITY.md) · [Report an accessibility or reading problem](https://github.com/KomorebiP/Operation-KOMOREBI/issues/new?template=04-accessibility.md)

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
