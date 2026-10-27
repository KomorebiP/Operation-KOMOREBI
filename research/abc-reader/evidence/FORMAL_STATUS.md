# ABC formal evidence

**Final report, 8 October 2026.** KTG passed its exact-version replay. The
original ABCJet module built with two retained style warnings. Its explicitly
patched copy passed direct elaboration with warnings treated as errors.

## Normalized claim and verdict

The KTG claim is a typed, conditional theorem: for abstract data `D`, certificate
semantics `S`, normalization data `N`, a supplied `SourceWitnessTheorem D S N`,
a certified realization, a normalization witness, and a monotone observable,
the q-pilot observable is bounded by the observable of the output hull.
The formal implication is proved as written. An application to the actual IUT
objects is incomplete. The smallest unsupplied theorem is
`KTG.IUT312.StepXiEWitnessPreservation` for an actual IUT instantiation.

This is a source-shaped abstract interface. Its named fields and source map do
not themselves authenticate their interpretation as the objects and theorems
of IUT. The finite Boolean countermodel establishes independence inside this
interface. It is not a counterexample to IUT III Corollary 3.12 or to ABC.

## Recovered inputs and distinct histories

| Input | Source pin | Historical status | Fresh status |
|---|---|---|---|
| Original ABC Jet Determinant Block 01 | Lean and mathlib v4.19.0 | Seven elementary scripts were not compiled in their authoring runtime | Build and seven axiom checks passed, with two style warnings. The stricter warning-as-error source check failed on those warnings |
| ABCJet checked copy in this edition | The same Lean and mathlib pins | Two disclosed tactic-sequencing edits to a separate copy | Build, direct warning-as-error elaboration and seven axiom checks passed |
| KTG Block 03 v0.3.0 | Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` | Checked release dated 17 September 2026 | Clean build and 22 warning-as-error direct elaborations passed |

The original KTG ZIP has SHA-256
`aab95b7b4bdf5e80908aa75917ea37a7ec2a1d8b66eec9faa09704d9e989a94b`.
Its ZIP CRC check and all 131 entries of its SHA-256 and size manifest passed.
The recovered fresh-replay JSON is historical evidence, rather than the
current run. Current input checks are in `formal/INPUT_AUTHENTICATION.json`.

The ABCJet ZIP has SHA-256
`8fa40fc2c39b13ed0eb05fde23a0a08d1e3426b189d0b7ec29b91f51d658bf8c`.
Its CRC check passed. The original module SHA-256 is
`6e7d9ca58b6b4591696c5afb55f13aec71cd6225bae6b2734acdfd05919b9fb5`.
The original module, project file and toolchain file are preserved unchanged
in `formal/jet_source`. Their hashes are in
`formal/ABCJet_INPUT_AUTHENTICATION.json`.

## Current KTG checks

The unchanged recovered verifier `verification/verify_block03.py --clean`
completed with exit code zero. It used the exact declared compiler and Lake
5.0.0-src+6a10ac8. The clean build completed all 24 Lake jobs. All 22 Lean source
files elaborated directly with warnings treated as errors. The placeholder and
custom axiom declaration scan had no hits. The 14 predecessor module files
matched their recorded source hashes. Source bytes before and after the run
matched.

The original contract audit is a text-marker check. Its
`iut_specific_global_instance_present` field is recorded as a literal `false`
by the verifier, rather than computed by an instantiation search. That flag
alone is not proof of absence. The raw-source review and the recorded
`SourceWitnessTheorem` references locate the supplied inhabitant only in the
finite `SourceExample` namespace. The declarations and inspection limit are
recorded in `formal/KTG_SOURCE_BOUNDARY_INSPECTION.json`.

A fresh `#print axioms` audit covered all 42 explicit named KTG theorems. Of
these, 41 depend on no axioms. The generic theorem
`KTG.Countermodels.prewitness_gates_do_not_imply_hull_witness` uses Lean's
standard `propext`. There is no custom axiom or `sorryAx` in the output.
The source-specific Boolean countermodel and positive equality model use no
axioms. The target list and actual output are preserved in
`formal/KTG_AXIOM_TARGETS.json` and `formal/ktg_axiom_audit.log`.

