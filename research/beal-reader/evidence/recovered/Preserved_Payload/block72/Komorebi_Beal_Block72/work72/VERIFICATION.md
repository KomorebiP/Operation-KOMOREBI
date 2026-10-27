# Verification protocol

Python standard library only; bytecode disabled. Run:

    python -B verify.py --report ../Block72_Replay.json

The report must be outside the immutable package. The verifier checks the exact
payload set and every hash, the original Block71 archive bytes, thirteen pinned
source/validator leaves (deepest leaf at archive level19), and the frozen eight
coefficient patterns. It creates a clean scratch copy, deletes both expected
scientific outputs, rebuilds them with the two separate programs, and compares
complete JSONs. It validates the retained v1 computation record and its additional
input before/after hashes using the copied project-local v1 checker.

Eight deliberate scientific corruptions must be rejected by the separate program
for the named mismatching field: wrong omega coordinate, wrong action matrix,
false elimination, false lift count, missing uniformizer, unsupported precision,
invented global lift, and altered local root. A ninth corruption changes README
and must be rejected by the payload checker. These are controlled negative tests,
not mathematical counterexamples to Beal or failed successful-science records.

--integrity-only does not run science. --replay-predecessor adds the immediate
Block71 DEFAULT verifier. Neither option claims fresh execution of all older
historical blocks. The pre-development default Block71 replay is retained in
work72/verification/Block71_Replay.json and its log.

Each scientific subprocess has a300-second wall timeout; the optional predecessor
has600seconds. Nonzero exit or timeout is failure/inconclusive execution, never
an arithmetic exclusion. The standard-library programs are single-threaded. No
memory limit is represented as enforced. Command output, runtime and exit status
are recorded in the external replay report.

Finite checks do not validate inherited geometry or global representation theorems.
No new Lean compilation, point counts, full-history replay, or independent
mathematical review is claimed.
