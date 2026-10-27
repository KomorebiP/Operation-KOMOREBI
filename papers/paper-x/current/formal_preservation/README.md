# Paper X source and evidence preservation

This collection preserves the content of three original Paper X archives, including every nested ZIP. Identical nonarchive files share one stored payload. The original archive names, Library identifiers, SHA-256 hashes, nested member chains and member metadata remain in `ARCHIVE_MAP.json`.

**This preserves extracted file content, not the original ZIP byte streams.** Compression settings, archive ordering and complete ZIP container metadata are not reconstructed. The original container hashes identify the source archives. They are not hashes that the restore script promises to reproduce.

## Read the two scopes separately

- `readable/checked_conditional/` contains the earlier checked conditional completion source and saved evidence. Its principal source is `source/PaperX/ConditionalOccupiedSystemCompletion.lean`. Its saved receipt is `evidence/VERIFICATION.json`. The release records a 20/20 internal ledger only at its expressly amended and conditional scope. Actual completed source members, compatible carrier presentations and constituent comparison data remain supplied inputs. See the original `PROOF_AUDIT.md` and `CLAIM_STATUS.json` here.
- `readable/later_residual_attempt/` contains the later residual-system completion attempt and its terminal records. These report a 19/20 ledger and no promotion because the requested Lean executable was unavailable. They do not constitute a compiler rejection or retraction of the earlier conditional theorem. The source reports describe a residual-system criterion beginning with finite nonempty companion levels, whereas the checked conditional source already assumes actual completed members.

Original file content is unchanged. Some original reports use paths relative to their original extracted release and execution workspace. Restore that release content to obtain the original directory layout, with nested ZIPs represented as directories.

Payloads also cover the retained Claim 9.1, Claim 9.2 and earlier dependency/history archives. `objects/sha256/` stores content that is not assigned a readable location above. For duplicate content, one occurrence may live at a readable path while other original names are represented only in the map. No original leaf payload is stored twice.

## Verify and restore

Only Python's standard library is required. These commands copy and hash files. They do not execute archived scripts or invoke Lean.

```bash
python3 restore.py --verify
python3 restore.py --list
python3 restore.py --output ../paper_x_restored
python3 restore.py --root conditional_checked --output ../paper_x_conditional_restored
```

The output directory must be new or empty. Each selected top-level archive receives its own directory. Nested archives become directories whose names end in `.zip.contents`; their nonarchive member bytes are restored exactly. Original duplicate ZIP members with different content receive an `.archive_entry_XXXXXX` suffix if their paths collide. Timestamps and file modes remain recorded in the map; the script restores file content rather than reenacting historical permissions.

## Collection checks

All leaf bytes were read through Python's ZIP reader, which checks member CRC values, and hashed using SHA-256. The compact store receives an independent payload-hash verification after creation. `PRESERVATION_SUMMARY.json` records the measured counts and `COLLECTION_VERIFICATION.json` records the collection checks.

The earlier checked conditional release's 41-entry original payload manifest matched before compaction, and its actual source hash matched its saved PASS receipt. No Lean compilation, archived verification script or new mathematical proof audit was performed for this collection.
