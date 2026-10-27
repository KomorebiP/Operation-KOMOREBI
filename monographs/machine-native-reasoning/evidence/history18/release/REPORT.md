# Machine-Native Reasoning — Core 2.5 Lean verification

**PASS · Selected-core correspondence 26/27 · Formal companion 0.18.0**

Author: Komorebi P. Date: 23 October 2026.

## Mathematical outcome

Core 2.5, *When complete packets are genuine probability components*, is now
formally mapped in both of its sectors. The original reviewed statement, setup,
proof and all five source-book files are unchanged.

For any real vector space, actual convex cone, strictly positive linear mass and
finite complete cone-preserving family, Lean proves nonnegative packet weights,
total weight one for a normalized input, zero weight exactly for zero packets,
unit-mass cone membership of every normalized positive packet, and exact mixture
reconstruction. Normalization takes a positive-index argument; a zero-mass packet
is not silently assigned an arbitrary normalized state. Idempotence and finite
dimension are not assumptions of this general mixture theorem.

For actual linear maps on the finite nonnegative coordinate cone, the new
classification derives diagonal form from positivity and completeness. Idempotence
then forces zero-or-one diagonal entries and exactly one owner per coordinate.
The original maps are represented by the constructed coordinate selectors.
Pairwise zero compositions are derived. The converse proves that selector families
satisfy all these input conditions. Zero coordinate dimension, empty indices and
zero operators are handled without accidental nonemptiness assumptions.

The supporting transport development pushes the cone forward, pulls the mass back
and conjugates the operators through a linear equivalence. It preserves weights
and normalized components. A real shear gives valid signed coordinates in the
transported cone. That example is distinguished from an ordinary Haar detail,
which has zero sum but is nonzero and lies outside the original positive cone.

Principal source-facing declarations:

```lean
Komorebi.MachineTheory.PositivePackets.source_core25
Komorebi.MachineTheory.PositivePackets.Coordinate.source_core25_coordinate
```

The separate `sum_positive_weights_one`, `classification_iff` and
`Transport.source_coordinate_change` endpoints record the active-weight identity,
classification converse and coordinate-covariance result. A direct raw-hypothesis
API checks both manuscript sectors, rather than assuming a mixture certificate or
diagonal representation as input.

## Complete current-source verification

Both complete gates terminated successfully, with successful supervisors. Each
started with an empty local proof-object directory. The second source tree was
separately extracted from the authenticated frozen source ZIP without project
objects. The runs were sequential and shared only the pinned external dependency
cache. Every required command passed and no command timed out.

| Check | Actual result |
|---|---:|
| Production modules in each cold build | 76 |
| Substantive same-kernel replays in each run | 75 |
| Declarations in each transitive axiom audit | 2,905 |
| Elaborated theorem constants, including generated auxiliaries | 2,286 |
| Expected control outcomes per run | 181 |
| Unchanged proof-gate inputs per run | 482 |
| Matched upstream artifacts per run | 13,440 |
| Preserved inherited substantive/source-book files | 76 |
| Production objects identical across the builds | 76 |
| Rebuild comparisons passed | 634 |

The actual transitive axiom union is `Classical.choice`, `Quot.sound`, `propext`.
Production code contains no proof placeholder, added trusted axiom, native-decision
shortcut, or unsafe/external implementation hook. The audit covers all authored
declarations and all theorem constants in the actual compiled project namespace,
including generated auxiliaries.

The four new modules contain **102 authored
declarations**, including **73 supporting theorem
declarations**. Cumulative authored counts are 1841
declarations and 1222 theorems. These are proof-code
inventories, not counts of independent discoveries or manuscript statements.

All 71 inherited substantive modules and five original source-book files retain
their exact bytes. All 170 inherited control contracts and fixture files are also
unchanged. Eleven new controls test the missing hypotheses and edge conditions.
The full suite has 180 invalid or unfinished fixtures rejected for their specified
proof diagnostics and one explicit added-axiom fixture rejected by the separate
axiom policy after compilation. Missing imports, unknown identifiers, parse errors
and timeouts never count as mathematical rejection evidence.

Nonproduction helper differences: **Audit.olean**.
Every production object matches byte for byte. Complete axiom records and generated
audit source match. A helper binary difference is not a production-identity success
and its cause is not inferred.

## Exact rational regression

