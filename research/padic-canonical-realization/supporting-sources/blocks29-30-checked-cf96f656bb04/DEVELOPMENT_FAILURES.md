# Preserved development failures and repairs

## Authoritative incoming failure
The candidate's results/VERIFICATION.json reported INCOMPLETE_LEAN_BUILD, first
failed module IdealClosureExamples. Six construction modules had successful
historical receipts, but that was not a release-level success. The exact candidate
is retained separately and original records are in history/candidate_results.

The nilpotent capacity example had two omega goals that were not solved, and its
state-cardinality simp list contained unused Fintype.card_fun. The repaired proof
uses le_antisymm with the already proved lower/upper bounds and removes the unused
simp argument. The statements and algorithms are unchanged. Both versions and the
original diagnostic are retained under history/candidate_attempt.

## Supplementary test repairs in this run
The first universal test lacked explicit (p:=2) (r:=2), causing implicit-type
elaboration to exceed Lean's heartbeat limit. Equivalence-valued example terms
also required noncomputable context. Explicit parameters and a noncomputable
section fixed these issues. The next run found an unclosed unnamed section;
a separate `end` closed it. No expected value or mathematical statement changed.
Failed drafts and all dev_universal*.log/json records are retained.

## Evidence classification
The dev_* builds and tests are development records only. After all test files and
verifier scripts were fixed, the project-local build cache was emptied and the
entire final verification sequence was executed on frozen source. Only final_*
receipts establish the current release. Historical failures are not erased or
reinterpreted as passes. No network installation or stable-toolchain fallback was
used. The five retained runtime chunks assembled to their recorded SHA256 and
extracted successfully; restore evidence is under results_current/runtime_*.

## Release-parser failure caught before promotion
The first complete final compiler sequence passed, but read-only aggregation
failed its coverage check. The Python regex allowed whitespace to span a newline
after an empty axiom list; the next theorem record was misread as an axiom name.
This was a report-parser bug, not an unexpected axiom in Lean. The parser was
replaced by strict line-wise field parsing with duplicate/malformed-record checks.
A regression phase tests empty lists, successive records, invalid fields, and
complete 2,024-entry coverage. The original failing verifier and all first-final
receipts are retained in history/first_final_before_parser_repair. Because the
verifier is a frozen execution input, every final phase was rerun after correction.
