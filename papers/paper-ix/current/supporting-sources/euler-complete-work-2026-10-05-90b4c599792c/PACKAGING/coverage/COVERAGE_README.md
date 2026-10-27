# Euler archive coverage check

This is a read-only packaging check. It does not introduce or change a mathematical result.

## Verified base

`handoff_inputs/Euler_Stationary_Separation_2026-10-05.zip`

- SHA-256: `19878d2553a5a5cbada8791e7751b37fdbe73422b6c0da9893a9d9e178c49c96`
- Size: 45,255,332 bytes.
- Its recursive archive closure contains 21 distinct ZIP blobs and 1,662 distinct included content objects, identified by SHA-256 rather than member name.
- CRC checks passed for every distinct recursively inspected ZIP. No absolute or traversal member paths were found.

## Additional surviving work

The verified base does not contain all historical source bytes that survive in the visible workspace. Among 1,958 eligible local files, 478 files fall outside the base's recursive SHA-256 closure. They represent 447 distinct objects totaling 45,267,737 bytes before compression.

Every extra local object is in one of these scopes:

| Scope | Extra local files | Extra local bytes |
|---|---:|---:|
| `inputs/` | 4 | 19,648,332 |
| `local_parameter/` | 1 | 175,059 |
| `recovered/` | 473 | 26,885,635 |

The extra distinct objects include 112 Lean sources, 48 Python sources, 26 Markdown files, 13 PDFs, 4 LaTeX files, 12 figures, stored results and logs, and eight distinct ZIP blobs. The ZIP histories add 14 distinct archives to the base's archive closure. Same-name historical ZIPs were not assumed to be byte-identical.

## Inclusion recommendation

For one complete, portable handoff of this Euler work:

1. Keep the exact verified latest ZIP unchanged.
2. Keep all eligible visible research directories in their original layout: `Euler_Address_One_Continuation_2026-10-05/`, `Euler_Regular_Address_and_Critical_Phases_2026-10-05/`, `audit_helpers/`, `carry_audit/`, `independent_review/`, `inputs/`, `local_parameter/`, `next/`, `recovered/`, `sources/`, and `transversality/`.
3. Keep the two visible standalone Address One and Regular Address/Critical Phases ZIPs. Both are already present in the latest recursive closure, so they may alternatively be omitted if the archive index records their exact existing locations.
4. Keep this packaging coverage record and the final packaging manifest.
5. Exclude the private transfer helpers, private transfer metadata, and Python caches from the outer working tree. The immutable historical ZIPs remain unchanged.

Keeping all eligible working directories avoids breaking relative imports and replay paths. It includes some byte-identical copies by design. The minimum additional distinct source set is enumerated exactly in `coverage_summary.json`, under `minimal_extra_inclusion`, if a future deduplicated handoff is needed.

## Evidence and limits

- `local_inventory.json` contains each eligible local path, size, SHA-256, and its coverage status.
- `latest_content_catalog.json` maps the included latest recursive content objects to archive member locations.
- `archive_catalog.json` records every distinct archive encountered across latest and local inputs.
- `coverage_summary.json` records aggregate counts and an exact additional inclusion list.
- `audit_coverage.py` reproduces the check without modifying any source or archive.

This establishes coverage for the exact latest checkpoint and the surviving visible Euler workspace. It is not an assertion that every historical Komorebi file anywhere in external storage has been collected. Historical Lean sources and stored Lean logs are preserved as supplied. Lean compilation was not rerun for packaging.
