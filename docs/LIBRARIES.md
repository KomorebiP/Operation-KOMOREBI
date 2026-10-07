# Independent libraries

Each flagship library has one canonical source destination. This central repository supplies navigation and a coordinated release manifest; it does not maintain another editable copy.

## Komorebi Math

Planned destination: [KomorebiP/komorebi-math](https://github.com/KomorebiP/komorebi-math).

The separately staged source candidate is **R4 Block 21 Certificate Consistency**, dated 24 September 2026, on the `1.0.0b4` line. The matched wheel has build tag `4b21`. Older documentation and test-profile names must be reconciled with this exact source.

The 5 October deep audit recorded finite-group certificate, prime-field arithmetic, and optimizer edge cases despite substantial passing tests. Repair and validation status belongs to the exact selected library revision. This central index grants no stronger implementation guarantee.

The 7 October preparation ran the original publication gate: 16 of 17 checks passed, while the complete source suite could not start because pytest was unavailable. Five exact-oracle producer probes completed 3,000 bounded cases with zero failures. The complete consistency probe was blocked by absent SymPy; strict documentation validation was skipped. These outcomes are separately retained. Existing source terms permit private evaluation and reserve redistribution rights.

## Polyphase Float

Planned destination: [KomorebiP/polyphase-float](https://github.com/KomorebiP/polyphase-float).

The separately staged candidate is **0.18.0**, an arbitrary-precision binary floating-point C library using GMP. MPFR is used by optional interoperability, differential tests, and reference benchmarks.

Its existing source terms are **LGPL-3.0-or-later**. The 5 October audit recorded Bessel signed-zero parity and interval-factorial enclosure defects. Platform qualification and the exact state of any repairs remain component-specific.

## Remote binding

These URLs are intended destinations whose availability has not been confirmed for this candidate. Commit IDs, tags, asset URLs, and release links will be recorded after the corresponding remote objects exist. No placeholder hash is a commit binding.

[Return to the program](../README.md).
