# Failures and their interpretation

These records concern this publication's fresh computation audit. Original development failures remain preserved in their unchanged historical payloads.

## Block 67 success label mismatch

The unchanged scientific verifier finished with status `PASS`, exit code zero, eight complete result comparisons and nine deliberate rejection controls. The generic archive wrapper required `PASS_DECLARED_CHECKS` and failed afterward. This was a wrapper interpretation error. It was not a failed scientific calculation.

The failed version 2 record and traceback are in `block67-run`. The separate `block67-status-review` confirms the actual verifier outcome and original output hashes. It keeps the failed wrapper status unchanged. The direct portable scientific replay subsequently completed independently in `portable67-run`.

## Block 69 aggregate wall timeout

The original archive verifier was invoked under one CPU of affinity, a 2 GiB address space cap and an aggregate wrapper wall cap of 840 seconds. It exceeded that wall cap. The wrapper exited unsuccessfully and produced no final verifier report or accepted scientific result set. The version 2 manifest explicitly lists the missing declared results.

The record is resource inconclusive. It does not establish a mismatch in the original finite data and does not provide a completed fresh archive replay of Block 69. Other original historical Block 69 evidence remains historical evidence. The separate direct portable scientific replay passed in475.410396 seconds, comparing all 17 complete scientific JSONs at unchanged bounds. Its900 second wall limit,2 GiB address space cap,800 second per process CPU cap, two cores of affinity and one conventional thread cap differ from the original attempt. It skips repeated archive integrity and corruption recomputations. This successful scientific result does not rewrite the earlier archival timeout.

## Block 71 legacy unit-domain metadata

The primary historical JSON hardcodes 2304 for a loop that enumerates 49²−7²=2352 units. The separate original JSON correctly records2352, and the quotient has 49 classes with 48 elements each. A new bounded enumeration confirms the correction in `unit-domain71-run/correction.json`. All original bytes and the already executed portable71 contract remain unchanged. Their original metadata is explicitly superseded for interpretation by this correction. The mathematical quotient and period/gauge results did not change.

## Independent final-guide QA test correction

The initial invocation of the version2 runner was refused before execution because it omitted explicit `--input` flags; listing execution artifacts in the contract does not replace those flags. No manifest or mathematical result was produced by that invocation. The recorded invocation then supplied every required input.

The first executed independent guide QA failed at the toric h value for337. Its own test used the cyclotomic residue arithmetic degree instead of the degree of the place in the all-inert base field. The correct base-field norm is Q=q² for every support prime. The failure is retained in `reader-data-qa-run`, with the executed original script `audit_reader_data.py` and its unchanged contract. A new separately versioned `audit_reader_data_v2.py` uses Q=q², retains all original guide and historical bytes, and passes in `reader-data-qa-v2-run`. This is a QA test normalization correction, not a repair to a guide matrix, support, count or scientific algorithm.

## Process inventory diagnostic

A diagnostic `ps -C python3` failed with the environment message `fatal library error, lookup self`. A default `ps -eo` inventory succeeded and showed only the active task processes. No scientific code or input was changed to address this diagnostic.

## Original development failures

The Block 80 payload retains the rejected overstrong primitive generator check and rejected verifier syntax source. The corrected original algorithms are the bytes replayed in this publication. Earlier failed exclusion attempts, resource records and the Block 70 zero product incident remain in the selected original history. Preserving them does not endorse a rejected argument.

No reported target solver success is an authenticated arithmetic realization. Every new evaluator input is synthetic. No new computation eliminates one of the eight surviving bounded patterns.

## Administrative run-summary correction

The first summary helper attempted to parse a declared text log as JSON and failed with JSONDecodeError. Its original code and a separate failure record remain under `rejected_helpers`. The corrected administrative helper treats non-JSON outputs as logs. This changed no mathematical run, result, original input or provenance manifest.
