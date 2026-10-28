# Verification evidence

This directory retains dated publication, source, and execution evidence. Use the [verification guide](../docs/VERIFICATION.md) to reproduce checks, the [workflow guide](../docs/WORKFLOWS.md) to understand GitHub runs, and the [records guide](../docs/RECORDS.md) to find the reports that interpret these files.

| Evidence family | Entry point and scope |
|---|---|
| Collection publication and source checks | [Publication receipt](publication/2026-10-27.json) and [source-publication record](source-publication-2026-10-27.json). Identity and publication scope are distinct from theorem replay. |
| Constructive Repair | [Windows summary](constructive-repair/windows-2026-10-27/summary.json), [source-to-wheel binding](constructive-repair/windows-2026-10-27/wheel-source-binding.json), and [reader guide](../docs/components/CONSTRUCTIVE_REPAIR.md). The recorded suite includes unresolved setup errors. |
| Focused soundness checks | [Contract](audits/soundness-2026-10-27/contract.json), [run record](audits/soundness-2026-10-27/run/manifest.json), and [report](../docs/SOUNDNESS_REVIEW_2026-10-27.md). |
| Original SRIC admission defects | [Contract](audits/sric-admission-2026-10-27/contract.json), [run record](audits/sric-admission-2026-10-27/run/manifest.json), and [audit](../docs/SRIC_ADMISSION_AUDIT_2026-10-27.md). Preserved diagnostic counterexamples. |
| Corrected SRIC 0.3.3 edition | [Contract](audits/sric-repair-2026-10-27/contract.json), [run record](audits/sric-repair-2026-10-27/run/manifest.json), and [repair guide](../docs/SRIC_REPAIR_2026-10-27.md). Finite fixtures and rejection controls. No checks with a real model. |
| AM-SPD publication | [Historical release receipt](am-spd-v1.0.0-publication.json). Its original scope and date remain attached. |

Some evidence lives inside a preserved component rather than this directory. Follow that component's [status entry](../docs/STATUS_CATALOG.md) and source instructions. Written reviews are indexed under [manifests](../manifests/README.md). This directory does not contain every proof or experiment.

Keep run inputs, source revisions, environments, outcomes, and failures together. Give new results their own record. Preserve sealed receipts and report setup errors as setup errors.

[Documentation](../docs/README.md) · [Records guide](../docs/RECORDS.md)
