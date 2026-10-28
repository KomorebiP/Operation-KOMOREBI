# GitHub source and qualification status

Source availability recorded 2026-10-27. Library checks and release tags observed 2026-10-28.

## Current source availability

The input source checkout was [080487d6401a7e9d90c415fd9ffbbf8d825e3842](https://github.com/KomorebiP/Operation-KOMOREBI/commit/080487d6401a7e9d90c415fd9ffbbf8d825e3842). The verified receipt set identifies **166 imported components** and **139,002 distinct source files**. The [component index](COMPONENT_INDEX.md) separates primary works, supporting scientific sources, and any selected components without a verified receipt.

Availability is derived from each component's receipt, expected source-tree digest, and the exact bytes of every owned file. An archive attachment or a selected filename alone does not establish this status. These records identify the published sources. Replaying the mathematics is a separate check.

The initial 18-component source-file import completed successfully in [Actions run 40521059972](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/40521059972) on 27 October 2026. Subsequent component receipts identify the expanded source collection.

## Software qualification records

All software is **beta and work in progress**. The library records below identify the commits and completed runs inspected on the observation date. Later source changes need their own checks.

| Library | Checked commit and runs | Result and scope |
|---|---|---|
| Komorebi Math | [Commit `b3aa11f8f41a`](https://github.com/KomorebiP/komorebi-math/commit/b3aa11f8f41a6acaef012260866cfe21730234ea) · [CPU release qualification](https://github.com/KomorebiP/komorebi-math/actions/runs/40704823688) · observed 2026-10-28 | The CPU release workflow passed all 18 jobs, including Linux and Windows source and installation checks on Python 3.11, 3.12, and 3.13. The Windows hardware wrapper passed its unavailable-backend rejection check. This is not a positive GPU hardware qualification. |
| Polyphase Float | [Commit `c1e8cf517661`](https://github.com/KomorebiP/polyphase-float/commit/c1e8cf517661b12bdb0530caf246374815ec0505) · [CI](https://github.com/KomorebiP/polyphase-float/actions/runs/40724366462) · [ABI governance](https://github.com/KomorebiP/polyphase-float/actions/runs/40724366461) · [CodeQL](https://github.com/KomorebiP/polyphase-float/actions/runs/40724366465) · observed 2026-10-28 | The CI, ABI governance, and CodeQL workflows passed for this commit. Their configured checks and platforms define the tested scope. |


The [publication metadata](../manifests/release-candidate.json) records these commit and workflow identities. The [tagged beta releases](PUBLICATION_STATUS.md#release-assets) point to earlier source commits. A passing run for a newer commit does not qualify an older release snapshot.

### Packages in this collection

| Component | Inspected record | Result and scope |
|---|---|---|
| AM-SPD | [Publication receipt](../verification/am-spd-v1.0.0-publication.json) and [release checklist](../packages/komorebi-am-spd/RELEASE_CHECKLIST.md) | The historical 1.0.0 release has its own qualification record. The current collection-wide software label is beta / work in progress. |
| Constructive Repair | [Windows acceptance and remaining checks](components/CONSTRUCTIVE_REPAIR.md), 27 October 2026 | Windows 11 / CPython 3.12.14: 134 engine tests and 72 installed cases passed. The 100-test release suite had 95 passes, 3 POSIX-only skips, and 2 symlink-fixture setup errors. This is partial Python qualification, with no new Lean replay. |

**Earlier Math failures:** [Run 40473822693](https://github.com/KomorebiP/komorebi-math/actions/runs/40473822693), inspected on 27 October 2026, failed after executing tests. Its Ubuntu Python 3.11 job reported 2,748 passed, 10 skipped, and one release-channel metadata failure. A Windows 3.13 distribution job failed a hardware-wrapper import. The [later repair](https://github.com/KomorebiP/komorebi-math/commit/b3aa11f8f41a6acaef012260866cfe21730234ea) corrected both issues. The passing run above belongs to that repair commit and leaves the earlier results intact.

The earlier Polyphase Float observations remain available in [CI 40473953308](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953308), [ABI 40473953130](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953130), and [CodeQL 40479469045](https://github.com/KomorebiP/polyphase-float/actions/runs/40479469045).

The [27 October repository audit](AUDIT_2026-10-27.md) records source-receipt verification, navigation repairs, and the new Windows evidence. Run `python -B tools/check_source_receipts.py` and `python -B tools/update_completion_status.py --check` to check the committed source inventory and all maintained navigation/status pages. These checks do not execute the research programs.

## Preserved history

The [7 October import report](history/GITHUB_IMPORT_STATUS_2026-10-07.md) preserves its original source revisions, qualification records, and remaining work. Its descriptions of private staging are historical. The [earlier contribution index](history/CONTRIBUTIONS_2026-10-09.md) and [ledger snapshot](../manifests/history/contributions-2026-10-09.json) retain their dated source-selection state.

Source-file import does not overwrite sealed proof receipts or historical numerical logs. Fresh Lean compilation, numerical reproduction, and empirical replication require their own explicit records.

[Current publication status](PUBLICATION_STATUS.md) · [Collection](../README.md)
