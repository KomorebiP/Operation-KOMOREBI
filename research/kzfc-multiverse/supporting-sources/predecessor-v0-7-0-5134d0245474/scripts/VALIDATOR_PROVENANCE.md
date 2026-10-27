# Evidence validator provenance

validate_manifest.py is the retained project copy of the installed mathbox computation-audit validator, originally read through its resource interface. Its schema and validation logic are unchanged in this block. It validates evidence records, not Lean proof terms.

The v0.7.0 final verification uses verify_staged.py and the source-enumeration helpers in verify.py. It additionally pins the manifest producer, validator and packager alongside compiler inputs and predecessor source files. The manifest identifies the actual v0.6.0 predecessor archive and has release-specific claims updated to the current proof boundary. Every compiler invocation and its actual exit is recorded. The completed staged-session record is not a claim of one uninterrupted compiler subprocess.
