# Independent libraries

Each flagship library has one canonical source destination. This central repository supplies navigation and a coordinated release manifest; it does not maintain another editable copy.

## Komorebi Math

Canonical private repository: [KomorebiP/komorebi-math](https://github.com/KomorebiP/komorebi-math).

The imported source checkpoint is **R4 Block 21 Certificate Consistency**, dated 24 September 2026, on the `1.0.0b4` line. The matched wheel has build tag `4b21`. Older documentation and test-profile names must be reconciled with this exact source.

The 5 October deep audit recorded finite-group certificate, prime-field arithmetic, and optimizer edge cases despite substantial passing tests. Repair and validation status belongs to the exact selected library revision. This central index grants no stronger implementation guarantee.

The 7 October preparation ran the original publication gate: 16 of 17 checks passed, while the complete source suite could not start because pytest was unavailable. Five exact-oracle producer probes completed 3,000 bounded cases with zero failures. The complete consistency probe was blocked by absent SymPy; strict documentation validation was skipped. These outcomes are separately retained. Existing source terms permit private evaluation and reserve redistribution rights.

## Polyphase Float

Canonical private repository: [KomorebiP/polyphase-float](https://github.com/KomorebiP/polyphase-float).

The imported source checkpoint is **0.18.0**, an arbitrary-precision binary floating-point C library using GMP. MPFR is used by optional interoperability, differential tests, and reference benchmarks.

Its existing source terms are **LGPL-3.0-or-later**. The 5 October audit recorded Bessel signed-zero parity and interval-factorial enclosure defects. Platform qualification and the exact state of any repairs remain component-specific.

## Remote binding

The three private destinations are populated. See [GitHub import status](GITHUB_IMPORT_STATUS.md) for actual remote commit bindings and fresh qualification outcomes. The preparation results above remain historical evidence for their stated revisions. No public release or visibility change is implied by a private source import.

[Return to the program](../README.md).
