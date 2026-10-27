# Evidence validator provenance

validate_manifest.py is the unchanged retained project copy of the installed mathbox computation-audit validator, originally read through its resource interface. It validates evidence records and their hashes, not Lean proof terms.

The v0.9.0 audit uses verify_staged.py and the source-enumeration helpers in verify.py. It pins proof sources, dependency configuration, predecessor sources, contract, manifest producer, validator and packager. The manifest records the actual v0.8.0 source archive. Every compiler invocation and actual exit is recorded. The completed staged-session record does not claim one uninterrupted compiler subprocess.
