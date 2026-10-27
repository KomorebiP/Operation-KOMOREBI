# Paper XII computation and reproduction audit

Audit date: 2026-10-06. The unmodified delivered checker code was replayed in disposable copies. Fresh bounded Python results pass. No fresh Lean compiler replay was performed in this environment.

## Claim and computational boundary

The mathematical paper concerns completed local/global quotient comparisons, patching support, finite Hecke packets, stable cores, and conditional companion/automorphic completion. The Python programs implement illustrative finite models, a few exact polynomial/matrix examples, and source-package checks. They do not implement a decision procedure for the complete mathematical paper.

A pass establishes execution and the stated finite assertions for the shipped code and recorded inputs. An assertion failure would require distinguishing a model/code problem from a counterexample to a theorem. A timeout, missing dependency, or resource cap would be an inconclusive run rather than a mathematical failure. No finite check discharges external representability, residual arithmetic occupancy, applicable patching, classicality, attached Galois representations, Frobenius density, or universal companion existence.

## Fresh results

| Check | Exact scope and result |
|---|---|
| Current complete archive | SHA256 sidecar matches; ZIP CRC passes; 788/788 extracted file hashes match; no duplicate paths; 44,153,678 uncompressed bytes |
| Current bundle checker | 786 manifest entries; 96 registered production modules and 96 object files; 113 local import references; 12 Python syntax checks; 18 manuscript and 14 appendix generated-figure references; 763 inherited archive members preserved |
| Original manuscript container | SHA256 matches its supplied original-archive sidecar; ZIP CRC passes; 48/48 extracted files match |
| Original manuscript manifest | 47/47 entries match; the manifest itself is outside its self-hash list |
| Current formal manifest | 659/659 entries match |
| Current inherited Lean record preservation | 96/96 source/object pairs and 196 build/axiom/control/consumer logs match their recorded hashes; cumulative and consumer report hashes form the expected chain |
| Original finite checker | 92,892/92,892 assertions pass in exactly 10 groups |
| Visual exact checker | 31/31 named illustrative assertions pass |
| Orthogonal primitive benchmark | All 3,123 two-by-two matrix ranks over F2, F3, F5, F7 agree with separate plain-Python forward elimination; 3,216 assertions including hand benchmarks pass |
| Native re-verification archive | SHA256 matches the recovered-source pin; ZIP CRC passes; 641/641 file hashes match; 640/640 manifest entries match |
| Native record preservation | 96 source/object pairs agree with the current formal tree; 196 logs match; all 1,229 production named axiom entries and three native contract entries parse consistently from the preserved logs |

The complete archive's 786-entry internal manifest excludes `BUNDLE_MANIFEST_SHA256.json` and its root `SHA256SUMS.txt`. Both exclusions are nevertheless authenticated by the complete archive's independent 788-member comparison. Archive-member counts are file counts, not theorem counts.

The complete archive SHA256 is `596006f0f85112a6e175f42278c15f9ee9fb15286d346eca5f49e08e0ab9a6a8`. The original manuscript archive SHA256 is `6923984146364eb47ce03083f13b7bd1274b0284945df4969c312079ca5cb9e3`. The separately recovered native archive SHA256 is `f1df76596c8046e52b230349fbf652d701fde7d0500b74380928517046797ae1`; this last expected pin is recorded from the recovered archive provenance, rather than presented as a user-uploaded `.sha256` sidecar.

## Original finite contract

| Group | Assertions | Bounds and interpretation |
|---|---:|---|
| Support and Fitting strata | 82,128 | Exhaustive support masks for n=1..9 and retained-coordinate subsets with `min(n,5)` variable bits; 120 sampled matrices for each 1..5 by 1..5 shape over F2, F3, F5, F7; thresholds r=1..n+1 |
| Finite adequacy certificate | 13 | One explicit two-dimensional S3 model over F7: relations, conjugation/projector/trace identities, invertibility of the averaging denominator |
| Auxiliary group algebras | 3,474 | All elements of F2[C2], F2[C4], F3[C3], F5[C5]; trivial idempotents and nilpotent augmentation generators; scalar rank/order bookkeeping for p in {2,3,5}, dimension/free rank 1..7 |
| Patching support and component boundaries | 1,796 | Six branch-label assertions, then full-support coordinate models for n=1..13 and at most eight varying retained-coordinate bits |
| Artin Hecke packets | 432 | Fields F5, F7, F11; both Jordan block sizes 1..4; eigenvalues 1 and 3; central orthogonal projectors and generalized eigenspaces |
| Finite carriers and stable cores | 1,102 | Scalar descending dimensions 1..29 with terminal 1..dimension; projection depth 2..39; finite-tail sizes 2..79 |
| R equals T transport | 2,200 | 200 deterministic sampled permutation/mask transports for each n=1..11 |
| Companion spines and finite separators | 1,699 | Vandermonde sizes 1..8, 100 sampled multiplicity vectors with entries 0..5 each; explicit positive scalar level models of depth 1..99 |
| Coefficient prime two | 4 | All four elements of F2[C2], square-zero augmentation element, and denominator bookkeeping |
| Source and package integrity | 44 | Labels/references/bibliography, proof-environment count, and 18 preserved figure existence/size checks in the historical manuscript |

