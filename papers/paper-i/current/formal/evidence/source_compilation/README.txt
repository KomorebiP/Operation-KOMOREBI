COMPILATION COMPONENT — EVIDENCE STORAGE

The original verification.json is preserved byte for byte. Its 115 production
objects and one boundary object are identical to the corresponding objects in
../whole_closure/objects/. They are stored there once. OBJECT_LOCATIONS.json
maps all 116 original component-relative paths to release-relative canonical
paths, with SHA-256 hashes and byte counts. Both original receipts authenticate
every object. All component snapshots and logs remain here.

The default formal/verify.sh builds fresh objects and does not use these
evidence objects. Storage relocation does not change the formal checks or
their results, and no unique evidence has been removed.

To validate the relocation from the release root:

  python3 formal/evidence/source_compilation/materialize_compilation_component.py --check-only

For optional verifier --base-fresh reuse, first restore the original layout:

  python3 formal/evidence/source_compilation/materialize_compilation_component.py /absolute/path/to/new-component

The destination must be new and outside this release tree. The helper validates
both receipts and every object, copies the metadata and logs, and restores
the original objects/ paths. Use that restored directory with --base-fresh;
this deduplicated directory is not itself a direct --base-fresh input.
Restoration is a file-copy operation, not a new Lean verification run.
