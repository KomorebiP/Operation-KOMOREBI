# Constructive Repair 1.0.0rc1 — release report

## Result

The exact rational repair component now has an installable Python package and a feature-frozen candidate contract. The Lean mathematics is unchanged and freshly rebuilt, audited and replayed. This is a release-engineering advance, not an increased theorem count.

The candidate includes the complete 74-page monograph, standalone LaTeX, source code, exact examples, all prior release archives, a pure-Python wheel, test logs, source manifests and a versioned ledger.

## Fresh results

| Gate | Result |
|---|---:|
| Unchanged proof modules compiled and replayed | 51/51 |
| Named theorem dependency lists covered | 526/526 |
| Full formal verifier | 141 commands, 230 passed checks |
| Paired corrupted-certificate controls | 24/24 |
| Separate forbidden-axiom policy control | 1/1 |
| New public API/parser/CLI tests | 56/56 |
| Existing rational/menu Python tests | 134/134 |
| Original Python tests | 20/20 |
| Original audit records rerun | 3,307 |
| Existing exported pairs through the API | 72/72 |
| New invertible-coordinate comparison pairs | 128/128 |
| New free and menu certificate checks | 512/512 |
| Independent subset rank comparisons | 1,348/1,348 |
| Clean offline wheel installation | PASS |
| Installed-wheel certificate checked by Lean | PASS |
| Two clean local wheel rebuilds | Byte-identical |
| LaTeX preflight and 74-page visual review | PASS |

The original 51 modules are verified byte-for-byte against the inherited v0.5.0 ZIP. The accepted axiom sets are contained in `{propext, Classical.choice, Quot.sound}`. Replay uses the same Lean kernel against the pinned imports; it is not a second independent proof checker.

## Interface corrections

The release audit fixed ignored explicit matrix widths, boolean indices treated as integers, and mutable nested storage accepted by the direct constructor. Those were external API integrity defects, not failures of the checked repair theorems.

The file reader now limits actual bytes, JSON structural depth, integer-token length and rational-wire length. The first depth test revealed that interpreter recursion settings alone were insufficient. Its failed log and the corrected test run are retained. Oversized outputs and failed checks remain unresolved, never mathematical impossibility.

## Installation and status discipline

The wheel needs no third-party runtime dependency. The clean test environment has no SymPy and imports the package from its installed site-packages directory, not from the source checkout. SymPy is only the optional independent audit oracle.

The installed CLI reports Python certificate validity. The source-archive commands separately compile the literal input and certificate, audit assumptions, replay the imported proof modules and check the original-input echo. A successful Python check is never labelled kernel acceptance.

## Residual gates

The final 1.0 tag awaits the author's public licensing decision and the final declared platform/version support matrix, plus acceptance of the exact frozen artifact. Here, execution covers Linux x86_64 with CPython 3.13.5 and the pinned Lean kit. A pure-Python portability tag does not mean Windows/WSL or all Python 3.10+ combinations have been tested.

The package is standalone. Integration into the main Komorebi library and the authoritative Paper III tree is not claimed. The JSON parser/emitter and orchestration are tested but not fully formalized. No new unrestricted integral, nonlinear or native arithmetic realization result is claimed.
