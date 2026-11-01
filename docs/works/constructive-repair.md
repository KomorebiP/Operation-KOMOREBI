# Constructive Repair

[Browse hub](../BROWSE.md) / [Software packages](../browse/PACKAGES.md)

<a id="work-navigation"></a>

[Read](#read) · [Written proofs](#written-proofs) · [Lean](#lean) · [Code](#code) · [Evidence](#evidence) · [Worked examples](#worked-examples-for-this-work)

**Completion:** Scoped release · **Lean:** Selected results recorded · **Confidence:** Recorded formal evidence

Constructive repairs, examples, and the accompanying reference implementation.

## Before you start

**Suggested background:** Basic command-line use and the package's programming language. Check its platform requirements before installation.

**Recorded results and limits:** Qualified beta distribution of the 1.0.0rc3 Python runtime. Linux x86_64 and Windows Server 2025 x86_64, both with CPython 3.13.5, passed 134 engine tests and 72 installed cases. Linux passed all 100 release tests; Windows passed 97 with the three named POSIX-only skips. Both symlink rejection controls passed on both platforms. The identical wheel's seven runtime files match the 2,254-file imported source. Historical Lean evidence retains its own scope; this qualification performs no new kernel replay.

**Remaining work:** Use the qualified beta and its exact source/wheel/receipt record. Rerun the qualification workflow for future candidates. Other interpreters, operating systems, architectures, integration adapters, and fresh Lean execution require their own evidence.

The background advice is an editorial starting point. The work itself states its prerequisites and hypotheses.

[Reading routes](../READING_ROUTES.md) · [Glossary](../GLOSSARY.md) · [Claim links](../CLAIM_LINKS.md#constructive-repair) · [Download this work](../DOWNLOADS.md#constructive-repair)

### Worked examples for this work

These introductory calculations lead into this work’s subject. The source and evidence links below retain the work’s recorded scope.

- [25. Choose repair directions from a finite menu](../examples/25_REPAIR_MENUS.md) · [Terms and source routes](../LEARNING_MAP.md#repair-menus)

Use the links below to read this work and its supporting files. Ctrl+click (Command+click on macOS) opens a link in another tab. Your browser’s Back button returns here.

## Read

- [Edition README](../../packages/constructive-repair/README.md)
- [Read PDF](../../packages/constructive-repair/monograph/Constructive_Repair.pdf)
- [Maintained edition guide](../components/CONSTRUCTIVE_REPAIR.md)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Written proofs

Find the statement number or section in the [reading files](#read), then read its assumptions and argument. A claim map may cover only part of the written result.

- [Manuscript text (TeX)](../../packages/constructive-repair/monograph/Constructive_Repair.tex)

[Find this work among other written proofs](../browse/PROOFS.md#constructive-repair)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Lean

Start with the [maintained edition guide](../components/CONSTRUCTIVE_REPAIR.md) and the build instructions below. Check the correspondence records to see which written claims the Lean declarations cover. Source links lead to `.lean` files. PDF guides explain the formalization.

- [Lean sources (directory)](../../packages/constructive-repair/lean/)

[Find this work among other Lean projects](../browse/LEAN.md#constructive-repair)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Code

These links include code, examples, checks, or build tools. Read the [maintained edition guide](../components/CONSTRUCTIVE_REPAIR.md) for setup instructions and what each command does. All software is beta and work in progress.

- [Code / scripts: python/komorebi_repair](../../packages/constructive-repair/python/komorebi_repair/)
- [Code / scripts: tests](../../packages/constructive-repair/tests/)

[Find this work among other code projects](../browse/CODE.md#constructive-repair)

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Evidence

- [Completion, Lean coverage, confidence, and cited evidence](../STATUS_CATALOG.md#constructive-repair)
- [Recorded software checks](../../verification/constructive-repair/qualified-2026-10-30/summary.json)
- [Source-file receipt (identity and availability)](../../manifests/source-imports/constructive-repair.json)
- [All files in this source edition](../../packages/constructive-repair/)

The evidence records describe the reviews and runs completed for this edition.

[Back to work navigation](#work-navigation) · [Worked examples](#worked-examples-for-this-work)

## Continue browsing

- [Previous: Certified Inference](certified-inference.md)
- [Next: RRCT](packages-rrct.md)
- [Back to Software packages](../browse/PACKAGES.md#contents)
- [All collections](../BROWSE.md)