The separate standard-library checker exhausts **28,645**
complete matrix families in declared rational grids. It identifies
**72** positive families and
**21** selector families, checking actual matrix
idempotence, diagonal action, unique ownership and pairwise composition.

It checks **7,056** normalized input/mass
contracts and observes **2,992** zero packet
weights. It additionally checks **5,760**
exact shear-transported mixture contracts, including
**2,608** normalized component
occurrences with negative coordinates but valid transported-cone membership.
Eight further exact boundary checks distinguish the failed hypotheses.

Arithmetic uses integers and `Fraction` only, with no random sampling, tolerance,
training or empirical timing claim. These domains overlap and are not summed as
independent results. Both complete gates reproduce the same finite record. This is
a same-project reference checker, not a universal proof of Python correctness or
an independent external implementation. The arbitrary-real-space Lean result is
separate from these finite regression checks.

## Recovery and reproducibility

The intact predecessor archive has 62,071,022 bytes and SHA-256
`406c4b0f63e129025abb313f437c96ce25295add96afec31c58fae3832d804d3`.
All 2,176 manifest-covered files passed exact-set, byte-length and hash checks.
No new archive-recovery gap occurred. The earlier missing Core 8.3 historical
payload remains documented in predecessor history and is not relabeled recovered.

The exact offline runtime was reconstructed from the five saved Library parts.
The combined 2,220,147,424-byte archive matches SHA-256
`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`,
and extraction completed for 166,035 members. The compiler is Lean 4.34.0-rc2,
commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine repositories and actually
imported cache artifacts are checked. Cache hashes are not independent origin
attestation and the upstream sources were not rebuilt.

Compiler invocations use one worker, a 4,096 MiB internal limit and warnings as
errors. Every gate subprocess has the unchanged 45-second wall allowance. Each
supervisor allows 1,800 seconds. The host has a shared 4 GiB cgroup ceiling, not an
additional separately imposed per-command OS cap. Replays use Lean's own kernel,
not a second independent implementation. Native Windows execution is not claimed.
Actual gate durations in the receipts are execution records, not benchmarks.

## Failed attempts and corrections

There were **22** recorded development Lean invocations:
**14 succeeded and 8 failed** before the accepted gates.
Their exact attempted source snapshots and diagnostics are retained. Corrections
addressed a deprecated real import and tactic names, strict linter diagnostics,
function extensionality on linear maps, placement of scoped `omit` declarations,
and explicit arithmetic for the real shear. The first raw API check also exposed
a finite-subtype instance mismatch. Using the same canonical subtype enumeration
made the external source statement and the general endpoint agree without changing
any mathematical premise or conclusion. No production proof was weakened.

Runtime title search initially returned no result and a named Library-path probe
failed. Size-based listing located all five parts. Container streaming launch was
unavailable before execution, and its uncreated directory caused an initial direct
launch failure. The directory was created explicitly and tracked restoration then
passed. These are tool/recovery failures, not mathematical evidence.

An administrative history-copy command initially expected a predecessor Markdown
map that was not shipped. The copy was restricted to actually present historical
files. A later metadata recheck correctly rejected a Python bytecode cache created
by importing the verifier. Only that newly generated cache was removed, bytecode
creation was disabled, and the full exact-set recheck passed. The archive and its
scientific payload were unchanged. The retained delivery tools passed all 28 small
fixtures in a fresh run. Those tests concern delivery mechanics, not proof truth.

## Remaining task and delivery boundary

The only remaining selected-core result is **Core 3.2**, the partition occupancy
classification, exact 2^r signature count and fixed-binary r-bit lower/upper bound.
`release/NEXT_CORE32_SPEC.md` gives the precise source anchor and restart contract.
Neither the theorem count nor the book's scope should be enlarged by merely
configuring an endpoint before its acceptance runs.

The monograph PDF is unchanged. A formal-status insertion is supplied for its next
build. The Large Signal Model's separate 39/87 inventory is unchanged. No learned
encoder, physical sensor semantics, deployed decision system, computational
complexity guarantee, hosted publication, independent review or full-book
formalization is established by this result.

The delivery manifest and external verification receipt separately authenticate
the supplied ZIPs, exact file sets and source inputs. No runtime or standalone font
binaries are distributed. See the archive-layout record for full versus compact
contents and the distinction between current and historical execution evidence.
