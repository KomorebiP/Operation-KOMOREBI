# Recovery log

Author: Komorebi P. — 2026-09-19

Earlier retrieval attempts could identify the v14 checksum but could not access
the actual archive. In this session file access succeeded and the original ZIP
was recovered from its saved record. Its hash matched, its CRC passed, and all
4,567 original manifest entries matched. All 4,568 extracted files were also
compared with the original ZIP entries.

Recovery of the later September 13 extension failed. Eight title searches found
no matching primary records. Automated workspace maintenance removed the earlier
transient copy. No source bytes from that extension were available for inclusion.
This archive therefore preserves the full v14 source release and states the
missing later extension explicitly.

No Lean compiler was run, no proof source was edited, and no new theorem-check
receipt is claimed. Historical build failures and receipts remain unchanged inside
the original release tree. The large portable runtime payload is external, as it
was in the original continuation archive.