## Environment correction and failures

Both exact official compiler releases were downloaded. The v4.34.0-rc2 archive
matched the SHA-256 supplied by the official GitHub API. The v4.19.0 release API
did not supply a digest. Its HTTPS source, size and freshly computed digest are
recorded without claiming a second independent digest check.

The first tar extraction commands failed with exit code 2 because this host
rejected the packaged numeric ownership. Re-extraction with `--no-same-owner`
passed. The official Lean binaries then failed before compilation because the
host denies `/proc/<calling-process-PID>/exe`, while allowing `/proc/self/exe`.
The official Lean runtime source identifies that lookup. A small `LD_PRELOAD`
compatibility shim redirects only this own-process executable lookup to
`/proc/self/exe`. Every other path is passed unchanged. The shim is disclosed,
hashed and included as source. Compiler and proof bytes were unchanged.

The direct compiler version checks, clean build, all per-file elaborations and
axiom audit passed with that shim. Their reports explicitly record its use.
This is a current exact-version replay with a host compatibility layer, rather
than a claim that the unassisted executables ran in this host.

`formal/RUNTIME_FAILURES.md`, the version diagnostics, API metadata, extraction
logs and command records retain the failed and corrected attempts. An attempted
`strace` diagnosis was denied by the host's ptrace restriction and is also
preserved. No infrastructure failure is interpreted as a failed theorem.

## Dependency graph and open boundary

1. `TypedData` gives separate type fields for output, q-pilot, hull-input,
   comparable-line, prime-strip, trace, arithmetic-structure and measurement roles.
2. `SourceRealizationCertificate` contains IPL, an APT trace carrying SHE, and
   an obstruction bundle. It contains no hull-containment or scalar-bound field.
3. `ObstructionControl` demands separate proof predicates for nine channels.
4. `NormalizationWitness` contains a comparable-line object and proofs for
   determinant and procession compatibility. Its tracked grade equation follows.
5. **Open application input:** a proof of `StepXiEWitnessPreservation` for
   actual IUT data yields `QPilotHullContainment`.
6. A monotone observable converts that containment into the scalar inequality.

The separate type fields distinguish roles in the generic interface. They do
not require pairwise unequal types. The finite models assign `Bool` to several
roles. The normalization grade's `vectorRank` field is only a positive natural
number. The comment describing a rank greater than one is not an encoded
rank-greater-than-one hypothesis. The grade-transfer equations and the later
`j * j` field are checks of the chosen abstract definitions. They do not prove
that those definitions match IUT's actual normalization or log-volume objects.
Those interpretation and instantiation obligations remain external to the
compiler check.

| Obligation | Audit status | Evidence or boundary |
|---|---|---|
| Abstract types and theorem quantifiers | Passed | Exact sources and direct elaboration |
| Typed certificate has no scalar target field | Passed | `IUT312Certificates.lean` |
| Explicit intermediate line and grade bridge | Passed | `IUT312Normalization.lean` |
| Conditional hull-to-scalar implication | Passed | `IUT312WitnessObligation.lean` and axiom output |
| Pre-witness fields logically imply containment | Refuted in the abstract interface | Boolean equality-order model with output false and q-pilot true |
| Actual IUT instantiation of field semantics | Not addressed by compilation | Source interpretation and mathematical instantiation remain separate |
| Actual IUT source witness theorem | Open | No inhabitant supplied outside the finite equality example |
| IUT III Corollary 3.12 or ABC from this development | Incomplete | The application-specific containment theorem is missing |

## ABCJet theorem scope

The separate ABCJet source contains exactly the following seven statements.
Its original broad `import Mathlib` and all seven proof bodies are unchanged
during recovery. The resolved mathlib tag is commit
`c44e0c8ee63ca166450922a373c7409c5d26b00b`. The nine resolved package commits
are retained in `formal/ABCJet_DEPENDENCY_PINS.json`.

