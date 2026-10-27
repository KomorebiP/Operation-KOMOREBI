# Constructive Repair 1.0.0rc2 — final technical candidate

## Outcome

The component's mathematics and public wire schemas remain frozen. The new candidate fixes a reproduced locale-dependent Lean-export failure, strengthens runtime pin validation in the free-repair workflow, supplies offline installed-wheel acceptance, and fixes the tested support scope. The final public license choice remains with the author. No public upload or new rights grant was performed.

## Changes with direct regression evidence

The original exporter returned unresolved under the POSIX C locale because its implicit ASCII encoder could not write a Lean conjunction. Both the before and after logs are retained. UTF-8 is now explicit in 131 existing text-I/O/subprocess calls across 24 maintained files. The same export and a complete free-repair Lean workflow pass with UTF-8 mode disabled.

The free-repair script previously checked only the Lean version string. It now checks the exact commit and Mathlib pin, and verifies that the certificate source as well as the input source is unchanged after checking. Two new adversarial kit fixtures reject a wrong commit and a wrong Mathlib repository before compilation. They do not claim to authenticate an arbitrary hostile compiler binary.

The first new appendix was inserted after backmatter and inherited the previous appendix's section numbering. Rendered review exposed this. It was moved before backmatter and rebuilt. The final appendix is correctly numbered I. All first-pass logs remain labeled as development evidence.

## Fresh results

| Check | Result |
|---|---:|
| Unchanged Lean proof modules compiled and replayed | 51/51 |
| Audited named theorem dependency lists | 526/526 |
| Formal verifier commands and checks | 141 commands, 230 passing checks |
| Paired certificate rejection controls | 24/24 |
| Forbidden-axiom policy control | 1/1 |
| Public API, parser, CLI, portability and wrong-pin unit tests | 68/68 |
| Retained rational and menu unit tests | 134/134 |
| Original prototype unit tests and audit records | 20 tests, 3,307 records |
| Retained problems processed from the isolated installed wheel | 72/72 |
| Assertions in the installed-package probe | 369/369 |
| Platform workflow checks | 24/24 |
| Two clean local wheel builds | Byte-identical |
| Monograph build | 77 pages, clean references, no overfull boxes or missing characters |

The installed tests use a fresh venv, no SymPy, no source checkout on the import path, and no package index. They cover Unicode filenames/directories, spaces, console entry points, malformed data, preserved output directories, and unresolved work-budget exhaustion. A Python PASS is not a Lean claim.

The installed wheel produced the cost-five branch certificate, which the separate pinned Lean workflow accepted under a Unicode output path. The free-repair workflow also passed under the POSIX C locale with UTF-8 mode disabled. Their full command logs, axioms and input echoes are retained separately.

## Explicit limits and failed environment setup

Fresh support is limited to Linux x86_64 and CPython 3.13.5. Additional interpreter downloads failed DNS resolution. Windows/WSL, macOS, ARM, PyPy, and the other Python versions were not run. The offline acceptance script is supplied for obtaining actual receipts on those platforms, not as proof that they work.

The original 51 Lean modules are byte-for-byte unchanged from v0.5.0. No theorem count increased. Axiom dependencies stay within `propext`, `Classical.choice`, and `Quot.sound`. Replay is through the same Lean kernel against pinned dependencies, not an independent checker or a full rebuild of Mathlib.

The external JSON parser, emitter, and orchestration remain tested rather than fully formalized. Search can be exponential. The component is standalone. Main-library and Paper III integration are not claimed.

## Final-publication decision

The previous release record and the recalled licensing record do not identify an author-selected code or document license. No license has been invented. For this narrow technical scope, the remaining author decision is the code and document license selection. The chosen texts and resulting metadata will require a final artifact rebuild and integrity check before the public 1.0 tag.

The exact archive is checked after packaging. Its report is supplied beside the ZIP so the archive does not have to contain a report of its own final hash.
