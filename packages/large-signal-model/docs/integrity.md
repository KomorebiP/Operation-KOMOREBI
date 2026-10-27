# Checking a delivered source archive

`RELEASE_MANIFEST.json` identifies every declared source file by relative path,
byte count and SHA-256. It excludes itself to avoid a self-referential digest.

```bash
python scripts/verify_manifest.py --strict
```

Run the strict check immediately after extraction, before creating test caches or
build outputs. Without `--strict`, local extra files are reported but do not fail the
hash check. The standard source distribution adds `PKG-INFO`, `setup.cfg` and egg-info
metadata, so the non-strict mode is appropriate for that representation.

The final wheel was byte-identical to the wheel tested in an isolated target. Its
RECORD entries were checked against actual member hashes. The complete handoff has
its own outer manifest for source, installation artifacts and preserved companions.
Companion ZIPs remain exactly identified original archives, not silently merged code.

Checksums establish integrity relative to the supplied manifest, not authorship or
an independently trusted signature. This release is not digitally signed. Publication
and licensing decisions remain separate from integrity verification.
