# Failures, repairs and boundaries

## Source recovery did not finish

The newer October 16–17 Paper X source and evidence ZIPs were not recovered from the inspected searches, current date-filtered Library listing or the preserved October 18 inventory. The inventory contained 19,926 entries. Absence from those inspected results does not establish permanent deletion or nonexistence. The October 11 package was recovered and its outer ZIP integrity checked, but it was not adopted as current mathematical source. Paper X's previously reported 122-module success therefore remains a prior report, not a new result of this checkpoint.

## Runtime recovery changed the execution situation

The runtime was initially absent in this session. The exact seven-part offline archive was recovered, assembled against its supplied chunk and whole-archive SHA-256 pins, and extracted. The pinned executable then ran the compiler fixtures. Nine dependency repository HEAD values matched the recovered manifest. This is runtime recovery and scope-specific execution, not a claim that every external dependency was freshly rebuilt.

## Auditor development compilation

The first new `AuditCore.lean` version failed to compile. Array indexing required an `Inhabited` instance for the target record, and mutable count variables needed explicit `Nat` types. The corrected source compiled. The original source, compiler output and exact diff remain in `evidence/failed_attempts/`. These were new verification-tool defects, not repairs to a Paper X mathematical proof.

## Fixture and diagnostic repairs

The first compiler-control pilot passed two fixtures, then failed before its intended third audit. The axiom-in-type fixture used `def` for a proposition-valued declaration and triggered Lean's linter. It was rewritten as a theorem with the same test purpose. Its successful compilation was then followed by the intended axiom-policy rejection.

A later batch rejected the invalid common-witness proof as intended, but the Python wrapper expected the wrong capitalization and phrasing of its diagnostic. The actual diagnostic was `Application type mismatch`. The specific expected text was corrected, the failed batch retained, and the final cases rerun. An unrelated compiler error was not counted as the intended rejection.

## Interrupted combined run

One outer container call reached its 120-second execution limit while running the controls. Its stored report remained `RUNNING`, with four completed cases. It is preserved as interrupted and is not a suite pass. Fresh disjoint batches in new directories later completed all 18 cases. Only the reports under `evidence/controls/` contribute to the accepted suite.

## Evidence parser hardening

The initial 55-method wrapper suite produced four failures and one error. Boolean values could be mistaken for integer process exit codes or timeout values. Nonfinite JSON constants were accepted. A JSON array in place of an event caused an uncontrolled attribute error rather than a deliberate validation exception. The parser and process checks were hardened to reject these inputs. The original test output and exact source diff are retained.

The corrected 55-method suite passed. Nine further receipt-mutation methods were added. The final 64-method suite passed with no skips. All 18 real compiler cases were rerun against the final parser revision, rather than retroactively relabeling the earlier runs.

## What is not certified

No Paper X production module was built or audited in this checkpoint. No new theorem, unrestricted existence result, same-witness identification, or arithmetic attachment is claimed. No Paper X manuscript or reader was replaced. Full Mathlib import, a cold upstream rebuild and native Windows execution were not performed. The subprocess helper kills a POSIX process group on timeout, but this suite does not certify general detached-process supervision. Saved-record authentication is different from a new compiler execution. The new tool is not a security boundary against malicious source metaprograms or an independently verified proof checker.
