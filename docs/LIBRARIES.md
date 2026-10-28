# Software guide

**All Komorebi software is beta and work in progress.** Version numbers and earlier release names identify revisions. The current public software status is beta.

| Library | Documentation | Current terms |
|---|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | [User guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md), [worked examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/WORKED_EXAMPLES.md), [public API](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md), and [platform requirements](https://github.com/KomorebiP/komorebi-math/blob/main/docs/SUPPORTED_PLATFORMS.md) | MIT for the current library. Retain third-party notices. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | [User guide](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/README.md), [build instructions](https://github.com/KomorebiP/polyphase-float/blob/main/docs/BUILDING.md), [semantic reference](https://github.com/KomorebiP/polyphase-float/blob/main/docs/PUBLIC_SEMANTIC_CONTRACT_0.20.0.md), and [testing](https://github.com/KomorebiP/polyphase-float/blob/main/docs/TESTING.md) | LGPL-3.0-or-later. Retain third-party notices. |

The [package index](../packages/README.md) covers software in this collection. The [experimental laboratories](../experiments/README.md) and [research programs](../research/README.md) contain further implementations and protocols.

The documentation links above follow each library's `main` branch. For a reproducible setup, use the exact commit and run links in the [software qualification record](GITHUB_IMPORT_STATUS.md#software-qualification-records). The [tagged beta releases](PUBLICATION_STATUS.md#release-assets) are earlier source snapshots and do not include every later fix.

Use the [code and script finder](browse/CODE.md) for direct file links across the collection, or the [browse hub](BROWSE.md) to move between a work's manuscript, formal sources, and evidence.

The [collection verification guide](VERIFICATION.md) provides Git checkout instructions, a small standard-library example, and commands for source and navigation checks. For a concrete package record, see [Constructive Repair](components/CONSTRUCTIVE_REPAIR.md): its engine and installed cases passed on the recorded Windows environment, while full release qualification remains incomplete.

The [corrected SRIC 0.3.3 source runtime](../packages/sric-admission-v0.3.3/README.md) has passed the recorded admission and CLI checks. It remains beta, with execution on a real model still pending.

## Reproduce a result

1. Select a source revision and read its supported platform and dependency requirements.
2. Run the documented small example before a larger calculation.
3. Run the component's documented checks and compare the results with the expected output and tested scope.
4. Record the source revision, inputs, platform, dependencies, arithmetic settings, and output.

A passing test applies to the exercised behavior. A finite computation, numerical approximation, formal theorem, and software qualification record provide different kinds of evidence. Read each result with its assumptions.

[Recorded publication and qualification status](GITHUB_IMPORT_STATUS.md) · [Reading guide](START_HERE.md)
