# Realization Calculus

**Komorebi P.**

Realization Calculus is a mathematical and computational research program concerned with transformations, compatibility, residuals, obstructions, and realization: what structure survives a change of representation, what prevents a proposed construction, and what evidence establishes that the construction works?

Packets retain selected components of a resolved object. Transfer blocks describe how maps act between those components. Exact reconstruction, refinement, and named residuals connect the work across arithmetic, algebra, signal processing, numerical computation, and experiments in machine reasoning.

Start with the [collected volume and publication package](https://github.com/KomorebiP/Operation-KOMOREBI/releases/download/papers-2026-10-25/Realization_Calculus_Publication_Package.zip), browse the [twelve core papers](papers/README.md), or open the [public release collection](https://github.com/KomorebiP/Operation-KOMOREBI/releases/tag/papers-2026-10-25). The [publication status](docs/PUBLICATION_STATUS.md) records the available editions and remaining uploads.

## Choose an entrance

| Entrance | Available material |
|---|---|
| [Collected Realization Calculus volume](https://github.com/KomorebiP/Operation-KOMOREBI/releases/download/papers-2026-10-25/Realization_Calculus_Publication_Package.zip) | Downloadable publication package for the core collection. |
| [Papers and companion editions](papers/README.md) | Public archives for Papers I–XII and further monographs. Earlier source imports remain browsable in this repository. |
| [Komorebi Space and Realization Boundaries](https://github.com/KomorebiP/Operation-KOMOREBI/releases/download/papers-2026-10-25/Realization_Calculus_Twin_Volumes_GitHub_Ready.zip) | The twin-volume package. |
| [Large Signal Model](https://github.com/KomorebiP/Operation-KOMOREBI/releases/download/papers-2026-10-25/Large_Signal_Model_Final_GitHub_Release_1.0.0.zip) | The published model research package and its recorded evidence. |
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | **Beta / work in progress.** Public Python library, MIT license. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | **Beta / work in progress.** Public C library, LGPL-3.0-or-later. |
| [Formalizations](formal/README.md) | Research Preview 1 and navigation to separate formal environments. |
| [Experiments](experiments/README.md) | Scientific and computational studies with their recorded controls and limits. |
| [Additional software](packages/README.md) | Numerical engines and research instruments, including AM-SPD. |

Both flagship libraries are beta releases and remain works in progress. Their current version numbers and technical stable-API names do not change that release status. See the [library guide](docs/LIBRARIES.md) for installation, documentation, and qualification links.

[START_HERE](docs/START_HERE.md) supplies a guided reading route. The [contribution index](CONTRIBUTIONS.md) preserves the source-import ledger and historical register. Use the publication status for the current downloadable collection.

## A concrete starting point

[Research Preview 1](formal/research-preview-1/README.md) develops prime-power Cartier systems. It constructs finite coefficient machines and proves a minimum-cardinality reachable-observable linear realization under explicit hypotheses. Its preserved source, mathematical note, claim map, small Python examples, and recorded proof replay are imported here.

From that component directory:

```bash
python -B demo.py
python -B tools/check_release.py
```

These commands run a finite reference computation and artifact checks. The separate [proof reproduction instructions](formal/research-preview-1/REPRODUCE.md) identify its pinned Lean environment.

## Publication and evidence

All three canonical repositories are public: [Operation-KOMOREBI](https://github.com/KomorebiP/Operation-KOMOREBI), [komorebi-math](https://github.com/KomorebiP/komorebi-math), and [polyphase-float](https://github.com/KomorebiP/polyphase-float).

The latest core-paper editions are distributed as release assets. Earlier Papers I–IV and K-COS source trees remain browsable here. A release archive and a source-tree import are separate records. Download the named assets on the release page for the published editions.

Written arguments, formal coverage, finite computations, and open obligations retain their stated scope. Publication does not constitute a new Lean replay or close a conjecture. Paper XI retains Conjecture 66 obligations. The historical register is an inclusion baseline, not a current theorem census.

[Distribution status](docs/DISTRIBUTION_STATUS.md) records component terms. Licenses and third-party notices remain attached to their respective packages. [GitHub import status](docs/GITHUB_IMPORT_STATUS.md) preserves the earlier import and qualification evidence.