| Theorem | Quantified arithmetic domain and hypotheses | Exact scope |
|---|---|---|
| `balanced_ratio` | Rational `a,b,c,R`, with `a,b,R` nonzero | Cancellation of the balanced `a*b` factor |
| `two_node_gram` | Four arbitrary rational weights and nodes | A two-node polynomial Gram identity |
| `three_node_gram` | Six arbitrary rational weights and nodes | A three-node polynomial Gram identity |
| `truncatedH2_formula` | Arbitrary rational `t` | Formula for the explicitly defined three-term truncation |
| `cleared_truncation` | Rational `a,c`, with `c` nonzero | Denominator-cleared formula for that truncation |
| `cleared_truncation_remainder` | Arbitrary integers `a,c` | Exact polynomial decomposition with remainder `a^5` |
| `determinant_in_jet_coordinates` | Three arbitrary rational symbols | An algebraic change of coordinates |

The Gram identities do not encode positivity or nonvanishing hypotheses.
The three-term truncation is not the infinite polylogarithm series. The
integer remainder identity does not itself formalize a prime-divisibility
argument. The final coordinate identity treats three rational symbols and
does not establish their equality to analytic or p-adic values. Infinite
convergence, general Hankel determinants, valuation-minimality and the
global ABC bridge are outside these seven scripts.

## Current ABCJet checks and the explicit corrected copy

The original `lake build` completed successfully under Lean 4.19.0, commit
`6caaee842e94`, and Lake 5.0.0-6caaee8. All seven original proofs compiled.
The compiler reported two `linter.unnecessarySeqFocus` style warnings at
lines 19 and 53. A direct run with `-DwarningAsError=true` rejected those
warnings. This unsuccessful strict run is retained as a valid unsuccessful
provenance record, rather than reported as a pass or a mathematical failure.

The original compiled module passed its seven `#print axioms` checks. Six
theorems depend on the standard Lean axioms `propext`, `Classical.choice` and
`Quot.sound`. The integer remainder identity depends only on `propext`.
No `sorryAx` or custom axiom dependency appeared.

A separate copy in `formal/jet_checked_source` makes exactly the compiler's
two suggested changes: `field_simp [ha, hb, hR] <;> ring` becomes
`field_simp [ha, hb, hR]; ring`, and `field_simp [hc] <;> ring` becomes
`field_simp [hc]; ring`. The original source is untouched. The theorem
statements, coefficient domains, constants and broad `import Mathlib` are
unchanged. The patch, locations and hashes are in
`formal/ABCJet_CHECKED_COPY_PATCH.diff` and its JSON record.

That checked copy passed its build, direct source elaboration with warnings
treated as errors, forbidden-token scan and seven axiom reports. Its source
bytes before and after the run matched. No linter was disabled.

## Run provenance and reproduction

The KTG replay, original ABCJet strict failure, and ABCJet checked-copy pass
each have a version 2 computation-audit manifest. All three manifests passed
the current validator with the project root supplied, including output hashes
and execution-input freshness. Validation authenticates the run record, rather
than the mathematical source interpretation. Actual validation commands,
stdout, exit status and manifest hashes are in
`formal/MANIFEST_VALIDATION.json`.

The exact command records, actual runtime versions, source hashes, shim hash,
logs, per-file checks and declared results are preserved. The compilation
contracts quantify over the 22 KTG source files and seven ABCJet statements.
They are not searches over ABC triples. The Lean proofs quantify over their
stated abstract, rational or integer objects, while their application to
unencoded analytic and arithmetic objects remains outside the formal scope.

The strongest safe statement is that the abstract KTG pipeline, its positive
model and its logical independence model have been replayed under the exact
recorded compiler, and the seven elementary ABCJet identities have been
compiler checked under their original exact compiler and mathlib pins. The
next mathematical check is a concrete source
instantiation of one load-bearing witness-preservation implication. Another
generic scalar lemma cannot supply that input.
