# Prime-spectrum positive-enumeration upper construction

Base: checked Realization Boundaries v0.6.0, original archive SHA-256
`032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.

Production source: `RealizationBoundaries/SearchEnumerableSpectrum.lean`.
Source SHA-256:
`beb34f6a62c4c4a67d37ab1f3d8f3c05259e3f0defad80d1db6264133a236a92`.

## Exact semantics

`OracleSearchEnumeration X A` consists of a total natural candidate test proved
oracle computable in native `Nat.RecursiveIn` semantics and the exact law
`n in A iff exists t, test(pair n t)=0`. This is explicit positive-witness
semantics for enumeration. It does not decide negative membership and does not
pretend a noncomputable mathematical selector is a computation.

The separate `OracleEnumerable X A` definition in the parent computability
module uses the domain of a native relative partial function. This new module
proves witness-test semantics implies that native partial-domain semantics by
actual oracle minimization. It does not assume or yet prove the converse normal
form. The computability work package separately owns that missing generic
partial-graph-to-total-witness-test bridge.

## Actual construction

A raw code is a stage and an ordinary finite residue list indexed by natural
prime value. The stage mask admits a prime only after one of its genuine positive
enumeration witnesses has appeared. Bounded products compute discovery without
asking whether the prime will never appear.

Each name denotes an actual element of `spectrumSubgroup B` inside the actual
finite-support subgroup of the original unrestricted product. Surjectivity is
proved because the finitely many selected nonzero coordinates of any target
vector all acquire witnesses by some common finite stage. Addition raises the
stage to the maximum of the two input stages and adds their already discovered
coordinate values. A monotonic-discovery proof identifies the result with the
actual subgroup sum. Equality is a proved bounded residue comparison, with
literal equality of the actual vector meanings.

Native oracle computation proofs cover the stage loop, each masked cell, finite
residue output loops, addition, and equality. `spectrumDiscoveryRawCodes` thus
satisfies the complete computational raw-code contract. The frozen generic
canonical-code bridge then produces a bijective Nat-domain `OracleGroupCopy`
for every infinite selected direct sum. Finite groups use the separate genuine
finite-domain table convention, nonuniformly as the printed proof permits.

## Exact checked statements

* `spectrumDiscoveryValue_surjective`: every actual selected vector has a raw
  name obtained after a sufficiently large finite discovery stage.
* `spectrumDiscoveryValue_add`: exact actual subgroup addition, not only
  agreement on a quotient or a bounded prefix.
* `spectrumDiscoveryEqual_exact`: zero code equality test iff actual names equal.
* `spectrumDiscoveryRawCodes`: native oracle algorithms, exact operation/equality
  contracts, and surjective meaning map, all proved.
* `oracle_spectrum_copy_of_searchEnumeration`: actual infinite Nat-domain copy.
* `oracle_any_spectrum_copy_of_searchEnumeration`: finite and infinite domains.
* `spectrumSearchEnumeration_of_any_copy`: every actual copy gives the same
  explicit positive-witness enumeration semantics, including finite groups.
* `oracle_spectrum_copy_iff_searchEnumeration`: full actual-copy iff positive
  enumeration-witness contract, with both finite and infinite groups covered.
* `OracleSearchEnumeration.toOracleEnumerable`: native partial-domain implication.

This closes the mathematical c.e.-selector-to-copy construction under explicit
standard positive-search semantics. To claim literal equivalence to the
existing native partial-domain `OracleEnumerable` API, integrate and check the
separately owned converse normal-form theorem; it is not a hidden premise of
this source.

## Verification and provenance

`verification/development/SearchEnumerableSpectrum_006.json` records a clean
warning-as-error, autoImplicit-false compiler pass, exit zero, 3.49 seconds,
with the exact source hash above. The source is frozen for integrated checking.
The local kernel replay log is
`verification/development/SearchEnumerableSpectrum_kernel_replay.log`.
Development failures remain preserved separately and are not accepted evidence.

The same author developed and self-reviewed this source. A fresh-agent semantic
review and root's final immutable clean verification are separate obligations.

## Literal listing semantics closes the printed criterion

The separate `ListingSearchEquivalence.lean` source is frozen with SHA-256
`c27f0c8381c76167b369ce749ca2ecb6d82d6ca5452cdb2be4f841b6de68fc2c`.
Its final local warning-as-error compiler pass exited zero in 2.73 seconds.

`OracleStageListing X A` supplies an actual finite list of natural numbers at
every stage, a native oracle computation of that encoded list, and the exact
condition that n belongs to A iff it appears in some emitted list. Duplicates
are harmless. Positive witness tests produce such a listing by examining all
flattened candidate/witness pairs below each stage, emitting the successful
candidate indices, and removing explicit blank entries. Each witness appears
at a finite stage. The reverse conversion uses actual finite-list membership as
an oracle-computable candidate test.

Consequently `oracle_searchEnumeration_iff_stageListing` proves equivalence of
explicit positive-search and literal listing semantics, and
`oracle_spectrum_copy_iff_stageListing` proves exactly the printed 3.3 criterion:
an actual finite or infinite X-computable copy of D_B exists iff its prime
indices can be listed by an actual X-computable stage procedure.

The optional generic native partial-domain normalization API is therefore not a
missing hypothesis of the printed criterion. It remains a separately identified
additional API theorem until the other work package completes it. No native
domain normalization has been assumed or silently inserted.

## Native recursion trace helper

`OraclePartialRecursionTraces.lean`, hash
`172328b148f24cca56ba2f2fc51925aa489336e715b3f3a0957a5cb8fc20ac83`,
is a disjoint pure semantic helper requested by the optional native-normal-form
work package. It identifies membership in the literal native partial primitive
recursor with a finite trace of terminating initial and step evaluations. The
proof is induction with a single update at the final trace index; no computable
trace-selection claim is made. Its local warning-as-error compiler check passed,
exit zero, 2.45 seconds. It is frozen and can be imported independently.

Kernel replay of each frozen new source exited zero:
`SearchEnumerableSpectrum_kernel_replay.log`,
`ListingSearchEquivalence_kernel_replay.log`, and
`OraclePartialRecursionTraces_kernel_replay.log`, under development evidence.
