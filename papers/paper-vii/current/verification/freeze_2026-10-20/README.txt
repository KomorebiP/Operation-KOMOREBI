All 3,262 selected baseline files retain exact original bytes. Only the root
manifest moves to before/ so the complete current manifest can include freeze
additions. All original scripts, source, PDFs and dated evidence remain at their
original paths. BASELINE_PRESERVATION.json maps every original file uniquely.

The primary strict checker is new to VII and byte-identical to Paper VI's
accepted checker. Its exact 21-control receipt and harness are retained as
inherited tooling evidence under tooling/paper_vi/. No control suite is rerun.
All original VII checker bytes remain unchanged. The new root manifest retains
the accepted portable checker's exact schema; original VII's checker can still
read its files list on Linux. The additional checksum list excludes itself and
the root manifest, which in turn authenticates the list, avoiding a hash cycle.

No scientific code, PDF, Lean or TeX is rebuilt. Read-only fresh checks cover
baseline identity, accepted source/report bindings, closed source preservation,
reader structure/selected renders and safe clean archive extraction. Historical
compiler, computational, control and PDF-rebuild events retain their dates.
The source audit scripts target the original unmodified baseline; reproduce
them in a separate working copy with the retained original manifest restored.
