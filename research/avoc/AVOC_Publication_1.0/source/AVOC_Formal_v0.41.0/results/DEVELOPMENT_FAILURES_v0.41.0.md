# AVOC v0.41.0 failures, corrections, and obstructions

## Protocol and mathematical obstructions

The inherited immutable calibration log rejects unfinished-to-terminal reuse
of one operation ID. This is formally proved. The new recorder keeps pending
intents separate; the original log was not silently changed into a mutable one.

Complete resolved lifecycle logs do not by themselves provide IID completed
prefixes. Independent fair initiation outcomes reordered success-first have
first-report success probability 3/4 for two attempts. In a twenty-attempt
example, the implemented n=m=10, alpha=1/10 interval misses p=1/2 on an event
of mass at least 308333/524288. All twenty records are present and all intents
resolved. Exact review evidence is retained in review_completion_order.py/json.
This refutes an external physical-model implication, not the explicit
source-generative theorem.

## Proof development failures

Recorder builds 01,02,04,06 had elaboration, list/filter simplification, equality
elimination, deprecated-lemma, or unused-parameter lint failures. Builds 03,05,07
passed successive revisions. recorder_report.md gives the individual fixes and
all invocation logs/hashes are preserved.

Refinement builds 01 and 03 had proof elaboration/simplification and unused
DecidableEq section-variable failures. Builds 02,04 and05_finalcore passed; the
last rebuilt against the frozen recorder. refinement_development_failures.md
lists the failures. Its initial prose count of 25 theorems came from an unanchored
regex matching a comment; the exact inventory correctly contains 24. The module
was not changed to inflate the count.

Root codec_initial failed to unfold Except.toOption on the rejected branch of
its equivalence proof. Adding that definitional simplification fixed the proof;
codec_second passed. RecorderPolicy compiled on its first attempt. No admitted
proof, project axiom, native_decide, unsafe theorem, or disabled linter repaired
these failures.

## Bounded execution failures

The Python/reference and actual Lean development comparisons passed. A first
resource-controlled run then failed at Lean startup under a 2 GiB virtual-memory
cap with a thread-creation error. A second run under 8 GiB failed while mapping
an existing core object file. Neither produced a scientific result.

Both exact failed manifests/stdout/stderr files are preserved under
executable_failed_run_001 and executable_failed_run_002, with archival notes.
A separate diagnostic observed approximately 8.56 GiB virtual peak and 3.66 GiB
resident memory for successful startup. The final run removes only the added
RLIMIT_AS restriction, records the shared 20 GiB cgroup limit, and retains its
wall, CPU, core-affinity, and output bounds. It uses the clean final objects.

The launcher initially exposed stderr only on abnormal exit, hiding a diagnostic
written to stdout. It now reports both streams. The failed runs are not counted
as passing evidence, and the larger inherited memory envelope is not described
as a per-process 8 GiB guarantee.

A fresh-output-directory guard also refused a launch because failed-run output
files were present. Their bytes matched the archived second failure, and only
the duplicate copies were removed. Both prior runner sessions had exited; the
cause of the duplicate presence was not established. The guard prevented an
untracked overwrite and the archived originals remain intact.

## Independent release-validator findings

Review found and closed mixed parser/crash diagnostics that could be mistaken
for substantive negative proof failures, missing import digests in resumption
records, omitted inherited example-fixture hashes, and missing negative-compiler
identity binding. The revised gates fail closed on those cases. Runtime evidence
also binds the final source/object dependency closure and compiler identity.

The separate gate reviewer passed 57 isolated initial probes plus 15 runtime
provenance probes, 72 total. One reviewer-script invocation failed by trying to
JSON-serialize a Python set; sorted-list serialization repaired it and the full
probe rerun passed. That script failure was not proof or production evidence.

No inherited mathematical, runtime/check, or historical evidence source was
modified to achieve the new result. Full verification and packaging records
remain separate from development notes and bounded experiments.