Randomness is deterministic `random.Random(12012)` in the unchanged checker. The source generates the seed itself. Modular matrices use integer arithmetic; their small dimensions and bounded entries keep intermediate products safely below machine-integer overflow. The separator matrices use `dtype=object` and exact SymPy rational inversion. The sole use of `float(0.5)` is an exactly representable denominator illustration, not a numerical tolerance test.

Many assertion counts include definitions or bookkeeping: comparing a support set to its own constructed set/intersection, comparing the same augmentation sum to itself, `rank == rank`, a positive prime power, fixed branch names, and a rearranged rank/nullity inequality. These are not independent verification of geometric support or freeness theorems. The multiplicity-recovery check converts the exact rational result to integers before comparison; that check is weaker than comparing rationals directly, although the prescribed nonsingular integer Vandermonde system has an exact integer solution. We preserve the source and report that limitation. The 3,123 independent rank comparisons and identity/zero/Jordan benchmarks audit arithmetic primitives only.

## Visual exact contract

The 31 records include exhaustive 625-candidate F5 order-three local maps and 25-candidate order-two maps, a 21-monomial window of total degree below six, six compatible 5-adic digit prefixes, explicit Fitting ideals over QQ, stabilization of `diag(x,y)` by a unit summand, four rational fiber points, diagonal base change, an invertible coordinate change in characteristic different from two, a five-dimensional nonsemisimple CRT/Jordan model with packet dimensions two and three, an empty packet example, all four dyadic dual-number elements, exact involution/rank/trace examples, exact small stable-core projectors, and the three derived-fiber scalars 0, 1, -1.

The exact symbolic ideal comparisons use SymPy Groebner bases over QQ. They do not establish presentation independence in general or transfer automatically to characteristic two. Explicit projector and nilpotence identities explain structural features of the selected examples; bounded level lists alone do not prove an infinite intersection or inverse-limit theorem. The uniform arguments remain in the mathematical text, with their own hypotheses.

## Environment, caps, provenance and failures

The primary runs used Python 3.12.14, NumPy 2.3.5, SymPy 1.14.0 and mpmath 1.3.0 on Linux x86_64. SymPy/mpmath were already available under the prior task's local dependency directory and were supplied with explicit `PYTHONPATH`; no new installation was performed. External package versions are recorded, but this audit does not claim a hash-pinned binary closure of the Python installation.

The three primary runs each enforced a 300-second wall cap, 240 CPU seconds per process, 2 GiB address-space cap, one inherited CPU affinity core, and conventional numerical-library thread caps of one. Smaller auxiliary runs enforced 60 wall seconds, 30 CPU seconds and 1 GiB. Thread environment settings are cooperative; CPU-time caps are per process, not a total descendant budget. All runs completed without assertion failure, timeout, missing declared result or resource-limit failure. These limits did not truncate the implemented ranges.

Version 2 bounded-run manifests record argv, UTC time, run duration, exit code, enforced caps, source hashes before/after, and declared result/log hashes. They were validated with input freshness and output-hash checks. This archive is not a Git checkout; the manifests retain the absence of a repository commit instead of inventing one. The local runtime inventory and bytecode-cache incident are separately documented in `verification/lean/ENVIRONMENT_AUDIT.json` and `audit/computation/RECORDED_INCIDENTS.md`.

The incidental bytecode cache was removed, no supplied file bytes changed, a safe benchmark entry point prevents recurrence, and a final full integrity replay re-established the exact 788-file raw inventory. There is no mathematical counterexample in these outputs. Historical recorded failures/corrections remain part of the original formal and native source evidence.

## Lean evidence boundary

No `lean`, `lake` or `elan` executable was found in PATH or in the searched accessible roots `/workspace`, `/opt`, `/root`, `/usr/local`, `/usr/bin`, `/tmp`. The recorded `/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2` kit path is absent. The source bundle explicitly excludes that multi-gigabyte compiler/Mathlib environment. No download or compiler invocation was attempted.

The preserved September 12 evidence records 96 production modules, 1,229 named production declaration axiom audits, 748 own public named theorems, 81 reused Paper X theorems, three negative controls, and three core final consumers. The native archive records a second cumulative replay and three separately named manuscript consumers. These consumers are outside the production census and do not create six new manuscript claims. The revised internal-claim ledger is 49 complete, zero partial, zero unchecked; the original-wording ledger remains 41 complete, seven partial, one unchecked. Eight inherited amendments and external arithmetic assumptions remain explicit.

Fresh checksum/log checks authenticate preservation of those records. They do not turn inherited compiler evidence into an October 6 compiler certificate or independently authenticate the external arithmetic theorems. A future pinned Lean replay should rebuild the cumulative production tree, parse all named transitive axiom reports, reject all three negative controls, then compile both applicable consumer files against those same fresh objects. Use Linux/WSL, one Lean thread, warning-as-error, and a caller-enforced memory cap; the inherited verifier does not itself set `RLIMIT_AS`.
