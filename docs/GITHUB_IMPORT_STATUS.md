# GitHub source and qualification status

Recorded 2026-10-27.

## Current source availability

The input source checkout was [080487d6401a7e9d90c415fd9ffbbf8d825e3842](https://github.com/KomorebiP/Operation-KOMOREBI/commit/080487d6401a7e9d90c415fd9ffbbf8d825e3842). The verified receipt set identifies **166 imported components** and **139,002 distinct source files**. The [component index](COMPONENT_INDEX.md) separates primary works, supporting scientific sources, and any selected components without a verified receipt.

Availability is derived from each component's receipt, expected source-tree digest, and the exact bytes of every owned file. An archive attachment or a selected filename alone does not establish this status. These records identify the published sources. Replaying the mathematics is a separate check.

The initial 18-component source-file import completed successfully in [Actions run 40521059972](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40521059972) on 27 October 2026. Subsequent component receipts identify the expanded source collection.

## Software qualification records

All software is **beta and work in progress**. The following records are dated observations of specific runs, not claims about every later revision:

| Component | Inspected record | Result and scope |
|---|---|---|
| Komorebi Math | [Qualification run 40473822693](https://github.com/KomorebiP/komorebi-math/actions/runs/40473822693), 27 October 2026 | The run executed tests and failed. The inspected Ubuntu Python 3.11 job reported 2,748 passed, 10 skipped, and one release-channel metadata failure. The Windows 3.13 distribution job separately failed a hardware-wrapper import. |
| Polyphase Float | [CI 40473953308](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953308), [ABI 40473953130](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953130), [CodeQL 40479469045](https://github.com/KomorebiP/polyphase-float/actions/runs/40479469045), 27 October 2026 | The inspected CI, ABI, and CodeQL runs completed successfully. These results apply to the runs' source revisions and configured coverage. |
| AM-SPD | [Publication receipt](../verification/am-spd-v1.0.0-publication.json) and [release checklist](../packages/komorebi-am-spd/RELEASE_CHECKLIST.md) | The historical 1.0.0 release has its own qualification record. The current collection-wide software label is beta / work in progress. |
| Constructive Repair | [Windows acceptance and remaining checks](components/CONSTRUCTIVE_REPAIR.md), 27 October 2026 | Windows 11 / CPython 3.12.14: 134 engine tests and 72 installed cases passed. The 100-test release suite had 95 passes, 3 POSIX-only skips, and 2 symlink-fixture setup errors. This is partial Python qualification, with no new Lean replay. |

The Math failure above supersedes the earlier publication note that described failures before any job steps. Consult the live Actions pages and exact commit before making a newer qualification claim.

The [27 October repository audit](AUDIT_2026-10-27.md) records source-receipt verification, navigation repairs, and the new Windows evidence. Run `python -B tools/check_source_receipts.py` and `python -B tools/update_completion_status.py --check` to check the committed source inventory and all maintained navigation/status pages. These checks do not execute the research programs.

## Preserved history

The [7 October import report](history/GITHUB_IMPORT_STATUS_2026-10-07.md) preserves its original source revisions, qualification records, and remaining work. Its descriptions of private staging are historical. The [earlier contribution index](history/CONTRIBUTIONS_2026-10-09.md) and [ledger snapshot](../manifests/history/contributions-2026-10-09.json) retain their dated source-selection state.

Source-file import does not overwrite sealed proof receipts or historical numerical logs. Fresh Lean compilation, numerical reproduction, and empirical replication require their own explicit records.

[Current publication status](PUBLICATION_STATUS.md) · [Collection](../README.md)
