# Block31 development failures

1. The first container-discovery call exceeded its transport window before a useful
result. A later ordinary invocation succeeded. The five existing runtime parts
assembled to the recorded SHA256 and extracted with zero exit status.

2. The first LinearReachability draft had an underconstrained submodule inclusion
coercion, an unused binder, two letI-style warnings under warning-as-error, and a
noncomputable subtype alias without the required annotation. Explicit typing and
local normalization corrected them. The intended statements were unchanged.

3. The first mask embedding proof used rewriting across a semireducible subtype
alias; Lean rejected its implicit-transparency type inference. An explicit
composition of the same two proved equalities repaired the unchanged theorem.

4. The initial witness file omitted explicit p,r arguments in a type that contains
ZMod(p^r), and conditional Fin literals were not normalized. Explicit parameters
and a literal three-component vector repaired the examples. An unused generic
Fintype parameter was removed. The intended diagonal and cardinalities stayed fixed.

5. The first Python audit called a nonexistent inherited `in_box` helper. No
finite assertion result was retained from that failed run. A local exact
integer-divisibility membership function was added, without altering inherited code.

6. Supplementary Lean tests had two unused simp arguments and one missing p,r
specialization. Those test fragments were repaired. All final expected values
are unchanged. A bare leanchecker help probe lacked Lean on PATH and failed;
actual verification runs use the recorded portable PATH and module replay.

Four deliberate negative controls assert false arithmetic, a placeholder proof,
a false orbit-equals-span consequence, and a false coordinate-box cardinality.
They are successful controls only when Lean produces the expected explicit
false-proposition or placeholder diagnostic, not merely an arbitrary nonzero exit.

The authoritative final phases remove only the current project's .lake/build,
retain pinned dependencies, and freeze all Lean/Python execution inputs. Source
hashes before and after every phase must agree. Development logs and first drafts
are retained under development/. No inherited theorem is weakened or retracted.

Release aggregation caught an axiom-output parser omission after the first full
successful build/test sequence. Lean wrapped 62 declaration reports across lines;
the single-line parser counted only872 of934. The kernel-driven inventory already
covered all2131 project-owned theorem constants. The parser now stops at matching
brackets while allowing multiline bodies, with tests for empty lists, axiom-free
records, duplicate names, truncation, and the complete934-declaration log.
All final phases are rerun after this verifier change because the verifier itself
is part of the frozen execution inputs. The first receipts are retained in history/.

A read-only interim evidence check during the second active rebuild reported stale
first-run receipt hashes and a not-yet-written parser-test receipt. This was an
incomplete-run consistency check, not a failure of a completed final sequence.
Only the final post-completion read-only replay is used for release promotion.
