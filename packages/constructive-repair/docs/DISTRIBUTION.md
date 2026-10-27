# Current release and historical evidence

The rc3 ZIP is a complete **current** source-and-evidence distribution. It is not
an archive of every previous ZIP recursively nested inside every later ZIP.
The earlier rc2 package was 47,558,578 bytes. Most of those bytes were predecessor
archives, which in turn contained their own predecessor archives.

## What is retained

The package retains all active Python modules and tests, the installable wheel,
all 51 Lean proof modules, all certificate inputs and fixtures, the complete
monograph source/PDF, the historical development and verification logs already
present as ordinary files, and the original exact Python audit.

`provenance/` additionally contains **121 byte-exact historical proof snapshots**:
10 from v0.2.0, 23 from v0.3.0, 37 from v0.4.0, and 51 from v0.5.0. Each snapshot
was extracted from the corresponding original archive. `lineage.json` records
the original archive's hash, original byte count, source filename and source hash.
The full formal verifier checks each snapshot against its current counterpart
before rebuilding the current proof modules.

## What is not recursively included

Predecessor ZIPs and their complete old binary contents are not embedded in this
ZIP. The original rc2 artifact remains a separate unchanged archive:

- Name: `Komorebi_Constructive_Repair_v1.0.0-rc2.zip`
- Bytes: 47,558,578
- SHA-256: `0be8e88bef0398405dc3b1693e539779ed083d35f2f008caba85187e9d49fc6c`

Old reports that describe an archive as bundled describe their historical
release, not the rc3 distribution. The references and failure records are not
rewritten into new historical claims. Current verification requires neither a
network request nor access to the predecessor ZIPs.

The Lean compiler and Mathlib cache remain a separate pinned runtime. These are
not included in the small distribution, exactly as in the previous releases.

## Integrity versus authentication

Hashes and manifests check bytes against a record. They are not signatures and
cannot authenticate a release obtained from an untrusted source. An adversary
who replaces both the code and every receipt can fabricate matching hashes.
The gate checks consistency of the supplied record, not that the producer or
compiler was honest. Fresh Lean verification is available through the included
scripts and still uses Lean's own kernel against the pinned imports.

No code license, document license, or public publishing action is inferred from
this redistribution of the user's working package.
