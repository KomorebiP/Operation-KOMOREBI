# Independent libraries

**Both libraries are beta releases and works in progress.** They are publicly available for use, inspection, and feedback under their respective licenses. Their current version numbers do not imply completion or a stable release designation.

Each library has one canonical source repository. This central collection supplies navigation and publication records without maintaining a second editable copy.

## Komorebi Math

Canonical public repository: [KomorebiP/komorebi-math](https://github.com/KomorebiP/komorebi-math). Download the [beta prerelease](https://github.com/KomorebiP/komorebi-math/releases/tag/beta-2026-10-27).

Komorebi Math is the Python library for finite operator, coordinate, signal, and arithmetic calculations. The current package metadata uses version **1.0.0**. Its distribution status remains **beta / work in progress**. The `stable` and `v1` namespaces are technical API names.

Start with the [README](https://github.com/KomorebiP/komorebi-math#readme), [user guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md), and [worked examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/WORKED_EXAMPLES.md). Original software and documentation use the [MIT License](https://github.com/KomorebiP/komorebi-math/blob/main/LICENSE.md). Third-party material retains its notices.

The source revision inspected for the start of public publication was [5f2b7dd](https://github.com/KomorebiP/komorebi-math/commit/5f2b7ddc879c12d2bb00cbe5c487aa0bc7709222). Later publication-label changes have their own commits. The [release guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/RELEASE_PROCESS.md) and [Actions runs](https://github.com/KomorebiP/komorebi-math/actions) record qualification procedures and execution outcomes.

## Polyphase Float

Canonical public repository: [KomorebiP/polyphase-float](https://github.com/KomorebiP/polyphase-float). Download the [beta prerelease](https://github.com/KomorebiP/polyphase-float/releases/tag/beta-2026-10-27).

Polyphase Float is a C11 library for arbitrary-precision binary floating-point arithmetic built on GMP. The current source uses version **0.20.0** and remains a **beta / work in progress** candidate. MPFR supports optional interoperability, differential tests, and reference benchmarks.

Start with the [README](https://github.com/KomorebiP/polyphase-float#readme) and [User Guide and Reference](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/README.md). The source uses [LGPL-3.0-or-later](https://github.com/KomorebiP/polyphase-float/blob/main/LICENSE.md).

The source revision inspected for the start of public publication was [0b551118](https://github.com/KomorebiP/polyphase-float/commit/0b551118e9664b4aff174b74ebe1579357995fa9). The [readiness record](https://github.com/KomorebiP/polyphase-float/blob/main/docs/ONE_POINT_ZERO_READINESS.md) identifies remaining promotion requirements. [Claims and evidence](https://github.com/KomorebiP/polyphase-float/blob/main/docs/CLAIMS_AND_EVIDENCE.md) and [qualification](https://github.com/KomorebiP/polyphase-float/blob/main/docs/QUALIFICATION.md) define the numerical and platform evidence boundaries.

## Evidence and earlier checkpoints

The [7 October import report](GITHUB_IMPORT_STATUS.md) preserves the older R4 Block 21 Python and 0.18.0 C checkpoints, repairs, and qualification results. Those records describe their named revisions. They do not establish the results of later source changes.

At the initial 27 October publication check, the latest inspected hosted Math qualification and Polyphase fuzz runs had failed before any job steps executed. These runs supply no fresh test results. Current execution outcomes are available from each repository's Actions page.

Public availability does not change the beta status or the limits stated by an individual numerical routine or certificate.

[Return to the program](../README.md).

